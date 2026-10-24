# -*- coding: utf-8 -*-
"""2611.pdf 排版质量综合分析 v2（只读）
- 文字坐标来自 PyPDF2（基线 y，距页顶 mm）
- 照片框：按已知栏带，逐行统计非白密度（照片密度高、文字密度低）
- 指标：每栏底部留白、照片框、文字行落入照片框=撞图、图注行位置
"""
import PyPDF2, re
from PIL import Image
import numpy as np

PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
PNGD = r"D:\CloudyInkForge\pentium\_tmp\pdfpng"
PT2MM = 25.4 / 72.0
PX = None  # 从 PNG 实际尺寸算
BODY_BOTTOM = 262.7          # .body 底边（续页/首页一致）
LINE = 4.57

def col_bands(label):
    p = int(label)
    if 16 <= p <= 27:
        return [(16.0, 102.25), (107.75, 194.0)]
    return [(16.0, 71.67), (77.17, 132.83), (138.33, 194.0)]

r = PyPDF2.PdfReader(PDF)
report = []
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
    bands = col_bands(label)
    im = Image.open(f"{PNGD}\\p{pi+1:02d}.png").convert("L")
    a = np.asarray(im)
    PX = 210.0 / a.shape[1]
    dark = a < 232
    h, w = dark.shape
    print(f"=== P{label} (pdf#{pi+1}) ===")
    for ci, (cx0, cx1) in enumerate(bands):
        px0, px1 = int(cx0 / PX), int(cx1 / PX)
        band = dark[:, px0:px1]
        dens = band.mean(axis=1)
        # 照片行：密度>0.5 连续 >25px(4.4mm)
        photo_rows = dens > 0.5
        segs = []
        y = 0
        while y < h:
            if photo_rows[y]:
                y0 = y
                while y < h and photo_rows[y]:
                    y += 1
                if (y - y0) * PX > 8:
                    segs.append((y0, y))
            else:
                y += 1
        # 文字
        colitems = [(x, yy, t) for x, yy, t in items if cx0 - 2 <= x < cx1 and yy < 262]
        low = max(colitems, key=lambda it: it[1]) if colitems else None
        if low:
            slack = BODY_BOTTOM - low[1]
            print(f"  col{ci+1} 最低文字 y={low[1]:6.1f}  底部余 {slack:5.1f}mm ({slack/LINE:5.1f}行)  {low[2][:12]!r}")
        else:
            print(f"  col{ci+1} 无文字")
        for (y0, y1) in segs:
            # 精确 x 范围
            sub = dark[y0:y1, px0:px1]
            colD = sub.mean(axis=0)
            xs = np.where(colD > 0.5)[0]
            if len(xs) < 20:
                continue
            bx0 = (px0 + xs.min()) * PX
            bx1 = (px0 + xs.max()) * PX
            by0, by1 = y0 * PX, y1 * PX
            print(f"  col{ci+1} 照片 x {bx0:6.1f}-{bx1:6.1f}  y {by0:6.1f}-{by1:6.1f}  (w{bx1-bx0:5.1f} h{by1-by0:5.1f})")
            # 撞图：文字基线在框内（排除图注：图框下 6mm 内且 x 接近图右缘）
            hits = [(x, yy, t) for x, yy, t in items
                    if bx0 - 1 <= x <= bx1 and by0 + 1.5 <= yy <= by1 - 0.5]
            for x, yy, t in hits[:10]:
                print(f"      !!撞图 y={yy:6.1f} x={x:6.1f} {t[:16]!r}")
            caps = [(x, yy, t) for x, yy, t in items
                    if bx0 - 4 <= x <= bx1 + 45 and by1 - 0.5 <= yy <= by1 + 7.5]
            for x, yy, t in caps[:2]:
                print(f"      cap y={yy:6.1f} {t[:22]!r}")
