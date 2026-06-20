# 主線劇情翻譯批次:以唯一子串比對語料取「精確 key」,配繁中譯文。
# 譯名遵循 CONTEXT.md(阿拉伯/波斯風)。
import sys
corpus = [l.rstrip('\n') for l in open('build/corpus_clean.txt', encoding='utf-8')]

# {唯一辨識子串: 繁體中文譯文}  ([[ 為 AGS 換行,譯文保留)
BATCH = {
 "ancient prophecy, when Raseir fell into darkness":
   "根據一則古老的預言,當拉希爾陷入黑暗之時,一位來自北方的英雄將會降臨,為這座城市重新帶來光明。",
 "Ad Avis is intent on raising Iblis":
   "阿德·阿維斯一心想要喚醒伊布利斯。",
 "Ad Avis stands, glaring sternly, his black robes":
   "阿德·阿維斯佇立著,目光森冷,黑袍在風中翻飛。",
 "Although few see the Sultan, he sees all":
   "雖然鮮少有人見過蘇丹,他卻洞悉一切。夏皮爾城中的每一個人、每一件事,都逃不過蘇丹的眼睛。",
 "A Raseirian guard patrols this section of the city":
   "一名拉希爾衛兵在這一帶的城區巡邏。",
 "A strong aura of magic radiates from the Water Elemental":
   "水元素精靈散發出強烈的魔法氣息。你懷疑這頭生物遠不如外表看來那般無害。",
 "An Air Elemental grows in power the more it blows":
   "風元素精靈颳得越猛,力量就越強大。",
 "A Water Elemental in the fountain of town would be the greatest of misfortunes":
   "若讓水元素精靈進入城中的噴泉,將是天大的災禍。",
 "As you have discovered, incense is quite a lure for Fire Elementals":
   "正如你所發現的,薰香對火元素精靈頗具吸引力。",
 "A powerful aura of dark magic radiates from the Air Elemental":
   "風元素精靈散發出強大的黑暗魔法氣息。",
 "All you have to do is to throw it at the Earth Elemental":
   "你只需把它擲向土元素精靈即可。它爆炸時會綻放出美麗的火花。",
 "As you listen through the keyhole, you hear the regular goings on of Shapeirian life":
   "你透過鑰匙孔聆聽,聽見夏皮爾市井生活的尋常聲響。",
 "A business owner's sign hangs overhead":
   "一面店家的招牌懸在頭頂上方。",
 "A caravan is many travelers journeying together. It is much less dangerous that way":
   "商隊是許多旅人結伴同行。如此一來危險便少了許多。",
 "A barrel full of animal entrails. Lovely":
   "一桶滿滿的動物內臟。真「可愛」。",
}

# 解析:每個子串找到唯一對應的完整原文行
resolved=[]
for sub, zh in BATCH.items():
    hits=[c for c in corpus if sub in c]
    if len(hits)==1:
        resolved.append((hits[0], zh))
    else:
        print(f"  ⚠ 子串命中 {len(hits)} 筆,跳過: {sub[:40]}", file=sys.stderr)

# 既有 disclaimer + 標題保留(從現有 tsv 讀回前兩條非註解)
existing=[]
for line in open('tools/translation.tsv', encoding='utf-8'):
    line=line.rstrip('\n')
    if line and not line.startswith('#') and '\t' in line:
        existing.append(tuple(line.split('\t',1)))

seen=set()
with open('tools/translation.tsv','w',encoding='utf-8') as f:
    f.write("# 英雄傳奇II 繁中翻譯  英文原文<TAB>繁體中文  (譯名見 CONTEXT.md)\n")
    for s,d in existing + resolved:
        if s in seen: continue
        seen.add(s); f.write(f"{s}\t{d}\n")
print(f"翻譯總計 {len(seen)} 條(既有 {len(existing)} + 主線批次 {len(resolved)})")
