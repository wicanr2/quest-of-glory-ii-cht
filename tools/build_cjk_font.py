#!/usr/bin/env python3
"""烘 CJK 點陣字型 atlas,供 ScummVM AGS 引擎 CJK 繪字 patch 使用。

輸出:
  atlas.png   — 灰階 (L) 點陣字圖,每格 size×size,橫向排 cols 格
  atlas.json  — { "size":24, "cols":N, "glyphs":{ "U+XXXX": cell_index, ... } }

charset 來源(擇一):
  --charset-file <txt>  讀檔內所有非 ASCII 漢字/標點(去重、排序)
  --common              內建常用字測試集(驗證管線與字型品質用)

用法(docker uv venv):
  uv run tools/build_cjk_font.py --size 24 --common --out fonts/cjk24
"""
import argparse, json, os, struct, sys
from PIL import Image, ImageFont, ImageDraw

# host 字型候選(rule:中文字形從 host 上面找)
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
]

# 驗證用常用字 + QFG 譯名常見字
COMMON_TEST = (
    "英雄傳奇沙佩爾拉塞爾貓族獅人冒險者公會魔法師學院"
    "你我他的是不了在有人這那要說生命力法力金幣經驗值"
    "向左向右上下前進後退攻擊防禦施法逃跑購買出售對話"
    "儲存讀取設定離開繼續開始新遊戲是否確定取消返回"
    "蘇丹城衛兵小偷沙漠綠洲駱駝商隊地毯神燈精靈火水風土"
    "，。、！？：；「」『』（）—…0123456789"
)

def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                # TTC index 0 = 預設(Noto 第一個 face);TC face 由 fontconfig 處理,
                # 對點陣烘製用預設 face 即可正確顯示繁體字形。
                return ImageFont.truetype(path, size, index=0), path
            except Exception as e:
                print(f"  跳過 {path}: {e}", file=sys.stderr)
    sys.exit("找不到可用的 host CJK 字型")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=24)
    ap.add_argument("--charset-file")
    ap.add_argument("--common", action="store_true")
    ap.add_argument("--cols", type=int, default=64)
    ap.add_argument("--out", default="fonts/cjk24")
    ap.add_argument("--bin", help="另輸出引擎用 .cjkfont 二進位(CJKF + glyph coverage)")
    args = ap.parse_args()

    chars = set()
    if args.common:
        chars |= set(COMMON_TEST)
    if args.charset_file:
        with open(args.charset_file, encoding="utf-8") as f:
            for ch in f.read():
                if ord(ch) > 0x2000:  # 排除 ASCII/控制字(ASCII 走原引擎字型)
                    chars.add(ch)
    chars = sorted(chars)
    if not chars:
        sys.exit("charset 為空,請給 --common 或 --charset-file")

    font, font_path = load_font(args.size)
    size, cols = args.size, args.cols
    rows = (len(chars) + cols - 1) // cols
    atlas = Image.new("L", (cols * size, rows * size), 0)
    draw = ImageDraw.Draw(atlas)

    glyphs = {}
    for i, ch in enumerate(chars):
        cx, cy = (i % cols) * size, (i // cols) * size
        # 置中:用 bbox 量測實際墨水範圍
        bbox = draw.textbbox((0, 0), ch, font=font)
        gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        ox = cx + (size - gw) // 2 - bbox[0]
        oy = cy + (size - gh) // 2 - bbox[1]
        draw.text((ox, oy), ch, fill=255, font=font)
        glyphs[f"U+{ord(ch):04X}"] = i

    # 引擎用二進位:'CJKF' + int32 size + int32 count
    #   每字:int32 codepoint + int32 advance(水平前進寬) + byte[size*size] coverage
    # 同時烘 ASCII 0x20-0x7E(同一套 Noto、等高、比例半寬),讓中英混排同大小/同基線。
    # 全字共用基線:em box 垂直置中,所有 glyph 以 anchor='la' 畫在固定 oy。
    if args.bin:
        ascent, descent = font.getmetrics()
        oy = (size - (ascent + descent)) // 2  # em box 垂直置中 → 共用基線
        bin_chars = list(chars) + [chr(c) for c in range(0x20, 0x7F)]
        os.makedirs(os.path.dirname(args.bin) or ".", exist_ok=True)
        with open(args.bin, "wb") as bf:
            bf.write(b"CJKF")
            bf.write(struct.pack("<ii", size, len(bin_chars)))
            cell = Image.new("L", (size, size), 0)
            cdraw = ImageDraw.Draw(cell)
            for ch in bin_chars:
                cdraw.rectangle([0, 0, size, size], fill=0)
                cp = ord(ch)
                glyph_w = font.getlength(ch)
                if cp >= 0x2000:                 # 全形:置中,advance = size
                    adv = size
                    ox = (size - round(glyph_w)) // 2
                else:                            # 半形 ASCII:左對齊,比例寬
                    adv = min(size, max(1, round(glyph_w)))
                    ox = 0
                cdraw.text((ox, oy), ch, fill=255, font=font, anchor="la")
                bf.write(struct.pack("<ii", cp, adv))
                bf.write(cell.tobytes())
        print(f"OK bin: {len(bin_chars)} 字(含 ASCII)@ {size}px → {args.bin}")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    atlas.save(args.out + ".png")
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump({"size": size, "cols": cols, "count": len(chars),
                   "font": font_path, "glyphs": glyphs}, f,
                  ensure_ascii=False, indent=0)
    print(f"OK: {len(chars)} 字 @ {size}px → {args.out}.png ({atlas.width}x{atlas.height}), 字型={font_path}")

if __name__ == "__main__":
    main()
