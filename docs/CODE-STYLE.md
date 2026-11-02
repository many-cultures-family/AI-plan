# 코딩 스타일 (팀 합의)

- 합의일: 2026.11.02
- 근거: `STACK.md`, `CLAUDE.md`, `SETUP-PLAN.md` 1~3절

## 규칙

| # | 규칙 | 지키는지 확인하는 방법 |
| --- | --- | --- |
| 1 | 이름 규칙: 서버의 파일·함수·변수는 소문자와 밑줄로 쓴다 (`get_status`). 화면의 컴포넌트와 파일은 단어 첫 글자를 대문자로 (`UploadPage.jsx`), 함수·변수는 첫 단어만 소문자로 쓴다 (`fileName`) | PR 리뷰에서 확인 |
| 2 | 포매터·린터: 서버는 ruff (설정 파일은 `ruff.toml`), 화면은 Vite가 만든 ESLint 설정을 그대로 쓴다. Prettier는 쓰지 않는다 | 명령: 서버 `ruff check .`, `ruff format --check .` / 화면 `npm run lint` (`SETUP-PLAN.md` 3절, 아직 확인·실행 안 함) |
| 3 | 폴더: 서버 코드는 `backend/app/`, 테스트는 `backend/tests/`, 화면 코드는 `frontend/src/`에 둔다. 자기 담당 폴더만 고친다. | PR에서 바뀐 파일이 담당 폴더 안에 있는지 확인 |
| 4 | 공유 파일(공통 코드, 설정, 의존성 파일)은 테크리더, 문서 공유 파일(`API.md`, `DATA-MODEL.md`)은 PM만 고친다 | PR에서 확인 |
| 5 | 커밋 메시지: `feat:` `fix:` `docs:` `chore:` `test:` + 내용 (1커밋 = 1의도) | `git log --oneline` |
| 6 | 테스트 이름: 어떤 스토리·인수 조건을 확인하는지 알 수 있게 쓴다 | `US-xx`가 이름이나 주석에 있다 |
| 7 | 테스트의 기대값을 구현에 맞춰 바꾸지 않는다 | `git diff`에 tests가 없다 |
| 8 | 비밀 값(키, 비밀번호)을 코드·문서에 쓰지 않는다 | `.env`만 사용, `.gitignore` 확인 |

## 담당 폴더
| 영역 | 폴더 | 수정할 수 있는 사람 |
| --- | --- | --- |
| 공유 (공통 코드, 설정, 의존성 파일) | 루트 설정 파일, `backend/requirements.txt`, ruff 설정 파일, `frontend/`의 설정 파일 (`package.json`, `vite.config.js` 등) | 테크리더 (요청은 PR 댓글로) |
| 서버 | `backend/app/` | 개발자1 |
| 화면 | `frontend/src/` | 개발자2 |
| 테스트 | `backend/tests/` | 테스트 담당 |
