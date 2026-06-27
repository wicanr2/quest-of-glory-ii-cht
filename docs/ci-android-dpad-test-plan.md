# 計畫:用 GitHub Actions Android 模擬器驗證 on-screen D-pad(不涉版權)

> 目標:在 CI 上自動確認 [`docs/android-dpad-virtual-mouse.md`](android-dpad-virtual-mouse.md)
> 裡那個「待驗證點」—— **ScummVM 的螢幕 D-pad 在 AGS 遊戲內(不只 launcher 選單)是否真的
> 移動滑鼠游標**。不必每次手動裝手機,也**完全不碰 QFG2 的版權遊戲資料**。
>
> 本文是設計計畫(素材選定 + workflow 草圖 + 判讀 + 風險),尚未實作成 `build.yml` 的 job。

## 為什麼不能直接用 QFG2,也不能用 ScummVM 官方 freeware

- **QFG2 遊戲資料是 AGDI 版權**,絕不上 CI/公開 repo(本專案鐵則)。
- ScummVM 官方提供 11 款可合法下載的 freeware,但**全都不是 AGS engine**
  (Beneath a Steel Sky、Drascula、Sfinx… 各是自己的 engine)。D-pad→游標雖是後端通用機制,
  但要驗證「**AGS context**」就得用真的跑在 **AGS engine** 上的遊戲。

→ 所以需要一款「**免費授權 + AGS engine + ScummVM 支援**」的第三方遊戲當測試素材。

## 選定素材:5 Days a Stranger

| 項目 | 內容 |
|---|---|
| 遊戲 | **5 Days a Stranger**(Ben "Yahtzee" Croshaw,Chzo Mythos 第一部,2003) |
| 引擎 | **AGS**(2003 AGS Awards 最佳遊戲;與 QFG2 同 engine) |
| 類型 | 2D point-and-click(正好需要滑鼠游標精準點擊 → 測 D-pad 推游標) |
| 授權 | **Freeware**(archive.org 標記;Curly's World of Freeware 捐贈) |
| 下載 | `https://archive.org/download/5_Days_a_Stranger/5days.zip`(**1.2 MB**,小、CI 抓很快) |
| ScummVM | AGS engine 支援(注意有版本變體;CI 用 `--add` 自動偵測,偵測不到就 fallback 直接指定路徑啟動) |

**備選**(同 Yahtzee、同 freeware、同 AGS,若 5 Days 偵測有問題可換):Chzo Mythos 後續
《7 Days a Skeptic》《Trilby's Notes》《6 Days a Sacrifice》。

> 為何不用 AGS 官方 demo/template:體積雖更小,但不一定有 ScummVM detection entry、也未必
> 進得到「有游標的遊戲畫面」。選一款**確定能跑、確定有 point-and-click 畫面**的 freeware 最可靠。

## Workflow 草圖(`build.yml` 新增 `android-dpad-test` job)

```yaml
android-dpad-test:
  runs-on: ubuntu-latest          # 需要 KVM 加速 emulator
  steps:
    - uses: actions/checkout@v4
    # 1) 取得引擎 APK:用本 repo CI 既有的 android job 產的純引擎 base APK(無遊戲)
    - 下載 base APK artifact(或在同 workflow 內 needs: android)
    # 2) 取免費 AGS 測試遊戲(不涉版權)
    - run: |
        wget -q https://archive.org/download/5_Days_a_Stranger/5days.zip
        unzip -q 5days.zip -d game5days       # AGS data:*.exe / acsetup.cfg / ac2game.dta / *.vox
    # 3) 開 Android 模擬器(headless + swiftshader,標準 action)
    - uses: reactivecircus/android-emulator-runner@v2
      with:
        api-level: 30
        arch: x86_64
        force-avd-creation: false
        emulator-options: -no-window -gpu swiftshader_indirect -noaudio -no-boot-anim
        script: bash tools/android_dpad_probe.sh   # 下面這支
```

`tools/android_dpad_probe.sh`(在模擬器內跑,全程 adb):

```bash
set -e
adb install -r base.apk                                   # 純引擎 APK
# 把測試遊戲推進 app 可讀路徑(sdcard),不進 APK、不碰版權
adb shell mkdir -p /sdcard/ags5days
adb push game5days/. /sdcard/ags5days/
# 預設觸控設定:開 on-screen control + 2D 遊戲用 Gamepad(D-pad)模式
#   onscreen_control=true / touch_mode_2d_games=2 / kbdmouse_speed=3
adb shell "run-as org.scummvm.scummvm sh -c 'cat >> files/.config/scummvm/scummvm.ini'" <<INI
[scummvm]
onscreen_control=true
touch_mode_2d_games=2
kbdmouse_speed=3
INI
# 啟動 ScummVM 直接跑這款遊戲(用 --path 指 sdcard 的遊戲;engineid 由 detection 決定)
adb shell am start -n org.scummvm.scummvm/.ScummVMActivity \
  --es "Args" "--path=/sdcard/ags5days --auto-detect"
sleep 25                                                  # 等載入到遊戲畫面
adb exec-out screencap -p > shot_00_start.png            # D-pad 應已顯示在左下
# 連續往同一方向推 D-pad,每步截圖 → 游標應一路移動
for i in 1 2 3 4 5; do
  adb shell input swipe 120 600 120 600 400              # 長按左下 D-pad 的「右」方向格
  adb exec-out screencap -p > shot_0${i}_dpad.png
done
# 點右下動作鈕 = 滑鼠點擊
adb shell input tap 1000 600
adb exec-out screencap -p > shot_06_click.png
```

最後 `actions/upload-artifact` 把 `shot_*.png` 收起來。

## 怎麼判讀「D-pad 有移游標」

- **第一版(最快、最可靠):存截圖 artifact 人工看一眼** — 比對 `shot_00`→`shot_05`,游標
  有沒有沿 D-pad 方向一路移動;`shot_06` 有沒有觸發點擊反應。先求「看得到真相」。
- **第二版(可選自動化):游標位移 diff** — 游標是畫面上少數會移動的小區塊,對相鄰截圖做
  影像差分、取質心位移,位移 > 閾值就算 PASS。等第一版確認手感與座標後再加,免得一開始就被
  影像判斷的雜訊卡住。

## 已知風險 / 要在實作時確認

1. **ScummVM Android 怎麼吃命令列遊戲路徑** — `am start ... --es Args` 的參數格式要對;若不行,
   改成先 `--add` 把遊戲加進 launcher,再用 launcher 點進去(多一步 adb input)。
2. **config 寫入路徑** — `scummvm.ini` 在 app 內部 `files/` 下,需 `run-as`(debug APK 可)。
   路徑依 ScummVM 版本可能不同,實作時先 `adb shell run-as ... ls` 確認。
3. **D-pad 座標** — `gamepad.svg` 在左下、按鈕在右下,實際像素要看模擬器解析度,第一版先粗抓、
   對著 `shot_00` 校正。
4. **detection 變體** — 5 Days 某些版本 ScummVM 不認(bug #12150)。若 `--auto-detect` 失敗,
   換備選遊戲、或直接指定 `--engine=ags`。
5. **emulator 啟動 ScummVM 的 OpenGL ES** — swiftshader 軟體渲染雖可跑,首畫面可能較慢,
   `sleep` 要給夠;必要時改 `-gpu swiftshader_indirect` 以外的選項。

## 實作踩雷記錄(CI 迭代)

第一版 probe 落地後在 CI 模擬器上反覆踩雷,每輪 ~25-30 分(android build + emulator),逐一收斂。
這也是上面 plan 風險 #1~#3 的實戰驗證:

| 輪 | 症狀 | 根因 | 修法 |
|---|---|---|---|
| 1 | step 3「首次啟動」`exit 252` 整支掛掉,沒有任何截圖 | `monkey -c LAUNCHER` 配寫死的 `PKG=org.scummvm.scummvm` 找不到 activity → monkey abort;又因 `set -e` 一非零就整支退出 | 改 `set +e` + 每步截圖 + `exit 0`,讓 probe 跑完、從 artifact 反推;啟動先改 `am start` |
| 2 | job 變 success 但 9 張截圖**全是 Android 桌面**、size 幾乎一樣(105823 bytes) | ScummVM 根本沒啟動 —— `am start -n $PKG/.SplashActivity` 仍失敗,log 同時報 `pm path` 找不到 package | 指向 package 名問題(見第 3 輪) |
| 3 | package 名修對後,launcher 截圖跳出「**ScummVM (debug) keeps stopping**」彈窗 | **根因**:`dists/android/build.gradle` 有 `applicationIdSuffix ".debug"`,真實 package 名是 **`org.scummvm.scummvm.debug`**;寫死 `org.scummvm.scummvm` 讓 `pm path`/`am start`/`monkey` 全找不到。修對後 ScummVM 被啟動了,卻一啟動就 crash(見第 4 輪) | install 後 `pm list packages \| grep scummvm` **動態抓**真名 |
| 4 | ScummVM 一啟動就 crash(keeps stopping) | **ABI 不匹配**:`android` job 只 build **arm64-v8a**(給手機),但 GitHub x86 runner 的模擬器是 **x86_64**;arm64 的 `libscummvm.so` 在 x86_64 模擬器載入失敗 → crash。`adb install` 不擋(照裝),要跑起來才爆 | **改用官方 ScummVM x86_64 APK**(D-pad 是上游引擎機制、與本專案 patch 無關,官方 APK 一樣有)。順帶解開「官方 release 不能 `run-as` 改 config」的死結:`onscreen_control` 預設就是 `true`(options.cpp:494),用右上角控制器圖示 tap 循環切 Gamepad 即可,不必寫 config |

**通用教訓(別的專案也適用)**:
- **APK ABI 要對上模擬器 arch** — 一顆 arm64 APK `adb install` 到 x86_64 模擬器**會裝、但一跑就 crash**(native lib 載入失敗)。GitHub x86 runner 跑 x86_64 模擬器最順,所以測試素材要嘛含 x86_64 ABI、要嘛另 build 一顆 x86_64。
- **package 名別寫死** — debug build 帶 `.debug` 後綴。`adb install` 回報成功 ≠ 你以為的 package id 存在;一律 `pm list packages \| grep <app>` 撈真名。
- **截圖 size 全部相同 = 畫面靜止** — headless 看不到螢幕時,這是「app 沒起來/卡死」最快的判讀訊號,比逐張開圖快。
- **probe 要 `set +e` + `exit 0`** — CI 探測腳本的目的是「跑完、把證據(截圖/log)全帶回來」,不是「第一個錯就停」。讓它跑到底,從 artifact 反推哪步壞。
- **`am start -n $PKG/.Activity` 的相對類名是陷阱** — 會用 package-id(帶 .debug)當前綴 → 類名錯;用 `monkey -p $PKG` 不指定 activity 最省事。

## 產出與下一步

- 本計畫先決定**素材(5 Days a Stranger,1.2 MB freeware AGS)**與 **workflow 形狀**。
- 下一步(待核可後實作):把 `android-dpad-test` job 與 `tools/android_dpad_probe.sh` 落到
  `.github/workflows/build.yml`,跑出第一批 `shot_*.png` artifact,人工確認 D-pad 在 AGS 遊戲內
  移游標 → 回填 [`android-dpad-virtual-mouse.md`](android-dpad-virtual-mouse.md) 的「待驗證點」。

## 參考

- [5 Days a Stranger — Internet Archive(freeware)](https://archive.org/details/5_Days_a_Stranger)
- [ScummVM AGS 相容性清單](https://www.scummvm.org/compatibility/2.7.0/ags:ags/)
- [`reactivecircus/android-emulator-runner`](https://github.com/ReactiveCircus/android-emulator-runner)
- 機制本體見姊妹文件 [`android-dpad-virtual-mouse.md`](android-dpad-virtual-mouse.md)
