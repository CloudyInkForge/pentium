# -*- coding: utf-8 -*-
"""从 PDF 重建视觉行:按基线聚类,x 间隙拆行,输出每栏行序列"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
items = json.load(open(r"_tmp\pdf_items2.json", encoding="utf-8"))

def char_w(ch, fs):
    o = ord(ch)
    if o < 0x2E80:  # ascii/latin
        return fs * 0.3528 * (0.30 if ch in ' .,\'’‘"“”!i' else 0.55)
    return fs * 0.3528  # CJK 全角

def item_w(it):
    fs = it["fs"] or 8.7
    return sum(char_w(c, fs) for c in it["t"])

def vlines_for_page(pno, col_edges):
    its = [i for i in items[pno-1] if 20 <= i["y"] <= 272]
    by_y = {}
    for i in its:
        key = round(i["y"] * 2) / 2  # 0.5mm 聚类
        by_y.setdefault(key, []).append(i)
    lines = []
    for y in sorted(by_y, reverse=True):
        runs = sorted(by_y[y], key=lambda i: i["x"])
        cur = None
        for r in runs:
            if cur is None:
                cur = {"y": y, "x0": r["x"], "x1": r["x"] + item_w(r), "t": r["t"], "fs": r["fs"]}
            elif r["x"] - cur["x1"] > 2.5:
                lines.append(cur); cur = {"y": y, "x0": r["x"], "x1": r["x"] + item_w(r), "t": r["t"], "fs": r["fs"]}
            else:
                cur["t"] += r["t"]; cur["x1"] = r["x"] + item_w(r)
        if cur: lines.append(cur)
    # 分栏
    for ln in lines:
        best, bd = None, 1e9
        for ci, (a, b) in enumerate(col_edges):
            cx = (max(ln["x0"], a) + min(ln["x1"], b)) / 2
            if a - 1 <= ln["x1"] and ln["x0"] <= b + 1:
                d = abs(cx - (a + b) / 2)
                if d < bd: bd, best = d, ci
        ln["col"] = best if best is not None else -1
    return lines

if __name__ == "__main__":
    import sys
    pno = int(sys.argv[1]); ncol = int(sys.argv[2])
    if ncol == 3: edges = [(16,71.67),(77.17,132.83),(138.33,194)]
    elif ncol == 2: edges = [(16,102.25),(107.75,194)]
    else: edges = [(16,194)]
    for ln in vlines_for_page(pno, edges):
        print(f"c{ln['col']} y={ln['y']:6.1f} x={ln['x0']:6.1f} fs={ln['fs']} | {ln['t'][:46]}")
