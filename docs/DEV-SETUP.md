# 開發環境設置(Dev Setup)

從零把這個繁中化專案 build 起來、產出可玩釋出包。整條工具鏈都跑在 Docker 裡,不污染系統環境。

## 你需要什麼

- **Docker**(唯一硬需求;編譯、Python、字型烘製全在容器內)。
- 一份原版遊戲 **Quest for Glory II: Trial by Fire(AGD Interactive VGA remake)**。
  原版免費,到 [agdinteractive.com](https://www.agdinteractive.com) 下載,解壓到專案根目錄的 `game/`。
  - `game/Qfg2vga.exe` 存在就對了。
  - 遊戲是 AGDI 版權檔,**不入 repo**(已 gitignore),只在本機處理。

## 一鍵 bootstrap

```bash
bash tools/dev-setup.sh
```

它會依序:

1. 建好 build 用的 Docker image(`qfg2-scummvm-builder`)。
2. 取 pinned 上游 ScummVM 原碼 + 套我們的 CJK patch(`tools/apply_patches.sh`)。
3. 只開 `ags` engine,在容器內編譯 ScummVM。
4. 從 host 的 Noto Sans CJK TC 烘 16/24px 點陣字型(`tools/build_cjk_font.py`)。
5. 產生繁中翻譯 `chinese.tra`(`tools/make_tra.py`)。
6. 把繁中資產放進 `game/`。

跑完後組釋出包:

```bash
bash tools/package_release.sh linux      # → out/release/qfg2-cht-linux.tar.gz(含遊戲、引擎、中文、啟動器)
```

解開後執行「玩英雄傳奇II-繁中」啟動器即可;遊戲中按 **F8** 循環 繁中16 → 繁中24 → 英文原版。

## 各步驟手動拆解(想單獨重跑某段時)

| 目的 | 指令 |
|---|---|
| 套 patch 到上游 | `bash tools/apply_patches.sh ./scummvm-src` |
| 重編引擎 | 在 builder 容器 `cd scummvm-src && ./configure --disable-all-engines --enable-engine=ags && make -j$(nproc)` |
| 重烘字型 | `tools/build_cjk_font.py --size 24 --charset-file build/charset.txt --bin game/cjkfont24.bin` |
| 重產翻譯 | `tools/make_tra.py tools/translation.tsv --out game/chinese.tra --charset-out build/charset.txt` |
| 滾翻譯一批 | `tools/translate_batch.py`(改 BATCH dict)→ 重產 .tra → `tools/gen_translation_record.py` |
| 重產中英對照典藏 | `tools/gen_translation_record.py`(→ `translation/`) |
| 本機跑英文 baseline | `bash tools/run_cht.sh` |

## 跨平台打包

- **Linux**:本機 `tools/package_release.sh linux`(用本機 build 的引擎)。
- **macOS / Windows / Android**:CI 編譯。push tag 或 `workflow_dispatch` 觸發 `.github/workflows/build.yml`,下載對應 artifact 後:
  - `ENGINE=ScummVM.app tools/package_release.sh macos`
  - `ENGINE=scummvm.exe DLLDIR=path/to/dlls tools/package_release.sh windows`(Windows job artifact 已含相依 DLL)

> patch 釘在上游 commit `patches/UPSTREAM_COMMIT.txt`,本機與 CI 共用同一份 `apply_patches.sh`,確保結果一致。
> 工程過程與技術決策見 `docs/MAKING-OF.md`;可重用方法論見 `.claude/skills/scummvm-ags-cht/`。
