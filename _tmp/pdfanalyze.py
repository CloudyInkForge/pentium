# -*- coding: utf-8 -*-
"""综合分析 2611.pdf 排版质量（只读）：
- PyPDF2 提取文字坐标（pt->mm）
- PNG 扫描图片 bbox（大块非白区域）
- 输出：每页每栏最低文字、底部留白、图片框位置、文字与图框重叠
坐标均为“距页顶 mm”。页面 210x285。正文区：x 16~194，y 15~268.5（.page 15~268.5）。
正文可用底边（.body 内容底）= 15 + 253.5 - 5.8 - 4.2 = 258.5mm（续页），首页题头更高。
"""
import PyPDF2
from PIL import Image
import numpy as np

PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
PNGD = r"D:\CloudyInkForge\pentium\_tmp\pdfpng"
PT2MM = 25.4 / 72.0
SCALE = 2.0  # png scale vs pt
PX2MM = PT2MM / SCALE

# 文史 P16-P27 双栏: 栏 x [16,102.25],[107.75,194]；社会热点 P35-39 三栏: [16,71.67],[77.17,132.83],[138.33,194]
def cols_for(pageno_label):
    p = int(pageno_label)
    if 16 <= p <= 27:
        return [(16.0, 102.25), (107.75, 194.0)]
    return [(16.0, 71.67), (77.17, 132.83), (138.33, 194.0)]

r = PyPDF2.PdfReader(PDF)

def find_photo_bboxes(png_path):
    im = Image.open(png_path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    # 非白且有彩色（照片通常是彩色或灰阶大块）——判据：3x3 下采样后 30x30 块内方差大或颜色非黑白
    h, w, _ = a.shape
    # 灰度
    g = a.mean(axis=2)
    colored = (np.abs(a[:, :, 0] - a[:, :, 2]) > 18) | (np.abs(a[:, :, 1] - a[:, :, 2]) > 18)
    dark = g < 235
    # 图片区域: 彩色像素密度高的行x列
    from scipy import ndimage  # may not exist
    return im, colored, dark

def photo_bboxes_simple(png_path):
    """不依赖 scipy：按行列投影找彩色块"""
    im = Image.open(png_path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    colored = (np.abs(a[:, :, 0] - a[:, :, 2]) > 18) | (np.abs(a[:, :, 1] - a[:, :, 2]) > 18)
    rowsum = colored.sum(axis=1)
    colsum = colored.sum(axis=0)
    h, w = colored.shape
    bands = []
    in_b = False
    for y in range(h):
        if rowsum[y] > 40 and not in_b:
            in_b = True; y0 = y
        elif rowsum[y] <= 40 and in_b:
            in_b = False
            if y - y0 > 60:  # >10mm 高
                bands.append((y0, y))
    if in_b and h - y0 > 60:
        bands.append((y0, h))
    boxes = []
    for y0, y1 in bands:
        sub = colored[y0:y1, :]
        cs = sub.sum(axis=0)
        xs = np.where(cs > (y1 - y0) * 0.3)[0]
        if len(xs) == 0:
            continue
        # 分列
        groups = []
        s = xs[0]; p = xs[0]
        for x in xs[1:]:
            if x - p > 12:
                groups.append((s, p)); s = x
            p = x
        groups.append((s, p))
        for x0, x1 in groups:
            if x1 - x0 > 80:  # >14mm 宽
                boxes.append((x0, y0, x1, y1))
    return boxes

for pi, page in enumerate(r.pages):
    H = float(page.mediabox.height)
    items = []
    def visitor(text, cm, tm, fontDict, fontSize):
        t = text.strip()
        if t:
            items.append((tm[4] * PT2MM, (H - tm[5]) * PT2MM, t))
    page.extract_text(visitor_text=visitor)
    if not items:
        continue
    label = ""
    for x, y, t in items:
        if t.isdigit() and x > 180:
            label = t
    cols = cols_for(label or "16")
    png = f"{PNGD}\\p{pi+1:02d}.png"
    boxes = photo_bboxes_simple(png)
    print(f"=== P{label} (pdf#{pi+1}) ===")
    for ci, (x0, x1) in enumerate(cols):
        colitems = [(x, y, t) for x, y, t in items if x0 - 1 <= x < x1 and y < 260]  # 排除页脚
        if not colitems:
            print(f"  col{ci+1}: no text")
            continue
        low = max(colitems, key=lambda it: it[1])
        print(f"  col{ci+1} lowest text y={low[1]:6.1f}mm  -> body-bottom(258.5) slack={258.5-low[1]:6.1f}mm ({(258.5-low[1])/4.57:.1f}行)  {low[2][:14]!r}")
    for (bx0, by0, bx1, by1) in boxes:
        print(f"  photo bbox x {bx0*PX2MM:.1f}-{bx1*PX2MM:.1f}mm, y {by0*PX2MM:.1f}-{by1*PX2MM:.1f}mm (w{(bx1-bx0)*PX2MM:.1f} h{(by1-by0)*PX2MM:.1f})")
        # 撞图检测：文字基线落在图框内
        hit = [(x, y, t) for x, y, t in items
               if bx0*PX2MM - 2 <= x <= bx1*PX2MM + 2 and by0*PX2MM + 2 <= y <= by1*PX2MM - 1]
        for x, y, t in hit[:8]:
            print(f"      !! text-in-photo y={y:.1f} x={x:.1f} {t[:16]!r}")
        # 图注区检测（图下 0-8mm）
        cap = [(x, y, t) for x, y, t in items
               if bx0*PX2MM - 5 <= x <= bx1*PX2MM + 30 and by1*PX2MM <= y <= by1*PX2MM + 9]
        for x, y, t in cap[:3]:
            print(f"      cap? y={y:.1f} {t[:20]!r}")
