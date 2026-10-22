import sys, re
from lxml import html as LH

SRC = r"D:\CloudyInkForge\pentium\2611\2611.html"
doc = LH.parse(SRC)
root = doc.getroot()
pages = root.xpath("//div[contains(concat(' ', normalize-space(@class), ' '), ' page ')]")
print("pages:", len(pages))
for p in pages:
    num = p.xpath(".//span[@class='footer-page']/text()")
    body = p.xpath("./div[contains(concat(' ',normalize-space(@class),' '),' page-body ')]")
    body = body[0] if body else None
    flows = body.xpath("./div[contains(concat(' ',normalize-space(@class),' '),' flow ')]") if body is not None else []
    print(f"\n=== page {num[0] if num else '?'} classes={p.get('class')!r} flows={len(flows)}")
    for fl in flows:
        print("  flow style:", fl.get('style'))
        for ch in fl:
            if not isinstance(ch.tag, str):
                continue
            cls = ch.get('class') or ''
            txt = re.sub(r"\s+", "", ch.text_content())
            tag = ch.tag
            extra = ''
            if tag == 'img':
                extra = ch.get('src')
            imgs = ch.xpath(".//img")
            if imgs:
                extra = " imgs=" + ",".join(i.get('src') for i in imgs)
            print(f"   - <{tag} class={cls!r}> chars={len(txt)}{extra}  text={txt[:22]!r}")
    # also non-flow body children
    if body is not None:
        for ch in body:
            if not isinstance(ch.tag, str):
                continue
            cls = ch.get('class') or ''
            if 'flow' in cls.split():
                continue
            print(f"   [body] <{ch.tag} class={cls!r}>")
