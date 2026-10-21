# cs-study-map · 나만을 위한 컴퓨터 과학 교재

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

이 프로젝트는 주로 관리자의 자기 학습을 위한 것입니다. [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT)에서 학습할 주제를 찾고 선수 지식 순서에 따라 중국어 교재로 재구성하며 설명, 창작 예제, 풀이가 있는 연습문제, 자가 점검을 더합니다. 동기화, AI 분류, 자료 안내는 교재 선정과 갱신을 돕습니다.

**[교재](../textbook/index.md)** · [학습 지도](../index.md) · [범위](../status.md) · [사용 안내](../usage.md) · [출처 및 라이선스](../../ATTRIBUTION.md)

Pleniluner가 관리하는 개인 학습 프로젝트이며 칭화대학교나 상류 저장소 관리자와 공식 관계가 없습니다. 공개 저장소에는 자체 도구, 교재 초안, 출처 색인, AI 안내가 포함됩니다. 원본 교재, 강의자료, 과제, 학생 소스 코드, 추출 전문은 공개하지 않습니다.

## 아홉 장을 순서대로 학습하기

| # | 주제 | 실습 |
| --- | --- | --- |
| 1 | [이진수, 바이트, 리틀 엔디언](../textbook/01-data-and-bytes.md) | 수를 바이트로 나눈 뒤 메모리에서 복원하기 |
| 2 | [레지스터, 메모리, 스택](../textbook/02-execution-and-stack.md) | 간단한 기계의 상태를 단계별로 추적하기 |
| 3 | [최초 적합, 분할, 병합](../textbook/03-first-fit.md) | 할당과 해제를 손으로 계산하고 외부 단편화 설명하기 |
| 4 | [순차 실행, 분기, 반복](../textbook/04-control-flow.md) | 변수를 추적하고 경계 사례와 반복 종료 조건 확인하기 |
| 5 | [매개변수, 반환값, 함수](../textbook/05-functions.md) | 함수를 조합하고 출력, 반환, 지역 이름 구분하기 |
| 6 | [배열과 순차 리스트](../textbook/06-arrays.md) | 인덱스, 용량, 리스트 공유, 원소 이동 추적하기 |
| 7 | [단일 연결 리스트](../textbook/07-linked-lists.md) | 노드 참조를 추적하고 삽입, 삭제, 연결 뒤집기 연습하기 |
| 8 | [스택](../textbook/08-stacks.md) | 후입선출로 실행 취소와 괄호 짝 검사하기 |
| 9 | [큐와 원형 배열](../textbook/09-queues.md) | 선입선출, 인덱스 순환, 빈 상태와 가득 찬 상태 확인하기 |

4–9장은 Python 3.11 이상을 사용하며, 독립적으로 실행할 수 있는 프로그램 60개와 예상 출력을 제공합니다. 환경 준비와 연습 방법은 중국어로 작성된 [프로그래밍 연습 안내](../programming-practice.md)와 [자료 구조 연습 안내](../data-structures-practice.md)를 참고하세요.

각 장에는 자세한 설명, 창작 예제 2개, 펼쳐 볼 수 있는 풀이가 있는 연습문제 3개, 자가 점검과 출처가 있습니다. AI 초안이며 분야 전문가 검토나 학습자 시범 학습을 거치지 않았습니다. 모든 과목의 교재가 완성되었다는 뜻은 아닙니다.

## 할 수 있는 일

장별로 학습하고 개인 메모는 Git에서 제외되는 `.local/`에 보관합니다. 식별한 주제로 새 장을 작성하며 출처 버전을 기록할 수 있습니다. 분야, 과목, AI가 식별한 지식으로 자료를 찾아 상류 저장소의 고정 버전을 열고 주제, 선수 지식, 제안과 근거 위치를 확인할 수 있습니다. 변경되지 않은 분석을 재사용하고 수동 규칙으로 자동 분류를 수정할 수 있습니다.

AI 안내에는 추출 범위, 모델, 수동 검증 여부가 표시됩니다. 자료 색인의 완전성과 AI 안내의 범위는 별도로 집계하며 부분 추출, 미지원 형식, 실패도 표시합니다.

## 빠른 시작

Python 3.11 이상이 필요합니다. 아래 단계는 메타데이터를 가져오고 탐색 페이지를 만듭니다. 모델 키가 필요하지 않으며 자료 본문을 내려받지 않습니다.

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

## AI 실행 방식

두 방식은 같은 검증 및 안내 생성 과정을 사용합니다. 모델 API는 `CS_STUDY_API_BASE`, `CS_STUDY_MODEL`, `CS_STUDY_API_KEY`를 설정합니다. 로컬 Codex CLI는 `CS_STUDY_PROVIDER=codex`, `CS_STUDY_MODEL`을 설정하고 필요하면 `CS_STUDY_CODEX_BIN`도 지정합니다. API는 Chat Completions와 Responses를 지원합니다. 기본값은 `chat`이며 `CS_STUDY_API_STYLE=responses`로 전환합니다. 서비스가 지원하는 모델을 선택해야 합니다. Codex CLI도 선택한 모델을 지원하는 버전이어야 하며 인증 정보는 CLI가 관리합니다.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

설정, PowerShell 예제, GitHub 설정은 [사용 안내](../usage.md)를 참고하세요.

## 정기 동기화

GitHub Actions는 매일 상류 저장소를 확인하며 **Sync study map**으로 수동 실행할 수도 있습니다. 모델이 설정되면 예산 안에서 안내와 교재 장을 만들고 검증 후 커밋합니다. 기본 하루 상한은 자료 분석 6개와 교재 작성 1장입니다. 범위는 `config/curriculum.json`에서 설정합니다.

모델이 없어도 목록을 동기화하고 `not-configured`를 보고합니다. 기존 안내는 계속 사용할 수 있고 변경된 자료는 분석을 기다립니다. 파일명 규칙이나 모의 출력을 완료된 AI 작업으로 표시하지 않습니다. 공개 지도 열람에는 모델 계정이 필요 없습니다. Fork에는 자체 API 설정이 필요하며 로컬 Codex 로그인은 GitHub에 업로드하지 않습니다. 장기간 활동이 없으면 예약 실행이 중지될 수 있으며 Actions에서 다시 켤 수 있습니다.

## 프로젝트 구성

```text
config/                  학습 경로, 출처, 분류, 과목 매핑, 수동 수정
catalog/                 메타데이터, 분석, 교재 초안, 범위 통계
docs/textbook/           GitHub에서 읽을 수 있는 교재(현재 중국어)
docs/                    강의·분야 탐색, 학습 기록 서식, 사용 안내
src/cs_study_map/        동기화, 추출, AI 분류, 교재 작성
tests/                   동기화, 복구, 출처, 공개 내용 검증
.github/workflows/       예약 동기화 및 지속적 통합
.cache/                  로컬 원본 및 추출 캐시; 커밋 금지
.local/                  개인 학습 기록; 커밋 금지
```

README 번역은 교재 본문 번역을 뜻하지 않습니다. 현재 본문은 중국어입니다.

초기 분야 매핑은 관리자의 개인 과목 정리에서 가져왔으며 수정할 수 있습니다. 공식 분류나 대학 교육과정이 아닙니다. 새 과목은 분류 대기로 표시합니다. 텍스트, 일반 소스 코드, 텍스트 추출 가능한 PDF, DOCX, PPTX, Notebook을 지원합니다. 스캔 OCR, 구형 DOC/PPT, 압축 파일 분석은 구현되지 않았습니다. PDF 기본 추출 상한은 8쪽과 10,000자이므로 긴 자료는 일부만 읽을 수 있습니다.

## 검증과 기여

`python -m unittest discover -s tests -v`와 `cs-study-map validate --tracked`를 실행하세요. 오류는 Issue로 보고하고 코드, 매핑, 수동 수정 규칙은 PR로 개선할 수 있습니다. [기여 안내](../../CONTRIBUTING.md)를 참고하세요.

자체 프로그램, 교재 본문, 유지보수 문서는 MIT 라이선스를 따릅니다. 원본 자료의 권리는 바뀌지 않습니다. [출처 및 라이선스](../../ATTRIBUTION.md)를 참고하세요.

초기 성과: [전체 지식 지도와 과목 안내 60개](../early-work/index.md). 분류 개요와 교재 README도 포함하며 학습 내용은 보존하고 로컬 절대 경로를 제거하여 Git에 보관했습니다.
