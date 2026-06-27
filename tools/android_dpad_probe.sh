#!/usr/bin/env bash
# 驗證 ScummVM 的螢幕 on-screen D-pad 在 AGS 遊戲(2D context)內移動游標。
#
# 用本專案自己的 x86_64 debug APK(android-x86 job 產出):
#   - ABI 對上 GitHub Actions 的 x86_64 模擬器(踩雷第四輪:arm64 APK 在此 crash)
#   - debug build 可用 run-as 寫 scummvm.ini(官方 release 不行)
#
# 測試遊戲:《5 Days a Stranger》(Ben "Yahtzee" Croshaw, 2003)
#   - 免費 AGS freeware,與 QFG2 同引擎,完全不涉 QFG2 版權
#   - ScummVM gameid: 5daysastranger(detection_tables.h:482)
#
# 目標:進到 AGS 遊戲(2D context)後截到左下 D-pad 十字;launcher 不畫 D-pad 只有遊戲才畫。
#
# 五輪踩雷教訓:
#   set +e + exit 0 → 跑完把所有截圖帶回來,從 artifact 反推真相,不中途退出。
set +e

APK="${APK:-ScummVM-debug.apk}"
GAME_DIR="${GAME_DIR:-}"
SHOT() { adb exec-out screencap -p > "$1" 2>/dev/null && echo "  >> $1 ($(wc -c <"$1") bytes)"; }
LOG()  { echo "[$(date +%T)] $*"; }
# logcat 快照:把目前 ring buffer 存成 $1,過濾 crash/AndroidRuntime/DEBUG/ScummVM
LOGSNAP() {
  adb logcat -d -b crash,main -v time 2>/dev/null \
    | grep -E "AndroidRuntime|DEBUG|FATAL|ScummVM|Fatal|force finishing|Uncaught|JNI DETECTED|signal |Abort" \
    | tail -100 > "$1" 2>/dev/null
  echo "  >> $1 ($(wc -l <"$1") lines)"
}

LOG "== 0) 裝 debug APK + 動態抓 package =="
adb wait-for-device
adb shell input keyevent 82 >/dev/null 2>&1   # 解鎖螢幕
adb install -r -g "$APK" && LOG "  APK 裝好" || LOG "  !! 安裝失敗"
PKG=$(adb shell pm list packages 2>/dev/null | grep -i scummvm | sed 's/package://' | tr -d "\r" | head -1)
LOG "  package = ${PKG:-<找不到!>}"
# logcat 清空,讓後續快照只含本次執行的訊息
adb logcat -c 2>/dev/null; sleep 1
SHOT shot_00_installed.png

LOG "== 0b) 短暫首次啟動 → 讓 ScummVM 建立 files/ 目錄(run-as 需要此目錄存在) =="
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
sleep 12
LOGSNAP logcat_00b_first_launch.txt   # 診斷:首次啟動是否也 crash
adb shell am force-stop "$PKG" >/dev/null 2>&1
sleep 2

LOG "== 1) 推遊戲檔到 /sdcard/5days =="
adb shell mkdir -p /sdcard/5days
if [ -n "$GAME_DIR" ] && [ -d "$GAME_DIR" ]; then
  adb push "$GAME_DIR/." /sdcard/5days/ 2>&1 | tail -5
  LOG "  遊戲推完"
  adb shell ls /sdcard/5days/ | head -10
else
  LOG "  !! GAME_DIR='$GAME_DIR' 不存在或未設定 → 跳過 push(遊戲會缺 5days.exe)"
fi
SHOT shot_01_pushed.png

LOG "== 2) 用 run-as 寫 scummvm.ini(D-pad 模式 + 5daysastranger 遊戲條目) =="
# run-as 以 app 使用者身分執行,不需 adb root,debug APK 一定可用。
# 注意:ScummVM Android 的 ini 路徑是 files/scummvm.ini(不是 .config/scummvm/),
# 見 ScummVMActivity.java:1849。
cat > /tmp/scummvm_probe.ini << 'INIEOF'
[scummvm]
onscreen_control=true
touch_mode_2d_games=2
touch_mode_menus=1
kbdmouse_speed=3

[5daysastranger]
description=5 Days a Stranger
engineid=ags
gameid=5daysastranger
language=en
path=/sdcard/5days
INIEOF

adb shell "run-as $PKG sh -c 'cat > files/scummvm.ini'" < /tmp/scummvm_probe.ini \
  && LOG "  scummvm.ini 寫入完成" || LOG "  !! run-as 寫入失敗(嘗試繼續)"
# 確認寫入成功
adb shell "run-as $PKG sh -c 'cat files/scummvm.ini'" 2>/dev/null \
  && LOG "  ✓ 內容讀回成功" || LOG "  !! 讀回失敗"

LOG "== 3) am start 直接帶 --game=5daysastranger,繞過 launcher UI 選遊戲 =="
# 根因:過去 9 輪 tap/keyevent 選遊戲都失敗(tap 座標偏、TAB 開鍵盤、touch_mode 未對),
# 改用 am start 帶 --game 參數直接進遊戲,不走 launcher 互動。
#
# applicationIdSuffix '.debug' 只改 package id;Java class 仍是 org.scummvm.scummvm.*。
# ScummVMActivity.java: getIntent().getStringExtra("Args") → 當 argv 解析。
# step 0b 已做首次 monkey 啟動 → assets 已 copy 到 files/ → 這裡直接跑 ScummVMActivity。
SCUMMVM_ACT="org.scummvm.scummvm.ScummVMActivity"
AM_OUT=$(adb shell am start -n "${PKG}/${SCUMMVM_ACT}" \
  --es "Args" "--game=5daysastranger" 2>&1)
LOG "  am start result: ${AM_OUT}"
sleep 30   # AGS 首次載入較慢(解壓 + 可能有片頭)
SHOT shot_02_game.png
LOGSNAP logcat_03_game_start.txt

# crash 偵測
if adb shell uiautomator dump /sdcard/u.xml >/dev/null 2>&1; then
  if adb shell cat /sdcard/u.xml 2>/dev/null | grep -qi "stopping\|has stopped"; then
    LOG "  !! crash detected → 收 logcat"
    LOGSNAP logcat_03_crash.txt
    adb logcat -d -b crash,main -v time 2>/dev/null | tail -300 > logcat_03_full.txt || true
    adb shell input tap 160 380; sleep 2   # 關 crash dialog
  else
    LOG "  ✓ 無 crash dialog"
  fi
fi

# am start 失敗 fallback:若畫面仍在 launcher(或黑屏)則用 monkey + 直接 tap 選遊戲。
# touch_mode_menus=1(Direct Mouse)已寫進 ini → tap = 絕對座標點擊,應選中 5days。
if echo "$AM_OUT" | grep -qi "^Error\|error:"; then
  LOG "  !! am start 報錯 → monkey fallback"
  adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
  sleep 20
  SHOT shot_02b_launcher_fallback.png
  adb shell input tap 155 475; sleep 1     # 關說明框
  adb shell input keyevent 4 >/dev/null 2>&1; sleep 1
  # Direct Mouse(touch_mode_menus=1):tap 在 game list 第一個項目上 = 選中
  adb shell input tap 90 90; sleep 1      # y≈88 是 game list 第一行中心
  SHOT shot_02c_selected_fb.png
  adb shell input tap 265 587; sleep 3    # Start 鈕
  SHOT shot_02d_started_fb.png
fi

SHOT shot_03_after_launch.png

LOG "== 6) 等 AGS 遊戲載入 + 抓 logcat 看 5days 有沒有被載入(detection/start) =="
sleep 18
SHOT shot_07_ingame_wait.png
LOGSNAP logcat_07_start.txt
sleep 10
SHOT shot_08_ingame.png   # 目標:AGS 遊戲畫面 + 左下 D-pad 十字

LOG "== 7) 在 AGS 遊戲(2D context)內推 D-pad,截圖看游標是否移動 =="
# D-pad 位於左下角,右方向格約 x=60,y=560
for i in 9 10 11 12; do
  adb shell input swipe 60 560 60 560 600   # 長按右方向格
  sleep 1
  SHOT shot_0${i}_dpad.png
done

LOG "== 8) 右下動作鈕(=點擊)=="
adb shell input tap 280 560; sleep 2
SHOT shot_13_click.png
SHOT shot_14_final.png

LOG "== done =="
ls -la shot_*.png logcat*.txt 2>/dev/null || LOG "  !! 沒有截圖/logcat"
exit 0
