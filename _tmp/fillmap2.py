# -*- coding: utf-8 -*-
"""逐页逐栏核算 v2:按页面类型定栏界;free=每栏最底内容到正文区底的余量"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\CloudyInkForge\pentium\_tmp")
import cstream
from lxml import html as LH

MM = 72/25.4
BODY_BOT = 21.8
LINE = 4.57
IMG = re.compile(r'q\s+([\d.]+)\s+0\s+0\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+cm\s*/(I\w+|\w+)\s+Do', re.S)

doc = LH.parse(r"D:\CloudyInkForge\pentium\2611\2611.html")
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]
ptype = {}
for i, p in enumerate(pages, 1):
    cls = (p.get("class") or "").split()
    t = "pro" if "page-pro" in cls else ("2col" if "page-2col" in cls else "3col")
    ptype[i] = t

def images(pno):
    page = cstream.reader.pages[pno-1]
    data = page.get_contents().get_data().decode('latin-1')
    imgs = []
    for m in IMG.finditer(data):
        w,h,x,y = float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4))
        imgs.append({"x":x/MM,"y":y/MM,"w":w/MM,"h":h/MM})
    return imgs

def edges(t):
    if t=="3col": return [(16.0,71.67),(77.17,132.83),(138.33,194.0)]
    if t=="2col": return [(16.0,102.25),(107.75,194.0)]
    return [(16.0,194.0)]

out={}
for pno in range(1, 75):
    t = ptype[pno]
    lines,_ = cstream.parse_page(pno)
    imgs = [i for i in images(pno) if i["w"]<200]  # 排除整页出血底图
    body = [l for l in lines if l["y"]>BODY_BOT-0.2 and l["y"]<272 and l["fs"]>=6.0]
    es = edges(t)
    cols=[{"lines":[],"imgs":[]} for _ in es]
    for l in body:
        x0,fs=l["x"],l["fs"]
        w=sum(fs*0.3528*(0.5 if ord(ch)<0x2E80 else 1.0) for ch in l["text"])
        x1=x0+w
        best,bd=-1,1e9
        for ci,(a,b) in enumerate(es):
            if t=="2col" or t=="3col":
                mid=(max(x0,a)+min(x1,b))/2
                if x1>=a-1.5 and x0<=b+1.5:
                    d=abs(mid-(a+b)/2)
                    if d<bd: bd,best=d,ci
            else:
                d=abs((x0+x1)/2-105)
                if d<bd: bd,best=d,0
        if best>=0 and best<len(cols): cols[best]["lines"].append(l)
    for im in imgs:
        cx = im["x"]+im["w"]/2
        for ci,(a,b) in enumerate(es):
            if a-1<=cx<=b+1:
                cols[ci]["imgs"].append(im); break
    rep=[]
    for c in cols:
        ys=[l["y"] for l in c["lines"]]
        iy=[i["y"] for i in c["imgs"]]
        bot=min(ys+iy) if (ys or iy) else None
        n=len(c["lines"])
        # 估每栏文本行数(合并同一 y 的碎片)
        ny=len(set(round(y,1) for y in ys))
        rep.append({"n":n,"ny":ny,"bot":round(bot,1) if bot else None,
                    "freeL":round((bot-BODY_BOT)/LINE,1) if bot else None})
    out[pno]={"type":t,"cols":rep,
              "imgs":[{k:round(v,1) for k,v in i.items()} for i in imgs]}
    s=" ".join(f"c{i+1}[L{n['ny']:2d},bot{n['bot'] if n['bot'] is not None else -1:>5.1f},free{n['freeL'] if n['freeL'] is not None else -1:>5.1f}]" for i,n in enumerate(rep))
    ims=" I:"+",".join(f"({i['x']:.0f},{i['y']:.0f}+{i['h']:.0f})" for i in out[pno]["imgs"]) if imgs else ""
    print(f"P{pno:02d}[{t}] {s}{ims}")
json.dump(out,open(r"_tmp\fillmap2.json","w",encoding="utf-8"),ensure_ascii=False)
