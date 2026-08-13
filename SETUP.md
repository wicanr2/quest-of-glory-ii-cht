# SETUP — 在另一台機器重建 QFG2 繁中化開發/打包環境

英雄傳奇 II:烈火神兵(Quest for Glory II, AGDI VGA remake, AGS 2.72)繁中化專案。
跑在 ScummVM 的 AGS engine 上 + 自寫 CJK patch。本包讓另一台機器**重建環境**並用
`claude -r` **接續同一個 Claude 對話**(見 `previous-work.md` 末段)。

## 0. 解開到「相同絕對路徑」(★ claude -r 跨機接續的前提)

```bash
# 路徑必須是 /home/anr2/scummvm/qog-2,claude session 的目錄編碼才對得上
mkdir -p /home/anr2/scummvm && cd /home/anr2/scummvm
tar --zstd -xf dev-setup-qfg2-20260622.tar.zst -C qog-2   # 或解到 qog-2/
cd /home/anr2/scummvm/qog-2
```
若新機器 user/home 不同(路徑無法一致)→ 見 `previous-work.md` §跨機接續的 UUID 法。

## 1. 還原 Claude session(對話 + 記憶)

```bash
mkdir -p ~/.claude/projects
cp -a claude-session/projects/-home-anr2-scummvm-qog-2 ~/.claude/projects/
# 之後 cd 本專案 → claude --resume 03b19348-a7c3-41a5-88cb-97eb16b8173b
```

## 2. 前置:Docker(唯一硬需求)

全程 Docker,不污染系統 Python(專案鐵則)。三個工具鏈 image 都**從 Dockerfile 自動重建**,
不入包:
| image | 來源 Dockerfile | 由誰 build |
|---|---|---|
| `qfg2-scummvm-builder` | `tools/Dockerfile.builder` | `tools/dev-setup.sh` 自動 |
| `qfg2-win-cross` | `docker/Dockerfile.win-cross` | `tools/build_windows_debian.sh` 自動 |
| `qfg2-android-inject` | `docker/Dockerfile.android-inject` | `tools/inject_android.sh` 自動 |

> ⚠ 本機環境**出口防火牆只開 443(https)**:apt 走 http:80 會 timeout。三個 Dockerfile 都已
> 把 apt 來源改 https。若新環境正常(80 通),不影響。

## 3. 重建 ScummVM 引擎(scummvm-src/ 不入包,重建)

```bash
bash tools/dev-setup.sh     # clone pinned ScummVM → 套 patches/*.patch → 烘 12/16/24 字型 → 產 chinese.tra
                            # (內含 apply_patches.sh;產物進 game/ 與 scummvm-src/)
```
`game/`(原版 + 繁中資產)**已含在包內**,可直接打包;若要從零:解 `quest-for-glory-ii-trial-by-fire.zip` 到 `game/`。

## 4. 打包各平台

```bash
bash tools/make_appimage.sh                                   # Linux AppImage(self-contained)
bash tools/package_release.sh linux                           # Linux tar.gz(本地引擎)
# Windows:本地交叉編譯(不依賴 CI)
bash tools/build_windows_debian.sh                            # → out/win-debian/scummvm.exe + DLL
ENGINE=out/win-debian/scummvm.exe DLLDIR=out/win-debian bash tools/package_release.sh windows
# macOS:用 CI artifact 的 ScummVM.app
ENGINE=out/mac-ci/ext/ScummVM.app bash tools/package_release.sh macos
# Android:CI base APK + 注入遊戲(開箱即玩 FULL APK)
bash tools/inject_android.sh                                  # → out/apk/qfg2-cht-android-FULL.apk
```
Windows/macOS/Android 的 base 引擎來自 GitHub Actions(`.github/workflows/build.yml`):
`gh run download` 取 artifact 放 `out/win-ci`、`out/mac-ci`、`out/apk/ScummVM-debug.apk`。

## 重建注意
- `scummvm-src/`(917M)、`build/`(357M)、`out/`(產物)、合輯 zip(640M)**不入包**,皆可重建。
- `game/` 是 AGDI 版權資料 + 衍生中文檔,**僅供你本機自用,勿散布、勿入公開 repo**。
- 公開 repo:`github.com/wicanr2/quest-of-glory-ii-cht`(只有引擎 patch + 工具 + 翻譯,無遊戲)。
