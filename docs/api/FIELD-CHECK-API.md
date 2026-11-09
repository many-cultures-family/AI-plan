## 공통 규칙
> `DOC-UPLOAD-API.md`의 공통 규칙(기본 주소 `/api`, 응답은 JSON, 오류 응답 `{"detail": {"code": "<오류 코드>"}}`, 서버 파일 경로는 응답에 넣지 않음)을 그대로 따른다. 여기서는 이 문서에만 해당하는 것만 적는다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | **오늘(초안 시점)은 없음.** `DOC-UPLOAD-API.md`와 같은 상태. Google 로그인(`LOGIN-API.md`)이 구현되면 "작성 건은 올린 본인만" 조건(US-02 권한 인수 조건)을 여기도 적용해야 한다 |
| 전제 상태 | 아래 모든 요청은 `draft.step`이 `field_check`일 때만 다룬다. (`step` 대응표: `DATA-MODEL.md` 93~101행) `field_check` 이전(`upload`)이면 아직 OCR·인식이 끝나지 않은 것이므로 `409 DRAFT_STEP_INVALID` `[제안]`. OCR·인식완료 전이 자체는 US-01 #2·#3(F-01) 범위라 이 문서에서 만들지 않는다 |
| 사용 언어 | 모국어 설명(`form_field.description`)은 `user.language`로 만든다. 로그인이 없는 동안은 시드 사용자 값(`backend/app/db.py`의 `SEED_LANGUAGE`, 현재 `vi`)을 쓴다 |

## 항목 2: 입력 항목 목록 조회 (기능 ID: F-02 / 스토리: US-02)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/fields` `[제안]` |
| 입력 | 없음 (경로의 `draft_id`만) |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`, `fields_confirmed_at`, `reanalysis_count`)와 `fields`(배열: `id`, `label`, `format_code`, `required`, `prior_info_key`, `description`, `bbox`, `flagged_wrong`) |
| 실패 응답 | 작성 건이 없으면 `404 DRAFT_NOT_FOUND`. `step`이 `field_check`가 아니면 `409 DRAFT_STEP_INVALID` `[제안]` |
| 권한 | 오늘은 없음 (위 공통 규칙) |
| 관련 인수 조건 | `backlog.md` US-02 1번째 인수 조건 (원본과 나란히 목록 표시) |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 |

> 원본 파일(PDF·이미지)을 화면에 나란히 띄우는 API는 이 문서에서 다루지 않는다. `DOC-UPLOAD-API.md` "아직 없는 항목"에 "원본 파일 보기"가 이미 미정으로 적혀 있어, F-01 쪽에서 먼저 정해야 한다. 정해지면 이 화면은 그 주소를 그대로 쓴다.

## 항목 3: 입력 항목 추론·재분석 (기능 ID: F-02 / 스토리: US-02, US-03)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/fields:infer` `[제안]` |
| 입력 | 최초 추론: 본문 없음(또는 빈 객체). 재분석(US-03): `{"flagged_field_ids": [12, 15]}` — '원본과 다름'으로 표시한 `form_field.id` 1개 이상 |
| 동작 | L1(`03` 3-4)을 호출한다. 보내는 것: `document.masked_text`, 각 항목의 `bbox`·`label`(재분석이면 기존 항목 전체 + `flagged_field_ids`), `user.language`. **보내지 않는 것**: 원본 파일, 가리기 전 OCR 텍스트, 사전 정보, 사용자가 입력한 값 (`DATA-MODEL.md` "LLM에 보내지 않을 정보") |
| 규칙 검증 | L1 결과를 저장하기 전에 모든 항목에 `format_code`(허용 목록 안)·`required`가 있는지 검사한다(R2). 재분석이면 기존 `form_field` 행을 새 결과로 바꾸고 `fields_confirmed_at`을 비운다(US-02·US-03, `DATA-MODEL.md` 43행) |
| 출력 (성공) | `200`. 항목 2와 같은 `fields` 배열(검증 통과분). 재분석이면 `draft.reanalysis_count`를 1 올려 함께 돌려준다 |
| 재분석 실패 응답 | `flagged_field_ids`가 없거나 빈 배열이면 `400 NO_FIELDS_FLAGGED` (US-03 인수 조건 2번, L1을 부르지 않는다). `reanalysis_count`가 이미 3이면 `429 REANALYSIS_LIMIT_EXCEEDED` `[제안]` (`DATA-MODEL.md` 44행 "3회까지"도 `[제안]`이라 팀 확인 필요) |
| L1 호출 실패 응답 | `502 LLM_CALL_FAILED` `[제안]` — Gemini 호출 자체가 실패(타임아웃·오류)했을 때. 이 경우 작성 건 상태·단계는 바꾸지 않고 사용자가 다시 시도할 수 있게 한다 |
| 권한 | 오늘은 없음 |
| 관련 인수 조건 | US-02 인수 조건 2·3번, US-03 전체 |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 (재분석 요청 버튼) |

## 항목 4: 입력 항목 확정 (기능 ID: F-02 / 스토리: US-02)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/fields:confirm` `[제안]` |
| 입력 | 없음 |
| 동작 | 지금 저장된 `fields`가 모두 규칙 검증(R2)을 통과했는지 다시 확인한다(화면의 버튼 비활성화만 믿지 않는다). 통과하면 `draft.fields_confirmed_at`을 채우고 `draft.step`을 `field_check` → `prior_info`로 바꾼다(`DATA-MODEL.md` step 대응표, backlog '항목확정') |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`, `fields_confirmed_at`) |
| 실패 응답 | 검증 실패 항목이 남아 있으면 `400 FIELDS_INVALID` `[제안]` — **단, 이 실패가 `수정` 상태를 유지하는지(backlog US-02 인수 조건 3번) `반려`로 바꾸는지(`03` R2, `DATA-MODEL.md` `reject_reason=FIELD_INVALID`)는 서로 다르게 적혀 있어 팀이 정해야 한다 (바로 아래 "아직 정하지 못한 것" 1번)** |
| 권한 | 오늘은 없음 |
| 관련 인수 조건 | US-02 인수 조건 2·3·6번 |
| 화면이 쓰는 곳 | `DESIGN.md` 입력 항목 확인 ('확인했어요' 버튼) |

### 입력·출력 예시
```
요청:
POST /api/drafts/1/fields:infer
{}

응답(성공): 200
{
  "draft": {"id": 1, "status": "수정", "step": "field_check", "reanalysis_count": 0},
  "fields": [
    {
      "id": 12, "label": "보호자 연락처", "format_code": "phone",
      "required": true, "prior_info_key": "phone",
      "description": "자녀의 보호자 전화번호를 적습니다",
      "bbox": {"page": 1, "x": 0.1, "y": 0.3, "w": 0.4, "h": 0.04},
      "flagged_wrong": false
    }
  ]
}

요청(재분석):
POST /api/drafts/1/fields:infer
{"flagged_field_ids": [12]}

응답(실패 예): 400
{"detail": {"code": "NO_FIELDS_FLAGGED"}}

요청(확정):
POST /api/drafts/1/fields:confirm

응답(성공): 200
{"draft": {"id": 1, "status": "수정", "step": "prior_info", "fields_confirmed_at": "2026-11-09T10:00:00"}}
```

## 아직 없는 항목
> 다음에 추가한다.
- 사용자가 L1 제안 항목을 직접 고치는 기능(라벨·형식·필수 여부 수정). 아래 "아직 정하지 못한 것" 2번 참고
- 원본 파일 보기 API (F-01 쪽에서 정할 것)

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| 규칙 검증 실패 시 상태: `수정` 유지(backlog US-02·US-03 인수 조건)인지 `반려`(`03` R2, `DATA-MODEL.md` 127행에 이미 같은 충돌이 적혀 있음)인지 | 팀 / 구현 전 — 이 문서의 `FIELDS_INVALID` 응답 설계가 여기에 달려 있다 |
| 개발 태스크 설명엔 "사용자가 수정 및 확정한 입력값 저장 처리"가 있는데, `backlog.md` US-02 인수 조건에는 직접 수정 항목이 없고 '원본과 다름' 표시 + 재분석만 있다. 사용자가 L1 제안을 직접 고치는 기능을 이번에 넣을지 | 팀 / 구현 전 — 넣는다면 `PATCH /api/drafts/{draft_id}/fields/{field_id}` 같은 엔드포인트가 추가로 필요하다 |
| `reanalysis_count` 상한 3회, 초과 시 `429`로 막을지 | 팀 (`DATA-MODEL.md`도 `[제안]`) |
| L1 호출 실패(타임아웃·오류) 때 재시도 횟수를 둘지, 바로 `502`로 사용자에게 알릴지 | 개발자1 / 구현 전 (`first-feature.md`에 이미 "L1 호출의 키·실패 동작·저장 응답을 먼저 정해야 함"으로 보류돼 있던 항목) |
| 경로 이름(`:infer`, `:confirm` 콜론 표기)을 이 팀이 쓰는 방식인지, `DOC-UPLOAD-API.md`처럼 평범한 명사 경로로 바꿀지 | 개발자1·2 합의 → PM 반영 |
| `backend/app/db.py`에 `form_field` 테이블이 아직 없음. `DATA-MODEL.md` 53~62행 필드 그대로 추가 필요 | 개발자1 / 구현 전 |
