> **이 문서의 전제 (팀 결정, 2026-11-17):** 사전 정보와 입력값(서술형 답변 포함)은 **서버에 저장하지 않는다** — `docs/decisions/no-server-storage-user-input.md`. 그래서 F-07(개인정보 감지·결정)은 **브라우저에서** 하고, 서버는 브라우저가 가린 답변을 **다시 검사한 뒤 L3에 중계만** 한다. 흐름·토큰 규칙·결정별 처리는 `docs/privacy/l3-masking.md`(P4 ①~⑧)가 기준이고, 이 문서는 그중 **서버 API 계약**과 검토 단계의 시작·끝(전이)을 적는다. 같은 내용을 옮겨 적지 않고 절 번호로 가리킨다.
>
> **이미 만든 F-06 코드는 이 결정과 맞지 않는다.** `DIDIMDOL` 저장소 `feat/f02-field-check-v2-leehyosang6950`(PR #26, `main`에는 없음)의 `review.py`는 `field_answer`에서 답변을 읽고, `review_suggestion`에 제안을 저장하고, 서버에 저장된 사전 정보로 가린다. 아래 "기존 F-06 코드에서 바꿀 것"을 본다.
>
> 근거: `backlog.md` US-05, `03-rules-states-llm.md` R3·R6·R7·R8·R9·3-4 L3, `docs/privacy/` 3개 문서, `prototypes/masking/`. 경로·오류 코드는 기존 API 문서와 구현된 코드 방식에 맞췄고, 맞출 것이 없던 값은 `l3-masking.md`의 제안과 프로젝트 원칙(개인정보 최소 수집, 상태 변경은 서버 규칙 검증 뒤)에 맞춰 정했다. 칸마다 근거를 괄호로 적었다. 리뷰에서 바뀔 수 있다.

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. 세션이 없으면 `401 LOGIN_REQUIRED`, 본인 작성 건이 아니면 `403 FORBIDDEN_DRAFT`, 없는 작성 건이면 `404 DRAFT_NOT_FOUND`. US-05 권한 인수 조건 "사용자만 볼 수 있다" |
| 전제 상태 | `draft.status`가 `수정`이 아니면 `409 DRAFT_NOT_EDITABLE`. `draft.step`은 항목마다 적는다. 맞지 않으면 `409 DRAFT_STEP_INVALID` (기존 `review.py`와 같음) |
| 서버가 저장하지 않는 것 | 서술형 답변(원문·가린 글 모두), 개인정보 감지 결과, 결정, 토큰 대응표, 검토 제안, 제안 결정 (`pii-items.md` 1절). **요청·응답 본문을 로그에 남기지 않는다** — 로그에는 작성 건 번호·사유 코드만 (`l3-masking.md` 5절, 기존 `drafts.py` 로그 방식) |
| 서버가 쓰는 것 | 서버에 이미 있는 것만: `form_field`(`label`, `guide_text`, `description`, `format_code`), `draft`, `user.language`. `guide_text`는 OCR 마스킹을 거친 값이다 (`DATA-MODEL.md` 59행) |
| 검토 대상 | `form_field.format_code`가 `long_text`(서술형)인 칸만 |
| 사용 언어 | 제안 설명은 `user.language`로 만든다. MVP에서는 베트남어(`vi`) (`VIETNAMESE-SCOPE.md`) |

## F-07은 브라우저에서 한다 (서버는 규칙 목록만 내려 줌)

| 하는 일 | 기준 문서 |
| --- | --- |
| ① 감지 (규칙 + 사전 정보 대조). 규칙은 항목 4로 내려받는다 | `l3-masking.md` 2절, 감지 종류는 `pii-items.md` 2절 |
| ② 감지 모달과 결정 (유지·삭제·검토 제외). **결정이 하나라도 남아 있으면 항목 3을 부르지 않는다** (R7) | `l3-masking.md` 3절 |
| ③ 토큰으로 바꾸기 (`[전화번호1]` 등), 대응표는 메모리에만 | `l3-masking.md` 4절 |
| ⑧ 제안의 토큰을 원래 값으로 되돌리기, 대응표 버리기 | `l3-masking.md` 6절 |
| 제안 반영 여부 고르기 (반영·무시) — 결정은 브라우저가 들고 있는다 (R6) | `l3-masking.md` 6절 |

- **'유지'를 골라도 토큰으로 바꿔 보낸다.** 서버가 항목 3에서 가린 답변을 다시 검사하므로, 원문 그대로 보내면 `422 PII_REMAINING`으로 거절된다. 그래서 API는 이 방식으로 정했다 (`l3-masking.md` 3절). R7·US-05 문구를 이에 맞게 고치는 일은 팀이 한다 (아래 "팀 확인이 필요한 것")
- R7을 서버가 직접 확인할 방법은 없다(결정은 브라우저에만 있다). 서버는 대신 **가린 답변에 개인정보가 남았는지** 다시 검사한다(⑤)

## 항목 1: 검토 시작 — `writing` → `review` (기능 ID: F-06 / 스토리: US-05)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/review:start` (`fields:confirm`이 단계를 넘기는 방식에 맞춤) |
| 입력 | 없음 |
| 전제 단계 | `step`=`writing` |
| 동작 | `draft.step`을 `writing` → `review`로 바꾼다. 필수 입력·불일치 확인은 여기서 막지 않고 항목 5(최종 확인)에서 본다 (R9) |
| 검토 중 답변을 고치면 | 답변이 서버에 없으므로 서버 단계는 `review`로 둔다. 브라우저가 그 답변의 감지 결과·제안을 지우고 ①부터 다시 한다 (`DATA-MODEL.md` 64행 "서술형 값이 바뀌면 다시 검토"). `VIRTUAL-FORM-API.md`의 "`review`에서 값이 바뀌면 `writing`으로 되돌림"은 서버에 값이 있다는 전제라 이 방식으로 바뀐다 |
| 출력 (성공) | `200`. `{"draft": {"id", "status": "수정", "step": "review"}}` (`fields:confirm` 응답 모양에 맞춤) |
| 실패 응답 | 공통 규칙의 `401`/`403`/`404`/`409` |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-05 '관련 상태 전이: 작성중 → 검토완료'의 시작점 |
| 화면이 쓰는 곳 | 가상 작성 환경의 '검토하러 가기' 버튼 |

## 항목 2: 검토할 서술형 칸 목록 (기능 ID: F-06 / 스토리: US-05)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/review` (기존 경로 유지) |
| 전제 단계 | `step`=`review` |
| 출력 (성공) | `200`. `{"fields": [{"id", "label", "guide"}]}` — `id`는 **`form_field.id`**, `guide`는 `guide_text`가 없으면 `description` (기존 `review.py` 규칙). 답변은 서버에 없으므로 넣지 않고, 화면이 들고 있는 답변을 칸 `id`로 짝지어 보여 준다 |
| 바뀐 점 | 기존 응답 `{"answers": [{id(field_answer.id), label, guide, value}]}`에서 키를 `fields`로 바꾸고 `value`를 뺐다 |
| 실패 응답 | 공통 규칙의 `401`/`403`/`404`/`409` |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-05 권한 |
| 화면이 쓰는 곳 | `DESIGN.md` 서술형 검토 |

## 항목 3: 검토 요청 — 다시 검사 후 L3 중계 (기능 ID: F-06·F-07 / 스토리: US-05)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/review:request` (기존 경로 유지) |
| 전제 단계 | `step`=`review` |
| 입력 | `{"answers": [{"form_field_id": 31, "masked_text": "저는 [이름1]입니다. ...", "tokens": ["[이름1]", "[전화번호1]"]}]}` — 브라우저가 ①~③을 마친 **가린 답변**과 쓴 토큰 **이름** 목록. 토큰 값(대응표)은 보내지 않는다 (`l3-masking.md` 4절, 5절 ④) |
| 입력 검사 | `form_field_id`가 이 작성 건의 서술형 칸이 아니면 `404 FIELD_NOT_FOUND` (`FIELD-CHECK-API.md`·`VIRTUAL-FORM-API.md`와 같은 코드). 본문 모양이 틀렸거나 `tokens`에 `[종류N]`·`[가림N]` 모양이 아닌 값이 있으면 `400 INVALID_REVIEW_REQUEST` (본문 형식 오류를 `422` 대신 `400`으로 받는 `INVALID_FLAGGED_FIELD_IDS`에 맞춤) |
| 빈 답변 | `masked_text`가 비었거나 공백뿐이면 `400 ANSWER_EMPTY` (기존 코드와 같음, US-05 실패·거절 인수 조건) |
| ⑤ 다시 검사 | 토큰을 지운 답변에 OCR 마스킹과 **같은 규칙 한 벌**(`masking.py` `detect_pii`)을 돌린다. 하나라도 걸리면 **L3를 부르지 않고** `422 PII_REMAINING`, 본문 `{"detail": {"code": "PII_REMAINING", "field_ids": [31]}}` (`l3-masking.md` 5절. 코드 옆에 목록을 싣는 `FIELDS_INVALID` 방식에 맞춤). 걸린 글자·위치는 돌려주지 않는다 |
| ⑥ L3에 보내는 것 | 가린 답변, 칸 `label`·`guide_text`(서버 값), `user.language`, "토큰은 바꾸지 말고 그대로 둘 것, 토큰 안의 값을 짐작하지 말 것" 지시 (`03` 3-4 L3, `l3-masking.md` 5절 ⑥) |
| L3에 보내지 않는 것 | 답변 원문, 토큰 대응표, 사전 정보 — 셋 다 서버에 오지 않는다 |
| ⑦ 제안 검사 | 제안의 고친 문장에 **보낸 목록에 없는 토큰**이 있거나 토큰 글자가 바뀌었으면 그 제안을 버린다. 토큰이 빠진 제안은 둔다. 버린 개수만 로그에 남긴다 (`l3-masking.md` 5절 ⑦) |
| 호출 횟수 제한 | 제안을 저장하지 않으므로 **부를 때마다 L3를 다시 호출한다.** 작성 건 하나에 **5회**까지 받고, 넘으면 L3를 부르지 않고 `409 REVIEW_LIMIT_EXCEEDED` (작성 건 누적 제한을 `409`로 주는 F-02 `REANALYSIS_LIMIT_EXCEEDED`(3회)에 맞춤. 서술형은 답변을 고칠 때마다 다시 검토해야 해서 2회 더 둠). 횟수는 `draft.review_count`(정수, 처음 0)로 센다 — 개인정보가 아니므로 서버에 둬도 결정과 어긋나지 않는다. `DATA-MODEL.md` 반영은 PM. ⑤에서 거절되거나 L3 호출이 실패한 경우는 세지 않는다 |
| 출력 (성공) | `200`. `{"suggestions": [{"form_field_id", "kind", "suggested_text", "explanation"}]}`. `kind`는 `맞춤법`/`문법`/`질문 의도`/`보충` (`DATA-MODEL.md` `review_suggestion.kind`). **`id`·`decision`은 없다** — 저장하지 않으므로 행 번호가 없고, 결정은 브라우저가 들고 있는다. 화면은 배열 순서로 구분한다. `suggested_text`의 토큰은 브라우저가 되돌린다(⑧) |
| 서술형 칸이 없으면 | `answers`가 빈 배열이면 L3를 부르지 않고 `200 {"suggestions": []}` (기존 코드와 같음). 횟수도 세지 않는다 |
| 실패 응답 | `400 ANSWER_EMPTY`, `400 INVALID_REVIEW_REQUEST`, `404 FIELD_NOT_FOUND`, `409 REVIEW_LIMIT_EXCEEDED`, `422 PII_REMAINING`, `502 LLM_CALL_FAILED`(기존과 같음), 그 외 공통 규칙 |
| 바뀌는 상태 | 바뀌지 않는다 (`수정` 유지, `03` 3-4 L3 "이어지는 상태 전이") |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-05 (실패·거절) 빈 답변 거절, (LLM이 있으면) 사람이 확인하기 전 상태 안 바뀜·개인정보 안 보냄 |
| 화면이 쓰는 곳 | `DESIGN.md` 서술형 검토 ('검토 받기' 버튼 → 감지 모달 → 제안 목록) |

## 항목 4: 감지 규칙 목록 (기능 ID: F-07 / 스토리: US-05)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/privacy-rules` (작성 건과 관계없는 목록이라 `/api` 바로 아래에 둠) |
| 두는 이유 | 브라우저 감지(①)와 서버 재검사(⑤)가 **같은 규칙**을 써야 한다. 규칙을 화면 코드에 따로 적으면 서버와 어긋나 ⑤에서 이유 없이 거절된다 (`l3-masking.md` 2절 '규칙 한 벌'. `input_format`을 DB 한 곳에만 두는 `db.py` 원칙과 같음) |
| 출력 (성공) | `200`. `{"rules": [{"kind": "phone", "pattern": "..."}]}` — 서버 마스킹 모듈의 값 모양 규칙(`masking.py` `_PATTERNS`)을 그대로 내려 준다. 라벨 규칙은 OCR 문서용이라 넣지 않고, 사전 정보 대조는 브라우저가 한다 |
| 확인할 것 | Python 정규식이 JavaScript에서 똑같이 동작하는지 `확인 필요` (`l3-masking.md` 9절 #4). 다르게 동작하는 규칙은 두 언어에서 같게 동작하는 모양으로 고쳐 쓴다 |
| 권한 | 로그인한 사용자 |
| 화면이 쓰는 곳 | 서술형 검토 화면을 열 때 한 번 받는다 |

## 항목 5: 최종 확인 — `review` → `성공` / `반려` (기능 ID: F-06·F-07 / 스토리: US-05, R9)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}:complete` (작성 건 자체의 상태를 바꾸는 `:submit`·`:cancel`에 맞춤) |
| 전제 단계 | `step`=`review` |
| 입력 | `{"remaining_required": 0, "unacknowledged_mismatches": 0, "undecided_suggestions": 0, "undecided_privacy": 0}` — 브라우저가 R9 조건 4개를 센 **숫자만**. 값은 보내지 않는다 |
| 이렇게 정한 이유 | 서버에 입력값이 없어 서버가 직접 셀 수 없다 (`data-flow.md` 5절 #2). 후보 셋 중 ㉠(요약 숫자만 보냄)을 골랐다. ㉡(판정 때만 값을 보냄)은 "서버로 원문을 보내지 않는다"는 결정 취지와 어긋나고, ㉢(브라우저에서 판정·상태 변경)은 CLAUDE.md "상태 변경은 서버 규칙 검증 뒤에만"과 어긋난다. ㉠은 상태를 서버가 바꾸고, 원문이 서버로 가지 않는다 |
| 규칙 엔진 | 필수 누락·형식·불일치 판정은 브라우저의 규칙 엔진이 한다 — 서버의 `input_format.pattern`을 그대로 써야 서버 규칙과 어긋나지 않는다. 지금 `GET .../fields`는 `format_label`·`format_example`만 주고 `pattern`은 주지 않으므로, `FIELD-CHECK-API.md` "아직 없는 항목"에 이미 후보로 적힌 `GET /api/input-formats`(코드·이름·예시·`pattern`)를 둔다. LLM은 판정하지 않는다 (R3) |
| 동작 | 서버는 ① 숫자 4개가 모두 0인지 ② 서버에 있는 조건(`fields_confirmed_at`이 채워져 있음)을 본다. 모두 맞으면 `status`를 `성공`으로, 하나라도 아니면 `반려`로 바꾸고 `reject_reason`=`CONDITION_UNMET`을 남긴다 (R9 "조건이 남은 채 완성을 요청하면 반려", `DATA-MODEL.md` `reject_reason`). 이 요청 자체가 R9의 "사용자가 완성본을 최종 확인"이다 |
| 출력 | `200`. `{"draft": {"id", "status": "성공", "step": "review"}}` 또는 `{"draft": {"id", "status": "반려", "step": "review", "reject_reason": "CONDITION_UNMET"}}` (`OCR-API.md`처럼 결과가 `반려`여도 요청은 처리됐으므로 `200`) |
| 실패 응답 | 숫자 4개가 다 없거나 0 이상의 정수가 아니면 `400 INVALID_COMPLETE_REQUEST`. 그 외 공통 규칙 |
| 성공 뒤 | 브라우저가 감지 결과·검토 제안을 지운다 (T4 "처리 목적 달성 시점", `pii-items.md` 1절). 서버에는 지울 것이 없다 |
| 한계 | 숫자는 브라우저가 보낸 값이라 서버가 참인지 확인할 수 없다. 이 서비스는 실제 기관에 아무것도 보내지 않으므로(R4·R10) 잘못된 숫자의 결과는 사용자 자신의 연습 결과에 그친다 |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-05 (LLM이 있으면) "사람이 확인하기 전에는 상태가 바뀌지 않는다", R9 |
| 화면이 쓰는 곳 | 서술형 검토 화면의 '완성하기' 버튼 |

### 입력·출력 예시
```
요청:
POST /api/drafts/1/review:start

응답(성공): 200
{"draft": {"id": 1, "status": "수정", "step": "review"}}

요청 (브라우저가 감지·결정·가리기를 마친 뒤):
POST /api/drafts/1/review:request
{"answers": [{"form_field_id": 31,
              "masked_text": "저는 [이름1]입니다. [전화번호1]로 연락 주세요.",
              "tokens": ["[이름1]", "[전화번호1]"]}]}

응답(성공): 200
{"suggestions": [{"form_field_id": 31, "kind": "문법",
                  "suggested_text": "저는 [이름1]입니다. 연락은 [전화번호1]로 부탁드립니다.",
                  "explanation": "(베트남어로 쓴 제안 이유)"}]}

요청 (가리지 않은 번호가 남아 있음):
POST /api/drafts/1/review:request
{"answers": [{"form_field_id": 31, "masked_text": "010-0000-1234로 연락 주세요.", "tokens": []}]}

응답(실패): 422
{"detail": {"code": "PII_REMAINING", "field_ids": [31]}}

요청:
POST /api/drafts/1:complete
{"remaining_required": 0, "unacknowledged_mismatches": 0, "undecided_suggestions": 1, "undecided_privacy": 0}

응답: 200
{"draft": {"id": 1, "status": "반려", "step": "review", "reject_reason": "CONDITION_UNMET"}}
```

## 기존 F-06 코드에서 바꿀 것 (`feat/f02-field-check-v2-leehyosang6950`)

| 지금 코드 | 바꿀 내용 |
| --- | --- |
| `get_review`: `field_answer`를 조인해 `answers[].value`를 돌려줌 | `form_field`만 읽어 항목 2 모양(`fields`)으로 |
| `request_review`: 본문 없이 서버 `field_answer.value`를 읽음 | 항목 3 입력(가린 답변 + 토큰 이름)을 받음 |
| `_mask_known_prior_info`: 서버에 저장된 사전 정보로 가림 | 지운다. 사전 정보 대조는 브라우저 몫 (`l3-masking.md` 2절) |
| (없음) | ⑤ 다시 검사 → `422 PII_REMAINING`, ⑦ 제안 토큰 검사, 토큰 유지 지시, `review_count` 제한 추가 |
| `review_suggestion` 저장과 멱등성 처리 | 지운다 |
| `decide_suggestion` (`PATCH .../review/suggestions/{id}`) | 엔드포인트를 지운다. 제안 결정은 브라우저가 들고 있는다 |
| `db.py` `field_answer`·`review_suggestion`·`prior_info` 테이블, `prior_info.py`, `crypto.py` | 서버 모델에서 뺀다 (`no-server-storage-user-input.md` "이 결정으로 바뀌는 것") |
| (없음) | 항목 1 `review:start`, 항목 4 `privacy-rules`, 항목 5 `:complete` 추가 |
| 프론트 `api/review.js`·`mocks/review.js`·`useAnswerReview.js` | 항목 2·3 모양에 맞추고, 감지 모달·토큰 처리·완성하기 추가 |

- 작업 브랜치는 `main`에서 딴다. 그래서 PR #26 브랜치를 그대로 `main`에 병합하지 않고, **`main`에서 딴 F-07 작업 브랜치에서 `review.py`를 이 문서대로 다시 만든다**. PR #26에서 가져올 것은 L3 프롬프트·응답 검사(`llm.py` `review_answers`, `_validate_suggestion_shape`)와 테스트 틀이다

## 아직 없는 항목
- `GET /api/input-formats` — 브라우저 규칙 엔진이 쓸 형식 목록. `FIELD-CHECK-API.md` 담당 영역이라 그 문서에 추가한다
- `DATA-MODEL.md` 반영 (PM): `draft.review_count` 추가, `prior_info`·`field_answer`·`privacy_detection`·`review_suggestion`을 서버 모델에서 빼기 (결정 기록에 이미 적힘)
- `VIRTUAL-FORM-API.md` 반영 (담당자): 입력값 저장·불일치 계산을 브라우저로, "`review`에서 값이 바뀌면 `writing`으로" 규칙 삭제, "아직 없는 항목"의 단계 전이 ②·③을 이 문서 항목 1·5로 연결

## 팀 확인이 필요한 것
> CLAUDE.md상 Claude가 정하지 않는 것(인수 조건·규칙 문구, MVP 범위, 다른 사람의 코드)이다. 추천안만 적는다.

| 항목 | 추천안 | 누가 |
| --- | --- | --- |
| R7·US-05 문구: '유지'도 토큰으로 보냄 | R7을 "결정 전에는 보내지 않고, 결정 뒤에도 감지된 값은 토큰으로 바꿔 보낸다"로, US-05 (LLM이 있으면) 인수 조건을 같은 뜻으로 고친다 (`l3-masking.md` 9절 #1) | 팀 (규칙·인수 조건은 팀이 직접 고침) |
| '사용자가 직접 가리기'(`[가림N]`)를 MVP에 넣을지 | 넣는다 — R7 예외 사례(자녀 병명·학교 이름)를 규칙으로 못 잡는 유일한 방법이고, 서버는 이미 `[가림N]`을 받도록 정했다 (`l3-masking.md` 9절 #2) | 팀 (`mvp-scope.md`) |
| 답변·감지 결과·제안을 브라우저 어디에 둘지 | API에는 영향이 없다. 작성 중 값은 탭을 닫으면 지워지는 곳에 두고, 사전 정보만 R11을 위해 기기에 남기되 사용자 동의를 받는 쪽을 추천 (`data-flow.md` 5절 #3) | 화면 담당·팀 |
| PR #26 코드를 위 방식대로 다시 만드는 것 | 위 "기존 F-06 코드에서 바꿀 것" 마지막 줄 | 이효상(PR #26 작성자)·F-07 담당 합의 |
| Gemini가 토큰을 지키는 비율 | 저장한 응답이 아니라 실제 호출로 확인 (`확인 필요`, `l3-masking.md` 9절 #5) | 개발자 / L3 동작 확인 때 |
