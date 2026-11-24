> **이 문서의 근거:** `backlog.md` US-01 인수 조건 2·3번(F-01 OCR 인식·개인정보 가림), `03-rules-states-llm.md` R1·R8·3-2, `DATA-MODEL.md` `document`, `docs/privacy/`·`prototypes/masking/`(PR #126), `docs/decisions/no-server-storage-user-input.md`. `DOC-UPLOAD-API.md`는 파일 올리기(#1)만 다루고 "OCR·마스킹은 하지 않는다"고 적었다.
>
> **2026-11-23 구현 반영.** 코드 저장소 `stepping-stone`(옛 이름 `DIDIMDOL`) PR #28(병합됨)에 이 문서의 항목 1을 구현했다. 마스킹은 `prototypes/masking/masking.py`를 `backend/app/privacy.py`로 옮겨 쓰고, 가리는 종류와 토큰 모양은 `docs/privacy/pii-items.md` 2절을 따른다. 구현하면서 정한 값과 실측은 아래 "구현에서 정한 것" 절에 모았다.
>
> **OCR 엔진은 EasyOCR(ko+en)로 정했다** (2026-11-23 기록, `docs/STACK.md` "OCR 엔진 선정"). 아래 API는 엔진과 관계없이 정해 두었고, 엔진 출력을 `OcrLine`(줄 텍스트 + `page` + `bbox`)으로 바꾸는 부분만 엔진에 따라 달라진다. 그 코드는 `backend/app/ocr.py` 한 파일뿐이다.
>
> **코드 출처:** 이 문서가 "기존 코드"라고 부르는 `fields.py`·`review.py`·`llm.py`·`drafts.py`·`db.py`는 이 저장소(AI-plan)가 아니라 **코드 저장소 [`many-cultures-family/DIDIMDOL`](https://github.com/many-cultures-family/DIDIMDOL)** 의 `backend/app/`에 있다 (2026-11-17 `origin/main` 기준으로 읽고 적음).
>
> 경로·응답·오류 코드는 기존 API 문서와 구현된 코드 방식에 맞췄다. 칸마다 근거를 괄호로 적었다. 리뷰에서 바뀔 수 있다.

## 공통 규칙
> `DOC-UPLOAD-API.md` 공통 규칙(기본 주소 `/api`, JSON, 오류 응답 `{"detail": {"code": "..."}}`, 서버 파일 경로는 응답에 넣지 않음)을 그대로 따른다.

| 항목 | 내용 |
| --- | --- |
| 인증·권한 | `LOGIN-API.md` 명세를 따른다. `401 LOGIN_REQUIRED`, `403 FORBIDDEN_DRAFT`, `404 DRAFT_NOT_FOUND`. US-01 권한 인수 조건 "올린 본인만 볼 수 있다" |
| 전제 상태 | `draft.step`=`upload`, `draft.status`=`수정`. 다르면 `409 DRAFT_STEP_INVALID` / `409 DRAFT_NOT_EDITABLE` (다른 API 문서와 같은 코드) |
| 마스킹 위치 | OCR 직후 **한 함수(`mask_ocr_lines`)에서** 개인정보를 가린 뒤에만 저장·LLM 전달한다 (R1, CLAUDE.md) |
| 원문 저장 | 가리기 전 OCR 원문은 **저장하지 않고 로그에도 남기지 않는다.** 메모리에서 바로 가려 `masked_text`로만 저장한다 (`DATA-MODEL.md` 87행, R8). 로그에는 작성 건 번호·사유 코드만 (기존 `drafts.py` 로그 방식) |
| 서버에 남는 것 | 원본 파일(`document.file_path`)과 가린 텍스트(`masked_text`)뿐이다 (`no-server-storage-user-input.md`) |
| LLM | 이 API는 LLM을 부르지 않는다 (US-01 "LLM 관여: 아니오"). 이미지를 LLM에 직접 넣지 않는다 (`mvp-scope.md` 34행) |

## 항목 1: 문서 인식 (기능 ID: F-01 / 스토리: US-01)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts/{draft_id}/document:recognize` — 업로드(`POST /api/drafts`)와 **따로** 부른다. 화면은 업로드 성공 직후 이어서 부른다 |
| 따로 부르는 이유 | 단계마다 화면이 명시적으로 부르는 기존 흐름에 맞췄다 (업로드 → `fields:infer` → `fields:confirm`). 업로드 응답이 OCR 시간에 묶이지 않고, 인식만 다시 시도할 수 있다. 경로는 `fields:infer`의 `<자원>:<동작>` 방식 |
| 동기·비동기 | **동기**로 처리한다(인식이 끝날 때까지 응답을 기다림). MVP는 샘플 신청서 1종, 로컬 시연이라 진행 상태 조회 API를 따로 두지 않는다 (`fields:infer`의 L1 호출도 동기). 처리 시간은 엔진을 정한 뒤 `확인 필요`이고, 너무 길면 그때 비동기(`202`)로 바꾼다 |
| 입력 | 없음 (경로의 `draft_id`만) |
| 동작 | ① 올린 파일을 OCR로 읽어 `OcrLine` 목록으로 바꾼다 → ② `mask_ocr_lines()`로 가린다 → ③ 아래 "실패"에 걸리지 않으면 `document.masked_text`·`document.empty_pages`를 저장한다 → ④ `draft.step`을 `upload` → `field_check`로 바꾼다 (`DATA-MODEL.md` step 대응표, backlog '인식완료') |
| `masked_text` 모양 | 가린 줄마다 페이지와 칸 위치를 앞에 붙여 저장한다: `@p1 0.12,0.34,0.30,0.04 \| 성명: [이름]` — `@p<페이지> x,y,w,h` 다음 ` \| ` 뒤가 그 줄의 가린 글자다(`bbox`는 `DATA-MODEL.md` `form_field.bbox`와 같은 0~1 비율). **위치 표기에는 대괄호를 쓰지 않는다.** 대괄호는 개인정보 토큰(`[이름]`, `pii-items.md` 2절) 전용이라, 둘을 같은 문법으로 쓰면 L1·재검사·화면이 헷갈릴 수 있다. L1(`fields:infer`)은 `masked_text`만 받아 항목마다 `bbox`를 내놓아야 하므로(`llm.py` 응답 형식의 필수 값), 위치를 따로 저장하지 않고 `masked_text`에 넣는다 — `document` 테이블을 바꾸지 않아도 된다. 프로토타입의 `MaskResult.masked_text`(줄 텍스트만 이어 붙임)를 그대로 쓰지 않고 서버가 이 모양으로 만든다 |
| L1 프롬프트에 넣을 지시 | `llm.py` `infer_fields`의 프롬프트에 다음을 넣는다: "각 줄 앞 `@p<페이지> x,y,w,h \|`는 그 줄의 위치 데이터다. 항목의 `bbox`는 이 값에서 고른다. 대괄호 `[이름]`·`[전화번호]` 등은 가린 개인정보 토큰이므로 값을 짐작하지 말고, 항목 이름·설명에 옮겨 쓰지 않는다." 지금 `fields:infer` 코드는 이 모양을 모르므로 OCR 구현 때 같이 고친다 |
| 가리는 개인정보 | `pii-items.md` 2절의 8종. 라벨 없는 날짜는 L1에 필요해서 남긴다. 서술형 재검사(`REVIEW-PRIVACY-API.md` 항목 3 ⑤)·L2 검사(`WORD-EXPLAIN-API.md` 항목 2)와 **같은 규칙 한 벌**을 쓴다 |
| 출력 (성공) | `200`. `{"draft": {"id", "status": "수정", "step": "field_check"}, "document": {"page_count", "empty_pages": []}}` (`POST /api/drafts` 응답의 `draft`+`document` 모양에 맞춤). `masked_text`는 넣지 않는다 — 다음 화면(입력 항목 확인)은 `GET .../fields`를 쓴다. 가린 문서 글자가 필요한 화면(단어 고르기)은 `WORD-EXPLAIN-API.md` 항목 3(`GET .../document/text`)으로 받는다 |
| 실패와 상태 | `03` R1·3-2대로 **`수정` → `반려`**로 바꾸고 `draft.reject_reason`에 사유 코드를 남긴다. 상태 이름은 `03` 3-2를 따르라는 CLAUDE.md 규칙에 맞췄다. `masked_text`는 저장하지 않는다 |
| 실패 사유 코드 | `OCR_FAILED`(글자를 하나도 읽지 못함), `PAGE_MISSING`(`empty_pages` 1개 이상, `DATA-MODEL.md` 52행), `PII_REMAINING`(`mask_ocr_lines()`가 `residual=True`를 돌려줌 — US-01 인수 조건 3번 "개인정보가 하나라도 남으면") |
| 실패 응답 | `200`. `{"draft": {"id", "status": "반려", "step": "upload", "reject_reason": "OCR_FAILED"}}` — 요청 자체는 처리됐고 결과가 `반려`라서 `200`으로 주고, 화면은 `reject_reason` 코드로 안내 문구를 만든다 (R3, `DRAFT-STATUS-API.md` 취소 응답이 바뀐 `draft`를 `200`으로 돌려주는 방식에 맞춤) |
| 다시 올리기 | `반려` 뒤 다시 올리는 API는 아직 없다 (`DOC-UPLOAD-API.md` "아직 없는 항목"). 재업로드하면 이전 파일·입력 항목을 지운다 (`DATA-MODEL.md` `document.draft_id`) |
| 문서 속 이름의 한계 | 라벨(`성명`·`이름`·`Name`) 뒤 값만 가린다. 라벨 없는 문장 속 이름은 못 찾는다 — 알려진 한계로 두고, 시연 문서(공식 빈 서식, `VIETNAMESE-SCOPE.md` "빈 양식만 사용")에서는 문제가 되지 않는지 확인한다 (`data-flow.md` 5절 #4) |
| 권한 | 로그인한 본인만 |
| 관련 인수 조건 | US-01 인수 조건 2·3·4번 |
| 화면이 쓰는 곳 | `DESIGN.md` 업로드 (인식 중 표시·실패 안내) |

### 입력·출력 예시
```
요청:
POST /api/drafts/1/document:recognize

응답(성공): 200
{
  "draft": {"id": 1, "status": "수정", "step": "field_check"},
  "document": {"page_count": 1, "empty_pages": []}
}

응답(가린 뒤 개인정보가 남음): 200
{"draft": {"id": 1, "status": "반려", "step": "upload", "reject_reason": "PII_REMAINING"}}
```

## 점검 순서 (샘플 신청서로 끝까지 실행)
> 마지막에 몰아서 하지 않고, F-07·F-05 작업 중간중간 이 순서대로 샘플 신청서(가짜 데이터)를 끝까지 부른다. **점검은 `main`에서 한다** (작업 브랜치는 모두 `main`에서 딴다).
> **결과 칸은 각자 자기 Mac에서 실제로 실행한 결과만 적는다.** 실행하지 않았으면 `미실행` (CLAUDE.md "완료 판정"). 문제는 이슈나 `logs/daily/`에 적고 이 표에는 결과 한 줄만 적는다.
> **API가 아직 없는 단계는 기다리지 않고 건너뛴다**: SQLite에서 그 작성 건의 `draft.step`만 다음 값으로 직접 바꾸고, 결과 칸에 `건너뜀(DB 수정)`이라고 적는다. 구현되면 다시 실행한다.
> '구현'은 2026-11-17 기준 `DIDIMDOL` 저장소 `origin/main`에 라우터가 있는지만 본 것이다(동작 확인 아님).

| 순서 | 할 일 | API | 명세 문서 | 구현 (`main`) | 결과 (날짜·실행한 사람) |
| --- | --- | --- | --- | --- | --- |
| 1 | 로그인 | `GET /api/auth/google/login` → `callback` → `GET /api/auth/me` | `LOGIN-API.md` | 있음 | 미실행 |
| 2 | 문서 올리기 | `POST /api/drafts` | `DOC-UPLOAD-API.md` | 있음 | 미실행 |
| 3 | 문서 인식·개인정보 가림 | `POST /api/drafts/{id}/document:recognize` | 이 문서 | 없음 (PR #28 리뷰 중) | 미실행 |
| 4 | 입력 항목 추론 | `POST /api/drafts/{id}/fields:infer` | `FIELD-CHECK-API.md` | 있음 | 미실행 |
| 5 | 입력 항목 확정 | `POST /api/drafts/{id}/fields:confirm` | `FIELD-CHECK-API.md` | 있음 | 미실행 |
| 6 | 사전 정보 입력 (브라우저에만 저장) | 없음 (서버 API 없음) | `no-server-storage-user-input.md` | 화면 없음 | 미실행 |
| 7 | `prior_info` → `writing` 전이 | `POST /api/drafts/{id}/writing:start` | `VIRTUAL-FORM-API.md` 항목 2 | 없음 (PR #30 리뷰 중) | 미실행 |
| 8 | 가상 작성 (입력값·형식 검사·불일치 계산은 브라우저) | `GET /api/drafts/{id}/form`, `GET …/document/pages/{page}` | `VIRTUAL-FORM-API.md` 항목 1·3 | 없음 (PR #30 리뷰 중, 불일치 표시는 아직) | 미실행 |
| 9 | 단어 설명·쉬운 풀이 | `GET …/document/text`, `GET /api/glossary`, `POST /api/drafts/{id}/explanations` | `WORD-EXPLAIN-API.md` | 없음 | 미실행 |
| 10 | `writing` → `review` 전이 | `POST /api/drafts/{id}/review:start` | `REVIEW-PRIVACY-API.md` 항목 1 | 없음 | 미실행 |
| 11 | 개인정보 감지·결정·가리기 (브라우저) | `GET /api/privacy-rules` | `REVIEW-PRIVACY-API.md` 항목 4, `l3-masking.md` | 없음 | 미실행 |
| 12 | 서술형 검토 요청 | `GET …/review`, `POST …/review:request` | `REVIEW-PRIVACY-API.md` 항목 2·3 | 없음 (`f02-v2` 브랜치 코드는 결정 전 방식) | 미실행 |
| 13 | `review` → `성공` 최종 확인 | `POST /api/drafts/{id}:complete` | `REVIEW-PRIVACY-API.md` 항목 5 | 없음 | 미실행 |
| 14 | 제출 기록·목록 확인 | `POST /api/drafts/{id}:submit`, `GET /api/drafts` | `DRAFT-STATUS-API.md` | 있음 | 미실행 |

## 구현에서 정한 것 (PR #28, 2026-11-23)
> 이 문서에 값이 없어 구현하면서 정한 것이다. 리뷰에서 바뀔 수 있다. 실측은 석준영 Mac(Apple M3)에서 Claude가 가짜 데이터로 실행한 결과이고, `main`에서 점검한 것이 아니다.

| 항목 | 정한 것 | 이유·근거 |
| --- | --- | --- |
| 엔진 | EasyOCR 1.7.2, 언어 `ko`+`en`. Apple Silicon이면 GPU(MPS)를 쓴다 | `STACK.md` "OCR 엔진 선정"에 기록 |
| 추가 의존성 | `easyocr==1.7.2`(PyTorch 포함 약 1GB), `pymupdf==2.1`(PDF 쪽을 이미지로) | 코드 저장소 README상 `requirements.txt`는 기술 리더 확인이 필요하다 |
| PDF 처리 | 쪽마다 200dpi 회색조 이미지로 바꿔 읽는다 | 200dpi에서 A4 한국어 신청서 글자를 충분히 읽음 (실측) |
| 줄 합치기 | EasyOCR은 표의 라벨 칸과 값 칸을 박스 따로 준다. 박스 중심 높이 차가 쪽 높이의 1.2% 안이면 같은 줄로 보고 왼쪽부터 이어 붙인다 | 같은 줄이어야 라벨 규칙(`성명 홍길동`)이 값을 잡는다. 기울어진 스캔에서 값이 라벨 앞에 붙던 문제를 실측으로 확인 |
| 처리 시간 | 첫 요청은 모델을 내려받고(약 95MB, `~/.EasyOCR/`) 불러오느라 20초 넘게 걸린다. 그 뒤로 1쪽 GPU 약 1~3초, CPU 약 6초 | 실측. 동기 처리로 두어도 되는지는 팀 확인 |
| 엔진 오류 | 파일을 못 열거나 엔진이 실패하면 `OCR_FAILED`로 `반려`. 로그에는 작성 건 번호와 오류 종류 이름만 남긴다 | R8 (문서 내용을 로그에 남기지 않음) |
| OCR 오인식 보완 | 숫자 속 `O`·`l` 등을 숫자로 바꾼 뒤 가리고, 전화·이메일·등록번호 라벨 뒤 값은 모양과 상관없이 통째로 가린다 | EasyOCR 실측에서 `O1O-…`, 점 빠진 이메일이 가려지지 않고 `residual=False`로 통과했다. 규칙은 `pii-items.md` 2절 |
| 화면 | 업로드가 끝나면 바로 이 API를 부르고, `반려`면 사유 코드로 안내 문구를 만든다. 화면을 닫아 인식을 못 마친 작성 건은 내 작성 목록에서 다시 부를 수 있다 | 항목 1 "화면은 업로드 성공 직후 이어서 부른다" |

## 아직 없는 항목
- 원본 파일 보기 API (`DOC-UPLOAD-API.md`·`FIELD-CHECK-API.md` "아직 없는 항목"과 같은 질문). 가상 작성 화면에 필요한 쪽 이미지만 `VIRTUAL-FORM-API.md` 항목 3에 `[제안]`으로 두었다
- `반려` 뒤 다시 올리기 API

## 팀 확인이 필요한 것
> CLAUDE.md상 Claude가 정하지 않는 것(스택, 인수 조건)이다. 추천안만 적는다.

| 항목 | 추천안 | 누가 |
| --- | --- | --- |
| ~~OCR 엔진 (PaddleOCR / EasyOCR), Apple Silicon 동작~~ | EasyOCR로 정함. `STACK.md` "OCR 엔진 선정"에 기록 (2026-11-23) | 석준영 / 끝남 |
| US-01 인수 조건 3번 "'업로드됨'에 머문다"와 이 문서(`03` R1대로 `반려`)가 다름 | `03` 3-2 상태에 맞춰 인수 조건을 "반려되고 사유를 보여 주며 다시 올리도록 안내"로 고친다 (`data-flow.md` 5절 #5, `PRD.md` 8절 상태 이름 문제와 같이) | 팀 (인수 조건은 팀이 직접 고침) |
| `prototypes/masking/`을 서버 코드로 옮기는 위치 | PR #28에서 `backend/app/privacy.py`·`backend/tests/test_privacy.py`로 옮김. 서버 담당이 리뷰에서 확인 | 서버 담당 / PR #28 리뷰 때 |
