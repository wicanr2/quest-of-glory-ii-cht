# 製作筆記:把 AGS 2.72 老遊戲做成繁中化 ScummVM

這份筆記記錄《英雄傳奇 II:烈火試煉》繁中化的工程過程與技術決策,供日後同類專案(AGS / ScummVM 老遊戲漢化)參考。對應可重用方法論見 `.claude/skills/scummvm-ags-cht/`。

## 一、先搞清楚引擎(最關鍵的第一步)

直覺以為 QFG2 是 Sierra SCI(原版 1990 確實是),但這個專案的目標是 **AGDI 的 VGA 重製版**,它用 **Adventure Game Studio (AGS) 2.72** 製作。辨識依據:

- 檔案出現 `acsetup.cfg` / `winsetup.exe` → AGS 標記。
- `Qfg2vga.exe` 內 `strings` 出現 `ACI version 2.72.920`。
- 遊戲資料是 AGS 的 CLIB 多檔庫(append 在 exe 尾端,簽章 `CLIB\x01\x02\x03\x04SIGE`),asset bytes 散在 `Qfg2vga.001`–`.024`,主邏輯在 embed 的 `ac2game.ags`。

**教訓:同一個 IP 可能有 SCI 原版 / DGDS 版 / AGS 重製版,引擎不同則整套做法不同。** 動手前先驗明引擎與版本。

## 二、為什麼選 ScummVM 而不是原生 AGS

需要 **Android 版**。ScummVM 有成熟的 Android port,原生 AGS 沒有。代價是要在 ScummVM 的 AGS 引擎裡自己寫 CJK 繪字 patch(原生 AGS 3.6 有內建 UTF-8 + TTF,但綁不到 Android)。

## 三、CJK 渲染:在 1999 年的單位元組引擎裡畫方塊字

AGS 2.72 是徹底的單位元組 ANSI 引擎。讓它畫中文,動的是 ScummVM 的 AGS 引擎,全部收斂在一份自包含 patch(`patches/0001-qfg2-cht-cjk.patch`):

1. **`set_uformat(U_UTF8)`** → Allegro 的 `ugetxc()` 自動把 UTF-8 解成整個 codepoint。觸發方式:`.tra` 加 `ext_sopts` block 宣告 `encoding=utf-8`,`init_translation` 會自己設好(比改 engine.cpp 可靠,免順序問題)。
2. **`wfn_font_renderer.cpp` 三方法加分支**:codepoint 命中 CJK atlas → blit 點陣字;否則走原 WFN。`GetTextWidth` 要把 ASCII(×SizeMultiplier)與 CJK(固定字級)分開累加。
3. **`fonts.cpp` `font_post_init`**:CJK 啟用時把行高/行距抬到 ≥ 字級,否則多行中文上下重疊(行距預設用原 WFN ~8px)。**必踩。**
4. **字型 atlas**:`tools/build_cjk_font.py` 從 host 的 Noto Sans CJK TC 烘 `CJKF` 二進位(每字 codepoint + advance + 覆蓋率),引擎用 AssetMgr 載入。

## 四、翻譯注入:自製 AGS `.tra`,不用 editor

AGS 翻譯走 `.tra`(原文→譯文 dictionary,Avis Durgan 加密)。`tools/make_tra.py` 完整實作格式(權威來源 = ScummVM `shared/game/tra_file.cpp` + `data_ext.cpp` + `words_dictionary.cpp`):

- header `"AGSTranslation\0"` + blocks(數字 id / 字串 id "ext_sopts")+ EOF。
- 字串 = int32 len + Avis Durgan 加密 bytes;**GameUid=0 + 空名 → 跳過 game 比對。**
- 抽字用「引擎內 dump 重用其 parser」(`cht_dump_static_strings` 走訪 `game.messages` + 三個 script 字串表 + 物品名),一次抽出 6716 字串(2350 乾淨可翻句),比自寫 MFL/script 解析器穩。

## 五、踩過的雷(AGDI / ScummVM 特有)

- **`SetSpeechFont` 崩潰**:AGDI 遊戲偵測到翻譯時會要一個 base game 沒有的字型 slot → `quit()`。改成寬容(warning + return),CJK 渲染本就字型無關。
- **主選單裝飾標題字繞過 `get_translation`**(自繪/精靈圖)→ 翻不到。對白 / `Display()` 才走翻譯。
- **中英混排大小不一**:中文是 atlas 固定字級、英文是原 WFN ~8px,同行會大小不一、英文偏上。解法:**把 ASCII 0x20–0x7E 也烘進 atlas**(同 Noto、等高、比例寬、共用基線),繪字器每行先偵測有無中文,含中文整行走 atlas。
- **無頭擷取**:`xvfb` + `xdotool`(focus 視窗後定向 click / 鍵盤捷徑)+ `import` dump PNG。AGDI 標題選單的輸入在無頭環境不穩,需 `windowactivate --sync` + `mousedown/up`。

## 六、做不到的事(誠實記錄)

**真 640×480 內部畫布在 ScummVM AGS 不可行。** 軟體渲染器 `ali_3d_scummvm` 的 `RenderSpritesAtScreenResolution()` 是空實作;一切在 native 320×200 渲染再由後端縮放,無 supersampling。要更大畫布就得把所有美術 2× + 全座標 remap,動到整個資料模型。**實務替代:16/24px 點陣 + F8 動態切換 + 視窗放大。**

CJK 抗鋸齒也卡在 `makeacol32`/`getr32` 的全域 allegro 像素格式不一定等於目標 bitmap 實際格式(會變洋紅),需取該 bitmap 自身格式,留待後續。

## 七、F8 遊戲中動態切換(仿 Dynamix 漢化)

按 F8 循環 **繁中16 → 繁中24 → 英文原版**。在 `run_service_key_controls` 攔截 `eAGSKeyCodeF8` 並消耗(QFG2 未綁 F8);切字級後**必須** `font_recalc_metrics` 逐字型重算行距,否則 16↔24 行距不符會重疊。

## 八、翻譯工程(2352 句)

語感參照 1990 年代《軟體世界》三大誌攻略(生動口語、對讀者直呼);專名走阿拉伯/波斯風音譯;角色語域(Uhura 獅人 pidgin、Effendi=閣下);諧音盡量保趣味。自創生物/地名顯示時附原文(`make_tra.py` 的 GLOSS map,如 索魯斯(Saurus)、卡塔(Katta))。

工具鏈每批流程:`translate_batch.py`(BATCH dict,resolver 精確全字優先+唯一子串退路)→ `make_tra.py`(.tra,加註)→ `build_cjk_font.py`(16/24)→ `gen_translation_record.py`(中英對照典藏 `translation/`)→ commit+push。

## 九、打包

`tools/apply_patches.sh` 取 pinned 上游 ScummVM 套 patch(本機/CI 共用)。GitHub Actions(`.github/workflows/build.yml`)出 translate-assets(平台無關中文資產,CI 綠燈)、macOS `.dmg`(綠燈)、Windows、Android。`tools/package_release.sh` 把引擎 + 遊戲 + 中文資產 + 啟動腳本組成完整可玩包(遊戲版權檔本機處理,不入公開 repo)。

> 對應可重用 skill:`.claude/skills/scummvm-ags-cht/SKILL.md`(觸發「AGS 中文化」「AGDI 重製版」等)。
