# Android 觸控:虛擬滑鼠與 on-screen D-pad

> 《英雄傳奇 II》是滑鼠驅動的 point-and-click 冒險遊戲。搬到手機上有個根本矛盾:
> **手指不是滑鼠**。遊戲內部是 320×200、放大到全螢幕後,手指直接戳很難精準點到小物件、
> 也難走到定點。本文整理 ScummVM 內建的解法 —— 用螢幕上的 D-pad 精確移動滑鼠游標 ——
> 的機制、設定,以及怎麼用 GitHub Actions 的 Android 模擬器自動驗證。

## 問題:手指 ≠ 滑鼠

滑鼠游標是「絕對位置 + 像素級精度」;手指是「一坨約 40px 寬的接觸面 + 會遮住目標」。
冒險遊戲常要點中幾個像素大的熱區(門把、地上的小物件)、或讓角色走到精確座標,手指直接戳
(absolute touch)既不準又擋視線。解法是把「移動游標」和「點擊」拆開:用一個**方向控制**慢慢
把游標推到定點,再用**獨立按鈕**點下去。這正是家用主機把 point-and-click 遊戲搬上手把時的
通用做法 —— 而 ScummVM 已經內建了。

## ScummVM 的三種觸控模式

ScummVM Android 對「ScummVM 選單 / 2D 遊戲 / 3D 遊戲」可各自設定觸控模式,三選一:

| 模式 | 行為 | 適合 |
|---|---|---|
| **Direct Mouse** | 手指戳哪、游標跳哪(絕對位置) | 選單;手指夠準時 |
| **Touchpad Emulation** | 手指相對拖動游標,像筆電觸控板(游標不跟著手指跳) | 需要精度、但不想要實體按鍵時 |
| **Gamepad Emulation** | 螢幕左下顯示 **D-pad**、右下顯示**動作按鈕**;不直接移游標,而是發虛擬手把事件 | 想要「D-pad 推游標 + 按鈕點擊」 |

> 預設值(`scummvm-src/backends/platform/android/options.cpp`):選單=Direct Mouse、
> 2D 遊戲=Touchpad、3D 遊戲=Gamepad。

## 關鍵:on-screen D-pad 怎麼變成滑鼠游標

「Gamepad 模式的 D-pad 不直接移游標」聽起來不就不能用?關鍵在 ScummVM 的 **VirtualMouse +
keymapper** 把這條路接了起來。整條鏈(行號為 ScummVM 上游 source):

1. **畫出控制器** — Gamepad 模式時,觸控層載入 `gamepad.svg`,在螢幕左下畫 D-pad、右下畫按鈕
   (`backends/platform/android/touchcontrols.cpp`)。
2. **D-pad 觸控 → 虛擬手把事件** — 按住 D-pad 的某個方向,送出 `EVENT_JOYBUTTON_DOWN` 帶
   `JOYSTICK_BUTTON_DPAD_UP/DOWN/LEFT/RIGHT`(`touchcontrols.cpp:403`)。
3. **DPAD → 移游標** — ScummVM 的 `VirtualMouse`(`backends/keymapper/virtual-mouse.cpp`)
   訂閱這些方向鍵,把它們轉成滑鼠游標位移。Android 後端預設就把 DPAD 綁到虛擬滑鼠:
   `android.cpp:731`「By default DPAD directions will be used for virtual mouse」,游標速度由
   `kbdmouse_speed` 控制(`android.cpp:358`,預設放慢成 2)。
4. **按鈕 → 點擊** — 右下動作按鈕透過 keymap 對應滑鼠左/右鍵。

→ 結果就是:**螢幕上一個 D-pad 把游標一格一格推到定點,再按鈕點下去**,正是手指戳不準的解法。

## 設定(config key)

這些是 `scummvm.ini` 的 key(在裝置上由 ScummVM 自己的 config 管理;`Options → Backend` 改了會寫回):

| key | 值 | 作用 |
|---|---|---|
| `onscreen_control` | `true` | 顯示螢幕虛擬控制器(D-pad/按鈕圖示) |
| `touch_mode_2d_games` | `2` | 2D 遊戲觸控模式 **0=Touchpad、1=Direct、2=Gamepad** |
| `touch_mode_menus` | `0`~`2` | 選單觸控模式 |
| `kbdmouse_speed` | `2`~`4` | DPAD/搖桿推游標的速度 |

> 列舉值定義在 `backends/platform/android/android.h`:`TOUCH_MODE_TOUCHPAD=0`、
> `TOUCH_MODE_MOUSE=1`、`TOUCH_MODE_GAMEPAD=2`。

## 在本專案啟用:三個層級

由淺到深,看需求選:

1. **玩家自己開(零工程)** — 進 ScummVM `Options → Backend`,勾「Show on-screen control」,
   把 2D 遊戲的 touch mode 選成 **Gamepad**。設一次永久生效。最省事,先用這個試手感。
2. **patch 成預設(中等)** — 改 ScummVM Android 後端的 `registerDefault`,讓 `onscreen_control`
   預設 `true`、`touch_mode_2d_games` 預設 Gamepad,玩家裝了就有。需重編 base APK 再重新注入
   遊戲(和「遊戲目錄有 chinese.tra 就自動套中文」那個 patch 一起做最划算)。
3. **完全客製外觀(大工程)** — 內建 `gamepad.svg` 的 D-pad 若不合用,才需自繪觸控覆蓋層、
   自己合成滑鼠事件。非必要不做。

## 用 GitHub Actions 自動驗證

可以用 **Android 模擬器**在 CI 上確認「on-screen D-pad 有顯示、且能推動游標」,不必每次手動裝手機:

- **模擬器**:[`reactivecircus/android-emulator-runner`](https://github.com/ReactiveCircus/android-emulator-runner)
  預設以 `-gpu swiftshader_indirect -no-window -noaudio` headless 跑,正好夠 ScummVM 的
  OpenGL ES 軟體渲染。
- **操作**:`adb install` 裝 APK → `adb shell input tap/swipe` 模擬觸控點 D-pad →
  `adb exec-out screencap -p` 截圖,比對游標前後位置。
- **版權**:本專案的遊戲資料(AGDI 版權)**不上 CI**。要驗證「遊戲內」D-pad,可改用一款
  **免費 AGS 遊戲**(AGS 官方 freeware,非版權)當測試素材 —— D-pad→游標是引擎層機制,與
  哪個 AGS 遊戲無關,用免費遊戲驗證即可。或退而求其次,只在 ScummVM launcher(GUI context)
  驗證 D-pad 移游標。

## 待驗證的一點

`android.cpp:731` 那句寫的是 DPAD 移游標「**in GUI context**」(ScummVM 自己的選單)。
進到 **AGS 遊戲內**,游標是否仍由 D-pad 驅動,取決於 AGS engine 有沒有攔截方向鍵、以及 global
keymap 的 fallback。**這需要實機(或上述 CI 模擬器)確認**;若遊戲內 D-pad 沒接到 VirtualMouse,
方案 2 的 patch 要再加一條「AGS context 綁定 DPAD→VMOUSE」的 keymap。

> CI 驗證進度:已在 ScummVM **launcher(menu context)** 實證「touch mode 切 Gamepad + VirtualMouse 游標
> 被觸控移動」(有截圖);但 launcher 不畫左下 D-pad 十字視覺,**進 AGS 遊戲內推 visual D-pad 仍待驗**。
> 五輪迭代根因、三張證據圖與已實證範圍見成果記錄 [`android-dpad-outcome.md`](android-dpad-outcome.md)。

## 參考

- [ScummVM Android 文件 — 觸控控制](https://docs.scummvm.org/en/v2.6.1/other_platforms/android.html)
- [ScummVM 控制設定 — `kbdmouse_speed`](https://docs.scummvm.org/en/v2.6.1/settings/control.html)
- [ScummVM Wiki — User Manual: Controls](https://wiki.scummvm.org/index.php/User_Manual/Appendix:_Controls)
- ScummVM 上游 source:`backends/keymapper/virtual-mouse.cpp`、
  `backends/platform/android/{android.cpp,touchcontrols.cpp,options.cpp}`
- [`reactivecircus/android-emulator-runner`](https://github.com/ReactiveCircus/android-emulator-runner)(CI 模擬器)
