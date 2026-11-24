> **2026-11-17 개정 — 서버 미저장 결정 반영.** 병합된 결정 `docs/decisions/no-server-storage-user-input.md`가 "사전 정보와 입력값은 서버에 저장하지 않는다"로 정하고, 이 문서를 "입력값 저장 API와 서버 불일치 계산을 브라우저 계산으로 바꾼다"로 고치도록 적었다. 그래서 이전 판의 **입력값 저장(`PUT .../answers/{field_id}`)·불일치 확인(`POST .../answers/{field_id}:acknowledge-mismatch`) API를 없애고**, 조회 API는 값 없이 칸 정보와 형식 규칙만 주도록 바꿨다. 이전 판의 "`review` 단계에서 값이 바뀌면 `step`을 `writing`으로 되돌린다"도 서버가 값 변경을 알 수 없어 없앴다 (`REVIEW-PRIVACY-API.md` 항목 1). PR #131 리뷰 지적(두 문서가 서로 반대로 말함)을 풀려고 김원우가 고쳤고, **원래 담당자(이효상) 확인이 필요하다.**
>
> **2026-11-23 구현 반영.** 코드 저장소 `stepping-stone` PR #30(리뷰 중)에 항목 1·2를 구현했다. 구현하면서 원본 위에 입력칸을 겹쳐 그리려고 항목 1 응답에 위치 값(`bbox`·`input_bbox`·`option_bboxes`·`part_bboxes`·`document.page_count`)을 더했고, 원본 페이지 이미지 API(항목 3)를 새로 두었다. 더한 것은 모두 `[제안]`이다.
>
> **이 문서는 근거가 약하다.** F-04(가상 작성 환경·불일치 표시)는 `backlog.md`에 스토리와 인수 조건이 **아직 없다** (`mvp-scope.md` 17·20행, `PRD.md` 47행). 이 문서는 `mvp-scope.md`·`03-rules-states-llm.md`·`DATA-MODEL.md`·`docs/privacy/`를 보고 만든 엔드포인트 명세이고, 인수 조건은 팀이 `backlog.md`에 직접 쓴다 (CLAUDE.md).

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. 세션이 없으면 `401 LOGIN_REQUIRED`, 작성 건이 본인 것이 아니면 `403 FORBIDDEN_DRAFT`, 없는 작성 건이면 `404 DRAFT_NOT_FOUND` (`LOGIN-API.md` "다른 API의 권한 규칙") |
| 전제 상태 | `draft.status`가 `수정`이 아니면 `409 DRAFT_NOT_EDITABLE`. `draft.step`은 항목마다 적고, 맞지 않으면 `409 DRAFT_STEP_INVALID` |
| 가상 환경 | 여기서 다루는 값은 실제 기관에 **절대 전송하지 않는다** (R4). 사용자에게 "연습" 화면임을 알리는 문구는 화면 담당 |
| 서버가 저장하지 않는 것 | 사용자가 칸에 쓴 값, 사전 정보, 불일치 확인 여부(`mismatch_acknowledged`) — 모두 **브라우저에만** 둔다 (`no-server-storage-user-input.md`, `pii-items.md` 1절). 서버에 입력값을 보내는 API는 없다 |
| 형식 검사·불일치 계산 | **브라우저의 규칙 엔진**이 한다. 형식 검사는 항목 1이 내려 주는 `pattern`(서버 `input_format`과 같은 값)으로, 불일치는 브라우저에 있는 사전 정보와 비교해서 계산한다. 차이 나는 글자 표시도 화면 몫이다 (R3 — 오류 판정은 규칙 엔진이 하고 LLM은 하지 않는다. 규칙의 출처는 서버 `input_format` 한 곳이다) |
| 날짜시간 형식 | UTC, ISO 8601 + `Z` (예: `2026-11-09T10:00:00Z`) |

## 항목 1: 가상 작성 화면용 칸 정보 조회 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/form` |
| 전제 단계 | `step`이 `writing` 또는 `review` (검토 중에도 답변을 고칠 수 있어야 한다) |
| 입력 | 없음 |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`) + `document`(`page_count`) `[제안]` + `fields`(배열). 칸마다: `field_id`, `label`, `format_code`, `format_label`, `format_example`, `pattern`(정규식, `long_text`·`choice`·`signature`는 `null`), `required`, `prior_info_key`, `description`, `options`(선택형이면 선택지 배열, 아니면 `null`), 그리고 아래 위치 값 4개 `[제안]` |
| 위치 값 `[제안]` | 모두 `form_field.bbox`와 같은 0~1 비율 `{"page", "x", "y", "w", "h"}`. 원본에서 못 찾으면 `null`이고, 그때 화면은 `bbox`로 자리를 어림한다 — `bbox`: L1이 고른 위치(F-02 `form_field.bbox` 그대로). 표 안 칸이면 **라벨** 자리, 표 밖이면 그 **줄** 자리다 / `input_bbox`: 실제로 값을 적는 자리 — 표의 값 칸, 밑줄(`____`) 위, 라벨 뒤 빈자리. `signature` 칸은 `(인)`·`(서명 또는 인)` 표시 자리 / `option_bboxes`: `choice` 칸의 체크 상자(`□`) 위치 배열, `options`와 같은 순서. 상자 수가 보기 수와 다르면 `null` / `part_bboxes`: 날짜줄(`    년   월   일`)의 `{"year", "month", "day"}` 빈자리 |
| 위치 값을 계산하는 방법 | OCR·L1은 글자가 있는 곳만 알려 주므로, 서버가 조회 때마다 원본 그림에서 선·상자·글자 덩어리 모양을 보고 계산한다(글자는 읽지 않는다, OpenCV — EasyOCR이 같이 설치함). 저장하지 않고 매번 계산한다(`errors`를 저장하지 않는 `FIELD-CHECK-API.md` 방식과 같음). 실제 동의서 1종과 합성 그림으로만 확인했고, 스캔본·다른 서식은 `확인 필요` |
| 서명 칸 | `signature` 칸도 내려 준다. 화면은 값을 받지 않고 `input_bbox` 자리에 '직접 서명' 표시만 한다 (R10) |
| 화면이 그리는 방법 (참고) | 원본 페이지 이미지(항목 3) 위에 위치 값 자리마다 입력칸을 겹친다. `choice`는 `□` 위에 체크(하나만), 날짜줄은 년·월·일 칸을 따로 받아 `YYYY.MM.DD`로 합쳐 `pattern`으로 검사한다 |
| 값·불일치가 없는 이유 | 입력값과 사전 정보가 서버에 없으므로 이전 판의 `value`·`mismatch`는 뺐다. 화면은 브라우저에 있는 값을 `field_id`로 짝지어 보여 주고 불일치를 계산한다 |
| `pattern`을 주는 이유 | 브라우저 규칙 엔진이 서버와 **같은 형식 규칙**을 쓰게 하려는 것이다 (`input_format`을 DB 한 곳에만 두는 `db.py` 원칙). `REVIEW-PRIVACY-API.md` 항목 5의 최종 확인 숫자도 이 규칙으로 센다 |
| 실패 응답 | 공통 규칙의 `401`/`403`/`404`/`409` |
| 관련 인수 조건 | 없음 — F-04 스토리 작성 뒤 채움 |
| 화면이 쓰는 곳 | 가상 작성 환경 (`DESIGN.md`에 이 화면 행을 추가해야 한다, 화면 담당) |

## 항목 2: 작성 시작 — `prior_info` → `writing` (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/writing:start` (`REVIEW-PRIVACY-API.md` `review:start`와 같은 방식) |
| 전제 단계 | `step`=`prior_info` |
| 입력 | 없음 |
| 동작 | `draft.step`을 `prior_info` → `writing`으로 바꾼다. 사전 정보는 브라우저에만 있어 서버가 다 입력됐는지 확인할 수 없으므로, 사전 정보 입력이 끝났는지는 화면이 확인한 뒤 부른다 (US-04, R11 "이미 있으면 다시 묻지 않음"도 화면 몫) |
| 출력 (성공) | `200`. `{"draft": {"id", "status": "수정", "step": "writing"}}` |
| 실패 응답 | 공통 규칙의 `401`/`403`/`404`/`409` |
| 관련 인수 조건 | US-04 '관련 상태 전이: 항목확정 → 사전정보입력완료'의 다음 단계 |
| 화면이 쓰는 곳 | 사전 정보 입력 화면의 '작성 시작' 버튼 |

## 항목 3: 원본 페이지 이미지 (기능 ID: F-04) `[제안]`

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/document/pages/{page}` (`page`는 1부터) |
| 왜 두나 | 가상 작성 화면이 원본 위에 입력칸을 겹쳐 그리려면 원본 그림이 필요하다. `DOC-UPLOAD-API.md`·`FIELD-CHECK-API.md`·`OCR-API.md` "아직 없는 항목: 원본 파일 보기 API"를 이 화면에 필요한 만큼만 채운다 |
| 전제 | 단계 제한 없음. `status`=`취소`면 문서가 지워지므로 `404 DOCUMENT_NOT_FOUND` |
| 출력 (성공) | `200`. 이미지 파일이면 원본 그대로, PDF면 서버가 그 쪽을 PNG로 그려 준다(화면에 PDF 뷰어 의존성이 필요 없음). `Cache-Control: no-store` (원본에 개인정보가 있을 수 있음) |
| 실패 응답 | 공통 규칙의 `401`/`403`/`404 DRAFT_NOT_FOUND`, 문서가 없거나 취소됨 `404 DOCUMENT_NOT_FOUND`, 쪽 번호가 범위 밖 `404 PAGE_NOT_FOUND` |
| LLM | 부르지 않는다. 원본 그림은 브라우저에만 간다 (`mvp-scope.md` "이미지를 LLM에 직접 넣지 않는다") |
| 화면이 쓰는 곳 | 가상 작성 환경 |

### 입력·출력 예시
```
요청:
GET /api/drafts/1/form

응답(성공): 200
{
  "draft": {"id": 1, "status": "수정", "step": "writing"},
  "document": {"page_count": 1},
  "fields": [
    {
      "field_id": 12, "label": "보호자 연락처", "format_code": "phone",
      "format_label": "전화번호", "format_example": "010-0000-0000",
      "pattern": "^010-\\d{4}-\\d{4}$",
      "required": true, "prior_info_key": "phone",
      "description": "자녀의 보호자 전화번호를 적습니다",
      "options": null,
      "bbox": {"page": 1, "x": 0.1, "y": 0.3, "w": 0.08, "h": 0.02},
      "input_bbox": {"page": 1, "x": 0.31, "y": 0.297, "w": 0.6, "h": 0.026},
      "option_bboxes": null, "part_bboxes": null
    },
    {
      "field_id": 13, "label": "개인정보 수집·이용 동의", "format_code": "choice",
      "format_label": "선택형", "format_example": "보기 중 선택", "pattern": null,
      "required": true, "prior_info_key": null,
      "description": "동의하는지 하나만 고릅니다",
      "options": ["동의합니다", "동의하지 않습니다"],
      "bbox": {"page": 1, "x": 0.36, "y": 0.29, "w": 0.28, "h": 0.02},
      "input_bbox": null,
      "option_bboxes": [
        {"page": 1, "x": 0.432, "y": 0.291, "w": 0.015, "h": 0.01},
        {"page": 1, "x": 0.623, "y": 0.291, "w": 0.014, "h": 0.01}
      ],
      "part_bboxes": null
    },
    {
      "field_id": 14, "label": "작성일", "format_code": "date",
      "format_label": "날짜", "format_example": "YYYY.MM.DD",
      "pattern": "^\\d{4}\\.\\d{2}\\.\\d{2}$",
      "required": true, "prior_info_key": null, "description": "쓰는 날짜를 적습니다",
      "options": null,
      "bbox": {"page": 1, "x": 0.46, "y": 0.75, "w": 0.07, "h": 0.01},
      "input_bbox": {"page": 1, "x": 0.406, "y": 0.749, "w": 0.157, "h": 0.016},
      "option_bboxes": null,
      "part_bboxes": {
        "year": {"page": 1, "x": 0.406, "y": 0.749, "w": 0.055, "h": 0.016},
        "month": {"page": 1, "x": 0.478, "y": 0.749, "w": 0.033, "h": 0.016},
        "day": {"page": 1, "x": 0.529, "y": 0.749, "w": 0.034, "h": 0.016}
      }
    }
  ]
}

요청:
POST /api/drafts/1/writing:start

응답(성공): 200
{"draft": {"id": 1, "status": "수정", "step": "writing"}}
```

## 단계 전이 정리 (이전 판 "아직 없는 항목"의 3개)
| 전이 | API | 문서 |
| --- | --- | --- |
| ① `prior_info` → `writing` | `POST /api/drafts/{id}/writing:start` | 이 문서 항목 2 |
| ② `writing` → `review` | `POST /api/drafts/{id}/review:start` | `REVIEW-PRIVACY-API.md` 항목 1 |
| ③ `review` → `성공`·`반려` | `POST /api/drafts/{id}:complete` | `REVIEW-PRIVACY-API.md` 항목 5 |

## 없앤 것
| 이전 판 | 없앤 이유 |
| --- | --- |
| `PUT /api/drafts/{draft_id}/answers/{field_id}` (입력값 저장·형식 검증·`400 FORMAT_INVALID`) | 입력값을 서버에 저장하지 않는다. 형식 검증은 브라우저 규칙 엔진이 항목 1의 `pattern`으로 한다 |
| `POST /api/drafts/{draft_id}/answers/{field_id}:acknowledge-mismatch` (`400 NO_MISMATCH`) | `mismatch_acknowledged`도 브라우저에 둔다 (`pii-items.md` 4절 #2) |
| `GET /api/drafts/{draft_id}/answers`의 `value`·`mismatch` | 서버에 값이 없다. 경로도 값 없는 칸 정보라 `.../form`으로 바꿨다 |
| "`review` 단계에서 값이 바뀌면 `step`을 `writing`으로 되돌린다" | 서버가 값 변경을 알 수 없다. 검토 중 답변을 고치면 브라우저가 다시 검토한다 (`REVIEW-PRIVACY-API.md` 항목 1) |
| "서술형 값이 바뀌면 검토 제안·감지 결과를 지운다"(서버) | 둘 다 브라우저에 있다. 지우는 것도 브라우저 몫 (`l3-masking.md` 6절) |

## 정한 것 (2026-11-24, 화면 담당)
| 항목 | 정한 내용 | 반영 |
| --- | --- | --- |
| 연결된 사전 정보가 브라우저에 없을 때(`prior_info_key`는 있는데 값이 없음) | 사전 정보 화면으로 돌려보내지 않고 **그 칸에서 바로 입력받는다.** 도움말에 '저장된 사전 정보가 없어요' 안내와 사전 정보 화면(`/prior-info`) 링크를 둔다. 저장하고 돌아오면 아직 빈 연결 칸만 채운다(쓴 값은 덮어쓰지 않음). 불일치는 저장된 값이 없으므로 판정하지 않는다 | `stepping-stone` PR #68 |
| 입력값을 브라우저 어디에 둘지 | 가상 작성 입력값·'그대로 둘게요' 확인 기록은 **`sessionStorage`** (새로고침하면 남고, 탭을 닫거나 작성 건 취소·로그아웃 때 지움). 사전 정보는 `localStorage`(사용자별, 화면에서 직접 지움). `data-flow.md` 5절 #3 | `stepping-stone` PR #57·#58 (`utils/browserStore.js`) |

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| **F-04 스토리·인수 조건이 `backlog.md`에 없음** | 팀 / 가장 먼저 |
| 이번 개정(서버 미저장 반영) 확인 | 이효상(원래 담당) / PR #131 리뷰 때 |
| `backend/app/db.py`에 `field_answer`·`prior_info` 테이블을 만들지 않는다 (`DATA-MODEL.md`에서 빼는 것은 PM) | PM / 결정 반영 때 |
| 이번에 더한 위치 값 4개·`document.page_count`·항목 3을 받아들일지 | 이효상(원래 담당)·화면 담당 / `stepping-stone` PR #30 리뷰 때 |
