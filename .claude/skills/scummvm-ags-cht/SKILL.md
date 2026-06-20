---
name: scummvm-ags-cht
description: 把 AGS (Adventure Game Studio) 引擎的老遊戲(尤其 AGDI/Sierra 重製版,如 Quest for Glory II VGA)做繁體中文化 + 全平台打包的 SOP,跑在 ScummVM 的 AGS engine 上。當使用者談到「AGS 中文化」「AGDI 重製版」「Quest for Glory II VGA / 英雄傳奇II」「ac2game.ags」「.tra 翻譯檔」「acsetup.cfg」「ScummVM ags engine CJK」「CLIB / MFL 解包」「Avis Durgan」「AGS 字型 WFN」「AGS Android/macOS 打包」等情境觸發。與 DGDS 系(rise-of-the-dragon-cht)互補:那支處理 DGDS/TTM,本支處理 AGS。
---

# ScummVM AGS 引擎遊戲繁中化 SOP

把 AGS 老遊戲(常見於 AGDI / Infamous Adventures 的 Sierra 重製版)中文化,跑在 **ScummVM 的 ags engine** 上(因為要 Android / macOS / 全平台,ScummVM port 成熟,原生 AGS 沒有 Android)。

> 與 `rise-of-the-dragon-cht`(DGDS 引擎)是平行方法論。**先確認引擎**:同一個 Sierra IP 可能有 SCI 原版(走 ScummVM sci)、DGDS 版、或 AGS 重製版,做法完全不同。

## 0. 先辨識引擎(最關鍵,選錯白做)

老遊戲資料夾若出現以下任一,就是 **AGS**,不是 SCI:
- `acsetup.cfg` / `winsetup.exe`(AGS 設定/設定程式)
- `ac2game.ags` 或 `*.exe` 內 embed CLIB
- exe `strings` 出現 `Adventure Game Studio` / `ACI version 2.xx.xxx`

抓 AGS 版本:`strings GAME.exe | grep -E "ACI version"`。
- 2.xx(如 **2.72**)= 舊版,單位元組 ANSI,原生不支援 CJK。
- 3.6+ = 現代,原生支援 UTF-8。

ScummVM 偵測:`scummvm --detect --path=GAMEDIR`。AGDI 的遊戲多半已在偵測表(如 `ags:qfg2agdi`)。

## 1. AGS 資料結構速查

- **CLIB / MFL**(Multi-File Library):資料庫,常 append 在 `GAME.exe` 尾端。
  - exe 末 16 bytes = `int32 offset` + 簽章 `CLIB\x01\x02\x03\x04SIGE`。
  - 該 offset 處 = `CLIB\x1a` + version byte(如 `0x0f` = MFL v15)+ 資料檔清單(`ac2game.ags`, `GAME.001`...`.0NN`)。
  - asset bytes 分散在 `GAME.001`–`.0NN`;`.001` 常是 sprite 庫(`"Sprite File"` 標頭)。
- **`ac2game.ags`** = 主遊戲資料:全域訊息、對白、GUI 文字、角色/物品名、編譯後 script(含字串表)。**文字所在**。
- 部分字串以 AGS 慣用 key **"Avis Durgan"** 加密。
- **`.tra`**(編譯後翻譯檔)= 中文化的注入點:
  - 結構 = **dictionary(原文英→譯文)** + `GameUid`/`GameName`(需與遊戲相符)。
  - 可指定 `NormalFont` / `SpeechFont` 替換字型 slot、`RightToLeft`。
  - 權威格式見 ScummVM `engines/ags/shared/game/tra_file.{h,cpp}`。
- **字型**:`.wfn`(點陣,glyph 0–255 單位元組)或 TTF。renderer 見 `engines/ags/shared/font/{wfn,ttf}_font_renderer.cpp`、`fonts.cpp`。ScummVM AGS 已有 `shared/util/utf8.h`。

## 2. Docker build ScummVM(只開 ags engine,加快)

`tools/Dockerfile.builder`(ubuntu:24.04 + libsdl2-dev + libfreetype-dev + libpng/jpeg/vorbis/flac… + xvfb)。
```
./configure --disable-all-engines --enable-engine=ags --enable-release
make -j$(nproc)
```
HARD:一律 docker;Python 一律 docker uv venv(不污染系統)。

## 3. Headless 驗證 feedback loop(本 skill 核心技巧)

無頭環境跑 ScummVM 並截圖,驅動輸入跳過 splash —— 所有改動的 pass/fail 訊號:
```bash
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get install -y xvfb imagemagick xdotool
Xvfb :99 -screen 0 1024x768x24 &
timeout 30 ./scummvm --path=/game --auto-detect &
sleep 9
for i in 1 2 3 4 5; do xdotool key Return space Escape; sleep 1.2; done   # 跳過 AGDI logo/splash
import -window root /out/shot.png         # dump PNG,再用 Read 看(rule 35:不開 GUI viewer)
```
鐵則(rule 35):**有界**(`timeout`)、**dump PNG 不開視窗**、**不寫 sentinel 輪詢迴圈**、docker 同步前景。

## 4. CJK 中文化策略

AGS 2.xx 原生 ANSI,但 ScummVM AGS engine 有 utf8.h + TTF/FreeType,路徑比想像輕量:

1. **文字抽取**:最乾淨 = 在引擎內加 dump 模式,**重用引擎自己的 parser** 把全部可翻譯字串吐成 `.trs`(避免自寫 MFL/script 解析器)。退路才是自寫 MFL v15 解包 + `ac2game.ags`/`roomN.crm` parser。
2. **翻譯**:`.trs` 逐行填繁中 → 編 `.tra`(dictionary)。先建 `CONTEXT.md` 譯名表(rule 50)。
3. **字型**:從 host 烘 24×24 / 16×16 點陣 atlas(`tools/build_cjk_font.py`,docker uv + Pillow,Noto Sans CJK TC / AR PL UMing TW)。
4. **繪字 patch**:攔截 `fonts.cpp` 繪字/字寬路徑,偵測多位元組(UTF-8)序列 → blit atlas 24×24 glyph;ASCII 走原 WFN/TTF。`.tra` 用 UTF-8 中文 + 指定 CJK 字型 slot。
5. **hi-res canvas(rule 81)**:內部畫布拉 640×480,原圖 nearest 放大保銳利,中文 24×24 畫在放大後畫布;舊 UI 座標做比例 remap、滑鼠 hit-test 同步映射。**不要把中文縮小塞原字位**。

## 5. 全平台打包(GitHub Actions,不需 Mac 機)

- **Android**:ScummVM NDK build → APK,把遊戲資料 + `.tra` + 字型注入 assets。
- **macOS**:GitHub Actions `macos-14` runner build universal `.app` → `.dmg`(對齊 `mac-app-cross-pack` skill:`std::unary_function` C++14 fallback、dylibbundler、quarantine 解除)。
- 輸出 repo README:照 `80-retro-cht-readme-polish`(三層 voice:hero 信 / 雜誌風 / technical)。

## 踩雷

- `Unable to decode video 'AGDI.001'` / `Failed to find RIFF header` = AGDI launcher splash 影片,**無害**,遊戲照進。
- ALSA `seq_hw open failed` 噪音 = 無音效裝置,無害。
- 遊戲內部解析度可能是 320×**200**(非 240),看 ScummVM log `Graphics mode set`。
- 截圖全黑 3KB = 抓太早或 game 在 splash;先用 ScummVM launcher GUI(不帶 `--auto-detect`)截圖當對照確認擷取管線 OK,再 xdotool 跳 splash。
- HARD 譯名:對外文件用 `CONTEXT.md` 定版術語,不臨時造詞。

## 參考個案

- **quest-of-glory-ii-cht**(英雄傳奇II:烈火試煉,AGS 2.72,AGDI VGA remake)— 本 skill 的源頭專案。
- 字型烘製:`tools/build_cjk_font.py`。
