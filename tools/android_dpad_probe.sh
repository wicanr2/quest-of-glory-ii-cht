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

LOG "== 3) 啟動 ScummVM(game list 應有 5 Days a Stranger) =="
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
sleep 25
SHOT shot_02_launcher.png

# 偵測 crash dialog + 收集 logcat crash 原因
if adb shell uiautomator dump /sdcard/u.xml >/dev/null 2>&1; then
  if adb shell cat /sdcard/u.xml 2>/dev/null | grep -qi "stopping\|has stopped\|crash"; then
    LOG "  !! 偵測到 crash dialog → 收集 logcat 再關閉後重啟"
    # [診斷] crash 時立即抓 logcat:AndroidRuntime(Java 異常)+ DEBUG(native tombstone)
    LOGSNAP logcat_02_crash.txt
    LOG "  logcat_02_crash.txt: $(wc -l < logcat_02_crash.txt 2>/dev/null) lines"
    # 也存完整 logcat 讓事後細查(含 dlopen/linker 錯誤)
    adb logcat -d -b crash,main -v time 2>/dev/null | tail -300 > logcat_02_full.txt || true
    adb shell input tap 160 380; sleep 2
    adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    sleep 20
    SHOT shot_02b_relaunch.png
  else
    LOG "  ✓ 無 crash dialog"
  fi
fi

LOG "== 3b) 關掉首次啟動說明框 + 可能的權限框 =="
# shot_02_launcher 已知 OK 鈕在 y≈475,x≈155(上幾輪校準過)
adb shell input tap 155 475; sleep 1
adb shell input keyevent 4 >/dev/null 2>&1; sleep 1
SHOT shot_03_dismissed.png

LOG "== 4) 確認 touch mode(launcher 自身是 menu context,點圖示確認狀態) =="
# 控制器圖示在右上角 (298,28);5days 在 game list 所以 Gamepad 模式應已就位
SHOT shot_04_pre_game.png

LOG "== 5) 點選 game list 中的 5 Days a Stranger(第一個條目) =="
# ScummVM launcher 320x640:game list 在 y≈100-540 的米色區;
# 第一個遊戲條目約在 y=115。點選後遊戲反白。
adb shell input tap 160 115; sleep 2
SHOT shot_05_selected.png

LOG "== 5b) 點 Start 鈕(右下角,y≈587) =="
adb shell input tap 265 587; sleep 3
SHOT shot_06_starting.png

LOG "== 6) 等 AGS 遊戲載入(首次可能需 20-30 秒) =="
sleep 20
SHOT shot_07_ingame_wait.png
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
