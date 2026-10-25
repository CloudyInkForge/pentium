# -*- coding: utf-8 -*-
"""按页 dump layout.json 的视觉行"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
pno = int(sys.argv[1])
d = LAY[str(pno)]
ls = sorted(d["lines"], key=lambda l: (-l["y"], l["x"]))
for l in ls:
    print(f"y={l['y']:7.1f} x={l['x']:6.1f} fs={l['fs']:4.1f} | {l['text'][:64]}")
