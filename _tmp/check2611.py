# -*- coding: utf-8 -*-
# 只读体检：逐页提取文本与坐标，按栏分桶，报告每栏最底一行位置
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2

PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
MM = 72 / 25.4
reader = PyPDF2.PdfReader(PDF)
print("pages:", len(reader.pages))
pw = float(reader.pages[0].mediabox.width); ph = float(reader.pages[0].mediabox.height)
print("page size pt:", pw, ph, "mm:", round(pw/MM,1), round(ph/MM,1))

for pno in range(len(reader.pages)):
    page = reader.pages[pno]
    items = []  # (x_mm, y_mm, text)
    def visitor(text, cm, tm, fd, fs):
        t = text.strip()
        if not t: return
        x = tm[4]; y = tm[5]
        items.append((x/MM, y/MM, t))
    try:
        page.extract_text(visitor_text=visitor)
    except Exception as e:
        print(pno+1, "ERR", e); continue
    if not items:
        print(f"P{pno+1:02d} NO-TEXT"); continue
    # 按栏分桶：基础页版心 16..194mm（三栏 55.67+5.5*2）；PRO 全出血
    # 用聚类：把 x 排序后按间隙>20mm 分组
    xs = sorted(set(round(x,0) for x,y,t in items))
    print(f"P{pno+1:02d} items={len(items)}")
