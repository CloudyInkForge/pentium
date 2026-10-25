# -*- coding: utf-8 -*-
import sys, io, re, zlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")
page = reader.pages[4]
data = page.get_contents().get_data().decode('latin-1')
# 找包含 "代表当年" 的 Tj 附近算子 — CJK 在流里是十六进制或转义;先看 BT/ET 块结构样本
blocks = data.split('BT')
print("BT blocks:", len(blocks))
# 打印前 3 个含 Tm 的块的开头
cnt = 0
for b in blocks:
    if 'Tm' in b and cnt < 4:
        print("=" * 40)
        print(b[:600].strip()[:600])
        cnt += 1
