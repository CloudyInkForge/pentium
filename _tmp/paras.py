# -*- coding: utf-8 -*-
import sys, io, re, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import html as LH

doc = LH.parse(r"D:\CloudyInkForge\pentium\2611\2611.html")
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]
CPL = {8.7:18.14, 9.2:17.14, 9.3:16.96, 9.4:16.79, 9.5:16.53}
def fs_of(p):
    st = p.get("style") or ""
    m = re.search(r'--body-font:\s*([\d.]+)pt', st)
    return float(m.group(1)) if m else 8.7

for pno in [int(x) for x in sys.argv[1:]]:
    p = pages[pno-1]
    cls = (p.get("class") or "").split()
    t = "pro" if "page-pro" in cls else ("2col" if "page-2col" in cls else "3col")
    body = [e for e in p.iter("div") if "body" in (e.get("class") or "").split()]
    fs = fs_of(body[0]) if body else 8.7
    cpl = CPL.get(fs, 18.14)
    ncol = 2 if t=="2col" else 3
    print(f"== P{pno:02d} [{t}] fs={fs} cpl={cpl}")
    if not body: continue
    ci = 0
    for ch in body[0]:
        c = (ch.get("class") or "").split()
        if "cbrk" in c: ci += 1
        if ch.tag == "p":
            txt = ch.text_content()
            n = math.ceil((len(txt)+2)/cpl) if not any(x in c for x in ("cont","verse","attr","cap")) else math.ceil(len(txt)/cpl)
            mark = "CBRK" if "cbrk" in c else ("cont" if "cont" in c else "")
            print(f"  c{ci+1} p[{mark}] ~{n}L {len(txt)}ch | {txt[:16]}...{txt[-10:]}")
        elif ch.tag == "div" and "photo-block" in c:
            m = re.search(r'--ph-h:\s*([\d.]+)', ch.get("style") or "")
            print(f"  c{ci+1} IMG {m.group(1) if m else '?'}mm")
        elif ch.tag == "h2":
            print(f"  c{ci+1} SUB | {ch.text_content()[:16]}")
        elif ch.tag == "div" and "gap" in c:
            print(f"  c{ci+1} GAP")
