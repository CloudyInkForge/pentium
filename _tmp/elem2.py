# -*- coding: utf-8 -*-
"""元素级丢失核对 v2:HTML 文本节点 vs 当前 layout.json 视觉行"""
import sys, io, re, json, html as hm
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
SRC = open(r"2611\2611.html", encoding="utf-8").read()
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
starts = [m.start() for m in re.finditer(r'<div class="page[ "]', SRC)]
pages_html = [SRC[s:(starts[i+1] if i+1 < len(starts) else len(SRC))] for i, s in enumerate(starts)]
def norm(t):
    return re.sub(r'[\s\u00a0]+', '', t)
bad = 0
for idx, ph in enumerate(pages_html):
    pno = idx + 1
    ph2 = re.sub(r'<!--.*?-->', '', ph, flags=re.S)
    ph2 = re.sub(r'<style.*?</style>', '', ph2, flags=re.S)
    nodes = re.findall(r'>([^<>]+)<', ph2)
    pt = norm(''.join(l["text"] for l in LAY[str(pno)]["lines"]))
    lost = []
    for n in nodes:
        t = norm(hm.unescape(n))
        if len(t) < 2: continue
        if not re.search(r'[\u4e00-\u9fffA-Za-z0-9]', t): continue
        if t not in pt:
            lost.append(t)
    if lost:
        bad += len(lost)
        print(f"P{pno:02d} 丢失 {len(lost)} 个文本节点:")
        for t in lost[:12]:
            print(f"   [{len(t):3d}字] {t[:58]}")
        if len(lost) > 12: print(f"   ...共 {len(lost)} 个")
print(f"\n总丢失节点: {bad}")
