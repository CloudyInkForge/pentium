# readme.md（人看）

## 项目目标
使用 Agent 完成杂志 HTML 排版，通过 PeachPDF 转为 PDF。AI 只负责 HTML 排版设计，以及文章目录、图片标签生成；可只读查看 PDF 做校验，但不生成、不修改、不转换 PDF。

## 目录与文件
- `PP/peachpdf.exe`：PDF 转换工具。仅人类/CI 使用；AI 禁止调用。AI 可以只读方式解析 PDF（读取文本、页数、页面尺寸、元数据），但不得生成、修改、转换或删除 PDF。
- 每期一个 4 位编号目录，如 `2611/`，存放该期全部内容。
- `src/`：原始数据，可含原始文章。必须有 `descriptor.txt` 记录处理情况。
- `articles/`：处理好的文章 txt。`content.txt` 统计每篇名称、字数、所属栏目。
- `photos/`：图片。`phototags.txt` 记录每图所属文章、尺寸、字数、内容概要。
- `template/`：封面、内容页模板，HTML 据此构建。
- 每期目录下有与文件夹同名的 HTML，为主要交付物。

## AI 权限
AI 有三种权力，且仅在明确要求时执行：
1. **HTML 排版设计**：创建/修改指定期同名 HTML，合理排布文章和图片，修改模板格式相关文字。
2. **文章目录、图片标签生成**：生成/维护 `articles/content.txt`、`photos/phototags.txt`。
3. **PDF 只读校验**：用 Python 3.13 脚本读取既有 PDF（页数、页面尺寸、文本、元数据），核对 HTML 排版结果。只读，不写回、不生成、不转换。

禁止：整理原始数据到文章；为图片构建其他索引；创建/修改/转换/删除 PDF；调用 PeachPDF；写其他文件。未明确要求构建/修改 HTML 时，读完说明即停止。

## PDF 只读读取环境
- 解释器：`C:\Python313\python.exe`（Python 3.13.3）。
- 已装库：`PyPDF2` 3.0.1（`import PyPDF2` 即可用，无需再装）。
- 读文本与页数：

```python
import PyPDF2
r = PyPDF2.PdfReader(r"old/2611/2611.pdf")
print(len(r.pages), r.pages[0].mediabox)
print(r.pages[0].extract_text())
```

- 输出中文时先 `sys.stdout.reconfigure(encoding="utf-8")`，或在 PowerShell 里 `$env:PYTHONIOENCODING="utf-8"`，否则控制台会显示乱码。
- 只读用途：可解析、比对文本与页面尺寸；不得写入、修改、重新生成 PDF，也不得调用 `PP/peachpdf.exe`。如需把页面渲染成图片目检，另装 PyMuPDF（当前未安装）。

## HTML 兼容 PeachPDF 的硬性要求
HTML 必须能被 PeachPDF 稳定转换且无格式问题。以下为已验证的支持边界，所有 HTML 均须满足。

### 1. 页面与尺寸
- 页面尺寸必须 `210 × 285 mm`，用 `@page { size: 210mm 285mm; margin: ... }` 定义。
- 所有长度单位按标准物理比率解析：`1px = 0.75pt`，`96px = 1in`，`1mm = 2.835pt`[reference:0]。不要用旧式“1px≈1pt”的写法，否则内容会放大 33%。
- 绝对单位优先：`mm` / `pt` / `cm` / `in`。避免依赖视口单位做关键布局。

### 2. 颜色（device-cmyk）
- 所有颜色必须用 `device-cmyk(C M Y K)`，不得用 hex、rgb、hsl、颜色名等 sRGB 写法。
- `device-cmyk` 会原样传递为 PDF 的 DeviceCMYK 操作符，不会被近似成 RGB。
- **不得依赖透明度**：`opacity < 1`、半透明渐变 stop、`fill-opacity`/`stroke-opacity < 1`、SVG `<mask>` 会触发光栅化或透明组；在 PDF/X-1a 等 CMYK 受限模式下，透明内容可能被光栅化，或直接报错[reference:2]。杂志排版应使用实色，如需浅色请用低百分比 CMYK，不要用透明度调浅。
- 避免使用 `spot color`：PeachPDF 没有专色支持，实践中按 CMYK-only 处理。

### 3. 分页与溢出（高危区）
- PeachPDF 的分页行为不完全等同浏览器，尤其以下情况必须规避：
  - **不要用 `overflow: hidden` 包裹跨页内容**。曾经因为把这类容器当成不可分割，导致页边缘把最后一行切掉。跨页文章用普通块级流，不要套固定高或 `overflow: hidden` 的壳。
  - **不要让 flex item / grid item 直接跨页**。这类盒子当前仍倾向于整体移动，容易造成页末大片空白或内容错位。跨页内容用普通 block 流；分栏用 `multi-column`，不要用 grid 硬撑杂志跨页排版。
  - 避免把大段文字放入固定高度的 `max-height` 盒子：内容超过 max-height 时**不会撑开**，而是直接溢出底边[reference:6]。
- 需要强制分页时用 `page-break-before: always` / `break-before: page`。不要让 PeachPDF 去“猜”复杂碎片化场景。

### 4. 不支持的样式（会导致光栅化或直接失效）
- **滤镜类**：`filter: blur()/grayscale()/sepia()/saturate()/hue-rotate()/drop-shadow()` 以及模糊 `box-shadow`，PeachPDF 无法作为矢量绘制，会转成位图或失效[reference:7]。杂志排版不应依赖这些效果。
- **CSS Grid**：不要用 `display: grid` 做主要版面。PeachPDF 对复杂 Grid/Flexbox 布局支持有限，官方兼容矩阵中 Grid 没有完整的排版保证；版面结构用 block 流 + `float` + 表格（必要时）+ multi-column[reference:8]。
- **复杂选择器**：不认识的伪类可能使整个选择器列表失效[reference:9]。只用标准、简单、浏览器和 PeachPDF 都能识别的选择器（元素、类、ID、后代、子代、基本属性选择器）。
- 不要用 JS、动态 DOM、`<dialog>` 的开关行为、`<details>` 的展开行为；这些要么不执行，要么按静态块渲染[reference:10]。

### 5. 图片
- 支持 JPEG、PNG、BMP、GIF、WebP、AVIF、TIFF；SVG 作为矢量支持（inline `<svg>`、`<img src="x.svg">`、`background-image`）[reference:12]。
- 图片用**本地相对路径**或 `data:` URI。PeachPDF 默认**静默跳过远程 HTTP(S) 资源**，远程图片会直接不出现[reference:13]。
- 需要透明背景时，PNG 的 alpha 在普通 PDF 中可用，但若输出模式涉及 PDF/X-1a 且要求 CMYK-only，透明区域可能被光栅化或处理成位图；保险起见，印刷用图片尽量用实底 CMYK 图，不要依赖透明叠色。
- 图片放入固定尺寸容器时，显式设置 `width`/`height` 或 `max-width: 100%`，避免 PeachPDF 的布局引擎对替换元素尺寸计算产生歧义。

### 6. 字体
- 使用 `@font-face` 嵌入本地字体，格式支持 TTF、OTF/CFF、WOFF、WOFF2。
- 字体文件放在项目本地，用相对路径引用；不要引用远程字体 CDN。
- 中文字体尽量在 `font-family` 中给出完整回退栈，并用 `unicode-range` 声明覆盖范围，避免缺字时 PeachPDF 的回退逻辑产生意外字重或字宽[reference:15]。
- 不要依赖彩色 emoji 字体：彩色 emoji 表不会被嵌入，只保证单色轮廓[reference:16]。

### 7. 结构、选择器与外部资源
- 文档结构只用标准 HTML 元素（`div`、`p`、`h1`–`h6`、`ul`、`table`、`img`、`figure` 等）。`<head>` 中只有 `<style>` 和 `<link rel="stylesheet">` 会被处理，其余忽略。
- 所有样式写在 HTML 内的 `<style>` 中，或通过本地 `<link rel="stylesheet">` 引入；不要用内联 `style` 中 PeachPDF 不认识的属性。
- 禁止外链任何 CSS、JS、图片、字体。需要引用的资源一律本地相对路径或 `data:`。
- 装饰性矢量优先用 inline `<svg>` 或本地 SVG 文件。SVG 的渐变、裁剪、遮罩大部分支持，但 `<filter>` 中 PDF 无对应操作符的部分（模糊、光照、形态学等）会被光栅化[reference:18]。杂志装饰不要用模糊滤镜。

### 8. 转换验证
每次 HTML 修改后，由人类/CI 用 `PP/peachpdf.exe` 转换。AI 可用 Python 只读解析转换结果（页数、页面尺寸、文本）核对排版，但不得写入、修改、重新生成 PDF，也不得调用转换工具；若收到转换报错文本，只修复 HTML。
严禁安装PDF相关库，终端任务必须及时，超时立刻停止，不要歇着，不要浪费时间。