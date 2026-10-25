# -*- coding: utf-8 -*-
"""逐页账本:HTML元素序列 × PDF视觉行 → 每元素每栏行数/栏底/丢失检测"""
import sys, io, re, json, html as hm
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = open(r"2611\2611.html", encoding="utf-8").read()
LAY = json.load(open(r"_tmp\layout.json", encoding="utf-8"))
lines_src = SRC.split('\n')
starts = [i for i, l in enumerate(lines_src) if re.match(r'<div class="page[ "]', l)]

# 每页栏数
P2COL = {4,5,8,12,13,14,15,18,22,23,24,25,26,27,28,29,34,36,37,40,46,47,49,54,62,66,67,71,74}
PRO = {2,3,6,7,10,11,16,17,20,21,30,32,38,39,44,45,52,58,59,65,70,73}
def ncol(p):
    if p in PRO: return None
    return 2 if p in P2COL else 3

def est_w(t, fs):
    return sum((fs*0.3528*0.5 if ord(c) < 0x2E80 else fs*0.3528) for c in t)

EDGES = {2:[(16.0,102.25),(107.75,194.0)], 3:[(16.0,71.67),(77.17,132.83),(138.33,194.0)]}

def assign_col(l, n):
    x0 = l["x"]; x1 = x0 + est_w(l["text"], l["fs"])
    best, bd = -1, 1e9
    for ci,(a,b) in enumerate(EDGES[n]):
        if x1 >= a-0.5 and x0 <= b+0.5:
            mid = (max(x0,a)+min(x1,b))/2
            d = abs(mid-(a+b)/2)
            if d < bd: bd, best = d, ci
    return best

def page_elements(seg):
    """页面 body 区元素序列: (kind, class, text, attrs)"""
    # 截取 body/cols/zone 到 folio 之前
    m = re.search(r'<div class="body[^"]*">|<div class="cols">|<div class="zone-\w+[^"]*">', seg)
    if not m: return []
    seg2 = seg[m.end():]
    cut = re.search(r'<div class="folio">', seg2)
    if cut: seg2 = seg2[:cut.start()]
    elems = []
    for m2 in re.finditer(r'<(p|h2|div)\b([^>]*)>(.*?)</\1>', seg2, re.S):
        tag, attrs, inner = m2.group(1), m2.group(2), m2.group(3)
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = cls.group(1) if cls else ""
        if tag == 'div':
            if 'photo-block' in cls:
                phw = re.search(r'--ph-w:([\d.]+)mm', attrs)
                phh = re.search(r'--ph-h:([\d.]+)mm', attrs)
                capm = re.search(r'<p class="cap">(.*?)</p>', inner, re.S)
                elems.append(("photo", cls, (capm.group(1) if capm else "").strip(),
                              (float(phw.group(1)) if phw else 55.67, float(phh.group(1)) if phh else 36.6)))
            elif 'gap' in cls:
                elems.append(("gap", cls, "", None))
            continue
        txt = re.sub(r'<[^>]+>', '', inner)
        txt = hm.unescape(txt)
        txt = re.sub(r'\s+', '', txt)
        if not txt: continue
        elems.append((tag, cls, txt, None))
    return elems

def analyze(pno):
    n = ncol(pno)
    seg = '\n'.join(lines_src[starts[pno-1]: (starts[pno] if pno < len(starts) else len(lines_src))])
    elems = page_elements(seg)
    raw = LAY[str(pno)]["lines"]
    body = [l for l in raw if 20 < l["y"] < 265.5]
    if n is None:
        # PRO 页:整宽分类,栏位标 x 端
        for l in body: l["col"] = 0 if l["x"] < 60 else (1 if l["x"] < 120 else 2)
        nprint = "PRO"
    else:
        for l in body: l["col"] = assign_col(l, n)
    return pno, n, elems, body

if __name__ == "__main__":
    import collections
    for pno in range(1, 75):
        p, n, elems, body = analyze(pno)
        if not elems:
            print(f"P{pno:02d}: (无 body 元素)"); continue
        # 按元素匹配行
        seq = []  # 每栏行序列(按 y 降序)
        cols = collections.defaultdict(list)
        for l in sorted(body, key=lambda l: (-l["y"], l["x"])):
            cols[l["col"]].append(l)
        # 元素匹配:总体阅读顺序 = 栏0→栏1→栏2
        flat = []
        for ci in sorted(cols):
            flat.extend(cols[ci])
        ei = 0; consumed = [0]*len(elems)
        li = 0
        assign = collections.defaultdict(list)   # elem idx -> lines
        unmatched = []
        for l in flat:
            t = re.sub(r'\s+', '', l["text"])
            matched = False
            for k in range(ei, min(ei+3, len(elems))):
                et = elems[k][2]
                if not et: continue
                # 行文本是元素文本的子串(或元素文本以行文本开头)
                if t and (t in et or et.startswith(t[:max(4,len(t)//2)]) or t[:6] in et):
                    assign[k].append(l); ei = k; matched = True; break
            if not matched:
                unmatched.append(l)
        # 输出
        tot = {}
        print(f"── P{pno:02d} (ncol={n}) elems={len(elems)} lines={len(body)} unmatched={len(unmatched)}")
        for k,(kind, cls, txt, dim) in enumerate(elems):
            ls = assign.get(k, [])
            cs = collections.Counter(l["col"] for l in ls)
            tag = f"{kind}.{cls}" if cls else kind
            info = f" ph={dim}" if dim else ""
            tshow = (txt[:16] + "…") if len(txt) > 16 else txt
            print(f"   [{k:2d}] {tag:22s} {info:16s} 行={dict(cs)} | {tshow}")
        if unmatched:
            for l in unmatched[:6]:
                print(f"   ?? 未匹配 y={l['y']} x={l['x']} | {l['text'][:30]}")
