# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")
t = reader.pages[32].extract_text()
for i, ln in enumerate(t.split('\n')):
    print(f"{i:3d} [{len(ln):3d}] {ln[:64]}")
