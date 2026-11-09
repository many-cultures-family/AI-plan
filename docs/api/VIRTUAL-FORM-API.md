> **이 문서는 다른 두 API 문서보다 근거가 약하다.** `DOC-UPLOAD-API.md`·`FIELD-CHECK-API.md`는 `backlog.md`에 쓰인 인수 조건(US-01~US-03)을 바탕으로 했지만, **F-04(가상 작성 환경·불일치 표시)는 `backlog.md`에 스토리와 인수 조건이 아직 없다** (`mvp-scope.md` 17·20행, `PRD.md` 47행, `ai-check-log.md` "2주차 - 1" — 초안 스토리를 한 번 버렸고 아직 새로 안 씀). 그래서 이 문서는 `mvp-scope.md`·`03-rules-states-llm.md`·`DATA-MODEL.md`만 보고 만든 **엔드포인트 제안**이고, 아래 "인수 조건이 없다" 항목이 먼저 해결돼야 테스트를 쓸 수 있는 상태다. 구현 전에 팀이 `backlog.md`에 F-04 스토리부터 추가해야 한다 (CLAUDE.md 규칙: 인수 조건은 Claude가 못 쓰고 팀이 쓴다).

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | 오늘은 없음 (다른 두 문서와 동일) |
| 전제 상태 | `draft.step`이 `writing`일 때만 다룬다. `prior_info`(사전 정보 입력)에서 `writing`으로 넘어가는 전이는 아래 "아직 없는 항목" 참고 — F-03(US-04) 쪽 일인지 F-04 쪽 일인지 아직 안 정해짐 |
| 가상 환경 | 여기서 다루는 값은 실제 기관에 **절대 전송하지 않는다** (R4). 사용자에게도 "연습" 화면임을 알리는 문구가 필요하지만 문구는 화면(F-04 프론트) 담당 |
| 불일치 계산 | 사전 정보와의 불일치는 **저장하지 않고 그때그때 계산한다** (`DATA-MODEL.md` 86행). 그래서 아래 조회·저장 API는 매번 `prior_info.value`와 비교해서 응답에 `mismatch` 결과를 같이 돌려준다 |

## 항목 1: 가상 작성 화면 데이터 조회 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/answers` `[제안]` |
| 입력 | 없음 |
| 출력 (성공) | `200`. 입력 항목마다: `field_id`, `label`, `format_code`, `required`, `value`(없으면 `null`), `prior_info_key`, `mismatch`(아래 구조), `review_pending`(서술형이면, F-06 소관이라 값만 전달) |
| `mismatch` 구조 | `prior_info_key`가 있고 그 사전 정보가 있을 때만 계산: `{"has_prior_info": true, "prior_value": "010-0000-1234", "differs": true, "acknowledged": false}`. `prior_info_key`가 없거나 연결된 사전 정보가 없으면 `{"has_prior_info": false}` |
| 실패 응답 | `404 DRAFT_NOT_FOUND`. `step`이 `writing`이 아니면 `409 DRAFT_STEP_INVALID` |
| 관련 인수 조건 | 없음 — `mvp-assumptions-questions.md` 26행 F-04 설명("입력값을 사전 정보와 비교해 다르면 칸에 불일치 표시")만 근거 |
| 화면이 쓰는 곳 | `DESIGN.md` — 가상 작성 환경 화면 (현재 `DESIGN.md`엔 이 화면 자체가 "아직 연결된 스토리가 없어 표에 안 넣었다"고 적혀 있음, 37행) |

## 항목 2: 입력값 저장 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `PUT /api/drafts/{draft_id}/answers/{field_id}` `[제안]` |
| 입력 | `{"value": "010-0000-5678"}` |
| 동작 | 형식 검증(`input_format.pattern`, R3)을 거쳐 `field_answer`를 만들거나 바꾼다. 저장 직후 `prior_info_key`가 있으면 사전 정보와 비교해 `mismatch`를 계산해 응답에 넣는다. 값이 바뀌면 그 항목의 `mismatch_acknowledged`는 거짓으로 되돌린다(사전 정보가 바뀐 경우와 같은 규칙, R11을 값 변경에도 적용 `[제안]`). 서술형(`long_text`)이면 기존 검토 제안·개인정보 감지 결과를 지운다(R6·R9, F-06·F-07 몫이라 이 문서는 "지운다"까지만 적음) |
| 출력 (성공) | `200`. `{"field_id": .., "value": .., "mismatch": {...}}` (항목 1과 같은 구조) |
| 실패 응답 | 형식이 `input_format.pattern`에 안 맞으면 `400 FORMAT_INVALID` (R3). 없는 `field_id`면 `404 FIELD_NOT_FOUND` |
| 관련 인수 조건 | 없음 (근거: `DATA-MODEL.md` `field_answer.value`, R3) |
| 화면이 쓰는 곳 | `DESIGN.md` 가상 작성 환경 (칸마다 입력) |

## 항목 3: 불일치 확인 처리 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/answers/{field_id}:acknowledge-mismatch` `[제안]` |
| 입력 | 없음 |
| 동작 | `field_answer.mismatch_acknowledged`를 참으로 바꾼다. "값은 사전 정보와 다르지만 일부러 그렇게 썼다"는 사용자 결정을 저장한다 (R3 예외: 이사 전 주소 칸) |
| 출력 (성공) | `200`. `{"field_id": .., "mismatch_acknowledged": true}` |
| 실패 응답 | `404 FIELD_NOT_FOUND`. 애초에 불일치가 없는 항목(`mismatch.differs`가 거짓)에 호출하면 `400 NO_MISMATCH` `[제안]` |
| 관련 인수 조건 | 없음 (근거: `DATA-MODEL.md` `field_answer.mismatch_acknowledged`, R9 성공 조건) |
| 화면이 쓰는 곳 | `DESIGN.md` 가상 작성 환경 (불일치 툴팁·모달의 "그대로 둔다" 버튼) |

### 입력·출력 예시
```
요청:
GET /api/drafts/1/answers

응답(성공): 200
{
  "answers": [
    {
      "field_id": 12, "label": "보호자 연락처", "format_code": "phone",
      "required": true, "value": "010-0000-5678",
      "mismatch": {
        "has_prior_info": true,
        "prior_value": "010-0000-1234",
        "differs": true,
        "acknowledged": false
      }
    }
  ]
}

요청:
PUT /api/drafts/1/answers/12
{"value": "010-0000-9999"}

응답(실패 예): 400
{"detail": {"code": "FORMAT_INVALID"}}

요청:
POST /api/drafts/1/answers/12:acknowledge-mismatch

응답(성공): 200
{"field_id": 12, "mismatch_acknowledged": true}
```

## 아직 없는 항목
> 다음에 추가한다.
- `prior_info` 입력(US-04, F-03)과 사전 정보 조회·등록 API — 이 문서는 F-04만 다룬다
- 서술형 답변 검토 제안(F-06)·개인정보 감지(F-07) API — `field_answer.value`가 바뀌면 지운다는 것만 이 문서에 적었고, 만드는 건 F-06·F-07 몫
- `prior_info` 입력완료 → `writing` 전이, `review` → 성공(작성완료) 전이 엔드포인트 (아래 "아직 정하지 못한 것" 참고)

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| **F-04 스토리·인수 조건이 `backlog.md`에 아직 없음.** 이 문서 전체가 그 전까지는 제안일 뿐이다 | 팀 / 가장 먼저 |
| `prior_info` 입력완료 → `writing` 전이를 누가(F-03 쪽? F-04 쪽?) 어떤 조건(연결된 사전 정보가 모두 채워졌을 때?)으로 만들지 | 팀 / 구현 전 |
| `review` → 성공(작성완료) 전이(`mvp-scope.md` 17행엔 F-04 몫으로 적혀 있지만, 실제 조건(R9: 서술형 검토·개인정보 결정까지 포함)은 F-06·F-07과 겹친다 | 팀 / F-06·F-07 범위가 정해진 뒤 |
| 값이 바뀌면 `mismatch_acknowledged`를 되돌리는 것(R11을 값 변경에도 적용)이 맞는지 — R11 원문은 "사전 정보가 바뀌면"이지 "입력값이 바뀌면"이 아니다 | 팀 / 구현 전 |
| 연결된 사전 정보 자체가 없을 때(`has_prior_info: false`) 그 항목을 필수로 둘지, 사전 정보 입력(F-03)으로 돌려보낼지 | 팀 / 구현 전 |
| 경로 이름(`:acknowledge-mismatch` 콜론 표기 등)을 `FIELD-CHECK-API.md`와 같은 스타일로 계속 쓸지 | 개발자1·2 합의 → PM 반영 |
| `backend/app/db.py`에 `field_answer`, `prior_info` 테이블이 아직 없음. `DATA-MODEL.md` 35~39·63~65행 필드 그대로 추가 필요 | 개발자1 / 구현 전 |
