# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
MM = 72/25.4
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")
page = reader.pages[4]
def visitor(text, cm, tm, fd, fs):
    t = text.strip()
    if not t: return
    y = tm[5]/MM
    if 234 <= y <= 248:
        print(f"y={y:6.2f} x={tm[4]/MM:6.2f} | {repr(t)}")
page.extract_text(visitor_text=visitor)
