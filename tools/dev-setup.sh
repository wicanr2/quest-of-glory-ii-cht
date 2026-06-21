#!/usr/bin/env bash
# 一鍵 bootstrap:從零把繁中化專案 build 到可打包。全程 Docker,不污染系統。
# 需求:Docker + 原版遊戲解壓到 game/(game/Qfg2vga.exe 存在)。詳見 docs/DEV-SETUP.md。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

command -v docker >/dev/null || { echo "!! 需要 Docker。見 docs/DEV-SETUP.md"; exit 1; }
[ -f game/Qfg2vga.exe ] || { echo "!! 找不到 game/Qfg2vga.exe。請先把原版(agdinteractive.com)解壓到 game/"; exit 1; }

echo "==> [1/5] 建 builder image(qfg2-scummvm-builder)"
docker build -q -t qfg2-scummvm-builder -f tools/Dockerfile.builder tools/ >/dev/null

echo "==> [2/5] 取 pinned 上游 ScummVM + 套 CJK patch"
bash tools/apply_patches.sh "$ROOT/scummvm-src"

echo "==> [3/5] 編譯 ScummVM(只開 ags engine)"
docker run --rm -v "$ROOT/scummvm-src":/src -w /src qfg2-scummvm-builder bash -c '
  [ -f config.mk ] || ./configure --disable-all-engines --enable-engine=ags
  make -j"$(nproc)"'

echo "==> [4/5] 烘 16/24px 字型 + 產生 chinese.tra"
docker run --rm -v "$ROOT":/work -v /usr/share/fonts:/usr/share/fonts:ro -w /work \
  ghcr.io/astral-sh/uv:python3.12-bookworm-slim bash -c '
    uv venv -q && uv pip install -q pillow
    uv run tools/make_tra.py tools/translation.tsv --out game/chinese.tra --charset-out build/charset.txt
    uv run tools/build_cjk_font.py --size 16 --charset-file build/charset.txt --bin game/cjkfont16.bin --out build/cjk16
    uv run tools/build_cjk_font.py --size 24 --charset-file build/charset.txt --bin game/cjkfont24.bin --out build/cjk24'
echo "==> [5/5] 角色創建中文背景(headless dump 原版 bg + OpenCV inpaint;best-effort)"
bash tools/make_roombg.sh || echo "   (略過:此步需 headless 進角色創建,失敗不擋;稍後可單獨 bash tools/make_roombg.sh)"

echo "==> 完成。下一步:"
echo "    bash tools/package_release.sh linux     # 組完整可玩包(含遊戲)→ out/release/"
echo "    bash tools/run_cht.sh                    # 無頭跑一輪、dump 截圖驗證"
