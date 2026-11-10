> **이 문서는 다른 두 API 문서보다 근거가 약하다.** `DOC-UPLOAD-API.md`·`FIELD-CHECK-API.md`는 `backlog.md`에 쓰인 인수 조건(US-01~US-03)을 바탕으로 했지만, **F-04(가상 작성 환경·불일치 표시)는 `backlog.md`에 스토리와 인수 조건이 아직 없다** (`mvp-scope.md` 17·20행, `PRD.md` 47행, `ai-check-log.md` "2주차 - 1" — 초안 스토리를 한 번 버렸고 아직 새로 안 씀). 그래서 이 문서는 `mvp-scope.md`·`03-rules-states-llm.md`·`DATA-MODEL.md`만 보고 만든 **엔드포인트 제안**이고, 아래 "인수 조건이 없다" 항목이 먼저 해결돼야 테스트를 쓸 수 있는 상태다. 구현 전에 팀이 `backlog.md`에 F-04 스토리부터 추가해야 한다 (CLAUDE.md 규칙: 인수 조건은 Claude가 못 쓰고 팀이 쓴다). **이 PR은 "제안"으로만 병합하는 것을 권장한다.**

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. **단, 서버 쪽 구현(auth 라우터·세션)은 아직 없다** — stepping-stone `origin/main`의 `backend/app/main.py`는 `drafts.router`만 등록돼 있다(프론트 로그인 화면만 구현됨). 명세대로라면 세션이 없을 때 `401 LOGIN_REQUIRED`, 작성 건이 본인 것이 아니면 `403 FORBIDDEN_DRAFT`, 없는 작성 건이면 `404 DRAFT_NOT_FOUND`다 (`LOGIN-API.md` "다른 API의 권한 규칙"). 서버 구현은 별도 태스크로 먼저 끝나야 한다 |
| 전제 상태 | `draft.step`이 `writing` **또는 `review`**일 때 다룬다(아래 "값이 바뀌면 review→writing" 참고). `status`가 `수정`이 아니면 `409 DRAFT_NOT_EDITABLE` `[제안]`. `prior_info`(사전 정보 입력)에서 `writing`으로 넘어가는 전이는 아래 "아직 없는 항목" 참고 — F-03(US-04) 쪽 일인지 F-04 쪽 일인지 아직 안 정해짐 |
| 가상 환경 | 여기서 다루는 값은 실제 기관에 **절대 전송하지 않는다** (R4). 사용자에게도 "연습" 화면임을 알리는 문구가 필요하지만 문구는 화면(F-04 프론트) 담당 |
| 불일치 계산 | 사전 정보와의 불일치는 **저장하지 않고 그때그때 계산한다** (`DATA-MODEL.md` 86행). 그래서 아래 조회·저장 API는 매번 `prior_info.value`와 비교해서 응답에 `mismatch` 결과를 같이 돌려준다. 어느 글자가 다른지(글자 단위 비교·강조 표시)는 **프론트 몫**이다. 서버는 `value`·`prior_value`·`differs`(참거짓)만 준다 (R3 "차이 나는 글자를 화면에서 표시한다"는 이 값들로 프론트가 만든다) |
| 날짜시간 형식 | 모든 날짜시간 값은 UTC, ISO 8601 + `Z` 접미사 (예: `2026-11-09T10:00:00Z`). `backend/app/db.py`의 SQLite `CURRENT_TIMESTAMP`(UTC)를 그대로 쓰는 값은 응답을 만들 때 `Z`를 붙여 변환한다 `[제안]` |

## 항목 1: 가상 작성 화면 데이터 조회 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/answers` `[제안]` |
| 입력 | 없음 |
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`) + `answers`(배열). 항목마다: `field_id`, `label`, `format_code`, `format_label`, `format_example`, `required`, `prior_info_key`, `description`, `options`(선택형이면 선택지 배열, 아니면 `null`), `value`(없으면 `null`), `mismatch`(아래 구조) |
| `mismatch` 구조 | `prior_info_key`가 있고 그 사전 정보가 있을 때만 계산: `{"has_prior_info": true, "prior_value": "010-0000-1234", "differs": true, "mismatch_acknowledged": false}`. `prior_info_key`가 없거나 연결된 사전 정보가 없으면 `{"has_prior_info": false}`. 필드 이름은 `field_answer.mismatch_acknowledged`와 똑같이 맞춘다 |
| 실패 응답 | `401 LOGIN_REQUIRED`, `403 FORBIDDEN_DRAFT`, `404 DRAFT_NOT_FOUND`. `step`이 `writing`·`review`가 아니면 `409 DRAFT_STEP_INVALID`. `status`가 `수정`이 아니면 `409 DRAFT_NOT_EDITABLE` |
| 관련 인수 조건 | 없음 — `mvp-assumptions-questions.md` 26행 F-04 설명("입력값을 사전 정보와 비교해 다르면 칸에 불일치 표시")만 근거 |
| 화면이 쓰는 곳 | `DESIGN.md` — 가상 작성 환경 화면 (현재 `DESIGN.md`엔 이 화면 자체가 "아직 연결된 스토리가 없어 표에 안 넣었다"고 적혀 있음, 37행) |

> 서술형(F-06)·개인정보 감지(F-07) 관련 값(검토 제안 상태 등)은 이 응답에 넣지 않는다. 근거가 되는 모델(`review_suggestion`, `privacy_detection`)이 있는 건 맞지만, 그 상태를 어떻게 요약해 보여줄지는 F-06·F-07 문서가 정할 일이라 여기서 임의로 필드를 만들지 않는다.

## 항목 2: 입력값 저장 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `PUT /api/drafts/{draft_id}/answers/{field_id}` `[제안]` |
| 입력 | `{"value": "010-0000-5678"}` |
| 형식 검증 | `format_code`별로 다르게 본다(R3): 일반 형식(`phone`·`date`·`email`·`number`·`name`·`address`·`short_text`)은 `input_format.pattern` 정규식. `long_text`(서술형)는 `pattern`이 없으므로 **어떤 값이든 통과**시킨다(빈 문자열 포함 — 필수 미입력 여부는 아래 참고). `choice`(선택형)는 정규식 대신 **`form_field.options` 안에 있는 값인지** 검사한다. 어느 경우든 안 맞으면 `400 FORMAT_INVALID`로 통일한다 |
| 필수 미입력은 여기서 안 막음 | `required`인데 `value`가 비어도 저장은 허용한다(작성 중에는 비어 있을 수 있다). 필수 누락 여부는 **성공 조건(R9) 확인 때**(F-06·F-07 쪽 "최종 확인" API) 판정한다. 이 문서는 형식이 맞는지만 본다 |
| 동작 | 형식 검증을 거쳐 `field_answer`를 만들거나 바꾼다. 저장 직후 `prior_info_key`가 있으면 사전 정보와 비교해 `mismatch`를 계산해 응답에 넣는다. 값이 바뀌면 그 항목의 `mismatch_acknowledged`는 거짓으로 되돌린다(사전 정보가 바뀐 경우와 같은 규칙, R11을 값 변경에도 적용 `[제안]`). 서술형(`long_text`)이면 기존 검토 제안·개인정보 감지 결과를 지운다(R6·R9, F-06·F-07 몫이라 이 문서는 "지운다"까지만 적음) |
| `review` 단계에서 값이 바뀌면 | `draft.step`을 `review` → `writing`으로 되돌린다 `[제안]` — `DATA-MODEL.md` 64행("서술형 값이 바뀌면 검토 제안을 지우고 다시 검토한다")과 R11(성공→수정)의 취지를 확장한 것이다. `step`이 `writing`일 때만 저장을 허용하면, 검토 단계에서 값을 고치려 할 때 `409`로 막혀 재검토 자체가 불가능해진다 |
| 출력 (성공) | `200`. `{"field_id": .., "value": .., "mismatch": {...}}` (항목 1과 같은 구조), `step`이 바뀌었으면 `draft.step`도 같이 돌려준다 |
| 실패 응답 | 형식이 안 맞으면 `400 FORMAT_INVALID`. 없는 `field_id`면 `404 FIELD_NOT_FOUND`. 그 외는 공통 규칙의 `401`/`403`/`404`/`409` |
| 관련 인수 조건 | 없음 (근거: `DATA-MODEL.md` `field_answer.value`, R3, R6, R11) |
| 화면이 쓰는 곳 | `DESIGN.md` 가상 작성 환경 (칸마다 입력) |

## 항목 3: 불일치 확인 처리 (기능 ID: F-04)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/answers/{field_id}:acknowledge-mismatch` `[제안]` |
| 입력 | 없음 |
| 동작 | `field_answer.mismatch_acknowledged`를 참으로 바꾼다. "값은 사전 정보와 다르지만 일부러 그렇게 썼다"는 사용자 결정을 저장한다 (R3 예외: 이사 전 주소 칸) |
| 출력 (성공) | `200`. `{"field_id": .., "mismatch_acknowledged": true}` |
| 실패 응답 | `404 FIELD_NOT_FOUND`. 애초에 불일치가 없는 항목(`mismatch.differs`가 거짓)에 호출하면 `400 NO_MISMATCH` `[제안]`. 그 외는 공통 규칙의 `401`/`403`/`404`/`409` |
| 관련 인수 조건 | 없음 (근거: `DATA-MODEL.md` `field_answer.mismatch_acknowledged`, R9 성공 조건) |
| 화면이 쓰는 곳 | `DESIGN.md` 가상 작성 환경 (불일치 툴팁·모달의 "그대로 둔다" 버튼) |

### 입력·출력 예시
```
요청:
GET /api/drafts/1/answers

응답(성공): 200
{
  "draft": {"id": 1, "status": "수정", "step": "writing"},
  "answers": [
    {
      "field_id": 12, "label": "보호자 연락처", "format_code": "phone",
      "format_label": "전화번호", "format_example": "010-0000-0000",
      "required": true, "prior_info_key": "phone",
      "description": "자녀의 보호자 전화번호를 적습니다",
      "options": null,
      "value": "010-0000-5678",
      "mismatch": {
        "has_prior_info": true,
        "prior_value": "010-0000-1234",
        "differs": true,
        "mismatch_acknowledged": false
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
- 단계 전이 엔드포인트 3개 — ① `prior_info` 입력완료 → `writing`, ② `writing` → `review`, ③ `review` → 성공(작성완료). 셋 다 이 문서 혼자 정할 수 없고, F-01·F-03·F-04·F-06·F-07에 흩어진 담당을 **API 문서 전체에서 한 번에** 정리해야 한다 (아래 "아직 정하지 못한 것" 참고)

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| **F-04 스토리·인수 조건이 `backlog.md`에 아직 없음.** 이 문서 전체가 그 전까지는 제안일 뿐이다 | 팀 / 가장 먼저 |
| `writing`·`review`·`prior_info`·(F-06·F-07 쪽) 단계 전이 3개(위 "아직 없는 항목" 참고)를 누가 만들지 — F-02(`FIELD-CHECK-API.md`)·F-08(`DRAFT-STATUS-API.md`)에도 같은 질문이 흩어져 있어, 한 문서(예: `DATA-MODEL.md`나 새 `STEP-TRANSITIONS.md`)에 모아 정리할지 | 팀(PM) / 구현 전 |
| 값이 바뀌면 `mismatch_acknowledged`를 되돌리는 것(R11을 값 변경에도 적용), `review` 단계에서 값이 바뀌면 `step`을 `writing`으로 되돌리는 것 — 둘 다 R11·R6 원문 그대로가 아니라 취지를 확장 해석한 것이라 팀 확인 필요 | 팀 / 구현 전 |
| 연결된 사전 정보 자체가 없을 때(`has_prior_info: false`) 그 항목을 필수로 둘지, 사전 정보 입력(F-03)으로 돌려보낼지 | 팀 / 구현 전 |
| `choice`(선택형) 형식 오류와 일반 형식 오류를 같은 `FORMAT_INVALID` 코드로 묶은 게 맞는지, 따로 코드를 둘지(예: `CHOICE_NOT_ALLOWED`) | 개발자1·2 합의 |
| 경로 이름(`:acknowledge-mismatch` 콜론 표기 등)을 `FIELD-CHECK-API.md`와 같은 스타일로 계속 쓸지 | 개발자1·2 합의 → PM 반영 |
| `backend/app/db.py`에 `field_answer`, `prior_info` 테이블이 아직 없음. `DATA-MODEL.md` 35~39·63~65행 필드 그대로 추가 필요 | 개발자1 / 구현 전 |
