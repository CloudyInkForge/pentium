# -*- coding: utf-8 -*-
import sys, io, json, re, html as hm
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = open(r"D:\CloudyInkForge\pentium\2611\2611.html", encoding="utf-8").read()
items = json.load(open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items.json", encoding="utf-8"))
starts = [m.start() for m in re.finditer(r'<div class="page[ "]', SRC)]
pages_html = [SRC[s:(starts[i+1] if i+1 < len(starts) else len(SRC))] for i, s in enumerate(starts)]

def norm(t):
    return re.sub(r'[\s\u00a0]+', '', t)

report = {}
for idx, ph in enumerate(pages_html):
    ph2 = re.sub(r'<!--.*?-->', '', ph, flags=re.S)
    ph2 = re.sub(r'<style.*?</style>', '', ph2, flags=re.S)
    # 文本节点:标签间内容
    nodes = re.findall(r'>([^<>]+)<', ph2)
    pt = norm(''.join(i["t"] for i in items[idx]))
    lost = []
    for n in nodes:
        t = norm(hm.unescape(n))
        if len(t) < 2: continue
        # 跳过纯符号
        if not re.search(r'[\u4e00-\u9fffA-Za-z0-9]', t): continue
        if t not in pt:
            lost.append(t)
    if lost:
        report[idx+1] = lost
for p, lost in sorted(report.items()):
    print(f"P{p:02d} 丢失 {len(lost)} 个文本节点:")
    for t in lost:
        print(f"     [{len(t)}字] {t[:56]}")
