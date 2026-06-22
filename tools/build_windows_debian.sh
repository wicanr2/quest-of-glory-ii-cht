#!/usr/bin/env bash
# 本地 Windows build:Linux 上交叉編譯 ScummVM(AGS engine)→ scummvm.exe + 相依 DLL。
# 工具鏈與踩過的雷固化在 docker/Dockerfile.win-cross(首次自動 build,之後重用)。
# 與 CI 的 MSYS2 同一套 mingw-w64 GCC,只是換在 Linux 上 cross。產出 out/win-debian/。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
[ -d scummvm-src ] || { echo "!! 先備妥 scummvm-src(tools/dev-setup.sh)"; exit 1; }
IMAGE="qfg2-win-cross"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "==> 首次:build 工具鏈 image($IMAGE)"
  docker build -f docker/Dockerfile.win-cross -t "$IMAGE" docker/
fi

rm -rf out/win-debian; mkdir -p out/win-debian
echo "==> 交叉編譯(源碼複製到 /tmp 編,不污染工作樹)"
docker run --rm \
  -v "$ROOT/scummvm-src":/src:ro -v "$ROOT/out/win-debian":/out \
  "$IMAGE" bash -c '
set -e
HOST=x86_64-w64-mingw32
export PKG_CONFIG_PATH="/usr/x86_64-w64-mingw32/lib/pkgconfig"   # 讓 configure 找到 sysroot 的 vorbis
mkdir -p /tmp/build && cp -a /src/. /tmp/build/ && cd /tmp/build
rm -f scummvm scummvm.exe config.log config.mk; find . -name "*.o" -delete 2>/dev/null || true

# vorbis 啟用(背景音樂 ogg);flac/mad/freetype/png 等遊戲用不到的 codec 仍關以縮小依賴
./configure --host=$HOST --disable-all-engines --enable-engine=ags --enable-release \
  --with-sdl-prefix="$SDL2_MINGW/bin" \
  --disable-fluidsynth --disable-flac --disable-mad --disable-png \
  --disable-freetype2 --disable-theoradec --disable-faad --disable-mpeg2 --disable-a52 \
  --disable-libcurl --disable-sndio --disable-timidity --disable-sparkle \
  --disable-nuked-opl --disable-eventrecorder \
  >/tmp/cfg.log 2>&1 || { echo "### CONFIGURE FAILED ###"; tail -30 /tmp/cfg.log; exit 11; }
echo "    configure OK — $(grep -m1 "^Backend" /tmp/cfg.log)"
echo "    vorbis: $(grep -iE "Ogg Vorbis|vorbis support" /tmp/cfg.log | head -1 || echo "(未列)")"

make -j"$(nproc)" >/tmp/make.log 2>&1 || { echo "### MAKE FAILED ###"; tail -45 /tmp/make.log; exit 12; }
$HOST-strip scummvm.exe
echo "    scummvm.exe(stripped)= $(stat -c%s scummvm.exe) bytes"

# 收集執行期 DLL:SDL2 + zlib1 + gcc/c++ runtime
cp scummvm.exe /out/
cp "$SDL2_MINGW/bin/SDL2.dll" /out/
ZLIB=$(find /usr -name zlib1.dll 2>/dev/null | head -1); [ -n "$ZLIB" ] && cp "$ZLIB" /out/ || echo "  ! 找不到 zlib1.dll"
for dll in libgcc_s_seh-1 libstdc++-6 libwinpthread-1; do
  f=$(find /usr/lib/gcc/$HOST -name "$dll.dll" 2>/dev/null | head -1); [ -n "$f" ] && cp "$f" /out/ || true
done
chmod -R a+rw /out

echo "=== exe 需要的 DLL(逐一對照 out/ 是否齊備)==="
for d in $($HOST-objdump -p scummvm.exe | awk "/DLL Name:/{print \$3}" | sort -u); do
  case "$d" in
    *.dll|*.DLL|*.Drv|*.DRV)
      low=$(echo "$d" | tr "A-Z" "a-z")
      if echo "$low" | grep -qE "^(kernel32|user32|gdi32|shell32|winmm|winspool|ole32|msvcrt|advapi32|version|imm32|setupapi|oleaut32)"; then
        echo "  $d  → 系統內建(免帶)"
      elif [ -f "/out/$d" ] || [ -f "/out/$low" ]; then
        echo "  $d  → ✓ 已打包"
      else
        echo "  $d  → ✗ 缺!"
      fi ;;
  esac
done
echo "BUILD_OK"
'
echo "==> 完成:out/win-debian/"
ls -la out/win-debian/
