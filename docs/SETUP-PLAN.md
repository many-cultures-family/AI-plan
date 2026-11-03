# 프로젝트 초기화 계획과 실행 확인

> **저장 위치:** `docs/SETUP-PLAN.md`

> **사용 방법**
> 1. **만들기 전에** 1~4절을 채웁니다. Plan 모드로 받은 계획을 팀이 읽고 고친 뒤 승인한 내용입니다. 만든 뒤에는 실제 결과와 비교합니다(7절).
> 2. 범위는 **실행되는 최소 구조**까지입니다. 폴더·의존성·기본 화면·서버 시작·실행 방법. **PRD의 실제 기능은 만들지 않습니다.**
> 3. 스택과 버전은 `STACK.md`를 따릅니다. **설치와 초기화는 Claude가 아니라 학생이 공식 문서를 보고 직접 합니다.** 확인한 공식 문서의 **주소와 절**, 직접 실행한 명령을 1·3절에 적습니다. 공식 문서를 확인하지 못한 것은 `미확인`으로 씁니다. 최신 버전으로 무조건 바꾸지 않습니다.
> 계획(Claude가 제안)과 공식 문서가 다르면 **공식 문서를 따르고** 7절에 차이를 적습니다.
> 4. **5절과 6절은 정리 담당 한 사람이 적습니다.** 5명이 같은 표를 동시에 고치면 충돌이 납니다. 나머지는 팀 채팅에 올립니다.
> 5. 6절 실행 확인은 **5명 모두**, 각자 자기 Mac에서 실행한 결과입니다. "AI가 완료라고 답함"은 확인이 아닙니다. 실행하지 않은 것은 `미실행`, 테스트가 아직 없으면 `테스트 미구성`으로 씁니다.
> 6. `>`로 시작하는 안내 문장은 지워도 됩니다.

- 작성일: 2026-10-27
- 근거: `STACK.md`(A안 React(Vite) + FastAPI + SQLite), `PRD.md`(v0.1), `mvp-scope.md`, 팀이 승인한 초기화 계획 v2

## 1. 사용할 기술과 버전

> 사용할 버전은 **팀이 정한 값**입니다. 최신 안정 버전·호환성·공식 문서 주소는 아직 아무도 확인하지 않았으므로 `미확인`입니다. 확인한 사람이 주소·절·날짜를 채웁니다. 공식 문서 칸의 절 이름은 찾아볼 곳이며, 실제 이름과 다를 수 있습니다.

| 기술 | 사용할 버전 | 최신 안정 버전 | 호환성·제약 | 공식 문서 (주소·절) | 확인한 사람 | 확인 날짜 |
| --- | --- | --- | --- | --- | --- | --- |
| Python (`python3`) | 3.14 | 미확인 | FastAPI 0.162.0·pydantic·ruff가 3.14를 지원하는지, arm64용 wheel이 있는지 확인 필요 | 미확인 (찾을 곳: python.org "Status of Python versions", PyPI `fastapi`·`pydantic-core`의 Requires-Python·파일 목록) | | |
| venv | Python 내장 (`backend/.venv`) | — | — | 미확인 (찾을 곳: docs.python.org "venv — Creation of virtual environments") | | |
| FastAPI | 0.162.0 | 미확인 | 지원 Python 범위 확인 필요 | 미확인 (찾을 곳: fastapi.tiangolo.com "Tutorial – First Steps", "Deployment – About FastAPI versions") | | |
| Uvicorn | 0.54.0 | 미확인 | 서버 실행은 Uvicorn으로 함 | 미확인 (찾을 곳: uvicorn.org "Settings", fastapi "Deployment – Run a Server Manually") | | |
| pytest | 미정 (공유 담당이 정해 고정) | 미확인 | FastAPI TestClient가 요구하는 패키지도 함께 고정 | 미확인 (찾을 곳: docs.pytest.org "Get Started", fastapi "Tutorial – Testing") | | |
| ruff (서버 린트+포맷) | 미정 (공유 담당이 정해 고정) | 미확인 | 설정 파일을 `ruff.toml`과 `pyproject.toml` 중 무엇으로 할지 미정 | 미확인 (찾을 곳: docs.astral.sh/ruff "Configuring Ruff", "The Ruff Linter", "The Ruff Formatter") | | |
| Node.js | 24 LTS (Homebrew) | 미확인 | Vite 8.3.4가 요구하는 Node 버전에 맞는지 확인 필요 | 미확인 (찾을 곳: nodejs.org "Releases", vite.dev "Getting Started") | | |
| npm | Node 24에 포함된 버전 | 미확인 | `package-lock.json`을 커밋함 | 미확인 (찾을 곳: docs.npmjs.com "package-lock.json", "npm ci") | | |
| Vite | 8.3.4 | 미확인 | create-vite 버전은 Vite 버전과 다를 수 있음 → 생성 후 `package.json`에서 확인 | 미확인 (찾을 곳: vite.dev "Scaffolding Your First Vite Project", "Server Options") | | |
| React | 19.3 | 미확인 | Vite 템플릿이 설치한 버전과 다르면 19.3으로 맞춤. JavaScript 사용 | 미확인 (찾을 곳: react.dev "Installation") | | |
| ESLint (화면) | Vite 템플릿 기본 그대로 | — | Prettier는 미구성 | 생성된 `frontend/package.json`의 scripts | | |
| MUI | 9.5 (Mantine 제외) | 미확인 | React 19.3과의 호환 확인 필요. **뼈대에서는 설치하지 않음** | 미확인 (찾을 곳: mui.com "Material UI – Installation") | | |
| SQLite | Python 내장 | — | 뼈대에서는 사용하지 않음 | — | | |
| Gemini API | — | — | 뼈대에서는 호출하지 않음 | — | | |
| PaddleOCR / EasyOCR | — | — | 뼈대에서는 설치하지 않음 (`STACK.md` "확인할 것" 결과를 따름) | — | | |

- 버전 고정: 서버는 `requirements.txt`에 `==`, 화면은 `package.json`과 커밋한 `package-lock.json`.

## 2. 폴더 구조와 담당 영역

```
AI-service/
├── .gitignore              [공유] 기존 내용 유지 + 추가 (.venv/, node_modules/, .env, __pycache__/, .ruff_cache/, .pytest_cache/, *.db, dist/)
├── .env.example            [공유] 환경변수 이름만
├── README.md               [공유] 기존 내용 유지 + "설치·실행" 절 추가
├── backend/
│   ├── requirements.txt    [공유] fastapi, uvicorn, pytest, TestClient용 패키지, ruff (모두 ==)
│   ├── ruff.toml 또는 pyproject.toml   [공유] ruff 설정
│   ├── .venv/              (각자 로컬에 만듦, 커밋 안 함)
│   ├── app/
│   │   ├── __init__.py     [서버]
│   │   └── main.py         [서버] FastAPI 앱 + GET /api/health
│   └── tests/
│       └── test_health.py  [테스트] 서버 스모크 테스트 1개
└── frontend/               [공유] Vite(React, JavaScript) 초기화로 생성되는 파일 전부
    ├── package.json, package-lock.json(커밋), vite.config.js, index.html, ESLint 설정
    ├── .gitignore          (Vite가 만든 것 그대로 둠)
    └── src/
        ├── main.jsx        [화면] (생성본 그대로 사용 가능)
        └── App.jsx         [화면] 제목 "디딤돌" + 서버 상태 한 줄
```

**공유 파일(루트 설정, `requirements.txt`·`package.json`·`package-lock.json`, `vite.config.js`, ruff 설정, `.gitignore`, `.env.example`)은 공유 기반 담당만 만들고 고칩니다.** 다른 영역에서 의존성이 필요하면 공유 기반 담당에게 요청해 공유 PR로 반영합니다.

담당은 `docs/team/roles.md` 역할 교대 계획의 **S1** 기준입니다. 스프린트가 바뀌면 교대표를 따릅니다.

| 역할 | 맡는 영역 (폴더·파일) | 만드는 것 |
| --- | --- | --- |
| 공유 기반 (테크 리드 · 석준영) | 루트 설정, 의존성 파일, `.gitignore`, `.env.example`, ruff 설정, `frontend/` 초기화, `vite.config.js`, README의 설치·실행 공통 절 | 공유 뼈대 (영역 폴더는 비워 둠), `vite.config.js`에 port 5173과 `/api` → `http://127.0.0.1:8080` proxy |
| 서버 (개발자1 · 이은채) | `backend/app/` | 서버 시작 지점, 상태 확인 주소 `GET /api/health` |
| 화면 (개발자2 · 김원우) | `frontend/src/` | 기본 화면 (제목 "디딤돌" + "서버 상태: ok" / 서버가 꺼져 있으면 "서버 연결 실패") |
| 테스트·실행 (테스트 담당 · 이효상) | `backend/tests/` | 서버 스모크 테스트 1개 (서버보다 먼저 써서 실패 확인 → 서버 PR 후 통과). 화면 테스트는 나중에 |
| 정리 담당 (리더 · 박승목) | `docs/`, PR 병합 | 문서, 병합 순서 관리 |

병합 순서: ① 공유 기반 PR → ② 서버·화면·테스트 PR (폴더가 달라 동시에 진행 가능) → ③ 5명 모두 새 폴더에 clone해서 실행 확인 (6절).

## 3. 설치와 실행 방법 (Mac)

> 설치·초기화 명령은 **공식 문서에서 확인한 것을 직접 실행한 것**만 적습니다.
> 아래 명령은 **계획 단계의 예상 형태**입니다. 아직 공식 문서로 확인하거나 실행한 사람이 없어 근거는 `미확인`, 실행한 사람은 `미실행`입니다. 확인·실행한 뒤 실제 명령으로 고칩니다.

| 단계 | 명령 | 실행 위치 | 근거 공식 문서 (주소·절) | 직접 실행한 사람 |
| --- | --- | --- | --- | --- |
| 사전 확인 | `uname -m`, `python3 --version`, `node --version` | 아무 곳 | 미확인 | 미실행 |
| 사전 설치 | `xcode-select --install`, Homebrew 설치, `brew install python@3.14`, `brew install node@24` | 아무 곳 | 미확인 (찾을 곳: docs.brew.sh "Installation", formulae.brew.sh `python@3.14`·`node@24`) | 미실행 |
| 가상환경·설치 | `python3 -m venv .venv` → `source .venv/bin/activate` → `python3 -m pip install -r requirements.txt` | `backend/` | 미확인 (찾을 곳: docs.python.org "venv", Packaging User Guide "Using a requirements file") | 미실행 |
| 프로젝트 초기화 | (공유 기반 담당 1회) `npm create vite@<버전> frontend -- --template react` 형태 → vite 8.3.4, react 19.3으로 맞춤 / (나머지) `npm ci` | 저장소 루트 / `frontend/` | 미확인 (찾을 곳: vite.dev "Scaffolding Your First Vite Project", docs.npmjs.com "npm ci") | 미실행 |
| 실행 | 서버: `uvicorn app.main:app --reload --port 8080` / 화면: `npm run dev` | `backend/`(venv 켠 상태) / `frontend/` | 미확인 (찾을 곳: uvicorn.org "Settings", vite.dev "Server Options") | 미실행 |
| 테스트 | 서버: `python3 -m pytest` / 화면: 테스트 미구성 (나중에 추가) | `backend/` | 미확인 (찾을 곳: docs.pytest.org "Get Started", fastapi "Tutorial – Testing") | 미실행 |
| 린트·포맷 | 서버: `ruff check .`, `ruff format --check .` / 화면: `npm run lint` (Prettier 미구성) | `backend/` / `frontend/` | 미확인 (찾을 곳: docs.astral.sh/ruff "The Ruff Linter"·"The Ruff Formatter", 생성된 `frontend/package.json`) | 미실행 |

- 서버 포트: **8080**, 화면 포트: **5173** (**5000은 쓰지 않음** — Mac AirPlay가 씀). 화면의 `/api` 요청은 Vite proxy로 서버에 전달 (CORS 설정 없음)
- 필요한 환경변수 이름 (값은 쓰지 않음, `.env.example`에 이름만): `BACKEND_PORT`(선택), `GEMINI_API_KEY`·`GEMINI_MODEL`·`DATABASE_PATH`(이름만 예약, 뼈대에서는 쓰지 않음). `.env`는 커밋하지 않고, 키는 서버에서만 읽음 (`VITE_`로 시작하는 이름에 키를 넣지 않음)
- 성공 기준 (무엇을 실행하면 무엇이 보이면 성공인가):
  1. `python3 --version` / `node --version` / `uname -m` → 3.14.x / v24.x / 내 칩(arm64 또는 x86_64)과 일치
  2. 서버 실행 → 터미널에 오류 없이 `http://127.0.0.1:8080` 실행 중 표시
  3. 브라우저 `http://127.0.0.1:8080/api/health` → `{"status":"ok"}`
  4. 브라우저 `http://127.0.0.1:8080/docs` → Swagger UI에 `GET /api/health` 1개
  5. `npm run dev` 후 `http://localhost:5173` → 제목 "디딤돌" + "서버 상태: ok"
  6. 서버를 끄고 5173 새로고침 → 빈 화면이 아니라 "서버 연결 실패" 문구
  7. `python3 -m pytest` → `1 passed`
  8. `ruff check .` / `ruff format --check .` → 오류 0개 / 바꿀 파일 없음
  9. `npm run lint` → 오류 없이 종료
- Apple Silicon 주의: Homebrew 경로가 Apple Silicon은 `/opt/homebrew`, Intel은 `/usr/local`. Rosetta로 실행한 터미널을 쓰지 않음 (`uname -m`과 `python3 -c "import platform; print(platform.machine())"` 값이 같은지 확인). `python3`가 macOS 기본 python3가 아니라 brew의 3.14인지 확인. `node@24`는 설치 후 PATH 안내(caveats)가 나오면 따름. `.venv`·`node_modules`는 칩마다 다르므로 복사·커밋하지 않고 각자 설치. 공유 기반 담당은 Apple Silicon·Intel 각 1대에서 먼저 설치해 보고 공유 PR을 올림.

## 4. 이번에 하는 것과 하지 않는 것

| 이번에 한다 | 이번에 하지 않는다 |
| --- | --- |
| 폴더·의존성·실행 설정 (`requirements.txt`, Vite 초기화, ruff, ESLint 기본) | PRD의 실제 업무 기능 (F-01~F-08) |
| 기본 화면 (제목 "디딤돌" + 서버 상태 한 줄) | 업로드·인식·입력 항목 등 기능 화면, MUI 설치 |
| 서버 시작 지점 (`GET /api/health`) | 실제 데이터 처리 (SQLite, OCR, Gemini 호출) |
| 실행·테스트 방법 (서버 스모크 테스트 1개) | 기능별 테스트, 화면 테스트, Prettier |

## 5. 계획 수정 요청 (정리 담당이 적음)

| 수정 요청한 내용 | 반영 / 보류 / 반영하지 않음 | 이유 |
| --- | --- | --- |
| | | |

## 6. 실행 확인 (5명 전원, 정리 담당이 모아 적음)

| 이름 | macOS 버전·칩 | 설치 | 기본 실행 | 테스트 명령 | 남은 문제 |
| --- | --- | --- | --- | --- | --- |
| | | 성공 / 실패 | 성공 / 실패 | 성공 / 실패 / 테스트 미구성 | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

실패한 팀원은 **실행한 명령과 오류 메시지**를 그대로 적습니다. "안 돼요"는 기록이 아닙니다.

## 7. 계획과 실제의 차이

| 계획 | 실제 | 이유 |
| --- | --- | --- |
| 루트 `.env.example` | `frontend/.env.example`, `backend/.env.example` | 화면과 서버가 각자 쓰는 환경변수 이름만 각 폴더에 둠 |
| `backend/requirements.txt` (fastapi, uvicorn, pytest, TestClient용 패키지, ruff) | 위에 `python-multipart`, `pypdf` 추가. TestClient용 패키지는 `httpx2` | US-01 #1: 파일 업로드 받기, PDF 쪽수 확인 |
| `python3 -m pytest` → `1 passed` | `backend/`에서 `pytest` → `11 passed` (US-01 #1 테스트 포함, Python 3.14.10 venv) | US-01 #1 테스트를 더함 |
