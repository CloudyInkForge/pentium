# -*- coding: utf-8 -*-
"""逐栏摘要 v2:视觉行合并(同栏同y且x衔接) + 按起点x分栏"""
import sys, io, re, json
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
SRC = open(r"2611\2611.html", encoding="utf-8").read()
lines_src = SRC.split('\n')
starts = [i for i, l in enumerate(lines_src) if re.match(r'<div class="page[ "]', l)]

def est_w(t, fs):
    return sum((fs*0.3528*0.55 if ord(c) < 0x2E80 else fs*0.3528) for c in t)

def page_ncol(pno):
    seg = '\n'.join(lines_src[starts[pno-1]: starts[pno] if pno < len(starts) else len(lines_src)])
    m = re.search(r'<div class="page([^"]*)"', seg)
    cls = m.group(1) if m else ""
    if 'page-pro' in cls: return None
    if 'page-2col' in cls: return 2
    return 3

EDGES = {2:[(16.0,102.25),(107.75,194.0)], 3:[(16.0,71.67),(77.17,132.83),(138.33,194.0)]}

def page_cols(pno):
    n = page_ncol(pno)
    d = LAY[str(pno)]
    ls = [l for l in d["lines"] if 20 < l["y"] < 265.5]
    if n is None: return None, ls, d["images"]
    edges = EDGES[n]
    buckets = [[] for _ in edges]
    for l in ls:
        x0 = l["x"]
        best = -1
        for ci,(a,b) in enumerate(edges):
            if a-1.0 <= x0 <= b+1.0: best = ci; break
        if best < 0:  # 右对齐元素(图注/落款):按估宽右端归属
            x1 = x0 + est_w(l["text"], l["fs"])
            for ci,(a,b) in enumerate(edges):
                if a-1.0 <= x1 <= b+1.0: best = ci; break
        if best >= 0: buckets[best].append(l)
    # 合并同栏同 y 且 x 衔接的片段
    merged = []
    for ci, c in enumerate(buckets):
        byy = {}
        for l in c: byy.setdefault(round(l["y"],1), []).append(l)
        col_lines = []
        for y, frags in byy.items():
            frags.sort(key=lambda l: l["x"])
            cur = None
            for f in frags:
                if cur is None: cur = dict(f)
                elif f["x"] - (cur["x"] + est_w(cur["text"], cur["fs"])) <= 3.0:
                    cur["text"] += f["text"]
                else:
                    col_lines.append(cur); cur = dict(f)
            if cur: col_lines.append(cur)
        col_lines.sort(key=lambda l: -l["y"])
        merged.append(col_lines)
    return n, merged, d["images"]

if __name__ == "__main__":
    show_text = "-t" in sys.argv
    for pno in range(1, 75):
        n, cols, imgs = page_cols(pno)
        if n is None:
            print(f"P{pno:02d} PRO lines={len(cols)} imgs={len(imgs)}")
            continue
        parts = []
        for ci, c in enumerate(cols):
            if not c: parts.append(f"c{ci+1}:—"); continue
            parts.append(f"c{ci+1}:{len(c):3d}[{c[-1]['y']:5.1f}]")
        print(f"P{pno:02d} {n}栏 " + " ".join(parts) + f"  imgs={len(imgs)}")
        if show_text:
            for ci, c in enumerate(cols):
                for l in c:
                    print(f"   c{ci+1} y={l['y']:6.1f} x={l['x']:6.1f} | {l['text'][:38]}")
