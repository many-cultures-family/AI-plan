> **이 문서의 근거:** `03-rules-states-llm.md` R5·3-4 L2, `DATA-MODEL.md` `glossary_term`·`easy_explanation`, `VIETNAMESE-SCOPE.md`(PR #127), `docs/decisions/no-server-storage-user-input.md`·`docs/privacy/`(PR #126), `STACK.md` 35행.
>
> **F-05(단어·문장 설명)는 `backlog.md`에 스토리와 인수 조건이 아직 없다** (`mvp-scope.md` 18·20행, `PRD.md` 47행). 인수 조건은 팀이 직접 쓴다(CLAUDE.md). 이 문서의 API 세부는 정해 두었고, 스토리가 생기면 "관련 인수 조건" 칸만 채운다.
>
> **코드 출처:** 이 문서가 "기존 코드"라고 부르는 `fields.py`·`review.py`·`llm.py`·`drafts.py`·`db.py`는 이 저장소(AI-plan)가 아니라 **코드 저장소 [`many-cultures-family/DIDIMDOL`](https://github.com/many-cultures-family/DIDIMDOL)** 의 `backend/app/`에 있다 (2026-11-17 `origin/main` 기준으로 읽고 적음).
>
> 경로·오류 코드는 기존 API 문서와 구현된 코드(`fields.py`·`review.py`·`drafts.py`·`llm.py`) 방식에 맞췄고, 맞출 것이 없던 값은 프로젝트 원칙(개인정보 최소 수집 R8, 무료, 같은 질문에 같은 설명 R5)에 맞춰 정했다. 칸마다 근거를 괄호로 적었다. 리뷰에서 바뀔 수 있다.

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. 세션이 없으면 `401 LOGIN_REQUIRED`. 작성 건을 경로에 받는 API는 본인 것이 아니면 `403 FORBIDDEN_DRAFT`, 없으면 `404 DRAFT_NOT_FOUND` |
| 전제 상태 (항목 2) | `draft.step`이 `writing` 또는 `review`이고 `draft.status`가 `수정`일 때 (`VIRTUAL-FORM-API.md` 항목 1 `GET .../form`이 `writing`·`review`에서 열리는 것에 맞춤). 다르면 `409 DRAFT_STEP_INVALID` / `409 DRAFT_NOT_EDITABLE`. 상태를 바꾸지 않는다 (`수정` 유지, `03` 3-4 L2) |
| 기본 설명은 항상 사전에서 | 단어를 누르면 **서버 용어 사전(`glossary_term`)의 설명을 먼저** 보여 준다. LLM은 사용자가 '이해하지 못함'을 고를 때만 부른다 (R5) |
| AI 풀이 표시 | L2가 만든 풀이는 응답에 `source: "ai"`를 넣고, 화면은 'AI 풀이'로 표시한다 (R5) |
| 사용 언어 | 설명 언어는 **베트남어(`vi`) 하나**다. 단어·문장은 한국어 신청서에서 고르고, 설명은 베트남어로 준다 (`VIETNAMESE-SCOPE.md` "번역 방향"). 서버는 `user.language`를 읽는 구조를 그대로 두고(`FIELD-CHECK-API.md` 사용 언어 규칙), MVP에서 그 값은 `vi`다 |
| 번역 API | **쓰지 않는다.** 기본 설명은 팀이 만든 용어 사전, 그 밖은 L2로 충분하다. `STACK.md` A안이 번역을 "LLM + 프론트 i18n"으로 정했고 Argos는 선택(품질 확인 필요)으로 남겼기 때문이다. Argos를 붙이기로 하면 항목 1의 "사전에 없을 때"에만 끼운다 |
| 서버에 남는 개인정보 경로 | 사전 정보·입력값을 서버에 저장하지 않기로 한 뒤에도 **L2는 서버에 저장되는 경로**다. `easy_explanation.selected_text`는 서버에 저장되고 사용자 사이에도 같이 쓴다 (`pii-items.md` 1절 마지막 줄). 그래서 항목 2의 `selected_text` 검사가 이 문서에서 가장 중요하다 (`data-flow.md` 5절 #1) |
| LLM에 보내지 않는 것 | 사용자가 입력한 값, 사전 정보 (`03` 3-4 L2). 둘 다 서버에 오지 않는다 (서버 미저장 결정) |

## 항목 1: 기본 설명 조회 (기능 ID: F-05 / 스토리: 없음)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/glossary?term=<단어>` (조회 조건을 쿼리로 받는 `GET /api/drafts?status=`에 맞춤). 언어는 서버가 `user.language`로 정한다 |
| 입력 | `term` (화면에서 누른 단어·문장, 1~50자 — `input_format`의 `name` 상한 50자에 맞춤) |
| 동작 | 앞뒤 공백만 지우고 `glossary_term`에서 (`term`, `language`)가 **정확히 같은** 행을 찾는다. LLM을 부르지 않는다 (R5) |
| 찾는 방법을 정확히 일치로 정한 이유 | 조사·어미를 떼려면 형태소 분석기가 필요한데, 무료·arm64 동작을 확인한 도구가 없다. 조사가 붙어 사전에서 못 찾으면 `found: false`가 되고 사용자는 '이해하지 못함'(항목 2)으로 풀이를 받으므로 설명이 끊기지는 않는다. 그렇게 반복 요청된 말은 팀이 사전에 넣는다(아래 "운영 방식"). 형태소 처리는 MVP 뒤에 다시 본다 |
| 출력 (성공) | `200`. `{"found": true, "term": "보호자", "explanation": "...", "source": "glossary"}` |
| 사전에 없을 때 | `200 {"found": false, "term": "..."}` — 화면은 '이해하지 못함'(항목 2)만 보여 준다. 기존 코드는 `404`를 경로에 넣은 자원이 없을 때만 쓰고, 값이 비어 있는 조회(`GET /api/prior-info`)는 `200`으로 돌려주므로 그에 맞춤 |
| 베트남어 설명이 없을 때 | 사전에 넣는 용어는 모두 베트남어 설명을 함께 넣는다. 그래도 `vi` 설명이 없으면 사전에 없는 것과 같이 `found: false` |
| 실패 응답 | `term`이 비었으면 `400 TERM_REQUIRED`, 50자를 넘으면 `400 TERM_TOO_LONG` (`FILE_REQUIRED`·`VALUES_REQUIRED`의 `<무엇>_<이유>` 이름에 맞춤) |
| 권한 | 로그인한 사용자 (사전은 사용자끼리 같이 쓴다) |
| 관련 인수 조건 | 없음 — F-05 스토리 작성 뒤 채움 (근거: R5) |
| 화면이 쓰는 곳 | 가상 작성 환경 (단어를 누르면 뜨는 설명). `DESIGN.md` 화면 표에 이 화면 행을 추가해야 한다 (화면 담당) |

## 항목 2: 쉬운 풀이 요청 — '이해하지 못함' (기능 ID: F-05 / 스토리: 없음)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/explanations` (작성 건 소유·`masked_text` 확인을 위해 `drafts/{id}` 아래에 둠) |
| 입력 | `{"selected_text": "보호자 동의"}` — 1~100자 (`input_format`의 `short_text` 상한 100자에 맞춤) |
| `selected_text` 검사 (개인정보 차단) | **두 단계로 막는다.** ① 서버가 `selected_text`가 이 작성 건의 **이미 가린** 문서 글자 안에 그대로 들어 있는지 본다. 대상은 화면이 실제로 받아 보여 주는 글자와 같다: 문서 본문 줄(`document.masked_text`, 항목 3으로 내려 줌), 칸 이름·설명·선택지(`form_field`의 `label`·`description`·`options`, `VIRTUAL-FORM-API.md` 항목 1 `GET .../form`으로 내려 줌), 서술형 안내 문구(`guide_text`, `GET .../review`로 내려 줌). 없으면 `400 TEXT_NOT_IN_DOCUMENT`. ② 들어 있어도 `detect_pii`(`prototypes/masking/masking.py`)로 다시 검사해 걸리면 L2를 부르지 않고 `422 PII_REMAINING` (`REVIEW-PRIVACY-API.md` 항목 3과 같은 코드) |
| 이렇게 정한 이유 | `data-flow.md` 5절 #1의 두 후보 중 ㉡(서버가 가린 글자 안으로 한정)을 골랐다. ㉠(브라우저에서 감지)만으로는 서버가 확인할 수 없고, L2 결과는 서버에 저장돼 다른 사용자에게도 보이므로 서버에서 막아야 한다. ②는 서술형과 같은 "서버 재검사" 원칙이다. 그 결과 사용자는 **원본 파일 이미지가 아니라 위 API로 받은 가린 글자에서만** 단어를 고를 수 있다. 화면은 문서 본문을 항목 3의 줄 목록으로 그리고, 그 글자를 골라 항목 2를 부른다 |
| 동작 | ① (`selected_text`, `user.language`)로 `easy_explanation`을 찾아 있으면 L2를 부르지 않고 그 풀이를 돌려주고 `request_count`를 1 올린다 (R5 "같은 질문에 같은 설명"). ② 없으면 L2를 부르고 결과를 저장한다(`request_count`=1). 사전에 있던 단어면 `glossary_term_id`를 연결한다 |
| L2에 보내는 것 | `selected_text`, 용어 사전의 기본 설명(있으면), `user.language` (`03` 3-4 L2). 문서 종류는 MVP가 샘플 1종이라 보내지 않는다 (`DATA-MODEL.md` 81행) |
| L2 호출 방법 | `backend/app/llm.py`의 `_call_gemini`를 그대로 쓰고 `explain_text` 함수만 추가한다 (`infer_fields`·`review_answers`가 같은 방식, 모델명은 `.env`의 `GEMINI_MODEL`) |
| 호출 횟수 제한 | 작성 건 하나에 **새로 L2를 부르는 횟수**를 20회로 제한한다. 저장된 풀이를 돌려주는 경우는 세지 않는다. 넘으면 `409 EXPLANATION_LIMIT_EXCEEDED` (작성 건 누적 제한을 `409`로 주는 `REANALYSIS_LIMIT_EXCEEDED`에 맞춤). 횟수는 `draft`에 `explanation_count`(정수, 처음 0)로 센다 — `reanalysis_count`와 같은 방식이며 `DATA-MODEL.md` 반영은 PM. 20회는 샘플 신청서 칸 수(10개 안팎)의 두 배로 잡은 값이고, Gemini 무료 한도는 `확인 필요`라 확인 뒤 조정한다 |
| 출력 (성공) | `200`. `{"selected_text": "...", "explanation": "...", "source": "ai"}` — 저장된 풀이를 돌려줄 때도 같은 모양 (`fields:infer`·`review:request` 멱등 응답에 맞춤) |
| 실패 응답 | `400 TEXT_REQUIRED`(빈 값), `400 TEXT_TOO_LONG`(100자 초과), `400 TEXT_NOT_IN_DOCUMENT`, `422 PII_REMAINING`, `409 EXPLANATION_LIMIT_EXCEEDED`, L2 호출 실패 `502 LLM_CALL_FAILED`, 그 외 공통 규칙 |
| 바뀌는 상태 | 바뀌지 않는다 (`수정` 유지) |
| 권한 | 로그인한 본인만 (작성 건 소유 확인). 만들어진 풀이는 사용자끼리 같이 쓴다 (`DATA-MODEL.md` 81행) |
| 관련 인수 조건 | 없음 — F-05 스토리 작성 뒤 채움 (근거: R5, `03` 3-4 L2) |
| 화면이 쓰는 곳 | 가상 작성 환경 — 기본 설명 아래 '이해하지 못함' 버튼 |

## 항목 3: 가린 문서 글자 조회 (기능 ID: F-05 / 스토리: 없음)

> 항목 2의 검사 ①이 "가린 문서 글자 안에 있는지"를 보려면, 화면이 그 글자를 받아 사용자에게 고르게 할 수 있어야 한다. 지금 `docs/api/`에는 `masked_text`를 내려 주는 API가 없어 이 항목을 둔다.

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/drafts/{draft_id}/document/text` (작성 건 아래 하위 자원을 명사 경로로 읽는 `GET .../fields`·`GET .../review`에 맞춤) |
| 입력 | 없음 |
| 전제 상태 | `draft.step`이 `field_check` 이후(`field_check`·`prior_info`·`writing`·`review`)이고 `masked_text`가 있어야 한다. 비어 있으면 `422 DOCUMENT_NOT_READY` (`fields:infer`와 같은 코드) |
| 동작 | 저장된 `document.masked_text`를 줄 단위로 나눠, 줄 앞의 위치 표기(`OCR-API.md` "`masked_text` 모양")를 `page`·`bbox`로 풀어 돌려준다. 가리기 전 글자는 서버에 없으므로 돌려줄 수도 없다 |
| 출력 (성공) | `200`. `{"lines": [{"page": 1, "bbox": {"x": 0.12, "y": 0.34, "w": 0.30, "h": 0.04}, "text": "성명: [이름]"}]}` — 화면은 `bbox`로 원본 위에 겹쳐 그리거나 줄 목록으로 보여 주고, 토큰(`[이름]` 등)은 "가려진 정보"로 표시한다 |
| 실패 응답 | `422 DOCUMENT_NOT_READY`, 그 외 공통 규칙의 `401`/`403`/`404`/`409` |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | 없음 — F-05 스토리 작성 뒤 채움 |
| 화면이 쓰는 곳 | 가상 작성 환경 — 단어를 고르는 문서 본문 |

### 입력·출력 예시
```
요청:
GET /api/glossary?term=보호자

응답(성공): 200
{"found": true, "term": "보호자", "explanation": "(베트남어 기본 설명)", "source": "glossary"}

요청:
POST /api/drafts/1/explanations
{"selected_text": "보호자 동의"}

응답(성공): 200
{"selected_text": "보호자 동의", "explanation": "(L2가 만든 베트남어 쉬운 풀이와 예시)", "source": "ai"}

요청 (문서의 가린 글자에 없는 값):
POST /api/drafts/1/explanations
{"selected_text": "홍길동"}

응답(실패): 400
{"detail": {"code": "TEXT_NOT_IN_DOCUMENT"}}

요청:
GET /api/drafts/1/document/text

응답(성공): 200
{"lines": [{"page": 1, "bbox": {"x": 0.12, "y": 0.34, "w": 0.30, "h": 0.04}, "text": "성명: [이름]"}]}
```

## 운영 방식 (API를 두지 않는 것)
| 하는 일 | 방식 |
| --- | --- |
| 용어 사전 추가·수정 | API를 두지 않고 **시드 데이터**로 넣는다 — `db.py`가 `input_format`을 `SEED_INPUT_FORMATS`로 넣는 방식과 같다. 관리자 역할이 없어서다 (`backlog.md` US-06 미확정 "관리자 역할이 없음") |
| 자주 요청된 풀이 검토 | API를 두지 않고 팀이 DB를 직접 조회한다 (`request_count` 높은 순). 검토한 풀이는 시드 데이터로 옮긴다 (`03` 3-4 L2) |
| 선택지(`form_field.options`)의 설명 | 따로 API를 두지 않는다. 선택지 글자도 항목 1·2로 그대로 조회한다 (`options`는 항목 2 검사 대상에 들어 있다) |

## 아직 없는 항목
- `backend/app/db.py`에 `glossary_term`·`easy_explanation` 테이블과 `draft.explanation_count`가 없다. `DATA-MODEL.md` 75~82행 필드 그대로 추가 (`explanation_count`는 `DATA-MODEL.md` 반영 필요)

## 팀 확인이 필요한 것
> CLAUDE.md상 Claude가 정하지 않는 것(인수 조건, 범위)이다. 추천안만 적는다.

| 항목 | 추천안 | 누가 |
| --- | --- | --- |
| **F-05 스토리·인수 조건 작성** (`backlog.md`) | 이 문서의 실패 응답(사전 없음, 가린 글자 밖, 개인정보 남음, 호출 한도)을 실패·거절 조건 후보로 쓸 수 있다 | 팀 / 가장 먼저 |
| 쉬운 한국어(`ko`) 설명을 함께 둘지 | 두지 않는다 — `VIETNAMESE-SCOPE.md`가 "한국어 → 베트남어"로만 정했다. `DATA-MODEL.md` `user.language` 목록과 `PRD.md` 8절 "언어 수"를 이에 맞게 고친다 | 팀 → PM 반영 |
| 용어 사전 초기 데이터 작성자 | 샘플 신청서 용어부터 시작해 대상 분야(체류·국적, 가족관계등록, 자녀·복지) 공식 빈 서식 용어로 넓힌다 (`mvp-scope.md` 40행, `VIETNAMESE-SCOPE.md`) | 팀 / 구현 전 |
| Gemini 무료 한도에 맞춰 20회 한도를 조정 | 한도 확인 뒤 조정 (`확인 필요`) | 개발자 / L2 동작 확인 때 |
