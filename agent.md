# agent.md（AI 看）

## 0. 最高优先级与适用范围

1. 本文件是 AI 执行排版的唯一规则。与历史文件、口头说明、旧 HTML 冲突时，以 **本文件 + `template/` 中对应模板** 为准。
2. AI 只拥有第 1 节列出的三项权限。未明确要求构建/修改 HTML 时，读完必要说明即停止，不输出无关解释。
3. 任何一项硬性约束不满足，即视为任务未完成。

## 1. 权限（仅此三项，仅在明确要求时执行）

1. **HTML 排版设计**：在指定期目录创建/修改同名 HTML；必须基于 `template/`，按模板机制排布文章和图片；仅可修改与版式直接相关的文字，不得改写正文事实、标题、作者、页码。
2. **目录/标签生成**：生成/维护 `articles/content.txt` 和 `photos/phototags.txt`。
3. **PDF 只读校验**：仅用 `C:\Python313\python.exe` + `PyPDF2` 读取既有 PDF 的页数、页面尺寸、文本。只读，不写回、不生成、不转换、不删除。

### 绝对禁止

- 禁止创建/修改/转换/删除/移动 PDF；禁止调用 `PP/peachpdf.exe`；禁止安装 PDF 相关库。
- 禁止整理原始数据到文章；禁止构建其他索引；禁止写除 HTML、`content.txt`、`phototags.txt` 之外的文件。
- 禁止擅自改变模板的页尺寸、边距、栏数、正文区高度、行高、栏宽、页脚机制。
- 禁止用自动多栏平衡、自动分页、自动避让代替人工逐行核算。
- 禁止把大段正文放进固定高 `overflow:hidden` 容器后依赖裁切“分页”。
- 禁止用“绝对定位图 + 洞”机制排栏内图（PeachPDF 下行进位漂移，图/图注与正文必然叠压）；栏内图一律流内图块（§2.2）。
- 禁止绝对定位图片/附记/装饰覆盖正文。
- 禁止无核算、无 debug 校准、无 PDF 只读核对就交付。

## 2. 模板硬性机制（必须照做）

### 2.1 正文区

- 文章页必须沿用模板的 `.body`：固定正文区、三栏、`column-gap`、`margin-bottom` 给页脚留白。不得改成双栏、单栏或自动平衡多栏。
- 每页正文必须人工切分。每页占用行数 = 正文行数 + 洞行数 + 空行数 + 图注预留行数；必须 ≤ 该页容量 − 6 行。不足 6 行余地必须移段、移图或分页。
- 页脚区域必须预留。正文、图片、图注、附记、装饰不得进入页脚区域。
- `.page` 的 `overflow:hidden` 只能作为最终裁切保险，不得作为分页手段。正文不得被裁切。

### 2.2 图片（流内图块 · PeachPDF 唯一安全机制）

- 栏内图一律用**流内图块** `.photo-block`：图与图注同块、`break-inside:avoid`，随文排。流内元素互不叠压，图注永远紧贴图下，任何引擎下都不可能与正文冲突。结构：
  `<div class="photo-block" style="--ph-w:…; --ph-h:…"><div class="ph" style="--ph-img:url('photos/…')"></div><p class="cap">图注</p></div>`
- **禁止"绝对定位图（.photo-abs）+ 洞（.hole）"机制**：PeachPDF 与浏览器的行进位存在 ±1–2 行差异（换行与取整细节不同，任何分栏标记都无法消除），固定 `top` 的图和图注必然与正文互相叠压，甚至整行正文被图盖住（隐性丢字）。2611 期两轮实排均因此返工，此机制已废弃。
- 块宽 `--ph-w`（≤栏宽），窄图块居中：`width:var(--ph-w); margin:0.5mm auto 1mm;`。图注 1 行 ≤20 字；超长时块随文加高，不得溢出块外。
- 块内 `.ph` 必须显式包含：`width:100%`、`height`、`background-size:cover`、`background-position:center center`、`background-repeat:no-repeat`。需要角标时保留 `position:relative`。
- 图片路径必须为本地相对路径或 `data:` URI；引用前确认文件存在。禁止 HTTP(S) 远程图片。
- 首页顶部配图 `.photo` 机制不变（位于 `.body` 之外，不算栏内图）。

### 2.3 分栏确定性（PeachPDF 关键机制，2026-10-25 修订）

- **根因**：浏览器与 PeachPDF 的行进位存在 ±1–2 行差异（换行、取整细节不同，且随栏内行数累积），多栏平衡算法也不同。任何依赖"流内元素落到某一固定行"的做法（洞、绝对定位 top）都会在 PDF 里漂移；流内块随文走即可免疫，但各栏装哪些元素仍需钉死，否则每栏容量与切分失控。
- **硬性对策（缺一不可）**：
  1. `.body` 必须显式设 `column-fill: auto`；
  2. 每栏起点元素（段落、小标题或图块）必须加 `class="cbrk"`（`.cbrk { break-before: column; }`）钉死切分点，使每栏装哪些元素与引擎无关；
  3. 栏内图用流内图块（§2.2），不写 `top`、不挖洞、不做红蓝框校准。
- 每个非末栏的内容底必须留 ≥1 行空气（防止取整差异导致末行溢出到下一栏）；末栏余量按 §2.1 的 ≥6 行执行。
- 收尾页/短文页（内容天然不足一页）允许放大图块的宽与高，把留白吸收进版面；图注仍 1 行。

### 2.4 目录页与绝对定位

- `.toc-col`、`.toc2-col` 等包含内部绝对定位元素的列，必须设 `position:relative`，否则内部绝对定位会相对 `.page` 定位。
- 版权、栏目索引、引文等绝对定位块不得与 `.folio` 页脚重叠。`.copyright` 不得使用 `bottom:0` 直接压页脚。

### 2.5 校准与核算

- 交付前必须逐页核算：栏数 × 每栏行数 = 页容量；占用行数必须留 ≥6 行。
- 图块的流内成本 = 图高 + 图注 1 行 + 上下 margin ≈ 图高 + 1.3 行；行数核算用于选切分点。
- 流内图块无需 top、无需挖洞、无需红蓝框校准；交付前逐页目检：图注紧贴图下、无图文叠压、无溢出、页底留白均匀。
- 图片、图注、附记、页脚必须分别占位；不得用“看起来差不多”代替核算。

## 3. PeachPDF 兼容硬性要求（逐条自检）

### 页面与单位
- [ ] `@page { size: 210mm 285mm; margin: ... }` 显式给出。
- [ ] 所有尺寸用 `mm` / `pt` / `cm` / `in` 或标准 `px`（`1px=0.75pt`，`96px=1in`）。不得使用旧式“1px 当 1pt”。

### 颜色
- [ ] 全文件不得出现 `#`、`rgb(`、`hsl(`、颜色名。全部用 `device-cmyk(...)`。
- [ ] 不得使用 `opacity`、半透明渐变、`fill-opacity`/`stroke-opacity` 调浅。浅色用低百分比 CMYK 实色。
- [ ] 不使用专色/spot color。

### 分页与溢出
- [ ] 跨页内容不得放在 `overflow:hidden` 容器中依赖裁切。
- [ ] 跨页内容不得是 flex item 或 grid item；多栏用 `multi-column`。
- [ ] 不得给大段正文设固定 `max-height`；内容超限会溢出底边。
- [ ] 强制分页只用 `break-before: page` / `page-break-before: always`。

### 不支持的样式
- [ ] 无 `filter: blur()/grayscale()/sepia()/saturate()/hue-rotate()/drop-shadow()`，无模糊 `box-shadow`。
- [ ] 版面主要结构不得用 `display:grid`；用 block 流、`float`、`table`、`multi-column`。
- [ ] 选择器只用元素、类、ID、后代、子代、基本属性选择器；不用不认识的伪类。
- [ ] 无 JS、`<dialog>` 开关、`<details>` 展开等交互。

### 图片与资源
- [ ] 图片路径全部本地相对路径或 `data:` URI；无 HTTP(S) 远程资源。
- [ ] 图片格式在 JPEG/PNG/BMP/GIF/WebP/AVIF/TIFF/SVG 范围内。
- [ ] 图片容器显式给出 `width`/`height` 或 `max-width:100%`。
- [ ] 印刷图片不依赖透明叠色；不依赖透明背景做视觉。

### 字体
- [ ] `@font-face` 只引用本地 TTF/OTF/WOFF/WOFF2；无远程字体。
- [ ] `font-family` 有完整回退栈；中文用 `unicode-range` 声明覆盖范围。
- [ ] 不依赖彩色 emoji。

### 结构与外部资源
- [ ] 样式只在 HTML 内 `<style>` 或本地 `<link rel="stylesheet">`；无外链 CSS/JS/字体/图片。
- [ ] 文档结构只用标准 HTML 元素。
- [ ] 装饰矢量用 inline SVG 或本地 SVG；SVG `<filter>` 中模糊、光照、形态学不得使用。

## 4. 交付前自检（任一不满足即未完成）

- [ ] 已从 `template/` 复制对应页面结构，未自创栏数/正文区/行高/栏宽。
- [ ] 文章页为模板三栏固定正文区，不是双栏自动流。
- [ ] `.body` 带 `column-fill:auto`；每个分栏起点元素带 `.cbrk`（切分点钉死）。
- [ ] 栏内图全部为流内图块 `.photo-block`（图+图注一体），无 `.hole`、无 `.photo-abs`、无 `top`。
- [ ] 每栏内容底均未超出正文区（无溢出）；每页逐行核算，末栏留 ≥6 行余地；未依赖 `overflow:hidden` 裁切。
- [ ] 页脚区域无正文/图片/版权重叠。
- [ ] 目录列有 `position:relative`；版权/索引/引文未压页脚。
- [ ] 所有 `.ph` 含 cover/center/no-repeat/position:relative。
- [ ] 颜色全部 `device-cmyk`；无远程资源；无 filter/grid 主布局/JS。
- [ ] 已用只读 PDF 核对页数、页面尺寸、页脚文本、末页附记文本是否存在；发现 HTML 问题只修 HTML。
- [ ] PDF 只读检查未写回、未生成、未修改 PDF。

## 5. 交付

仅交付：指定期同名 HTML，或 `content.txt` / `phototags.txt`。完成即停。PDF 可只读查看，但不得修改、生成或转换。