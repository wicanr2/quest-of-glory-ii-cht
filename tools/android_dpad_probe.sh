#!/usr/bin/env bash
# 在 reactivecircus/android-emulator-runner 的 script context 跑(host 端 adb 對 emulator)。
# 目的:驗證 ScummVM 的螢幕 on-screen D-pad 在 AGS 遊戲內是否真的移動滑鼠游標。
# 測試素材是免費的《5 Days a Stranger》(AGS engine, freeware),**完全不涉及 QFG2 版權**。
#
# ScummVM Android 沒有 intent 命令列參數接口,所以走:config 預加 game target → 啟動進
# launcher → adb input 點進遊戲 → 推 D-pad + 連續 screencap,最後人工/自動看游標有沒有動。
#
# 第一版:座標(D-pad/按鈕/launcher entry)先粗抓,跑出 shot_*.png 後對著截圖校正再迭代。
set -e
PKG=org.scummvm.scummvm
GAME_DIR="${GAME_DIR:-game5days}"          # workflow 解壓 5days.zip 後偵測到的遊戲根目錄
APK="${APK:-base.apk}"
SHOT() { adb exec-out screencap -p > "$1" 2>/dev/null || true; echo "  screencap → $1"; }

echo "== 1) 裝 ScummVM 純引擎 APK =="
adb install -r -g "$APK"

echo "== 2) 推免費 AGS 測試遊戲到 sdcard(不進 APK、不涉版權)=="
adb shell rm -rf /sdcard/ags5days
adb shell mkdir -p /sdcard/ags5days
adb push "$GAME_DIR"/. /sdcard/ags5days/ >/dev/null
adb shell ls /sdcard/ags5days | head

echo "== 3) 首次啟動讓 ScummVM 解壓 assets + 建 config,再關掉 =="
adb shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
sleep 25
adb shell am force-stop $PKG; sleep 2

echo "== 4) 找 scummvm.ini(debug APK 可 run-as 讀寫)=="
CFG=$(adb shell run-as $PKG sh -c '
  for p in files/.config/scummvm/scummvm.ini files/.local/share/scummvm/scummvm.ini files/scummvm.ini; do
    [ -f "$p" ] && { echo "$p"; break; }
  done' | tr -d '\r')
echo "  config = ${CFG:-<找不到>}"

echo "== 5) 寫入:開 on-screen D-pad(Gamepad 模式)+ 預加 5 Days 為 game target =="
# touch_mode_2d_games=2 → Gamepad(螢幕 D-pad);onscreen_control=true → 顯示控制器
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

echo "== 6) 重啟 → launcher(應顯示 D-pad + 遊戲列表)=="
adb shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
sleep 18
SHOT shot_00_launcher.png

echo "== 7) 進遊戲:點列表第一個遊戲再點 Start(座標粗抓,看 shot_00 校正)=="
adb shell input tap 360 240; sleep 1          # 選遊戲列第一列
adb shell input tap 360 240; sleep 1          # 雙擊/或之後按 Start
SHOT shot_01_selected.png
adb shell input tap 620 1180; sleep 2         # 可能的 Start 鈕(底部),粗抓
sleep 22
SHOT shot_02_ingame.png

echo "== 8) 推 D-pad「右」方向,每步截圖 → 游標應沿方向移動 =="
# gamepad.svg:D-pad 在左下、動作鈕在右下。座標依模擬器解析度,第一版粗抓。
for i in 3 4 5 6; do
  adb shell input swipe 230 1700 230 1700 500    # 長按左下 D-pad 的右方向格
  SHOT shot_0${i}_dpad.png
done

echo "== 9) 右下動作鈕 = 滑鼠點擊 =="
adb shell input tap 980 1700; sleep 2
SHOT shot_07_click.png

echo "== done:shot_*.png 已產出,交給 artifact 上傳 =="
ls -la shot_*.png 2>/dev/null || echo "  !! 沒有截圖,檢查上面各步"
