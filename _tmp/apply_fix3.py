# -*- coding: utf-8 -*-
"""stage3：P22/P27 cbrk 前移 + 全部图 top 按 DOM 实测校准"""
import io

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = io.open(F, encoding="utf-8").read()

def rep(old, new, tag, count=1):
    global src
    c = src.count(old)
    assert c == count, f"[{tag}] 命中 {c} 次: {old[:70]!r}"
    src = src.replace(old, new)
    print(f"  ok {tag}")

# ---------- P22：cbrk 从 sub2 移到 p很多人都说 ----------
rep('<h2 class="subhead cbrk">2</h2>', '<h2 class="subhead">2</h2>', "P22 sub2 去 cbrk")
rep('<p>很多人都说，杜甫是个伟大的现实主义诗人',
    '<p class="cbrk">很多人都说，杜甫是个伟大的现实主义诗人', "P22 brk->很多人都说")

# ---------- P27：cbrk 从 hole雪中关外 移到 p他们是真正的流浪者 ----------
rep('<div class="hole cbrk" style="--ph-w:55mm; --ph-h:36.6mm;"></div>',
    '<div class="hole" style="--ph-w:55mm; --ph-h:36.6mm;"></div>', "P27 洞去 cbrk")
rep('<p>他们是真正的流浪者。</p>', '<p class="cbrk">他们是真正的流浪者。</p>', "P27 brk->他们是真正的流浪者")

# ---------- top 校准（DOM 实测） ----------
rep("--ph-w:48mm; --ph-h:66.8mm; top:45.8mm;", "--ph-w:48mm; --ph-h:66.8mm; top:45.7mm;", "P17 爵 45.7")
rep("--ph-w:44mm; --ph-h:73.1mm; top:132.3mm;", "--ph-w:44mm; --ph-h:73.1mm; top:132.6mm;", "P19 铜像 132.6")
rep("--ph-w:36mm; --ph-h:54.8mm; top:91.3mm;", "--ph-w:36mm; --ph-h:54.8mm; top:91.4mm;", "P20 方升 91.4")
rep("--ph-w:39mm; --ph-h:54.8mm; top:54.8mm;", "--ph-w:39mm; --ph-h:54.8mm; top:59.4mm;", "P23 唐画像 59.4")
rep("--ph-w:86.25mm; --ph-h:54.8mm; top:154.8mm;", "--ph-w:86.25mm; --ph-h:54.8mm; top:167mm;", "P23 草堂 167")
rep("--ph-w:36mm; --ph-h:54.8mm; top:56.1mm;", "--ph-w:36mm; --ph-h:54.8mm; top:57.3mm;", "P24 文官 57.3")
rep("--ph-w:86.25mm; --ph-h:45.7mm; top:157.5mm;", "--ph-w:86.25mm; --ph-h:45.7mm; top:158.4mm;", "P24 望月 158.4")
rep("--ph-w:70mm; --ph-h:45.7mm; top:38.4mm;", "--ph-w:70mm; --ph-h:45.7mm; top:98.4mm;", "P24 书影 98.4")
rep("--ph-w:50mm; --ph-h:68.6mm; top:56.6mm;", "--ph-w:50mm; --ph-h:68.6mm; top:57.3mm;", "P25 铜钱 57.3")
rep("--ph-w:86.25mm; --ph-h:64mm; top:69.9mm;", "--ph-w:86.25mm; --ph-h:64mm; top:71mm;", "P25 王维 71")
rep("--ph-w:86.25mm; --ph-h:64mm; top:40.8mm;", "--ph-w:86.25mm; --ph-h:64mm; top:41.1mm;", "P26 鹳雀楼 41.1")
rep("--ph-w:68mm; --ph-h:45.7mm; top:180.5mm;", "--ph-w:68mm; --ph-h:45.7mm; top:181.3mm;", "P26 飞虹塔 181.3")
rep("--ph-w:46mm; --ph-h:70.4mm; top:27.3mm;", "--ph-w:46mm; --ph-h:70.4mm; top:27.4mm;", "P26 木塔 27.4")
rep("--ph-w:68mm; --ph-h:45.7mm; top:130.1mm;", "--ph-w:68mm; --ph-h:45.7mm; top:130.4mm;", "P26 晋祠 130.4")
rep("--ph-w:40mm; --ph-h:54.8mm; top:41.3mm;", "--ph-w:40mm; --ph-h:54.8mm; top:41.1mm;", "P35 梅瓶 41.1")
rep("--ph-w:46mm; --ph-h:54.8mm; top:119.3mm;", "--ph-w:46mm; --ph-h:54.8mm; top:124.1mm;", "P35 李承晚 124.1")
rep("--ph-w:55.67mm; --ph-h:45.7mm; top:77.8mm;", "--ph-w:55.67mm; --ph-h:45.7mm; top:96mm;", "P35 李健熙 96")
rep("--ph-w:44mm; --ph-h:73.1mm; top:119.1mm;", "--ph-w:44mm; --ph-h:73.1mm; top:123.4mm;", "P36 李在镕 123.4")
rep("--ph-w:55.67mm; --ph-h:36.6mm; top:132.6mm;", "--ph-w:55.67mm; --ph-h:36.6mm; top:137.1mm;", "P37 东海道 137.1")
rep("--ph-w:55.67mm; --ph-h:91.4mm; top:36.5mm;", "--ph-w:55.67mm; --ph-h:91.4mm; top:36.6mm;", "P38 玉米 36.6")
rep("--ph-w:55.67mm; --ph-h:91.4mm; top:45.8mm;", "--ph-w:55.67mm; --ph-h:91.4mm; top:45.7mm;", "P38 朝珠 45.7")
rep("--ph-w:55.67mm; --ph-h:100.5mm; top:50.3mm;", "--ph-w:55.67mm; --ph-h:100.5mm; top:54.9mm;", "P39 红莲 54.9")

io.open(F, "w", encoding="utf-8", newline="\n").write(src)
print("stage3 done")
