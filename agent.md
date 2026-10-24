# agent.md（AI 看）
## 绝对不允许违反
对模板进行排版时必须严格遵守模板，自己逐行计算分页等，且要留有一定余地。坚决不允许引入CSS自动排版。
## 权限（仅此三项，仅在明确要求时执行）
1. **HTML 排版设计**：在指定期目录创建/修改同名 HTML；依据 `template/`，合理排布文章和图片；可加矢量装饰、微调文本、裁切缩放图片、修改模板格式文字。
2. **目录/标签生成**：生成/维护 `articles/content.txt` 和 `photos/phototags.txt`。
3. **PDF 只读校验**：用 `C:\Python313\python.exe` + `PyPDF2` 读取既有 PDF（页数、页面尺寸、文本），核对排版。

禁止：创建/修改/转换/删除/移动 PDF；调用 `PP/peachpdf.exe`；整理原始数据到文章；构建其他索引；写其他文件。PDF 转换验证由人类/CI 执行；你只接收报错文本并修 HTML。

## 读取与省 tokens
按需读取最小集：指定期同名 HTML → `template/` → `articles/content.txt`、`photos/phototags.txt` → 任务指定文章/图片。未明确要求构建/修改 HTML 时，读完必要说明即停止。不输出无关解释，直接产出文件内容或修改。

## PeachPDF 兼容硬性要求（逐条自检）
生成或修改 HTML 后，逐项核对以下规则。违反任一项即视为未完成。

### 页面与单位
- [ ] `@page { size: 210mm 285mm; }`，边距显式给出。
- [ ] 所有尺寸用 `mm` / `pt` / `cm` / `in` 或按标准解析的 `px`（`1px = 0.75pt`，`96px = 1in`）[reference:19]。不要写“1px 当 1pt”的旧逻辑。

### 颜色
- [ ] 全文件搜索 `#`、`rgb(`、`hsl(`、颜色名（`red`、`black` 等），全部替换为 `device-cmyk(...)`。
- [ ] 不使用 `opacity`、半透明渐变、半透明 stop、`fill-opacity`/`stroke-opacity` 做视觉调整；需要浅色时用低百分比 CMYK 实色[reference:20]。
- [ ] 不使用专色/spot color 概念。

### 分页与溢出
- [ ] 跨页内容**不**放在 `overflow: hidden` 容器中；跨页壳用普通块级流。
- [ ] 跨页内容**不**是 flex item 或 grid item；多栏用 `multi-column`，不要用 grid 跨页。
- [ ] 没有固定 `max-height` 的大段文字容器；内容超过 max-height 会直接溢出底边，不会撑开[reference:24]。
- [ ] 强制分页只用 `break-before: page` / `page-break-before: always`。

### 不支持的样式
- [ ] 没有 `filter: blur()/grayscale()/sepia()/saturate()/hue-rotate()/drop-shadow()`，没有模糊 `box-shadow`；这些会被光栅化或失效[reference:25]。
- [ ] 版面主要结构**不**用 `display: grid`；用 block 流、`float`、`table`、`multi-column`[reference:26]。
- [ ] 不使用不认识的伪类或复杂选择器；选择器只用元素、类、ID、后代、子代、基本属性选择器[reference:27]。
- [ ] 没有 JS、`<dialog>` 开关、`<details>` 展开等交互行为[reference:28]。

### 图片与资源
- [ ] 图片路径**全部**为本地相对路径或 `data:` URI；没有 HTTP(S) 远程图片，因为 PeachPDF 默认静默跳过远程资源[reference:29]。
- [ ] 图片格式在 JPEG / PNG / BMP / GIF / WebP / AVIF / TIFF / SVG 范围内。
- [ ] 图片容器给出了 `width`/`height` 或 `max-width: 100%`，避免替换元素尺寸歧义。
- [ ] 印刷用途的图片不依赖透明叠色；透明可能触发光栅化或 CMYK-only 限制下的位图回退。

### 字体
- [ ] `@font-face` 字体文件为本地 TTF / OTF(CFF) / WOFF / WOFF2，没有远程字体 URL。
- [ ] `font-family` 有完整回退栈；中文字体用 `unicode-range` 声明覆盖范围，避免缺字回退异常[reference:32]。
- [ ] 不依赖彩色 emoji；彩色 emoji 表不会被嵌入[reference:33]。

### 结构与外部资源
- [ ] 样式在 HTML 内的 `<style>` 或本地 `<link rel="stylesheet">` 中；没有外链 CSS、JS、字体、图片。
- [ ] 文档结构为标准 HTML 元素；`<head>` 中只依赖 `<style>` / `<link rel="stylesheet">`，其他子元素不影响布局。
- [ ] 装饰矢量用 inline `<svg>` 或本地 SVG；SVG `<filter>` 中模糊、光照、形态学等会被光栅化，装饰不要用这些[reference:35]。

## 交付
仅交付：指定期同名 HTML，或 `content.txt` / `phototags.txt` 文本。PDF 可只读查看，但不得修改、生成或转换。完成即停。