# -*- coding: utf-8 -*-
"""2611.html 修正脚本（一次性）：
1. .body 加 column-fill:auto；新增 .cbrk { break-before: column }
2. 每栏起点元素加 class="cbrk"（钉死分栏切分点，引擎无关）
3. 洞/图 --ph-w/--ph-h 同步放大（尾页/均衡留白），33 处 top 重写
4. P35 两段移入 P36
每个替换断言恰好命中一次。
"""
import io, re, sys

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = io.open(F, encoding="utf-8").read()
n0 = src

def rep(old, new, tag):
    global src
    c = src.count(old)
    assert c == 1, f"[{tag}] 命中 {c} 次（应为1）: {old[:60]!r}"
    src = src.replace(old, new)
    print(f"  ok {tag}")

# ---------- 1. CSS ----------
rep(""".body {
  flex: 1 1 auto;
  min-height: 0;
  position: relative;
  column-count: 3;
  column-gap: 5.5mm;
  font-size: var(--body-font);
  line-height: var(--body-lh);
  margin-bottom: 5.8mm;
}""",
""".body {
  flex: 1 1 auto;
  min-height: 0;
  position: relative;
  column-count: 3;
  column-gap: 5.5mm;
  column-fill: auto;
  font-size: var(--body-font);
  line-height: var(--body-lh);
  margin-bottom: 5.8mm;
}""", "css column-fill")

rep("""/* ---------- 空行：一个 = 一行正文（4.57mm） ---------- */""",
"""/* ---------- 栏切分标记：钉死每栏起点（分栏引擎无关） ---------- */
.cbrk { break-before: column; }

/* ---------- 空行：一个 = 一行正文（4.57mm） ---------- */""", "css cbrk")

# ---------- 2. 分栏标记 ----------
def add_cls(anchor, tag):
    """把 <p>锚点 / <h2 ...> / <div class="hole" ...> 加上 cbrk"""
    global src
    # p 无属性
    old = "<p>" + anchor
    if old in src:
        rep(old, '<p class="cbrk">' + anchor, tag); return
    # p 已有属性
    m = re.search(r'<p class="([^"]*)">' + re.escape(anchor), src)
    if m:
        rep(f'<p class="{m.group(1)}">' + anchor, f'<p class="{m.group(1)} cbrk">' + anchor, tag); return
    # h2 subhead
    m = re.search(r'<h2 class="subhead">([^<]*)</h2>\s*<p>' + re.escape(anchor), src)
    if m:
        rep('<h2 class="subhead">' + m.group(1) + '</h2>', '<h2 class="subhead cbrk">' + m.group(1) + '</h2>', tag); return
    raise AssertionError(f"[{tag}] 未找到锚点: {anchor[:40]!r}")

def add_cls_hole(anchor_para_before_hole, hole_style, tag):
    """在 anchor 段后的 hole div 加 cbrk（洞成为栏顶）"""
    global src
    i = src.find(anchor_para_before_hole)
    assert i >= 0, f"[{tag}] 段锚点未找到"
    j = src.find(hole_style, i)
    assert j >= 0 and j - i < 600, f"[{tag}] hole 未找到或过远"
    pre = '<div class="hole" style="'
    assert src[j-25:j] == pre, f"[{tag}] 上下文异常: {src[j-30:j+40]!r}"
    src = src[:j-25] + '<div class="hole cbrk" style="' + src[j:]
    print(f"  ok {tag}")

# P16 栏2起：士人阶级
add_cls("士人阶级在此之前的地位都极为尴尬", "P16 brk")
# P17 栏2起：吴起变法之所以失败
add_cls("吴起变法之所以失败，便是对于变法这一事业", "P17 brk")
# P18 栏2起：与之相同的变法还有燕国变法
add_cls("与之相同的变法还有燕国变法", "P18 brk")
# P19 栏2起：商鞅变法的很多法令
add_cls("商鞅变法的很多法令就是赢师隰先提出的", "P19 brk")
# P20 栏2起：湖北省博物馆
add_cls("湖北省博物馆的镇馆之宝云梦睡虎地秦简", "P20 brk")
# P21 栏2起：但可惜，他生于弱韩
add_cls("但可惜，他生于弱韩", "P21 brk")
# P22 栏2起：subhead 2（锚：其前段尾"尽量全面。"之后……用其标志段）
i = src.find('<h2 class="subhead">2</h2>')
assert i > 0
rep('<h2 class="subhead">2</h2>', '<h2 class="subhead cbrk">2</h2>', "P22 brk")
# P23 栏2起：subhead 3
i = src.find('<h2 class="subhead">3</h2>')
assert i > 0
rep('<h2 class="subhead">3</h2>', '<h2 class="subhead cbrk">3</h2>', "P23 brk")
# P24 栏2起：他的长子叫杜宗武
add_cls("他的长子叫杜宗武", "P24 brk")
# P25 栏2起：哥哥你走西口
add_cls("哥哥你走西口，", "P25 brk")
# P26 栏2起：应县木塔是目前
add_cls("应县木塔是目前中国保存最好的木质古建筑之一", "P26 brk")
# P27 栏2起：hole 雪中关外（其后是 subhead 三）
add_cls_hole("他们无家可归了。", "--ph-w:55mm; --ph-h:36.6mm;", "P27 brk")
# P35 栏2起：hole 李秉喆（28x36.6）；栏3起：为实现发展本国制造业
add_cls_hole("一举结束了韩国长期以来进口白糖的历史", "--ph-w:28mm; --ph-h:36.6mm;", "P35 brk1")
add_cls("为实现发展本国制造业的目标", "P35 brk2")
# P36 栏2起：hole 政商（42x45.7）；栏3起：hole 国旗（55.67x36.6）
add_cls_hole("造成了一种恶性的循环。", "--ph-w:42mm; --ph-h:45.7mm;", "P36 brk1")
add_cls_hole("如果没有这些大财阀", "--ph-w:55.67mm; --ph-h:36.6mm;", "P36 brk2")
# P37 栏2起：赛场之内；栏3起：竞技之外
add_cls("赛场之内，竞技争锋轮番上演", "P37 brk1")
add_cls("竞技之外，赛场涌动着超越胜负的温情", "P37 brk2")
# P38 栏2起：五颜六色的小玉米；栏3起：据央视新闻
add_cls("五颜六色的小玉米吸引了许多消费者的眼球", "P38 brk1")
add_cls("据央视新闻报道", "P38 brk2")
# P39 栏2起：这位“公园大爷”叫杨树荣；栏3起：走红之后的杨树荣
add_cls("这位“公园大爷”叫杨树荣", "P39 brk1")
add_cls("走红之后的杨树荣，日程忽然满了起来", "P39 brk2")

# ---------- 3. P35 两段移入 P36 ----------
m = re.search(r'    <p>剧本总是同样的，全斗焕，以及他的挚友、下一任总统卢泰愚，都得到了三星集团的好处，[^<]*</p>\n\n    <p>李健熙是李秉喆的三子，1987年起接替去世的李秉喆，成为三星集团第二任会长。</p>\n\n', src)
assert m, "P35 两段未匹配"
two = m.group(0).rstrip("\n")  # 含两段与中间空行
src = src.replace(m.group(0), "", 1)
print("  ok P35->P36 剪切两段")
# 插入 P36 body 开头（朴槿惠段之前）
anchor36 = '    <p>朴正熙的女儿朴槿惠也曾担任韩国总统'
i = src.find(anchor36)
assert i > 0
src = src[:i] + two + "\n\n" + src[i:]
print("  ok P35->P36 插入两段")

io.open(F, "w", encoding="utf-8", newline="\n").write(src)
print("stage1 done, bytes:", len(n0), "->", len(src))
