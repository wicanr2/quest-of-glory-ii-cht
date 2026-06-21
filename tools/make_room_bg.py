#!/usr/bin/env python3
# 角色創建 room 背景中文化(美術):讀乾淨原版 bg + manifest,用 OpenCV inpaint
# 把屬性名英文區的卷軸紋理補回來(content-aware,不是填單色),再畫中文。
# 產出中文版 bg(cht_roombg<N>.bin),引擎在中文模式替換、F8 切回原版。
#
# 用法: make_room_bg.py <origbg.raw> <manifest.txt> <out.bin> [font.ttc]
#   origbg.raw: 引擎 dump 的乾淨原版 bg(int32 w,h,bpp + BGRA),版權美術只在本機處理
import sys, struct
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

RAW  = sys.argv[1] if len(sys.argv) > 1 else "out/cap/cb.origbg502.raw"
MAN  = sys.argv[2] if len(sys.argv) > 2 else "tools/cht_room502.txt"
OUT  = sys.argv[3] if len(sys.argv) > 3 else "game/cht_roombg502.bin"
FONT = sys.argv[4] if len(sys.argv) > 4 else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
DIL  = int(sys.argv[5]) if len(sys.argv) > 5 else 4   # dilate 大小(金框內職業名用小避免破壞金框)
THR  = int(sys.argv[6]) if len(sys.argv) > 6 else 330  # 深色閾值(room503 淺色米黃字要調高才抓得到)
MINS = int(sys.argv[7]) if len(sys.argv) > 7 else 0    # 最小 sum(503 排金框外黑底用100;502 屬性名深褐字 sum~82 須用0)
MODE = sys.argv[8] if len(sys.argv) > 8 else "sum"     # mask 模式:sum=深色字(502);hsv=米黃字亮本體+暗描邊、避金框(503)

d = open(RAW, "rb").read()
w, h, bpp = struct.unpack("<iii", d[:12])
assert bpp == 4
arr = np.frombuffer(d[12:], dtype=np.uint8).reshape(h, w, 4).copy()   # BGRA
bgr = arr[:, :, :3].copy()

# 讀 manifest(x y 中文)
items = []
for ln in open(MAN, encoding="utf-8"):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    p = ln.split()
    if len(p) >= 3:
        fs = int(p[3]) if len(p) >= 4 else 14   # 第4欄=字級(預設14;底部窄欄用11)
        rw = int(p[4]) if len(p) >= 5 else 95   # 第5欄=清除寬度(金框內職業名用窄,預設95)
        items.append((int(p[0]), int(p[1]), p[2], fs, rw))

# mask:屬性名 rect 內的英文字 pixel,inpaint 用周圍補
mask = np.zeros((h, w), np.uint8)
hsvimg = cv2.cvtColor(bgr.astype(np.uint8), cv2.COLOR_BGR2HSV) if MODE == "hsv" else None
for (x, y, _t, fs, rw) in items:
    RH = fs + 2
    x0, y0 = max(0, x - 3), max(0, y - 2)
    x1, y1 = min(w, x + rw), min(h, y + RH)
    if MODE == "fill":
        # 浮雕同色字(職業名筆畫=金框金色,亮度/色相都分不開):不分字,整個 rect 全 mask,
        # inpaint 從 rect 外的金框內金黃補進填平。rect 須精確在金框內、避開金框邊框。
        mask[y0:y1, x0:x1] = 255
    elif MODE == "hsv":
        Vr = hsvimg[y0:y1, x0:x1, 2].astype(int)
        m = (Vr >= 175) | ((Vr >= 55) & (Vr < 120))
        mask[y0:y1, x0:x1][m] = 255
    else:
        rsum = bgr[y0:y1, x0:x1].astype(int).sum(axis=2)
        m = (rsum >= MINS) & (rsum < THR)    # 深色字(502 卷軸);MINS>0 排黑底
        mask[y0:y1, x0:x1][m] = 255
mask = cv2.dilate(mask, np.ones((DIL, DIL), np.uint8))   # 擴張涵蓋抗鋸齒邊

inp = cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)   # 卷軸紋理修復

# 取屬性名原英文字色(深褐)當中文色:用 mask 區原圖最暗 pixel
dk = bgr[mask > 0].astype(int)
if len(dk):
    textcol = tuple(int(c) for c in dk[dk.sum(axis=1).argmin()])   # BGR 最暗
else:
    textcol = (40, 50, 70)

im = Image.fromarray(cv2.cvtColor(inp, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(im)
fill = (textcol[2], textcol[1], textcol[0])          # BGR→RGB
_fcache = {}
for (x, y, t, fs, rw) in items:
    if fs not in _fcache:
        _fcache[fs] = ImageFont.truetype(FONT, fs)
    draw.text((x, y - 1), t, fill=fill, font=_fcache[fs])

# 存中文版 bg.bin(int32 w,h + BGRA),引擎讀
rgba = np.array(im.convert("RGBA"))
out = bytearray(struct.pack("<ii", w, h))
for yy in range(h):
    for xx in range(w):
        r, g, b, a = rgba[yy, xx]
        out += bytes([b, g, r, 255])
open(OUT, "wb").write(out)
im.convert("RGB").resize((w * 2, h * 2), Image.NEAREST).save(OUT.replace(".bin", "_preview.png"))
print(f"中文版 room bg → {OUT} ({w}x{h}, {len(items)} 屬性名, 文字色 BGR={textcol})")
