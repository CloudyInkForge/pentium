# -*- coding: utf-8 -*-
"""栏间平衡:拆段移动 + 图高微调 + 行距微调 (基于浏览器实测)"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import html as LH
from lxml import etree

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = open(F, encoding="utf-8").read()
doc = LH.fromstring(src)
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]
CPL = {8.7:18.14, 9.2:17.14, 9.3:16.96, 9.5:16.53}
STRONG = "。！？；"
WEAK = "，、：”）》……"

def body_of(page):
    return [e for e in page.iter("div") if "body" in (e.get("class") or "").split()][0]

def find_para(page, prefix, tag="p"):
    for p in page.iter(tag):
        if (p.text_content() or "").strip().startswith(prefix):
            return p
    return None

def classes(el):
    return (el.get("class") or "").split()

def set_cls(el, cls):
    el.set("class", " ".join(cls))

def split_at(txt, tchars, from_end):
    n = len(txt)
    pos = n - tchars if from_end else tchars
    pos = max(2, min(n-2, pos))
    best, bd = None, 999
    for i in range(max(2,pos-16), min(n-1,pos+17)):
        if txt[i-1] in STRONG:
            d = abs(i-pos)
            if d < bd: bd, best = d, i
    if best is None:
        for i in range(max(2,pos-16), min(n-1,pos+17)):
            if txt[i-1] in WEAK:
                d = abs(i-pos)
                if d < bd: bd, best = d, i
    if best is None: return None
    return txt[:best], txt[best:]

def fs_of_page(page):
    st = body_of(page).get("style") or ""
    m = re.search(r'--body-font:\s*([\d.]+)pt', st)
    return float(m.group(1)) if m else 8.7

def mk_p(txt, cls):
    p = etree.SubElement(pages[0], "p")  # temp attach
    pages[0].remove(p)
    p.text = txt
    if cls: p.set("class", cls)
    return p

report = []
def do_back(pno, prefix, lines):
    page = pages[pno-1]; fs = fs_of_page(page); cpl = CPL.get(fs, 18.14)
    para = find_para(page, prefix)
    if para is None: report.append(f"P{pno:02d} !! back not found: {prefix}"); return
    txt = para.text_content()
    r = split_at(txt, int(lines*cpl), False)
    if r is None: report.append(f"P{pno:02d} !! back no boundary: {prefix}"); return
    head, tail = r
    if not tail.strip(): report.append(f"P{pno:02d} !! back empty tail: {prefix}"); return
    # 头段插入点:若 para 有 cbrk -> 插在 para 前;否则插在其栏首个 cbrk 元素前
    cls = classes(para)
    anchor = para
    if "cbrk" not in cls:
        # 找本栏起点(前方最近的 cbrk 元素)
        body = body_of(page); kids = list(body)
        i = kids.index(para); j = i
        while j > 0 and "cbrk" not in classes(kids[j]): j -= 1
        anchor = kids[j]
    headp = mk_p(head, "")
    anchor.addprevious(headp)
    cls = classes(para)
    if "cont" not in cls: cls.append("cont")
    set_cls(para, cls)
    para.text = tail
    report.append(f"P{pno:02d} back {lines}L {prefix[:10]}: head {len(head)}ch -> prev col end")

def do_fwd(pno, prefix, lines):
    page = pages[pno-1]; fs = fs_of_page(page); cpl = CPL.get(fs, 18.14)
    para = find_para(page, prefix)
    if para is None: report.append(f"P{pno:02d} !! fwd not found: {prefix}"); return
    txt = para.text_content()
    r = split_at(txt, int(lines*cpl), True)
    if r is None: report.append(f"P{pno:02d} !! fwd no boundary: {prefix}"); return
    head, tail = r
    if not head.strip(): report.append(f"P{pno:02d} !! fwd empty head: {prefix}"); return
    para.text = head
    tailp = mk_p(tail, "cont cbrk")
    para.addnext(tailp)
    # 下一个元素(原后栏起点)去 cbrk
    nxt = tailp.getnext()
    if nxt is not None and "cbrk" in classes(nxt):
        cls = classes(nxt); cls.remove("cbrk"); set_cls(nxt, cls)
    report.append(f"P{pno:02d} fwd {lines}L {prefix[:10]}: tail {len(tail)}ch -> next col top")

def move_whole_back(pno, prefix):
    """c2 首段整段并入前栏尾,cbrk 移交下一段"""
    page = pages[pno-1]
    para = find_para(page, prefix)
    if para is None: report.append(f"P{pno:02d} !! mv not found: {prefix}"); return
    cls = classes(para)
    if "cbrk" in cls: cls.remove("cbrk")
    set_cls(para, cls)
    nxt = para.getnext()
    if nxt is not None:
        ncls = classes(nxt)
        if "cbrk" not in ncls: ncls.append("cbrk")
        set_cls(nxt, ncls)
    report.append(f"P{pno:02d} whole-para -> prev col: {prefix[:10]} (cbrk -> next)")

def img_resize(pno, old, new, occ=1):
    page = pages[pno-1]
    k = 0
    for b in page.iter("div"):
        if "photo-block" not in classes(b): continue
        st = b.get("style") or ""
        m = re.search(r'--ph-h:\s*([\d.]+)mm', st)
        if m and abs(float(m.group(1)) - old) < 0.05:
            k += 1
            if k == occ:
                b.set("style", st.replace(f'--ph-h:{m.group(1)}mm', f'--ph-h:{new}mm', 1))
                report.append(f"P{pno:02d} img {old}->{new} (occ{occ})")
                return
    report.append(f"P{pno:02d} !! img {old} occ{occ} not found")

# ============ 执行 ============
img_resize(12, 45.0, 42.0)
do_back(13, "习近平主席指出", 4)
do_fwd(14, "长征精神要“活”起来", 3)
do_fwd(15, "2019年，我作为全国青年代表", 4)
# P22 行距 1.52
b = body_of(pages[21]); b.set("style", (b.get("style") or "").replace("--body-lh:1.55; --line:4.76mm","--body-lh:1.52; --line:4.67mm"))
do_fwd(22, "楚国当时的君主是楚悼王", 1)
# P23 行距 1.46
b = body_of(pages[22]); b.set("style", (b.get("style") or "").replace("--body-lh:1.55; --line:4.76mm","--body-lh:1.46; --line:4.48mm"))
do_back(27, "公元 770 年，杜甫由于过于饥", 3)
do_back(28, "公元 747年，由于“野无遗贤”", 2)
do_fwd(29, "杜甫的悲哀，是生错了时代", 2)
do_fwd(34, "地下建筑看陕西，地上建筑看山西", 2)
do_back(35, "1917年，北京城外闯入", 2)
img_resize(36, 37.2, 30.0, occ=2)
do_back(36, "遭日本宪兵挟持", 1)
do_back(40, "车队行至高山", 3)
do_back(41, "他们本来是坐在雕花木椅", 2)
do_fwd(41, "教授们穿着妻儿做的布鞋", 4)
do_back(42, "但如果没人坐", 3)
do_fwd(43, "下葬的日子很快到来", 1)
# P46
b = body_of(pages[45]); b.set("style", "--body-lh:1.58; --line:4.85mm")
img_resize(46, 30.0, 65.0); img_resize(46, 48.9, 60.0); img_resize(46, 40.1, 52.0)
move_whole_back(46, "李健熙是李秉喆的三子")
# P47
b = body_of(pages[46]); b.set("style", "--body-lh:1.58; --line:4.85mm")
img_resize(47, 41.3, 75.0); img_resize(47, 34.7, 42.0); img_resize(47, 51.2, 58.0); img_resize(47, 45.7, 52.0)
do_back(48, "田径赛场上演速度与力量", 2)
img_resize(49, 130.0, 150.0)
do_fwd(49, "本届亚运会全程多项纪录", 3)
do_back(50, "五颜六色的小玉米", 3)
do_back(50, "实际上，不止文玩玉米", 3)
do_back(51, "杨爷爷自己说过", 2)
do_fwd(51, "正如上文所写", 2)
img_resize(54, 70.0, 62.0)
do_back(54, "出狱后，刘晓庆从龙套角色演起", 2)
do_fwd(55, "转折发生在1985年", 2)
do_fwd(55, "“王家卫导演来找我拍电视剧了", 3)
# P56: cbrk 从 SUB《亚洲雄风》移至其首段拆点
p56 = pages[55]
sub = find_para(p56, "《亚洲雄风》", "h2")
if sub is not None:
    cls = classes(sub)
    if "cbrk" in cls: cls.remove("cbrk"); set_cls(sub, cls)
    para = find_para(p56, "《亚洲雄风》其实并非北京亚运会的")
    if para is not None:
        txt = para.text_content()
        head, tail = split_at(txt, 34, False)
        para.text = head
        tailp = mk_p(tail, "cont cbrk")
        para.addnext(tailp)
        report.append(f"P56 sub-move 《亚洲雄风》: head {len(head)}ch stays, tail {len(tail)}ch cbrk")
do_back(57, "站在鸟巢的球形舞台", 4)
do_back(61, "其次，我想要分享的是", 2)
do_fwd(61, "其一，知识掌握不够熟练", 2)
do_back(62, "最后，我想要强调的是", 3)
do_back(62, "接着，我要强调的是", 3)
img_resize(63, 80.0, 72.0)
do_back(66, "读图，是地理学习的基本功", 2)
do_back(67, "高中学习容易出现一种误区", 2)
do_back(68, "开始只有三五个人跟着", 4)
do_fwd(68, "这道风景，与寻常的跑操并不一样", 2)
# P69: SUB 二 前移 + 拆段
p69 = pages[68]
sub = find_para(p69, "二", "h2")
if sub is not None and sub.text_content().strip() == "二":
    cls = classes(sub)
    if "cbrk" in cls: cls.remove("cbrk"); set_cls(sub, cls)
    para = find_para(p69, "骄阳冷雨不折少年锐气")
    if para is not None:
        txt = para.text_content()
        head, tail = split_at(txt, 36, False)
        para.text = head
        tailp = mk_p(tail, "cont cbrk")
        para.addnext(tailp)
        report.append(f"P69 sub-move 二: head {len(head)}ch stays, tail {len(tail)}ch cbrk")
do_back(69, "一万年太久 只争朝夕", 2)
img_resize(19, 82.5, 95.0)
# P19 字号 9.3
b = body_of(pages[18]); st = b.get("style") or ""
b.set("style", (st + "; --body-font:9.3pt").strip("; "))

out = etree.tostring(doc, method="html", encoding="unicode")
with open(F, "w", encoding="utf-8", newline=chr(10)) as fh:
    fh.write(out)
print(chr(10).join(report))
print("SAVED")
