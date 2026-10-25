# -*- coding: utf-8 -*-
"""从 PDF 内容流精确重建视觉行:逐 BT 块跟踪 Td/Tj,经 ToUnicode 解码"""
import sys, io, re, json
import PyPDF2

MM = 72/25.4
reader = PyPDF2.PdfReader(r"D:\CloudyInkForge\pentium\2611\2611.pdf")

def build_cmaps(page):
    cmaps = {}
    fonts = page["/Resources"].get("/Font", {})
    for fname in fonts:
        f = fonts[fname].get_object()
        tu = f.get("/ToUnicode")
        if tu is None:
            cmaps[str(fname)] = {}
            continue
        data = tu.get_object().get_data().decode('latin-1')
        m = {}
        for sec in re.findall(r'beginbfchar(.*?)endbfchar', data, re.S):
            for bf, uni in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', sec):
                m[int(bf, 16)] = ''.join(chr(int(uni[i:i+4], 16)) for i in range(0, len(uni), 4))
        for sec in re.findall(r'beginbfrange(.*?)endbfrange', data, re.S):
            for a, b, u in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', sec):
                a, b, u0 = int(a,16), int(b,16), int(u,16)
                for g in range(a, b+1):
                    m[g] = chr(u0 + (g - a))
        cmaps[str(fname)] = m
    return cmaps

TOK = re.compile(r'''
    (?P<hex><[0-9A-Fa-f\s]*>) |
    (?P<str>\((?:\.|[^\()])*\)) |
    (?P<num>[-+]?\d*\.?\d+) |
    (?P<op>/[^\s/\[\]<>()]+) |
    (?P<any>[\[\]{}]) |
    (?P<kw>[A-Za-z'"*]+)
''', re.X)

def parse_page(pno):
    page = reader.pages[pno-1]
    cmaps = build_cmaps(page)
    data = page.get_contents().get_data().decode('latin-1')
    lines = []          # {y,x,text,fs,blk}
    x = y = 0.0; fs = 0.0; font = None
    in_bt = False
    blk = 0
    for m in TOK.finditer(data):
        if m.lastgroup == 'kw':
            op = m.group()
            if op == 'BT': in_bt = True; blk += 1
            elif op == 'ET': in_bt = False
            elif op == 'Td': pass  # 数值在后面处理
        elif m.lastgroup == 'num':
            pass
    # 简化:顺序扫描 token 流,维护操作数栈
    stack = []
    x = y = 0.0; fs = 0.0
    in_bt = False; blk = 0
    cur = None   # 当前行 {y,x0,text}
    def flush():
        nonlocal cur
        if cur and cur["text"].strip():
            lines.append(cur)
        cur = None
    for m in TOK.finditer(data):
        kind, val = m.lastgroup, m.group()
        if kind == 'num':
            stack.append(float(val)); continue
        if kind == 'hex':
            stack.append(('hex', val)); continue
        if kind == 'str':
            stack.append(('str', val)); continue
        if kind == 'op':
            stack.append(['op', val]); continue
        if kind != 'kw':
            stack.append(val); continue
        op = val
        if op == 'BT':
            in_bt = True; blk += 1; x = y = 0.0; flush()
        elif op == 'ET':
            in_bt = False; flush()
        elif not in_bt:
            stack = []; continue
        elif op == 'Td' and len(stack) >= 2:
            dx, dy = stack[-2], stack[-1]
            if cur and abs(dy) > 0.5:   # 换行
                flush()
            x += dx; y += dy
            if cur is None:
                cur = {"y": round(y/MM,2), "x": round(x/MM,2), "text": "", "fs": fs, "blk": blk}
            stack = []
        elif op == 'Tf' and len(stack) >= 2:
            fs = stack[-1]
            for sv in stack:
                if isinstance(sv, list) and sv and sv[0] == 'op':
                    font = sv[1]
            stack = []
        elif op in ('Tj', "'", '"') and stack and isinstance(stack[-1], tuple):
            kind2, raw = stack[-1]
            cmap = cmaps.get(font, {}) if font else {}
            txt = ''
            if kind2 == 'hex':
                hx = re.sub(r'[<>\s]', '', raw)
                for i in range(0, len(hx)-3, 4):
                    g = int(hx[i:i+4], 16)
                    txt += cmap.get(g, '?')
            else:
                txt = raw[1:-1]
            if cur is None:
                cur = {"y": round(y/MM,2), "x": round(x/MM,2), "text": "", "fs": fs, "blk": blk}
            cur["text"] += txt
            stack = []
        elif op == 'TJ':
            # 数组内 hex
            arr = [s for s in stack if isinstance(s, tuple) and s[0]=='hex']
            if arr:
                cmap = cmaps.get(font, {}) if font else {}
                txt = ''
                for _, raw in arr:
                    hx = re.sub(r'[<>\s]', '', raw)
                    for i in range(0, len(hx)-3, 4):
                        txt += cmap.get(int(hx[i:i+4],16), '?')
                if cur is None:
                    cur = {"y": round(y/MM,2), "x": round(x/MM,2), "text": "", "fs": fs, "blk": blk}
                cur["text"] += txt
            stack = []
        elif op == 'Tm' and len(stack) >= 6:
            x, y = stack[-2], stack[-1]
            if cur and abs(y/MM - cur["y"]) > 0.5: flush()
            if cur is None:
                cur = {"y": round(y/MM,2), "x": round(x/MM,2), "text": "", "fs": fs, "blk": blk}
            stack = []
        elif op in ('Tc','Tw','Tz','TL','Ts','Tr','T*','gs','rg','k','K','w','J','j','d','cm','q','Q','Do','gs'):
            stack = []
        else:
            stack = []
    flush()
    return lines, cmaps

if __name__ == "__main__":
    pno = int(sys.argv[1])
    lines, _ = parse_page(pno)
    lines.sort(key=lambda l: (-l["y"], l["x"]))
    for l in lines:
        print(f"y={l['y']:7.2f} x={l['x']:7.2f} fs={l['fs']:4.1f} b{l['blk']:3d} | {l['text'][:50]}")
