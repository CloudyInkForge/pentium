# -*- coding: utf-8 -*-
"""全刊扫描:页脚侵入 + 逐栏行当量失衡(含图块)"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
SRC = open(r"2611\2611.html", encoding="utf-8").read()
import re
starts = [m.start() for m in re.finditer(r'<div class="page[ "]', SRC)]
pages_html = [SRC[s:(starts[i+1] if i+1 < len(starts) else len(SRC))] for i, s in enumerate(starts)]
def pncol(pno):
    m = re.search(r'<div class="page([^"]*)"', pages_html[pno-1])
    cls = m.group(1) if m else ""
    if 'page-pro' in cls: return None
    if 'page-2col' in cls: return 2
    return 3
EDGES = {2:[(16.0,102.25),(107.75,194.0)], 3:[(16.0,71.67),(77.17,132.83),(138.33,194.0)]}
print("== 页脚侵入检查 (正文 8.7pt 行 y<23) ==")
for pno in range(1, 75):
    for l in LAY[str(pno)]["lines"]:
        if l["y"] < 23 and abs(l["fs"]-8.7) < 0.1:
            print(f"  P{pno:02d} y={l['y']:6.1f} x={l['x']:6.1f} | {l['text'][:36]}")
print()
print("== 逐栏行当量 (正文行 + 图块行) 与失衡 ==")
LH = 4.573
for pno in range(1, 75):
    n = pncol(pno)
    if n is None: continue
    d = LAY[str(pno)]
    edges = EDGES[n]
    cols = [[] for _ in edges]
    for l in d["lines"]:
        if not (20 < l["y"] < 265.5): continue
        x0 = l["x"]
        for ci,(a,b) in enumerate(edges):
            if a-1 <= x0 <= b+1: cols[ci].append(l); break
        else:
            for ci,(a,b) in enumerate(edges):
                x1 = x0 + l["w"]
                if a-1 <= x1 <= b+1: cols[ci].append(l); break
    # photos: 分配到 x 中心所在栏
    fills = [len(c) for c in cols]
    for im in d["images"]:
        if im["h"] < 20: continue  # 忽略小装饰
        cx = im["x"] + im["w"]/2
        for ci,(a,b) in enumerate(edges):
            if a-1 <= cx <= b+1:
                cap_lines = 2  # 图注约 2 行
                fills[ci] += round(im["h"]/LH) + cap_lines
                break
    mm = [f*LH for f in fills]
    spread = (max(fills)-min(fills)) if len(fills) > 1 else 0
    flag = " ⚠" if spread > 4 else ""
    colstr = " ".join(f"c{i+1}:{fills[i]:3d}({mm[i]:5.1f})" for i in range(n))
    print(f"P{pno:02d} {n}栏 {colstr} 差{spread}{flag}")
