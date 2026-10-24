# -*- coding: utf-8 -*-
"""2611.html stage2：洞/图尺寸放大 + top 重写（洞与图逐字一致）"""
import io

F = r"D:\CloudyInkForge\pentium\2611\2611.html"
src = io.open(F, encoding="utf-8").read()

def rep(old, new, tag, count=1):
    global src
    c = src.count(old)
    assert c == count, f"[{tag}] 命中 {c} 次（应为{count}）: {old[:70]!r}"
    src = src.replace(old, new)
    print(f"  ok {tag}")

# ---------- P16 鼎 58x54.8 -> 66x72.4（洞+图，top 64.0 不变） ----------
rep("--ph-w:58mm; --ph-h:54.8mm", "--ph-w:66mm; --ph-h:72.4mm", "P16 鼎 x2", count=2)

# ---------- P17 爵 40x54.8 -> 48x66.8，top 50.3 -> 45.8 ----------
rep("只在湘鄂山间留下了几声不甘的悲鸣。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:40mm; --ph-h:54.8mm;\"></div>",
    "只在湘鄂山间留下了几声不甘的悲鸣。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:48mm; --ph-h:66.8mm;\"></div>",
    "P17 爵洞")
rep("--ph-w:40mm; --ph-h:54.8mm; top:50.3mm;", "--ph-w:48mm; --ph-h:66.8mm; top:45.8mm;", "P17 爵图")

# ---------- P19 铜像 36x54.8 -> 44x73.1，top 150.8 -> 132.3 ----------
rep("因此秦国人长期被六国所歧视。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:36mm; --ph-h:54.8mm;\"></div>",
    "因此秦国人长期被六国所歧视。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:44mm; --ph-h:73.1mm;\"></div>",
    "P19 铜像洞")
rep("--ph-w:36mm; --ph-h:54.8mm; top:150.8mm;", "--ph-w:44mm; --ph-h:73.1mm; top:132.3mm;", "P19 铜像图")

# ---------- P20 方升 尺寸不变，top 68.6 -> 91.3 ----------
rep("--ph-w:36mm; --ph-h:54.8mm; top:68.6mm;", "--ph-w:36mm; --ph-h:54.8mm; top:91.3mm;", "P20 方升图")

# ---------- P22 top：饮中八仙 71->70.1；雕像 135->97.6 ----------
rep("--ph-w:86.25mm; --ph-h:64.0mm; top:71mm;", "--ph-w:86.25mm; --ph-h:64.0mm; top:70.1mm;", "P22 饮中图")
rep("--ph-w:41mm; --ph-h:54.8mm; top:135mm;", "--ph-w:41mm; --ph-h:54.8mm; top:97.6mm;", "P22 雕像图")

# ---------- P23 top：唐画像 59.4->54.8；草堂坐像 141.7->154.8 ----------
rep("--ph-w:39mm; --ph-h:54.8mm; top:59.4mm;", "--ph-w:39mm; --ph-h:54.8mm; top:54.8mm;", "P23 唐画像图")
rep("--ph-w:86.25mm; --ph-h:54.8mm; top:141.7mm;", "--ph-w:86.25mm; --ph-h:54.8mm; top:154.8mm;", "P23 草堂图")

# ---------- P24 top：文官 57.3->56.1；望月 158.4->157.5；书影 98.4->38.4 ----------
rep("--ph-w:36mm; --ph-h:54.8mm; top:57.3mm;", "--ph-w:36mm; --ph-h:54.8mm; top:56.1mm;", "P24 文官图")
rep("--ph-w:86.25mm; --ph-h:45.7mm; top:158.4mm;", "--ph-w:86.25mm; --ph-h:45.7mm; top:157.5mm;", "P24 望月图")
rep("--ph-w:70mm; --ph-h:45.7mm; top:98.4mm;", "--ph-w:70mm; --ph-h:45.7mm; top:38.4mm;", "P24 书影图")

# ---------- P25 铜钱 40x54.8 -> 50x68.6 top 57.3->56.6；王维 54.8->64 top 75.6->69.9 ----------
rep("供后人瞻仰，财力可见一斑。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:40mm; --ph-h:54.8mm;\"></div>",
    "供后人瞻仰，财力可见一斑。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:50mm; --ph-h:68.6mm;\"></div>",
    "P25 铜钱洞")
rep("--ph-w:40mm; --ph-h:54.8mm; top:57.3mm;", "--ph-w:50mm; --ph-h:68.6mm; top:56.6mm;", "P25 铜钱图")
rep("惊惊天阴谋", "惊惊天阴谋", "noop", count=0) if False else None
rep("讨论着他们的惊天阴谋。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:86.25mm; --ph-h:54.8mm;\"></div>",
    "讨论着他们的惊天阴谋。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:86.25mm; --ph-h:64mm;\"></div>",
    "P25 王维洞")
rep("--ph-w:86.25mm; --ph-h:54.8mm; top:75.6mm;", "--ph-w:86.25mm; --ph-h:64mm; top:69.9mm;", "P25 王维图")

# ---------- P26 鹳雀楼 54.8->64 top 41.1->40.8；飞虹塔 top 172.1->180.5；木塔月夜 36x54.8->46x70.4 top 27.4->27.3；晋祠 top 114.8->130.1 ----------
rep("凝碧池头奏管弦。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:86.25mm; --ph-h:54.8mm;\"></div>",
    "凝碧池头奏管弦。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:86.25mm; --ph-h:64mm;\"></div>",
    "P26 鹳雀楼洞")
rep("--ph-w:86.25mm; --ph-h:54.8mm; top:41.1mm;", "--ph-w:86.25mm; --ph-h:64mm; top:40.8mm;", "P26 鹳雀楼图")
rep("--ph-w:68mm; --ph-h:45.7mm; top:172.1mm;", "--ph-w:68mm; --ph-h:45.7mm; top:180.5mm;", "P26 飞虹塔图")
rep("阶前留下了一个个踩得坚实的脚印。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:36mm; --ph-h:54.8mm;\"></div>",
    "阶前留下了一个个踩得坚实的脚印。</p>\n    <p class=\"gap\"></p>\n    <div class=\"hole\" style=\"--ph-w:46mm; --ph-h:70.4mm;\"></div>",
    "P26 木塔洞")
rep("--ph-w:36mm; --ph-h:54.8mm; top:27.4mm;", "--ph-w:46mm; --ph-h:70.4mm; top:27.3mm;", "P26 木塔图")
rep("--ph-w:68mm; --ph-h:45.7mm; top:114.8mm;", "--ph-w:68mm; --ph-h:45.7mm; top:130.1mm;", "P26 晋祠图")

# ---------- P27 top：释迦 43.6->43.1；雪中关外 22.9->0 ----------
rep("--ph-w:24mm; --ph-h:54.8mm; top:43.6mm;", "--ph-w:24mm; --ph-h:54.8mm; top:43.1mm;", "P27 释迦图")
rep("--ph-w:55mm; --ph-h:36.6mm; top:22.9mm;", "--ph-w:55mm; --ph-h:36.6mm; top:0mm;", "P27 雪中图")

# ---------- P35 top：梅瓶 41.1->41.3；李承晚 124.1->119.3；李健熙 105.1->77.8（李秉喆 0 不变） ----------
rep("--ph-w:40mm; --ph-h:54.8mm; top:41.1mm;", "--ph-w:40mm; --ph-h:54.8mm; top:41.3mm;", "P35 梅瓶图")
rep("--ph-w:46mm; --ph-h:54.8mm; top:124.1mm;", "--ph-w:46mm; --ph-h:54.8mm; top:119.3mm;", "P35 李承晚图")
rep("--ph-w:55.67mm; --ph-h:45.7mm; top:105.1mm;", "--ph-w:55.67mm; --ph-h:45.7mm; top:77.8mm;", "P35 李健熙图")

# ---------- P36 李在镕 34x45.7->44x73.1 top 82.3->119.1；政商 42x45.7->52x73.1 top 4->0；大楼 27.4->41.4 top 86.9->110.1；国旗 36.6->73.1 top 4->0；海报 32x45.7->44x73.1 top 82.3->114.8 ----------
rep('<div class="hole" style="--ph-w:34mm; --ph-h:45.7mm;"></div>',
    '<div class="hole" style="--ph-w:44mm; --ph-h:73.1mm;"></div>', "P36 李在镕洞")
rep("--ph-w:34mm; --ph-h:45.7mm; top:82.3mm;", "--ph-w:44mm; --ph-h:73.1mm; top:119.1mm;", "P36 李在镕图")
rep('<div class="hole cbrk" style="--ph-w:42mm; --ph-h:45.7mm;"></div>',
    '<div class="hole cbrk" style="--ph-w:52mm; --ph-h:73.1mm;"></div>', "P36 政商洞")
rep("--ph-w:42mm; --ph-h:45.7mm; top:4mm;", "--ph-w:52mm; --ph-h:73.1mm; top:0mm;", "P36 政商图")
rep('<div class="hole" style="--ph-w:55.67mm; --ph-h:27.4mm;"></div>',
    '<div class="hole" style="--ph-w:55.67mm; --ph-h:41.4mm;"></div>', "P36 大楼洞")
rep("--ph-w:55.67mm; --ph-h:27.4mm; top:86.9mm;", "--ph-w:55.67mm; --ph-h:41.4mm; top:110.1mm;", "P36 大楼图")
rep('<div class="hole cbrk" style="--ph-w:55.67mm; --ph-h:36.6mm;"></div>',
    '<div class="hole cbrk" style="--ph-w:55.67mm; --ph-h:73.1mm;"></div>', "P36 国旗洞")
rep("--ph-w:55.67mm; --ph-h:36.6mm; top:4mm;", "--ph-w:55.67mm; --ph-h:73.1mm; top:0mm;", "P36 国旗图")
rep('<div class="hole" style="--ph-w:32mm; --ph-h:45.7mm;"></div>',
    '<div class="hole" style="--ph-w:44mm; --ph-h:73.1mm;"></div>', "P36 海报洞")
rep("--ph-w:32mm; --ph-h:45.7mm; top:82.3mm;", "--ph-w:44mm; --ph-h:73.1mm; top:114.8mm;", "P36 海报图")

# ---------- P37 东海道 top 137.1 -> 132.6 ----------
rep("--ph-w:55.67mm; --ph-h:36.6mm; top:137.1mm;", "--ph-w:55.67mm; --ph-h:36.6mm; top:132.6mm;", "P37 东海道图")

# ---------- P38 玉米摊 28x36.6 -> 55.67x91.4 top 36.6->36.5；朝珠 35x45.7 -> 55.67x91.4 top 27.4->45.8 ----------
rep('<div class="hole" style="--ph-w:28mm; --ph-h:36.6mm;"></div>',
    '<div class="hole" style="--ph-w:55.67mm; --ph-h:91.4mm;"></div>', "P38 玉米洞")
rep("--ph-w:28mm; --ph-h:36.6mm; top:36.6mm;", "--ph-w:55.67mm; --ph-h:91.4mm; top:36.5mm;", "P38 玉米图")
rep('<div class="hole" style="--ph-w:35mm; --ph-h:45.7mm;"></div>',
    '<div class="hole" style="--ph-w:55.67mm; --ph-h:91.4mm;"></div>', "P38 朝珠洞")
rep("--ph-w:35mm; --ph-h:45.7mm; top:27.4mm;", "--ph-w:55.67mm; --ph-h:91.4mm; top:45.8mm;", "P38 朝珠图")

# ---------- P39 红莲游鱼 34x54.8 -> 55.67x100.5 top 54.8->50.3 ----------
rep('<div class="hole" style="--ph-w:34mm; --ph-h:54.8mm;"></div>',
    '<div class="hole" style="--ph-w:55.67mm; --ph-h:100.5mm;"></div>', "P39 红莲洞")
rep("--ph-w:34mm; --ph-h:54.8mm; top:54.8mm;", "--ph-w:55.67mm; --ph-h:100.5mm; top:50.3mm;", "P39 红莲图")

io.open(F, "w", encoding="utf-8", newline="\n").write(src)
print("stage2 done")
