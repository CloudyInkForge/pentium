# -*- coding: utf-8 -*-
"""zone/ctab 行数核算:86.25mm 栏宽,8.7pt 正文,10.5pt 小标题,10.2pt 导语"""
import sys, io, re, html as hm, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def em_len(t):
    return sum(0.55 if ord(c) < 0x2E80 else 1.0 for c in t)
def body_lines(t, col=86.25, fs=8.7, indent=2.0):
    cap = col / (fs * 0.3528)
    return math.ceil((em_len(t) + indent) / cap - 1e-9)
def plain_lines(t, col=86.25, fs=8.7):
    cap = col / (fs * 0.3528)
    return math.ceil(em_len(t) / cap - 1e-9)
def sub_lines(t, col=86.25):
    cap = col / (10.5 * 0.3528)
    return math.ceil(em_len(t) / cap - 1e-9)
def lead_lines(t, col=178.0):
    cap = col / (10.2 * 0.3528)
    return math.ceil(em_len(t) / cap - 1e-9)
# 用法: 从 stdin 读 HTML 片段,逐元素报行数
src = sys.stdin.read()
for m in re.finditer(r'<(p|h2)([^>]*)>(.*?)</\1>', src, re.S):
    tag, attrs, inner = m.groups()
    cls = re.search(r'class="([^"]*)"', attrs)
    cls = cls.group(1) if cls else ""
    t = re.sub(r'\s+', '', hm.unescape(re.sub(r'<[^>]+>', '', inner)))
    if not t: continue
    if tag == 'h2':
        n = sub_lines(t); h = n * 10.5 * 1.35 * 0.3528 + (1.2+0.8) * 0.3528 * 0  # margins below
        print(f"h2[{cls:12s}] {n}行 ({n*10.5*1.35*0.3528+2.0:.1f}mm含边距) | {t[:24]}")
    elif 'verse' in cls:
        n = plain_lines(t)
        print(f"verse      {n}行 | {t[:24]}")
    elif 'cap' in cls or 'cont' in cls and False:
        n = plain_lines(t, fs=7.5)
        print(f"cap        {n}行 | {t[:24]}")
    elif 'lead' in cls:
        n = lead_lines(t)
        print(f"lead[{cls:8s}] {n}行 ({n*10.2*1.68*0.3528:.1f}mm) | {t[:24]}")
    elif 'continued-mark' in cls:
        print(f"cont-mark  1行 3.97mm | {t[:24]}")
    elif 'attr' in cls:
        n = plain_lines(t)
        print(f"attr       {n}行 | {t[:24]}")
    else:
        n = body_lines(t)
        print(f"p  [{cls:12s}] {n}行 | {t[:24]}")
