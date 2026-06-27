# 手機上怎麼操作 QFG2 —— ScummVM Android 觸控與移植經驗

這款是 1990 年代的滑鼠驅動冒險遊戲,搬到沒有實體滑鼠鍵盤的手機上,有幾個不直覺、
卻能讓操作從「很難用」變「順手」的關鍵。這篇把實機(Galaxy S23 Ultra / Android 16)
一路踩過的整理成可照做的步驟,後半段則是給開發者的移植踩雷記錄。

---

## 一、最重要的一招:左鍵/右鍵/中鍵 = 點按住的「時間長短」

ScummVM Android 沒有可見的左右鍵按鈕。**一根手指點下去、按住多久再放開,決定送出哪個滑鼠鍵**
(原始碼 `backends/platform/android/events.cpp` 的 `JE_TAP`,門檻 500ms / 1500ms):

| 你要的動作 | 怎麼點 | 實際送出 |
|---|---|---|
| **左鍵**(選項、走路、互動) | 快點一下就放(< 0.5 秒) | LMB |
| **右鍵**(QFG 用來「看」/切換動作游標) | 按住約 **0.5~1.5 秒**再放開 | RMB |
| **中鍵** | 按住 **> 1.5 秒**再放開 | MMB |
| **拖曳**(拖物品/捲動) | **雙擊**,第二下不放、直接移動手指 | 按住左鍵拖曳 |

> 這就是為什麼一開始會覺得「很難點」—— 手指按太久,左鍵就被判成右鍵了。
> 訣竅:要左鍵就「輕快地點」,別停留。要右鍵就「按著數半秒再放」。

---

## 二、觸控模式:點擊類遊戲選「Direct Mouse」

ScummVM 有三種觸控模式(`android.h`:`TOUCH_MODE_*`):

| 值 | 模式 | 行為 | 適合 |
|---|---|---|---|
| 0 | Touchpad | 手指相對移動游標(像筆電觸控板) | 預設,但對點擊類不直覺 |
| **1** | **Direct Mouse** | **點哪游標跳哪 + 點擊** | ✅ **QFG2 這類點擊冒險最順** |
| 2 | Gamepad | 螢幕 D-pad 推游標 + 動作鈕 | 鍵盤操作的遊戲;點擊類反而慢 |

**切換方式**:畫面右上角的「手勢圖示」可循環切換;或直接寫 `scummvm.ini`(見下)。
實測對 QFG2:`Direct Mouse` 點哪到哪,搭配上面的「按住時長 = 鍵」最好用。

> 注意:`Gamepad` 模式雖然名義上有 D-pad,但在這款的遊戲場景沒有穩定畫出左下方向十字,
> 容易變成「游標卡中央、點不動」。所以點擊類冒險建議用 `Direct Mouse`,別用 Gamepad。

---

## 三、推薦 `scummvm.ini` 設定(一次設好不用每次調)

```ini
[scummvm]
onscreen_control=true
touch_mode_2d_games=1   ; Direct Mouse:遊戲場景點哪到哪
touch_mode_menus=1      ; 選單也用 Direct Mouse
touch_mode_3d_games=1
```

debug 版 APK 可用 `adb shell run-as <pkg> sh -c 'cat > files/scummvm.ini'` 寫入;
一般玩家從遊戲內右上角選單調整即可。

---

## 四、實機測試狀態(Galaxy S23 Ultra / Android 16 / SDK 36)

### ✅ 已修(實機驗證)
- **遊戲跑起來**:AGS 引擎編入(libmad,見下節)。
- **片頭動畫**:`AGDI.001` 是 MPEG-1 system stream,補 libmpeg2(USE_MPEG2,CPU 軟解)後播放正常。
  AGS 走「先試 AVI(RIFF 失敗)→ fallback MPEGPSDecoder」,故 log 仍有一行 `Failed to find RIFF header`
  屬正常,MPEG 接手即播。
- **自動進遊戲**:patch 0003 改 `ScummVMActivity.java`,launcher 圖示啟動(無 intent data)時
  args 預設帶 `qfg2agdi` → 直接進遊戲、不停在 ScummVM 列表。

### ⚠️ 待解問題(2026-06-27 實機發現,優先序由高到低)

#### 4.1【高】16 KB ELF 對齊警告(Android 15+/16)
Android 16(SDK 36)要求 native lib 的 LOAD 段對齊 16 KB。debuggable APK 一啟動就跳警告對話框,
**出現很多次、很擾人**,且會擋住畫面讓人誤以為沒進遊戲。
- 實測:`libscummvm.so`、`liboboe.so` 已是 **16 KB 對齊**(`readelf -l` 顯示 LOAD align `0x4000`=2¹⁴);
  **未對齊的是 `libc++_shared.so`**(來自 NDK r26d,4 KB 對齊)。
- **修法**:NDK 升級到 **r27+**(預設 16 KB page size,連 `libc++_shared.so` 都是對齊版);
  或單獨對齊 `libc++_shared.so`。我們自編的 .so 也應加 linker flag `-Wl,-z,max-page-size=16384` 保險。
- 註:release(非 debuggable)APK 不會跳此對話框,但仍應修以符合 Android 16 規範。

#### 4.2【高】遊戲預設英文(沒套中文)
FULL apk 解壓後 `scummvm.ini` 的 `[qfg2agdi]` 是 `language=en`,**沒有 `translation=chinese`**
(Windows/macOS 包的 scummvm.ini 都有預設)。所以進遊戲是英文。
- **暫解**:進遊戲後 Game Options 手動選 Chinese translation。
- **修法**:`inject_android.sh` 預植 `scummvm.ini`(或在 mass-add 後設 `translation=chinese`),開箱即中文。

#### 4.3【中】沒有背景音樂
QFG2 的 `music.vox`(30 MB)內含 **OGG Vorbis** 音樂(7000+ 個 `OggS`),但 Android build 的
features 是「MP3 RGB zLib MPEG2…」**沒有 Vorbis** → OGG 音樂播不出。
- **修法**:比照 libmad / libmpeg2,把 **libvorbis + libogg** cross-build 進 NDK sysroot,啟用 Vorbis 解碼。

#### 4.4【中】系統鍵盤待實機驗證
patch 0003 已加「每幀偵測可見 GUITextBox → 開/關 `kFeatureVirtualKeyboard`」(game_run.cpp,已編入)。
但這次測試被 16 KB 對話框 + 英文介面卡住,**還沒實際走到建角色姓名輸入確認系統鍵盤會跳**。下次優先驗。
- 機制背景:AGS 原生不呼叫 `kFeatureVirtualKeyboard`,故手機上文字輸入框預設叫不出鍵盤(patch 0003 就是補這個)。

---

## 五、移植工程經驗:為什麼 Android 版一路踩雷

把這款搬上各平台時,踩到一連串**「解碼/音訊依賴沒進 build,導致功能默默消失」**的雷,
根因同一類。記下來給之後的 retro 移植參考。

### 5.1【最致命】AGS 引擎缺 libmad → 整個引擎沒被編入
AGS engine 把 **libmad(MP3 解碼)列為必要依賴**(`engines/ags/configure.engine` 第 6 欄 `"16bit mad"`)。
build 環境缺 libmad 時,configure 印 `Disabling engine AGS because dependencies unmet: MAD`
**卻仍以退出碼 0 結束** → 只編 `engines/ags/detection.o`、引擎本體 0 個 .o →
遊戲認得出(進得了 list)卻跑不起來:`Could not find suitable engine plugin`。
- **影響**:Windows 本地 cross、macOS、Android 全中招(各自缺 libmad)。
- **也是** headless 模擬器測 D-pad 卡 13 輪進不了遊戲的真根因 —— 不是 Intent 格式,是引擎沒進 APK。
- **修法**:各平台用對應工具鏈把 libmad 0.15.1b cross-build 進 sysroot(NDK / mingw / brew 替代)。
  libmad 老 configure 兩雷:gcc 專屬最佳化 flag(clang/NDK 不認)要 sed 清光、舊 config.sub 不認新 triple 要換。

### 5.2 configure 參數順序:`--disable-all-engines` 必須在 `--enable-engine=ags` 之前
configure 逐一處理參數、後者覆蓋。`--enable-engine=ags --disable-all-engines`(順序反)
會把剛 enable 的 ags 又一起關掉 → `Engines Skipped: Adventure Game Studio`、只剩 detection。
正解:`--disable-all-engines --enable-engine=ags`。

### 5.3 oboe ABI 不符 → 注入遊戲時別覆蓋 base APK 的 liboboe.so
ScummVM Android 用 Google oboe 做音訊。CI 從 **oboe git 源碼**編 `liboboe.so`,並用同版 header 編 `libscummvm.so`。
若打包工具用**另一版 oboe(如 1.9.0 aar)覆蓋**它,`libscummvm.so`(新版 ABI)呼叫舊 `liboboe.so` →
在 `oboe::AudioStreamBase` 複製建構子 crash(`openStream` 時 std::string layout 對不上 → `operator new`
爆量 → 未捕捉例外 → terminate),**一開機初始化音訊就秒退**。
正解:注入只補 base APK 缺的 `libc++_shared.so`(同 NDK 版),**保留 base 自帶的 liboboe.so**,絕不覆蓋。

### 5.4 片頭 MPEG 影片:同 5.1 的解碼依賴缺失(見 4.2)

### 5.5 驗證方法(撞牆時先驗「東西到底建進去了沒」)
- `scummvm(.exe) --list-engines` → ags 在不在(空 = 引擎沒編入)
- build log:`find engines/ags -name '*.o' ! -name detection.o | wc -l`(0 = 只有 detection)
- configure log:`Checking for MAD... yes/no`、`Disabling engine.*MAD`
- 真機 crash:`adb logcat -b crash` 看 backtrace 落在哪個 .so 的哪個函式(audio/engine/extraction)
- 檔案完整性:本地 vs 裝置解壓後 `stat -c%s` + header 比對(排除「不是 build 問題、是檔案壞」)

> 第一性原理:這一整串雷的共通教訓 —— build「成功」(退出碼 0)不代表功能進去了。
> 解碼/引擎依賴常以 warning 默默剔除。撞牆時先驗證「目標到底建進產物沒」,別預設機制對只調參數。
