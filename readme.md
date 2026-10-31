# readme.md（人看）

## 项目目标

用 AI 完成杂志 HTML 排版，由人类/CI 用 PeachPDF 转 PDF。AI 主要负责 HTML 排版、目录/图片标签生成，以及 PDF 只读校验。

## 目录与文件

- `PP/peachpdf.exe`：唯一权威PDF转换工具。
- 每期一个 4 位编号目录，如 `2611/`，存放该期同名 HTML 和内容。
- `src/`：原始数据，含 `descriptor.txt`。
- `articles/`：文章 txt；`content.txt` 统计名称、字数、栏目。
- `photos/`：图片；`phototags.txt` 记录所属文章、尺寸、字数、概要。
- `template\next_genera`：标题页与内容页模板，HTML 必须据此构建。

# 使用模板前请阅读对应的design.md和每系列模板的api文件，目前仅使用template\next_genera系列模板。
# 按需读取文档，项目极其庞大，除了修改涉及期文件夹和template\next_genera外如无必要禁止阅读其他文件夹。
# 无必要禁止直接读取文章或图片，仅看对应的目录或标签文件。