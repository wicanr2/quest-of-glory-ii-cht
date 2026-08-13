# previous-work — QFG2 繁中化 工作交接(截至 2026-06-22)

## 專案現況快照
- 公開 repo:`github.com/wicanr2/quest-of-glory-ii-cht`,分支 `main`,HEAD `2113568`。
- 已 push:README 雜誌增強 + 譯名修正(`e1d517a`)、Windows 交叉編譯工具鏈(`a5eb807`)、
  烈火考驗(`d21dbf1`)、**打包補 ScummVM data 檔修 GitHub issue #1/#2**(`2113568`)。
- **未 commit**:`docker/Dockerfile.android-inject` + `tools/inject_android.sh`(待 Android 實機驗證後再 commit)。
- 成品(`out/`,皆不入庫,可重建):
  - Linux:`英雄傳奇II-烈火神兵-x86_64.AppImage`(160M)、`qfg2-cht-linux.tar.gz`(147M)
  - Windows:`qfg2-cht-windows.tar.gz`(159M,本地 Debian-mingw 交叉編譯 exe,含 vorbis 音樂)
  - macOS:`qfg2-cht-macos.tar.gz`(146M,CI 的 ScummVM.app)
  - Android:`ScummVM-debug.apk`(CI 純引擎 base)+ `qfg2-cht-android-FULL.apk`(99M,注入遊戲開箱即玩)
  - ★ 桌面三平台都已補 ScummVM 15 個 data 檔(見本次工作 #5)、全部最新譯文。

## 本次做的工作(依主題)
1. **README 雜誌段參考《軟體世界》增強**:兩章織入 1991 攻略具體橋段(四元素收服、殺價、午夜潛行、
   Djinn 三願、計分表),三大誌人聲,合理引用一句標出處。攻略 OCR `docs/softworld-qfg2-walkthrough.md`
   gitignore、未入庫。
2. **譯名修正(對齊遊戲文本)**:Reversal「驅散」→「反轉」(撞 Dispel);Force Bolt 統一「原力箭」
   (參考魔獸世界;原 translation.tsv 力箭/力鏢/力矢/衝擊彈混用;另修 line 6144 一般語境
   trial by fire「烈火試煉」→「烈火考驗」避免與副標《烈火神兵》撞字)。CONTEXT.md 同步副標
   「烈火神兵」+ 反轉/原力箭詞條。已重編 `game/chinese.tra`(9645 對)+ 12/24 字型,重打全平台。
3. **Windows 本地交叉編譯**(`docker/Dockerfile.win-cross` + `tools/build_windows_debian.sh`):
   Linux 上 Debian-mingw cross,不依賴 CI。四個雷固化:apt 走 https(出口僅 443)、裝 binutils 補
   host `strings`(否則 configure endianness=unknown)、官方 SDL2-devel-mingw、手編 libogg/libvorbis
   static(music.vox 是 ogg)。產 26M exe,vorbis 已驗證啟用。
4. **Android inject**(`docker/Dockerfile.android-inject` + `tools/inject_android.sh`):把遊戲注入
   CI base APK → 開箱即玩 FULL APK。雷:雙層 `assets/assets/games/qfg2agdi/` + 登錄 `MD5SUMS`、補
   runtime libs(liboboe.so + r26d libc++_shared.so,否則秒退)、zipalign + debug 重簽。
   **跨容器傳檔的 NFS 不一致雷(見工具鏈段)** → 把 libs/工具烘進 image、不經 mount 傳遞解決。
5. **修 Windows/Linux 包啟動失敗(GitHub issue #1 #2)**:`package_release.sh`/`make_appimage.sh`
   只 cp 引擎+DLL+遊戲,漏帶 ScummVM 執行必需的 **15 個 data 檔**(GUI theme zip + engine data:
   `scummmodern/scummremastered.zip`、`gui-icons.dat`、`encoding.dat`、`fonts.dat`、`fonts-cjk.dat`
   等)。macOS 走 `.app`(`make bundle` 含 Resources)未中,故只 Windows/Linux 玩家撞:#1「Failed to
   load theme SCUMMREMASTERED.ZIP」、#2「Could not find suitable engine plugin」(同一包不完整的
   連鎖)。修:兩腳本從 `scummvm-src/gui/themes` + `dists/engine-data` + `dists/networking` 收集
   data(對齊 mac core 集);AppImage 另用 `--themepath`/`--extrapath` 指 `usr/share/scummvm/`。
   wine 驗證:補 data 後 `engine ID 'ags'` 正確載入、錯誤消失。四平台包已重打。commit `2113568`。

## 工具鏈 / harness 注意
- 三個 docker image,全可從 Dockerfile 重建(見 SETUP.md 表)。
- **docker 出口防火牆只開 443**:apt 必走 https(三 Dockerfile 已處理)。
- **docker bind-mount 跨容器不一致 = NFS 掛載所致(非 docker 本身問題)**:使用者環境是**兩台
  機器透過 NFS 共享掛載**本專案目錄。NFS 的 client 端快取 + close-to-open 一致性,造成「host/
  容器 A 寫小檔 → 容器 B 啟動時 mount 到舊內容」「大檔(660M NDK zip)寫入沒同步回 NFS」。
  徵兆:同一檔反覆變回舊版、stdout 寫好的檔被下個容器覆蓋。對策:小檔用 `unzip -p` 等經 stdout
  直接落地(繞過 mount 寫入);需跨容器穩定的檔**烘進 image**,別放 NFS mount 目錄反覆讀寫。
  (根因由使用者澄清 2026-06-27;原誤判為 docker 快照問題)
- Python 一律 docker uv venv(`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`),不污染系統。
- **macOS build 的 SDL2**:brew 的 SDL 可能已升 SDL3,ScummVM configure 會誤 link SDL3 → 編譯/
  執行壞掉。對策同 Windows(用官方 SDL2-devel-mingw):macOS 改**自己編 SDL2 from source**(或 pin
  `sdl2@2` formula、明確 `--with-sdl-prefix` 指向 SDL2),別讓 configure 抓到 brew 的 SDL3。
  (使用者提醒 2026-06-26;目前 CI macos job 用 `brew install sdl2`,brew 一旦改版就會中,要先改)。

## 待辦 / 開放項目
- 🔲 **README 截圖更新(暫緩 — 使用者決定 2026-06-22 等功能齊再一次拍)**:查證後,圖內容大多
   正確(對話/屬性名中文都對),唯一確實「舊」的是遊戲世界 status bar 副標「烈火試煉」(現已神兵);
   角色創建的 `Name`/`start`/`cancel`/`Health`/`Mana` 及主選單 `Start New Hero` 等英文,是**尚未
   中文化的 room 美術字**(非圖過期)。決定:等這批 room/GUI 美術字也中文化後,再一次性重截全部
   README 圖。屆時重截建議用**客棧存檔**(headless 自動 playthrough 到客棧對話不可靠 — 無存檔可
   跳關、開場動畫時長不定、AGS 對話樹難盲操作,實測兩輪都卡在主選單/動畫)。
- ⏳ **Android FULL APK 實機測**:launcher 是否自動出現遊戲 / 啟動不秒退(r26d libc++_shared)/
   Game Options 選 Chinese 後中文。過了才 commit inject 工具。
- 🔲 **自動中文(可選)**:AGS 走 ScummVM config key,Android 要手動選一次 Chinese translation。
   若要「裝了免設定直接中文」→ 加「遊戲目錄有 chinese.tra 就自動 translation=chinese」patch
   (`config.cpp` usetup.translation 預設;桌面也受益),需 CI 重編 android base APK。

## 鐵則 / 硬約束
- `game/`(AGDI 版權)+ `docs/softworld-qfg2-walkthrough.md`(雜誌 OCR)+ `cht_roombg*/btnsprites.bin`
  (衍生)**絕不入公開 repo**(已 gitignore);dev-setup 私用可含,勿散布。
- push 到 GitHub 前要使用者確認。Python 只用 docker uv。不 kill 其他專案的 docker 容器。
- headless/agent 環境不開 GUI viewer(用 Read 看 dump PNG);docker 同步前景、不背景空轉。

## § 在別台電腦接續(claude -r)
- 最近 session UUID:**`03b19348-a7c3-41a5-88cb-97eb16b8173b`**
- 步驟:解包到**相同路徑** `/home/anr2/scummvm/qog-2` → 還原
  `claude-session/projects/-home-anr2-scummvm-qog-2` 到 `~/.claude/projects/` → `cd` 專案 →
  `claude --resume 03b19348-a7c3-41a5-88cb-97eb16b8173b`(用 UUID 不卡路徑)。
- 路徑不同時:把 `~/.claude/projects/<舊編碼>` 改名成新路徑編碼,或直接用上面 UUID resume。

## 記憶索引(`~/.claude/projects/-home-anr2-scummvm-qog-2/memory/`)
- `qfg2-cht-project.md` — 專案總覽(AGS 2.72、CJK patch、CI 打包)
- `qfg2-translation-voice.md` — 譯文語氣參照《軟體世界》攻略
- `scummvm-win-cross-linux.md` — Linux→Windows 交叉編譯四雷 + Dockerfile 配方(可跨專案)
