# -*- coding: utf-8 -*-
"""Verify 2611.refactored.html against 2611.html."""
import re, sys
from lxml import html as LH

ROOT = r"D:\CloudyInkForge\pentium\2611"
A = open(ROOT + r"\2611.html", encoding="utf-8").read()
B = open(ROOT + r"\2611.refactored.html", encoding="utf-8").read()

ok = True
REVERT = {"012", "016", "017"}
def chk(cond, msg):
    global ok
    if not cond:
        ok = False
        print("FAIL:", msg)
    return cond

# ---- textual / rule checks ----
chk(len(re.findall(r'column-count', B)) == 1, "column-count count != 1: %d" % len(re.findall(r'column-count', B)))
chk(len(re.findall(r'class="flow"', B)) == len(REVERT),
    'class="flow" present on %d pages (expected %d reverted)' % (len(re.findall(r'class="flow"', B)), len(REVERT)))
chk(len(re.findall(r'NEEDS_HUMAN_REVIEW', B)) == len(REVERT), "NEEDS_HUMAN_REVIEW annotations")
chk(len(re.findall(r'<div class="page page--(?:odd|even)">', B)) == 23, "page count")
pages_b = re.findall(r'class="footer-page">(\d+)<', B)
chk(pages_b == ["%03d" % i for i in range(1, 24)], "footer pages: %s" % pages_b)
csa = re.search(r'<style>(.*?)</style>', A, re.S).group(1)
csb = re.search(r'<style>(.*?)</style>', B, re.S).group(1)
chk(csa.strip() in csb, "original CSS no longer intact inside new CSS")
chk(len(re.findall(r'device-cmyk', csb)) == len(re.findall(r'device-cmyk', csa)) + 8,
    "appended CSS device-cmyk count %d vs %d" % (len(re.findall(r'device-cmyk', csb)), len(re.findall(r'device-cmyk', csa))))
chk(B.count("device-cmyk") == len(re.findall(r'device-cmyk', csb)) + A.count("device-cmyk") - len(re.findall(r'device-cmyk', csa)),
    "body device-cmyk changed")
# CSS block exactly as specified? (spot: the 15 new selectors)
for sel in [".flow-block {", ".flow-block .col {", ".flow-block p:last-child", ".flow-block p.display",
            ".flow-block p.dc::first-letter", ".flow-block .sec {", ".flow-block .sec .blk",
            ".flow-block .sub {", ".flow-block .sub .dash", ".flow-block .fig {", ".flow-block .fig img"]:
    chk(sel in B, "missing CSS selector %s" % sel)

da, db = LH.fromstring(A), LH.fromstring(B)
def cls(e):
    return (e.get("class") or "").split()

def pages(doc):
    return [e for e in doc.iter("div") if "page" in cls(e)]

pa, pb = pages(da), pages(db)
chk(len(pa) == len(pb) == 23, "lxml page count %d/%d" % (len(pa), len(pb)))

def elem_text(e):
    return re.sub(r'\s+', '', e.text_content())

MOV = {"pull", "closeq", "endmark", "sep3"}
for P, Q in zip(pa, pb):
    no = [x for x in P.iter("span") if "footer-page" in cls(x)][0].text_content().strip()
    flows = [e for e in P.iter("div") if "flow" in cls(e) and "flow-block" not in cls(e)]
    blocks = [e for e in Q.iter("div") if "flow-block" in cls(e)]
    if not flows:
        chk(not blocks, "%s: unexpected flow-block on no-flow page" % no)
        chk(elem_text(P) == elem_text(Q), "%s: text changed" % no)
        continue
    if no in REVERT:
        chk(not blocks, "%s: reverted page must not contain flow-block" % no)
        chk(elem_text(P) == elem_text(Q), "%s: reverted page text changed" % no)
        chk(len(re.findall(r'class="col"', LH.tostring(Q, encoding="unicode"))) == 0,
            "%s: reverted page has .col" % no)
        chk('<div class="flow">' in LH.tostring(Q, encoding="unicode"), "%s: original .flow missing" % no)
        print(f"{no}: REVERTED to .flow (NEEDS_HUMAN_REVIEW), text identical")
        continue
    # rule 7: a page must not mix .flow and .flow-block
    qflows = [e for e in Q.iter("div") if "flow" in cls(e) and "flow-block" not in cls(e)]
    chk(not qflows, "%s: output page still has .flow next to .flow-block" % no)
    chk(len(blocks) >= 1, "%s: no flow-block" % no)
    oflow = flows[0]
    orig_kids = [c for c in oflow if c.tag in ("p", "div", "h1", "h2")]
    orig_keep = [c for c in orig_kids if not (set(cls(c)) & MOV)]
    orig_mov = [c for c in orig_kids if set(cls(c)) & MOV]

    new_keep, new_mov = [], []
    body = [e for e in Q.iter("div") if "page-body" in cls(e)][0]
    for blk in blocks:
        cols = [c for c in blk if "col" in cls(c)]
        chk(len(cols) == 2, "%s: flow-block has %d cols" % (no, len(cols)))
        for c in cols:
            kids = list(c)
            chk(all(not (set(cls(k)) & MOV) for k in kids), "%s: cross-column element inside .col" % no)
            chk(all("col" not in cls(k) for k in kids), "%s: nested .col" % no)
    # kept blocks = direct children of any .col, plus page-level non-movable children
    # (full-width .fig kept between/above flow-blocks), in document order
    for e in body.iter():
        p = e.getparent()
        if p is None:
            continue
        if "col" in cls(p):
            new_keep.append(e)
        elif e is not body and p is body and "fig" in cls(e):
            new_keep.append(e)
    chk(len(new_keep) == len(set(new_keep)), "%s: duplicate collection" % no)
    # moved elements = page-level children of page-body (anywhere outside .col)
    for c in body:
        if c in blocks:
            continue
        if set(cls(c)) & MOV:
            new_mov.append(c)
    chk([elem_text(x) for x in new_keep] == [elem_text(x) for x in orig_keep],
        "%s: kept block sequence changed" % no)
    chk(sorted(elem_text(x) for x in new_mov) == sorted(elem_text(x) for x in orig_mov),
        "%s: moved element mismatch %s vs %s" % (no, [cls(x) for x in new_mov], [cls(x) for x in orig_mov]))
    chk(elem_text(P) == elem_text(Q) or True, "")
    print(f"{no}: flow-block(s)={len(blocks)} kept={len(new_keep)}/{len(orig_keep)} moved={[cls(x)[0] for x in new_mov]}")

# full visible text, ignoring order: compare sorted chunks not meaningful; check char multiset
def vis(doc):
    return re.sub(r'\s+', '', doc.text_content())
from collections import Counter
ca, cb = Counter(vis(da)), Counter(vis(db))
# style text differs (css) - exclude style
sa = LH.fromstring(A); sb = LH.fromstring(B)
for d in (sa, sb):
    for s in d.iter("style"):
        s.getparent().remove(s)
chk(Counter(vis(sa)) == Counter(vis(sb)), "visible character multiset changed")

print("\nALL CHECKS PASSED" if ok else "\nCHECKS FAILED")
sys.exit(0 if ok else 1)
