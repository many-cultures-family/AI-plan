## 공통 규칙
| 항목 | 내용 |
| --- | --- |
| 기본 주소 | 경로는 `/api`로 시작한다. 화면(5173)의 `/api` 요청은 Vite proxy가 서버 `http://127.0.0.1:8080`으로 넘긴다 (`SETUP-PLAN.md` 2·3절) |
| 응답 형식 | JSON. 필드 이름과 상태값은 `DATA-MODEL.md`와 같게 쓴다. 서버 파일 경로(`document.file_path`)는 응답에 넣지 않는다 |
| 오류 응답 형식 | `{"detail": {"code": "<오류 코드>"}}` `[제안]`. 문장은 넣지 않고 코드만 준다. 사용자에게 보일 문장은 화면이 코드로 만든다 (`03` R3). FastAPI가 오류를 `{"detail": ...}` 모양으로 돌려준다는 것은 `[추정]` (공식 문서 "Handling Errors" 확인 필요) |
| 인증·권한 | **오늘은 없음.** 권한 조건(`first-feature.md` 2절 #4)을 오늘 만들지 않으므로 로그인 없이 올릴 수 있다. 다음에 #4를 만들 때 Google 로그인(`DATA-MODEL.md` `user`)으로 정한다 |

## 항목 1: 문서 올리기 (기능 ID: F-01 / 스토리: US-01)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/drafts` `[제안]` |
| 입력 | `multipart/form-data`의 `file` 한 개 (PDF 또는 이미지) |
| 출력 (성공) | `201`. 새로 생긴 작성 건 `draft`(`id`, `status`, `step`)와 올린 문서 `document`(`mime_type`, `page_count`). `page_count`는 PDF면 페이지 수, 이미지(PNG·JPEG)면 1 `[제안]` (`DATA-MODEL.md` `document.page_count` "이미지는 1". `DATA-MODEL.md`가 아직 초안이라 그 문서 확정 뒤 확정). 서버는 파일을 저장하고 `draft`·`document` 행을 만든다. **OCR·마스킹은 하지 않는다** (#2를 오늘 만들지 않음) |
| 실패 응답 | 파일이 없거나 PDF·이미지가 아니면 작성 건을 만들지 않는다 (#1 "PDF·이미지 파일을 올리면"의 반대). `400 FILE_REQUIRED` `[제안]` / `415 FILE_TYPE_NOT_ALLOWED` `[제안]`. 파일 앞부분(서명)만 PDF이고 열어서 읽을 수 없는 파일도 `415 FILE_TYPE_NOT_ALLOWED`로 거절한다 `[제안]`. 허용하는 형식은 `DATA-MODEL.md` `document.mime_type`의 `application/pdf`·`image/png`·`image/jpeg` `[제안]`. 형식을 거절할지는 backlog US-01 미확정("제안서에 근거 없음")이고 `DATA-MODEL.md`도 초안이라, 둘 다 정해진 뒤 확정한다. 크기·페이지 상한(10MB·10페이지)은 backlog US-01 미확정이라 오늘 검사하지 않는다 |
| 권한 (누가 못 하나) | 오늘은 없음 (#4 아니오) |
| 바뀌는 상태 | (신규) → `status`=`수정`, `step`=`upload`. backlog의 '업로드됨'은 `DATA-MODEL.md` `step` 대응표에 따라 `수정` 상태의 `upload` 단계로 쓴다 |
| 관련 인수 조건 | `first-feature.md` 2절 #1 |
| 화면이 쓰는 곳 | `DESIGN.md` 업로드 |

### 입력·출력 예시
```
요청:
POST /api/drafts
Content-Type: multipart/form-data
file = 방과후학교_신청서_샘플.pdf

응답(성공): 201
{
  "draft": {"id": 1, "status": "수정", "step": "upload"},
  "document": {"mime_type": "application/pdf", "page_count": 1}
}

응답(실패): 415
{"detail": {"code": "FILE_TYPE_NOT_ALLOWED"}}
```

## 아직 없는 항목
> 다음 차시에 추가합니다.
- US-01의 나머지 완성 기준: #2 OCR 인식·개인정보 가림 → '인식완료', #3 인식 실패·개인정보 남음 때 처리, #4 본인만 보기·비로그인 거절 (`first-feature.md` 2절 "아니오")
- 작성 건 목록 조회는 `DRAFT-STATUS-API.md` 항목 1(`GET /api/drafts`)이 채웠다. **작성 건 1건 상세 조회, 원본 파일 보기, 다시 올리기는 아직 없다** (`FIELD-CHECK-API.md`의 입력 항목 확인 화면도 원본 파일 보기가 없어 이 문서부터 정해지길 기다리는 중)
- US-02~US-05 (`first-feature.md` 고르지 않은 후보)

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| 로그인 없이 만든 작성 건의 `draft.user_id`(`DATA-MODEL.md`에서 필수)를 어떻게 채울지. 예: 시드 2번 사용자(`test-sub-0001`)로 둘지 | 개발자1·2 / 구현 전 |
| 올린 파일을 서버 어느 폴더에 저장할지. 실제 사용자 문서는 저장소에 올리지 않으므로 그 폴더를 `.gitignore`에 넣어야 함 (`CLAUDE.md`, 공유 파일이라 테크리더) | 개발자1·테크리더 / 구현 전 |
| 경로 이름, `400 FILE_REQUIRED`, `415 FILE_TYPE_NOT_ALLOWED`, 허용 형식 목록, 이미지 `page_count`=1, 오류 응답 형식 (`[제안]`). `415`·허용 형식·이미지 `page_count`는 backlog US-01 미확정과 `DATA-MODEL.md` 확정을 기다린다 | 개발자1·2 합의 → PM 반영 / 구현 전 |
| backlog 단계 이름('업로드됨' 등)을 `03` 3-2 상태에 맞출지 (`PRD.md` 8절). 이 문서는 `DATA-MODEL.md` 대응표(`수정` + `step`)를 따름 | 팀 / 확인 필요 |
