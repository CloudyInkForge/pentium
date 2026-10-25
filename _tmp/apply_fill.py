# -*- coding: utf-8 -*-
"""按页应用行距/字号覆盖与图高调整(基于 budget2 实测与逐页规划)"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = open(F, encoding="utf-8").read()

# 页索引(1起) -> 规格 BodyStyle 加到该页首个 <div class="body..."> 上;Imgs: (old_h, new_h) 按出现序替换
PLAN = {
 1:  {"style": "--body-font:9.4pt; --body-lh:1.52; --line:5.04mm"},
 9:  {"imgs": [(46.0, 50.0), (41.8, 45.0)]},
 12: {"imgs": [(41.2, 45.0), (53.3, 57.0), (41.9, 46.0)]},
 13: {"style": "--body-font:9.2pt; --body-lh:1.56; --line:5.06mm", "photo": 64.0},
 14: {"style": "--body-font:9.2pt; --body-lh:1.56; --line:5.06mm"},
 15: {"style": "--body-font:9.2pt; --body-lh:1.56; --line:5.06mm"},
 22: {"style": "--body-lh:1.55; --line:4.76mm"},
 23: {"style": "--body-lh:1.55; --line:4.76mm"},
 24: {"style": "--body-lh:1.55; --line:4.76mm"},
 25: {"style": "--body-lh:1.55; --line:4.76mm"},
 26: {"style": "--body-lh:1.55; --line:4.76mm"},
 27: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(54.0, 60.0)]},
 28: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(54.8, 60.0), (42.2, 47.0)]},
 29: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(32.6, 38.0)]},
 34: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(41.3, 48.0), (41.3, 48.0)]},
 35: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(53.9, 58.0)]},
 36: {"style": "--body-lh:1.55; --line:4.76mm"},
 37: {"style": "--body-lh:1.55; --line:4.76mm", "imgs": [(24.0, 36.0)]},
 40: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(73.1, 95.0)]},
 41: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(55.1, 110.0)]},
 42: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(53.8, 115.0), (37.0, 68.0)]},
 43: {"style": "--body-lh:1.55; --line:4.76mm", "photo": 56.0},
 48: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm"},
 49: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(54.3, 130.0)]},
 50: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(37.3, 70.0), (45.9, 80.0)]},
 51: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(54.1, 75.0)]},
 54: {"style": "--body-lh:1.58; --line:4.85mm", "imgs": [(50.4, 70.0)]},
 56: {"style": "--body-lh:1.58; --line:4.85mm"},
 57: {"style": "--body-lh:1.58; --line:4.85mm", "imgs": [(37.2, 48.0)]},
 61: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(45.4, 85.0)]},
 62: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm"},
 63: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(45.0, 80.0)]},
 66: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm"},
 67: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm"},
 68: {"style": "--body-font:9.3pt; --body-lh:1.6; --line:4.91mm", "imgs": [(45.7, 75.0)]},
 74: {"style": "--body-font:9.5pt; --body-lh:1.62; --line:5.43mm"},
}

# 定位每页 div 的行区间
lines = src.split("\n")
starts = []
for i, l in enumerate(lines):
    if re.match(r'^<div class="page[" ]', l):
        starts.append(i)
assert len(starts) == 74, f"page divs: {len(starts)}"
ranges = {}
for n, s in enumerate(starts, 1):
    e = starts[n] if n < 74 else len(lines)
    ranges[n] = (s, e)

report = []
for pno, spec in sorted(PLAN.items()):
    s, e = ranges[pno]
    seg = lines[s:e]
    if "style" in spec:
        for j, l in enumerate(seg):
            m = re.match(r'^(\s*)<div class="body( [^"]*)?"(\s*)>', l)
            if m:
                cls = m.group(2) or ""
                seg[j] = f'{m.group(1)}<div class="body{cls}" style="{spec["style"]}">'
                report.append(f"P{pno:02d}: body style added -> {spec['style']}")
                break
        else:
            report.append(f"P{pno:02d}: !!! body div NOT FOUND")
    if "photo" in spec:
        done = False
        for j, l in enumerate(seg):
            m = re.search(r'<div class="photo"([^>]*)>', l)
            if m:
                attrs = m.group(1)
                if 'style="' in attrs:
                    seg[j] = seg[j].replace('style="', f'style="height:{spec["photo"]}mm; ', 1)
                else:
                    seg[j] = seg[j].replace(f'<div class="photo"{attrs}>',
                                            f'<div class="photo"{attrs} style="height:{spec["photo"]}mm">')
                report.append(f"P{pno:02d}: .photo height -> {spec['photo']}mm")
                done = True
                break
        if not done: report.append(f"P{pno:02d}: !!! .photo NOT FOUND")
    if "imgs" in spec:
        occ = 0
        for old, new in spec["imgs"]:
            found = False
            for j, l in enumerate(seg):
                if "--ph-h:" not in l: continue
                m = re.search(r'--ph-h:([\d.]+)mm', l)
                if not m: continue
                if occ in [k for k,(o,_) in enumerate([])]:
                    pass
                # 只匹配当前这一项的 old 值且未被替换过
                if abs(float(m.group(1)) - old) < 0.05:
                    seg[j] = seg[j].replace(f'--ph-h:{m.group(1)}mm', f'--ph-h:{new}mm', 1)
                    report.append(f"P{pno:02d}: img {old} -> {new}")
                    found = True
                    break
            if not found:
                report.append(f"P{pno:02d}: !!! img {old} NOT FOUND (all occ values: "
                              + ",".join(re.search(r'--ph-h:([\d.]+)', l).group(1) for l in seg if '--ph-h:' in l) + ")")
    lines[s:e] = seg

open(F, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n".join(report))
print("DONE")
