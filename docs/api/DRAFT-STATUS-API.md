> F-08은 `backlog.md`에 US-06·US-07 인수 조건이 있다 (F-04와 다름). 다만 둘 다 **우선순위 '선택'**이고, US-07을 필수로 올릴지는 `PRD.md` 8절에 아직 미정으로 남아 있다. 이 문서는 인수 조건이 있는 부분부터 명세하고, 없는 부분(목록·필터)은 `[제안]`으로 채웠다.

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md`가 병합되어 로그인이 구현됐다(더 이상 "오늘은 없음"이 아니다). 세션이 없으면 `401 LOGIN_REQUIRED`. 작성 건이 본인 것이 아니면 `403 FORBIDDEN_DRAFT`. 없는 작성 건이면 `404 DRAFT_NOT_FOUND` (`LOGIN-API.md` "다른 API의 권한 규칙"). US-06 인수 조건의 '관리자'는 이 서비스에 관리자 역할이 없어(`mvp-scope.md`) 적용하지 않는다 — `PRD.md` 8절 93행에 이미 미정으로 적혀 있음 |
| 상태 이름 | `draft.status`(수정·반려·성공·취소)와 `draft.step`을 그대로 쓴다. 프론트 작업 설명의 '작성완료·검토완료·제출완료' 같은 이름은 `backlog.md`식 이름이라 `status`/`step`과 그대로 안 맞는다 (아래 "아직 정하지 못한 것" 1번) |
| 상태 검사(FIELD-CHECK·VIRTUAL-FORM과 다름) | `FIELD-CHECK-API.md`·`VIRTUAL-FORM-API.md`는 `status`가 `수정`일 때만 허용하지만, 이 문서의 제출·취소는 **여러 `status`에 걸쳐 동작하는 게 설계 의도**다(R10·R12). 그래서 "status가 수정이 아니면 막는다" 같은 일괄 규칙을 넣지 않았고, 각 항목마다 필요한 상태 조건을 따로 적는다 |
| 날짜시간 형식 | 모든 날짜시간 값은 UTC, ISO 8601 + `Z` 접미사 (예: `2026-11-09T12:00:00Z`). `backend/app/db.py`의 SQLite `CURRENT_TIMESTAMP`(UTC)를 그대로 쓰는 값은 응답을 만들 때 `Z`를 붙여 변환한다 `[제안]` |

## 항목 1: 작성 목록 조회 (기능 ID: F-08)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts` `[제안]` — `DOC-UPLOAD-API.md` "아직 없는 항목"에 있던 "작성 건 조회"를 여기서 채운다 |
| 입력 | 쿼리: `status`(수정·반려·성공·취소, 생략하면 전체) `[제안]` |
| 출력 (성공) | `200`. **로그인한 사용자 본인 소유의 작성 건만** 돌려준다 (다른 사용자의 작성 건은 목록에도 안 나온다 — 조회 자체를 막는 `FIELD-CHECK-API.md`의 `403 FORBIDDEN_DRAFT`와 달리, 목록은 애초에 본인 것만 쿼리한다). `drafts` 배열: `id`, `status`, `step`, `reject_reason`, `submitted_at`, `next_action`(아래 표) |
| `next_action` 코드 | `step`·`status`로 서버가 계산해서 주는 코드. 문구는 프론트 국제화가 만든다 (R3와 같은 방식): `UPLOAD`(수정+upload), `FIELD_CHECK`(수정+field_check), `PRIOR_INFO`(수정+prior_info), `WRITING`(수정+writing), `REVIEW`(수정+review), `REJECTED`(반려), `SUBMIT`(성공, `submitted_at` 없음), `DONE`(성공, `submitted_at` 있음) `[제안]` |
| 실패 응답 | `401 LOGIN_REQUIRED`. 그 외는 없음(빈 배열도 `200`) — 목록 API라 특정 작성 건에 대한 `403`/`404`는 해당 없음 |
| 관련 인수 조건 | 인수 조건 없음(목록·필터는 backlog에 스토리 자체가 없음). F-08 설명(`mvp-assumptions-questions.md` 30행 "내 작성 목록에서 작성 건의 지금 단계와 다음 할 일을 보여 준다")만 근거 |
| 화면이 쓰는 곳 | `DESIGN.md` 내 작성 목록 |

## 항목 2: 제출 완료 처리 (기능 ID: F-08 / 스토리: US-06)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}:submit` `[제안]` |
| 입력 | 없음 |
| 동작 | 사용자가 공식 사이트에서 직접 제출한 뒤 누르는 버튼(R10). `draft.submitted_at`을 지금 시각으로 채운다. **상태(`status`)는 바꾸지 않는다** (R10 "기록으로만 남긴다") |
| 출력 (성공) | `200`. `{"id": .., "status": "성공", "submitted_at": "2026-11-09T12:00:00Z"}` |
| 실패 응답 ("유효하지 않은 신청 건", US-06 인수 조건) | `401 LOGIN_REQUIRED`, `403 FORBIDDEN_DRAFT`, `404 DRAFT_NOT_FOUND`. `status`가 `성공`이 아니면(아직 완성본 최종 확인 전) `409 DRAFT_NOT_READY` `[제안]`. 이미 `submitted_at`이 있으면 `409 ALREADY_SUBMITTED` `[제안]` — US-06 미확정("유효하지 않은 신청 건" 기준이 원래 안 적혀 있어 이 두 가지로 구체화함, 팀 확인 필요) |
| 권한 | 로그인한 본인만. 인수 조건의 '관리자'는 위 공통 규칙대로 적용 안 함 |
| 관련 인수 조건 | US-06 전체 |
| 화면이 쓰는 곳 | `DESIGN.md` 내 작성 목록 ('제출 완료' 버튼) |

## 항목 3: 작성 건 취소 (기능 ID: F-08 / 스토리: US-07)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}:cancel` `[제안]` |
| 입력 | 없음 |
| 동작 | `draft.status`를 `취소`로 바꾼다(R12, 되돌릴 수 없음). `수정`·`반려`·`성공` 어느 상태에서든 호출할 수 있다(R12 "제출 전 모든 상태 → 취소"). 업로드 문서·입력 항목·입력값·검토 제안·개인정보 감지 결과를 지운다(T3). 업로드 파일(`document.file_path`)도 디스크에서 지운다 — `DATA-MODEL.md`엔 "삭제"라고만 적혀 있고 파일 삭제까지 명시하지 않아 `[제안]`으로 추가함. 사전 정보(`prior_info`)는 지우지 않는다(T3, 다른 작성 건이 같이 씀) |
| 출력 (성공) | `200`. `{"id": .., "status": "취소"}` |
| 실패 응답 ("유효하지 않은(이미 삭제되었거나 옳지 않은 참조) 작성 건", US-07 인수 조건) | `401 LOGIN_REQUIRED`, `403 FORBIDDEN_DRAFT`, `404 DRAFT_NOT_FOUND`. 이미 `취소`면 `409 ALREADY_CANCELED` `[제안]`. `submitted_at`이 있으면(이미 공식 제출 완료) `409 ALREADY_SUBMITTED` `[제안]` — US-07 "제출 전이라면 어느 단계에서든"의 반대 해석 |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-07 전체 |
| 화면이 쓰는 곳 | `DESIGN.md` 내 작성 목록 ('취소' 버튼) |

### 입력·출력 예시
```
요청:
GET /api/drafts?status=수정

응답(성공): 200
{
  "drafts": [
    {"id": 1, "status": "수정", "step": "field_check", "reject_reason": null, "submitted_at": null, "next_action": "FIELD_CHECK"}
  ]
}

요청:
POST /api/drafts/3:submit

응답(실패 예): 409
{"detail": {"code": "DRAFT_NOT_READY"}}

요청:
POST /api/drafts/4:cancel

응답(성공): 200
{"id": 4, "status": "취소"}
```

## 아직 없는 항목
> 다음에 추가한다.
- 작성 건 상세 1건 조회(`GET /api/drafts/{draft_id}`) — 지금은 F-02·F-04 문서가 각자 필요한 조각만(`fields`, `answers`) 돌려준다. 상세 화면에 이 셋을 하나로 합쳐 줄지는 미정
- 상태 변경 이력 API — `DATA-MODEL.md` 90행에 "상태 변경 기록은 DB 테이블 없이 서버 로그로 남긴다"고 이미 정해져 있어, 화면에 이력을 보여줄 계획이면 이 결정부터 다시 확인해야 함

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| **`status`/`step` 조합과 프론트 작업 설명의 '작성완료·검토완료·제출완료' 같은 이름이 안 맞는다.** `next_action` 코드로 우회했지만, `PRD.md` 8절의 "backlog 단계 이름을 03 상태에 맞출지" 미정이 먼저 풀려야 화면 필터 설계가 정리된다 | 팀 / 확인 필요 (`PRD.md` 8절에 이미 있는 항목) |
| US-07을 필수로 올릴지 (`PRD.md` 81행 미정) — 선택 기능이라도 이 문서 자체는 먼저 만들어 둠 | 팀 |
| 취소 때 업로드 파일을 디스크에서도 지우는 서버 코드 위치(`backend/app/drafts.py`에 둘지, 별도 모듈로 뺄지) | 개발자1 / 구현 전 |
| US-06 "유효하지 않은 신청 건", US-07 "유효하지 않은 작성 건" 기준을 위 실패 응답들(`DRAFT_NOT_READY`/`ALREADY_SUBMITTED`/`ALREADY_CANCELED`)로 구체화한 것이 맞는지 | 팀 / 구현 전 |
| 상태 변경 기록을 서버 로그로만 남기는 지금 결정(`DATA-MODEL.md` 90행)을 F-08 "이력 관리" 요구와 함께 다시 볼지 | 팀 (PM) |
| `writing → review`, `review → 성공` 등 단계 전이 담당을 `VIRTUAL-FORM-API.md` "아직 없는 항목"에 모아 적었다 — 이 문서(F-08)의 목록·상태 표시도 그 결정에 영향을 받는다 | 팀(PM) / `VIRTUAL-FORM-API.md`와 같이 정리 |
