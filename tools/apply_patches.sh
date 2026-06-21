#!/usr/bin/env bash
# 取得 pinned 上游 ScummVM 並套上本專案的繁中化 patch。
# 用於本機與 GitHub Actions:確保所有平台 build 同一份原始碼。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-$ROOT/scummvm-src}"
UPSTREAM="$(cat "$ROOT/patches/UPSTREAM_COMMIT.txt")"

if [ ! -d "$SRC/.git" ]; then
	echo ">> clone ScummVM @ $UPSTREAM"
	# [HARD] core.autocrlf=false:Windows(MSYS2)預設 true 會把行尾轉 CRLF,
	# 導致 LF 的 patch 對不上(patch does not apply)。強制 LF 讓各平台一致。
	git clone --config core.autocrlf=false --config core.eol=lf https://github.com/scummvm/scummvm.git "$SRC"
fi
cd "$SRC"
git config core.autocrlf false
git config core.eol lf
git fetch --depth 1 origin "$UPSTREAM" 2>/dev/null || git fetch origin
git checkout -f "$UPSTREAM"
git clean -fdx >/dev/null 2>&1 || true

echo ">> 套用 patches/*.patch"
for p in "$ROOT"/patches/*.patch; do
	echo "   - $(basename "$p")"
	git apply --check --ignore-whitespace "$p"
	git apply --ignore-whitespace "$p"
done
echo ">> 完成。原始碼已就緒:$SRC"
