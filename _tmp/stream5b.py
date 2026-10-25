# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")
page = reader.pages[4]
data = page.get_contents().get_data().decode('latin-1')
blocks = data.split('BT')
for i, b in enumerate(blocks[1:5], 1):
    print(f"===== BT block {i} ({len(b)} chars) =====")
    print(b[:900].strip())
    print()
