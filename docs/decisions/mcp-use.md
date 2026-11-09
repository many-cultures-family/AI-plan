# MCP 사용 기록

- 작성 시작일: 261102

## 1. 팀 결정 — 우리 팀에 필요한 MCP

> 쓰지 않기로 했습니다. 저희 팀에서 써야 할 MCP가 딱히 없다고 판단했기 때문입니다.

**필요한 일 파악** (`STACK.md`, `PRD.md`, `backlog.md`를 보고 외부 도구가 있으면 좋은 일)

| 필요한 일 | 왜 필요한가 (우리 팀 상황에서) |
| --- | --- |
| 화면 동작 확인 | 화면 자동 테스트가 아직 없어서 수동으로 확인한다. 다만 `first-feature.md` 3절은 내가 직접 브라우저에서 연 결과만 근거로 인정하므로, 자동화 도구의 결과로 대신할 수 없다. 지금 단계에서는 외부 도구가 꼭 필요하지 않다. |
| 라이브러리 공식 문서 조회 | React, Vite, MUI, FastAPI 버전이 고정되어 있어 문서 버전이 어긋날 수 있다. 다만 공식 문서를 직접 열어 확인하면 되고 필수는 아니다. |
| 저장소·PR·이슈 작업 | 코드 PR 리뷰와 병합이 있다. 지금은 GitHub 웹 화면과 git으로 한다. |
| 데이터베이스 내용 확인 | 업로드 기능이 DB에 행을 만드는지 볼 때 필요하다. 서버가 만든 SQLite 파일을 직접 열어 확인할 수 있다. |

**후보 비교와 선택** (Claude가 찾아 준 것도 공식 문서·저장소로 직접 확인한 것만 적음)

| 후보 서버 | 공식 문서·저장소 (주소, 절) | 하는 일 | 내 컴퓨터에서 실행되는 명령 | 읽기만 / 쓰기도 | 키 필요 | 고른다 / 보류 / 고르지 않는다 | 이유 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Playwright MCP | https://github.com/microsoft/playwright-mcp (절: Getting started, Requirements, Security, Configuration, 확인일 2026-11-03) | 브라우저를 자동으로 조작해 화면을 열고 클릭·입력·스크린샷 등을 한다 | `npx @playwright/mcp@latest` (설정 예시의 `command`: `npx`, `args`: `@playwright/mcp@latest`). Node.js 18 이상 | 쓰기도 (브라우저 조작 도구. `browser_run_code_unsafe`는 서버 프로세스에서 임의 JavaScript를 실행하며 문서가 RCE-equivalent라고 적음) | 문서에서 키 언급을 찾지 못함 | 고르지 않는다 | (1) 화면 확인은 내가 직접 브라우저에서 연 결과만 근거로 인정한다(`first-feature.md` 3절). (2) 문서가 "not a security boundary"라고 경고한다(절: Security). (3) 지금 필요한 일이 없다. 화면 자동 테스트를 시작하면 다시 본다. |
| Context7 | https://github.com/upstash/context7 (절: Installation, Available Tools, Disclaimer, 확인일 2026-11-03) | 라이브러리 공식 문서를 조회한다 | 이 페이지에서 로컬 실행의 `command`·`args`를 찾지 못함(설치는 `npx ctx7 setup` 또는 원격 `https://mcp.context7.com/mcp`). Node.js 22.13 이상(ctx7 CLI). 실행 명령 미확인 | 문서에 읽기·쓰기 구분이 적혀 있지 않음 (미확인) | 선택. "API Key Recommended", 무료 키가 있으면 한도가 높아진다(수치 없음) | 고르지 않는다 | (1) 로컬 실행 명령을 문서에서 확인하지 못했다. (2) 도구 매개변수에 `query` 등이 있어 질문이 외부 서버로 가는 것으로 보이며, 서버 쪽 동작은 비공개라고 적혀 있다(절: Disclaimer). (3) 공식 문서를 직접 열어 보면 되고, 지금 필요한 일이 없다. |
| GitHub MCP Server | https://github.com/github/github-mcp-server (절: Local GitHub MCP Server > Prerequisites, Installation, Remote GitHub MCP Server, Tool Configuration, 확인일 2026-11-03) | GitHub 저장소·이슈·PR 등을 조작한다 | 원격: `https://api.githubcopilot.com/mcp/`. 로컬: `docker run -i --rm ghcr.io/github/github-mcp-server`(Docker 필요) 또는 Go로 빌드해 `github-mcp-server stdio`. 이 값들은 전체 `command`·`args`가 아님 | 쓰기도 (`--read-only` 읽기 전용 모드가 문서에 있으나 켜는 방법은 확인하지 못함) | 원격은 OAuth 또는 PAT. 로컬(github.com)은 OAuth가 기본이고 PAT(`GITHUB_PERSONAL_ACCESS_TOKEN`)는 선택. Go 빌드 예시는 PAT를 읽음 | 고르지 않는다 | (1) 쓰기 도구가 있어 PR·이슈를 바꿀 수 있다. (2) 5명이 Docker 설치 또는 로그인·토큰 설정을 해야 한다. (3) 지금은 GitHub 웹 화면과 git으로 충분하다. |
| SQLite MCP Server | https://github.com/modelcontextprotocol/servers-archived (절: About this Archive > Security Notice, Archived Servers, 확인일 2026-11-03) | SQLite DB를 조회·수정한다(하위 README는 열지 못해 미확인) | 미확인 (저장소 첫 화면에 실행 명령이 없고 하위 페이지는 가져오지 못함) | 미확인 | 미확인 | 고르지 않는다 | 저장소가 2025-05-29에 보관(archived)되어 읽기 전용이 되었고, "더 이상 유지되지 않으며 보안 보장이 없다"는 안내가 있다. 유지되는 서버는 `modelcontextprotocol/servers`를 보라고 안내한다. DB 내용은 SQLite 파일을 직접 열어 확인할 수 있다. |

| 항목 | 우리 결정 |
| --- | --- |
| 쓰는 서버 (팀당 1~2개부터. 없으면 "연결하지 않음"과 이유) |  연결하지 않음. 이유: 팀이 써야 할 MCP가 딱히 없다고 판단했다. 후보 4개를 공식 문서로 확인했지만 지금 필요한 일은 외부 도구 없이 할 수 있다. |
| 설정 위치 | 해당 없음(연결하지 않음). 저장소에 `.mcp.json`을 두지 않는다 |
| 승인 방법 | 해당 없음(연결하지 않음) |
| 버전 고정 여부 🔧 |  해당 없음(연결하지 않음). 참고: Playwright MCP 설정 예시는 `@latest`라서 나중에 쓰게 되면 버전을 고정해야 한다. |
| 설치에 쓴 공식 문서 (주소, 절) |  설치하지 않음. 후보 확인에만 위 표의 공식 저장소 4곳(2026-11-03)을 사용했다. |
| 보류한 서버와 이유 |  Playwright MCP는 화면 자동 테스트를 시작할 때 다시 검토한다. 나머지 3개는 보류하지 않고 고르지 않는다(위 표의 이유). |

## 2. 연결 확인 (5명 전원, 구현을 시작하기 전에)

1절 결정에 따라 MCP를 연결하지 않으므로, 연결 확인(노션 기준 ③)은 하지 않는다 (2026-11-03 팀 결정).
그래서 아래 표의 확인 칸은 모두 `미실행`으로 둔다. 나중에 MCP를 연결하기로 하면 이 절을 다시 쓴다.

| 이름 | 따로 설치한 것 (런타임·브라우저 등, 공식 문서 주소) | `claude mcp list` 상태 (저장소 루트에서 실행한 출력 그대로, 프로젝트/개인 구분) | `/mcp` 상태 (세션 안에서 본 것 그대로, 프로젝트/개인 구분) | 남은 문제 (실패하면 운영체제, 명령, 오류 메시지 그대로) |
| --- | --- | --- | --- | --- |
| 석준영 | 없음(연결하지 않음) | 미실행 | 미실행 | 미실행 |
| 이은채 | 없음(연결하지 않음) | 미실행 | 미실행 | 미실행 |
| 김원우 | 없음(연결하지 않음) | 미실행 | 미실행 | 미실행 |
| 이효상 | 없음(연결하지 않음) | 미실행 | 미실행 | 미실행 |
| 박승목 | 없음(연결하지 않음) | 미실행 | 미실행 | 미실행 |

## 3. 사용 기록

| 날짜 | 누가 | MCP (서버 이름) | 어떤 작업 | 무엇을 요청했나 | 무엇을 얻었나 | 내가 직접 확인한 것 | 쓰지 않은 것과 이유 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
