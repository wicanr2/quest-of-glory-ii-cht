---
name: adventure-game-cht-qa
description: 用 headless(無頭)Docker 自動驗證老冒險遊戲(尤其 ScummVM 上的 AGS/SCI/DGDS 重製版,如 英雄傳奇II Quest for Glory、Rise of the Dragon、Willy Beamish、Heart of China)中文化後的實機畫面。當使用者談到「測試遊戲」「驗證中文化」「跑一輪看截圖」「進角色創建/對話畫面確認中文」「F8 語言切換驗證」「AppImage / 完整包能不能跑」「self-contained 驗證」「headless 截圖 QA」「冒險遊戲測試專家」等情境觸發。核心:Xvfb + xdotool + imagemagick 在 Docker 內跑、自適應偵測進畫面(避開 attract mode)、dump PNG 用 Read 看、有界不空轉。與 `scummvm-ags-cht`(做中文化)互補:那支做翻譯,本支驗收成果。
---

# 冒險遊戲中文化實機驗證 SOP

把老冒險遊戲中文化的成果，用 **headless Docker** 跑起來、截真實畫面、用 Read 看圖確認。目標是「不靠人眼盯著視窗」就能回答:中文有沒有正確渲染?F8 切換對不對?角色創建/對話畫面進得去嗎?打包出來的 AppImage/完整包在乾淨環境跑不跑?

> 對應全域 rule:**60**(先建快速決定性 pass/fail 訊號)、**35**(背景任務 liveness,絕不空轉)、**81**(320×200→640×480 座標映射)。本 skill 是這幾條在「冒險遊戲 QA」場景的落地。

## 0. 鐵則(踩過的雷,違反必出事)

1. **全程同步前景跑 Docker，等回傳再下一步。禁止 background sentinel 迴圈**(`until [ -f x ]; do sleep; done` 等過夜空轉)。
2. **headless dump 一定有界**:`timeout N` 或遊戲跑固定秒數後 `pkill`。無界 poll = 殭屍 process 吃 CPU 數小時。
3. **只用檔案輸出 + Read 看圖。禁 GUI viewer**(`eog`/`feh`/`xdg-open`/瀏覽器)——在 headless/agent 環境會開視窗永久阻塞。
4. **Python 一律 Docker uv venv**，不污染系統。
5. 派背景 agent 做這件事時，prompt 必寫:「直接執行不要進 plan mode、Docker 同步前景、有界、禁 GUI viewer、做不到就誠實標受阻結束不要掛起」。

## 1. 環境:capture image(一次建好)

`tools/Dockerfile.capture` 裝 `xvfb xdotool imagemagick python3-pil`，加上已 build 的 ScummVM 引擎掛載進來。建一次重用:

```bash
docker build -q -t qfg2-capture -f tools/Dockerfile.capture tools/
```

跑一輪的骨架(掛載引擎 + 遊戲 + 輸出目錄):

```bash
docker run --rm -v "$PWD/scummvm-src":/src -v "$PWD/game":/game -v "$PWD/out/cap":/out qfg2-capture bash -c '
  export HOME=/tmp DISPLAY=:99
  Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
  timeout 110 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/r.log &
  sleep 7
  WID=$(xdotool search --onlyvisible --name . | tail -1)
  xdotool windowactivate --sync "$WID"; xdotool windowfocus "$WID"
  # ...互動 + 截圖...
  pkill -f scummvm; sleep 1'
```

## 2. 最大難關:進到你要驗證的畫面(自適應，避開 attract mode)

老遊戲(尤其 AGDI 重製版)主選單有 **attract mode**:閒置會自動播片頭過場，且過場播完(~23-35s)選單才出現。**固定 sleep 後盲點會點到過場、或點空**。解法是**自適應輪詢**——偵測目標畫面的特徵 pixel 才動作:

```python
# redcheck.py 範式:數某區域的特徵色 pixel(這裡是選單的鮮紅按鈕字)
import sys; from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB"); px = im.load(); c = 0
for y in range(420, 610):
    for x in range(380, 580):
        r, g, b = px[x, y]
        if r > 175 and g < 75 and b < 70: c += 1
print(c)
```

```bash
# 輪詢直到特徵出現才點(上限 30 次，有界)
for i in $(seq 1 30); do sleep 1.4; import -window root /tmp/p.png
  R=$(python3 /out/redcheck.py /tmp/p.png 2>/dev/null || echo 0)
  [ "${R:-0}" -gt 25 ] && break; done
```

**通用化**:換遊戲就換特徵(某顏色塊、某區域非黑、某字的點陣密度)。原則是「偵測畫面狀態，不要賭時間」。

進角色創建的完整點擊序列(QFG2 實測，座標依視窗大小)記在 `scummvm-ags-cht` skill 與 `tools/capture_*.sh`:New Game(512,384)→ 等紅字 → 確認 → 職業 → 進 room。

## 3. 座標映射(關鍵教訓)

遊戲內部多半是 **320×200**，在 640×480 視窗放大 2× 顯示，上下各有 **40px letterbox 黑邊**:

```
room bg y = (顯示 y - 40) / 2          顯示 x = room bg x * 2
```

- ScummVM 視窗在 root 的偏移:截 root 後 `convert shot.png -crop 640x480+192+144 +repage out.png` 取遊戲區。
- 滑鼠命中、F10 dump 出的 raw 座標跟顯示可能差 ~19，**從實機截圖反推**最準，別信單一來源。

## 4. 驗證 checklist(逐項 dump PNG → Read 看)

| 項目 | 怎麼驗 | 通過標準 |
|------|--------|----------|
| CJK 端到端 | 截開場免責聲明/disclaimer | 繁中正確渲染、中英混排同大小同基線 |
| 對話 | 進 NPC 對話截圖 | 台詞繁中、專名加註(如「卡塔(Katta)」) |
| 角色創建 | 進 room 截圖 | 屬性名/職業/標題中文、數值正確、背景紋理完整 |
| F8 語言切換 | 連按 F8 各截一張(中16→中24→英) | 三態都對、切回原版不破圖、玩家數值不變 |
| 打包完整性 | **乾淨環境**跑 AppImage/完整包 | self-contained 啟動、不缺 .so、中文正常 |

**看圖用 Read 工具直接看 PNG**(harness 會視覺呈現)，不要 `cat`、不要開 viewer。

## 4b. 完整翻譯掃描(最易漏 — 實戰血淚)

**「畫面有中文」≠「翻完整」。** 每進一個畫面,要逐字掃**殘留英文**,而不是看到有中文就過。實戰漏掉過一整批:角色創建底部欄(Avail Pts / Puzzle Pts / Health / Stamina / Mana 全沒翻,只翻了上半 15 個屬性名)、職業 button 的 normal sprite(未 hover 是英文、hover 才中文)、start / cancel button、空名時的錯誤提示框 "Please choose a longer name"、遊戲內 dialog 對話介面、頂部標題字級過大。QA 當時只確認「有中文」就放行,全數漏掉。

掃描鐵則:
- **逐畫面列「英文殘留清單」**:每張截圖讀完,把**還是英文的字一個個列出來**當待辦,而不是確認有中文就過。通過標準 = 畫面上找不到任何一個英文單字(專名加註的原文括號如「夏皮爾(Shapeir)」除外)。
- **button/sprite 兩態都要看**:normal(未選/未 hover)與 highlight(選中/hover)是**不同 sprite**,常只換了一個。對每個 button 都 hover 上去截一張、移開再截一張,兩張都要中文。
- **互動觸發的文字才看得到**:錯誤提示框(故意觸發,如空名按確定)、hover tooltip、對話選項 UI、暫停選單、確認對話框(Yes/No、still-have-points)。不互動就完全漏掉。
- **room bg 美術字要數齊**:一個面板的標籤常分散多區(主屬性 + 底部統計 + 按鈕列),manifest/inpaint 要涵蓋**全部**,不只顯眼的上半。
- **字級也算瑕疵**:標題/標籤中文若被切邊、過大溢出、與框不對齊,一併記。

## 5. 打包驗證(self-contained 的真測法)

別在「已裝開發依賴的機器」測打包——那測不出缺函式庫。**用乾淨 base image 模擬目標機**:

```bash
docker run --rm -v "$PWD/out/release":/rel ubuntu:24.04 bash -c '
  apt-get update -qq && apt-get install -y -qq xvfb libgl1 imagemagick >/dev/null
  export DISPLAY=:99 HOME=/tmp APPIMAGE_EXTRACT_AND_RUN=1 SDL_AUDIODRIVER=dummy
  Xvfb :99 -screen 0 1024x768x24 & sleep 2
  timeout 70 /rel/*.AppImage > /tmp/run.log 2>&1 &
  sleep 16; import -window root /rel/test.png
  pkill -f scummvm; grep -iE "error|cannot|no such" /tmp/run.log'
```

- `error while loading shared libraries: libXXX` = 打包漏了 load-time 依賴。AppImage 的 linuxdeploy excludelist 會排掉 ALSA/JACK/PulseAudio(假設系統有，但多數桌面沒裝 JACK)→ 把 `ldd` 全依賴補進 `usr/lib`，只跳過 glibc 核心與 display/GL。
- `APPIMAGE_EXTRACT_AND_RUN=1` 讓 AppImage 在無 FUSE 的容器內解壓跑。
- ALSA conf 警告、`translations.dat` 警告無害(前者缺音效設定、後者是 ScummVM GUI 介面翻譯，都不影響遊戲)。

## 6. 判活死(背景 agent 編排時)

- output 檔 `stat -c %Y` 距今秒數 + 有無活躍 docker/python process = 區分「長操作」vs「卡死」。
- **小 output + 無 process + 數分鐘不動 = 卡死前兆，立刻介入**，不等數小時。
- 殭屍容器(`--rm`+`timeout` 卻 Up 數小時)→ `docker kill`。只動本專案資源，別碰別人的容器。

## 參考實作(本專案已驗證)

- `tools/capture_gameplay.sh` / `tools/capture_story.sh` — 進遊戲 + 密集截圖
- `tools/Dockerfile.capture` — capture image
- `out/cap/redcheck.py` — 自適應特徵偵測範式
- `tools/make_appimage.sh` — 打包 + 內附乾淨環境驗證思路
- 中文化本身的 SOP 在姊妹 skill `scummvm-ags-cht`
