# tools/ — 公开图源插图工具（可复用）

为各期杂志文章从公开博物馆/摄影集 API 检索并下载插图。图片均来自开放获取
（Public Domain / CC0 为主）来源，逐图记录来源与许可，写入当期
`photos/phototags.txt`（沿用项目五列格式，末尾追加"来源与许可"列）。

## 文件

- `fetch_images.py` — 主工具（Python 3.11+，依赖 requests、Pillow）
- `queries_2611.toml` — 2611 期检索清单（每篇文章的选图方向、检索词、图源优先级）
- 新增一期：复制 `queries_2611.toml` 为 `queries_<期号>.toml`，只改检索词。

## 图源

| 键 | 来源 | 许可 | 备注 |
|----|------|------|------|
| met | 大都会艺术博物馆 | CC0 | 搜索+逐对象详情，稍慢 |
| cma | 克利夫兰艺术博物馆 | CC0 | 一次请求出结果，首选 |
| mia | 明尼阿波利斯艺术博物馆 | PD 为主 | image 字段有脏数据，已过滤 |
| smk | 丹麦国家美术馆 | PD | 优先走 api.smk.dk 整图直链 |
| vam | 英国 V&A | 以馆方标注为准 | 许可信息不在 API 中，慎用于封面 |
| nasa | NASA 影像库 | 公有领域 | 图片 CDN 有突发限流，失败可重试 |
| wikimedia | 维基共享资源 | PD/CC 按项过滤 | 许可白名单过滤 |
| aic | 芝加哥艺术博物馆 | CC0 | 本网络偶被拦截 |
| loc | 美国国会图书馆 | 逐项核对 | 本网络被拦截 |

脚本在源不可达（连续 4 次失败）时自动跳过该源，其余源照常工作；
`probe` 子命令可查看本机当前可用状态。

## 流程

```bash
# 0) 查看各源连通性
python tools/fetch_images.py probe

# 1) 按清单检索，产出候选 JSON（不下载）
python tools/fetch_images.py search --manifest tools/queries_2611.toml \
       --out _tmp/2611_candidates.json
#    --sources cma,met 只用指定源；--only 02,09 只补跑指定文章并合并结果

# 2) 人工审阅 _tmp/2611_candidates.json，对选中条目加：
#    "selected": true, "order": n, "summary": "图注文字（中文）"
#    同一候选出现在多篇时，只保留一篇的 selected。

# 3) 下载选中图到 <期号>/photos/，自动校验/转存 JPEG（长边≤3200）、
#    重写 phototags.txt，完整元数据落 _tmp/<期号>_credits.json（不提交）
python tools/fetch_images.py download --candidates _tmp/2611_candidates.json \
       --issue-dir 2611

# 4) 生成 HTML 速览页供人工目检
python tools/fetch_images.py contact --issue-dir 2611 --out _tmp/2611_preview.html
```

## 约定

- 照片命名沿用旧期规范：`<文章题目>.jpg`，同篇第 2/3 张为 `<题目>02.jpg`、
  `<题目>03.jpg`；`order` 字段决定序号。
- 许可规则：Met/CMA/AIC/SMK/NASA 均为公版或 CC0，可用于印刷；
  Wikimedia 仅保留 PD/CC-BY/CC-BY-SA；V&A 许可不明，仅作候选备选。
- 图注来源格式：`<作者>，<馆名>，<许可>`（见 phototags.txt 末列）。
- 网络注意：本仓库工作机直连 Wikimedia/LOC/Openverse 不通；
  NASA 图片 CDN（images-assets.nasa.gov）有突发限流，403 时等几分钟重试。
