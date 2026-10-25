# -*- coding: utf-8 -*-
# 模板 PDF 只读审计：页数、页面尺寸、逐页文本坐标分桶、越界检查
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import PyPDF2

MM = 72 / 25.4

TPL = {
    r"D:\CloudyInkForge\pentium\template\PRO\pro-6.pdf": dict(
        pages=2,
        # (名称, x0,y0,x1,y1, 允许的文本数上限) 坐标为 mm、自页顶向下
        allow=[
            ("cap-l",   16, 120, 194, 130),
            ("body-l",  16, 131, 194, 273),
            ("folio-l", 16, 273, 194, 285),
            ("body-r",  16, 131, 194, 273),
            ("folio-r", 16, 273, 194, 285),
        ],
        forbid=[("band-img", 0, 0, 210, 120, 0), ("band-img", 0, 0, 210, 120, 1)],
    ),
    r"D:\CloudyInkForge\pentium\template\PRO\pro-7.pdf": dict(
        pages=2,
        allow=[
            ("head-l",  16, 14, 194, 118),
            ("cap-l",   16, 267, 194, 274),
            ("folio-l", 16, 274, 194, 285),
            ("cap-r",   16, 127, 194, 136),
            ("body-r",  16, 136, 194, 273),
            ("folio-r", 16, 274, 194, 285),
        ],
        # forbid: (标签, x0,y0,x1,y1, 页码从0计)
        forbid=[("art-a-img", 0, 119, 210, 266, 0), ("art-b-img", 0, 15, 210, 126, 1)],
    ),
    r"D:\CloudyInkForge\pentium\template\PRO\pro-8.pdf": dict(
        pages=2,
        allow=[
            ("head-l",  16, 14, 194, 46),
            ("cap-l",   16, 263, 194, 271),
            ("folio-l", 16, 274, 194, 285),
            ("body-r",  16, 14, 194, 273),
            ("folio-r", 16, 274, 194, 285),
        ],
        forbid=[("plate-img", 0, 49, 210, 262, 0)],
    ),
    r"D:\CloudyInkForge\pentium\template\MIDDLE\middle-1.pdf": dict(
        pages=1,
        allow=[
            ("cap",    16, 130, 194, 140),
            ("body",   16, 141, 194, 273),
            ("folio",  16, 274, 194, 285),
        ],
        forbid=[("band-img", 0, 0, 210, 129, 0)],
    ),
    r"D:\CloudyInkForge\pentium\template\MIDDLE\middle-2.pdf": dict(
        pages=1,
        allow=[
            ("body",  16, 14, 112, 273),
            ("cap",   119, 258, 196, 268),
            ("folio", 16, 274, 112, 285),
        ],
        forbid=[("rail-img", 119, 0, 210, 257, 0)],
    ),
    r"D:\CloudyInkForge\pentium\template\MIDDLE\middle-3.pdf": dict(
        pages=1,
        allow=[
            ("body", 16, 14, 194, 123),
            ("cap",  16, 123, 194, 132),
            ("chip", 0, 276, 12, 285),
        ],
        forbid=[("band-img", 0, 134, 210, 284, 0)],
    ),
}

ok_all = True
for pdf, spec in TPL.items():
    name = pdf.split("\\")[-1]
    reader = PyPDF2.PdfReader(pdf)
    errs = []
    if len(reader.pages) != spec["pages"]:
        errs.append(f"页数 {len(reader.pages)} != {spec['pages']}")
    for pno in range(len(reader.pages)):
        page = reader.pages[pno]
        pw = float(page.mediabox.width); ph = float(page.mediabox.height)
        if abs(pw / MM - 210) > 1 or abs(ph / MM - 285) > 1:
            errs.append(f"P{pno+1} 尺寸 {pw/MM:.1f}x{ph/MM:.1f}mm != 210x285")
        items = []
        def visitor(text, cm, tm, fd, fs):
            t = text.strip()
            if not t:
                return
            x = tm[4] / MM
            y_top = (ph - tm[5]) / MM
            items.append((x, y_top, t, fs))
        try:
            page.extract_text(visitor_text=visitor)
        except Exception as e:
            errs.append(f"P{pno+1} 提取失败 {e}")
            continue
        if not items:
            errs.append(f"P{pno+1} 无文本")
            continue
        # 逐条文本归区：必须落在本页 allow 区或通用 folio/chip 区，且不得落 forbid 区
        page_allows = [a for a in spec["allow"] if f"-{['l','r'][pno]}" not in a[0] or a[0].endswith(f"-{['l','r'][pno]}")] if spec["pages"] == 2 else spec["allow"]
        page_allows = []
        for a in spec["allow"]:
            tag = a[0]
            if spec["pages"] == 2:
                if tag.endswith("-l") and pno != 0: continue
                if tag.endswith("-r") and pno != 1: continue
            page_allows.append(a)
        stray = []
        for x, y, t, fs in items:
            placed = False
            for tag, x0, y0, x1, y1 in page_allows:
                # 文本锚点 x 是字串起点，右侧可延展，扩 3mm 容差
                if x0 - 1 <= x <= x1 + 3 and y0 - 2 <= y <= y1 + 2:
                    placed = True
                    break
            if not placed:
                stray.append((round(x,1), round(y,1), t[:22]))
                continue  # 已判区外，不再重复报压图
            for tag, x0, y0, x1, y1, pg in spec["forbid"]:
                if pg != pno:
                    continue
                if x0 - 1 <= x <= x1 + 1 and y0 - 1 <= y <= y1 + 1:
                    # 允许区与禁图区重叠（如压图页码角标）不报
                    overlapping_allow = any(
                        a[1]-1 <= x <= a[3]+3 and a[2]-2 <= y <= a[4]+2
                        for a in page_allows if a[0] in ("chip",)
                    )
                    if not overlapping_allow:
                        errs.append(f"P{pno+1} 文本压图区[{tag}] @({x:.0f},{y:.0f}) {t[:18]}")
        if stray:
            errs.append(f"P{pno+1} 区外文本 {len(stray)} 条: " + "; ".join(f"({a},{b}){c}" for a,b,c in stray[:6]))
        # 摘要：本页文本 y 范围与栏 x 分桶
        xs = sorted(set(round(x) for x, y, t, f in items))
        ymin = min(y for x, y, t, f in items); ymax = max(y for x, y, t, f in items)
        clusters = []
        for x in xs:
            if not clusters or x - clusters[-1][-1] > 15:
                clusters.append([x])
            else:
                clusters[-1].append(x)
        buckets = ",".join(f"{c[0]}-{c[-1]}" for c in clusters)
        print(f"{name} P{pno+1}: {len(items)}段 y[{ymin:.0f}..{ymax:.0f}] 栏x[{buckets}]")
    status = "PASS" if not errs else "FAIL"
    if errs:
        ok_all = False
        for e in errs:
            print(f"  !! {name}: {e}")
    print(f"{name}: {status}")
print("====", "ALL PASS" if ok_all else "HAS FAILURES")
