# -*- coding: utf-8 -*-
"""精确段落行数:HTML 段落文本 × PDF 视觉行(栏序) 前缀对齐"""
import sys, io, re, json, html as hm
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
SRC = open(r"2611\2611.html", encoding="utf-8").read()
starts = [m.start() for m in re.finditer(r'<div class="page[ "]', SRC)]
pages_html = [SRC[s:(starts[i+1] if i+1 < len(starts) else len(SRC))] for i, s in enumerate(starts)]
def pncol(pno):
    m = re.search(r'<div class="page([^"]*)"', pages_html[pno-1])
    cls = m.group(1) if m else ""
    if 'page-pro' in cls: return None
    if 'page-2col' in cls: return 2
    return 3
EDGES = {2:[(16.0,102.25),(107.75,194.0)], 3:[(16.0,71.67),(77.17,132.83),(138.33,194.0)]}
def est_w(t, fs):
    return sum((fs*0.3528*0.55 if ord(c) < 0x2E80 else fs*0.3528) for c in t)
def page_cols(pno):
    n = pncol(pno)
    d = LAY[str(pno)]
    ls = [dict(l) for l in d["lines"] if 20 < l["y"] < 265.5]
    if n is None: return None, []
    edges = EDGES[n]
    buckets = [[] for _ in edges]
    for l in ls:
        x0 = l["x"]; placed = False
        for ci,(a,b) in enumerate(edges):
            if a-1 <= x0 <= b+1: buckets[ci].append(l); placed=True; break
        if not placed:
            x1 = x0 + est_w(l["text"], l["fs"])
            for ci,(a,b) in enumerate(edges):
                if a-1 <= x1 <= b+1: buckets[ci].append(l); break
    cols = []
    for c in buckets:
        byy = {}
        for l in c: byy.setdefault(round(l["y"],1), []).append(l)
        col = []
        for y, frags in byy.items():
            frags.sort(key=lambda l: l["x"])
            cur = None
            for f in frags:
                if cur is None: cur = dict(f)
                elif f["x"] - (cur["x"] + est_w(cur["text"], cur["fs"])) <= 3.0: cur["text"] += f["text"]
                else: col.append(cur); cur = dict(f)
            if cur: col.append(cur)
        col.sort(key=lambda l: -l["y"])
        cols.append(col)
    return n, cols
def paras_of(pno):
    seg = pages_html[pno-1]
    m = re.search(r'<div class="body[^"]*">', seg)
    if not m: return []
    seg2 = seg[m.end():]
    cut = re.search(r'<div class="folio">', seg2)
    if cut: seg2 = seg2[:cut.start()]
    out = []
    for m2 in re.finditer(r'<(p|h2)\b([^>]*)>(.*?)</\1>', seg2, re.S):
        tag, attrs, inner = m2.groups()
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1) if cls else ""
        t = re.sub(r'\s+', '', hm.unescape(re.sub(r'<[^>]+>', '', inner)))
        if not t: continue
        out.append((tag, cls, t))
    return out
def align(pno):
    n, cols = page_cols(pno)
    if n is None: return
    paras = paras_of(pno)
    flat = []
    for ci, c in enumerate(cols): flat.extend((ci, l) for l in c)
    res = []
    ii, cp = 0, 0
    for ci, l in flat:
        t = re.sub(r'\s+', '', l["text"])
        if not t: continue
        matched = False
        for k in range(ii, min(ii+2, len(paras))):
            pt = paras[k][2]
            remain = pt[cp:] if k == ii else pt
            if t[:8] and (remain.startswith(t[:min(len(t), 12)]) or t[:10] in pt):
                if k != ii: cp = 0
                take = min(len(t), len(paras[k][2]) - cp)
                cp += take
                res.append((ci, l["y"], k))
                ii = k
                if cp >= len(paras[k][2]):
                    ii += 1; cp = 0
                matched = True
                break
        if not matched:
            res.append((ci, l["y"], -1))
    from collections import Counter
    cnt = Counter(k for _,_,k in res if k >= 0)
    lines_out = []
    for k,(tag, cls, t) in enumerate(paras):
        lines_out.append(f"  [{k:2d}] {tag}.{cls:14s} {cnt.get(k,0):2d}行 | {t[:22]}")
    print(f"P{pno:02d} ({n}栏) 未匹配行: {sum(1 for _,_,k in res if k<0)}")
    print("\n".join(lines_out))
if __name__ == "__main__":
    for a in sys.argv[1:]:
        align(int(a))
