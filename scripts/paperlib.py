"""paperlib — 로컬 논문 라이브러리 (Zotero·LLM API 없이 동작).

논문 하나 = 라이브러리의 폴더 하나(papers/<citekey>/):
  meta.json     서지 정보 (Crossref·arXiv·OpenAlex, 모두 무료·키 불필요)
  paper.pdf     원문 PDF (--no-pdf 이면 추출 후 삭제)
  text.md       쪽 표시(<!-- page N -->)가 달린 본문
  figures/      fig1.jpg ... (캡션 기준으로 잘라낸 그림)
  figures.json  그림 번호·쪽·캡션·파일
  summary.md    요약 노트 (Claude가 작성, 주장마다 [@citekey, p. N])
라이브러리 루트에는 library.json(목록)과 library.bib(BibTeX)를 자동으로 다시 만든다.

사용:
  python paperlib.py add <DOI | arXiv ID/URL | PDF 경로 | PDF URL> [--no-pdf]
  python paperlib.py list | search <단어...> | show <citekey>
  python paperlib.py cite <원고.md> [-o 결과.md] [--style apa|ieee] [--table] [--heading 참고문헌]
  python paperlib.py render [citekey]      summary.md → index.html (라이브러리 목록 index.html 포함)
  python paperlib.py rebuild

라이브러리 위치: 환경 변수 PAPER_LIB, 없으면 ~/paper-library
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz  # PyMuPDF
import requests

LIB = Path(os.environ.get("PAPER_LIB", Path.home() / "paper-library"))
PAPERS = LIB / "papers"
UA = {"User-Agent": "paperlib/1.0 (personal literature library)"}
STOP = {"a", "an", "the", "on", "of", "for", "in", "to", "and", "with", "via", "from", "towards", "toward", "is", "are", "beyond"}


# ---------------------------------------------------------------- 서지 정보
def http_json(url, **kw):
    r = requests.get(url, headers=UA, timeout=30, **kw)
    r.raise_for_status()
    return r.json()


def split_name(full):
    parts = full.strip().split()
    return {"family": parts[-1], "given": " ".join(parts[:-1])} if parts else {"family": "", "given": ""}


def from_crossref(doi):
    m = http_json(f"https://api.crossref.org/works/{requests.utils.quote(doi)}")["message"]
    abstract = re.sub(r"<[^>]+>", "", m.get("abstract", "") or "").strip()
    date = (m.get("issued") or m.get("published") or {}).get("date-parts", [[None]])[0]
    return {
        "title": html.unescape((m.get("title") or [""])[0]),
        "authors": [{"family": a.get("family", a.get("name", "")), "given": a.get("given", "")} for a in m.get("author", [])],
        "year": date[0] if date else None,
        "venue": html.unescape((m.get("container-title") or [""])[0]),
        "volume": m.get("volume", ""), "issue": m.get("issue", ""), "pages": m.get("page", ""),
        "doi": m.get("DOI", doi).lower(), "url": m.get("URL", ""), "type": m.get("type", ""),
        "abstract": html.unescape(abstract), "source": "crossref",
    }


def from_arxiv(aid):
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    r = requests.get("https://export.arxiv.org/api/query", params={"id_list": aid}, headers=UA, timeout=30)
    r.raise_for_status()
    e = ET.fromstring(r.text).find("a:entry", ns)
    if e is None or e.find("a:title", ns) is None:
        raise SystemExit(f"arXiv에서 {aid}를 찾지 못함")
    t = lambda tag: " ".join((e.findtext(tag, "", ns) or "").split())
    pdf = next((l.get("href") for l in e.findall("a:link", ns) if l.get("title") == "pdf"), f"https://arxiv.org/pdf/{aid}")
    return {
        "title": t("a:title"), "authors": [split_name(a.findtext("a:name", "", ns)) for a in e.findall("a:author", ns)],
        "year": int(t("a:published")[:4]), "venue": "arXiv", "volume": "", "issue": "", "pages": "",
        "doi": t("x:doi").lower(), "arxiv": aid, "url": f"https://arxiv.org/abs/{aid}", "type": "preprint",
        "abstract": t("a:summary"), "pdf_url": pdf, "journal_ref": t("x:journal_ref"), "source": "arxiv",
    }


def oa_pdf_url(doi):
    try:
        w = http_json(f"https://api.openalex.org/works/https://doi.org/{doi}")
    except Exception:
        return ""
    loc = w.get("best_oa_location") or {}
    return loc.get("pdf_url") or (w.get("open_access") or {}).get("oa_url") or ""


def search_title(title):
    """제목으로 Crossref 검색. 제목이 충분히 비슷할 때만 DOI를 돌려준다."""
    items = http_json("https://api.crossref.org/works", params={"query.bibliographic": title, "rows": 3})["message"]["items"]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    for it in items:
        cand = (it.get("title") or [""])[0]
        a, b = norm(cand), norm(title)
        if a and b and (a in b or b in a):
            return it["DOI"]
    return ""


ARXIV_RE = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arxiv:\s*)?(\d{4}\.\d{4,5})(v\d+)?", re.I)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.I)


def resolve(src):
    """입력 하나를 (meta, 로컬 PDF 경로 또는 None)으로."""
    p = Path(src)
    if p.suffix.lower() == ".pdf" and p.exists():
        doc = fitz.open(p)
        head = "".join(doc[i].get_text() for i in range(min(2, len(doc))))
        m = ARXIV_RE.search(head) if "arxiv" in head.lower() else None
        d = DOI_RE.search(head)
        if d:
            meta = from_crossref(d.group(1).rstrip(".,;)"))
        elif m:
            meta = from_arxiv(m.group(1))
        else:
            title = doc.metadata.get("title") or max(
                (s for b in doc[0].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]),
                key=lambda s: s["size"])["text"]
            doi = search_title(title)
            meta = from_crossref(doi) if doi else {"title": title.strip(), "authors": [], "year": None, "venue": "",
                                                   "doi": "", "url": "", "abstract": "", "source": "pdf"}
        return meta, p
    m = ARXIV_RE.fullmatch(src.strip()) or (ARXIV_RE.search(src) if "arxiv" in src.lower() else None)
    if m:
        meta = from_arxiv(m.group(1))
        if meta["doi"]:  # 출판본이 있으면 서지는 출판본, PDF는 arXiv
            try:
                pub = from_crossref(meta["doi"])
                pub.update(arxiv=meta["arxiv"], pdf_url=meta["pdf_url"], source="crossref+arxiv")
                meta = pub
            except Exception:
                pass
        return meta, None
    d = DOI_RE.search(src)
    if d:
        meta = from_crossref(d.group(1).rstrip(".,;)"))
        meta["pdf_url"] = oa_pdf_url(meta["doi"])
        return meta, None
    if src.lower().startswith("http"):
        tmp = LIB / "_download.pdf"
        download(src, tmp)
        return resolve(str(tmp))
    raise SystemExit(f"알 수 없는 입력: {src}")


def download(url, dest):
    r = requests.get(url, headers=UA, timeout=90)
    r.raise_for_status()
    if not r.content.startswith(b"%PDF"):
        raise RuntimeError(f"PDF가 아님 (아마 로그인·유료 페이지): {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)


# ---------------------------------------------------------------- citekey
def ascii_word(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]", "", s)


def make_key(meta):
    fam = ascii_word(meta["authors"][0]["family"]) if meta.get("authors") else ""
    word = next((ascii_word(w) for w in meta["title"].split() if ascii_word(w).lower() not in STOP and ascii_word(w)), "paper")
    base = f"{fam or 'Anon'}{meta.get('year') or 'nd'}{word.lower()}"
    key, n = base, 0
    while (PAPERS / key).exists() and json.loads((PAPERS / key / "meta.json").read_text(encoding="utf-8")).get("doi") != meta.get("doi"):
        n += 1
        key = base + "abcdefghij"[n - 1]
    return key


def find_existing(meta):
    for mj in PAPERS.glob("*/meta.json"):
        m = json.loads(mj.read_text(encoding="utf-8"))
        if (meta.get("doi") and m.get("doi") == meta["doi"]) or (meta.get("arxiv") and m.get("arxiv") == meta["arxiv"]):
            return mj.parent.name
    return None


# ---------------------------------------------------------------- 본문·그림
CAP_RE = re.compile(r"^\s*(fig(?:ure)?\.?)\s*(\d+)\s*[:.|   ]", re.I)


def extract_text(doc, out):
    parts = [f"<!-- page {i + 1} -->\n{pg.get_text('text').strip()}\n" for i, pg in enumerate(doc)]
    out.write_text("\n".join(parts), encoding="utf-8")


def extract_figures(doc, outdir, zoom=2.5):
    """캡션(Figure N: …) 위쪽의 그래픽 요소(이미지·벡터 그림)를 모아 잘라낸다."""
    outdir.mkdir(exist_ok=True)
    figs, seen = [], set()
    for pno, page in enumerate(doc):
        W, H = page.rect.width, page.rect.height
        blocks = [b for b in page.get_text("blocks") if b[6] == 0]
        caps = [b for b in blocks if CAP_RE.match(b[4])]
        if not caps:
            continue
        gfx = [fitz.Rect(i["bbox"]) for i in page.get_image_info()]
        gfx += [d["rect"] for d in page.get_drawings() if d["rect"].width * d["rect"].height < 0.8 * W * H]
        gfx = [g for g in gfx if g.width > 1 or g.height > 1]
        for cb in sorted(caps, key=lambda b: b[1]):
            num = int(CAP_RE.match(cb[4]).group(2))
            if num in seen:
                continue
            cap = fitz.Rect(cb[:4])
            col = (W / 2 - 5, W) if cap.x0 > W * 0.45 else (0, W / 2 + 5) if cap.x1 < W * 0.55 else (0, W)
            above_caps = [b[3] for b in caps if b[3] <= cap.y0 and b is not cb]
            top_limit = max(above_caps, default=0)
            cand = sorted((g for g in gfx if g.y1 <= cap.y0 + 4 and g.y0 >= top_limit - 2
                           and g.x1 > col[0] and g.x0 < col[1]), key=lambda g: -g.y1)
            if not cand or cap.y0 - cand[0].y1 > 60:
                continue
            box = fitz.Rect(cand[0])
            for g in cand[1:]:
                if g.y1 >= box.y0 - 30:
                    box |= g
            if box.height < 25 or box.width < 40:
                continue
            for _ in range(3):  # 그림 안팎의 짧은 글자(축 눈금·축 이름·범례) 포함
                near = box + (-22, -14, 22, 14)
                for b in blocks:
                    r = fitz.Rect(b[:4])
                    short = len(b[4].strip()) < 80 or r.intersects(box)
                    if short and r.intersects(near) and r.y1 <= cap.y0 + 1 and r.y0 >= top_limit and b is not cb:
                        box |= r
            box = (box + (-6, -6, 6, 6)) & page.rect
            name = f"fig{num}.jpg"
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=box)
            pix.save(outdir / name, jpg_quality=85)
            seen.add(num)
            figs.append({"id": f"fig{num}", "label": f"Figure {num}", "page": pno + 1,
                         "caption": " ".join(cb[4].split()), "file": f"figures/{name}"})
    return sorted(figs, key=lambda f: int(f["id"][3:]))


# ---------------------------------------------------------------- 라이브러리 색인
def bib_entry(m):
    esc = lambda s: str(s).replace("{", "").replace("}", "")
    kind = "misc" if m.get("type") in ("preprint", "posted-content") else "inproceedings" if "proceedings" in m.get("type", "") else "article"
    f = {"title": "{" + esc(m["title"]) + "}",
         "author": " and ".join(f"{a['family']}, {a['given']}".strip(", ") for a in m.get("authors", [])),
         "year": m.get("year") or "", ("booktitle" if kind == "inproceedings" else "journal"): m.get("venue", ""),
         "volume": m.get("volume", ""), "number": m.get("issue", ""), "pages": m.get("pages", ""),
         "doi": m.get("doi", ""), "eprint": m.get("arxiv", ""), "url": m.get("url", "")}
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items() if v)
    return f"@{kind}{{{m['key']},\n{body}\n}}\n"


def rebuild():
    metas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(PAPERS.glob("*/meta.json"))]
    idx = [{k: m.get(k) for k in ("key", "title", "year", "venue", "doi", "arxiv", "added")} |
           {"authors": "; ".join(a["family"] for a in m.get("authors", [])),
            "has_summary": (PAPERS / m["key"] / "summary.md").exists(),
            "figures": len(json.loads((PAPERS / m["key"] / "figures.json").read_text(encoding="utf-8")))
            if (PAPERS / m["key"] / "figures.json").exists() else 0} for m in metas]
    (LIB / "library.json").write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    (LIB / "library.bib").write_text("\n".join(bib_entry(m) for m in metas), encoding="utf-8")
    return metas


def load_meta(key):
    p = PAPERS / key / "meta.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ---------------------------------------------------------------- 명령
def cmd_add(a):
    PAPERS.mkdir(parents=True, exist_ok=True)
    meta, local_pdf = resolve(a.source)
    key = find_existing(meta) or make_key(meta)
    d = PAPERS / key
    d.mkdir(exist_ok=True)
    meta.update(key=key, added=meta.get("added") or datetime.date.today().isoformat())
    pdf = d / "paper.pdf"
    note = ""
    if local_pdf:
        if Path(local_pdf).resolve() != pdf.resolve():
            shutil.copyfile(local_pdf, pdf)
        if Path(local_pdf).name == "_download.pdf":
            Path(local_pdf).unlink()
    elif not pdf.exists() and meta.get("pdf_url"):
        try:
            download(meta["pdf_url"], pdf)
        except Exception as e:
            note = f"PDF 내려받기 실패: {e}"
    elif not pdf.exists():
        note = "공개 PDF 없음 — PDF 파일 경로로 다시 add 하면 본문·그림을 추출함"
    figs = []
    if pdf.exists():
        doc = fitz.open(pdf)
        extract_text(doc, d / "text.md")
        figs = extract_figures(doc, d / "figures")
        (d / "figures.json").write_text(json.dumps(figs, ensure_ascii=False, indent=1), encoding="utf-8")
        meta["n_pages"] = len(doc)
        doc.close()
        if a.no_pdf:
            pdf.unlink()
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    rebuild()
    size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
    print(json.dumps({"key": key, "dir": str(d), "title": meta["title"], "year": meta.get("year"),
                      "venue": meta.get("venue"), "doi": meta.get("doi"), "text": (d / "text.md").exists(),
                      "figures": [f"{f['label']} (p.{f['page']})" for f in figs], "size_kb": size // 1024,
                      "note": note}, ensure_ascii=False, indent=1))


def cmd_list(a):
    for r in json.loads((LIB / "library.json").read_text(encoding="utf-8")) if (LIB / "library.json").exists() else []:
        print(f"{r['key']:32} {r['year'] or '':5} {'요약O' if r['has_summary'] else '요약X'} 그림{r['figures']:<2} {r['title'][:70]}")


def cmd_search(a):
    terms = [t.lower() for t in a.terms]
    for d in sorted(PAPERS.iterdir()):
        m = load_meta(d.name)
        if not m:
            continue
        hay = {"meta": f"{m['title']} {m.get('abstract', '')}".lower()}
        for f in ("summary.md", "text.md"):
            if (d / f).exists():
                hay[f] = (d / f).read_text(encoding="utf-8").lower()
        hits = {k: sum(v.count(t) for t in terms) for k, v in hay.items() if all(t in v for t in terms)}
        if hits:
            print(f"{d.name:32} {m['title'][:60]}  ({', '.join(f'{k}:{n}' for k, n in hits.items())})")


def cmd_show(a):
    m = load_meta(a.key) or sys.exit(f"없는 citekey: {a.key}")
    d = PAPERS / a.key
    print(json.dumps({k: v for k, v in m.items() if k != "abstract"}, ensure_ascii=False, indent=1))
    print("files:", ", ".join(str(p.relative_to(d)) for p in sorted(d.rglob("*")) if p.is_file()))


# ---------------------------------------------------------------- 인용
CITE_RE = re.compile(r"\[(@[^\[\]]+)\]")


def names_short(m):
    fam = [a["family"] for a in m.get("authors", [])]
    return fam[0] if len(fam) == 1 else f"{fam[0]} & {fam[1]}" if len(fam) == 2 else f"{fam[0]} et al." if fam else m["title"][:30]


def initials(given):
    return " ".join(f"{p[0]}." for p in re.split(r"[\s-]+", given) if p)


def ref_apa(m):
    au = [f"{a['family']}, {initials(a['given'])}".strip(", ") for a in m.get("authors", [])]
    if len(au) > 20:
        au_s = ", ".join(au[:19]) + ", ... " + au[-1]
    else:
        au_s = au[0] if len(au) == 1 else ", ".join(au[:-1]) + ", & " + au[-1] if au else ""
    src = f"*{m['venue']}*" if m.get("venue") else ""
    if m.get("volume"):
        src += f", *{m['volume']}*" + (f"({m['issue']})" if m.get("issue") else "")
    if m.get("pages"):
        src += f", {m['pages']}"
    link = f"https://doi.org/{m['doi']}" if m.get("doi") else m.get("url", "")
    return f"{au_s} ({m.get('year') or 'n.d.'}). {m['title']}. {src}. {link}".replace(" . ", " ").replace("..", ".")


def ref_ieee(m):
    au = [f"{initials(a['given'])} {a['family']}".strip() for a in m.get("authors", [])]
    au_s = au[0] if len(au) == 1 else ", ".join(au[:-1]) + ", and " + au[-1] if len(au) <= 6 else au[0] + " et al." if au else ""
    vol = f", vol. {m['volume']}" if m.get("volume") else ""
    no = f", no. {m['issue']}" if m.get("issue") else ""
    pp = (f", pp. {m['pages']}" if "-" in str(m["pages"]) else f", Art. no. {m['pages']}") if m.get("pages") else ""
    link = f", doi: {m['doi']}" if m.get("doi") else f", [Online]. Available: {m.get('url')}" if m.get("url") else ""
    return f"{au_s}, “{m['title']},” *{m.get('venue', '')}*{vol}{no}{pp}, {m.get('year') or 'n.d.'}{link}."


def cmd_cite(a):
    src = Path(a.draft)
    text = src.read_text(encoding="utf-8")
    order, missing = [], set()

    def parse(group):
        out = []
        for part in group.split(";"):
            part = part.strip()
            mm = re.match(r"@([\w:.\-]+)\s*(?:,\s*(.+))?$", part)
            if not mm:
                return None
            out.append((mm.group(1), (mm.group(2) or "").strip()))
        return out

    def repl(mt):
        items = parse(mt.group(1))
        if items is None:
            return mt.group(0)
        bits = []
        for key, loc in items:
            m = load_meta(key)
            if not m:
                missing.add(key)
                bits.append(f"??{key}")
                continue
            if key not in order:
                order.append(key)
            if a.style == "ieee":
                bits.append(f"{order.index(key) + 1}" + (f", {loc}" if loc else ""))
            else:
                bits.append(f"{names_short(m)}, {m.get('year') or 'n.d.'}" + (f", {loc}" if loc else ""))
        return f"[{', '.join(bits)}]" if a.style == "ieee" else f"({'; '.join(bits)})"

    body = CITE_RE.sub(repl, text)
    metas = {k: load_meta(k) for k in order}
    keys = order if a.style == "ieee" else sorted(order, key=lambda k: (names_short(metas[k]).lower(), metas[k].get("year") or 0))
    fmt = ref_ieee if a.style == "ieee" else ref_apa
    out = [body.rstrip(), "", f"## {a.heading}", ""]
    if a.table:  # hwpx 스킬용 표
        out += ["<!-- widths: 8,17,37,38 -->", "| 번호 | 저자(연도) | 논문·출처 | DOI |", "|---|---|---|---|"]
        out += [f"| {i} | {names_short(metas[k]).replace(' et al.', ' 외')} ({metas[k].get('year') or 'n.d.'}) | "
                f"{metas[k]['title']}, {metas[k].get('venue', '')} | {metas[k].get('doi') or metas[k].get('url', '')} |"
                for i, k in enumerate(keys, 1)]
    else:
        out += [f"{f'[{i}] ' if a.style == 'ieee' else ''}{fmt(metas[k])}" + ("" if a.style == "ieee" else "") for i, k in enumerate(keys, 1)]
        out = out[:4] + ["\n".join(out[4:]) if a.style == "ieee" else "\n\n".join(out[4:])]
    dest = Path(a.output) if a.output else src.with_name(src.stem + "_cited.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "cited": len(order), "missing": sorted(missing)}, ensure_ascii=False))


# ---------------------------------------------------------------- HTML 보기
CSS = """body{max-width:860px;margin:32px auto;padding:0 16px;font:16px/1.7 'Pretendard','Malgun Gothic',sans-serif;color:#1d1d1f;background:#fff}
h1{font-size:1.5em;line-height:1.35}h2{margin-top:2em;border-bottom:1px solid #e5e5ea;padding-bottom:.2em}
.meta{color:#555;font-size:.92em;background:#f5f5f7;padding:10px 14px;border-radius:8px}
img{max-width:100%;border:1px solid #e5e5ea;border-radius:6px}em{color:#555}
.cite{font-size:.8em;color:#0a66c2;background:#eef4fb;border-radius:4px;padding:0 4px}
code{background:#f5f5f7;padding:0 4px;border-radius:4px}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:4px 8px}
@media (prefers-color-scheme:dark){body{background:#1c1c1e;color:#eee}.meta,code{background:#2c2c2e;color:#ccc}em{color:#aaa}.cite{background:#1d3550;color:#8cc4ff}}"""


def page_html(title, body):
    return f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"


def render_one(key):
    import markdown
    d, m = PAPERS / key, load_meta(key)
    src = (d / "summary.md").read_text(encoding="utf-8") if (d / "summary.md").exists() else "_요약 노트 없음_"
    src = CITE_RE.sub(lambda mt: f"<span class='cite'>{html.escape(mt.group(1))}</span>", src)
    au = ", ".join(f"{a['given']} {a['family']}".strip() for a in m.get("authors", []))
    link = f"https://doi.org/{m['doi']}" if m.get("doi") else m.get("url", "")
    head = (f"<p><a href='../../index.html'>← 라이브러리</a></p><h1>{html.escape(m['title'])}</h1>"
            f"<div class='meta'><b>{html.escape(au)}</b><br>{html.escape(str(m.get('venue', '')))} ({m.get('year') or 'n.d.'})"
            f" · <a href='{link}'>{html.escape(link)}</a><br>인용 키: <code>[@{key}]</code></div>")
    (d / "index.html").write_text(page_html(m["title"], head + markdown.markdown(src, extensions=["tables"])), encoding="utf-8")


def cmd_render(a):
    keys = [a.key] if a.key else [p.name for p in sorted(PAPERS.iterdir()) if (p / "meta.json").exists()]
    for k in keys:
        render_one(k)
    rows = "".join(f"<tr><td><a href='papers/{r['key']}/index.html'>{html.escape(r['title'])}</a></td><td>{html.escape(r['authors'][:40])}</td>"
                   f"<td>{r['year'] or ''}</td><td><code>{r['key']}</code></td><td>{'✓' if r['has_summary'] else ''}</td></tr>"
                   for r in json.loads((LIB / "library.json").read_text(encoding="utf-8")))
    (LIB / "index.html").write_text(page_html("논문 라이브러리", "<h1>논문 라이브러리</h1><table><tr><th>제목</th><th>저자</th><th>연도</th><th>인용 키</th><th>요약</th></tr>"
                                              + rows + "</table>"), encoding="utf-8")
    print(f"{len(keys)}편 렌더링 → {LIB / 'index.html'}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("add"); p.add_argument("source"); p.add_argument("--no-pdf", action="store_true"); p.set_defaults(f=cmd_add)
    sp.add_parser("list").set_defaults(f=cmd_list)
    p = sp.add_parser("search"); p.add_argument("terms", nargs="+"); p.set_defaults(f=cmd_search)
    p = sp.add_parser("show"); p.add_argument("key"); p.set_defaults(f=cmd_show)
    p = sp.add_parser("cite"); p.add_argument("draft"); p.add_argument("-o", "--output")
    p.add_argument("--style", choices=["apa", "ieee"], default="apa"); p.add_argument("--table", action="store_true")
    p.add_argument("--heading", default="참고문헌"); p.set_defaults(f=cmd_cite)
    p = sp.add_parser("render"); p.add_argument("key", nargs="?"); p.set_defaults(f=cmd_render)
    sp.add_parser("rebuild").set_defaults(f=lambda a: print(f"{len(rebuild())}편 색인"))
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
