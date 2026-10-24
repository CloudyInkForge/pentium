# -*- coding: utf-8 -*-
"""分析 flowdump.txt：每页各栏内容底边、溢出检测、洞偏移 vs 图 top"""
import io
from collections import defaultdict

LINE = 4.57
rows = []
for ln in io.open(r"D:\CloudyInkForge\pentium\_tmp\flowdump.txt", encoding="utf-8"):
    p = ln.rstrip("\n").split("|")
    if len(p) < 9:
        continue
    rows.append(dict(folio=p[0], tag=p[1], cls=p[2], key=p[3],
                     left=float(p[4]), top=float(p[5]), bot=float(p[6]),
                     bodyTop=float(p[7]), bodyH=float(p[8])))

by_page = defaultdict(list)
for r in rows:
    by_page[r["folio"]].append(r)

# 图 top（来自 HTML，当前值）
photo_tops = {
 "16": [64.0], "17": [45.8], "19": [132.3], "20": [91.3], "21": [32.0],
 "22": [70.1, 97.6], "23": [54.8, 154.8], "24": [56.1, 157.5, 38.4],
 "25": [56.6, 69.9], "26": [40.8, 180.5, 27.3, 130.1], "27": [43.1, 0.0],
 "35": [41.3, 0.0, 119.3, 77.8], "36": [119.1, 0.0, 110.1, 0.0, 114.8],
 "37": [132.6], "38": [36.5, 45.8], "39": [50.3],
}

print(f"{'页':<4}{'栏':<3}{'内容底':>8}{'容量底':>8}{'余(mm)':>8}{'余(行)':>7}  溢出?")
for folio in sorted(by_page, key=int):
    items = by_page[folio]
    bt, bh = items[0]["bodyTop"], items[0]["bodyH"]
    capbot = bt + bh
    cols = defaultdict(list)
    for r in items:
        cx = round(r["left"], 1)
        cols[cx].append(r)
    worst = 0
    for cx in sorted(cols):
        its = cols[cx]
        bot = max(r["bot"] for r in its)
        slack = capbot - bot
        colno = {0.0:"1", 91.75:"2", 61.17:"2", 122.33:"3", 183.5:"溢出列"}.get(cx, str(cx))
        flag = " <<<溢出" if slack < 0 else (" <临界" if slack < 4.57 else "")
        print(f"P{folio:<3}栏{colno:<2}{bot:8.1f}{capbot:8.1f}{slack:8.1f}{slack/LINE:7.1f}{flag}")
        if slack < worst or worst == 0:
            worst = min(worst, slack)
    # 洞偏移与图top核对
    holes = [(r["left"], r["top"]-bt, r["bot"]-r["top"]) for r in items if "hole" in r["cls"]]
    tops = photo_tops.get(folio, [])
    msg = []
    for i, (hx, hoff, hh) in enumerate(holes):
        t = tops[i] if i < len(tops) else None
        d = round(hoff - (t or 0), 2)
        msg.append(f"洞{i+1}off={hoff:.1f} top={t} Δ={d}")
    print(f"     {'; '.join(msg)}")
