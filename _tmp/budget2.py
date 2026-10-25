# -*- coding: utf-8 -*-
"""预算表 v2:HTML 算页眉高度→body_top;干净列数据"""
import sys, io, json, re, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\CloudyInkForge\pentium\_tmp")
import cstream
from lxml import html as LH

BODY_BOT = 21.8
LINE = 4.57

doc = LH.parse(r"D:\CloudyInkForge\pentium\2611\2611.html")
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]

def header_h(p):
    """页眉高度(270 到 body 顶)"""
    h = 0.0
    kick = p.findall("./div[@class='kicker']")
    if kick:
        n = len(kick[0].text or "")
        w = n*8*0.3528*1.14
        h += 4.23 + 1.5
    title = p.findall("./h1[@class='title']")
    tl = 0
    if title:
        t = title[0].text or ""
        w = sum(22*0.3528*(0.55 if ord(c)<0x2E80 or c==' ' else 1.0) for c in t) + len(t)*0.16
        tl = max(1, math.ceil(w/177.5))
        h += tl*9.7
    if p.findall("./p[@class='byline']"): h += 4.49+1.5
    if p.findall("./div[@class='rule']"): h += 0.18+2.5+3.0
    photo = p.findall("./div[@class='photo']")
    if photo:
        st = photo[0].get("style") or ""
        m = re.search(r'height:\s*([\d.]+)mm', st)
        h += (float(m.group(1)) if m else 36.0) + 2.8
    cap = p.findall("./p[@class='cap']")
    if cap:
        n = len(cap[0].text or "")
        w = n*7.5*0.3528*1.04
        h += 3.97+0.5+1.8 + (0 if w<=177 else 3.97)
    return h

out={}
for i,p in enumerate(pages,1):
    cls=(p.get("class") or "").split()
    t="pro" if "page-pro" in cls else ("2col" if "page-2col" in cls else "3col")
    if t=="pro":
        out[i]={"type":t}; continue
    hh=header_h(p)
    body_top=270-hh
    lines,_=cstream.parse_page(i)
    body=[l for l in lines if BODY_BOT-0.2<l["y"]<body_top-2.0 and l["fs"]>=6.0]
    es=[(16.0,71.67),(77.17,132.83),(138.33,194.0)] if t=="3col" else [(16.0,102.25),(107.75,194.0)]
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
    # HTML 列构成
    bodyel=[e for e in p.iter("div") if "body" in (e.get("class") or "").split()]
    comp=[[]]
    if bodyel:
        for ch in bodyel[0]:
            c=(ch.get("class") or "").split()
            if "cbrk" in c: comp.append([])
            comp[-1].append(ch)
    def flat(els):
        out=[]
        for ch in els:
            c=(ch.get("class") or "")
            if ch.tag=="div" and "photo-block" in c.split(): out.append(("img",ch))
            elif ch.tag=="div" and "gap" in c.split(): out.append(("gap",ch))
            elif ch.tag=="p": out.append(("p",ch))
            elif ch.tag in ("h2","h3"): out.append(("sub",ch))
            elif ch.tag=="div": out.extend(flat(ch))
        return out
    crep=[]
    for ci,c in enumerate(cols):
        colcomp = flat(comp[ci]) if ci<len(comp) else []
        if not c and not colcomp:
            crep.append(None); continue
        body_n=sum(1 for l in c if 8.4<=l["fs"]<=9.0)
        cap_n=sum(1 for l in c if l["fs"]<8.0)
        sub_n=sum(1 for l in c if l["fs"]>9.0)
        bot=min((l["y"] for l in c),default=body_top)
        imgs=[float(re.search(r'--ph-h:\s*([\d.]+)',e.get("style") or "").group(1)) for k,e in colcomp if k=="img"]
        gaps=sum(1 for k,e in colcomp if k=="gap")
        first_img = bool(colcomp) and colcomp[0][0]=="img"
        extent=body_top-bot+LINE
        crep.append({"body_n":body_n,"cap_n":cap_n,"sub_n":sub_n,
            "bot":round(bot,1),"extent":round(extent,1),
            "freeL":round((bot-BODY_BOT)/LINE,1),
            "imgs":imgs,"gaps":gaps,"first_img":first_img,
            "nel":len(colcomp)})
    out[i]={"type":t,"body_top":round(body_top,1),"cols":crep,
            "bodyH":round(body_top-BODY_BOT,1)}
    print(f"P{i:02d}[{t}] top={body_top:.1f} H={body_top-BODY_BOT:.1f}mm")
    for ci,c in enumerate(crep):
        if c: print(f"   c{ci+1}: body{c['body_n']:2d} cap{c['cap_n']} sub{c['sub_n']} ext{c['extent']:6.1f} free{c['freeL']:5.1f}L imgs{[round(x,1) for x in c['imgs']]} gaps{c['gaps']} firstimg={int(c['first_img'])} nel={c['nel']}")
json.dump({str(k):v for k,v in out.items()},open(r"_tmp\budget2.json","w",encoding="utf-8"),ensure_ascii=False)
