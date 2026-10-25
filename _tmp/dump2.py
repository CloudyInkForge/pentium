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
        items.append({"x": round(tm[4]/MM,2), "y": round(tm[5]/MM,2), "fs": fs, "t": t})
    page.extract_text(visitor_text=visitor)
    out.append(items)
with open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items2.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print("dumped", sum(len(p) for p in out), "items")
