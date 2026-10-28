# paper-summary 사용 가이드 — Claude에게 이렇게 말하세요

Claude Code에서 자연어로 말하기만 하면, 논문·정책 보고서·웹 자료를 찾고 요약해 쌓아 두었다가 글을 쓸 때 참고문헌까지 자동으로 달아 주는 스킬입니다. 명령어를 외울 필요가 없습니다.

- 저장소: https://github.com/emilyJ7/paper-summary
- 비용: Zotero와 LLM API 키가 필요 없습니다. 서지 정보는 무료 공개 API에서 가져오고, 요약은 Claude가 대화 안에서 직접 씁니다.

## 1. 한눈에 보기

| 하고 싶은 일 | Claude에게 이렇게 말하기 |
|---|---|
| 주제로 논문 조사 | `/paper-summary rPPG 기반 HRV 추정 연구 정리해줘` |
| 논문 한 편 저장·요약 | `이 논문 라이브러리에 추가하고 요약해줘: 10.1038/s41598-026-70292-0` |
| 가진 PDF 정리 | `C:\Downloads\paper.pdf 논문 요약해줘` |
| 정책 자료 조사 | `/paper-summary AI 인재정책 관련 국내외 정책 보고서와 논문 조사해줘` |
| 보고서·보도자료 저장 | `이 보고서 정리해줘: <PDF 경로 또는 URL>` |
| 저장한 논문 찾기 | `라이브러리에서 HRV 관련 논문 찾아줘` |
| 글쓰기 + 인용 | `라이브러리의 HRV 논문들로 연구 배경 써주고 참고문헌 APA로 달아줘` |
| 내 원고에 참고문헌 | `draft.md 참고문헌 IEEE로 달아줘` |

> 팁: 처음에 `/paper-summary`를 붙이면 이 스킬을 확실히 씁니다. 붙이지 않아도 "논문 요약", "참고문헌" 같은 말이 있으면 Claude가 알아서 이 스킬을 고릅니다.

## 2. 설치 (처음 한 번)

Claude Code에 이렇게 말하면 Claude가 설치까지 해 줍니다.

```text
https://github.com/emilyJ7/paper-summary 스킬을 ~/.claude/skills/paper-summary에 설치하고 필요한 파이썬 패키지도 설치해줘
```

설치가 끝나면 Claude Code를 다시 시작하고 이렇게 확인합니다.

```text
paper-summary 스킬로 arXiv 2510.27028 논문 라이브러리에 추가해봐
```

- 주제 검색을 쓰려면 claude.ai → 설정 → 커넥터에서 **SciSpace**를 연결하세요. PubMed, alphaXiv 커넥터도 연결하면 검색 범위가 넓어집니다.
- 커넥터가 없어도 DOI·arXiv 번호·PDF로 논문을 추가하고 요약·인용하는 기능은 그대로 됩니다.

## 3. 주제로 문헌 조사

```text
/paper-summary rPPG 기반 심박·HRV 추정 정확도 연구 정리해줘
/paper-summary 최근 3년 LLM 에이전트 메모리 연구 10편 정도 비교해줘
/paper-summary 노쇠(frailty) 예측 연구, 임상 논문 위주로 찾아줘
```

Claude가 하는 일: 주제를 검색 질문으로 바꿔 SciSpace에서 찾고, 5~10편을 골라 핵심 요약, 비교표, 논문별 메모, 연구 공백, 참고문헌 순서로 정리합니다.

이어서 이렇게 말할 수 있습니다.

```text
여기서 고른 논문들 라이브러리에도 등록해줘
이 결과 한글(hwpx) 문서로 만들어줘
2번하고 5번 논문만 더 자세히 비교해줘
```

> 조건(기간, 대상, 논문 수, 분야)을 함께 말하면 결과가 더 정확합니다.

## 4. 논문 한 편 저장과 요약

```text
이 논문 라이브러리에 추가하고 요약해줘: 10.1038/s41598-026-70292-0
arXiv 2601.09742 요약해서 라이브러리에 넣어줘
C:\Users\me\Desktop\paper.pdf 논문 요약해줘
```

Claude가 하는 일:

1. 서지 정보(제목, 저자, 연도, 학술지, DOI)를 가져옵니다.
2. 본문을 쪽 번호와 함께 저장하고, 그림을 캡션 기준으로 잘라 저장합니다.
3. 본문을 읽고 요약 노트를 씁니다. 모든 사실 문장에 출처와 쪽 번호(`[@Pstras2026estimating, p. 7]`)를 답니다.
4. 브라우저로 볼 수 있는 페이지를 만듭니다.

요약이 끝난 뒤에는 이렇게 말할 수 있습니다.

```text
방금 요약한 논문 HTML로 열어줘
이 논문 그림 1 설명해줘
요약에서 Limitations 부분 더 자세히 써줘
디스크가 부족하니 PDF는 지워줘
```

### 유료 논문 (초록만 있을 때)

```text
이 논문 추가해줘: 10.1016/j.smhl.2026.100683
```

1. 공개 PDF가 없으면 서지 정보와 초록만 저장되고, 목록에 `PDF대기`로 표시됩니다. 요약은 초록 기준의 임시 요약입니다.
2. 도서관이나 출판사에서 PDF를 받으면 이렇게 말합니다.

```text
이 PDF로 정리해줘: C:\Downloads\physqual.pdf
```

3. Claude가 DOI나 제목으로 같은 논문을 찾아 본문과 그림을 채우고, 요약을 본문 기준으로 다시 씁니다.
4. 스캔본처럼 제목을 읽을 수 없는 PDF는 어느 논문인지 알려 주세요.

```text
이 PDF를 Mohamad2026physqual에 붙여줘: C:\Downloads\scan.pdf
PDF 기다리는 논문 목록 보여줘
```

## 5. 정책 자료·보고서·웹 자료

논문뿐 아니라 국책연구기관 보고서, 정부 보도자료, 국제기구 보고서도 같은 방식으로 저장하고 인용할 수 있습니다.

### 정책 주제 조사

```text
/paper-summary AI 인재정책 관련 국내외 정책 보고서와 논문 조사해줘
/paper-summary 탄소중립 R&D 예산 정책, KISTEP·STEPI·OECD 보고서 위주로 찾아줘
최근 2년 과기정통부 AI 관련 보도자료 정리해줘
```

Claude가 하는 일: 학술 논문 검색과 함께 웹 검색으로 국책연구기관(KDI, STEPI, KISTEP, 국회입법조사처 등), 정부 부처·정책브리핑, 국제기구(OECD, World Bank 등) 자료를 찾습니다. 언론 기사나 재게시 페이지는 원문을 찾는 데만 쓰고, 인용은 원 발행 기관 자료로 합니다.

### 보고서·웹페이지 저장

```text
이 보고서 정리해줘: C:\Downloads\stepi_report.pdf
이 보고서 라이브러리에 넣어줘: https://…/report.pdf
이 보도자료 정리해줘: https://www.korea.kr/briefing/…
```

1. PDF는 본문과 그림(「Figure N」, 「<그림 2-1>」 캡션)을 저장하고, 웹페이지는 본문 텍스트와 접속일을 저장합니다.
2. DOI가 없는 보고서는 서지 정보가 비어 있어서, Claude가 표지·판권면을 읽고 발행 기관, 연도, 보고서 번호, URL을 채웁니다.
3. 인용 키는 `STEPI2025인공지능`처럼 기관 약칭, 연도, 핵심어로 붙입니다.
4. 보고서 요약은 정책 배경, 목표, 주요 과제, 추진 체계, 예산, 시사점 중심으로 씁니다.

서지가 틀리면 말로 고칩니다.

```text
STEPI2025인공지능 보고서 번호를 정책연구 2025-07로 고쳐줘
이 보도자료 발행 기관을 과학기술정보통신부로, 게시일을 2025-12-03으로 해줘
인용 키를 KISTEP2025예산으로 바꿔줘
```

### 보고서 인용 결과 예

| 종류 | APA | IEEE |
|---|---|---|
| 보고서 | 과학기술정책연구원. (2025). *인공지능 시대의 과학기술 인재정책 방향* (정책연구 2025-07). | 과학기술정책연구원, "인공지능 시대의 과학기술 인재정책 방향," Rep. 정책연구 2025-07, 2025. |
| 보도자료 | 과학기술정보통신부. (2025, December 3). *2026년도 과기정통부 예산 23.7조원으로 확정*. URL | 과학기술정보통신부, "2026년도 과기정통부 예산…," Dec. 3, 2025. Accessed: …. [Online]. Available: URL |
| DOI 있는 보고서 | Tabassi, E. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. National Institute of Standards and Technology (U.S.). https://doi.org/10.6028/nist.ai.100-1 | E. Tabassi, "Artificial Intelligence Risk Management Framework…," National Institute of Standards and Technology (U.S.), 2023, doi: 10.6028/nist.ai.100-1. |

> 보고서 PDF가 로그인 뒤에 있거나 직접 링크가 없으면 Claude가 내려받아 달라고 요청합니다. 받은 파일 경로를 알려 주면 됩니다.

## 6. 저장한 논문 찾고 보기

```text
라이브러리에 있는 논문 목록 보여줘
라이브러리에서 SDNN 언급한 논문 찾아줘
Sampath2026adaptive 요약 보여줘
라이브러리 목록 페이지 열어줘
아직 요약 안 한 논문 요약해줘
```

> 라이브러리는 `~/paper-library`에 있습니다. 논문마다 폴더가 하나씩 있고, 폴더 이름이 인용 키입니다(예: `Sampath2026adaptive`).

## 7. 글쓰기와 자동 인용

### Claude에게 글을 맡길 때

```text
라이브러리의 HRV 논문들로 연구 배경 한 단락 써주고 참고문헌 APA로 달아줘
Sampath2026adaptive 내용을 인용해서 MCP 에이전트 설계 시사점 정리해줘
요약한 rPPG 논문들로 선행연구 표 만들고 IEEE 참고문헌 붙여줘
```

Claude는 요약 노트를 재료로 글을 쓰고, 인용 표시를 그대로 옮긴 뒤 본문 인용과 참고문헌 목록을 자동으로 만듭니다. 원고(인용 키 상태)와 완성본(`_cited.md`)이 함께 저장됩니다.

### 내가 쓴 원고에 참고문헌만 달 때

원고에 인용하고 싶은 자리마다 인용 키를 적어 두고 Claude에게 맡깁니다.

```markdown
도구가 많아지면 단일 에이전트는 선택이 흐려진다[@Sampath2026adaptive, p. 2].
HRV는 카메라로도 추정할 수 있다[@Pstras2026estimating; @Rouast2025vitallens].
```

```text
draft.md 참고문헌 APA로 달아줘
draft.md IEEE 형식으로 바꿔줘
draft.md 참고문헌을 한글 문서용 표로 만들어줘
```

인용 키를 모르면 이렇게 물어봅니다.

```text
SDNN 정확도 다룬 논문 인용 키 알려줘
이 문장에 맞는 출처 라이브러리에서 찾아서 인용 달아줘: "얼굴 영상으로 HRV를 추정할 수 있다"
```

### 결과 형식

| 원고에 적힌 인용 | APA로 달면 | IEEE로 달면 |
|---|---|---|
| `[@Pstras2026estimating]` | (Pstras et al., 2026) | [1] |
| `[@Pstras2026estimating, p. 7]` | (Pstras et al., 2026, p. 7) | [1, p. 7] |
| `[@Pstras2026estimating; @Rouast2025vitallens]` | (Pstras et al., 2026; Rouast, 2025) | [1, 2] |

- APA는 참고문헌을 저자 알파벳순으로, IEEE는 본문에 처음 나온 순서대로 번호를 매깁니다.
- 라이브러리에 없는 논문을 인용하면 `??키`로 표시되고, Claude가 그 논문을 추가할지 묻습니다.
- 최종 문서는 `Word로 만들어줘`, `PDF로 만들어줘`, `한글(hwpx)로 만들어줘`라고 하면 됩니다. LaTeX를 쓰면 `~/paper-library/library.bib`를 그대로 씁니다.

## 8. 잘 쓰는 요령

- **조건을 구체적으로**: "최근 5년", "임상 연구만", "10편", "한국어로" 같은 조건을 붙이면 결과가 좋아집니다.
- **숫자는 출처 확인**: Claude는 출처에 있는 수치만 쓰고 쪽 번호를 답니다. 중요한 수치는 "이 수치 원문 몇 쪽인지 보여줘"로 확인하세요.
- **요약은 다시 쓸 수 있음**: "요약을 실무자 관점으로 다시 써줘", "How 부분 수식 포함해서 자세히"처럼 요청하면 요약 노트를 고쳐 줍니다.
- **원고는 인용 키 상태로 관리**: 글을 고칠 때는 원고를 고치고 "참고문헌 다시 달아줘"라고 하면 번호가 자동으로 다시 매겨집니다.

## 9. 자주 묻는 질문

**Q. API 비용이 드나요?**
아니요. 무료 공개 API만 쓰고, 요약은 Claude Code 대화 안에서 이루어집니다. Claude Code 사용량은 평소처럼 쓰입니다.

**Q. 그림이 안 나오거나 잘못 잘렸어요.**
"이 논문 그림 다시 확인해줘"라고 하세요. 그림 추출은 캡션 기준이라 레이아웃이 특이한 PDF에서는 놓칠 수 있고, Claude가 요약할 때 잘못된 그림은 뺍니다.

**Q. 라이브러리를 다른 컴퓨터로 옮기려면?**
`paper-library` 폴더를 통째로 복사하면 됩니다. PDF와 본문이 들어 있으니 공개 저장소에는 올리지 마세요.

**Q. 스킬을 최신 버전으로 받으려면?**
`paper-summary 스킬 최신 버전으로 업데이트해줘`라고 말하면 됩니다.

## 부록. 직접 실행할 때의 명령

평소에는 필요 없습니다. Claude가 아래 명령을 대신 실행합니다.

| 명령 | 설명 |
|---|---|
| `paperlib.py add <DOI·arXiv·PDF·웹 URL> [--no-pdf] [--key <키>]` | 논문·보고서·웹페이지 등록, 받은 PDF 붙이기 |
| `paperlib.py set <키> 필드=값 …` | 서지 보완 (authors, year, publisher, number, url, date, type 등) |
| `paperlib.py rename <키> <새 키>` | 인용 키 바꾸기 |
| `paperlib.py list [--pending]` | 목록 (`--pending`: PDF 대기만) |
| `paperlib.py search <단어...>` | 제목·초록·요약·본문 검색 |
| `paperlib.py cite <원고.md> [--style apa\|ieee] [--table]` | 인용 키 → 본문 인용 + 참고문헌 |
| `paperlib.py render [키]` | 요약 노트 → HTML |

실행 위치: Windows PowerShell은 `python "$HOME\.claude\skills\paper-summary\scripts\paperlib.py" <명령>`, macOS·Linux는 `python3 ~/.claude/skills/paper-summary/scripts/paperlib.py <명령>`
