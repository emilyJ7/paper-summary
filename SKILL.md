---
name: paper-summary
description: '논문·정책 보고서·웹 자료를 찾아 요약하고, 로컬 논문 라이브러리(~/paper-library)에 서지 정보·본문·그림을 저장해 두었다가, 글을 쓸 때 [@citekey]로 인용하면 참고문헌을 자동으로 달아준다. Zotero·LLM API 비용 없이 동작(서지는 Crossref·arXiv·OpenAlex 무료 API, 요약은 Claude가 직접 작성). 검색은 SciSpace 커넥터(search-papers, add-column)와 PubMed·alphaXiv·bioRxiv로 보강. "논문 찾아서 요약해줘", "선행연구 조사", "문헌 리뷰", "이 논문 라이브러리에 추가/정리해줘", "요약한 논문들로 글 써줘·인용 달아줘", "참고문헌 자동으로", "정책 자료 조사", "보고서 요약", "국책연구기관·정부 보고서", "보도자료 정리" 등에 사용.'
---

# 논문 조사·요약·인용 (로컬 라이브러리)

도구: `python -X utf8 ~/.claude/skills/paper-summary/scripts/paperlib.py <명령>` (macOS·Linux는 `python3`; PyMuPDF, requests, markdown 필요 — 없으면 `pip install -r ~/.claude/skills/paper-summary/requirements.txt`). 라이브러리 위치는 환경 변수 `PAPER_LIB`, 없으면 `~/paper-library`.

```
paper-library/
  library.json  library.bib  index.html        ← 자동 생성(rebuild/render)
  papers/<citekey>/
    meta.json  paper.pdf  text.md(<!-- page N -->)  figures/figN.jpg  figures.json
    summary.md  index.html
```

## A. 주제로 문헌 조사 (검색 → 선별 → 종합)

1. **질문 만들기**: 주제를 영어 자연어 질문 1~3개로 바꾼다(키워드 나열 금지). 범위가 모호하면 기본값(최근 5년, 성인 등)으로 진행하고 가정을 적는다.
2. **검색**: SciSpace 커넥터의 `search-papers`(ToolSearch로 `search-papers`/`add-column`을 찾아 로드)를 질문마다 호출해 DOI 기준으로 합친다. 커넥터가 없거나 `needs_auth`이면 claude.ai 설정 → 커넥터에서 다시 연결하라고 안내한다.
3. **선별**: 관련성, 최신성, 동료 심사 여부, 인용 수, 초록의 수치를 보고 5~10편을 고른다. 필요하면 `add-column`(unique_id와 원래 검색어 그대로)으로 `limitations`, `dataset` 등을 뽑는다. 다만 이 값은 초록에 근거해 빈약할 수 있다.
4. **보강(선택)**: 의학은 PubMed, CS·물리는 alphaXiv, 생명과학 프리프린트는 bioRxiv로 1회 더 검색한다.
   - **정책·제도 주제**(정책, 규제, 예산, 제도, 거버넌스 등)는 반드시 D의 웹 검색으로 정부·국책연구기관·국제기구 보고서를 함께 찾는다.
5. **라이브러리 등록**: 고른 논문을 `add <DOI 또는 arXiv ID>`로 등록한다(B 참고). 사용자가 "가볍게"를 원하면 생략하고 초록만으로 정리한다.
6. **종합 원고**: 각 주장 뒤에 `[@citekey]` 또는 `[@citekey, p. N]`을 단 Markdown으로 쓰고, `cite`로 참고문헌을 붙인다(C 참고). 숫자는 출처에 있는 값만 쓴다.

## B. 논문 한 편을 라이브러리에 추가하고 요약

1. `add <입력>` — 입력은 DOI, arXiv ID·URL, 로컬 PDF 경로, PDF URL 중 하나.
   - 서지는 Crossref(DOI), arXiv API, OpenAlex(공개 PDF 위치)에서 받는다. 모두 무료이고 키가 필요 없다. PDF만 있으면 첫 2쪽에서 DOI·arXiv ID를 찾고, 없으면 제목으로 Crossref를 검색한다.
   - 공개 PDF가 있으면 내려받아 `text.md`(쪽 표시 포함)와 `figures/`(Figure N 캡션 위 그래픽을 잘라 JPG로)를 만든다.
   - **유료 논문**은 서지·초록만 저장되고 `list`에 `PDF대기`로 표시된다(`list --pending`으로 모아 보기). 이때 초록 기반의 임시 요약만 쓰고 "PDF를 받으면 본문 기준으로 다시 정리함"이라고 적는다. 사용자에게 PDF를 받아 달라고 안내한다.
   - **PDF를 받으면** `add <PDF 경로>`를 실행한다. PDF의 DOI·arXiv 번호, 없으면 제목으로 기존 항목을 찾아 같은 폴더에 본문·그림을 채우고, 기존 서지(Crossref 등)는 유지한다. 제목도 못 읽는 PDF(스캔본 등)는 `add <PDF 경로> --key <citekey>`로 직접 붙인다. 그다음 summary.md를 본문 기준으로 다시 쓴다(쪽 번호 인용 포함).
   - 같은 DOI·arXiv는 같은 폴더를 갱신한다. citekey는 `제1저자성+연도+제목첫단어` 형식이다(예: `Pstras2026estimating`).
   - **디스크가 빠듯하면** `--no-pdf`로 추출 후 PDF를 지운다.
2. **그림 확인**: `figures.json`의 그림을 Read로 몇 장 열어 잘림이나 엉뚱한 영역이 없는지 본다. 잘못된 그림은 요약에 넣지 않는다.
3. **summary.md 작성**: `text.md`를 읽고 Claude가 직접 쓴다. 섹션은 Essence → Motivation(Known/Gap) → How → Achievement → Limitations → 메모 순서다.
   - **모든 사실 문장 끝에 `[@citekey, p. N]`**을 단다. 쪽은 `text.md`의 `<!-- page N -->` 기준이고, 나중에 다른 글로 옮겨도 인용이 따라간다.
   - 그림은 `![Figure N](figures/figN.jpg)` 다음 줄에 `*Fig. N — 한국어 캡션 (p. N)*` 형식으로 넣는다. 핵심 그림 2~3장만 넣는다.
   - 수치는 본문 표 값을 우선하고, 초록과 다르면 메모에 적는다.
   - 저자가 밝힌 한계와 Claude의 해석을 구분해서 쓴다.
4. `render <citekey>` → `papers/<citekey>/index.html`과 라이브러리 목록 `index.html`을 만든다.

## C. 글을 쓸 때 자동 인용

1. 라이브러리에서 재료를 찾는다: `list`, `search <단어...>`(제목·초록·summary·본문 검색), `show <citekey>`.
2. 관련 `summary.md`와 `text.md`를 읽고 원고를 쓴다. **인용은 반드시 `[@citekey]`·`[@citekey, p. N]`·`[@a; @b]` 형식**으로 쓰고, 번호나 저자명을 손으로 쓰지 않는다. summary의 문장을 옮기면 그 문장의 인용 표시도 함께 옮긴다.
3. 참고문헌 생성: `cite 원고.md [-o 결과.md] [--style ieee|apa] [--table] [--heading 참고문헌]`
   - **기본은 IEEE 번호식**이다(이 팀의 표준: 본문 `[1]`, 끝에 번호순 참고문헌). 사용자가 형식을 말하지 않으면 IEEE로 한다.
   - APA는 사용자가 요청할 때만 쓴다. 본문 (Pstras et al., 2026, p. 7), 참고문헌은 알파벳순이다.
   - IEEE는 등장 순서대로 [1], [1, p. 7] 형식이다.
   - `--table`은 한글(hwpx) 문서용 참고문헌 표(번호/저자(연도)/논문·출처/DOI)를 만든다. 결과 md를 `hwpx-template` 스킬(설치돼 있을 때)로 넘기면 된다.
   - 결과의 `missing`에 키가 있으면(본문에 `??키`로 표시됨) 그 논문을 `add` 하거나 키 오타를 고친다.
4. 원본 원고(인용 키 상태)는 그대로 두고 `_cited.md`를 따로 만든다. 다시 고칠 때는 원본을 고치고 cite를 다시 실행한다.

## D. 정책 자료·보고서 (회색 문헌)

정책 주제는 학술 DB만으로 부족하다. A의 학술 검색과 함께 아래를 한다.

1. **웹 검색**: WebSearch(없으면 ToolSearch로 `WebSearch`·`WebFetch` 로드)로 한국어·영어 질의를 2~4개 낸다. 우선할 출처는 다음과 같다.
   - 국책연구기관·싱크탱크: KDI, STEPI, KISTEP, KISDI, KIET, KEI, 국회입법조사처(NARS), 국회예산정책처(NABO)
   - 정부: 부처 누리집, korea.kr 정책브리핑(보도자료), 법령정보센터
   - 국제기구: OECD, World Bank, IMF, UN, EU, WEF
   - 언론·블로그·재게시 사이트는 원문을 찾는 실마리로만 쓰고, 인용은 가능한 한 원 발행처 자료로 한다.
2. **원문 확보**: 보고서 PDF의 직접 링크가 있으면 `add <PDF URL>`, 정책 페이지·보도자료는 `add <페이지 URL>`(본문 텍스트와 접속일 저장), 사용자가 받은 파일은 `add <PDF 경로>`. 직접 링크가 없거나 로그인이 필요하면 사용자에게 내려받아 달라고 한다. 우회하지 않는다.
3. **서지 보완**: DOI 없는 보고서·웹페이지는 서지가 비어 있다(add 결과의 note). `text.md` 앞부분(표지·판권면·발간등록번호)을 읽고 `set`으로 채운다.
   - `set <키> authors="과학기술정책연구원" year=2025 publisher="과학기술정책연구원" number="정책연구 2025-07" url=… short=STEPI`
   - 기관 저자·한글 이름은 그대로(literal) 저장되고, 여러 명은 `;`로 구분한다. 개인 영문 이름은 `Smith, John` 형식이다.
   - 웹페이지는 게시일을 `date=2025-12-03`으로 넣는다. 게시일이 없으면 접속일로 인용된다.
   - 재게시 페이지면 원 발행 기관을 authors로, 실제 출처 URL을 url로 둔다.
4. **인용 키 정리**: `Anonnd…`처럼 의미 없는 키는 `rename <키> STEPI2025인공지능`처럼 `기관약칭+연도+핵심어`로 바꾼다(요약 노트 안의 키도 함께 바뀜). 새 항목을 처음부터 원하는 키로 만들려면 `add <입력> --key <새키>`.
5. **요약**: B-3과 같은 형식이되, 보고서는 How 대신 "정책 내용(배경·목표·주요 과제·추진 체계·예산)"과 "시사점"을 쓴다. 쪽 번호 인용은 그대로 단다(웹페이지는 쪽 없이 `[@키]`).
6. **인용 형식**: `cite`가 종류에 맞게 만든다. APA 보고서는 「기관. (연도). *제목* (보고서 번호). 발행처. URL」, 웹페이지는 「기관. (연도, Month Day). *제목*. URL」(게시일 없으면 Retrieved 접속일), IEEE 보고서는 「기관, "제목," 발행처, Rep. 번호, 연도.」

## E. 관리 요청

- "스킬 설치해줘" → `git clone https://github.com/emilyJ7/paper-summary.git ~/.claude/skills/paper-summary` 후 `pip install -r requirements.txt`, Claude Code 재시작 안내
- "스킬 최신 버전으로 업데이트해줘" → `git -C ~/.claude/skills/paper-summary pull` 후 `pip install -r requirements.txt`, 바뀐 내용 요약
- "라이브러리 목록 페이지 열어줘", "요약 HTML로 열어줘" → `render` 후 해당 `index.html`을 링크로 알려 준다.
- "PDF 기다리는 논문 목록" → `list --pending`
- "아직 요약 안 한 논문 요약해줘" → `list`에서 `요약X`인 항목을 B-3 방식으로 요약
- 원고 인용에서 `missing` 키가 나오면 그 논문을 라이브러리에 추가할지 사용자에게 묻는다.
- "이 문장에 맞는 출처 찾아서 인용 달아줘" → `search`와 summary.md에서 근거를 찾아 쪽 번호와 함께 `[@키, p. N]`을 단다. 근거가 없으면 없다고 말한다.

## 유의

- 요약·종합은 이 대화에서 Claude가 직접 하므로 별도 LLM API 비용이 없다. 스크립트는 무료 공개 API만 부른다.
- 사용자 이메일 등 개인정보는 외부 API 요청에 넣지 않는다.
- 유료 논문 PDF를 우회해서 받으려 하지 않는다. 사용자가 가진 PDF 경로를 받아서 처리한다.
