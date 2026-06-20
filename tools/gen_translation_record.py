#!/usr/bin/env python3
"""從 tools/translation.tsv 生成 translation/ 雙語典藏記錄(中英對照,經典流傳)。"""
import os
pairs = []
for line in open('tools/translation.tsv', encoding='utf-8'):
    line = line.rstrip('\n')
    if not line or line.startswith('#') or '\t' not in line:
        continue
    en, zh = line.split('\t', 1)
    pairs.append((en, zh))
pairs = sorted(set(pairs), key=lambda p: p[0].lower())
os.makedirs('translation', exist_ok=True)

with open('translation/qfg2-cht.tsv', 'w', encoding='utf-8') as f:
    f.write("# 英雄傳奇II:烈火試煉 — 英↔繁中 對照典藏\n")
    f.write("# English<TAB>繁體中文  /  共 %d 條\n" % len(pairs))
    for en, zh in pairs:
        f.write(f"{en}\t{zh}\n")

def esc(s):
    return s.replace('|', '\\|').replace('[[', '　').replace('[', '　')[:90]

with open('translation/README.md', 'w', encoding='utf-8') as f:
    f.write("# 英雄傳奇 II:烈火試煉 — 中英對照翻譯典藏\n\n")
    f.write("> Quest for Glory II: Trial by Fire — English ↔ Traditional Chinese translation record.\n")
    f.write("> 這份檔案完整記錄本專案的繁中化譯文,中英對照,作為經典流傳。\n\n")
    f.write(f"**目前收錄:{len(pairs)} 條**(持續增補中,語料總量約 2350 句)。\n\n")
    f.write("- 正式對照檔:[`qfg2-cht.tsv`](qfg2-cht.tsv)(`English<TAB>繁體中文`)\n")
    f.write("- 語感參照 1990 年代《軟體世界》三大誌攻略;專名走阿拉伯/波斯風音譯(見 [`../CONTEXT.md`](../CONTEXT.md))。\n")
    f.write("- 授權:譯文以 CC BY-NC-SA 釋出;英文原文版權屬原作者(Sierra / AGD Interactive)。\n\n")
    f.write("## 譯文摘錄\n\n| English | 繁體中文 |\n|---|---|\n")
    for en, zh in pairs[:60]:
        f.write(f"| {esc(en)} | {esc(zh)} |\n")
print(f"典藏記錄已生成:{len(pairs)} 條 → translation/")
