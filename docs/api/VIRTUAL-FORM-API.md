> **2026-11-17 개정 — 서버 미저장 결정 반영.** 병합된 결정 `docs/decisions/no-server-storage-user-input.md`가 "사전 정보와 입력값은 서버에 저장하지 않는다"로 정하고, 이 문서를 "입력값 저장 API와 서버 불일치 계산을 브라우저 계산으로 바꾼다"로 고치도록 적었다. 그래서 이전 판의 **입력값 저장(`PUT .../answers/{field_id}`)·불일치 확인(`POST .../answers/{field_id}:acknowledge-mismatch`) API를 없애고**, 조회 API는 값 없이 칸 정보와 형식 규칙만 주도록 바꿨다. 이전 판의 "`review` 단계에서 값이 바뀌면 `step`을 `writing`으로 되돌린다"도 서버가 값 변경을 알 수 없어 없앴다 (`REVIEW-PRIVACY-API.md` 항목 1). PR #131 리뷰 지적(두 문서가 서로 반대로 말함)을 풀려고 김원우가 고쳤고, **원래 담당자(이효상) 확인이 필요하다.**
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
| 출력 (성공) | `200`. `draft`(`id`, `status`, `step`) + `fields`(배열). 칸마다: `field_id`, `label`, `format_code`, `format_label`, `format_example`, `pattern`(정규식, `long_text`·`choice`는 `null`), `required`, `prior_info_key`, `description`, `options`(선택형이면 선택지 배열, 아니면 `null`) |
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

### 입력·출력 예시
```
요청:
GET /api/drafts/1/form

응답(성공): 200
{
  "draft": {"id": 1, "status": "수정", "step": "writing"},
  "fields": [
    {
      "field_id": 12, "label": "보호자 연락처", "format_code": "phone",
      "format_label": "전화번호", "format_example": "010-0000-0000",
      "pattern": "^010-\\d{4}-\\d{4}$",
      "required": true, "prior_info_key": "phone",
      "description": "자녀의 보호자 전화번호를 적습니다",
      "options": null
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

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| **F-04 스토리·인수 조건이 `backlog.md`에 없음** | 팀 / 가장 먼저 |
| 이번 개정(서버 미저장 반영) 확인 | 이효상(원래 담당) / PR #131 리뷰 때 |
| 연결된 사전 정보가 브라우저에 없을 때(`prior_info_key`는 있는데 값이 없음) 그 칸을 어떻게 다룰지 — 화면이 사전 정보 입력으로 돌려보낼지, 그 칸에서 바로 입력받을지 | 팀·화면 담당 / 구현 전 |
| `backend/app/db.py`에 `field_answer`·`prior_info` 테이블을 만들지 않는다 (`DATA-MODEL.md`에서 빼는 것은 PM) | PM / 결정 반영 때 |
