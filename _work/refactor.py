# -*- coding: utf-8 -*-
"""Refactor 2611.html: .flow (column-count:2) -> manual .flow-block with two .col."""
import re, io, os, sys

ROOT = r"D:\CloudyInkForge\pentium\2611"
SRC = os.path.join(ROOT, "2611.html")
DST = os.path.join(ROOT, "2611.refactored.html")

html = open(SRC, encoding="utf-8").read()

PAGE_OPEN = re.compile(r'<div class="page page--(odd|even)">')

# cut = number of (kept) blocks placed in the left column
CFG = {
    "002": {"cut": 10},
    "003": {"cut": 9},
    "004": {"cut": 4},
    "006": {"cut": 2},
    "007": {"cut": 2},
    "008": {"cut": 3},
    "009": {"cut": 1},
    "011": {"cut": 6},
    "012": {"cut": 6},
    "013": {"cut": 3},
    "014": {"cut": 4},
    "015": {"cut": 3},
    "016": {"cut": 4},
    "017": {"cut": 6},
    "018": {"collage": True},
    "019": {"cut": 2},
    "020": {"cut": 2},
    "021": {"cut": 5, "figfix": ("width:150mm", "width:100%")},
    "022": {"cut": 5, "figfix": ("width:142mm", "width:100%")},
    "023": {"figtop": True, "cut": 4},
}

MOVABLE = ("pull", "closeq", "endmark", "sep3")

# pages that cannot be balanced with whole-block cuts (see NOTES in report run):
# content at capacity, any paragraph-boundary cut puts one column 9-11mm over the
# 211-218mm available column height, and the allowed line-height/margin tunings
# recover at most ~4mm.  Rule: revert to original .flow and flag.
REVERT = {
    "012": "正文 70 行 + 通栏 pull/sep3，每栏可用 211mm；段落整块断点仅 193/221mm 与 234/181mm，总有一栏超 211mm",
    "016": "pull 通栏后每栏可用 218mm；断点仅 108/286mm 与 227/166mm，总有一栏超 218mm",
    "017": "closeq 通栏后每栏可用 216mm；断点仅 205/227mm 与 228/203mm，总有一栏超 216mm",
}


def match_div_end(s, start):
    depth = 0
    for m in re.finditer(r'</?div\b[^>]*>', s[start:]):
        t = m.group(0)
        if t.startswith("</"):
            depth -= 1
            if depth == 0:
                return start + m.end()
        else:
            depth += 1
    raise ValueError("unbalanced div")


def parse_blocks(inner):
    """Split inner HTML of .flow into top-level element strings."""
    blocks, pos = [], 0
    while True:
        nm = re.search(r'<(p|div|h\d)\b', inner[pos:])
        if not nm:
            break
        bstart = pos + nm.start()
        tag = nm.group(1)
        depth, endrel = 0, None
        for mm in re.finditer(r'</?%s\b[^>]*>' % tag, inner[bstart:]):
            t = mm.group(0)
            if t.startswith("</"):
                depth -= 1
                if depth == 0:
                    endrel = bstart + mm.end()
                    break
            elif not t.endswith("/>"):
                depth += 1
        if endrel is None:
            raise ValueError("unbalanced block")
        blocks.append(inner[bstart:endrel])
        pos = endrel
    return blocks


def cls_of(block):
    m = re.search(r'class="([^"]*)"', block)
    return m.group(1) if m else ""


def shift(block, delta):
    """Reindent a multi-line block by delta spaces (relative indentation kept)."""
    lines = block.split("\n")
    out = [" " * (8 + delta) + lines[0].lstrip(" ")]
    for ln in lines[1:]:
        if delta >= 0:
            out.append(" " * delta + ln)
        else:
            k = -delta
            out.append(ln[k:] if ln.startswith(" " * k) else ln.lstrip(" "))
    return "\n".join(out)


def col(blocks, delta=2):
    body = "\n".join(shift(b, delta) for b in blocks)
    return (
        "        <div class=\"col\">\n"
        + body
        + "\n        </div>"
    )


def flow_block(open_extra, left, right, delta=0):
    return (
        "      <div class=\"flow-block\"" + open_extra + ">\n"
        + col(left, delta + 2)
        + "\n"
        + col(right, delta + 2)
        + "\n      </div>"
    )


def refactor_page(page, pno):
    if pno in REVERT:
        return "<!-- NEEDS_HUMAN_REVIEW: %s · %s -->\n  " % (pno, REVERT[pno]) + page
    cfg = CFG[pno]
    fm = re.search(r'<div class="flow"[^>]*>', page)
    fstart = fm.start()
    fend = match_div_end(page, fstart)
    open_tag = fm.group(0)
    # preserve inline style on the (first) flow-block
    extra = ""
    st = re.search(r'(style="[^"]*")', open_tag)
    if st:
        extra = " " + st.group(1)
    inner = page[fm.end():fend - len("</div>")]

    blocks = parse_blocks(inner)

    # per-page figure tweaks (inline width -> 100%)
    if "figfix" in cfg:
        a, b = cfg["figfix"]
        blocks = [x.replace(a, b) for x in blocks]

    movable = [b for b in blocks if any(m in cls_of(b) for m in MOVABLE)]
    kept = [b for b in blocks if not any(m in cls_of(b) for m in MOVABLE)]

    tail = "\n" + "\n".join(shift(b, -2) for b in movable) if movable else ""

    if "collage" in cfg:
        # kept = [p, p, fig.wide, p, p]; full-width collage between two flow-blocks
        figidx = next(i for i, b in enumerate(kept) if "fig" in cls_of(b))
        before, fig, after = kept[:figidx], kept[figidx], kept[figidx + 1:]
        assert len(before) == 2 and len(after) == 2, (pno, len(before), len(after))
        new = (
            flow_block(extra, before[:1], before[1:], 0)
            + "\n"
            + shift(fig, -2)
            + "\n"
            + flow_block("", after[:1], after[1:], 0)
            + tail
        )
    else:
        head = []
        if "figtop" in cfg:
            assert "fig" in cls_of(kept[0]), (pno, cls_of(kept[0]))
            head.append(shift(kept[0], -2))
            kept = kept[1:]
        cut = cfg["cut"]
        assert 0 < cut < len(kept), (pno, cut, len(kept))
        new = ("\n".join(head) + "\n" if head else "") + flow_block(
            extra, kept[:cut], kept[cut:], 0
        ) + tail

    prefix = page[:fstart]
    prefix = prefix[:len(prefix) - (len(prefix) - len(prefix.rstrip(" \t")))]
    return prefix + new + page[fend:]


# ---- process all pages ----
out = []
pos = 0
seen = []
for i, m in enumerate(PAGE_OPEN.finditer(html)):
    pstart = m.start()
    if i + 1 < len(PAGE_OPEN.findall(html)):
        pass
    out.append(html[pos:pstart])
    # page end = next page open (or </body>)
    later = [x.start() for x in PAGE_OPEN.finditer(html, pstart + 1)]
    pend = later[0] if later else html.index("</body>")
    page = html[pstart:pend]
    pno = re.search(r'class="footer-page">(\d+)<', page).group(1)
    seen.append(pno)
    if '<div class="flow"' in page or re.search(r'<div class="flow"', page):
        out.append(refactor_page(page, pno))
    else:
        out.append(page)
    pos = pend
out.append(html[pos:])

res = "".join(out)

# ---- append CSS before </style> ----
CSS = """  .flow-block {
    flex: 1 1 auto; min-height: 0;
    display: flex; align-items: stretch; gap: 8mm;
  }
  .flow-block .col {
    flex: 1 1 0; min-width: 0;
    display: flex; flex-direction: column;
    overflow: hidden;
  }
  .flow-block p {
    margin: 0 0 0.35em; text-indent: 2em;
    font-family: "Noto Serif SC","Source Han Serif SC","SimSun",serif;
    font-size: 9pt; line-height: 1.78; text-align: justify;
    color: device-cmyk(0 0 0 1);
  }
  .flow-block p:last-child { margin-bottom: 0; }
  .flow-block p.display {
    text-indent: 0; text-align: center;
    font-family: "Noto Sans SC","Source Han Sans SC","Microsoft YaHei",sans-serif;
    font-weight: 700; font-size: 12pt;
    color: device-cmyk(0 0.88 0.90 0.02); margin: 2.5mm 0;
  }
  .flow-block p.dc::first-letter {
    float: left; font-family: "Noto Serif SC","Source Han Serif SC","SimSun",serif;
    font-size: 28pt; line-height: 1.05; padding: 0.6mm 1.8mm 0 0;
    color: device-cmyk(0 0.88 0.90 0.02); font-weight: 700;
  }
  .flow-block .sec { margin: 3.2mm 0 2mm; font-weight: 700; font-size: 11.5pt; line-height: 1.4; color: device-cmyk(0 0 0 1); }
  .flow-block .sec .blk { display: inline-block; width: 2.2mm; height: 2.2mm; background: device-cmyk(0 0.88 0.90 0.02); margin-right: 2mm; }
  .flow-block .sub { margin: 2.2mm 0 1.6mm; font-weight: 500; font-size: 10.5pt; line-height: 1.4; color: device-cmyk(0 0 0 1); }
  .flow-block .sub .dash { display: inline-block; width: 3.5mm; height: 0.7mm; background: device-cmyk(0 0.88 0.90 0.02); margin: 0 1.8mm 1mm 0; }
  .flow-block .fig { margin: 1.5mm 0 2mm; text-indent: 0; }
  .flow-block .fig img { display: block; width: 100%; box-sizing: border-box; border: 0.2mm solid device-cmyk(0 0 0 0.30); }
"""
assert res.count("</style>") == 1
res = res.replace("</style>", "\n" + CSS + "</style>")

open(DST, "w", encoding="utf-8", newline="").write(res)
print("pages:", len(seen), seen)
print("written:", DST, len(res))
