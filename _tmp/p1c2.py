# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"_tmp")
from colsum import page_cols
n, cols, imgs = page_cols(1)
for ci, c in enumerate(cols):
    print(f"===== col{ci+1} ({len(c)} lines) =====")
    for l in c:
        print(f"  y={l['y']:6.1f} | {l['text']}")
