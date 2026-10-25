# -*- coding: utf-8 -*-
"""逐页逐栏填充地图:每栏最底内容 y、距正文区底(21.8mm)的余量(行)"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\CloudyInkForge\pentium\_tmp")
import cstream

MM = 72/25.4
BODY_BOT = 21.8
LINE = 4.57
IMG = re.compile(r'q\s+([\d.]+)\s+0\s+0\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+cm\s*/(I\w+|\w+)\s+Do', re.S)

def images(pno):
    page = cstream.reader.pages[pno-1]
    data = page.get_contents().get_data().decode('latin-1')
    imgs = []
    for m in IMG.finditer(data):
        w,h,x,y = float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4))
        imgs.append({"x":round(x/MM,1),"y":round(y/MM,1),"w":round(w/MM,1),"h":round(h/MM,1)})
    return imgs

def col_edges():
    return [(16.0,71.67),(77.17,132.83),(138.33,194.0)]

out = {}
for pno in range(1, 75):
    lines, _ = cstream.parse_page(pno)
    imgs = images(pno)
    body = [l for l in lines if 21.0 < l["y"] < 272 and l["fs"] >= 6.0]
    cols = {0:[],1:[],2:[]}
    for l in body:
        x0, fs = l["x"], l["fs"]
        w = 0.0
        for ch in l["text"]:
            w += fs*0.3528*(0.5 if ord(ch)<0x2E80 else 1.0)
        x1 = x0 + w
        best, bd = -1, 1e9
        for ci,(a,b) in enumerate(col_edges()):
            mid=(max(x0,a)+min(x1,b))/2
            if x1>=a-1 and x0<=b+1:
                d=abs(mid-(a+b)/2)
                if d<bd: bd,best=d,ci
        if best>=0: cols[best].append(l)
    rep={}
    for ci,ls in cols.items():
        if not ls:
            rep[ci]={"n":0,"bot":None,"freeLines":None}
            continue
        bot=max(l["y"] for l in ls)
        rep[ci]={"n":len(ls),"bot":round(bot,1),"freeLines":round((bot-BODY_BOT)/LINE,1)}
    out[pno]={"cols":rep,"imgs":imgs}
    ib = " I:" + ",".join(f"y{i['y']:.0f}h{i['h']:.0f}" for i in imgs) if imgs else ""
    s=" ".join(f"c{ci+1}[n{r['n']:2d},bot{r['bot'] if r['bot'] is not None else -1:>5.1f},free{r['freeLines'] if r['freeLines'] is not None else -1:>5.1f}L]" for ci,r in rep.items())
    print(f"P{pno:02d} {s}{ib}")
json.dump(out, open(r"_tmp\fillmap.json","w",encoding="utf-8"), ensure_ascii=False)
