## 공통 규칙
> `DOC-UPLOAD-API.md`의 공통 규칙(기본 주소 `/api`, 응답은 JSON, 오류 응답 `{"detail": {"code": "<오류 코드>"}}`, 서버 파일 경로는 응답에 넣지 않음)을 그대로 따른다. 여기서는 이 문서에만 해당하는 것만 적는다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. **단, 서버 쪽 구현(auth 라우터·세션)은 아직 없다** — stepping-stone `origin/main`의 `backend/app/main.py`는 `drafts.router`만 등록돼 있고 로그인 관련 라우터·세션 처리가 없다(프론트 로그인 화면만 구현됨). 명세대로라면 세션이 없을 때 `401 LOGIN_REQUIRED`, 작성 건이 본인 것이 아니면 `403 FORBIDDEN_DRAFT`, 없는 작성 건이면 `404 DRAFT_NOT_FOUND`다 (`LOGIN-API.md` "다른 API의 권한 규칙", US-01·US-02 권한). 서버 구현은 별도 태스크로 먼저 끝나야 한다 |
| 전제 상태 | `draft.step`이 `field_check`이고 **`draft.status`가 `수정`**일 때만 다룬다. `step` 대응표: `DATA-MODEL.md` 93~101행. `field_check` 이전(`upload`)이면 `409 DRAFT_STEP_INVALID` `[제안]`. `status`가 `수정`이 아니면(반려·성공·취소인데 `step`이 `field_check`로 남아 있는 경우 포함) `409 DRAFT_NOT_EDITABLE` `[제안]` — `step`만 보고 `status`를 안 보면 반려·성공·취소된 작성 건에도 추론·저장이 통과해버린다. OCR·인식완료 전이 자체는 US-01 #2·#3(F-01) 범위라 이 문서에서 만들지 않는다 |
| 사용 언어 | 모국어 설명(`form_field.description`)은 `user.language`로 만든다. **단, 지금 프론트(`frontend/src/api/documents.js`)는 이미 `getValidationResult(documentId, lang)`로 `GET /documents/{id}/validation?lang=`을 부르고 있어, 이 문서의 "서버가 언어를 정한다"·"경로가 `/drafts/{id}/fields`"와 계약이 다르다.** 아래 "아직 정하지 못한 것" 참고 |
| 날짜시간 형식 | 모든 날짜시간 값은 **UTC, ISO 8601 + `Z` 접미사**로 돌려준다 (예: `2026-11-09T10:00:00Z`). `backend/app/db.py`가 SQLite `CURRENT_TIMESTAMP`(UTC, 시간대 표기 없음)를 그대로 쓰므로, 응답을 만들 때 `Z`를 붙여 변환한다 `[제안]` — KST로 보여줄지는 프론트가 변환 |

## 항목 1: 입력 항목 목록 조회 (기능 ID: F-02 / 스토리: US-02)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/fields` `[제안]` |
| 입력 | 없음 (경로의 `draft_id`만) |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`, `fields_confirmed_at`, `reanalysis_count`)와 `fields`(배열: `id`, `label`, `format_code`, `format_label`, `format_example`, `required`, `prior_info_key`, `description`, `bbox`, `flagged_wrong`), 검증 실패 항목이 있으면 `errors`(배열: `field_id`, `code`) |
| `errors`는 저장하지 않고 계산한다 `[제안]` | `form_field`에 오류를 담는 컬럼을 따로 두지 않는다. `GET`으로 조회할 때마다 저장된 `format_code`·`required`를 허용 목록과 대조해 그 자리에서 `errors`를 계산한다 — `DATA-MODEL.md` 86행이 사전 정보 불일치를 저장 안 하고 매번 계산하는 것과 같은 방식이다. 허용 목록 밖의 `format_code`도 **L1이 준 값 그대로 저장**한다(`null`로 바꾸지 않는다) — 그래야 뭐라고 잘못 추론했는지 남아서 재분석·디버깅에 쓸 수 있다 |
| `format_label`·`format_example` | `input_format.label`·`input_format.example`을 `format_code`로 찾아 각 항목에 같이 넣는다. US-02 1번째 인수 조건("입력 형식(예: 010-0000-0000, YYYY.MM.DD)" 표시)을 만족하려면 필요하다. 매번 조인하는 대신 `GET /api/input-formats` 같은 별도 목록 API를 둘지는 팀이 정할 수 있다 |
| 실패 응답 | `401 LOGIN_REQUIRED`, `403 FORBIDDEN_DRAFT`, `404 DRAFT_NOT_FOUND`. `step`이 `field_check`가 아니면 `409 DRAFT_STEP_INVALID`. `status`가 `수정`이 아니면 `409 DRAFT_NOT_EDITABLE` |
| 권한 | 로그인한 본인만 (위 공통 규칙) |
| 관련 인수 조건 | `backlog.md` US-02 1번째 인수 조건 (원본과 나란히 목록 표시) |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 |

> 원본 파일(PDF·이미지)을 화면에 나란히 띄우는 API는 이 문서에서 다루지 않는다. `DOC-UPLOAD-API.md` "아직 없는 항목"에 "원본 파일 보기"가 이미 미정으로 적혀 있고, 이게 없으면 US-02 1번째 인수 조건을 끝까지 만족할 수 없다. F-01 담당자와 기한을 먼저 정해야 한다.

## 항목 2: 입력 항목 추론·재분석 (기능 ID: F-02 / 스토리: US-02, US-03)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/fields:infer` `[제안]` |
| 입력 | 최초 추론: 본문 없음(또는 빈 객체). 재분석(US-03): `{"flagged_field_ids": [12, 15]}` — '원본과 다름'으로 표시한 `form_field.id` 1개 이상 |
| 동작 | L1(`03` 3-4)을 호출한다. 보내는 것: `document.masked_text`, 각 항목의 `bbox`·`label`(재분석이면 기존 항목 전체 + `flagged_field_ids`), `user.language`. **보내지 않는 것**: 원본 파일, 가리기 전 OCR 텍스트, 사전 정보, 사용자가 입력한 값 (`DATA-MODEL.md` "LLM에 보내지 않을 정보") |
| 규칙 검증 | L1 결과를 저장하기 전에 모든 항목에 `format_code`(허용 목록 안)·`required`가 있는지 검사한다(R2). 실패한 항목도 `fields` 배열에서 빼지 않고 그대로 돌려주되, `errors` 배열에 `{"field_id": .., "code": "FORMAT_CODE_INVALID"}`(허용 목록에 없음) 또는 `{"field_id": .., "code": "REQUIRED_MISSING"}`(필수 여부가 비어 있음)를 추가한다 — US-02 3번째 인수 조건·US-03 3번째 인수 조건("어느 항목이 어떤 검증에 실패했는지 사용자 언어로 보여 준다")은 '수정 유지냐 반려냐'와 무관하게 이 `errors` 자리가 있어야 지킬 수 있다 |
| 재분석 때 id 교체 | 재분석이면 기존 `form_field` 행을 **지우고 새 행으로 바꾼다** (새 `id` 발급). 그래서 응답의 `flagged_wrong`은 전부 거짓으로 돌아온다. `flagged_field_ids`에 이미 지워졌거나 다른 작성 건 소유인 `id`가 섞여 있으면 `404 FIELD_NOT_FOUND`로 거절한다(소유 여부를 굳이 구분해 `403`을 주지 않는다, 단순화) `[제안]`. `fields_confirmed_at`은 비운다(US-02·US-03, `DATA-MODEL.md` 43행) |
| 세 가지 요청을 구분한다 `[제안]` | 본문에 `flagged_field_ids` **키 자체가 없음**(최초 추론, 또는 사용자가 버튼을 두 번 눌러 생긴 단순 중복 호출) / `flagged_field_ids` **키는 있지만 빈 배열** `[]`(재분석을 시도했는데 아무것도 표시 안 함, 잘못된 요청) / `flagged_field_ids`에 **값이 1개 이상**(정상 재분석) — 이 셋을 구분해야 아래 "중복 호출"과 "재분석 실패 응답" 규칙이 서로 겹치지 않는다 |
| 중복 호출(멱등성) | `flagged_field_ids` **키가 없고** 이미 `fields`가 저장돼 있으면, L1을 다시 부르지 않고 저장된 `fields`·`errors`를 그대로 돌려준다(`200`) `[제안]` — 사용자가 버튼을 두 번 누르는 것만으로 L1 비용이 중복되지 않게 한다. `fields`가 아직 없으면(진짜 최초 호출) L1을 부른다 |
| 출력 (성공) | `200`. `fields`(전체, 통과·실패 모두 포함) + `errors`(실패분만). 재분석이면 `draft.reanalysis_count`를 1 올려 함께 돌려준다 |
| 재분석 실패 응답 | `flagged_field_ids` **키가 있는데 빈 배열**이면 `400 NO_FIELDS_FLAGGED` (US-03 인수 조건 2번, L1을 부르지 않는다) — 키 자체가 없는 경우(위 "중복 호출")와는 다르다. `reanalysis_count`가 이미 3이면 `409 REANALYSIS_LIMIT_EXCEEDED` `[제안]` (요청 빈도 제한이 아니라 이 작성 건의 누적 횟수 제한이라 `429`보다 `409`가 더 맞다. `DATA-MODEL.md` 44행 "3회까지"도 `[제안]`이라 팀 확인 필요) |
| L1 호출 실패 응답 | `502 LLM_CALL_FAILED` `[제안]` — Gemini 호출 자체가 실패(타임아웃·오류)했을 때. 이 경우 작성 건 상태·단계는 바꾸지 않고 사용자가 다시 시도할 수 있게 한다 |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-02 인수 조건 2·3번, US-03 전체 |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 (재분석 요청 버튼) |

## 항목 3: 입력 항목 확정 (기능 ID: F-02 / 스토리: US-02)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/fields:confirm` `[제안]` |
| 입력 | 없음 |
| 동작 | 지금 저장된 `fields`가 모두 규칙 검증(R2)을 통과했는지 다시 확인한다(화면의 버튼 비활성화만 믿지 않는다). 통과하면 `draft.fields_confirmed_at`을 채우고 `draft.step`을 `field_check` → `prior_info`로 바꾼다(`DATA-MODEL.md` step 대응표, backlog '항목확정') |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`, `fields_confirmed_at`) |
| 실패 응답 | 검증 실패 항목이 남아 있으면 `400 FIELDS_INVALID` `[제안]`, 응답 모양은 `{"detail": {"code": "FIELDS_INVALID", "errors": [{"field_id": .., "code": ..}]}}`처럼 오류 코드 바로 옆에 `errors` 배열을 같이 싣는다(공통 규칙의 `{"detail": {"code": ...}}` 모양을 확장) — **단, 이 실패가 `수정` 상태를 유지하는지(backlog US-02 인수 조건 3번) `반려`로 바꾸는지(`03` R2, `DATA-MODEL.md` `reject_reason=FIELD_INVALID`)는 서로 다르게 적혀 있어 팀이 정해야 한다 (바로 아래 "아직 정하지 못한 것" 1번)** |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-02 인수 조건 2·3·6번 |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 ('확인했어요' 버튼) |

### 입력·출력 예시
```
요청:
POST /api/drafts/1/fields:infer
{}

응답(성공, 검증 실패 1건 포함): 200
{
  "draft": {"id": 1, "status": "수정", "step": "field_check", "reanalysis_count": 0},
  "fields": [
    {
      "id": 12, "label": "보호자 연락처", "format_code": "phone",
      "format_label": "전화번호", "format_example": "010-0000-0000",
      "required": true, "prior_info_key": "phone",
      "description": "자녀의 보호자 전화번호를 적습니다",
      "bbox": {"page": 1, "x": 0.1, "y": 0.3, "w": 0.4, "h": 0.04},
      "flagged_wrong": false
    },
    {
      "id": 13, "label": "생년월일", "format_code": "resident_no",
      "format_label": null, "format_example": null,
      "required": true, "prior_info_key": "birth_date",
      "description": "태어난 날을 적습니다",
      "bbox": {"page": 1, "x": 0.1, "y": 0.4, "w": 0.4, "h": 0.04},
      "flagged_wrong": false
    }
  ],
  "errors": [{"field_id": 13, "code": "FORMAT_CODE_INVALID"}]
}
```
`format_code`가 `resident_no`(허용 목록 밖, R8로 애초에 목록에 없는 형식)처럼 L1이 잘못 추론한 값이라도 `null`로 바꾸지 않고 그대로 저장한다. `format_label`·`format_example`은 허용 목록에 있는 코드에만 채워지므로 이 경우엔 `null`이다.
```

요청(재분석):
POST /api/drafts/1/fields:infer
{"flagged_field_ids": [12]}

응답(실패 예): 400
{"detail": {"code": "NO_FIELDS_FLAGGED"}}

요청(확정, 검증 실패 남아 있을 때):
POST /api/drafts/1/fields:confirm

응답(실패 예): 400
{"detail": {"code": "FIELDS_INVALID", "errors": [{"field_id": 13, "code": "FORMAT_CODE_INVALID"}]}}

요청(확정, 성공):
POST /api/drafts/1/fields:confirm

응답(성공): 200
{"draft": {"id": 1, "status": "수정", "step": "prior_info", "fields_confirmed_at": "2026-11-09T10:00:00Z"}}
```

## 아직 없는 항목
> 다음에 추가한다.
- 사용자가 L1 제안 항목을 직접 고치는 기능(라벨·형식·필수 여부 수정). 아래 "아직 정하지 못한 것" 2번 참고
- 원본 파일 보기 API (F-01 쪽에서 정할 것)
- `format_label`·`format_example`을 필드마다 중복으로 넣는 대신 `GET /api/input-formats` 같은 별도 목록 API로 뺄지

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| 규칙 검증 실패 시 상태: `수정` 유지(backlog US-02·US-03 인수 조건)인지 `반려`(`03` R2, `DATA-MODEL.md` 127행에 이미 같은 충돌이 적혀 있음)인지 | 팀 / 구현 전 — 이 문서의 `FIELDS_INVALID` 응답 설계가 여기에 달려 있다 |
| 개발 태스크 설명엔 "사용자가 수정 및 확정한 입력값 저장 처리"가 있는데, `backlog.md` US-02 인수 조건에는 직접 수정 항목이 없고 '원본과 다름' 표시 + 재분석만 있다. 사용자가 L1 제안을 직접 고치는 기능을 이번에 넣을지 | 팀 / 구현 전 — 넣는다면 `PATCH /api/drafts/{draft_id}/fields/{field_id}` 같은 엔드포인트가 추가로 필요하다 |
| L1 호출 실패(타임아웃·오류) 때 재시도 횟수를 둘지, 바로 `502`로 사용자에게 알릴지 | 개발자1 / 구현 전 (`first-feature.md`에 이미 "L1 호출의 키·실패 동작·저장 응답을 먼저 정해야 함"으로 보류돼 있던 항목) |
| 경로 이름(`:infer`, `:confirm` 콜론 표기)을 이 팀이 쓰는 방식인지, `DOC-UPLOAD-API.md`처럼 평범한 명사 경로로 바꿀지 | 개발자1·2 합의 → PM 반영 |
| `backend/app/db.py`에 `form_field` 테이블이 아직 없음. `DATA-MODEL.md` 53~62행 필드 그대로 추가 필요 | 개발자1 / 구현 전 |
| **지금 프론트(`frontend/src/api/documents.js`)는 이미 `getValidationResult`로 `GET /documents/{id}/validation?lang=`을 부르고 `pass`/`fail`/`warn` 상태를 쓰는 다른 계약으로 구현돼 있다.** 이 문서(`/drafts/{id}/fields`, 서버가 언어 결정)로 바꾸려면 프론트를 다시 구현해야 한다. 병합 후 전환 계획(계약 교체 시점, 당분간 두 계약을 병행할지)을 합의해야 한다 | 개발자1·2 / 병합 전 |
| `writing → review`, `review → 성공` 등 단계 전이 담당(F-01/F-03/F-04/F-06/F-07 중 누구)을 이 문서 하나가 아니라 API 문서 전체에서 한 번에 정리해야 한다 (`VIRTUAL-FORM-API.md` "아직 없는 항목" 참고) | 팀 / 구현 전 |
| 이번에 추가한 `status`(=`수정`) 검사·`401`/`403`/`404` 인증 규칙·UTC `Z` 타임스탬프 표기가 다른 문서들과 일관되는지 | 리뷰어 확인 |
