# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
items = json.load(open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items.json", encoding="utf-8"))

# 页面类型:2col 页码列表(双栏),其余基础页三栏;PRO 跳过
P2COL = {4,5,8,12,13,14,15,18,22,23,24,25,26,27,28,29,34,36,37,40,46,47,49,54,62,66,67,71,74}
PRO = {2,3,6,7,10,11,16,17,20,21,30,32,38,39,44,45,52,58,59,65,70,73}

def analyze(pno, items):
    # 过滤 folio 区 (y<20) 与正文
    body = [i for i in items if 20 <= i["y"] <= 266]
    if not body: return
    ncol = 2 if pno in P2COL else 3
    cw = (178 - 5.5*(ncol-1)) / ncol
    x0 = 16
    cols = [[] for _ in range(ncol)]
    for it in body:
        rel = it["x"] - x0
        ci = int(rel // (cw + 5.5))
        if 0 <= ci < ncol: cols[ci].append(it)
        else:  # 图片说明右对齐等,归入最近的栏
            ci = min(range(ncol), key=lambda c: abs(x0 + c*(cw+5.5) + cw/2 - it["x"]))
            cols[ci].append(it)
    print(f"--- P{pno:02d} ({ncol}col) ---")
    for ci, c in enumerate(cols):
        if not c:
            print(f"  col{ci+1}: EMPTY"); continue
        ys = sorted({round(i["y"],1) for i in c}, reverse=True)
        # 聚类行 (相邻<1.5mm 视为一行)
        lines = []
        for y in ys:
            if not lines or lines[-1] - y > 1.5: lines.append(y)
        c.sort(key=lambda i: (-i["y"], i["x"]))
        top = c[0]; bot = min(c, key=lambda i: i["y"])
        print(f"  col{ci+1}: {len(lines):3d}行 y[{bot['y']:6.1f}..{max(ys):6.1f}] "
              f"首[{top['t'][:14]}] 末[{bot['t'][:14]}]")

for pno, its in enumerate(items, 1):
    if pno in PRO: continue
    analyze(pno, its)
