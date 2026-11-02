# 디딤돌

## 팀

| 항목 | 내용 |
| --- | --- |
| 팀명 | IDPD |
| 배정받은 큰 도메인 | 다문화 가정을 위한 디지털 적응·교육 서비스 |
| 세부 주제 (한 줄) | `다문화 가정 구성원`(누가)가 `공문서 작성 연습`(무엇)을 할 수 있게 하는 서비스 |
| 팀원과 역할 | [docs/team/roles.md](docs/team/roles.md) |

## 세부 주제 필수 조건

| 조건 | 우리 주제에서는 | 자세히 |
| --- | --- | --- |
| LLM이 서비스 기능 안에서 쓰인다 | 공고문·신청서 내용을 모국어와 쉬운 한국어로 설명하고 가상 신청서 초안을 만들어 상담원·사용자가 확인한다 | [03-rules-states-llm.md](docs/domain/03-rules-states-llm.md#3-4-llm이-들어갈-자리) |
| 핵심 대상에 상태 전이가 있다 | 신청 건: 접수됨 → 연습환경 검토중 → 리허설중 → 실전준비완료 → 실전작성중 → 최종점검완료 → 제출완료 → 승인·반려 → 종결 (취소·만료·보완요청 분기) | [03-rules-states-llm.md](docs/domain/03-rules-states-llm.md#3-2-핵심-대상과-상태-전이) |

## 문서 지도

| 단계 | 파일 | 하는 일 | 상태 |
| --- | --- | --- | --- |
| 0 | [docs/team/roles.md](docs/team/roles.md) | 팀 구성, 역할, 교대 계획 | ☑ |
| 0 | [docs/domain/README.md](docs/domain/README.md) | 조사 관점, 태그 규칙, 파일 규칙, 찾아볼 곳 | 읽기만 |
| 1 | [docs/domain/01-first-look-glossary.md](docs/domain/01-first-look-glossary.md) | 첫인상, 용어 사전, 검색어 | ☑ |
| 2 | [docs/domain/02-people-flow-benchmark.md](docs/domain/02-people-flow-benchmark.md) | 사람, 현재 흐름, 데이터, 기존 서비스, 논문 | ☑ |
| 3 | [docs/domain/03-rules-states-llm.md](docs/domain/03-rules-states-llm.md) | 규칙, 상태 전이, LLM 자리, 법령·통계 | ☑ |
| - | [docs/domain/cards/](docs/domain/cards/) | 논문·자료 근거 카드 (카드마다 파일 하나) | ☑ |
| - | [docs/domain/ai-check-log.md](docs/domain/ai-check-log.md) | AI에게 물어본 것과 확인 결과 | ☑ |
| 4 | [docs/decisions/topic-selection.md](docs/decisions/topic-selection.md) | 필수 조건 확인, 후보 평가, 주제 확정 | ☑ |
| 5 | [docs/interview/mvp-assumptions-questions.md](docs/interview/mvp-assumptions-questions.md) | MVP 가설, 기능 목록, 가정·위험, 질문지, 미팅 준비 | ☑ |
| 5 | [docs/interview/client-meeting-1.md](docs/interview/client-meeting-1.md) | 클라이언트 미팅 1 질의응답, 피드백 판정 | ☐ |
| 6 | [docs/proposal/README.md](docs/proposal/README.md) | **클라이언트에게 보내는 프로젝트 제안서** (Claude 초안 → 팀 확인 → Word 양식, 완성본 docx·PDF) | ☐ |
| - | `logs/pre-[GitHub 아이디].md` | 개인 회고 (사람마다 파일 하나) | ☐ |
| 2-2 | [docs/STACK.md](docs/STACK.md) | 기술 스택 결정과 이유 | ☐ |
| 2-2 | [docs/PRD.md](docs/PRD.md) | 정한 문서로 가는 안내판 PRD v0.1 | ☐ |
| 2-2 | [docs/SETUP-PLAN.md](docs/SETUP-PLAN.md) | 승인한 초기화 계획과 5명 실행 확인 | ☐ |
| 2-2 | [CLAUDE.md](CLAUDE.md) | Claude가 매 세션 읽는 팀 지침 | ☐ |
| 2-2 | [.claude/agents/](.claude/agents/) | stack-advisor | ☐ |
| 3-1 | [docs/decisions/prd-review.md](docs/decisions/prd-review.md) | PRD 검토 지적과 팀 판단 | ☐ |
| 3-1 | [docs/DATA-MODEL.md](docs/DATA-MODEL.md) | 데이터 구조·상태값·시드 데이터 | ☐ |
| 3-1 | [docs/DESIGN.md](docs/DESIGN.md) | UI 디자인 방향·토큰·화면 목록 | ☐ |
| 3-1 | [docs/CODE-STYLE.md](docs/CODE-STYLE.md) | 팀 코딩 스타일 | ☐ |
| 3-1 | [.mcp.json](.mcp.json) | 팀이 고른 MCP 서버 설정 (키 없음). **MCP를 고른 팀만** | ☐ |
| 3-1 | [docs/decisions/mcp-use.md](docs/decisions/mcp-use.md) | MCP를 고른 이유(또는 고르지 않은 이유), 설치, 연결 확인, 사용 기록 | ☐ |
| 3-1 | [docs/decisions/first-feature.md](docs/decisions/first-feature.md) | 우리가 고른 첫 기능과 범위, 실행 확인 | ☐ |
| 3-1 | [docs/API.md](docs/API.md) | 화면·서버가 주고받는 약속 (기능 1항목) | ☐ |
| 3-1 | [.claude/agents/](.claude/agents/) | prd-reviewer | ☐ |


## 논문·자료 근거 카드

| 순서 | 파일 | 팀원 이름 |
| --- | --- | --- |
| 1 | [1-kimwonu-bit-01.md](docs/domain/cards/1-kimwonu-bit-01.md) | 김원우 |
| 2 | [1-kimwonu-bit-02.md](docs/domain/cards/1-kimwonu-bit-02.md) | 김원우 |
| 3 | [1-kimwonu-bit-03.md](docs/domain/cards/1-kimwonu-bit-03.md) | 김원우 |
| 4 | [1-kimwonu-bit-04.md](docs/domain/cards/1-kimwonu-bit-04.md) | 김원우 |
| 5 | [2-kimwonu-bit-01.md](docs/domain/cards/2-kimwonu-bit-01.md) | 김원우 |
| 6 | [2-leehyosang6950-01.md](docs/domain/cards/2-leehyosang6950-01.md) | 이효상 |
| 7 | [2-leehyosang6950-02.md](docs/domain/cards/2-leehyosang6950-02.md) | 이효상 |
| 8 | [4-kimwonu-bit-01.md](docs/domain/cards/4-kimwonu-bit-01.md) | 김원우 |
| 9 | [4-kimwonu-bit-02.md](docs/domain/cards/4-kimwonu-bit-02.md) | 김원우 |
| 10 | [4-kimwonu-bit-03.md](docs/domain/cards/4-kimwonu-bit-03.md) | 김원우 |
| 11 | [5-kimwonu-bit-01.md](docs/domain/cards/5-kimwonu-bit-01.md) | 김원우 |
| 12 | [5-kimwonu-bit-02.md](docs/domain/cards/5-kimwonu-bit-02.md) | 김원우 |
| 13 | [5-kimwonu-bit-03.md](docs/domain/cards/5-kimwonu-bit-03.md) | 김원우 |
| 14 | [5-leehyosang6950-01.md](docs/domain/cards/5-leehyosang6950-01.md) | 이효상 |
| 15 | [5-sjy0128-01.md](docs/domain/cards/5-sjy0128-01.md) | 석준영 |
| 16 | [5-sjy0128-02.md](docs/domain/cards/5-sjy0128-02.md) | 석준영 |
| 17 | [5-sjy0128-03.md](docs/domain/cards/5-sjy0128-03.md) | 석준영 |

## 개인 회고

| 파일 링크 | 이름 | 깃허브 닉네임 |
| --- | --- | --- |
| `pre-tmdahr.md` | 박승목 | tmdahr |
| `pre-sjy0128.md` | 석준영 | sjy0128 |
| `pre-dldmsco-29.md` | 이은채 | dldmsco-29 |
| `pre-kimwonu-bit.md` | 김원우 | kimwonu-bit |
| `pre-leehyosang6950.md` | 이효상 | leehyosang6950 |

## 작업 규칙

- 첫 커밋 이후에는 main에 바로 커밋하지 않습니다. 모든 변경은 브랜치를 만들고 PR로 올립니다. 문서(조사 파일, 회고 등) PR은 작성자가 셀프 병합할 수 있고, 코드처럼 중요하거나 반드시 확인이 필요한 PR은 작성자 외 팀원 1명 이상이 승인한 뒤에 병합합니다. v2·제안서 PR은 작성자 제외 4명이 승인해야 합니다.
- 표가 있는 단계 파일(01~03, topic-selection 등)은 **블록마다 정리 담당 1명**이 고칩니다. 다른 사람은 근거 카드를 쓰거나 PR에 댓글을 남깁니다. 여러 명이 같은 파일을 동시에 고치면 충돌이 납니다.
- 근거 카드와 개인 회고는 사람마다 파일이 달라 동시에 써도 충돌하지 않습니다.
## 설치·실행

> **아직 아무도 공식 문서로 확인하거나 실행하지 않은 계획 단계 명령입니다.** 버전은 팀이 정한 값이고, 명령은 `[추정]`입니다.
> 각자 공식 문서를 보고 직접 실행한 뒤, 다른 점은 [docs/SETUP-PLAN.md](docs/SETUP-PLAN.md) 7절에, 실행 결과는 6절에 적습니다.
> `backend/`, `frontend/` 폴더는 공유 기반 PR이 병합된 뒤에 생깁니다.

### 사용하는 버전

| 기술 | 버전 | 설치 방법 |
| --- | --- | --- |
| Python | 3.14 | Homebrew (Windows는 아래 참고) |
| FastAPI | 0.162.0 | `backend/requirements.txt` (pip) |
| Uvicorn | 0.54.0 | `backend/requirements.txt` (pip), **서버는 Uvicorn으로 실행** |
| Node.js | 24 LTS | Homebrew (Windows는 아래 참고) |
| Vite | 8.3.4 | `frontend/package.json` (npm) |
| React | 19.3 | `frontend/package.json` (npm) |
| MUI | 9.5 | `frontend/package.json` (npm), 뼈대 단계에서는 설치하지 않음 |

- 포트: 서버 **8080**, 화면 **5173**. **5000번은 쓰지 않습니다** (Mac AirPlay가 사용)
- `.venv/`, `node_modules/`는 OS·칩마다 다르므로 복사하거나 커밋하지 않고 각자 설치합니다
- 비밀값은 `.env`에만 두고, 변수 이름은 `.env.example`을 봅니다

### 1. Python·Node.js 설치

**macOS (Apple Silicon·Intel)**

```bash
xcode-select --install          # 처음 한 번
# Homebrew 설치: https://brew.sh 의 설치 명령을 그대로 실행
brew install python@3.14
brew install node@24            # 설치 후 나오는 PATH 안내(caveats)를 따름
```

- Homebrew 경로: Apple Silicon `/opt/homebrew`, Intel `/usr/local`
- Rosetta 터미널을 쓰지 않습니다. `uname -m`과 `python3 -c "import platform; print(platform.machine())"` 값이 같아야 합니다

**Linux (Ubuntu 등)**

```bash
# Homebrew on Linux 설치: https://brew.sh 의 설치 명령 + 안내된 PATH 설정
brew install python@3.14
brew install node@24
```

**Windows 10·11** (Homebrew가 Windows를 지원하지 않으므로 winget 또는 공식 설치 파일)

```powershell
winget install Python.Python.3.14     # 또는 python.org 설치 파일 ("Add python.exe to PATH" 체크)
winget install OpenJS.NodeJS.LTS      # 또는 nodejs.org의 24 LTS 설치 파일
```

- WSL2(Ubuntu)를 쓴다면 위 Linux 방법을 따릅니다

**설치 확인 (모든 환경)**

```bash
python3 --version    # Windows: py -3.14 --version  → Python 3.14.x
node --version       # → v24.x
```

### 2. 서버 (FastAPI + Uvicorn)

`backend/` 폴더에서 실행합니다.

| 단계 | macOS·Linux | Windows (PowerShell) |
| --- | --- | --- |
| 가상환경 만들기 (처음 한 번) | `python3 -m venv .venv` | `py -3.14 -m venv .venv` |
| 가상환경 켜기 | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| 의존성 설치 | `python -m pip install -r requirements.txt` | 같음 |
| 서버 실행 | `uvicorn app.main:app --reload --port 8080` | 같음 |

- Windows에서 `Activate.ps1`이 막히면 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`를 한 번 실행합니다
- 확인: 브라우저에서 `http://127.0.0.1:8080/api/health` → `{"status":"ok"}`, `http://127.0.0.1:8080/docs` → Swagger UI

### 3. 화면 (React + Vite)

`frontend/` 폴더에서 실행합니다. 명령은 모든 OS에서 같습니다.

```bash
npm ci          # package-lock.json 그대로 설치 (npm install 아님)
npm run dev     # http://localhost:5173
```

- 화면의 `/api` 요청은 Vite proxy로 `http://127.0.0.1:8080`에 전달됩니다. 서버를 먼저 켭니다
- 확인: `http://localhost:5173` → 제목 "디딤돌" + "서버 상태: ok"

### 4. 테스트·린트

| 대상 | 명령 | 위치 |
| --- | --- | --- |
| 서버 테스트 | `python -m pytest` | `backend/` (가상환경 켠 상태) |
| 서버 린트·포맷 | `ruff check .` / `ruff format --check .` | `backend/` (가상환경 켠 상태) |
| 화면 린트 | `npm run lint` | `frontend/` |
| 화면 테스트 | 테스트 미구성 | — |