# -*- coding: utf-8 -*-
"""Cut-point analysis: line-based balance per page, with block constraints."""
import re, math, os
from PIL import Image

SRC = r"D:\CloudyInkForge\pentium\2611\2611.html"
ROOT = r"D:\CloudyInkForge\pentium\2611"
html = open(SRC, encoding="utf-8").read()
PAGE_MARKS = list(re.finditer(r'<div class="page page--(odd|even)">', html))

LINE_MM = 9 * 1.78 * 25.4 / 72      # 5.653 mm
COL_W = (170 - 8) / 2                # 81 mm
CHARS = 25.5                          # chars per line at 9pt in 81mm
BODY_LINES = (285 - 26 - 24) / LINE_MM

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
    raise ValueError

def strip_text(h):
    h = re.sub(r'<br\s*/?>', '', h)
    h = re.sub(r'<[^>]+>', '', h)
    return re.sub(r'\s+', '', h.replace('&nbsp;', ' '))

def img_h(lines_html, width_mm):
    out = []
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', lines_html):
        p = os.path.join(ROOT, m.group(1).replace('/', os.sep))
        with Image.open(p) as im:
            w, h = im.size
        out.append(width_mm * h / w)
    return out

def blocks_of(page):
    fm = re.search(r'<div class="flow"[^>]*>', page)
    if not fm:
        return None, None
    fstart = fm.start()
    fend = match_div_end(page, fstart)
    inner = page[fm.end():fend - 6]
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
            break
        h = inner[bstart:endrel]
        cls = (re.search(r'class="([^"]*)"', h) or [None, ""])[1]
        blocks.append({"html": h, "cls": cls, "chars": len(strip_text(h))})
        pos = endrel
    return fm, blocks

print(f"line={LINE_MM:.3f}mm  body_lines={BODY_LINES:.1f}  col chars/line={CHARS}")
for idx, m in enumerate(PAGE_MARKS):
    pstart = m.start()
    pend = PAGE_MARKS[idx+1].start() if idx+1 < len(PAGE_MARKS) else html.index("</body>")
    page = html[pstart:pend]
    pno = re.search(r'class="footer-page">(\d+)<', page).group(1)
    fm, blocks = blocks_of(page)
    if blocks is None:
        print(f"\n### {pno}: NO FLOW")
        continue
    # heights
    for b in blocks:
        c = b["cls"]
        if "sep3" in c: b["lines"] = 1.4
        elif "pull" in c: b["lines"] = 1.9
        elif "closeq" in c: b["lines"] = 3.0
        elif "endmark" in c: b["lines"] = 1.2
        elif "fig" in c:
            wm = 81.0
            w = re.search(r'width:([\d.]+)mm', b["html"])
            if w: wm = float(w.group(1))
            hs = img_h(b["html"], wm)
            cap = 3.0 if "collage" not in b["html"] else 6.0
            b["lines"] = sum(x / LINE_MM for x in hs) + 2.0 + cap
            b["imgmm"] = [round(x, 1) for x in hs]
        elif "display" in c: b["lines"] = 1.6
        elif "sec" in c: b["lines"] = 2.2
        elif "sub" in c: b["lines"] = 1.9
        elif "dc" in c:
            b["lines"] = math.ceil(b["chars"] / CHARS) + 0.6
        else:
            b["lines"] = max(1, math.ceil(b["chars"] / CHARS)) + 0.2
        if "op-head" in c:
            b["lines"] = 6.0
    movable = {"pull", "closeq", "endmark", "sep3"}
    keep = [b for b in blocks if not any(k in b["cls"] for k in movable)]
    moved = [b["cls"] for b in blocks if any(k in b["cls"] for k in movable)]
    print(f"\n### {pno}  blocks={len(blocks)} kept={len(keep)} moved={moved}")
    for i, b in enumerate(keep):
        print(f"  [{i:2d}] {b['cls']:10s} ch={b['chars']:4d} L={b['lines']:5.1f} {b.get('imgmm','')}")
    tot = sum(b["lines"] for b in keep)
    print(f"   total_lines={tot:.1f} cap/page={BODY_LINES*2:.1f} (col {BODY_LINES:.1f})")
    # candidate cuts
    opts = []
    for k in range(1, len(keep)):
        L = sum(b["lines"] for b in keep[:k])
        R = tot - L
        last = keep[k-1]
        bad = []
        if "sec" in last["cls"]: bad.append("ends-sec")
        if "sub" in last["cls"]: bad.append("ends-sub")
        if "op-head" in last["cls"]: bad.append("ends-ophead")
        opts.append((abs(L - R), k, L, R, ",".join(bad)))
    opts.sort()
    for d, k, L, R, bad in opts[:5]:
        print(f"   cut after[{k-1}] diff={d:5.1f} L={L:5.1f} R={R:5.1f} {bad}")
