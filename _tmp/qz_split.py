# -*- coding: utf-8 -*-
"""青藏文章 B1/B2 分页估算：按 18.14 cpl 估行，规划三页切分"""
import sys, io, math, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r"D:\CloudyInkForge\pentium\unformed\articles\世界屋脊上的生命接力：青藏高原动物从哪里来.txt"
CPL = 18.14

lines = [l.rstrip() for l in open(SRC, encoding='utf-8').read().splitlines()]
paras = []
for l in lines:
    if not l.strip():
        continue
    if l.startswith("标题："):
        continue
    if re.fullmatch(r"[^，。；：！？（）“”]{1,20}", l) and not l.endswith("。"):
        paras.append({"t": "sub", "x": l})
    else:
        paras.append({"t": "p", "x": l})

def nl(p):
    if p["t"] == "sub":
        return 1
    # 首行缩进2em；半角字符按0.5宽折算
    w = sum(0.5 if ord(c) < 0x2E80 else 1.0 for c in p["x"])
    return math.ceil((w + 2) / CPL)

tot = sum(nl(p) for p in paras)
print("paras:", len(paras), "sub:", sum(1 for p in paras if p['t']=='sub'), "total lines ~", tot)

# 容量: B1 3栏 x 39 行 = 117; B2 = lead 19 + body 3 x 35 = 124
cap1, cap2 = 117, 124
used, page = 0, 1
assign = []
for i, p in enumerate(paras):
    n = nl(p)
    cap = cap1 if page == 1 else cap2
    if used + n > cap - (0 if page < 3 else 0):
        page += 1
        used = 0
    assign.append((page, i, n))
    used += n
    print(f"pg{page} #{i:02d} {p['t']:3s} {n:3d}L cum{used:4d} | {p['x'][:22]}")

# 输出各页行数
for pg in sorted(set(a[0] for a in assign)):
    s = sum(a[2] for a in assign if a[0] == pg)
    print(f"page {pg}: {s} lines")
json.dump([{"i": i, "pg": a[0], "t": paras[i]["t"], "n": a[2], "x": paras[i]["x"]} for i, a in enumerate(assign)],
          open(r"D:\CloudyInkForge\pentium\_tmp\qz_assign.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
