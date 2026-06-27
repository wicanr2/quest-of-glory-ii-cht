#!/usr/bin/env bash
# 打包 self-contained AppImage:patched ScummVM 引擎 + 原版遊戲 + 繁中資產 + 依賴 .so。
# 雙擊即玩,不需安裝、不依賴系統 SDL2。全程 Docker(builder image)。
# 產出:out/release/英雄傳奇II-烈火神兵-x86_64.AppImage
# 注意:內含 AGDI 版權遊戲檔,僅供本機測試,勿公開散布。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
ENGINE="${ENGINE:-$ROOT/scummvm-src/scummvm}"
[ -x "$ENGINE" ]         || { echo "!! 找不到引擎 $ENGINE,先 bash tools/dev-setup.sh"; exit 1; }
[ -f game/Qfg2vga.exe ]  || { echo "!! game/ 無原版遊戲"; exit 1; }
[ -f game/chinese.tra ]  || { echo "!! game/ 無 chinese.tra,先 dev-setup 烘資產"; exit 1; }
mkdir -p out/release build/appimage
cd build/appimage

# AppRun:AppImage 每次 mount 到隨機路徑,故每次依 $HERE 重生 config 指向當前遊戲目錄
cat > AppRun <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export LD_LIBRARY_PATH="$HERE/usr/lib:${LD_LIBRARY_PATH:-}"
GAMEDIR="$HERE/usr/share/qfg2agdi"
CFGDIR="${XDG_CONFIG_HOME:-$HOME/.config}/qfg2-cht"; mkdir -p "$CFGDIR"
CFG="$CFGDIR/scummvm.ini"
cat > "$CFG" <<INI
[scummvm]
gui_browser_native=false

[qfg2agdi]
engineid=ags
gameid=qfg2agdi
description=Quest for Glory II: Trial by Fire (CHT)
path=$GAMEDIR
translation=chinese
INI
exec "$HERE/usr/bin/scummvm" --config="$CFG" --themepath="$HERE/usr/share/scummvm" --extrapath="$HERE/usr/share/scummvm" qfg2agdi "$@"
EOF

cat > qfg2-cht.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=英雄傳奇II 烈火神兵
Comment=Quest for Glory II Trial by Fire (CHT)
Exec=scummvm
Icon=qfg2-cht
Categories=Game;
Terminal=false
EOF

cd "$ROOT"
docker run --rm -e APPIMAGE_EXTRACT_AND_RUN=1 -v "$ROOT":/work -w /work/build/appimage qfg2-scummvm-builder bash -c '
set -e
apt-get update -qq && apt-get install -y -qq wget file imagemagick >/dev/null 2>&1
A=/work/build/appimage/AppDir
rm -rf "$A"; mkdir -p "$A/usr/bin" "$A/usr/lib" "$A/usr/share/qfg2agdi" "$A/usr/share/icons/hicolor/256x256/apps"
cp /work/scummvm-src/scummvm "$A/usr/bin/scummvm"
cp -r /work/game/. "$A/usr/share/qfg2agdi/"
# ScummVM 執行需要的 data 檔(GUI theme + engine data);缺了 theme 載入失敗、編碼/字型異常
mkdir -p "$A/usr/share/scummvm"
for f in scummmodern.zip scummclassic.zip scummremastered.zip residualvm.zip gui-icons.dat shaders.dat translations.dat; do cp "/work/scummvm-src/gui/themes/$f" "$A/usr/share/scummvm/" 2>/dev/null || true; done
for f in achievements.dat classicmacfonts.dat encoding.dat fonts-cjk.dat fonts.dat macgui.dat helpdialog.zip; do cp "/work/scummvm-src/dists/engine-data/$f" "$A/usr/share/scummvm/" 2>/dev/null || true; done
cp /work/scummvm-src/dists/networking/wwwroot.zip "$A/usr/share/scummvm/" 2>/dev/null || true
convert /work/docs/screenshot-charcreate-attribs.png -resize 256x256^ -gravity center -extent 256x256 "$A/qfg2-cht.png"
cp "$A/qfg2-cht.png" "$A/usr/share/icons/hicolor/256x256/apps/qfg2-cht.png"
cp /work/build/appimage/qfg2-cht.desktop "$A/qfg2-cht.desktop"
[ -f linuxdeploy-x86_64.AppImage ]   || wget -q https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
[ -f appimagetool-x86_64.AppImage ]  || wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage appimagetool-x86_64.AppImage
# linuxdeploy:ldd scummvm,把非系統依賴 .so 收進 usr/lib + 修 rpath(glibc/libGL 等走 excludelist 不收)
./linuxdeploy-x86_64.AppImage --appdir "$A" --executable "$A/usr/bin/scummvm" -i "$A/qfg2-cht.png" -d "$A/qfg2-cht.desktop"
# linuxdeploy excludelist 會排掉 ALSA/JACK/PulseAudio 等(假設系統有),但這些是 scummvm 的
# load-time 依賴,缺一個就無法啟動,且 JACK 在多數桌面根本沒裝 → 把 ldd 全依賴補進 usr/lib,
# 只跳過 glibc 核心與 display/GL(那些必須用 host 的,bundle 反而會跟驅動/顯示伺服器衝突)
for lib in $(ldd "$A/usr/bin/scummvm" | awk "/=> \// {print \$3}"); do
  base=$(basename "$lib")
  case "$base" in
    libc.so*|libm.so*|libpthread.so*|libdl.so*|librt.so*|ld-linux*|libresolv.so*|libpcre*) continue;;
    libGL*|libEGL*|libGLX*|libGLdispatch*|libOpenGL*|libdrm*|libX*|libxcb*|libxshmfence*|libwayland*|libgbm*|libxkbcommon*) continue;;
  esac
  [ -f "$A/usr/lib/$base" ] || cp -L "$lib" "$A/usr/lib/" 2>/dev/null || true
done
# 覆蓋成自訂 AppRun(自動帶 --config + qfg2agdi 跑遊戲,而非進 ScummVM launcher)
# 注意:linuxdeploy 把 AppRun 建成 symlink→usr/bin/scummvm,直接 cp 會寫穿 symlink 毀掉 binary
rm -f "$A/AppRun"
cp /work/build/appimage/AppRun "$A/AppRun"; chmod +x "$A/AppRun"
ARCH=x86_64 ./appimagetool-x86_64.AppImage "$A" /work/out/release/英雄傳奇II-烈火神兵-x86_64.AppImage
chown -R '"$(id -u):$(id -g)"' /work/out/release /work/build/appimage
'
echo ">> 完成:"
ls -la out/release/*.AppImage
