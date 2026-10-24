# -*- coding: utf-8 -*-
"""提取 PDF 每页：行距、每栏首行/末行文字 -> 推导分栏填充规则"""
import PyPDF2, re
from collections import Counter

PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
PT2MM = 25.4 / 72.0
r = PyPDF2.PdfReader(PDF)

def cols_for(label):
    p = int(label)
    if 16 <= p <= 27:
        return [(16.0, 102.25), (107.75, 194.0)]
    return [(16.0, 71.67), (77.17, 132.83), (138.33, 194.0)]

pitches = Counter()
for pi, page in enumerate(r.pages):
    H = float(page.mediabox.height)
    items = []
    def visitor(text, cm, tm, fontDict, fontSize):
        t = text.strip()
        if t:
            items.append((tm[4] * PT2MM, (H - tm[5]) * PT2MM, t))
    page.extract_text(visitor_text=visitor)
    label = "16"
    for x, y, t in items:
        if re.fullmatch(r"\d{2}", t) and x > 185 and 15 < y < 285:
            label = t
    bands = cols_for(label)
    print(f"=== P{label} ===")
    for ci, (x0, x1) in enumerate(bands):
        col = sorted([(y, x, t) for x, y, t in items if x0 - 2 <= x < x1 and y < 262])
        if not col:
            print(f"  col{ci+1}: empty"); continue
        # 行距
        ys = sorted(set(round(y, 2) for y, x, t in col))
        for a, b in zip(ys, ys[1:]):
            d = round(b - a, 2)
            if 3.5 < d < 6:
                pitches[round(d, 1)] += 1
        first = col[0]; last = col[-1]
        print(f"  col{ci+1} 首行 y={first[0]:6.1f} {first[2][:20]!r}")
        print(f"  col{ci+1} 末行 y={last[0]:6.1f} {last[2][:20]!r}")
print("\n行距分布:", pitches.most_common(6))
