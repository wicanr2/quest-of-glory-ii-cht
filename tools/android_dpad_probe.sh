#!/usr/bin/env bash
# 驗證 ScummVM 的螢幕 on-screen D-pad 是否真的移動滑鼠游標。
#
# 用官方 ScummVM x86_64 APK:D-pad→游標是 ScummVM **上游引擎機制**(不是本專案的 CJK patch),
# 用官方 APK 測一樣成立;而且本專案 CI 只 build arm64-v8a(給手機),arm64 的 libscummvm.so 在
# x86_64 模擬器載入失敗會 crash(踩過),官方 release 有 x86_64 ABI 才跑得起來。完全不涉版權。
#
# 策略:在 ScummVM **launcher**(GUI context,VirtualMouse 確定有效 — android.cpp:731)裡,
# onscreen_control 預設就是 true(options.cpp:494),用右上角控制器圖示循環 touch mode 到
# Gamepad(D-pad),推 D-pad 看游標移動。不需 run-as(官方 release 不可)、不需 Add Game。
# (進 AGS 遊戲內再驗一次是延伸 TODO,見 docs/ci-android-dpad-test-plan.md。)
#
# set +e + exit 0:CI 探測腳本目的是「跑完、把證據帶回來」,從 artifact 反推,不要中途就停。
set +e
APK="${APK:-base.apk}"
SHOT() { adb exec-out screencap -p > "$1" 2>/dev/null && echo "  → $1 ($(wc -c <"$1") bytes)"; }

echo "== 0) 裝官方 APK + 動態抓 package =="
adb wait-for-device
adb shell input keyevent 82 >/dev/null 2>&1
adb install -r -g "$APK" && echo "  APK 裝好" || echo "  !! 安裝失敗"
PKG=$(adb shell pm list packages 2>/dev/null | grep -i scummvm | sed 's/package://' | tr -d "\r" | head -1)
echo "  package = ${PKG:-<找不到!>}"

echo "== 1) 啟動 ScummVM launcher,等它起來(官方 x86_64 應該不再 crash) =="
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
sleep 28
SHOT shot_00_launcher.png
# 偵測 crash dialog(keeps stopping):有就關掉重試一次,並把畫面 dump 出來看
if adb shell uiautomator dump /sdcard/u.xml >/dev/null 2>&1; then
  if adb shell cat /sdcard/u.xml 2>/dev/null | grep -qi "stopping\|has stopped\|crash"; then
    echo "  !! 偵測到 crash dialog → 關閉重啟一次"
    adb shell input tap 160 380; sleep 2
    adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1; sleep 20
    SHOT shot_00b_relaunch.png
  else
    echo "  ✓ 無 crash dialog,ScummVM 應已起來"
  fi
fi

echo "== 2) onscreen_control 預設 true → 右上角有控制器圖示。tap 循環 touch mode 到 Gamepad =="
# 模擬器解析度約 320x640。控制器圖示在右上角;每 tap 循環一個 touch mode(menus 預設 mouse)。
for n in 1 2 3; do
  adb shell input tap 298 28; sleep 2
  SHOT shot_0${n}_touchmode.png
done

echo "== 3) Gamepad 模式應顯示左下 D-pad。推 D-pad「右」,每步截圖看 launcher 游標移動 =="
for i in 4 5 6 7; do
  adb shell input swipe 60 560 60 560 600    # 長按左下 D-pad 右方向格(座標粗抓,看截圖校正)
  SHOT shot_0${i}_dpad.png
done

echo "== 4) 右下動作鈕 = 點擊 =="
adb shell input tap 280 560; sleep 2
SHOT shot_08_click.png

echo "== done =="
ls -la shot_*.png 2>/dev/null || echo "  !! 沒有截圖"
exit 0
