# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import html as LH

doc = LH.parse(r"D:\CloudyInkForge\pentium\2611\2611.html")
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]
print("total page divs:", len(pages))
for i, p in enumerate(pages, 1):
    cls = p.get("class") or ""
    body = [e for e in p.iter("div") if "body" in (e.get("class") or "").split()]
    cbrks = [e for e in p.iter() if "cbrk" in (e.get("class") or "").split()]
    blocks = [e for e in p.iter("div") if "photo-block" in (e.get("class") or "").split()]
    folio = [e for e in p.iter("td") if "page-no" in (e.get("class") or "")]
    no = folio[0].text if folio else "?"
    bcls = body[0].get("class") if body else ""
    phs = []
    for b in blocks:
        m = re.search(r'--ph-h:\s*([\d.]+)mm', b.get("style") or "")
        phs.append(m.group(1) if m else "?")
    print(f"idx{i:02d} no={no} [{cls}] body[{bcls}] cbrk={len(cbrks)} blk={len(blocks)} ph_h={phs}")
