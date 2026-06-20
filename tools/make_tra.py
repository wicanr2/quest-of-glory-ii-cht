#!/usr/bin/env python3
"""把翻譯 TSV 編成 AGS `.tra`(ScummVM ags engine 可讀),並輸出所用 CJK 字集。

格式權威來源:ScummVM engines/ags/shared/game/tra_file.cpp
  header  = "AGSTranslation\0"            (15 bytes)
  block   = int32 block_id + int32 size_placeholder + <content> (回填 size)
            GameID(2): int32 GameUid + WriteString(enc(name), len+1)
            Dict(1)  : 每對 WriteString(enc(src),len+1) + WriteString(enc(dst),len+1)
                       結尾兩個空字串(enc 空 = 單一加密 null)
            TextOpts(3): int32 NormalFont, SpeechFont, RightToLeft
  EOF     = int32 -1
  WriteString(s,len) = int32 len + len bytes
  加密 = encrypt_text:byte[i] += "Avis Durgan"[i % 11](含結尾 null 一起加密)

GameUid=0 + 空 GameName → 引擎跳過 game 比對(TestTraGameID)。

TSV 格式(UTF-8):每行 `英文原文<TAB>繁體中文`;# 開頭為註解;空中文跳過。
用法:
  python3 tools/make_tra.py tools/translation.tsv --out game/chinese.tra --charset-out build/charset.txt
"""
import argparse, struct, sys

KEY = b"Avis Durgan"  # AGS passwencstring

def encrypt(text: str) -> bytes:
    raw = text.encode("utf-8") + b"\x00"   # 含結尾 null
    return bytes((b + KEY[i % 11]) & 0xFF for i, b in enumerate(raw))

def wstr_enc(text: str) -> bytes:
    enc = encrypt(text)
    return struct.pack("<i", len(enc)) + enc   # len 含 null(= utf8len+1)

def block(block_id: int, content: bytes) -> bytes:
    # 數字 id 區塊:int32 id + int32 size + content(File32)
    return struct.pack("<ii", block_id, len(content)) + content

def wstr_plain(s: str) -> bytes:
    # StrUtil::WriteString:int32 len + bytes(不加密、不含 null)
    b = s.encode("utf-8")
    return struct.pack("<i", len(b)) + b

def block_strid(ext_id: str, content: bytes) -> bytes:
    # 字串 id 區塊(block==0):int32 0 + 16-byte id + int64 size + content
    idbuf = ext_id.encode("utf-8")[:16].ljust(16, b"\x00")
    return struct.pack("<i", 0) + idbuf + struct.pack("<q", len(content)) + content

def strmap(d: dict) -> bytes:
    # StrUtil::WriteStringMap:int32 count + (WriteString key + WriteString val)*
    out = struct.pack("<i", len(d))
    for k, v in d.items():
        out += wstr_plain(k) + wstr_plain(v)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--out", default="game/chinese.tra")
    ap.add_argument("--charset-out", default="build/charset.txt")
    ap.add_argument("--normal-font", type=int, default=-1)
    ap.add_argument("--speech-font", type=int, default=-1)
    args = ap.parse_args()

    pairs = []
    with open(args.tsv, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            if "\t" not in line:
                print(f"  跳過第 {ln} 行(無 tab): {line[:40]}", file=sys.stderr)
                continue
            src, dst = line.split("\t", 1)
            if not dst.strip():
                continue
            pairs.append((src, dst))

    # 自創/系列專屬名詞首次出現時附原文(使用者要求:特殊名詞旁放英文)。
    # 每句每詞只加一次;已被括號跟隨者跳過。長詞先處理避免子詞重疊(卡塔族 > 卡塔)。
    GLOSS = {
        "恐魯斯": "Terrorsaurus", "索魯斯": "Saurus", "卡塔": "Katta",
        "獅人": "Liontaur", "鎮尼": "Djinni", "豺狼人": "Jackalman",
        "阿德·阿維斯": "Ad Avis", "伊布利斯": "Iblis", "夏皮爾": "Shapeir", "拉希爾": "Raseir",
    }
    def gloss(text):
        for zh in sorted(GLOSS, key=len, reverse=True):
            i = text.find(zh)
            if i < 0:
                continue
            after = i + len(zh)
            if after < len(text) and text[after] in "(（":
                continue  # 已加註
            text = text[:after] + f"({GLOSS[zh]})" + text[after:]
        return text
    pairs = [(src, gloss(dst)) for src, dst in pairs]

    # GameID block:uid=0, name=""
    gameid = struct.pack("<i", 0) + wstr_enc("")
    # Dict block
    dict_buf = bytearray()
    for src, dst in pairs:
        dict_buf += wstr_enc(src)
        dict_buf += wstr_enc(dst)
    dict_buf += wstr_enc("")  # 結尾空 key
    dict_buf += wstr_enc("")  # 結尾空 value
    data = b"AGSTranslation\x00"
    data += block(2, gameid)       # kTraFblk_GameID
    data += block(1, bytes(dict_buf))  # kTraFblk_Dict
    # TextOpts 只在需要覆蓋字型時輸出;-1 表預設(引擎以 >=0 才套用)。
    if args.normal_font >= 0 or args.speech_font >= 0:
        textopts = struct.pack("<iii", args.normal_font, args.speech_font, -1)
        data += block(3, textopts) # kTraFblk_TextOpts
    # ext_sopts:宣告譯文為 UTF-8,讓 init_translation 設 set_uformat(U_UTF8)
    data += block_strid("ext_sopts", strmap({"encoding": "utf-8"}))
    data += struct.pack("<i", -1)  # kTraFile_EOF

    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(data)

    # CJK 字集(所有譯文中的非 ASCII 字)
    charset = set()
    for _, dst in pairs:
        for ch in dst:
            if ord(ch) > 0x2000:
                charset.add(ch)
    os.makedirs(os.path.dirname(args.charset_out) or ".", exist_ok=True)
    with open(args.charset_out, "w", encoding="utf-8") as f:
        f.write("".join(sorted(charset)))

    print(f"OK: {len(pairs)} 對 → {args.out} ({len(data)} bytes);CJK {len(charset)} 字 → {args.charset_out}")

if __name__ == "__main__":
    main()
