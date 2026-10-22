# -*- coding: utf-8 -*-
"""Inventory: per page, top-level blocks of .flow with char counts and est. lines."""
import re, sys, json

SRC = r"D:\CloudyInkForge\pentium\2611\2611.html"
html = open(SRC, encoding="utf-8").read()

# split pages
page_marks = list(re.finditer(r'<div class="page page--(odd|even)">', html))
print("pages:", len(page_marks))

def match_div_end(s, start):
    """start index of tag '<div'. return index after matching close."""
    i = start
    depth = 0
    for m in re.finditer(r'</?div\b[^>]*>', s[start:]):
        tag = m.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return start + m.end()
        else:
            depth += 1
    raise ValueError("unbalanced")

def strip_text(h):
    h = re.sub(r'<br\s*/?>', '', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('&nbsp;', ' ')
    return re.sub(r'\s+', '', h)

pages = []
for idx, m in enumerate(page_marks):
    pstart = m.start()
    pend = page_marks[idx+1].start() if idx+1 < len(page_marks) else html.index("</body>")
    body = html[pstart:pend]
    pno = re.search(r'class="footer-page">(\d+)<', body)
    pno = pno.group(1) if pno else "?"
    # find flow
    fm = re.search(r'<div class="flow"[^>]*>', body)
    if not fm:
        pages.append((pno, None, body))
        continue
    fstart = pstart + fm.start()
    fend_abs = match_div_end(html, fstart)
    fend = fend_abs - pstart
    flow_open = fm.group(0)
    inner = body[fm.end():fend - len("</div>")]
    # top level blocks
    blocks = []
    pos = 0
    while True:
        nm = re.search(r'<(p|div|h\d|figure)\b', inner[pos:])
        if not nm:
            break
        bstart = pos + nm.start()
        # find matching end of this element (self-closing unlikely)
        tag = nm.group(1)
        depth = 0
        endrel = None
        for mm in re.finditer(r'</?%s\b[^>]*>' % tag, inner[bstart:]):
            t = mm.group(0)
            if t.startswith("</"):
                depth -= 1
                if depth == 0:
                    endrel = bstart + mm.end()
                    break
            else:
                if not t.endswith("/>"):
                    depth += 1
        if endrel is None:
            break
        blocks.append(inner[bstart:endrel])
        pos = endrel
    pages.append((pno, {"open": flow_open, "blocks": blocks, "body": body, "inner": inner}, body))

for pno, fl, body in pages:
    if fl is None:
        kind = "NO-FLOW"
        print(f"\n=== {pno} {kind}")
        continue
    blocks = fl["blocks"]
    print(f"\n=== {pno} blocks={len(blocks)}")
    total = 0
    for i, b in enumerate(blocks):
        cls = (re.search(r'class="([^"]*)"', b) or [None, ""])[1]
        chars = len(strip_text(b))
        imgs = len(re.findall(r'<img\b', b))
        total += chars
        head = re.sub(r'\s+', ' ', strip_text(b))[:22]
        print(f"  [{i:2d}] {cls:14s} chars={chars:5d} img={imgs} est_lines={max(1,round(chars/25)):4.1f}  {head}")
    print(f"  TOTAL chars={total}  half={total//2}  est_page_lines={total/25:.0f}")
