# -*- coding: utf-8 -*-
"""P01: 条目文本与渲染行精确对齐 → 每条目行数"""
import sys, io, re, json, html as hm
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"_tmp")
from colsum import page_cols

n, cols, imgs = page_cols(1)
SRC = open(r"2611\2611.html", encoding="utf-8").read()
lines_src = SRC.split('\n')
starts = [i for i, l in enumerate(lines_src) if re.match(r'<div class="page[ "]', l)]
seg = '\n'.join(lines_src[starts[0]:starts[1]])
items = re.findall(r'<p>(.*?)</p>', seg, re.S)
items = [re.sub(r'\s+', '', hm.unescape(re.sub(r'<[^>]+>', '', t))) for t in items]

# 阅读顺序行序列
flat = []
for ci, c in enumerate(cols):
    for l in c: flat.append((ci, l))
# 直接做:遍历行,维护 (item_idx, char_pos)
lines_out = []
ii, cp = 0, 0
for ci, l in flat:
    t = l["text"]
    # 跳过页眉行
    if t in ("时政汇编", "原初167班 高125班 王晨玮整理", "时政摘编"):
        lines_out.append((ci, l["y"], -1, t)); continue
    # 若当前行以 t 开头匹配 item[ii][cp:]
    remain = items[ii][cp:]
    if remain.startswith(t[:min(len(t), len(remain))]) or t[:6] in remain:
        cp += len(t) if remain.startswith(t[:len(t)]) else 0
        lines_out.append((ci, l["y"], ii, t))
        if cp >= len(items[ii]):
            ii += 1; cp = 0
    else:
        # 尝试推进到下一个条目
        found = False
        for k in range(ii, min(ii+2, len(items))):
            if items[k].startswith(t[:min(len(t), len(items[k]))]):
                ii, cp = k, len(t)
                found = True; break
        lines_out.append((ci, l["y"], ii if found else -2, t))
from collections import Counter
cnt = Counter()
for ci, y, k, t in lines_out:
    if k >= 0: cnt[k] += 1
print("P01 每条目行数:", [cnt.get(i, 0) for i in range(len(items))], "总行数(含页眉3):", len(lines_out))
for ci, y, k, t in lines_out:
    mark = f"item{k}" if k >= 0 else ("HDR" if k == -1 else "??")
    print(f"  c{ci+1} y={y:6.1f} {mark:7s} {t[:34]}")
