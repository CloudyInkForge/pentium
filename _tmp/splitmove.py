# -*- coding: utf-8 -*-
"""栏间行数微调:在标点边界拆段移动行数。back=后栏头段并入前栏尾;fwd=前栏尾段下移为后栏头"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import html as LH

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = open(F, encoding="utf-8").read()
doc = LH.fromstring(src)
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]

CPL = {8.7:18.14, 9.2:17.14, 9.3:16.96, 9.5:16.53}
STRONG_END = "。！？；"
WEAK_END = "，、：”）》"

def find_para(page, prefix):
    for p in page.iter("p"):
        if (p.text_content() or "").strip().startswith(prefix):
            return p
    return None

def col_of_para(page, para):
    body = [e for e in page.iter("div") if "body" in (e.get("class") or "").split()][0]
    ci = 0
    for ch in body:
        if "cbrk" in (ch.get("class") or "").split() and ch is not para:
            pass
    # 重算:遍历 body 直接子元素
    ci = 0
    for ch in body:
        if "cbrk" in (ch.get("class") or "").split() and ch is not para:
            ci += 1
        if ch is para:
            return ci
    return -1

def split_text(txt, target_chars, from_end=False):
    """在 target_chars 附近找标点边界;返回 (head, tail)"""
    n = len(txt)
    pos = n - target_chars if from_end else target_chars
    pos = max(1, min(n - 1, pos))
    best = None; bestd = 1e9
    for i in range(max(1, pos - 14), min(n - 1, pos + 14)):
        ch = txt[i - 1]
        if ch in STRONG_END:
            d = abs(i - pos) + (0 if True else 0)
            if d < bestd: bestd, best = d, i
    if best is None:
        for i in range(max(1, pos - 14), min(n - 1, pos + 14)):
            if txt[i - 1] in WEAK_END:
                d = abs(i - pos)
                if d < bestd: bestd, best = d, i
    if best is None:
        return None
    if from_end:
        return txt[:best], txt[best:]
    return txt[:best], txt[best:]

OPS = [
 # (page, para_prefix, dir, lines, fs)
 (13, "习近平主席指出", "back", 4, 9.2),
 (14, "长征精神要“活”起来", "fwd", 3, 9.2),
 (15, "2019年，我作为全国青年代表", "fwd", 4, 9.2),
 (22, "楚国当时的君主是楚悼王", "fwd", 1, 8.7),
 (27, "公元 770 年，杜甫由于过于饥", "back", 3, 8.7),
 (28, "公元 747年，由于“野无遗贤”", "back", 2, 8.7),
 (29, "他的长子叫杜宗武", "back", 2, 8.7),
 (34, "地下建筑看陕西，地上建筑看山西", "fwd", 2, 8.7),
 (35, "游本昌的艺术人生", "back", 2, 8.7),   # 占位,下面核对
 (36, "而当刘德华谈及自己对演艺生涯的", "back", 2, 8.7),  # 占位
 (40, "为了记录这支队伍的", "back", 3, 9.3),  # 占位
 (41, "在首尔", "back", 2, 9.3),  # 占位
 (42, "九龙潭", "back", 5, 9.3),  # 占位
 (46, "三星", "back", 4, 8.7),  # 占位
 (47, "财阀", "back", 3, 8.7),  # 占位
 (48, "开幕式", "back", 2, 9.3),  # 占位
 (49, "我和你", "fwd", 3, 9.3),  # 占位
 (50, "其一", "back", 3, 9.3),  # 占位
 (51, "其二", "back", 2, 9.3),  # 占位
 (54, "写真", "back", 2, 8.7),  # 占位
 (55, "游本昌", "fwd", 2, 8.7),  # 占位
 (56, "这一拜", "back", 4, 8.7),  # 占位
 (57, "我和你", "back", 4, 8.7),  # 占位
 (61, "其一", "back", 2, 9.3),  # 占位
 (62, "其二", "back", 3, 9.3),  # 占位
 (63, "第十七题", "fwd", 2, 9.3),  # 占位
 (66, "图难于其易", "back", 2, 9.3),  # 占位
 (67, "为大于其细", "back", 2, 9.3),  # 占位
 (68, "跑向更好的自己", "back", 4, 9.3),  # 占位
 (69, "军训", "back", 2, 8.7),  # 占位
]

for page_no, prefix, direction, lines, fs in OPS:
    page = pages[page_no-1]
    para = find_para(page, prefix)
    if para is None:
        print(f"P{page_no:02d} !! para not found: {prefix}")
        continue
    txt = para.text_content()
    cpl = CPL.get(fs, 18.14)
    tchars = int(round(lines * cpl))
    r = split_text(txt, tchars, from_end=(direction=="fwd"))
    if r is None:
        print(f"P{page_no:02d} !! no split point near {tchars}ch: {prefix} ({len(txt)}ch)")
        continue
    head, tail = r
    print(f"P{page_no:02d} [{direction} {lines}L] {prefix}: split@{len(head)}/{len(txt)} | head尾:…{head[-8:]} | tail头:{tail[:8]}…")
