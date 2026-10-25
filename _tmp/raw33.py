# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2
PDF = r"D:\CloudyInkForge\pentium\2611\2611.pdf"
MM = 72 / 25.4
reader = PyPDF2.PdfReader(PDF)
page = reader.pages[32]  # P33
def visitor(text, cm, tm, fd, fs):
    t = text.strip()
    if not t: return
    print(f"tm=({tm[4]/MM:6.1f},{tm[5]/MM:6.1f}) cm=({cm[4]/MM:6.1f},{cm[5]/MM:6.1f}) fs={fs} | {repr(t[:60])}")
page.extract_text(visitor_text=visitor)
