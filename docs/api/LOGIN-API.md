## 공통 규칙
| 항목 | 내용 |
| --- | --- |
| 기본 주소 | 경로는 `/api/auth`로 시작한다. 화면(5173)의 `/api` 요청은 Vite proxy가 서버 `http://127.0.0.1:8080`으로 넘긴다 (`SETUP-PLAN.md` 3절) |
| 응답 형식·오류 응답 형식 | `API.md` 공통 규칙과 같다. 오류는 `{"detail": {"code": "<오류 코드>"}}`로 코드만 주고, 사용자에게 보일 문장은 화면이 코드로 만든다 |
| 로그인 방식 | **Google 로그인만** 제공한다. 우리 서비스는 비밀번호를 받지도 저장하지도 않는다 (R8, `DATA-MODEL.md` `user`). 이메일 가입·다른 소셜 로그인은 없다 |
| 로그인 흐름 | 서버 리다이렉트(Authorization Code) 방식. 화면은 로그인 버튼에서 항목 1 주소로 이동만 하고, Google과 주고받는 일(code 교환, 사용자 정보 확인)은 **서버만** 한다. 화면은 Google 토큰을 받지 않는다 |
| 서버 라이브러리 | Authlib의 Starlette(FastAPI) 연동으로 Google 로그인을 처리하고, Starlette `SessionMiddleware`(서명한 쿠키)로 세션을 둔다. 의존성 추가(`requirements.txt`, `==` 고정)는 공유 기반 담당이 한다. 버전과 추가로 필요한 패키지(예: `itsdangerous`)는 `확인 필요` (Authlib·Starlette 공식 문서) |
| 로그인 상태 유지 | 서명한 세션 쿠키 하나로 유지한다. 쿠키 이름 `didimdol_session`, 속성 `HttpOnly`·`SameSite=Lax`·`Path=/`, 만료 **14일**. 로컬 시연(`http://localhost`)이라 `Secure`는 끈다. 쿠키 안에는 `user.id`와 로그인 중의 `state`만 넣는다. Google이 준 토큰은 **DB·쿠키에 저장하지 않고 응답에도 넣지 않는다** (`DATA-MODEL.md` `user.google_sub` 설명) |
| 응답에 넣지 않는 것 | `user.id`, `user.google_sub`, Google 토큰. 화면에는 `email`, `language`만 준다 (R8 최소 수집) |
| 환경변수 (이름만) | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `SESSION_SECRET_KEY`. 값은 각자 `.env`에만 두고 이 문서·커밋·채팅 기록에 쓰지 않는다. 서버에서만 읽고 `VITE_`로 시작하는 이름에 넣지 않는다 (`SETUP-PLAN.md` 3절, `CLAUDE.md`). `.env.example` 반영은 공유 기반 담당 |
| Google OAuth 클라이언트 | 테크 리드(공유 기반 담당)가 팀 Google Cloud 프로젝트에 '웹 애플리케이션' OAuth 클라이언트 **1개**를 만들고, 동의 화면은 '테스트' 상태로 두고 팀원 5명의 계정을 테스트 사용자로 넣는다. 클라이언트 ID·비밀값은 저장소가 아닌 개인 메시지로 나눈다 |
| 리디렉션 URI | `http://localhost:5173/api/auth/google/callback` 하나만 등록하고 `GOOGLE_REDIRECT_URI`에 같은 값을 둔다. Google이 화면 주소(5173)로 돌려보내고 Vite proxy가 서버로 넘기므로, 세션 쿠키가 화면 주소에 붙어 이후 `/api` 요청에 함께 간다 |
| 다른 API의 권한 규칙 | 로그인이 필요한 API(`API.md`의 `POST /api/drafts` 등, `/api/auth/*`와 `/health` 제외 전부)는 세션이 없으면 `401 LOGIN_REQUIRED`로 거절하고 작성 건을 만들지 않는다 (US-01 권한 "로그인하지 않은 사용자는 올릴 수 없다"). 남이 만든 작성 건을 보거나 확정·재분석을 요청하면 `403 FORBIDDEN_DRAFT`로 거절한다 (US-01·US-02 권한 "접근 거부"). 없는 작성 건은 `404 DRAFT_NOT_FOUND` |
| LLM | 로그인 정보(`id`, `google_sub`, `email`)는 LLM 호출 입력에 넣지 않는다 (`DATA-MODEL.md` 'LLM에 보내지 않을 정보') |

## 항목 1: 로그인 시작 (스토리: US-01 권한)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/auth/google/login` |
| 입력 | 없음. 화면은 `fetch`가 아니라 **페이지 이동**(링크·`window.location`)으로 이 주소를 연다 |
| 출력 (성공) | `302`. Google 로그인·동의 화면으로 보낸다. 서버는 위조 방지용 `state` 값을 만들어 세션에 저장하고 Google 주소에 붙인다. 요청하는 정보 범위는 `openid email`만 (R8 최소 수집. 이름·프로필 사진은 받지 않는다) |
| 실패 응답 | 서버에 `GOOGLE_CLIENT_ID`·`GOOGLE_CLIENT_SECRET`·`GOOGLE_REDIRECT_URI` 중 하나라도 없으면 `500 LOGIN_NOT_CONFIGURED` |
| 권한 (누가 못 하나) | 없음 (누구나 시작할 수 있다) |
| 바뀌는 상태 | 없음 (작성 건 상태와 관계없음) |
| 관련 인수 조건 | `backlog.md` US-01 권한, `first-feature.md` 2절 #4 |
| 화면이 쓰는 곳 | 모든 화면 위쪽 머리 영역의 'Google로 로그인' 버튼, 비로그인 상태의 업로드 화면 안내 (아래 "화면 약속") |

## 항목 2: 로그인 콜백 (스토리: US-01 권한)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/auth/google/callback`. Google이 사용자를 이 주소로 돌려보낸다. 화면이 직접 부르지 않는다 |
| 입력 | 쿼리 `code`, `state` (Google이 붙임). 사용자가 동의를 거절하면 `error`가 온다 |
| 출력 (성공) | `302`. 화면 첫 주소(`/`, 업로드 화면)로 보낸다. 서버는 `state`가 세션 값과 같은지 확인하고, `code`를 Google 토큰으로 바꿔 `google_sub`·`email`·`email_verified`를 확인한다. `google_sub`가 같은 `user`가 없으면 새로 만들고(`google_sub`, `email`, `language`, `created_at`), 있으면 `email`만 최신 값으로 바꾼다. 새 사용자의 `language`는 요청의 `Accept-Language` 헤더에서 사용 언어 목록(`DATA-MODEL.md` `user.language`)에 있는 첫 언어로 정하고, 맞는 것이 없으면 `ko`로 둔다. 그 뒤 세션에 `user.id`를 기록한다. Google 토큰은 이 자리에서 쓰고 버린다 |
| 실패 응답 | 로그인 상태를 만들지 않고 `302`로 `/?login_error=<코드>`에 보낸다. 코드: `GOOGLE_LOGIN_CANCELED`(사용자가 거절), `GOOGLE_EMAIL_NOT_VERIFIED`(`email_verified`가 거짓), `GOOGLE_LOGIN_FAILED`(`state` 없음·불일치, `code` 교환 실패, Google 응답 오류). 화면은 이 코드로 안내 문장을 만든다 |
| 권한 (누가 못 하나) | 없음. 단, `state`가 없거나 다르면 위 실패 응답 |
| 바뀌는 상태 | 작성 건 상태는 바뀌지 않는다. 처음 로그인이면 `user` 행이 생긴다 |
| 관련 인수 조건 | `backlog.md` US-01 권한, `first-feature.md` 2절 #4 |
| 화면이 쓰는 곳 | 화면 첫 주소에서 `login_error`를 읽어 업로드 화면 위에 안내 문구 표시 |

## 항목 3: 내 정보 (로그인 확인) (스토리: US-01·US-02 권한)

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `GET /api/auth/me` |
| 입력 | 없음 (세션 쿠키만. 같은 주소(proxy)라 브라우저가 자동으로 붙인다) |
| 출력 (성공) | `200`. `{"user": {"email", "language"}}`. 화면은 이 응답으로 로그인 여부를 판단하고, `language`로 표시 언어를 고른다 |
| 실패 응답 | 세션이 없거나 만료되었거나 세션의 사용자가 DB에 없으면 `401 LOGIN_REQUIRED`. 화면은 로그인 버튼을 보여 준다 |
| 권한 (누가 못 하나) | 비로그인 사용자 (`401`) |
| 바뀌는 상태 | 없음 |
| 관련 인수 조건 | `backlog.md` US-01 권한, US-02 권한 |
| 화면이 쓰는 곳 | 화면을 처음 열 때 (모든 화면 공통) |

## 항목 4: 사용 언어 바꾸기

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `PATCH /api/auth/me` |
| 입력 | JSON `{"language": "<코드>"}`. 값은 `DATA-MODEL.md` `user.language`의 사용 언어 목록 안에서만 받는다 (지금 목록은 `ko`·`vi`·`zh`·`en`. 목록이 고객 답변으로 바뀌면 이 항목도 그 목록을 따른다) |
| 출력 (성공) | `200`. 바뀐 `{"user": {"email", "language"}}` |
| 실패 응답 | 비로그인 `401 LOGIN_REQUIRED`. `language`가 없거나 목록에 없으면 `400 LANGUAGE_NOT_ALLOWED` |
| 권한 (누가 못 하나) | 비로그인 사용자. 다른 사람의 언어는 바꿀 수 없다 (세션의 본인만) |
| 바뀌는 상태 | 작성 건 상태는 바뀌지 않는다. 이미 만들어진 설명(L1·L2 결과)을 다시 만들지는 않는다 |
| 관련 인수 조건 | 없음 (`user.language`는 F-02·F-03·F-05·F-06의 설명 언어로 쓰이는데, 처음 값이 `Accept-Language`로 잘못 정해졌을 때 고칠 방법이 필요해 넣었다) |
| 화면이 쓰는 곳 | 머리 영역의 언어 선택 |

## 항목 5: 로그아웃

| 항목 | 내용 |
| --- | --- |
| 요청 (경로·방식) | `POST /api/auth/logout` |
| 입력 | 없음 (세션 쿠키만) |
| 출력 (성공) | `204`. 세션을 비우고 쿠키를 만료시킨다. 이미 로그아웃 상태여도 `204`. Google 계정 자체의 로그아웃은 하지 않는다 |
| 실패 응답 | 없음 |
| 권한 (누가 못 하나) | 없음 |
| 바뀌는 상태 | 없음 (작성 건·`user` 행은 그대로 남는다) |
| 관련 인수 조건 | 없음 (인수 조건에 로그아웃이 없다. 공용 PC에서 쓸 수 있어 로그인 상태를 끝낼 방법이 필요해 넣었다) |
| 화면이 쓰는 곳 | 머리 영역의 로그아웃 버튼 |

### 화면 약속
- 모든 화면 위쪽 머리 영역: 비로그인이면 'Google로 로그인' 버튼, 로그인이면 `email`·언어 선택·로그아웃 버튼
- 비로그인으로 업로드 화면에 오면 업로드 칸 대신 "로그인한 뒤 문서를 올릴 수 있어요" 안내와 'Google로 로그인' 버튼을 보여 준다 (US-01 권한)
- 다른 API에서 `401 LOGIN_REQUIRED`를 받으면 로그인 버튼이 있는 같은 안내를 보여 준다. 따로 로그인 화면은 두지 않는다
- `DESIGN.md` 화면 목록 반영은 `DESIGN.md` 담당(이효상)이 한다. 이 문서는 `DESIGN.md`를 고치지 않는다

### 입력·출력 예시
```
로그인 시작 (화면이 페이지 이동):
GET /api/auth/google/login
→ 302 Location: https://accounts.google.com/...(client_id, redirect_uri, scope=openid email, state)

로그인 콜백 (Google이 돌려보냄):
GET /api/auth/google/callback?code=<code>&state=<state>
→ 302 Location: /            (성공, Set-Cookie: didimdol_session=...; HttpOnly; SameSite=Lax; Path=/)
→ 302 Location: /?login_error=GOOGLE_LOGIN_FAILED   (실패)

내 정보:
GET /api/auth/me
응답(성공): 200
{"user": {"email": "tester@example.com", "language": "vi"}}

응답(실패): 401
{"detail": {"code": "LOGIN_REQUIRED"}}

사용 언어 바꾸기:
PATCH /api/auth/me
Content-Type: application/json
{"language": "en"}

응답(성공): 200
{"user": {"email": "tester@example.com", "language": "en"}}

응답(실패): 400
{"detail": {"code": "LANGUAGE_NOT_ALLOWED"}}

로그아웃:
POST /api/auth/logout
→ 204 (본문 없음)

로그인 없이 업로드 (API.md 항목 1):
POST /api/drafts
응답(실패): 401
{"detail": {"code": "LOGIN_REQUIRED"}}
```
- 예시 사용자는 `DATA-MODEL.md` 시드 2번(`test-sub-0001`, `tester@example.com`, `vi`)이며 가짜 값이다.
- 테스트에서는 Google을 실제로 부르지 않는다. 세션에 시드 사용자의 `user.id`를 넣은 상태로 다른 API를 시험한다 (방법은 테스트 담당이 정함)

## 정한 것
> 처음 초안에서 `미정`이던 것을 김원우의 기준으로 정했다. ① = 프로젝트에 맞아서, ② = 프로젝트와 따질 것이 없어 보편적인 방식을 따름.

| 항목 | 정한 내용 | 기준 | 이유 |
| --- | --- | --- | --- |
| 첫 로그인 `language` | `Accept-Language`에서 목록에 있는 첫 언어, 없으면 `ko`. `PATCH /api/auth/me`로 바꿈 | ① | 사용자는 한국어가 서툰 결혼이민자라 첫 화면부터 모국어일수록 좋다. 브라우저 언어가 모국어인 경우가 많고, 틀리면 바로 바꿀 수 있게 항목 4를 둠. `ko`는 목록의 "쉬운 한국어" |
| 세션 저장 방식 | Starlette `SessionMiddleware` 서명 쿠키 | ② | FastAPI에서 흔히 쓰는 방식이고 Authlib가 `state`를 세션에 두는 데도 쓴다. 서버 메모리·SQLite 세션 테이블이 필요 없음 |
| 쿠키 이름·속성·만료 | `didimdol_session`, `HttpOnly`·`SameSite=Lax`, 14일, `Secure` 끔 | ② | 보편적인 세션 쿠키 설정. 시연이 로컬 http라 `Secure`를 켜면 쿠키가 안 붙음 |
| 남의 작성 건 | `403 FORBIDDEN_DRAFT` (없는 건은 `404 DRAFT_NOT_FOUND`) | ① | 인수 조건(US-01·US-02 권한)이 "접근 거부"라고 적어 403이 그 뜻과 같고, 테스트가 거부를 바로 확인할 수 있음 |
| OAuth 클라이언트 담당 | 테크 리드가 1개 만들고 테스트 사용자로 팀원 등록 | ① | 클라이언트·비밀값은 공유 설정이라 공유 기반 담당 영역(`SETUP-PLAN.md` 2절). 시연이 팀원 Mac이라 '테스트' 상태로 충분 |
| 리디렉션 URI | `http://localhost:5173/api/auth/google/callback` 하나, `GOOGLE_REDIRECT_URI`로 둠 | ① | 화면↔서버를 Vite proxy로 연결해 CORS가 없는 구조(`SETUP-PLAN.md` 3절)라 쿠키가 5173 주소에 붙어야 함. proxy 뒤에서 서버가 주소를 잘못 만들지 않도록 환경변수로 고정 |
| 라이브러리 | Authlib (Starlette 연동) | ② | FastAPI·Starlette에서 Google 로그인에 많이 쓰이고 `state` 확인을 해 줌. 버전은 `확인 필요` |
| 미인증 이메일 | 거절 (`GOOGLE_EMAIL_NOT_VERIFIED`) | ② | 보편적인 처리. Google 계정은 대부분 인증되어 있어 시연에 지장 없음 |
| 로그인 화면 | 따로 두지 않고 머리 영역 버튼 + 업로드 화면 안내 | ① | 로그인 방법이 Google 하나라 화면을 늘릴 이유가 없고, `DESIGN.md` 화면 목록을 늘리지 않음 |
| 경로·상태 코드·오류 코드·환경변수 이름 | 이 문서에 적은 그대로 | ② | REST 경로와 HTTP 상태 코드의 보편적인 쓰임을 따름. 오류 형식은 `API.md`와 같음 |

## 아직 없는 항목
> 다음 차시에 추가합니다.
- 회원 탈퇴·계정 삭제 (사전 정보와 작성 건을 함께 지울지, T3·T4와 연결)

## 아직 정하지 못한 것
| 항목 | 누가 언제 정하나 |
| --- | --- |
| Authlib·`itsdangerous` 등 추가 패키지의 버전 (공식 문서로 확인 후 `requirements.txt`에 `==` 고정) | 공유 기반 담당(테크 리드) / 구현 전 (확인 필요) |
| 이 문서에서 정한 값을 개발자1·2가 받아들이는지 (다르게 하려면 PR 댓글) | 개발자1·2 확인 → PM 반영 / 구현 전 |
