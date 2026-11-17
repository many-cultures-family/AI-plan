"""개인정보 마스킹 프로토타입 (R1·R7·R8).

- `mask_ocr_lines`: OCR 직후 한 번만 부르는 마스킹 함수. 이 함수가 돌려준 텍스트만 LLM(L1)에 보낸다.
- `detect_pii`: 가린 서술형 답변에 개인정보가 남았는지 서버가 다시 검사할 때 쓴다 (L3 중계 ⑤).
  브라우저 감지(R7 모달)는 같은 규칙을 JavaScript로 옮겨 쓴다.

설계 근거: docs/privacy/data-flow.md, docs/privacy/pii-items.md, docs/privacy/l3-masking.md
표준 라이브러리만 쓴다. OCR 엔진이 정해지지 않아 입력은 '줄 단위 텍스트 + 칸 위치'로 받는다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# kind -> LLM에 보낼 자리표시 토큰. 값 대신 '이 자리에 무엇이 있었는지'만 남긴다.
TOKENS = {
    "resident_no": "[주민등록번호]",
    "alien_no": "[외국인등록번호]",
    "phone": "[전화번호]",
    "email": "[이메일]",
    "address": "[주소]",
    "name": "[이름]",
    "birth_date": "[생년월일]",
    "long_number": "[번호]",
}

# 1) 값 모양으로 찾는 규칙 (라벨이 없어도 잡는다). 순서가 우선순위다.
#    주민등록번호·외국인등록번호 뒷자리 첫 숫자 구분(1~4·9·0 / 5~8)은 [추정]. 출처 확인 필요.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("resident_no", re.compile(r"(?<!\d)\d{6}\s*-?\s*[1-490]\d{6}(?!\d)")),
    ("alien_no", re.compile(r"(?<!\d)\d{6}\s*-?\s*[5-8]\d{6}(?!\d)")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    (
        "phone",
        re.compile(
            r"(?<![\d+])(?:\+82[\s-]*0?|0)(?:1[016789]|[2-6]\d?|70)"
            r"\s*[-.)]?\s*\d{3,4}\s*[-.]?\s*\d{4}(?!\d)"
        ),
    ),
    # 도로명(…로/…길 + 번호) 또는 지번(…동/읍/면/리 + 번호). 앞쪽 시·도·구 이름까지 같이 가린다.
    (
        "address",
        re.compile(
            r"(?:[가-힣]+(?:특별시|광역시|특별자치시|특별자치도|도|시|군|구)\s+)*"
            r"[가-힣0-9]+(?:로|길|동|읍|면|리)\s*\d+(?:-\d+)?(?:\s*번지)?"
        ),
    ),
    # 위 규칙에 안 걸린 긴 숫자(계좌·여권·카드 번호 등)는 안전하게 가린다.
    ("long_number", re.compile(r"(?<!\d)\d(?:[\d\s-]{8,}\d)(?!\d)")),
]

# 2) 라벨 뒤 값을 가리는 규칙. 이름처럼 값 모양만으로 알 수 없는 항목용.
#    "성명: 홍길동", "성 명  홍길동", "Name: Nguyen Van A" 같은 줄에서 라벨 뒤 값 전체를 가린다.
_LABEL_TAIL = r"\s*(?:\([^)]*\))?\s*[:：]?\s*"  # "성명(한글):"처럼 괄호 설명이 붙은 라벨
_LABELS: list[tuple[str, re.Pattern[str]]] = [
    ("name", re.compile(r"(?:성\s*명|이\s*름|Name)" + _LABEL_TAIL, re.IGNORECASE)),
    ("birth_date", re.compile(r"(?:생\s*년\s*월\s*일|Date of Birth)" + _LABEL_TAIL, re.IGNORECASE)),
    ("address", re.compile(r"(?:주\s*소|Address)" + _LABEL_TAIL, re.IGNORECASE)),
]
# 개인정보가 아닌데 숫자 규칙에 걸리기 쉬운 것. 먼저 자리를 차지해 가리지 않게 한다.
# 날짜(신청일·기한)는 L1이 칸을 이해하는 데 필요하다. 생년월일은 라벨 규칙으로 따로 가린다.
_SAFE = re.compile(r"(?<!\d)\d{4}\s*[-./]\s*\d{1,2}\s*[-./]\s*\d{1,2}(?!\d)")
# 라벨만 있고 값이 비어 있는 빈칸(예: "성명: ____")은 가리지 않는다.
_BLANK = re.compile(r"^[\s_.\-()（）□☐]*$")


@dataclass
class Finding:
    """감지 결과. 원문 값은 담지 않는다 (R8: 감지된 원문은 저장하지 않음)."""

    kind: str
    start: int
    end: int
    line: int = -1  # OCR 줄 번호. 서술형 답변이면 -1


@dataclass
class OcrLine:
    text: str
    page: int = 1
    bbox: dict | None = None  # DATA-MODEL form_field.bbox 형식 (0~1 비율)


@dataclass
class MaskResult:
    lines: list[OcrLine]
    findings: list[Finding] = field(default_factory=list)
    residual: bool = False  # 가린 뒤에도 개인정보 모양이 남았으면 True → LLM에 보내지 않는다

    @property
    def masked_text(self) -> str:
        """DATA-MODEL `document.masked_text`에 저장할 값."""
        return "\n".join(line.text for line in self.lines)


def _spans(text: str) -> list[Finding]:
    """한 줄에서 개인정보 위치를 찾는다. 겹치면 먼저 찾은(우선순위 높은) 것을 남긴다."""
    kept: list[Finding] = []

    def add(f: Finding) -> None:
        if all(f.end <= k.start or f.start >= k.end for k in kept):
            kept.append(f)

    # 날짜 자리를 먼저 막아 둔다 (나중에 결과에서 뺀다).
    for m in _SAFE.finditer(text):
        add(Finding("_safe", m.start(), m.end()))

    # 값 모양 규칙 먼저: "성명: 홍길동 010-…"에서 전화번호를 따로 잡는다.
    for kind, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            add(Finding(kind, m.start(), m.end()))

    # 라벨 값은 다음 라벨이나 이미 찾은 개인정보 앞까지만이다.
    # 예: "성명: 홍길동 생년월일: 1990.01.01" → 이름은 "홍길동"까지.
    # 라벨 뒤 날짜는 생년월일이므로 막아 둔 자리를 푼다.
    label_hits = sorted(
        ((m.start(), m.end(), kind) for kind, p in _LABELS for m in p.finditer(text)),
    )
    kept[:] = [
        k
        for k in kept
        if not (
            k.kind == "_safe"
            and any(kind == "birth_date" and end == k.start for _, end, kind in label_hits)
        )
    ]
    stops = [s for s, _, _ in label_hits] + [k.start for k in kept] + [len(text)]
    for _, value_start, kind in label_hits:
        value_end = min(s for s in stops if s >= value_start)
        value = text[value_start:value_end].rstrip()
        if _BLANK.match(value):
            continue
        add(Finding(kind, value_start, value_start + len(value)))

    return sorted((k for k in kept if k.kind != "_safe"), key=lambda f: f.start)


def detect_pii(text: str) -> list[Finding]:
    """서술형 답변용 (F-07, R7). 위치와 종류만 돌려주고 텍스트는 바꾸지 않는다."""
    return _spans(text)


def _replace(text: str, spans: list[Finding]) -> str:
    out, cursor = [], 0
    for f in spans:
        out.append(text[cursor : f.start])
        out.append(TOKENS[f.kind])
        cursor = f.end
    out.append(text[cursor:])
    return "".join(out)


def _strip_tokens(text: str) -> str:
    for token in TOKENS.values():
        text = text.replace(token, " ")
    return text


def mask_ocr_lines(lines: list[OcrLine]) -> MaskResult:
    """OCR 직후 한 번 부르는 마스킹 함수 (R1).

    원문은 이 함수 안에서만 다루고 돌려주지 않는다. 호출한 쪽은 원문 변수를 바로 버린다.
    가린 뒤 같은 규칙으로 한 번 더 검사해, 남은 것이 있으면 residual=True로 알린다 (US-01 실패 조건).
    """
    masked: list[OcrLine] = []
    findings: list[Finding] = []
    residual = False

    for i, line in enumerate(lines):
        spans = _spans(line.text)
        for s in spans:
            s.line = i
        findings.extend(spans)
        new_text = _replace(line.text, spans)
        if _spans(_strip_tokens(new_text)):
            residual = True
        masked.append(OcrLine(text=new_text, page=line.page, bbox=line.bbox))

    return MaskResult(lines=masked, findings=findings, residual=residual)
