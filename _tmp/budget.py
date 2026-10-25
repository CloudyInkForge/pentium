# -*- coding: utf-8 -*-
"""每页每栏预算表:body_n(8.7pt行)/cap_n/sub_n/extent/free/首元素是否图/图块高"""
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
ptype={}; pcomp={}
for i,p in enumerate(pages,1):
    cls=(p.get("class") or "").split()
    ptype[i]="pro" if "page-pro" in cls else ("2col" if "page-2col" in cls else "3col")
    body=[e for e in p.iter("div") if "body" in (e.get("class") or "").split()]
    if body:
        cols=[[]]
        for ch in body[0]:
            c=(ch.get("class") or "")
            if ch.tag in ("div","p","h2","h3"):
                if "cbrk" in c.split(): cols.append([])
                cols[-1].append(ch)
        pcomp[i]=[[ (e.tag,(e.get("class") or ""),re.search(r'--ph-h:\s*([\d.]+)',e.get("style") or "").group(1) if re.search(r'--ph-h:\s*([\d.]+)',e.get("style") or "") else None) for e in col] for col in cols]

def images(pno):
    page=cstream.reader.pages[pno-1]
    data=page.get_contents().get_data().decode('latin-1')
    out=[]
    for m in IMG.finditer(data):
        w,h,x,y=float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4))
        if w<200: out.append({"x":x/MM,"y":y/MM,"w":w/MM,"h":h/MM})
    return out

def edges(t):
    if t=="3col": return [(16.0,71.67),(77.17,132.83),(138.33,194.0)]
    if t=="2col": return [(16.0,102.25),(107.75,194.0)]
    return [(16.0,194.0)]

res={}
for pno in range(1,75):
    t=ptype[pno]
    if t=="pro": continue
    lines,_=cstream.parse_page(pno)
    body=[l for l in lines if l["y"]>BODY_BOT-0.2 and l["y"]<272 and l["fs"]>=6.0]
    es=edges(t)
    cols=[[] for _ in es]
    for l in body:
        x0,fs=l["x"],l["fs"]
        w=sum(fs*0.3528*(0.5 if ord(ch)<0x2E80 else 1.0) for ch in l["text"])
        x1=x0+w
        best,bd=-1,1e9
        for ci,(a,b) in enumerate(es):
            mid=(max(x0,a)+min(x1,b))/2
            if x1>=a-1.5 and x0<=b+1.5:
                d=abs(mid-(a+b)/2)
                if d<bd: bd,best=d,ci
        if 0<=best<len(cols): cols[best].append(l)
    crep=[]
    for ci,c in enumerate(cols):
        if not c:
            crep.append(None); continue
        body_n=sum(1 for l in c if 8.4<=l["fs"]<=9.0)
        cap_n=sum(1 for l in c if l["fs"]<8.0)
        sub_n=sum(1 for l in c if l["fs"]>9.0)
        ys=[l["y"] for l in c]
        extent=(max(ys)-min(ys))+LINE
        comp=pcomp.get(pno,[])
        first_img=False
        if ci<len(comp) and comp[ci]:
            first_img = any("photo-block" in (x[1] or "") for x in comp[:1]) if False else ("photo-block" in (comp[ci][0][1] or ""))
        imgsum=sum(float(x[2]) for x in comp[ci] if x[2]) if ci<len(comp) else 0
        nlines=len(set(round(y,1) for y in ys))
        crep.append({"body_n":body_n,"cap_n":cap_n,"sub_n":sub_n,"all_n":nlines,
                     "extent":round(extent,1),"first_img":first_img,"img_h":imgsum,
                     "bot":round(min(ys),1),"freeL":round((min(ys)-BODY_BOT)/LINE,1)})
    res[pno]={"type":t,"cols":crep}
    print(f"P{pno:02d}[{t}]")
    for ci,c in enumerate(crep):
        if c: print(f"   c{ci+1}: body{c['body_n']:2d} cap{c['cap_n']} sub{c['sub_n']} all{c['all_n']:2d} ext{c['extent']:6.1f} img{c['img_h']:5.1f} firstimg={int(c['first_img'])} bot{c['bot']:6.1f} free{c['freeL']:5.1f}L")
json.dump({"comp":{str(k):v for k,v in pcomp.items()},"budget":{str(k):v for k,v in res.items()}},
          open(r"_tmp\budget.json","w",encoding="utf-8"),ensure_ascii=False)
