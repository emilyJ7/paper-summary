---
name: paper-summary
description: '논문을 찾아 요약하고, 로컬 논문 라이브러리(~/paper-library)에 서지 정보·본문·그림을 저장해 두었다가, 글을 쓸 때 [@citekey]로 인용하면 참고문헌을 자동으로 달아준다. Zotero·LLM API 비용 없이 동작(서지는 Crossref·arXiv·OpenAlex 무료 API, 요약은 Claude가 직접 작성). 검색은 SciSpace 커넥터(search-papers, add-column)와 PubMed·alphaXiv·bioRxiv로 보강. "논문 찾아서 요약해줘", "선행연구 조사", "문헌 리뷰", "이 논문 라이브러리에 추가/정리해줘", "요약한 논문들로 글 써줘·인용 달아줘", "참고문헌 자동으로" 등에 사용.'
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
3. 참고문헌 생성: `cite 원고.md [-o 결과.md] [--style apa|ieee] [--table] [--heading 참고문헌]`
   - APA는 본문에 (Pstras et al., 2026, p. 7) 형식, 참고문헌은 알파벳순이다.
   - IEEE는 등장 순서대로 [1], [1, p. 7] 형식이다.
   - `--table`은 한글(hwpx) 문서용 참고문헌 표(번호/저자(연도)/논문·출처/DOI)를 만든다. 결과 md를 `hwpx-template` 스킬(설치돼 있을 때)로 넘기면 된다.
   - 결과의 `missing`에 키가 있으면(본문에 `??키`로 표시됨) 그 논문을 `add` 하거나 키 오타를 고친다.
4. 원본 원고(인용 키 상태)는 그대로 두고 `_cited.md`를 따로 만든다. 다시 고칠 때는 원본을 고치고 cite를 다시 실행한다.

## 유의

- 요약·종합은 이 대화에서 Claude가 직접 하므로 별도 LLM API 비용이 없다. 스크립트는 무료 공개 API만 부른다.
- 사용자 이메일 등 개인정보는 외부 API 요청에 넣지 않는다.
- 유료 논문 PDF를 우회해서 받으려 하지 않는다. 사용자가 가진 PDF 경로를 받아서 처리한다.
