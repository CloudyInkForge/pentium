# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = open(r"D:\CloudyInkForge\pentium\2611\2611.html", encoding="utf-8").read()
lines = SRC.split('\n')
starts = []
for ln, line in enumerate(lines, 1):
    if re.match(r'<div class="page[ "]', line):
        starts.append(ln)
for i, s in enumerate(starts):
    e = starts[i+1]-1 if i+1 < len(starts) else len(lines)
    print(f"P{i+1:02d}: lines {s}-{e} ({e-s+1})")
