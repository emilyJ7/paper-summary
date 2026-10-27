# paper-summary 사용 가이드

Claude Code에서 논문을 찾고, 요약을 로컬 라이브러리에 쌓아 두었다가, 글을 쓸 때 인용하면 참고문헌이 자동으로 달리게 하는 스킬입니다.

- 저장소: https://github.com/emilyJ7/paper-summary
- 비용: Zotero와 LLM API 키가 필요 없습니다. 서지 정보는 무료 공개 API(Crossref, arXiv, OpenAlex)에서 가져오고, 요약은 Claude Code 대화 안에서 Claude가 직접 씁니다.

## 1. 한눈에 보기

| 단계 | 하는 일 | Claude에게 이렇게 말하기 |
|---|---|---|
| ① 조사 | 주제로 논문 검색·선별·종합 | `/paper-summary rPPG 기반 HRV 추정 연구 정리해줘` |
| ② 저장 | 논문 한 편의 서지·본문·그림 저장 + 요약 노트 | `이 논문 라이브러리에 추가하고 요약해줘: 10.1038/s41598-026-70292-0` |
| ③ 집필 | 라이브러리 내용으로 글을 쓰고 참고문헌 자동 생성 | `라이브러리의 HRV 논문들로 서론 써주고 참고문헌 APA로 달아줘` |

## 2. 설치

필요한 것: Claude Code, Python 3.9 이상, git

### Windows (PowerShell)

```powershell
git clone https://github.com/emilyJ7/paper-summary.git "$HOME\.claude\skills\paper-summary"
python -m pip install -r "$HOME\.claude\skills\paper-summary\requirements.txt"
```

### macOS / Linux

```bash
git clone https://github.com/emilyJ7/paper-summary.git ~/.claude/skills/paper-summary
python3 -m pip install -r ~/.claude/skills/paper-summary/requirements.txt
```

### 설치 확인

```bash
python ~/.claude/skills/paper-summary/scripts/paperlib.py add 2510.27028
```

- `~/paper-library/papers/Rouast2025vitallens/` 폴더가 생기면 성공입니다.
- Claude Code를 다시 시작하면 스킬 목록에 `paper-summary`가 보입니다.

### (선택) SciSpace 검색 연결

- 주제 검색(①)에는 claude.ai의 SciSpace 커넥터를 씁니다. claude.ai → 설정 → 커넥터에서 각자 자기 계정에 연결하세요.
- PubMed, alphaXiv, bioRxiv 커넥터도 연결하면 검색 범위가 넓어집니다.
- 커넥터가 없어도 DOI·arXiv 번호·PDF로 논문을 추가하는 ②와 집필하는 ③은 그대로 쓸 수 있습니다.

## 3. 사용법 ① — 주제로 문헌 조사

1. `/paper-summary <주제>`로 요청합니다. 기간, 대상, 논문 수 같은 조건이 있으면 함께 말합니다.
2. Claude가 주제를 영어 검색 질문으로 바꿔 SciSpace에서 찾고, 5~10편을 고릅니다.
3. 필요하면 의학은 PubMed, 공학은 alphaXiv로 보강 검색을 합니다.
4. 결과는 핵심 요약, 비교표, 논문별 메모, 연구 공백, 참고문헌 순서로 정리됩니다.
5. "라이브러리에도 등록해줘"라고 하면 고른 논문을 ② 방식으로 저장합니다.

> 팁: 결과를 한글(hwpx)로 받으려면 `hwpx-template` 스킬이 설치되어 있어야 합니다. Word·PDF가 필요하면 그렇게 요청하면 됩니다.

## 4. 사용법 ② — 논문 저장과 요약 노트

입력할 수 있는 것: DOI, arXiv 번호나 URL, PDF 파일 경로, PDF URL

```text
이 논문 라이브러리에 추가하고 요약해줘: 2510.27028
C:\Downloads\paper.pdf 라이브러리에 넣고 요약해줘
```

Claude가 하는 일:

1. 서지 정보(제목, 저자, 연도, 학술지, DOI)를 무료 API에서 가져옵니다.
2. 공개 PDF가 있으면 내려받아 쪽 번호가 표시된 본문(`text.md`)을 만듭니다.
3. 「Figure N」 캡션을 기준으로 그림을 잘라 `figures/`에 저장합니다.
4. 본문을 읽고 요약 노트(`summary.md`)를 씁니다. 섹션은 Essence, Motivation, How, Achievement, Limitations, 메모 순서입니다.
5. 요약 노트의 모든 사실 문장에는 출처 키와 쪽 번호를 답니다. 예: `[@Pstras2026estimating, p. 7]`
6. 보기용 HTML 페이지(`index.html`)를 만듭니다.

유의할 점:

- 유료 논문은 공개 PDF가 없으면 서지 정보만 등록됩니다. 직접 받은 PDF의 경로를 주면 본문과 그림을 추출합니다.
- 디스크가 부족하면 "PDF는 지워줘"라고 하세요. `--no-pdf` 옵션으로 추출만 하고 PDF는 남기지 않습니다.

## 5. 사용법 ③ — 글쓰기와 자동 인용

```text
라이브러리의 HRV 논문들로 연구 배경 한 단락 써주고 참고문헌 IEEE로 달아줘
```

1. Claude가 라이브러리를 검색하고, 관련 논문의 요약 노트와 본문을 읽습니다.
2. 원고에는 인용 키를 그대로 씁니다. 예: `[@Pstras2026estimating, p. 7]`
3. `cite` 명령이 키를 본문 인용으로 바꾸고, 원고 끝에 참고문헌 목록을 붙입니다.

### 인용 표기 규칙

| 원고에 쓰는 형식 | APA 결과 | IEEE 결과 |
|---|---|---|
| `[@Pstras2026estimating]` | (Pstras et al., 2026) | [1] |
| `[@Pstras2026estimating, p. 7]` | (Pstras et al., 2026, p. 7) | [1, p. 7] |
| `[@Pstras2026estimating; @Rouast2025vitallens]` | (Pstras et al., 2026; Rouast, 2025) | [1, 2] |

- APA는 참고문헌을 저자 알파벳순으로, IEEE는 본문에 처음 나온 순서대로 번호를 매깁니다.
- 라이브러리에 없는 키는 `??키`로 표시됩니다. 그 논문을 추가하거나 키 오타를 고치면 됩니다.
- 원고 원본은 그대로 두고 `원고_cited.md`를 새로 만듭니다. 고칠 때는 원본을 고친 뒤 다시 실행합니다.
- `--table` 옵션을 쓰면 한글 문서용 참고문헌 표(번호, 저자(연도), 논문·출처, DOI)를 만듭니다.

## 6. 명령어 정리 (직접 실행할 때)

평소에는 Claude에게 말로 시키면 되고, 아래 명령을 직접 실행할 필요는 없습니다.

| 명령 | 설명 |
|---|---|
| `paperlib.py add <입력> [--no-pdf]` | 논문 등록, 본문·그림 추출 |
| `paperlib.py list` | 라이브러리 목록 |
| `paperlib.py search <단어...>` | 제목·초록·요약·본문 검색 |
| `paperlib.py show <citekey>` | 서지 정보와 파일 목록 |
| `paperlib.py cite <원고.md> [--style apa\|ieee] [--table] [-o 결과.md]` | 인용 키를 본문 인용으로 바꾸고 참고문헌 생성 |
| `paperlib.py render [citekey]` | 요약 노트를 HTML로 만들기 |
| `paperlib.py rebuild` | `library.json`·`library.bib` 다시 만들기 |

실행 위치: `python ~/.claude/skills/paper-summary/scripts/paperlib.py <명령>` (macOS·Linux는 `python3`)

## 7. 라이브러리 구조

라이브러리 위치는 기본값이 `~/paper-library`이고, 환경 변수 `PAPER_LIB`로 바꿀 수 있습니다.

```text
paper-library/
  index.html      라이브러리 목록 페이지
  library.json    목록 데이터
  library.bib     BibTeX (LaTeX·다른 도구에서 그대로 사용 가능)
  papers/<citekey>/
    meta.json     서지 정보
    paper.pdf     원문 (--no-pdf면 없음)
    text.md       <!-- page N --> 쪽 표시가 달린 본문
    figures/      fig1.jpg …  + figures.json (번호·쪽·캡션)
    summary.md    요약 노트 (문장마다 [@키, p. N])
    index.html    보기용 페이지
```

- citekey는 `제1저자 성 + 연도 + 제목 첫 단어` 형식입니다. 예: `Pstras2026estimating`
- 같은 DOI나 arXiv 번호를 다시 추가하면 새로 만들지 않고 기존 폴더를 갱신합니다.

## 8. 자주 묻는 질문

**Q. API 비용이 드나요?**
아니요. 스크립트는 키가 필요 없는 무료 공개 API만 부르고, 요약은 Claude Code 대화 안에서 이루어집니다. 다만 Claude Code 자체의 사용량은 평소처럼 쓰입니다.

**Q. 그림이 안 나오거나 잘못 잘렸어요.**
그림 추출은 「Figure N:」「Fig. N」 캡션을 기준으로 합니다. 레이아웃이 특이한 PDF에서는 일부 그림을 놓칠 수 있습니다. Claude가 요약할 때 그림을 확인하고 잘못된 그림은 요약에서 뺍니다.

**Q. 라이브러리를 다른 컴퓨터로 옮기거나 공유할 수 있나요?**
`paper-library` 폴더를 통째로 복사하면 됩니다. 다만 PDF와 본문이 들어 있으니 공개 저장소에는 올리지 마세요.

**Q. 스킬을 최신 버전으로 받으려면?**
`git -C ~/.claude/skills/paper-summary pull`

**Q. LaTeX로 쓰는데 쓸 수 있나요?**
`library.bib`를 그대로 쓰면 됩니다. citekey가 같아서 `\cite{Pstras2026estimating}`로 인용할 수 있습니다.
