# -*- coding: utf-8 -*-
"""只读分析 2611.pdf：
1) PyPDF2 visitor 提取每页文字坐标 -> 每栏最低文字 y（底部留白）
2) Pillow 分析 PNG -> 图片框 bbox、与文字重叠检测
输出 mm 为单位。页面 210x285mm，1pt=0.352778mm。
"""
import sys, io
import PyPDF2
from PIL import Image

PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
PNGD = r"D:\CloudyInkForge\pentium\_tmp\pdfpng"
PT2MM = 25.4 / 72.0

r = PyPDF2.PdfReader(PDF)
print("pages:", len(r.pages))

for pi, page in enumerate(r.pages):
    W = float(page.mediabox.width); H = float(page.mediabox.height)
    items = []
    def visitor(text, cm, tm, fontDict, fontSize):
        t = text.strip()
        if t:
            items.append((tm[4], tm[5], t))
    page.extract_text(visitor_text=visitor)
    # 每个文字基线 y（pt，PDF 坐标原点左下）
    if not items:
        print(f"--- pdf p{pi+1}: no text")
        continue
    ys = sorted(set(round(y, 1) for x, y, t in items), reverse=True)
    # 行分组：y 相近合并
    rows = []
    for y in ys:
        if not rows or rows[-1][0] - y > 3:
            rows.append([y, []])
        rows[-1][1].append(y)
    print(f"--- pdf p{pi+1}  ({W*PT2MM:.0f}x{H*PT2MM:.0f}mm)  rows={len(rows)}")
    # 最高与最低文字
    ymax = max(y for x, y, t in items); ymin = min(y for x, y, t in items)
    print(f"    text top={ (H-ymax)*PT2MM:.1f}mm from page top, bottom_text_y_from_top={(H-ymin)*PT2MM:.1f}mm, page bottom margin={ (H-ymin)*PT2MM:.1f}mm->285")
    # 底部三行文字内容与位置
    for x, y, t in sorted(items, key=lambda it: it[1])[:6]:
        print(f"    low text y={(H-y)*PT2MM:6.1f}mm x={x*PT2MM:6.1f}mm  {t[:18]!r}")
