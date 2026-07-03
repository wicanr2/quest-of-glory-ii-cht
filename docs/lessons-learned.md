# 跨平台移植踩雷總集 — Lessons Learned

英雄傳奇 II 繁中化橫跨 Windows / macOS / Android / Linux 四個平台，全部走 ScummVM 的 AGS 引擎自編。
一路踩下來，幾乎每一個雷的根因都指向同一件事：**build 成功（退出碼 0）不代表功能真的在產物裡**。
configure 遇到缺依賴的 codec 或 engine，多半是印一行 warning 就默默剔除，整個流程仍以 0 收尾——
表面上「build 過了」，但引擎、解碼器、音訊後端可能整組不在最終產物內。這篇把撞到的雷連同症狀、
根因、修法整理下來，核心心法只有一句：**撞牆時第一件事是驗證「目標到底建進產物沒」，不是預設它在、只調參數。**

---

## 教訓 1 — AGS 引擎缺 libmad，整個引擎沒編入（最致命）

| | 內容 |
|---|---|
| **根因** | AGS engine 把 libmad（MP3 解碼）列為必要依賴（`engines/ags/configure.engine`）。build 環境缺 libmad 時，configure 印 `Disabling engine Adventure Game Studio because dependencies unmet: MAD`，**卻仍以退出碼 0 結束**——只編出 `engines/ags/detection.o`，引擎本體 0 個 `.o`。 |
| **症狀** | 遊戲認得出（`--list-targets` 有 `qfg2agdi`）但一跑就「Could not find suitable engine plugin」；`--list-engines` 是空的。 |
| **中招平台** | Windows 本地 cross、macOS、Android，各自缺 libmad。也是 Android headless D-pad 自動化測試卡 13 輪進不了遊戲的真根因——不是 `am start` 的 Intent 格式問題，是引擎壓根沒進 APK。 |
| **修法** | 各平台把 libmad 0.15.1b cross-build 進對應 sysroot；移除所有 `--disable-mad`。 |

---

## 教訓 2 — configure 參數順序：`--disable-all-engines` 要放前面

configure 逐一處理參數、後面的覆蓋前面的。`--enable-engine=ags --disable-all-engines`（順序反了）
會把剛 enable 的 ags 又一起關掉，log 印出 `Engines Skipped: Adventure Game Studio`，只剩 detection。

正解：**`--disable-all-engines` 放在 `--enable-engine=ags` 之前。**

---

## 教訓 3 — libmpeg2 的 x86 組語在 mingw x64 crash（issue #3）

| | 內容 |
|---|---|
| **根因** | 片頭 `AGDI.001` 是 MPEG-1 system stream，ScummVM 的 `MPEGPSDecoder` 用 libmpeg2 解碼。libmpeg2 0.5.1 在 x86_64 上仍套用 32-bit x86 MMX 內嵌組語（`config.h` 的 `#define ARCH_X86`）。那段 asm 是為 Linux System V ABI 寫的，跟 mingw / Windows x64 的暫存器慣例不合。 |
| **症狀** | `mpeg2_init()` 正常、序列頭解析也正常，但一解 slice（真正的影格資料）就 crash。ScummVM 把 `Could not initialize libmpeg2` 當致命錯誤，直接 `error()` 結束程式——對回報者來說就是「版權宣告畫面後程式自動結束」。 |
| **關鍵** | macOS / Android 是 arm64、不是 x86，同一段 asm 不會被套用，所以只有 Windows 中這個雷。 |
| **修法** | configure 之後 `sed` 停用 `config.h` 的 `ARCH_X86` 與 `ACCEL_DETECT`，改走純 C 路徑。實測 `accel=0`、成功 DECODED 51 frames。 |

---

## 教訓 4 — oboe ABI 不符：注入遊戲時別覆蓋 base APK 的 liboboe.so

| | 內容 |
|---|---|
| **根因** | CI 從 oboe git 源碼編 `liboboe.so`，並用同一版 header 編 `libscummvm.so`，兩者自洽。本地「注入遊戲檔」的工具卻用另一版 oboe（1.9.0 aar）覆蓋掉 base APK 的 `liboboe.so`，於是新 ABI 的 `libscummvm.so` 呼叫舊 ABI 的 `liboboe.so`。 |
| **症狀** | `oboe::AudioStreamBase` 複製建構子 crash（`openStream` 時 `std::string` layout 對不上 → `operator new` 爆量 → 未捕捉例外 → terminate）。一開機初始化音訊就秒退。 |
| **修法** | 注入只補 base APK 缺的 `libc++_shared.so`（同 NDK 版），**絕不覆蓋 base 的 `liboboe.so`**。 |

---

## 教訓 5 — C++ hex escape 貪婪解析，吃掉後面的數字

| | 內容 |
|---|---|
| **根因** | 字串 `"\xE7\xB9\x81\xE4\xB8\xAD16"` 裡，`\xAD` 後面緊接著 `16`，而 `1`、`6` 剛好都是合法 hex 數字 → C++ 把 `\xAD16` 當成同一個 hex escape（`0xAD16`，超出 `char` 範圍）。 |
| **症狀** | clang 直接編譯失敗；gcc 靜默截斷成 `0x16`，讓「中」字的第三個 byte 壞掉。連 Windows（gcc）都默默中了，只是先前引擎根本沒編入所以沒浮現——補上 libmad 之後，換 macOS（clang）先編到這個檔案才爆出來。 |
| **修法** | 用相鄰字串字面值把 escape 序列截斷：`"...\xAD" "16"`。 |

---

## 教訓 6 — 16 KB ELF 對齊（Android 15+/16）

| | 內容 |
|---|---|
| **根因** | Android 16（SDK 36）要求 native lib 的 LOAD 段對齊 16 KB。`libscummvm.so`、`liboboe.so` 已是 16 KB 對齊，但 `libc++_shared.so`（來自 NDK r26d）是 4 KB 對齊。 |
| **症狀** | debuggable APK 一啟動就跳「不支援 16KB / ELF 對齊檢查失敗」警告對話框，出現很多次、擋住畫面，容易誤以為遊戲沒進去。 |
| **修法** | NDK 升級到 r27+（預設 16 KB page size，連 `libc++_shared.so` 都是對齊版）；自編的 `.so` 也可加 `-Wl,-z,max-page-size=16384` 保險。 |

---

## 驗證方法論

「東西到底建進去了沒」有三招可以直接驗，不用猜：

1. **`scummvm --list-engines`**：看目標引擎在不在，空的就是沒編入。
2. **數 build 產物**：`find engines/xxx -name '*.o' ! -name detection.o | wc -l`，0 代表只有 detection、引擎本體沒編。
3. **最小測試程式**：懷疑哪個元件就把它單獨隔離出來餵資料驗，例如寫一支 40 行的 C 程式呼叫 `mpeg2_init()` 直接餵 `AGDI.001`，看 `accel` 值與解出幾個影格——比在整個 ScummVM 裡摸黑猜快很多。

**wine 不可靠**：wine 的 OpenGL / graphics 會卡在「Starting game」——卡在片頭影片播放*之前*，測不到真正 Windows 才會發生的解碼 crash。可疑元件要單獨拆出來測（教訓 3 的 mp2test 直接測 mingw 版 libmpeg2，才抓到 slice 解碼 crash）。

**環境假設要實測，別腦補**：本專案有一次把「檔案還是舊的」誤判成 NFS 快取問題，實際上工作目錄是本機 NVMe ext4（`df -T` 可證），真因是前一次 build 根本沒真的跑成功。斷言環境屬性前先 `df -T` / `findmnt` 確認，不要用經驗法則帶過。同樣地，**絕不在「壞掉或根本沒真跑」的 tool 輸出裡腦補結果**——tool call 被擋下就是沒有結果，乾淨重跑，不要順著殘缺輸出繼續推論。

---

## 附錄：老 autotools codec 交叉編譯通用配方

libmad / libmpeg2 / libvorbis 這類老 autotools 庫，交叉編到 NDK / mingw 上會撞到幾個共通雷：

- **`config.sub` / `config.guess`（2004 年代）不認新 triple**：`aarch64-linux-android`、`x86_64-w64-mingw32`、`aarch64-apple-darwin` 一律認不得，換成 GNU 新版覆蓋即可。
- **libmad**：configure 對「是 gcc 就塞」一堆 gcc 專屬最佳化 flag（`-fforce-mem`、`-fthread-jumps`、`-fcse-*`、`-fregmove`、`-fexpensive-optimizations`、`-fschedule-insns2`……），clang / NDK clang 全部不認，一次 `sed` strip 光。
- **libmpeg2**：`libvo` 底下的 DirectX 輸出模組（`video_out_dx.c`）用過時 Win32 API 編不過，只編核心 `make -C libmpeg2` 即可；mingw header 的 extern inline CRT helper 會重複定義，加 `-D__CRT__NO_INLINE`；x86 asm 在 x64 ABI 下 crash（見教訓 3），停用 `ARCH_X86` 改純 C。
- **裝進對應 sysroot**（NDK sysroot / mingw sysroot / `/opt/homebrew`），讓 ScummVM configure 的 compile-test 偵測得到，不然裝了也是白裝。

---

build pipeline 裡每一個「成功」，都要追問一句：**這個成功，真的代表我要的功能在最終產物裡嗎？**
這比任何一條單一修法都重要。
