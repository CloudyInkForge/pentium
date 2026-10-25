# -*- coding: utf-8 -*-
"""行数估算模型: em宽度(全角1/ASCII0.55) + 2em缩进, 每行 em 容量按栏宽/字号"""
import sys, io, re, html as hm, math, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def em_len(t):
    return sum(0.55 if ord(c) < 0x2E80 else 1.0 for c in t)

def lines_for(text, col_mm, fs_pt, indent_em=2.0, cap_em=None):
    if cap_em is None:
        cap_em = col_mm / (fs_pt * 0.3528)   # 每行全角字数
    return math.ceil((em_len(text) + indent_em) / cap_em - 1e-9)

if __name__ == "__main__":
    # 校验: P01 实测条目行数 1-7 = [9,8,6,8,6,7,3]
    SRC = open(r"2611\2611.html", encoding="utf-8").read()
    lines_src = SRC.split('\n')
    starts = [i for i, l in enumerate(lines_src) if re.match(r'<div class="page[ "]', l)]
    seg = '\n'.join(lines_src[starts[0]:starts[1]])
    items = re.findall(r'<p>(.*?)</p>', seg, re.S)
    items = [re.sub(r'\s+', '', hm.unescape(re.sub(r'<[^>]+>', '', t))) for t in items]
    measured = [9,8,6,8,6,7,3]
    print("P01 校验 (3栏 55.67mm 8.7pt, cap=18.14em):")
    for i, it in enumerate(items[:7]):
        p = lines_for(it, 55.67, 8.7)
        m = measured[i] if i < len(measured) else '?'
        print(f"  item{i+1}: 预测{p} 实测{m} {'✓' if p==m else '✗'}  em={em_len(it):.0f}")
    # 其余条目
    print("  其余:", [(i+1, lines_for(it, 55.67, 8.7)) for i, it in enumerate(items[7:], 7)])
