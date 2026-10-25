# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
MM = 72 / 25.4
reader = PyPDF2.PdfReader(PDF)
out = []
for pno in range(len(reader.pages)):
    page = reader.pages[pno]
    items = []
    def visitor(text, cm, tm, fd, fs):
        t = text.strip()
        if not t: return
        items.append({"x": round(tm[4]/MM,2), "y": round(tm[5]/MM,2), "t": t})
    page.extract_text(visitor_text=visitor)
    out.append(items)
with open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
# 摘要：每页最底文本行 y 与其文本
for pno, items in enumerate(out):
    if not items:
        print(f"P{pno+1:02d} EMPTY")
        continue
    low = max(items, key=lambda i: i["y"])
    txt = low["t"][:28].replace("\n"," ")
    print(f"P{pno+1:02d} lowest y={low['y']:7.1f} x={low['x']:6.1f} | {txt}")
