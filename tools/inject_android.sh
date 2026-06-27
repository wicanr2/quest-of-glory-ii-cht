#!/usr/bin/env bash
# 把 QFG2 遊戲 + 繁中資產注入 CI 編的 base APK → 開箱即玩的繁中 Android APK,重簽名。
# 遊戲資料僅在本機注入(AGDI 版權,絕不上 CI/GitHub)。全程 Docker,host 乾淨。
# 個人典藏用途(你合法擁有的遊戲)—— 請勿散布。
#
# 用法:tools/inject_android.sh [base.apk]   (預設 out/apk/ScummVM-debug.apk)
#
# 工具鏈(JDK/build-tools/r26d libc++_shared.so/oboe liboboe.so)固化在
# docker/Dockerfile.android-inject。native libs 走 image、不經 mount,避開這台
# docker bind-mount「host 寫小檔→下個容器讀到舊快照」的雷;只有遊戲檔(讀)與
# 輸出 APK(寫)走 mount。
#
# 注入機制(ScummVM Android,缺一不可,沿用 rise-of-the-dragon 經驗):
#  1. 遊戲放 APK 內層 assets/assets/games/<id>(雙層)+ 登錄 assets/MD5SUMS
#     (路徑 assets/games/<id>/<f>)→ ScummVM 視 assets updated、解開內層樹並
#     mass-add 進 launcher;少任一步 launcher 就是空的。
#  2. base APK 缺 runtime libs:libscummvm.so→liboboe.so→libc++_shared.so → 補上,否則秒退。
#  3. 注入後刪舊簽名 META-INF/*、zipalign、debug key 重簽。
set -e
cd "$(dirname "$0")/.."
BASE="${1:-out/apk/ScummVM-debug.apk}"
GAMEID="qfg2agdi"
OUT="out/apk/qfg2-cht-android-FULL.apk"
IMAGE="qfg2-android-inject"
[ -f "$BASE" ] || { echo "找不到 base APK:$BASE(先跑 CI 的 android job 取得)"; exit 1; }
[ -d game ] || { echo "找不到 game/(原版遊戲資料)"; exit 1; }
[ -f game/chinese.tra ] || { echo "game/ 缺 chinese.tra(先跑 build_release_assets / dev-setup)"; exit 1; }

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "==> 首次:build 注入工具鏈 image($IMAGE,含 build-tools + r26d libc++_shared + oboe)"
  docker build -f docker/Dockerfile.android-inject -t "$IMAGE" docker/
fi

echo "==> 注入遊戲 + 繁中資產 + native libs,重簽名"
docker run --rm -v "$PWD":/work -w /work "$IMAGE" bash -c '
  set -e
  BT="$BUILD_TOOLS"
  GID="'"$GAMEID"'"
  rm -rf /tmp/stage
  # [雷1] 遊戲放雙層 assets/assets/games/<id>;排除執行不需的 PDF/url 省空間
  mkdir -p "/tmp/stage/assets/assets/games/$GID"
  cp -r game/. "/tmp/stage/assets/assets/games/$GID/"
  rm -f "/tmp/stage/assets/assets/games/$GID"/*.pdf "/tmp/stage/assets/assets/games/$GID"/*.url 2>/dev/null || true
  cp "'"$BASE"'" /tmp/work.apk

  # [雷2] base APK 已含與 libscummvm.so 同版本(CI 從 oboe git 源碼編)的 liboboe.so。
  # 絕不可用 image 內的 oboe 1.9.0 覆蓋它 —— ABI 不符會在 oboe::AudioStreamBase 複製
  # 建構子 crash(openStream 時 std::string layout 對不上 → operator new 爆量 → terminate)。
  # 只補 base APK 缺的 libc++_shared.so(r26d,與 CI 同 ABI;CI 的 arm64 job 沒帶它)。
  mkdir -p /tmp/stage/lib/arm64-v8a
  cp /opt/android_libs/libc++_shared.so /tmp/stage/lib/arm64-v8a/

  # [雷1] 遊戲檔登錄 MD5SUMS(相對 files/,即 assets/games/<id>/<f>)→ 觸發 re-extract + mass-add
  unzip -o -q /tmp/work.apk "assets/MD5SUMS" -d /tmp/md5
  ( cd /tmp/stage/assets && find assets/games -type f | sort | xargs md5sum ) >> /tmp/md5/assets/MD5SUMS
  cp /tmp/md5/assets/MD5SUMS /tmp/stage/assets/MD5SUMS

  # 注入 assets/ + lib/ + 更新 MD5SUMS,丟舊簽名
  ( cd /tmp/stage && zip -qr /tmp/work.apk assets lib )
  zip -q -d /tmp/work.apk "META-INF/*" >/dev/null 2>&1 || true

  # [雷3] zipalign + debug key 重簽
  "$BT/zipalign" -p -f 4 /tmp/work.apk /tmp/aligned.apk
  keytool -genkeypair -keystore /tmp/debug.ks -alias qfg2 -storepass android -keypass android \
    -dname "CN=QFG2-CHT" -keyalg RSA -keysize 2048 -validity 10000 >/dev/null 2>&1
  mkdir -p /work/out/apk
  "$BT/apksigner" sign --ks /tmp/debug.ks --ks-pass pass:android --key-pass pass:android \
    --out "/work/'"$OUT"'" /tmp/aligned.apk
  "$BT/apksigner" verify "/work/'"$OUT"'" && echo "SIGNED OK"
  # 印出注入的 native libs md5,供外部核對是否 r26d 版
  echo "lib md5:"; md5sum /tmp/stage/lib/arm64-v8a/*.so
  chmod a+rw "/work/'"$OUT"'"
'
echo "==> 完成:$OUT"
ls -la "$OUT" 2>/dev/null
echo "   安裝後:launcher 會自動出現遊戲;首次進 Game Options 選 Chinese translation 即中文。"
