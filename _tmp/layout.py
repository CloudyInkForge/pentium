# -*- coding: utf-8 -*-
"""全刊版面真值:每页 = 文本行(带栏位) + 图片矩形;输出 JSON 供核算"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\CloudyInkForge\pentium\_tmp")
import cstream
MM = 72/25.4

# 栏位判定:按行起点 x 与估宽
def col_edges(ncol):
    if ncol == 3: return [(16.0,71.67),(77.17,132.83),(138.33,194.0)]
    if ncol == 2: return [(16.0,102.25),(107.75,194.0)]
    return [(16.0,194.0)]

def est_w(text, fs):
    w = 0.0
    for ch in text:
        o = ord(ch)
        if o < 0x2E80: w += fs*0.3528*0.5
        else: w += fs*0.3528
    return w

def classify(pno, ncol, lines):
    edges = col_edges(ncol)
    out = []
    for l in lines:
        x0, w = l["x"], est_w(l["text"], l["fs"])
        x1 = x0 + w
        best, bd = -1, 1e9
        for ci,(a,b) in enumerate(edges):
            mid = (max(x0,a)+min(x1,b))/2
            if x1 >= a-0.5 and x0 <= b+0.5:
                d = abs(mid-(a+b)/2)
                if d < bd: bd, best = d, ci
        l2 = dict(l); l2["col"] = best; l2["w"] = round(w,1)
        out.append(l2)
    return out

# 图片矩形
IMG = re.compile(r'q\s+([\d.]+)\s+0\s+0\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+cm\s*/(I\w+|\w+)\s+Do', re.S)

def images(pno):
    page = cstream.reader.pages[pno-1]
    data = page.get_contents().get_data().decode('latin-1')
    imgs = []
    for m in IMG.finditer(data):
        w,h,x,y = float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4))
        imgs.append({"x":round(x/MM,1),"y":round(y/MM,1),"w":round(w/MM,1),"h":round(h/MM,1),"name":m.group(5)})
    return imgs

if __name__ == "__main__":
    result = {}
    for pno in range(1, 75):
        lines, _ = cstream.parse_page(pno)
        result[pno] = {"lines": lines, "images": images(pno)}
    json.dump(result, open(r"_tmp\layout.json","w",encoding="utf-8"), ensure_ascii=False)
    print("pages:", len(result))
    # 汇总:每页行数/图片数/最高最低基线
    for pno, d in result.items():
        ls = d["lines"]
        if not ls: print(f"P{pno:02d}: 0 lines"); continue
        body = [l for l in ls if 20 < l["y"] < 272]
        top = max((l["y"] for l in body), default=0)
        bot = min((l["y"] for l in body), default=0)
        print(f"P{pno:02d}: {len(body):3d} lines, {len(d['images'])} imgs, y[{bot:.1f}..{top:.1f}]")
