# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
ls = [l for l in LAY["1"]["lines"] if 20 < l["y"] < 265.5]
ls.sort(key=lambda l: (-l["y"], l["x"]))
prev = None
for l in ls:
    print(f"y={l['y']:7.2f} x={l['x']:7.2f} fs={l['fs']:4.1f} | {l['text'][:40]}")
