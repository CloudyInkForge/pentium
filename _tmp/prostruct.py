# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = open(r"2611\2611.html", encoding="utf-8").read()
lines = SRC.split('\n')
starts = []
for ln, line in enumerate(lines, 1):
    if re.match(r'<div class="page[ "]', line):
        starts.append(ln)
PRO_TEXT = [3,31,33,45,53,59,10,16,20,64,72,11,17,21,65,73,70,71]
for p in PRO_TEXT:
    s = starts[p-1]
    e = starts[p] if p < len(starts) else len(lines)
    seg = '\n'.join(lines[s-1:e-1])
    print(f"== P{p:02d} ==")
    # content/zone 块及其内部子元素
    for zname in ('content','zone-l','zone-r','zone-t','zone-r2'):
        m = re.search(r'<div class="' + zname + r'[^"]*">\n(.*?)(?:\n  </div>|\n  <div class="folio")', seg, re.S)
        if not m: continue
        kids = re.findall(r'^\s{2,6}<(\w+)(?: class="([^"]*)")?[^>]*', m.group(1), re.M)
        out = []
        for a,b in kids[:16]:
            if a=='div' and b: out.append(b.split()[0])
            elif a=='div': out.append('div')
            else: out.append(a + ('.'+b if b else ''))
        print(f"   {zname}: {out}")
