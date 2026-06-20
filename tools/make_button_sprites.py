#!/usr/bin/env python3
# 重繪角色創建職業 button(AGS 美術 sprite,button 圖上印英文字,無法走 .tra)成中文,
# 打包成 cht_btnsprites.bin 供引擎 cht_load_button_sprites 注入(SetSprite 替換)。
#
# 前置:先用 patched 引擎 dump 原 sprite(設 ConfMan ags_dump_static),產生
#   <prefix>.spr<N>.raw / <prefix>.scan<N>.raw(int32 w,h,bpp + BGRA 像素)。
# 原 sprite 是 AGDI 版權美術,只在本機處理,不入 repo。
#
# 用法: make_button_sprites.py <raw_dir> <out.bin> [font.ttc]
import struct, sys, os, glob
from PIL import Image, ImageDraw, ImageFont

RAWDIR = sys.argv[1] if len(sys.argv) > 1 else "out/cap"
OUT    = sys.argv[2] if len(sys.argv) > 2 else "game/cht_btnsprites.bin"
FONT   = sys.argv[3] if len(sys.argv) > 3 else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# sprite 編號 -> 中文(由引擎 dump + 人工辨識比對 button 圖文字而來)
JOBS = {
    3:    "戰士",   # 屬性畫面 Fighter
    1947: "戰士",   # 職業選擇 Fighter(highlight,紅框選中)
    8129: "法師",   # 屬性畫面 Magic User
    1948: "法師",   # 職業選擇 Magic User(highlight) — 實機對應,非 sprite 文字
    1949: "盜賊",   # 職業選擇 Thief(highlight)
}

def find_raw(n):
    for pat in (f"*.spr{n}.raw", f"*.scan{n}.raw", f"*.rt{n}.raw"):
        hits = glob.glob(os.path.join(RAWDIR, pat))
        if hits:
            return hits[0]
    return None

def load_raw(p):
    d = open(p, "rb").read()
    w, h, bpp = struct.unpack("<iii", d[:12])
    if bpp != 4:
        return None, 0, 0
    return Image.frombytes("RGBA", (w, h), d[12:], "raw", "BGRA"), w, h

def redraw(im, w, h, text):
    bg = im.getpixel((6, h // 2))               # 卷軸背景色
    d = ImageDraw.Draw(im)
    d.rectangle([4, 3, w - 5, h - 4], fill=bg)  # 清原英文(保留外金框)
    font = ImageFont.truetype(FONT, 14 if h >= 18 else 13)
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (w - tw) // 2 - bb[0], (h - th) // 2 - bb[1] - 1
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        d.text((x + dx, y + dy), text, font=font, fill=(90, 55, 15, 255))   # 深褐描邊
    d.text((x, y), text, font=font, fill=(247, 221, 120, 255))             # 金字
    return im

entries = []
for idx, txt in sorted(JOBS.items()):
    rp = find_raw(idx)
    if not rp:
        print(f"  ! sprite {idx} 找不到 raw(需先 dump),跳過")
        continue
    im, w, h = load_raw(rp)
    if im is None:
        print(f"  ! sprite {idx} 非 32-bit,跳過")
        continue
    im = redraw(im, w, h, txt)
    bgra = bytearray()
    for yy in range(h):
        for xx in range(w):
            r, g, b, a = im.getpixel((xx, yy))
            bgra += bytes([b, g, r, a])
    entries.append((idx, w, h, bytes(bgra)))
    print(f"  sprite {idx} → {txt} ({w}x{h})")

with open(OUT, "wb") as f:
    f.write(struct.pack("<i", len(entries)))
    for idx, w, h, px in entries:
        f.write(struct.pack("<iii", idx, w, h))
        f.write(px)
print(f"打包 {len(entries)} 個職業 button → {OUT}")
