# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"_tmp")
from colsum import page_cols
n, cols, imgs = page_cols(31)  # PRO 返回 (None, flatlines, imgs)
LAY = __import__("json").load(open(r"_tmp\layout.json", encoding="utf-8"))
ls = [l for l in LAY["31"]["lines"] if 20 < l["y"] < 265.5]
ls.sort(key=lambda l: (-l["y"], l["x"]))
for l in ls:
    col = "L" if l["x"] < 100 else "R"
    print(f"{col} y={l['y']:6.1f} x={l['x']:6.1f} | {l['text'][:44]}")
