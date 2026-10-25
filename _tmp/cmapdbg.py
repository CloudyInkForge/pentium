# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")
page = reader.pages[4]
fonts = page["/Resources"].get("/Font", {})
for fname in fonts:
    f = fonts[fname].get_object()
    tu = f.get("/ToUnicode")
    sub = f.get("/Subtype")
    bf = f.get("/BaseFont")
    print(fname, sub, bf, "ToUnicode:", "yes" if tu else "NO")
    if tu:
        data = tu.get_object().get_data().decode('latin-1')
        nchar = len(re.findall(r'beginbfchar', data))
        nrange = len(re.findall(r'beginbfrange', data))
        print("   bfchar:", nchar, "bfrange:", nrange, "len:", len(data))
        # 样本
        m = re.search(r'beginbfchar\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', data)
        print("   sample:", m.groups() if m else None)
        # 检查范围格式变体
        m2 = re.search(r'beginbfrange(.{0,120})', data, re.S)
        print("   range sample:", repr(m2.group(1)[:100]) if m2 else None)
