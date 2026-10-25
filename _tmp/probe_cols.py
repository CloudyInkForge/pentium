# -*- coding: utf-8 -*-
# 探针：各 PDF 页面的文本 x 聚类，判断多栏是否真实分栏
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2

MM = 72 / 25.4

def probe(pdf, pages):
    r = PyPDF2.PdfReader(pdf)
    print("=", pdf.split("\\")[-1], "pages:", len(r.pages))
    for pno in pages:
        page = r.pages[pno]
        ph = float(page.mediabox.height)
        xs = {}
        ys = []
        def visitor(text, cm, tm, fd, fs):
            t = text.strip()
            if not t: return
            x = round(tm[4] / MM)
            y_top = round((ph - tm[5]) / MM)
            xs[x] = xs.get(x, 0) + 1
            ys.append(y_top)
        page.extract_text(visitor_text=visitor)
        # 聚类 x（间隙>12mm 分断）
        keys = sorted(xs)
        clusters = []
        for x in keys:
            if not clusters or x - clusters[-1][-1] > 12:
                clusters.append([x])
            else:
                clusters[-1].append(x)
        print(f"  P{pno+1}: x簇 " + " | ".join(f"{c[0]}-{c[-1]}({sum(xs[x] for x in c)})" for c in clusters) + f"  y[{min(ys)}..{max(ys)}]")

probe(r"D:\CloudyInkForge\pentium\template\PRO\pro-1.pdf", [1])       # 旧pro-1 右页 .cols
probe(r"D:\CloudyInkForge\pentium\template\page+.pdf", [0, 1])        # 基础双栏 .body（定高）
probe(r"D:\CloudyInkForge\pentium\template\page+++.pdf", [0])         # 基础三栏 .body（定高）
probe(r"D:\CloudyInkForge\pentium\2611\2611.pdf", [0, 4, 5])          # 封面 / P01 时政三栏 / P02 pro-1 右页
