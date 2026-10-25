# -*- coding: utf-8 -*-
import sys, io, json, re, html as htmlmod
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = open(r"D:\CloudyInkForge\pentium\2611\2611.html", encoding="utf-8").read()
items = json.load(open(r"D:\CloudyInkForge\pentium\_tmp\pdf_items.json", encoding="utf-8"))

# ---- split html into pages ----
starts = [m.start() for m in re.finditer(r'<div class="page[ "]', SRC)]
pages_html = []
for i, s in enumerate(starts):
    e = starts[i+1] if i+1 < len(starts) else len(SRC)
    pages_html.append(SRC[s:e])
print("html pages:", len(pages_html), "pdf pages:", len(items))

def strip_html(h):
    # remove style blocks
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    h = re.sub(r'<[^>]+>', '', h)
    h = htmlmod.unescape(h)
    h = re.sub(r'\s+', '', h)
    return h

def pdf_text(pg):
    t = ''.join(i["t"] for i in pg)
    return re.sub(r'\s+', '', t)

missing_report = []
for idx in range(min(len(pages_html), len(items))):
    htxt = strip_html(pages_html[idx])
    ptxt = pdf_text(items[idx])
    # 按块检查：把 html 文本切成 12 字滑窗段，找 html 中连续但 pdf 中没有的段落
    # 更实用：按 HTML 文本顺序，找到最长缺失前缀块
    miss = []
    i = 0
    n = len(htxt)
    while i < n:
        # try to match growing run
        j = i
        while j < n:
            if htxt[j] not in ptxt and htxt[j] not in '·—':
                break
            j += 1
        # binary-search longest k so that htxt[i:i+k] in ptxt
        lo, hi = 0, j - i
        best = 0
        while lo <= hi:
            mid = (lo+hi)//2
            if htxt[i:i+mid] in ptxt:
                best = mid; lo = mid+1
            else:
                hi = mid-1
        run = htxt[i:i+best]
        if best < 8:  # 无法匹配的段，报缺失
            # collect the maximal missing chunk (until next good match)
            k = i
            while k < n:
                nxt = htxt[k:k+8]
                if nxt in ptxt:
                    break
                k += 1
            miss.append(htxt[i:min(k, i+60)])
            i = k
        else:
            i += best
    if miss:
        missing_report.append((idx+1, miss))
        print(f"P{idx+1:02d} MISSING {len(miss)}:")
        for m in miss:
            print("    …" + m + "…")
if not missing_report:
    print("NO MISSING TEXT")
