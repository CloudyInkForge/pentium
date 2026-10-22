# -*- coding: utf-8 -*-
"""Analytic layout report for the refactored file: per-column content height vs available."""
import re, math, os
from PIL import Image
from lxml import html as LH

ROOT = r"D:\CloudyInkForge\pentium\2611"
B = open(os.path.join(ROOT, "2611.refactored.html"), encoding="utf-8").read()
LINE = 9 * 1.78 * 25.4 / 72      # 5.651 mm
CH = 25.0                        # chars per line (9pt, 81mm, conservative)
BODY = 285 - 26 - 24             # 235 mm


def cls(e):
    return (e.get("class") or "").split()


def px(src):
    p = os.path.join(ROOT, src.replace("/", os.sep))
    with Image.open(p) as im:
        w, h = im.size
    return w, h


def blk_h(e):
    """estimated height in mm of one block inside a column (or full width)."""
    c = cls(e)
    t = re.sub(r'\s+', '', e.text_content())
    if "fig" in c:
        st = e.get("style") or ""
        m = re.search(r'width:\s*([\d.]+)(mm|%)', st)
        imgs = e.findall(".//img")
        if "collage" in LH.tostring(e, encoding="unicode"):
            return 104 + 3.5 + 4.5 + 2.0       # h104 + caption + fig margins
        if m and m.group(2) == "mm":
            wmm = float(m.group(1))
        elif m and m.group(2) == "%":
            wmm = 81.0
        else:
            wmm = 81.0
        hsum = 0.0
        for im in imgs:
            w, h = px(im.get("src"))
            hsum += wmm * h / w
        # caption: 7.5pt chars on wmm, line 1.4 + margin
        cap = e.find("div[@class='figcap']")
        n = len(re.sub(r'\s+', '', cap.text_content())) if cap is not None else 0
        caplines = max(1, math.ceil(n * 2.646 / max(wmm, 1)))
        return hsum + caplines * 3.97 + 1.2 + 3.5
    if "sep3" in c:
        return 1.5 + 2.6 * 2
    if "pull" in c:
        return 13.5 * 1.55 * 25.4 / 72 + 3.2 * 2 + 1.6 * 2
    if "closeq" in c:
        qt = e.find("div[@class='qt']")
        n = len(re.sub(r'\s+', '', qt.text_content())) if qt is not None else 0
        lines = max(1, math.ceil(n * (15 * 25.4 / 72) / 170))
        return 6 + 0.2 + 3.5 + lines * 15 * 1.7 * 25.4 / 72
    if "endmark" in c:
        return 4 + 2.2
    if "sec" in c:
        return 11.5 * 1.4 * 25.4 / 72 + 3.2 + 2
    if "sub" in c:
        return 10.5 * 1.4 * 25.4 / 72 + 2.2 + 1.6
    if "display" in c:
        return 12 * 25.4 / 72 + 2.5 * 2
    if "op-head" in c:
        # kicker + title + bar + byline (+ art-sub / lead / toc)
        h = 3.2
        ti = e.find(".//h1")
        if ti is not None:
            fs = 30.0
            m = re.search(r'font-size:\s*([\d.]+)pt', ti.get("style") or "")
            if m:
                fs = float(m.group(1))
            h += 4.5 + fs * 1.18 * 25.4 / 72
        if e.find(".//div[@class='art-sub']") is not None:
            h += 2.2 + 12 * 25.4 / 72
        h += 4 + 0.9 + 2.8 + 3.0
        for extra in e.findall(".//p[@class='lead']"):
            n = len(re.sub(r'\s+', '', extra.text_content()))
            h += 2.5 + math.ceil(n * (10.5 * 25.4 / 72) / 170) * 10.5 * 1.85 * 25.4 / 72
        if e.find(".//div[@class='toc']") is not None:
            h += 3.5 + 4 + 3 * (1.6 + 1.2 + 11 * 1.4 * 25.4 / 72)
        return h
    # paragraph
    if "dc" in c:
        return math.ceil((len(t) + 2) / CH) * LINE + 0.35 * 9 * 25.4 / 72
    return max(1, math.ceil((len(t) + 2) / CH)) * LINE + 0.35 * 9 * 25.4 / 72


doc = LH.fromstring(B)


def pages(d):
    return [e for e in d.iter("div") if "page" in cls(e)]


print(f"{'page':5s} {'ophead':>6s} {'full':>5s} {'trail':>5s} {'avail':>6s} | "
      f"{'L':>6s} {'R':>6s} {'diff':>5s}  verdict")
worst = []
for P in pages(doc):
    pno = [x for x in P.iter("span") if "footer-page" in cls(x)][0].text_content().strip()
    body = [e for e in P.iter("div") if "page-body" in cls(e)][0]
    if not any("flow-block" in cls(c) for c in body):
        print(f"{pno:5s} (no flow-block)")
        continue
    op = sum(blk_h(c) for c in body if "op-head" in cls(c))
    full = sum(blk_h(c) for c in body if "fig" in cls(c))
    trail = sum(blk_h(c) for c in body if set(cls(c)) & {"pull", "closeq", "endmark", "sep3"})
    avail = BODY - op - full - trail
    blocks = [c for c in body if "flow-block" in cls(c)]
    res = []
    for blk in blocks:
        cols = [c for c in blk if "col" in cls(c)]
        hh = [sum(blk_h(k) for k in c) for c in cols]
        res.append(hh)
    base = sum(max(h) for h in res)
    # allocation: grow if space, shrink proportionally if over
    alloc = []
    for h in res:
        alloc.append([x * (avail / base) if base > avail else x + (avail - base) * x / base
                      for x in h])
    over = any(a < x - 0.2 for h, ah in zip(res, alloc) for x, a in zip(h, ah))
    L = sum(h[0] for h in res)
    R = sum(h[1] for h in res)
    d = abs(L - R)
    verdict = "CLIP-RISK" if over else ("ok" if d <= LINE else "ok(ragged %.1fmm)" % d)
    if over:
        worst.append(pno)
    print(f"{pno:5s} {op:6.1f} {full:5.1f} {trail:5.1f} {avail:6.1f} | "
          f"{L:6.1f} {R:6.1f} {d:5.1f}  {verdict}")

print("\nclip-risk pages:", worst or "none")
