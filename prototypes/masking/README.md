# 마스킹 프로토타입

OCR 직후 개인정보를 가리는 함수(R1)와 서술형 답변의 개인정보 위치를 찾는 함수(R7)를 시험하는 코드다.
설계는 [`docs/privacy/data-flow.md`](../../docs/privacy/data-flow.md), 항목은 [`docs/privacy/pii-items.md`](../../docs/privacy/pii-items.md)를 본다.

- **서버 코드가 아니다.** `backend/`가 생기면 서버 담당이 `backend/app/`으로 옮길지 정한다 (`SETUP-PLAN.md` 2절)
- 표준 라이브러리만 쓴다. 설치할 것이 없다
- 테스트 값은 모두 가짜다. 실제 문서·개인정보를 넣어 커밋하지 않는다

## 함수

| 함수 | 입력 | 출력 | 쓰는 곳 |
| --- | --- | --- | --- |
| `mask_ocr_lines(lines)` | `OcrLine(text, page, bbox)` 목록 | `MaskResult`: 가린 줄, 감지 위치(원문 없음), `residual`, `masked_text` | F-01 → L1 (P1) |
| `detect_pii(text)` | 서술형 답변 문자열 | `Finding(kind, start, end)` 목록 (텍스트는 안 바꿈) | L3 중계의 서버 재검사 (P4 ⑤). 브라우저 감지(①)는 같은 규칙을 JavaScript로 옮겨 쓴다 (`l3-masking.md` 2절) |

서술형의 사전 정보 대조, `[종류N]` 번호 토큰, 되돌리기(`l3-masking.md`)는 브라우저에서 할 일이라 이 프로토타입에 없다.

`residual`이 `True`면 LLM을 부르지 않는다.

`Finding.start`·`end`는 **가리기 전** 그 줄(또는 답변) 원문 기준 위치다. 가린 텍스트(`masked_text`)에 그대로 대입하면 다른 곳을 가리킨다. 화면에서 위치를 강조하는 기능을 만들 때는 원문을 가진 쪽(서술형은 브라우저)에서만 쓴다.

라벨 값 규칙 요약:
- 라벨에 붙은 괄호는 설명(`성명(한글) 홍길동`), 띄어 쓴 괄호는 값(`성명 (홍길동)`)
- 라벨 값은 다음 라벨(개인정보 라벨과 `신청일`·`배우자`·`국적` 같은 일반 라벨) 앞에서 끝난다
- 생년월일 라벨은 날짜 하나만 가린다. 날짜 모양이 없으면 라벨 뒤 값 전체를 가린다

## 실행

| 단계 | 명령 | 위치 | 상태 |
| --- | --- | --- | --- |
| 테스트 | `python3 -m unittest -v` | `prototypes/masking/` | Claude가 실행함 (2026-11-17, Python 3.13.2, 2차 리뷰 반영 후): `Ran 27 tests ... OK (expected failures=1)`. 본인 실행: 미실행 |
| 린트 | `ruff check .` | `prototypes/masking/` | 미실행 (ruff 미설치) |

`expected failures=1`은 알려진 한계(문장 속 이름) 테스트다. 고치면 이 표시가 `unexpected success`로 바뀐다.
