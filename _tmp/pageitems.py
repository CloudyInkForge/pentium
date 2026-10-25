# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
items = json.load(open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items.json", encoding="utf-8"))
pno = int(sys.argv[1])
for it in sorted(items[pno-1], key=lambda i: (-i["y"], i["x"])):
    print(f"y={it['y']:7.1f} x={it['x']:6.1f} | {it['t'][:52]}")
