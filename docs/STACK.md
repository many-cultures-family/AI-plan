# 기술 스택 결정 기록

> **저장 위치:** `docs/STACK.md`

> **결정은 팀이 합니다.** Claude는 후보 2안을 비교해 줄 뿐입니다. "AI가 추천해서"는 이유가 아닙니다. **우리 팀 경험·기간·핵심 기능**으로 씁니다.
> 확인하지 못한 버전이나 실행 명령은 추측하지 말고 `확인 필요`로 씁니다. `>`로 시작하는 안내 문장은 지워도 됩니다.

- 결정일:
- 근거: stack-inputs.md(팀 경험·조건), mvp-scope.md, backlog.md(필수 스토리)

## 우리 팀 상황
> 지난 시간에 쓴 `docs/decisions/stack-inputs.md`에서 요약해 옮깁니다. 새로 쓰지 않습니다.

| 항목 | 내용 |
| --- | --- |
| 서비스 | 항목 검증 + LLM/번역기 풀이 + LLM 수정 제안을 제공하는 웹 서비스 |
| 핵심 기능 (필수 스토리 기준) | 항목 검증, LLM 및 번역기 풀이, LLM 수정 제안 |
| 팀이 **직접 써 본** 언어·도구 (이름만 들어 본 것은 제외) | Java, Python(FastAPI, Flask, PyTorch, Numpy, Pandas), JavaScript(React, Vue), HTML/CSS, Lua, JSP, MySQL/PostgreSQL/MariaDB/SQLite/Oracle (팀원별 숙련도 차이 있음, 상세는 stack-inputs.md 참고) |
| 개발 기간 | 15시간 (남은 수업일 기준) |
| 화면 (웹 / 모바일, 반응형 여부) | 웹 |
| 시연 방식 (로컬 / 외부 접속) | 내 컴퓨터에서 (로컬) |
| 제약 (비용, 설치 권한, 외부 서비스) | 비용: 무료만 / 설치 권한·컴퓨터 환경 제약: 없음 / 외부 서비스 사용 제한: 없음 |

## 후보 2안 비교

| 비교 항목 | A안: React + FastAPI | B안: Spring Boot + Thymeleaf + OCR 사이드카 |
| --- | --- | --- |
| 프론트엔드 | React(Vite) | Thymeleaf 서버 렌더링 + 소량 JS |
| 백엔드 | FastAPI 단일 서버 | Spring Boot + OCR용 Python 사이드카 |
| DB | SQLite | SQLite 또는 H2 |
| UI 도구 | MUI 또는 Mantine | Bootstrap 5 |
| LLM 호출·키 | FastAPI 서버에서만 호출, 키는 `.env` (gitignore) | Spring 서버에서 호출, 키는 환경변수 또는 gitignore된 설정 파일 |
| LLM | Gemini 무료 티어 (한도 확인 필요) | 동일 |
| OCR | PaddleOCR 또는 EasyOCR | Tesseract(`brew install`) 또는 Python 사이드카 |
| 번역 | LLM + 프론트 i18n (Argos는 선택, 품질 확인 필요) | LLM + Spring MessageSource |
| 마스킹 | OCR 직후, LLM 호출 전 한 함수에서 | OcrResult → MaskingService → LlmClient |
| 써 본 기술 | Python/FastAPI, React(석준영), JS(김원우) | Java/Spring Boot, JSP, Python |
| 새로 배워야 할 것 | OCR 엔진, Gemini, React(3명) | Tesseract, Java에서 Gemini 연동, Thymeleaf, Spring↔FastAPI 연동 |
| 화면·서버 연결에서 어려울 곳 | React(SPA) ↔ FastAPI API 연동 | Spring Boot ↔ Python OCR 사이드카 간 프로세스 통신 |
| 테스트·실행 재현 (Mac·Apple Silicon) | Paddle·EasyOCR의 arm64 지원 공식 확인 못 함, 첫 실행 시 모델 다운로드 | JDK 17+ 필요, Tesseract arm64 확인 못 함, 한국어 데이터 별도 설치 |
| 비용·무료 한도 (확인한 것 / 확인 필요) | Gemini 무료 티어 사용 (한도 확인 필요) | Gemini 무료 티어 사용, 동일 (한도 확인 필요) |

## 최종 선택

- 선택한 안: A안 (React + FastAPI)
- 프론트엔드: React(Vite)
- 백엔드: FastAPI 단일 서버
- DB: SQLite
- UI 도구: MUI 또는 Mantine
- OCR 엔진: **EasyOCR** (ko+en). 아래 "OCR 엔진 선정" 절 (2026-11-23 기록)
- 테스트 방식: 미정
- 시연·배포 환경: 로컬

## 선택 이유 (팀 경험·기간·핵심 기능으로)
1. 팀 경험: 기술 스택 대다수가 팀원들에게 익숙하고 직접 써 본 적 있는 것들임
2. 빠른 개발 및 테스트: Java보다 Python이 빠른 개발 및 테스트가 가능하다고 판단
3. 핵심 기능: AI(LLM) 기술을 활용할 것을 생각하면 Python이 더 적합하다고 판단

## 선택하지 않은 안과 이유
1. B안(Spring Boot + Thymeleaf + OCR 사이드카): A안에 비해 배워야 할 기술 스택이 많아 개발이 더뎌질 것으로 예상
2. B안의 기술 스택을 어려워하는 팀원 존재

## LLM 연결
> 우리 서비스에서 LLM이 맡는 일(초안·요약·분류·설명)을 어느 스택에서 호출하는지, 상태를 바꾸는 최종 결정은 어디서 하는지 한 줄로 씁니다.
- LLM은 항목 검증 결과의 분류·설명을 담당하며, FastAPI 서버에서만 호출한다. 검증 통과/실패 등 상태를 바꾸는 최종 결정도 FastAPI 서버에서 처리한다.

## 예상 어려움과 대응
| 어려움 | 대응 |
| --- | --- |
| OCR 엔진(PaddleOCR/EasyOCR) 경험 부족, Apple Silicon(arm64) 지원 공식 미확인 | 초반에 설치·실행부터 먼저 테스트, 문제 시 다른 OCR 엔진으로 교체 → EasyOCR이 Apple M3에서 설치·실행됨을 확인 (아래 "OCR 엔진 선정") |
| Gemini API 경험 부족, 무료 티어 호출 한도 확인 필요 | 공식 문서로 한도 먼저 확인, 개발 중에는 호출 횟수를 최소화 |
| React 미경험 팀원 존재 | 경험자(석준영) 주도로 컴포넌트 단위로 작업을 나눠 분담 |
| AI 기능과 웹(React↔FastAPI) 연동 경험 부족 | API 요청/응답 형식을 먼저 정하고, 프론트는 목데이터로 먼저 개발 |
| 개인정보가 OCR로 뽑혀 Gemini로 나갈 수 있음 | OCR 직후 한 곳에서 마스킹 후 LLM 호출, 원문은 서버 DB에만 저장 |
| 무료 한도·모델명 문제로 시연 중 호출 실패 가능 | 모델명은 `.env`로 분리, 한도 미리 확인, 시연용 결과 미리 저장해 대체 |
| AI 답을 그대로 믿어 틀린 결과가 확정될 수 있음 | AI 결과는 제안으로만 저장, 상태 변경은 서버에서 검증·사용자 확인 후 처리 |

## 확인할 것
| 확인할 내용 | 담당 | 언제 |
| --- | --- | --- |
| PaddleOCR 문서 구조 분석이 M4 외 Apple Silicon(M1~M3)에서도 되는지 확인 | 석준영 | 10월 27일까지 → **미확인으로 끝냄.** EasyOCR로 정해 확인하지 않음 (2026-11-23) |
| EasyOCR의 문서 구조 분석 지원 여부 확인 | 석준영 | 10월 27일까지 → **확인함 (2026-11-23).** 글자 덩어리 위치·글자·신뢰도만 주고 표 구조(행·열)는 주지 않음. 서버 코드에서 보완 (아래 "OCR 엔진 선정") |

## OCR 엔진 선정 (2026-11-23 기록, 석준영)

| 항목 | 내용 |
| --- | --- |
| 선정 엔진 | **EasyOCR 1.7.2**, 언어 `ko` + `en` |
| PDF 처리 | `pymupdf 2.1`로 쪽마다 200dpi 회색조 이미지로 바꾼 뒤 인식. PNG·JPG는 그대로 인식 |
| 실행 장치 | Apple Silicon이면 GPU(MPS), 아니면 CPU |
| 의존성 크기 | `easyocr` 설치 때 PyTorch가 같이 깔려 **약 1GB**. 모델 약 95MB는 첫 실행 때 `~/.EasyOCR/`에 받는다(저장소에 올리지 않음) |
| Apple Silicon 실측 | 석준영 Mac(Apple M3), 2026-11-23, 가짜 데이터: arm64에서 설치·실행됨. 첫 요청은 모델 다운로드·로딩으로 20초 넘게, 그 뒤 1쪽 GPU(MPS) 약 1~3초, CPU 약 6초 |
| 주는 것 | 글자 덩어리마다 네 꼭짓점 위치, 글자, 신뢰도 |
| 주지 않는 것과 보완 | 표 구조(행·열) → 같은 줄 박스 합치기 / 빈 칸·체크 상자·밑줄 위치 → OpenCV로 원본 그림에서 찾기 / 글자 기울기 각도 없음 / 체크 상자 `□`를 글자로 잘못 읽음 → L1 프롬프트에 알림 (`docs/api/OCR-API.md`, `VIRTUAL-FORM-API.md`) |
| 고르지 않은 엔진 | PaddleOCR — 같은 문서로 비교 실행하지 않았다. 엔진에 따라 달라지는 코드는 코드 저장소 `backend/app/ocr.py` 한 파일이라, 필요하면 그 파일만 바꿔 비교한다 |
| 코드 저장소 기록 | `stepping-stone` `docs/ocr-engine.md` (같은 내용 + 코드 위치) |

## 의견이 갈렸다면
> 갈린 의견과, 어떤 정보가 부족했는지를 씁니다. 중요한 불확실성이 남았다면 **임시 선택과 확인 조건**을 남깁니다.
-
