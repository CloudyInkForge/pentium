# -*- coding: utf-8 -*-
"""Enumerate all valid cuts per page (conservative metric) and compare with chosen cut."""
import re, sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report as R
from lxml import html as LH

A = open(os.path.join(R.ROOT, "2611.html"), encoding="utf-8").read()
doc = LH.fromstring(A)
MOV = {"pull", "closeq", "endmark", "sep3"}
APPLIED = {"002": 10, "003": 9, "004": 4, "006": 2, "007": 2, "008": 3, "009": 1, "011": 6,
           "012": 6, "013": 3, "014": 4, "015": 3, "016": 4, "017": 6, "019": 2, "020": 2,
           "021": 5, "022": 5, "023": 4}
FIGTOP = {"023", "022"}
print(f"{'pg':4s} {'avail':>6s} {'chosen':>12s} {'best':>14s}  note")
for P in R.pages(doc):
    no = [x for x in P.iter("span") if "footer-page" in R.cls(x)][0].text_content().strip()
    body = [e for e in P.iter("div") if "page-body" in R.cls(e)][0]
    flows = [e for e in body if "flow" in R.cls(e)]
    if not flows:
        continue
    op = sum(R.blk_h(c) for c in body if "op-head" in R.cls(c))
    fig = sum(R.blk_h(c) for c in body if "fig" in R.cls(c))
    kids = [c for c in flows[0] if c.tag in ("p", "div", "h1")]
    trail = sum(R.blk_h(c) for c in kids if set(R.cls(c)) & MOV)
    avail = R.BODY - op - fig - trail
    kept = [c for c in kids if not (set(R.cls(c)) & MOV)]
    if no in FIGTOP and "fig" in R.cls(kept[0]):
        kept = kept[1:]
    hs = [R.blk_h(c) for c in kept]
    tot = sum(hs)
    cands = []
    for k in range(1, len(kept)):
        L = sum(hs[:k]); Rr = tot - L
        last = R.cls(kept[k - 1])
        bad = []
        if "sec" in last or "sub" in last or "op-head" in last:
            bad.append("ends-heading")
        fits = L <= avail and Rr <= avail
        cands.append((abs(L - Rr), k, L, Rr, fits, bad))
    chosen = APPLIED[no]
    c = [x for x in cands if x[1] == chosen][0]
    fitc = sorted([x for x in cands if x[4] and not x[5]])
    best = fitc[0] if fitc else None
    note = ""
    if best and best[0] + 3 < c[0]:
        note = "BETTER cut=%d  L %.1f R %.1f  diff %.1f" % (best[1], best[2], best[3], best[0])
    print(f"{no:4s} {avail:6.1f} cut{c[1]:2d} {c[2]:5.1f}/{c[3]:5.1f} "
          f"{('%d' % best[1]) if best else '-':>4s}  {note}")
