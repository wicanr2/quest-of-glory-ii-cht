#!/usr/bin/env bash
# 產生玩家用的繁中化資產(平台無關):chinese.tra + cjkfontNN.bin。
# 玩家把這兩個檔放進 QFG2 VGA 遊戲目錄,並設定 translation=chinese 即生效。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SIZE="${CJK_SIZE:-16}"
OUT="$ROOT/dist"
mkdir -p "$OUT" "$ROOT/build"

run() { # 在 docker uv venv 內跑 python(rule:不污染系統)
	docker run --rm -v "$ROOT":/work -v /usr/share/fonts:/usr/share/fonts:ro -w /work \
		ghcr.io/astral-sh/uv:python3.12-bookworm-slim bash -c "$1"
}

run "uv venv -q && uv pip install -q pillow && \
     uv run tools/make_tra.py tools/translation.tsv --out dist/chinese.tra --charset-out build/charset.txt && \
     uv run tools/build_cjk_font.py --size $SIZE --charset-file build/charset.txt --bin dist/cjkfont${SIZE}.bin --out build/cjk${SIZE}"

cp "$ROOT/README.md" "$OUT/README.md" 2>/dev/null || true
echo ">> 資產就緒:$OUT/chinese.tra, $OUT/cjkfont${SIZE}.bin"
ls -la "$OUT"
