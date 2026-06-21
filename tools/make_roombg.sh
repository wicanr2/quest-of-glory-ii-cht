#!/usr/bin/env bash
# 產生角色創建 room 中文背景 cht_roombg502.bin(版權衍生美術,僅本機、不入庫):
#   1. headless 跑遊戲進角色創建畫面,引擎 dump 乾淨原版 room 背景(.origbg502.raw)
#   2. OpenCV inpaint(TELEA)依周圍卷軸紋理補回英文屬性名區,再印中文 → game/cht_roombg502.bin
# 引擎在中文模式載入此 bin、F8 可切回保存的原版;玩家填的數值不受影響。
# 全程 Docker,不污染系統。需求:已 build 的 scummvm-src + game/ 原版。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
[ -f scummvm-src/scummvm ] || { echo "!! 請先 bash tools/dev-setup.sh 編好引擎"; exit 1; }
[ -f game/Qfg2vga.exe ]   || { echo "!! 找不到 game/Qfg2vga.exe,請先放入原版"; exit 1; }
mkdir -p build
docker build -q -t qfg2-capture -f tools/Dockerfile.capture tools/ >/dev/null

echo "==> [1/2] headless 進角色創建畫面,dump 乾淨原版 room 背景(約 60s)"
docker run --rm -v "$ROOT/scummvm-src":/src -v "$ROOT/game":/game -v "$ROOT/build":/out qfg2-capture bash -c '
  export HOME=/tmp DISPLAY=:99
  Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
  cat >/out/rb.ini <<EOF
[scummvm]
[qfg2agdi]
gameid=qfg2agdi
path=/game
translation=chinese
engineid=ags
ags_dump_static=/out/rb
EOF
  # 偵測角色選擇選單的紅字按鈕(自適應等待,避開片頭 attract 動畫)
  cat >/tmp/red.py <<PY
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB"); px = im.load(); c = 0
for y in range(420, 610):
    for x in range(380, 580):
        r, g, b = px[x, y]
        if r > 175 and g < 75 and b < 70: c += 1
print(c)
PY
  timeout 110 /src/scummvm --config=/out/rb.ini qfg2agdi 2>/dev/null &
  sleep 7
  WID=$(xdotool search --onlyvisible --name . | tail -1)
  xdotool windowactivate --sync "$WID"; xdotool windowfocus "$WID"
  click(){ xdotool mousemove --sync $1 $2; sleep 0.15; xdotool mousedown 1; sleep 0.12; xdotool mouseup 1; }
  click 512 384                                  # 主選單 → New Game
  for i in $(seq 1 30); do sleep 1.4; import -window root /tmp/p.png 2>/dev/null
    R=$(python3 /tmp/red.py /tmp/p.png 2>/dev/null || echo 0); [ "${R:-0}" -gt 25 ] && break; done
  click 470 500; sleep 4                          # 確認 → 進角色創建
  click 280 408; sleep 4                          # 角色創建 room 502 載入(觸發 dump)
  pkill -f scummvm 2>/dev/null; sleep 1'
[ -f build/rb.origbg502.raw ] || { echo "!! dump 失敗(沒進到角色創建畫面);可重跑,座標依視窗大小可能要微調"; exit 1; }

echo "==> [2/2] OpenCV inpaint 補卷軸紋理 + 印中文 → game/cht_roombg502.bin"
docker run --rm -v "$ROOT":/work -v /usr/share/fonts:/usr/share/fonts:ro -w /work \
  ghcr.io/astral-sh/uv:python3.12-bookworm-slim bash -c '
    apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq libgl1 libglib2.0-0 >/dev/null 2>&1
    uv venv -q && uv pip install -q pillow numpy opencv-python-headless
    uv run tools/make_room_bg.py build/rb.origbg502.raw tools/cht_room502.txt game/cht_roombg502.bin'
echo "==> 完成:game/cht_roombg502.bin(中文模式套用,F8 切回原版)"
