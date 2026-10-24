#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_images.py — 公开博物馆/摄影集 API 插图检索与下载工具（可复用）

用公开的开放获取（Open Access）图片 API 为杂志各篇文章检索并下载插图。
图片仅来自允许印刷使用的公版/CC0/CC-BY 类来源，逐图记录来源与许可。

用法：
  python tools/fetch_images.py probe
      探测各源连通性，列出本机可用的 API。
  python tools/fetch_images.py search --manifest tools/queries_2611.toml --out _tmp/2611_candidates.json
      按 manifest 逐条检索，输出候选 JSON（未自动下载）。
      之后人工审阅 JSON：对选中条目补 "selected": true、"order": n、"summary": "图注文字"。
  python tools/fetch_images.py download --candidates _tmp/2611_candidates.json --issue-dir 2611
      下载选中图片到 <issue-dir>/photos/，校验/转存 JPEG，
      生成 <issue-dir>/photos/phototags.txt（沿用项目五列格式，末尾加"来源与许可"列），
      并把完整元数据写 _tmp/<issue>_credits.json（不提交）。
  python tools/fetch_images.py contact --issue-dir 2611 --out _tmp/2611_preview.html
      依据已下载图片生成 HTML 速览页，便于人工目检。

新增一期：复制 queries_2611.toml 为 queries_<期号>.toml 改检索词即可。
新增图源：在 SOURCES 注册一个 adapter（search() + resolve()）。

注意：Wikimedia Commons / LOC / AIC / Openverse 等源在部分网络环境不可达，
脚本会在首次访问失败后自动跳过该源（probe 可查看状态），不影响其余源工作。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

UA = {"User-Agent": "Mozilla/5.0 PentiumMagResearch/1.0 (school-magazine illustration sourcing)"}
TIMEOUT = 25
RETRIES = 3
MIN_SIDE = 640          # 任一边低于该像素数视为不适合印刷，警告
MAX_SIDE = 3200         # 长边超过则等比缩小（210×285mm 下 3200px ≈ 280dpi 足够）

# ---------------------------------------------------------------- 网络 ----

_dead: set[str] = set()
_session = requests.Session()
_session.headers.update(UA)


def _get(url: str, *, params=None, timeout=TIMEOUT):
    last = None
    for i in range(RETRIES):
        try:
            r = _session.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code == 429:          # 限流：退避更久，不算失败
                time.sleep(6 + 4 * i)
                last = "HTTP 429"
                continue
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = str(e.__class__.__name__)
        time.sleep(1.2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def _alive(source: str) -> bool:
    """同一次运行内，源连续失败 2 次即标记为不可达并跳过。"""
    return source not in _dead


def _fail(source: str):
    _dead.add(source)
    print(f"  [跳过源 {source}：连续失败，本运行内不再尝试]", file=sys.stderr)


def safe_get(source: str, url: str, **kw):
    if not _alive(source):
        return None
    try:
        r = _get(url, **kw)
        _fail_count[source] = 0          # 成功即重置失败计数
        return r
    except RuntimeError as e:
        _fail_count[source] = _fail_count.get(source, 0) + 1
        if _fail_count[source] >= 4:      # 容忍网络瞬断，连续 4 次失败才判死
            _fail(source)
        print(f"  [warn] {e}", file=sys.stderr)
        return None


_fail_count: dict[str, int] = {}


# ------------------------------------------------------------ adapters ----
# 每个 adapter：
#   search(q, limit) -> [candidate]
#   resolve(candidate) -> 直链下载 URL
# candidate 统一字段：
#   key, source, id, title, artist, date, medium, desc,
#   license, page_url, image_url, width, height

def _clip(s, n=200):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s[:n]


def met_search(q, limit):
    r = safe_get("met", "https://collectionapi.metmuseum.org/public/collection/v1.1/search",
                 params={"q": q})
    if r is None:
        return []
    ids = (r.json().get("objectIDs") or [])[: limit * 3]
    out = []
    for oid in ids[: limit * 2]:
        time.sleep(0.15)          # Met 对高频请求限流，保持礼貌间隔
        ro = safe_get("met", f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        if ro is None:
            continue
        o = ro.json()
        if not o.get("isPublicDomain") or not o.get("primaryImage"):
            continue
        out.append(dict(
            key=f"met:{oid}", source="met", id=oid,
            title=_clip(o.get("title"), 120), artist=_clip(o.get("artistDisplayName"), 80),
            date=_clip(o.get("objectDate"), 40), medium=_clip(o.get("medium"), 80),
            culture=_clip(o.get("culture"), 40), department=o.get("department", ""),
            desc=_clip(o.get("creditLine"), 80), license="The Met Open Access (CC0)",
            page_url=f"https://www.metmuseum.org/art/collection/search/{oid}",
            image_url=o["primaryImage"], width=None, height=None,
        ))
        if len(out) >= limit:
            break
    return out


def cma_search(q, limit):
    r = safe_get("cma", "https://openaccess-api.clevelandart.org/api/artworks/",
                 params={"q": q, "cc0": 1, "has_image": 1, "limit": limit})
    if r is None:
        return []
    out = []
    for a in r.json().get("data", []):
        imgs = a.get("images") or {}
        pick = imgs.get("print") or imgs.get("web")
        if not pick or not pick.get("url"):
            continue
        out.append(dict(
            key=f"cma:{a['id']}", source="cma", id=a["id"],
            title=_clip(a.get("title"), 120),
            artist=_clip("; ".join(c.get("description", "") for c in a.get("creators") or []), 90),
            date=_clip(a.get("creation_date"), 40), medium=_clip(a.get("type"), 60),
            culture=_clip(", ".join(a.get("culture") or []), 40),
            desc=_clip(a.get("description") or a.get("tombplate"), 200),
            license="CC0 1.0（克利夫兰艺术博物馆）",
            page_url=f"https://www.clevelandart.org/art/{a.get('accession_number','')}",
            image_url=pick["url"], width=pick.get("width"), height=pick.get("height"),
        ))
    return out


def mia_search(q, limit):
    r = safe_get("mia", "https://search.artsmia.org/" + requests.utils.quote(q))
    if r is None:
        return []
    hits = (r.json().get("hits", {}).get("hits") or [])[: limit * 2]
    out = []
    for h in hits:
        s = h.get("_source", {})
        img = s.get("image")
        # image 字段应为文件名；"valid"等脏数据会导致下载到 HTML 错误页
        if not img or not re.fullmatch(r"[A-Za-z0-9._-]+", img) or img in ("valid", "invalid"):
            continue
        pd = s.get("public_domain")
        if pd is False:  # 未知(None)时保留但许可标注馆方
            continue
        out.append(dict(
            key=f"mia:{s.get('id')}", source="mia", id=s.get("id"),
            title=_clip(s.get("title"), 120),
            artist=_clip(s.get("artist") or s.get("artist_of_object"), 80),
            date=_clip(s.get("dated"), 40), medium=_clip(s.get("medium"), 80),
            culture=_clip(s.get("country") or s.get("continent"), 40),
            desc=_clip(s.get("context") or s.get("text"), 160),
            license="Public Domain（明尼阿波利斯艺术博物馆）" if pd else
                    "Mia 公开图像（以馆方标注为准）",
            page_url=f"https://collections.artsmia.org/art/{s.get('id')}",
            image_url=f"https://collections.artsmia.org/{img}/{img}_main.jpg",
            width=None, height=None,
        ))
        if len(out) >= limit:
            break
    return out


def smk_search(q, limit):
    r = safe_get("smk", "https://api.smk.dk/api/v1/art/search/",
                 params={"keys": q, "rows": limit * 2})
    if r is None:
        return []
    out = []
    for it in r.json().get("items", []):
        if not it.get("public_domain") or not it.get("has_image"):
            continue
        iiif = it.get("image_iiif_id")
        if not iiif:
            continue
        titles = it.get("titles") or [{}]
        prod = (it.get("production") or [{}])[0]
        names = "; ".join(
            n.get("name") if isinstance(n, dict) else str(n)
            for n in (it.get("object_names") or []))
        # iip.smk.dk（IIIF 图像服务器）在部分网络下超时；优先用 api.smk.dk 的整图下载直链
        dl = it.get("image_native") or f"{iiif}/full/!1400,1400/0/default.jpg"
        out.append(dict(
            key=f"smk:{it.get('id')}", source="smk", id=it.get("id"),
            title=_clip(titles[0].get("title"), 120),
            artist=_clip(prod.get("creator"), 80),
            date=_clip(str(prod.get("production_date") or ""), 40),
            medium=_clip(names, 60),
            culture="Denmark",
            desc=_clip("; ".join(it.get("content_subject") or []), 120),
            license="Public Domain（丹麦国家美术馆 SMK）",
            page_url=it.get("object_url") or it.get("frontend_url") or "",
            image_url=dl,
            width=it.get("image_width"), height=it.get("image_height"),
        ))
        if len(out) >= limit:
            break
    return out


def vam_search(q, limit):
    r = safe_get("vam", "https://api.vam.ac.uk/v2/objects/search/",
                 params={"q": q, "images_exist": "true", "page_size": limit})
    if r is None:
        return []
    out = []
    for rec in r.json().get("records", []):
        img = rec.get("_images") or {}
        base = img.get("_iiif_image_base_url")
        if not base:
            continue
        maker = rec.get("_primaryMaker") or {}
        out.append(dict(
            key=f"vam:{rec.get('systemNumber')}", source="vam", id=rec.get("systemNumber"),
            title=_clip(rec.get("_primaryTitle"), 120),
            artist=_clip(maker.get("name"), 80),
            date=_clip(rec.get("_primaryDate"), 40),
            medium=_clip(rec.get("objectType"), 60),
            culture=_clip((rec.get("_primaryPlace") or ""), 40),
            desc="",
            license="V&A 开放图像（具体许可以馆方标注为准）",
            page_url=f"https://collections.vam.ac.uk/item/{rec.get('systemNumber')}",
            image_url=f"{base}full/!1600,1600/0/default.jpg",
            width=None, height=None,
        ))
    return out


def nasa_search(q, limit):
    r = safe_get("nasa", "https://images-api.nasa.gov/search",
                 params={"q": q, "media_type": "image", "page_size": limit})
    if r is None:
        return []
    out = []
    for item in r.json().get("collection", {}).get("items", []):
        d = (item.get("data") or [{}])[0]
        thumb = (item.get("links") or [{}])[0].get("href")
        if not d.get("nasa_id"):
            continue
        out.append(dict(
            key=f"nasa:{d['nasa_id']}", source="nasa", id=d["nasa_id"],
            title=_clip(d.get("title"), 120),
            artist="NASA",
            date=_clip(d.get("date_created"), 40),
            medium="Photograph",
            culture="",
            desc=_clip(d.get("description"), 200),
            license="NASA 图片（公有领域，标注 NASA）",
            page_url=f"https://images.nasa.gov/details/{d['nasa_id']}",
            image_url=thumb, width=None, height=None,
        ))
    return out


def wikimedia_search(q, limit):
    r = safe_get("wikimedia", "https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": limit * 2,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1600,
    })
    if r is None:
        return []
    pages = (r.json().get("query") or {}).get("pages") or {}
    ok_lic = re.compile(r"(public domain|cc0|cc by(?!-nc)|cc by-sa)", re.I)
    bad_lic = re.compile(r"(nc|nd|fair use|non-free)", re.I)
    out = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata") or {}
        lic = _clip((meta.get("LicenseShortName") or {}).get("value", ""), 60)
        if not ok_lic.search(lic) or bad_lic.search(lic):
            continue
        url = ii.get("thumburl") or ii.get("url")
        if not url:
            continue
        artist = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", ""))
        out.append(dict(
            key=f"wikimedia:{p.get('pageid')}", source="wikimedia", id=p.get("pageid"),
            title=_clip(p.get("title", "").removeprefix("File:"), 120),
            artist=_clip(artist, 90), date=_clip((meta.get("DateTimeOriginal") or {}).get("value", ""), 40),
            medium="Photograph", culture="",
            desc=_clip(re.sub(r"<[^>]+>", "", (meta.get("ImageDescription") or {}).get("value", "")), 200),
            license=f"{lic}（Wikimedia Commons）",
            page_url=f"https://commons.wikimedia.org/wiki/{p.get('title','')}",
            image_url=url, width=ii.get("thumbwidth") or ii.get("width"),
            height=ii.get("thumbheight") or ii.get("height"),
        ))
        if len(out) >= limit:
            break
    return out


def aic_search(q, limit):
    r = safe_get("aic", "https://api.artic.edu/api/v1/artworks/search",
                 params={"q": q, "limit": limit,
                         "fields": "id,title,artist_titles,date_display,medium_display,image_id,is_public_domain"})
    if r is None:
        return []
    out = []
    for a in r.json().get("data", []):
        if not a.get("image_id") or a.get("is_public_domain") is not True:
            continue
        out.append(dict(
            key=f"aic:{a['id']}", source="aic", id=a["id"],
            title=_clip(a.get("title"), 120), artist=_clip("; ".join(a.get("artist_titles") or []), 90),
            date=_clip(a.get("date_display"), 40), medium=_clip(a.get("medium_display"), 80),
            culture="", desc="",
            license="CC0（芝加哥艺术博物馆）",
            page_url=f"https://www.artic.edu/artworks/{a['id']}",
            image_url=f"https://www.artic.edu/iiif/2/{a['image_id']}/full/1680,/0/default.jpg",
            width=None, height=None,
        ))
    return out


def loc_search(q, limit):
    r = safe_get("loc", "https://www.loc.gov/search/", params={"q": q, "fo": "json", "c": limit})
    if r is None:
        return []
    out = []
    for res in r.json().get("results", []):
        urls = res.get("image_url") or []
        if not urls:
            continue
        out.append(dict(
            key=f"loc:{res.get('id','')[-40:]}", source="loc", id=res.get("id"),
            title=_clip(res.get("title"), 120), artist="", date=_clip(res.get("date"), 40),
            medium="", culture="", desc=_clip("".join(res.get("description") or []), 160),
            license="美国国会图书馆（多为公版，逐项核对）",
            page_url=res.get("id"), image_url=urls[-1], width=None, height=None,
        ))
    return out


SOURCES = {
    "met": met_search, "cma": cma_search, "mia": mia_search, "smk": smk_search,
    "vam": vam_search, "nasa": nasa_search, "wikimedia": wikimedia_search,
    "aic": aic_search, "loc": loc_search,
}
SOURCE_NAME = {
    "met": "大都会艺术博物馆", "cma": "克利夫兰艺术博物馆", "mia": "明尼阿波利斯艺术博物馆",
    "smk": "丹麦国家美术馆", "vam": "英国V&A博物馆", "nasa": "NASA 影像库",
    "wikimedia": "维基共享资源", "aic": "芝加哥艺术博物馆", "loc": "美国国会图书馆",
}


def nasa_resolve(c):
    for size in ("~orig.jpg", "~large.jpg", "~medium.jpg"):
        url = f"https://images-assets.nasa.gov/image/{c['id']}/{c['id']}{size}"
        r = safe_get("nasa", url, timeout=40)
        if r is not None:
            return url
    return None


def mia_resolve(c):
    img = Path(c["image_url"]).parts[-2]
    for pattern in ("original.jpg", f"{img}_main.jpg"):
        url = f"https://collections.artsmia.org/{img}/{pattern}"
        r = safe_get("mia", url, timeout=40)
        if r is not None:
            return url
    return None


def resolve(c):
    if c["source"] == "nasa":
        return nasa_resolve(c)
    if c["source"] == "mia":
        return mia_resolve(c)
    return c["image_url"]


# -------------------------------------------------------------- 检索 ------

def cmd_probe(_args):
    for src, fn in SOURCES.items():
        t0 = time.time()
        try:
            res = fn("landscape", 1)
            status = f"OK  {len(res)} 条" if res else "OK（此查询无结果）"
        except Exception as e:  # noqa: BLE001
            status = f"FAIL {e}"
        print(f"{src:10s} {SOURCE_NAME[src]:14s} {status}  ({time.time()-t0:.1f}s)")


def cmd_search(args):
    if tomllib is None:
        sys.exit("需要 Python 3.11+（tomllib）")
    manifest = tomllib.loads(Path(args.manifest).read_text(encoding="utf-8"))
    entries = manifest.get("items") or manifest.get("item") or []
    only = set(args.sources.split(",")) if args.sources else None
    only_nos = {n.strip() for n in args.only.split(",") if n.strip()}
    result = {"manifest": args.manifest, "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "items": []}
    for item in entries:
        if only_nos and item["no"] not in only_nos:
            continue
        queries = item.get("queries", [])
        seen, candidates = set(), []
        for query in queries:
            src = query["source"]
            if only and src not in only:
                continue
            res = SOURCES[src](query["q"], int(query.get("limit", args.limit)))
            print(f"[{item['no']}] {src:9s} {query['q']!r:44s} -> {len(res)}")
            for c in res:
                w, h = c.get("width"), c.get("height")
                try:
                    w, h = int(w), int(h)
                except (TypeError, ValueError):
                    w = h = None
                if w and h and min(w, h) < (query.get("min_side", args.min_side)):
                    continue
                if c["key"] in seen:
                    continue
                seen.add(c["key"])
                c["_query"] = query["q"]
                candidates.append(c)
        result["items"].append({k: item.get(k) for k in ("no", "title", "file", "count", "note")}
                               | {"candidates": candidates})
    if only_nos and Path(args.out).exists():          # 增量模式：与旧结果按篇合并
        old = json.loads(Path(args.out).read_text(encoding="utf-8"))
        fresh = {i["no"]: i for i in result["items"]}
        merged = [fresh.get(i["no"], i) for i in old["items"]]
        for no, i in fresh.items():                   # 新增的篇目追加
            if all(m["no"] != no for m in merged):
                merged.append(i)
        merged.sort(key=lambda m: m["no"])
        result["items"] = merged
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(i["candidates"]) for i in result["items"])
    print(f"\n共 {n} 条候选 -> {args.out}")
    for it in result["items"]:
        if not it["candidates"]:
            print(f"  [!] 第 {it['no']} 篇《{it['title']}》无候选，需换检索词")


# -------------------------------------------------------------- 下载 ------

def safe_filename(s):
    s = unicodedata.normalize("NFC", s)
    return re.sub(r'[\\/:*?"<>|]+', "", s).strip()


def pick_width_height(w, h):
    if w and h and w > MAX_SIDE:
        return MAX_SIDE, round(h * MAX_SIDE / w)
    return w, h


def cmd_download(args):
    data = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    issue = Path(args.issue_dir)
    photos = issue / "photos"
    photos.mkdir(parents=True, exist_ok=True)
    credits_path = Path("_tmp") / f"{issue.name}_credits.json"

    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    used, records = set(credits), []

    # 字数表
    words = {}
    contents = issue / "articles" / "contents.txt"
    if contents.exists():
        for line in contents.read_text(encoding="utf-8").splitlines()[1:]:
            tok = line.split()
            if len(tok) >= 4 and tok[-2].isdigit():
                words[" ".join(tok[:-2])] = int(tok[-2])

    for item in data["items"]:
        sel = [c for c in item["candidates"] if c.get("selected")]
        sel.sort(key=lambda c: c.get("order", 1))
        for order, c in enumerate(sel, start=1):
            base = safe_filename(c.get("target_file") or item["file"])
            fname = f"{base}.jpg" if order == 1 else f"{base}{order:02d}.jpg"
            if fname in used:
                print(f"  [skip] {fname} 已存在")
                continue
            url = resolve(c)
            if not url:
                print(f"  [fail] {fname}: 拿不到直链 {c['key']}")
                continue
            try:
                raw = _get(url, timeout=60).content
            except RuntimeError as e:
                print(f"  [fail] {fname}: 下载失败 {e}")
                continue
            info = save_jpeg(raw, photos / fname)
            if info is None:
                print(f"  [fail] {fname}: 非法图片数据 {c['key']}")
                continue
            w, h = info
            warn = "  [warn 小图]" if min(w, h) < MIN_SIDE else ""
            print(f"  [ok] {fname}  {w}x{h}  <- {c['source']} {c['key']}{warn}")
            used.add(fname)
            credits[fname] = dict(
                file=fname, article=item["title"], no=item["no"],
                key=c["key"], source=c["source"], source_name=SOURCE_NAME[c["source"]],
                id=str(c["id"]), title=c["title"], artist=c["artist"], date=c["date"],
                medium=c["medium"], page_url=c["page_url"], license=c["license"],
                origin_url=url, summary=c.get("summary", ""),
            )
            records.append(fname)
        # 每篇结束保存一次，中断不丢
        credits_path.parent.mkdir(parents=True, exist_ok=True)
        credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")

    write_phototags(credits, issue, words)
    print(f"\n新增 {len(records)} 张；元数据 -> {credits_path}")


def save_jpeg(raw: bytes, path: Path):
    from io import BytesIO
    try:
        from PIL import Image
    except ImportError:
        sys.exit("需要 Pillow：pip install pillow")
    try:
        im = Image.open(BytesIO(raw))
        im.load()
    except Exception:
        return None
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > MAX_SIDE:
        im = im.resize(pick_width_height(w, h), Image.LANCZOS)
    im.save(path, "JPEG", quality=90)
    return im.size


def write_phototags(credits: dict, issue: Path, words: dict):
    lines = ["文件名 | 所属文章 | 尺寸(宽x高px) | 所属文章字数 | 内容大致 | 来源与许可"]
    for fname, c in sorted(credits.items(), key=lambda kv: (kv[1]["no"], kv[0])):
        from PIL import Image
        with Image.open(issue / "photos" / fname) as im:
            size = f"{im.width}x{im.height}"
        src = f"{c['source_name']}，{c['license']}"
        if c.get("artist"):
            src = f"{c['artist']}，{src}"
        lines.append(f"{fname} | {c['article']} | {size} | {words.get(c['article'],'')} | "
                     f"{c.get('summary','')} | {src}")
    out = issue / "photos" / "phototags.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"phototags.txt -> {out}（{len(lines)-1} 图）")


# -------------------------------------------------------------- 速览 ------

def cmd_contact(args):
    issue = Path(args.issue_dir)
    credits_path = Path("_tmp") / f"{issue.name}_credits.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    rows = []
    for fname, c in sorted(credits.items(), key=lambda kv: (kv[1]["no"], kv[0])):
        rows.append(
            f'<figure><img src="../{issue.as_posix()}/photos/{fname}" alt="{fname}">'
            f"<figcaption><b>{c['article']}</b><br>{fname}<br>"
            f"{c.get('summary','')}<br><small>{c['source_name']} · {c['license']} · "
            f"{c['title']} ({c['date']})</small></figcaption></figure>")
    head = ("<!doctype html><meta charset='utf-8'><title>插图速览</title><style>"
            "body{font-family:sans-serif;background:#222;color:#eee}"
            "figure{display:inline-block;width:300px;vertical-align:top;margin:8px;"
            "background:#333;padding:8px;border-radius:4px}"
            "img{max-width:100%;height:auto}figcaption{font-size:12px;margin-top:6px;line-height:1.5}"
            f"</style><h1>插图速览（{len(rows)} 张）</h1>")
    Path(args.out).write_text(head + "".join(rows), encoding="utf-8")
    print(f"速览页 -> {args.out}")


# --------------------------------------------------------------- CLI -----

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe").set_defaults(fn=cmd_probe)

    p = sub.add_parser("search")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sources", default="", help="逗号分隔，默认全部")
    p.add_argument("--only", default="", help="只跑指定文章序号（逗号分隔），结果并入 --out")
    p.add_argument("--limit", type=int, default=6, help="每个检索词保留的候选数")
    p.add_argument("--min-side", type=int, default=640)
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser("download")
    p.add_argument("--candidates", required=True)
    p.add_argument("--issue-dir", required=True)
    p.set_defaults(fn=cmd_download)

    p = sub.add_parser("contact")
    p.add_argument("--issue-dir", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_contact)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
