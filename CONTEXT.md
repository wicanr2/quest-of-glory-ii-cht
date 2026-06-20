# CONTEXT.md — 英雄傳奇II 繁中化 Ubiquitous Language

Quest for Glory II: Trial by Fire(AGDI VGA remake, AGS 2.72)繁體中文化專案的 canonical 術語表。
寫程式、命名、翻譯、寫文件時優先使用本表詞彙;遇新概念先進本表再用。
格式:`Term — 定義/譯名. _Avoid_: 禁用同義詞`。

> 狀態:**音譯風格已定**(使用者 2026-06-20):副標「烈火試煉」;人名地名走**阿拉伯/波斯風**音譯(QFG2 為一千零一夜題材)。QFG 自創種族名(獅人/卡塔/索魯斯)維持原音譯。

## 專案 / 引擎

- AGS — Adventure Game Studio,本遊戲引擎(2.72.920)。_Avoid_: SCI、Sierra 引擎(那是 1990 原版,本專案是 VGA 重製)。
- ScummVM AGS engine — 執行平台,中文化在此 patch。
- CLIB — AGS 多檔資料庫(append 在 `Qfg2vga.exe`,MFL v15,asset bytes 在 `Qfg2vga.001`–`.024`)。
- `ac2game.ags` — 主遊戲資料(全域訊息/對白/GUI/角色/物品文字所在),embed 在 exe 內。
- `.tra` — AGS 編譯後翻譯檔(dictionary:原文英→譯文,可指定替換字型 slot)。_Avoid_: 把它叫「語言包」。
- `.trs` — 翻譯原始檔(抽出的全部原文 key,逐行待翻)。
- CJK atlas — 24×24 點陣中文字圖(`fonts/cjk24.png` + `.json`),引擎繪字 patch 用。
- hi-res canvas — 內部畫布拉 640×480、原圖 nearest 放大、中文 24×24(rule 81)。

## 系統 / 介面

- 冒險者公會 — Adventurers' Guild
- 榮譽 — Honor(聖騎士關鍵屬性)
- 法力 — Mana。_Avoid_: 魔力、MP
- 生命力 — Health/Hit Points
- 耐力 — Stamina
- 驅散藥水 — Dispel Potion
- 第納爾 — Dinar(貨幣)。_Avoid_: 金幣、銀幣

## 職業 / 種族

- 戰士 — Fighter
- 法師 — Magic User / Wizard
- 盜賊 — Thief
- 聖騎士 — Paladin
- 獅人 — Liontaur(獅身人馬族;Rakeesh、Uhura)
- 卡塔族 — Katta(貓臉商人族;Shameen、Shema)
- 索魯斯 — Saurus(可騎乘的蜥蜴坐騎)。_Avoid_: 恐龍

## 地名(阿拉伯/波斯風)

- 夏皮爾 — Shapeir(主城,商隊之城)。與拉希爾押 -爾 韻
- 拉希爾 — Raseir(受壓迫的姊妹城)
- 史畢柏格 — Spielburg(QFG1 故鄉,劇情提及;德語地名維持原音)

## 人物(主要,阿拉伯/波斯風音譯)

- 阿德·阿維斯 — Ad Avis(反派巫師)
- 伊布利斯 — Iblis(阿德·阿維斯欲喚醒的惡魔;阿拉伯傳說魔王 إبليس)
- 哈維因 — Khaveen(拉希爾衛隊長,反派;kh→哈)
- 阿濟莎 — Aziza(相助的女術士;عزيزة)
- 茱拉娜爾 — Julanar(化為樹的女子;一千零一夜 جلنار)
- 奧瑪爾 — Omar(說書人/盲眼詩人;عمر)
- 哈里克·阿塔爾 — Harik Attar(藥師/醫者;Attar 波斯姓 عطار)
- 埃米爾 — Emir(統治者頭銜);蘇丹 — Sultan
- 苦行僧 — Dervish(درويش)
- 拉基什 — Rakeesh(獅人聖騎士;QFG 自創,維持原音)
- 烏胡拉 — Uhura(獅人女戰士;QFG 自創)
- 伊瑞娜 — Erana(已逝善良女法師,非阿拉伯角色,維持原音)
- 伊拉斯謨 — Erasmus(QFG1 巫師)
- 費拉里夫人 — Signora Ferrari(義大利裔地下勢力,保留義式譯名)

## 待補(M2 抽字後定版)

- W.I.T. (Wizards' Institute of Technocery) → 巫師技術學院(暫,縮寫可保留 W.I.T.)
- E.O.F. (Eternal Order of Fighters) → 永恆戰士團(暫)
- Keapon Laffin 等諧音名:阿拉伯風下傾向音譯,趣味性以對白補。
- 屬性/技能名(力量/智力/敏捷/火鏢/取物…)待 M2 抽出完整清單後補齊。
