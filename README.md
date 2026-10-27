# paper-summary — Claude Code 논문 요약·인용 스킬

Claude Code에서 논문을 찾고 요약해 **로컬 논문 라이브러리**에 쌓아 두었다가, 글을 쓸 때 `[@citekey]`로 인용하면 **참고문헌을 자동으로 달아 주는** 스킬입니다.

- Zotero 없이 동작하고 LLM API 키도 필요 없습니다.
  - 서지 정보는 무료 공개 API(Crossref, arXiv, OpenAlex)에서 가져옵니다.
  - 요약은 Claude Code 대화 안에서 Claude가 직접 씁니다.
- 논문마다 서지 정보, 쪽 표시가 달린 본문, 캡션 기준으로 잘라낸 그림, 요약 노트, HTML 보기를 저장합니다.
- 인용 형식은 APA와 IEEE를 지원하고, 한글(hwpx) 문서용 참고문헌 표도 만들 수 있습니다.

## 설치

필요한 것: [Claude Code](https://claude.com/claude-code), Python 3.9 이상, git

**가장 쉬운 방법 — Claude에게 맡기기.** Claude Code에서 이렇게 말하면 아래 명령을 대신 실행합니다.
```text
https://github.com/emilyJ7/paper-summary 스킬을 ~/.claude/skills/paper-summary에 설치하고 필요한 파이썬 패키지도 설치해줘
```

직접 설치하려면:

**Windows (PowerShell)**
```powershell
git clone https://github.com/emilyJ7/paper-summary.git "$HOME\.claude\skills\paper-summary"
python -m pip install -r "$HOME\.claude\skills\paper-summary\requirements.txt"
```

**macOS / Linux**
```bash
git clone https://github.com/emilyJ7/paper-summary.git ~/.claude/skills/paper-summary
python3 -m pip install -r ~/.claude/skills/paper-summary/requirements.txt
```

설치 확인(논문 한 편을 시험 등록):
```powershell
# Windows (PowerShell)
python "$HOME\.claude\skills\paper-summary\scripts\paperlib.py" add 2510.27028
```
```bash
# macOS / Linux
python3 ~/.claude/skills/paper-summary/scripts/paperlib.py add 2510.27028
```
`~/paper-library/papers/Rouast2025vitallens/`에 `meta.json`, `text.md`, `figures/`가 생기면 성공입니다. Claude Code를 다시 시작하면 스킬 목록에 `paper-summary`가 보입니다.

업데이트 (또는 Claude에게 "paper-summary 스킬 최신 버전으로 업데이트해줘"):
```powershell
# Windows (PowerShell)
git -C "$HOME\.claude\skills\paper-summary" pull
```
```bash
# macOS / Linux
git -C ~/.claude/skills/paper-summary pull
```

### (선택) SciSpace 검색 연결

주제로 논문을 검색하는 기능은 claude.ai의 **SciSpace 커넥터**를 씁니다. 각자 자기 계정에서 연결해야 합니다.
claude.ai → 설정 → 커넥터 → SciSpace 연결. PubMed, alphaXiv, bioRxiv 커넥터도 연결하면 검색을 보강합니다.
커넥터가 없어도 DOI, arXiv 번호, PDF로 논문을 추가하고 요약·인용하는 기능은 그대로 쓸 수 있습니다.

## 사용법 — Claude에게 이렇게 말하세요

명령어를 외울 필요가 없습니다. Claude Code에서 아래처럼 말하면 Claude가 알아서 실행합니다. 자세한 내용은 [사용 가이드](docs/paper-summary_사용가이드.md)(Word·PDF·PPT 버전도 `docs/`에 있음)를 보세요.

| 하고 싶은 일 | Claude에게 이렇게 말하기 |
|---|---|
| 설치 | `https://github.com/emilyJ7/paper-summary 스킬 설치하고 패키지도 설치해줘` |
| 주제로 논문 조사 | `/paper-summary rPPG 기반 HRV 추정 연구 정리해줘` |
| 논문 저장·요약 | `이 논문 라이브러리에 추가하고 요약해줘: 10.1038/s41598-026-70292-0` |
| 가진 PDF 정리 | `Downloads 폴더의 paper.pdf 논문 요약해줘` |
| 유료 논문 PDF 붙이기 | `이 PDF로 정리해줘: <PDF 경로>` |
| 저장한 논문 찾기 | `라이브러리에서 SDNN 언급한 논문 찾아줘` |
| 글쓰기 + 인용 | `라이브러리의 HRV 논문들로 연구 배경 써주고 참고문헌 APA로 달아줘` |
| 내 원고에 참고문헌 | `draft.md 참고문헌 IEEE로 달아줘` |
| 출처 찾아 인용 | `이 문장에 맞는 출처 찾아서 인용 달아줘: "…"` |
| 업데이트 | `paper-summary 스킬 최신 버전으로 업데이트해줘` |

## 명령어 (직접 실행할 때, 참고)

```bash
P="python ~/.claude/skills/paper-summary/scripts/paperlib.py"
$P add <DOI | arXiv ID/URL | PDF 경로 | PDF URL> [--no-pdf]   # 등록(+본문·그림 추출)
$P add <받은 PDF 경로> [--key <citekey>]                         # 유료 논문: 나중에 받은 PDF를 기존 항목에 붙이기
$P list [--pending]                                             # 목록 (--pending: PDF 대기만)
$P search HRV ECG                                               # 제목·초록·요약·본문 검색
$P show Pstras2026estimating                                    # 서지·파일 보기
$P cite 원고.md --style apa|ieee [--table] [-o 결과.md]          # [@키] → 본문 인용 + 참고문헌
$P render [citekey]                                             # summary.md → index.html
$P rebuild                                                      # library.json·library.bib 재생성
```

원고에는 `[@Pstras2026estimating]`, `[@Pstras2026estimating, p. 7]`, `[@키1; @키2]` 형식으로 인용합니다.
`cite`는 원본은 그대로 두고 `원고_cited.md`를 새로 만듭니다. 라이브러리에 없는 키는 `??키`로 표시합니다.

## 라이브러리 구조

위치는 환경 변수 `PAPER_LIB`로 바꿀 수 있고, 기본값은 `~/paper-library`입니다.

```
paper-library/
  library.json  library.bib  index.html
  papers/<citekey>/
    meta.json        서지 정보
    paper.pdf        원문 (--no-pdf면 추출 후 삭제)
    text.md          <!-- page N --> 쪽 표시가 달린 본문
    figures/         fig1.jpg …  + figures.json(번호·쪽·캡션)
    summary.md       요약 노트 (문장마다 [@키, p. N])
    index.html       보기용 페이지
```

## 유의

- 라이브러리(PDF·본문·그림)는 이 저장소에 포함되지 않습니다. 저작권 문제가 있으니 공개 저장소에 올리지 마세요.
- 유료 논문은 공개 PDF가 없으면 서지·초록만 등록되고 목록에 `PDF대기`로 표시됩니다. 직접 받은 PDF로 `add <PDF 경로>` 하면 DOI나 제목으로 같은 항목을 찾아 본문과 그림을 채웁니다. 제목을 못 읽는 스캔본은 `--key <citekey>`로 지정하세요.
- 그림 추출은 「Figure N:」「Fig. N」 캡션을 기준으로 합니다. 레이아웃이 특이한 PDF에서는 일부 그림을 놓치거나 범위가 어긋날 수 있습니다.
- 한글(hwpx) 문서로 내보내려면 별도의 `hwpx-template` 스킬이 필요합니다.

## 라이선스

MIT
