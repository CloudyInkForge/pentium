# -*- coding: utf-8 -*-
"""§2.6 同字体浏览器实测：逐页测 .body / .lead-text 各栏底余量（行数）与溢出"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

URL = "http://127.0.0.1:8931/unformed/青藏高原动物.html"

opts = Options()
opts.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
opts.add_argument("--headless=new")
opts.add_argument("--disable-gpu")
opts.add_argument("--force-device-scale-factor=1")
svc = Service(executable_path=r"C:\Users\y\.cache\selenium\chromedriver\win64\117.0.5938.149\chromedriver.exe")
driver = webdriver.Chrome(options=opts, service=svc)
try:
    driver.set_window_size(1200, 2000)
    driver.get(URL)
    driver.implicitly_wait(2)
    script = r"""
const MM = 96/25.4;
const linePx = 8.7 * 0.3528 * 1.49 * MM;
const pages = [...document.querySelectorAll('.page')];
const out = [];
pages.forEach((pg, i) => {
  const o = { page: i+1, body: [], lead: [] };
  const body = pg.querySelector('.body');
  const lt = pg.querySelector('.lead-text');
  function detail(container, ncol, colWmm, gapmm) {
    const cr = container.getBoundingClientRect();
    const colW = colWmm*MM, gap = gapmm*MM;
    const rows = [];
    [...container.children].forEach(el => {
      const rs = el.getClientRects();
      let lines = 0, cols = [];
      for (const rc of rs) {
        const cx = rc.left + rc.width/2 - cr.left;
        let ci = Math.floor(cx / (colW + gap) + 0.0001);
        if (ci < 0) ci = 0;
        if (ci >= ncol) ci = ncol; // spill
        if (!cols.includes(ci)) cols.push(ci);
        lines += rc.height / linePx;
      }
      rows.push({ tag: el.tagName, cls: el.className, L: +lines.toFixed(2), cols: cols.sort() });
    });
    return rows;
  }
  if (body) o.body = detail(body, 3, 55.67, 5.5);
  if (lt) o.lead = detail(lt, 1, 55.67, 5.5);
  out.push(o);
});
return out;
"""
    data = driver.execute_script(script)
    for p in data:
        print("== page", p["page"])
        for zone in ("lead", "body"):
            for r in p.get(zone) or []:
                print(f"  {zone:4s} {r['L']:6.2f}L c{r['cols']} {r['cls'][:18]:18s}")
finally:
    driver.quit()
