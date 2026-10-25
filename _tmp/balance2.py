# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from lxml import html as LH
from lxml import etree

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = open(F, encoding="utf-8").read()
doc = LH.fromstring(src)
pages = [e for e in doc.iter("div") if "page" in (e.get("class") or "").split()]
CPL = {8.7:18.14, 9.2:17.14, 9.3:16.96}
STRONG = "。！？；"
WEAK = "，、：”）》……"
report = []

def classes(el): return (el.get("class") or "").split()
def set_cls(el, cls): el.set("class", " ".join(cls))
def find_para(page, prefix, tag="p"):
    for p in page.iter(tag):
        if (p.text_content() or "").strip().startswith(prefix): return p
    return None
def fs_of(page):
    body = [e for e in page.iter("div") if "body" in (e.get("class") or "").split()][0]
    m = re.search(r'--body-font:\s*([\d.]+)pt', body.get("style") or "")
    return float(m.group(1)) if m else 8.7
def split_at(txt, tchars, from_end):
    n = len(txt); pos = n - tchars if from_end else tchars
    pos = max(2, min(n-2, pos)); best, bd = None, 999
    for i in range(max(2,pos-16), min(n-1,pos+17)):
        if txt[i-1] in STRONG:
            d = abs(i-pos)
            if d < bd: bd, best = d, i
    if best is None:
        for i in range(max(2,pos-16), min(n-1,pos+17)):
            if txt[i-1] in WEAK:
                d = abs(i-pos)
                if d < bd: bd, best = d, i
    return None if best is None else (txt[:best], txt[best:])
def mk_p(txt, cls):
    p = etree.Element("p"); p.text = txt
    if cls: p.set("class", cls)
    return p
def do_back(pno, prefix, lines):
    page = pages[pno-1]; cpl = CPL.get(fs_of(page), 18.14)
    para = find_para(page, prefix)
    if para is None: report.append(f"P{pno:02d} !! back nf: {prefix}"); return
    txt = para.text_content(); r = split_at(txt, int(lines*cpl), False)
    if r is None: report.append(f"P{pno:02d} !! back no-bd: {prefix}"); return
    head, tail = r
    if not tail.strip(): report.append(f"P{pno:02d} !! back empty-tail: {prefix}"); return
    cls = classes(para); anchor = para
    if "cbrk" not in cls:
        body = [e for e in page.iter("div") if "body" in (e.get("class") or "").split()][0]
        kids = list(body); j = kids.index(para)
        while j > 0 and "cbrk" not in classes(kids[j]): j -= 1
        anchor = kids[j]
    anchor.addprevious(mk_p(head, ""))
    if "cont" not in cls: cls.append("cont")
    set_cls(para, cls); para.text = tail
    report.append(f"P{pno:02d} back {lines}L {prefix[:10]} head={len(head)}ch")
def do_fwd(pno, prefix, lines):
    page = pages[pno-1]; cpl = CPL.get(fs_of(page), 18.14)
    para = find_para(page, prefix)
    if para is None: report.append(f"P{pno:02d} !! fwd nf: {prefix}"); return
    txt = para.text_content(); r = split_at(txt, int(lines*cpl), True)
    if r is None: report.append(f"P{pno:02d} !! fwd no-bd: {prefix}"); return
    head, tail = r
    if not head.strip(): report.append(f"P{pno:02d} !! fwd empty-head: {prefix}"); return
    para.text = head
    tailp = mk_p(tail, "cont cbrk"); para.addnext(tailp)
    nxt = tailp.getnext()
    if nxt is not None and "cbrk" in classes(nxt):
        cls = classes(nxt); cls.remove("cbrk"); set_cls(nxt, cls)
        report.append(f"P{pno:02d} fwd {lines}L {prefix[:10]} tail={len(tail)}ch (next cbrk stripped)")
    else:
        # 继续向后找第一个带 cbrk 的元素并剥离
        n2 = nxt
        while n2 is not None and "cbrk" not in classes(n2): n2 = n2.getnext()
        if n2 is not None:
            cls = classes(n2); cls.remove("cbrk"); set_cls(n2, cls)
            report.append(f"P{pno:02d} fwd {lines}L {prefix[:10]} tail={len(tail)}ch (later cbrk stripped)")
        else:
            report.append(f"P{pno:02d} fwd {lines}L {prefix[:10]} tail={len(tail)}ch (NO cbrk found!)")
def img_resize(pno, old, new, occ=1):
    page = pages[pno-1]; k = 0
    for b in page.iter("div"):
        if "photo-block" not in classes(b): continue
        m = re.search(r'--ph-h:\s*([\d.]+)mm', b.get("style") or "")
        if m and abs(float(m.group(1)) - old) < 0.05:
            k += 1
            if k == occ:
                b.set("style", b.get("style").replace(f'--ph-h:{m.group(1)}mm', f'--ph-h:{new}mm', 1))
                report.append(f"P{pno:02d} img {old}->{new}")
                return
    report.append(f"P{pno:02d} !! img {old} nf")

# --- A. P14 修复:合并误拆,再从 c1 真末段拆 ---
p14 = pages[13]
p9 = find_para(p14, "长征精神要“活”起来")
p10 = find_para(p14, "必须坚持理论与实践相")
if p9 is not None and p10 is not None:
    p9.text = (p9.text_content() + p10.text_content())
    p10.getparent().remove(p10)
    set_cls(p9, [c for c in classes(p9) if c not in ("cont","cbrk")])
    report.append("P14 merged back 长征精神要活")
do_fwd(14, "和学生谈起长征", 3)

# --- B. P29 回退 ---
p29 = pages[28]
p12 = find_para(p29, "杜甫的悲哀，是生错了时代")
p13 = find_para(p29, "他与他的祖父没有什么")
if p12 is not None and p13 is not None:
    p12.text = (p12.text_content() + p13.text_content())
    p13.getparent().remove(p13)
    set_cls(p12, [c for c in classes(p12) if c not in ("cont","cbrk")])
    report.append("P29 reverted 杜甫的悲哀")
else:
    report.append("P29 !! revert failed")

# --- C. P34 回退 + 图缩 ---
p34 = pages[33]
pa = find_para(p34, "地下建筑看陕西")
pb = find_para(p34, "而现在，山西的文化历")
if pa is not None and pb is not None:
    pa.text = (pa.text_content() + pb.text_content())
    pb.getparent().remove(pb)
    cls = classes(pa)
    set_cls(pa, cls)
    report.append("P34 reverted 地下建筑")
img_resize(34, 41.3, 36.0)
img_resize(34, 44.9, 40.0)

# --- D. P55 修复 ---
p55 = pages[54]
p4 = find_para(p55, "转折发生在1985年")
p5 = find_para(p55, "从此，我们就看见了荧")
if p4 is not None and p5 is not None:
    full = p4.text_content() + p5.text_content()
    head, tail = split_at(full, int(7*16.96), False)
    if head and tail:
        p4.text = head; p5.text = tail
        report.append(f"P55 re-split 转折: a={len(head)} b={len(tail)}")
p10 = find_para(p55, "“王家卫导演来找我拍电视剧了")
p11 = find_para(p55, "但王家卫的邀请也足以")
if p10 is not None and p11 is not None:
    p10.text = (p10.text_content() + p11.text_content())
    p11.getparent().remove(p11)
    set_cls(p10, [c for c in classes(p10) if c not in ("cont","cbrk")])
    report.append("P55 merged back 王家卫")
p13 = find_para(p55, "后来的故事，大家就都知道了")
if p13 is not None:
    cls = classes(p13)
    if "cbrk" in cls: cls.remove("cbrk"); set_cls(p13, cls); report.append("P55 stripped 后来的故事 cbrk")

# --- E~K ---
img_resize(9, 60.0, 52.0)
do_back(27, "结果杜甫由于过度", 1)
do_back(46, "朴正熙的女儿朴槿惠", 2)
img_resize(47, 75.0, 85.0)
do_back(48, "火炬传递环节层层递进", 2)
do_back(43, "继续向山上走", 1)

# --- L. P19 七律移 c2 + img 115 ---
p19 = pages[18]
sub7 = None
for h in p19.iter("h2"):
    if (h.text_content() or "").strip().startswith("七律·长征"): sub7 = h; break
subX = None
for h in p19.iter("h2"):
    if (h.text_content() or "").strip().startswith("西江月·湘江血"): subX = h; break
if sub7 is not None and subX is not None:
    block = [sub7]
    n = sub7.getnext()
    while n is not None and n is not subX:
        block.append(n); n = n.getnext()
    for el in block: subX.addprevious(el)
    c7 = classes(sub7)
    if "cbrk" not in c7: c7.append("cbrk"); set_cls(sub7, c7)
    cX = classes(subX)
    if "cbrk" in cX: cX.remove("cbrk"); set_cls(subX, cX)
    report.append(f"P19 moved 七律 block ({len(block)} els) to c2")
img_resize(19, 95.0, 115.0)

out = etree.tostring(doc, method="html", encoding="unicode")
if not out.startswith("<!DOCTYPE"):
    out = "<!DOCTYPE html>\n" + out
with open(F, "w", encoding="utf-8", newline=chr(10)) as fh: fh.write(out)
print(chr(10).join(report)); print("SAVED")
