#!/usr/bin/env bash
# 把「patched ScummVM 引擎 + 原版遊戲 + 繁中資產 + 啟動器」組成完整可玩釋出包。
#
# 用法:
#   tools/package_release.sh linux                 # 用本機 build 的 Linux 引擎
#   ENGINE=path/to/scummvm.exe tools/package_release.sh windows   # 指定 Windows 引擎(+ DLL 目錄)
#   DLLDIR=path/to/dlls ENGINE=... tools/package_release.sh windows
#
# 注意:遊戲資料(game/)為 AGDI 版權檔,只在本機打包、不入公開 repo;
#       釋出時請遵循 AGDI 的散布條款(原版可於 agdinteractive.com 免費取得)。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLAT="${1:-linux}"
OUT="$ROOT/out/release/qfg2-cht-$PLAT"
GAME="$ROOT/game"

[ -d "$GAME" ] || { echo "找不到遊戲資料 $GAME(請先解壓原版到 game/)"; exit 1; }
rm -rf "$OUT"; mkdir -p "$OUT"

echo ">> 組裝 $PLAT 釋出包 → $OUT"

# 1) 遊戲資料(整包複製,排除我們的中文檔以免重複,稍後一起放)
rsync -a --exclude 'chinese.tra' --exclude 'cjkfont*.bin' "$GAME"/ "$OUT"/ 2>/dev/null || cp -r "$GAME"/* "$OUT"/

# 2) 繁中資產
cp "$GAME"/chinese.tra "$OUT"/ 2>/dev/null || { echo "缺 chinese.tra,先跑 build_release_assets.sh"; exit 1; }
cp "$GAME"/cjkfont16.bin "$GAME"/cjkfont24.bin "$OUT"/ 2>/dev/null || true

# 3) 預生成 scummvm.ini(把遊戲與 translation=chinese 烘進去,玩家免設定)
cat > "$OUT/scummvm.ini" <<'INI'
[scummvm]
gui_browser_native=false

[qfg2agdi]
engineid=ags
gameid=qfg2agdi
description=Quest for Glory II: Trial by Fire (CHT)
path=.
translation=chinese
INI

# 4) 引擎二進位 + 啟動器(依平台);啟動器先 cd 到包目錄,再 --config 跑 target
case "$PLAT" in
  linux)
    ENGINE="${ENGINE:-$ROOT/scummvm-src/scummvm}"
    [ -x "$ENGINE" ] || { echo "找不到 Linux 引擎 $ENGINE(先 build)"; exit 1; }
    cp "$ENGINE" "$OUT"/scummvm; chmod +x "$OUT"/scummvm
    cat > "$OUT/玩英雄傳奇II-繁中.sh" <<'LAUNCH'
#!/usr/bin/env bash
cd "$(dirname "$0")"
./scummvm --config=scummvm.ini qfg2agdi
LAUNCH
    chmod +x "$OUT/玩英雄傳奇II-繁中.sh"
    ;;
  windows)
    ENGINE="${ENGINE:?Windows 需指定 ENGINE=scummvm.exe(來自 CI windows job artifact)}"
    cp "$ENGINE" "$OUT"/scummvm.exe
    # 把相依 DLL 一起放(來自 DLLDIR;MinGW build 需 SDL2.dll、libstdc++-6.dll 等)
    if [ -n "${DLLDIR:-}" ] && [ -d "$DLLDIR" ]; then cp "$DLLDIR"/*.dll "$OUT"/ 2>/dev/null || true; fi
    cat > "$OUT/玩英雄傳奇II-繁中.bat" <<'LAUNCH'
@echo off
cd /d "%~dp0"
scummvm.exe --config=scummvm.ini qfg2agdi
LAUNCH
    ;;
  macos)
    ENGINE="${ENGINE:?macOS 需指定 ENGINE=ScummVM.app(來自 CI macos job)}"
    cp -R "$ENGINE" "$OUT"/ScummVM.app
    cat > "$OUT/玩英雄傳奇II-繁中.command" <<'LAUNCH'
#!/usr/bin/env bash
cd "$(dirname "$0")"
./ScummVM.app/Contents/MacOS/scummvm --config=scummvm.ini qfg2agdi
LAUNCH
    chmod +x "$OUT/玩英雄傳奇II-繁中.command"
    ;;
  *) echo "未知平台:$PLAT"; exit 1 ;;
esac

# 4) 玩家說明
cp "$ROOT/README.md" "$OUT/README.md" 2>/dev/null || true
cat > "$OUT/說明.txt" <<TXT
英雄傳奇 II:烈火試煉 — 繁體中文版

直接執行「玩英雄傳奇II-繁中」啟動器即可。
遊戲中按 F8 可循環切換:繁中16 → 繁中24 → 英文原版。

本包包含:patched ScummVM 引擎、原版遊戲資料、繁中翻譯(chinese.tra)與點陣字型。
原版遊戲由 AGD Interactive 製作(agdinteractive.com),請支持原作者。
TXT

echo ">> 完成。內容:"
ls -la "$OUT"
echo ">> 壓縮:"
( cd "$ROOT/out/release" && tar czf "qfg2-cht-$PLAT.tar.gz" "qfg2-cht-$PLAT" && ls -la "qfg2-cht-$PLAT.tar.gz" )
