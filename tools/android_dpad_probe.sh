#!/usr/bin/env bash
# 在 reactivecircus/android-emulator-runner 的 script context 跑(host 端 adb 對 emulator)。
# 目的:驗證 ScummVM 的螢幕 on-screen D-pad 在 AGS 遊戲內是否真的移動滑鼠游標。
# 測試素材是免費的《5 Days a Stranger》(AGS engine, freeware),**完全不涉及 QFG2 版權**。
#
# 設計見 docs/ci-android-dpad-test-plan.md、機制見 docs/android-dpad-virtual-mouse.md。
# ScummVM Android 沒有 intent 命令列參數接口,走:config 預加 game target → 啟動進 launcher
# → adb input 點進遊戲 → 推 D-pad + 連續 screencap,最後人工/自動看游標有沒有動。
#
# 刻意 NOT set -e:第一版座標/路徑都還在校正,寧可每步都截圖跑完、從截圖看真相,
# 也不要中途某個 adb 非零退出就整支掛掉(上一輪就是 monkey 啟動失敗 exit 252 卡死)。
set +e
GAME_DIR="${GAME_DIR:-game5days}"
APK="${APK:-base.apk}"
SHOT() { adb exec-out screencap -p > "$1" 2>/dev/null && echo "  screencap → $1 ($(wc -c <"$1" 2>/dev/null) bytes)"; }
# PKG 在 step 0 動態抓到後才定義內容;monkey -p $PKG 用 package 的 LAUNCHER intent 啟動,
# 不必知道 activity 完整類名(debug 的 package id 帶 .debug,但 activity 類名沒帶,寫死會錯)。
START() { adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1; }

echo "== 0) 等開機完成 + 裝 APK =="
adb wait-for-device
adb shell input keyevent 82 >/dev/null 2>&1   # 解鎖
adb install -r -g "$APK" && echo "  APK 裝好" || echo "  !! APK 安裝失敗"
# [關鍵] CI 是 debug build,build.gradle 有 applicationIdSuffix ".debug",真實 package 名是
# org.scummvm.scummvm.debug。寫死 org.scummvm.scummvm 會全找不到 → 動態抓。
PKG=$(adb shell pm list packages 2>/dev/null | grep -i scummvm | sed 's/package://' | tr -d "\r" | head -1)
echo "  package = ${PKG:-<找不到 scummvm package!>}"
adb shell pm path "$PKG" >/dev/null 2>&1 && echo "  pm path OK" || echo "  !! pm path 找不到"

echo "== 1) 推免費 AGS 測試遊戲到 sdcard(不涉版權)=="
adb shell rm -rf /sdcard/ags5days; adb shell mkdir -p /sdcard/ags5days
adb push "$GAME_DIR"/. /sdcard/ags5days/ >/dev/null && echo "  遊戲推好" || echo "  !! push 失敗"
adb shell ls /sdcard/ags5days

echo "== 2) 首次啟動 ScummVM(解壓 assets + 建 config),等久一點再關 =="
START; sleep 30
SHOT shot_00_firstboot.png
adb shell am force-stop $PKG; sleep 3

echo "== 3) 找 scummvm.ini(debug APK 可 run-as) =="
CFG=$(adb shell run-as $PKG sh -c '
  for p in files/.config/scummvm/scummvm.ini files/.local/share/scummvm/scummvm.ini files/scummvm.ini .config/scummvm/scummvm.ini; do
    [ -f "$p" ] && { echo "$p"; break; }
  done' 2>/dev/null | tr -d "\r")
echo "  config = ${CFG:-<找不到,列出 files/ 看看>}"
[ -z "$CFG" ] && adb shell run-as $PKG sh -c 'find files -name "*.ini" 2>/dev/null; ls -R files 2>/dev/null | head -40'

echo "== 4) 寫入:開 on-screen D-pad(Gamepad)+ 預加 5 Days 為 game target =="
if [ -n "$CFG" ]; then
  adb shell run-as $PKG sh -c "cat >> '$CFG'" <<'INI'

onscreen_control=true
touch_mode_menus=2
touch_mode_2d_games=2
kbdmouse_speed=3

[5daysastranger]
engineid=ags
gameid=5daysastranger
description=5 Days a Stranger (AGS D-pad test)
path=/sdcard/ags5days
INI
  echo "  寫入完成"; adb shell run-as $PKG sh -c "tail -20 '$CFG'"
else
  echo "  !! 沒找到 config,跳過(截圖仍會抓 launcher 狀態)"
fi

echo "== 5) 重啟 → launcher(應顯示 D-pad + 遊戲列表)=="
START; sleep 20
SHOT shot_01_launcher.png

echo "== 6) 進遊戲:點列表第一列 + 可能的 Start 鈕(座標粗抓,看截圖校正)=="
adb shell input tap 360 240; sleep 1; SHOT shot_02_tap1.png
adb shell input tap 360 240; sleep 1
adb shell input tap 620 1180; sleep 2          # 底部可能的 Start 鈕
sleep 22
SHOT shot_03_ingame.png

echo "== 7) 推 D-pad「右」方向,每步截圖 → 游標應沿方向移動 =="
for i in 4 5 6 7; do
  adb shell input swipe 230 1700 230 1700 500   # 長按左下 D-pad 右方向格
  SHOT shot_0${i}_dpad.png
done

echo "== 8) 右下動作鈕 = 滑鼠點擊 =="
adb shell input tap 980 1700; sleep 2
SHOT shot_08_click.png

echo "== done =="
ls -la shot_*.png 2>/dev/null || echo "  !! 完全沒有截圖"
exit 0
