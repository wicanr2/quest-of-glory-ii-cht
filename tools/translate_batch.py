# 主線劇情翻譯批次:以唯一子串比對語料取「精確 key」,配繁中譯文。
# 語感:參照《軟體世界》三大誌生動口語;專名走 CONTEXT.md 阿拉伯/波斯風音譯。
# 角色語域:Uhura 講 pidgin → 中文略簡略粗獷;Effendi → 敬稱「閣下」。
import sys
corpus = [l.rstrip('\n') for l in open('build/corpus_clean.txt', encoding='utf-8')]

# {唯一辨識子串: 繁體中文譯文}  ([[ = AGS 換行,保留)
BATCH = {
 # --- 開場 / 系統 ---
 "ancient prophecy, when Raseir fell into darkness":
   "古老的預言有云:當拉希爾墮入黑暗,北方終將有一位英雄前來,為這座城市重燃光明。",
 # --- 反派 Ad Avis / 伊布利斯 ---
 "Ad Avis is intent on raising Iblis":
   "阿德·阿維斯一心要喚醒伊布利斯。",
 "Ad Avis stands, glaring sternly, his black robes":
   "阿德·阿維斯佇立著,目光森冷,一襲黑袍在風中獵獵翻飛。",
 # --- 蘇丹 / 城市 ---
 "Although few see the Sultan, he sees all":
   "蘇丹深居簡出,卻洞燭一切。夏皮爾城裡的每一個人、每一樁事,都瞞不過他的眼睛。",
 "A Raseirian guard patrols this section of the city":
   "一名拉希爾衛兵在這一帶巡邏。",
 "As you listen through the keyhole, you hear the regular goings on of Shapeirian life":
   "你貼著鑰匙孔聽,夏皮爾市井的尋常喧鬧一一傳入耳中。",
 "A business owner's sign hangs overhead":
   "一面店家招牌懸在頭頂上。",
 "A caravan is many travelers journeying together. It is much less dangerous that way":
   "所謂商隊,就是一大群旅人結伴上路——這樣一來,危險可就少多了。",
 "A barrel full of animal entrails. Lovely":
   "一整桶的動物內臟。真是「賞心悅目」。",
 # --- 四大元素精靈 ---
 "A strong aura of magic radiates from the Water Elemental":
   "水元素精靈渾身散發著濃烈的魔法氣息。你直覺這傢伙絕不像外表那般人畜無害。",
 "An Air Elemental grows in power the more it blows":
   "風元素精靈颳得越狂,力量就越驚人。",
 "A Water Elemental in the fountain of town would be the greatest of misfortunes":
   "要是讓水元素精靈鑽進城裡的噴泉,那可就是天大的災難了。",
 "As you have discovered, incense is quite a lure for Fire Elementals":
   "你已經發現:薰香對火元素精靈很有吸引力。",
 "A powerful aura of dark magic radiates from the Air Elemental":
   "風元素精靈散發出強大的黑暗魔法氣息。",
 "All you have to do is to throw it at the Earth Elemental":
   "你只管把它往土元素精靈身上一扔就成。它炸開時,那火花可漂亮得很。",
 # --- 商人介紹(自然口語)---
 "It is Tashtari, the lamp merchant":
   "這位是塔什塔里,賣燈的商人。",
 "It is Ugarte, the water smuggler":
   "這位是烏加特,走私水的販子。",
 "It is Saba, the basket merchant":
   "這位是薩巴,賣籃子的商人。",
 "It is Lasham, the plant merchant":
   "這位是拉珊,賣花草的商人。",
 "It is Khaveen, captain of the Raseirian Guard":
   "這位是哈維因,拉希爾衛隊的隊長。",
 # --- 敬語 NPC(Effendi → 閣下)---
 "It is my honor to aid you, Effendi":
   "能為您效勞,是小的的榮幸,閣下。",
 "It is I who owe you my humble thanks, Effendi":
   "該道謝的是小的才對,閣下。",
 "It is always a pleasure to see you, great Hero":
   "能見到您,永遠是一件樂事,偉大的英雄。",
 # --- 物品 / 場景描述 ---
 "It is an ordinary, slightly rusty nail":
   "一根普通的釘子,還有點生鏽。",
 "It is a small clay pot, filled with dirt":
   "一只小陶罐,裡頭裝滿了泥土。",
 "It is dark beyond the open doorway":
   "敞開的門後一片漆黑。",
 "It is the reflection of your lamp light":
   "那是你燈火的倒影。",
 "It is hard to be a hero in the bottom of a dungeon":
   "困在地牢底下,英雄也難當啊。",
 "It is beyond repair":
   "已經修不好了。",
 "It is something you will never forget":
   "這是你一輩子都忘不了的經歷。",
 # --- 冒險者公會 / 戰鬥導師 Uhura(pidgin → 簡略粗獷)---
 "I am sorry, but Uhura is the Guildmaster and combat instructor here":
   "抱歉,烏胡拉是這兒的公會會長兼格鬥教官。我一般是不跟訪客過招的。",
 "Maybe you do not hear so good. I be thinking you give me back Rakeesh's sword":
   "你耳朵不大靈光吧?我看哪,你最好把拉基什的劍還來,不然我可要發大火了。",
 "If you be willing to know more about swordsmanship, talk to Rakeesh":
   "你要是想多學點劍術,就去找拉基什。我們還是娃娃的時候,他就已經會耍劍了。",
 "Don't stand over Uhura when she flips back to her feet":
   "烏胡拉翻身站起時,別站在她正上方——她會冷不防反擊,把局面整個翻過來。",
 # --- 問候 ---
 "Farewell, young adventurer. We shall speak again soon":
   "再會了,年輕的冒險者。我們很快會再聊的,這點毋庸置疑。",
 "Good day. I hope you are well, young adventurer":
   "你好。願你一切安好,年輕的冒險者。",
 "Obviously a graduate of the Famous Adventurers' Correspondence School":
   "一看就是「著名冒險家函授學校」的高材生。",
 # --- 第二批:系統 / 對白 / 戰鬥 ---
 "Nothing you can say will mend the broken pot":
   "破罐子難補,你再怎麼說好話也沒用。",
 "Perhaps the carpet ride into the city was a bit much for you":
   "乘魔毯進城,對你來說是不是有點吃不消啊,英雄?",
 "Perhaps you should dismount first":
   "或許你該先下坐騎。",
 "Perhaps you should learn more about who sent you before you seek me":
   "在來找我之前,你或許該先弄清楚究竟是誰派你來的。",
 "Perhaps there is more a brain about you than I suspected":
   "看來你腦袋比我想的還要靈光些。",
 "That doesn't make you look very sexy":
   "這可不怎麼讓你顯得有魅力。",
 "That doesn't seem to affect the living flames of the Elemental":
   "這對元素精靈那活生生的火焰,似乎起不了作用。",
 "That file already exists. Please pick another name":
   "這個檔名已經有了,請另取一個。",
 "That is a most valuable item you have there":
   "你手上那玩意兒,可是件稀世珍寶啊。",
 "That is most kind of you. We love treats like these":
   "您真是太客氣了。我們最愛這種好東西了。",
 "That is indeed a sad tale. Let me show you of that which we speak":
   "這的確是個令人傷感的故事。讓我把我們所說的指給你看吧。",
 "That person isn't interested in the item you offer":
   "那人對你拿出來的東西不感興趣。",
 "That Saurus doesn't belong to you":
   "那頭索魯斯可不是你的。",
 "A potion to break enchantments? I know of one in which the victim drinks the potion and the spell ends":
   "破除魔咒的藥水?我聽過一種——只要中咒的人喝下去,法術便會解除。",
 "Aziza's pawn isn't a valid target for that spell":
   "阿姿莎的棋子不能當這個法術的目標。",
 "Casting spells when guards are around is not the wisest course of action":
   "衛兵就在旁邊還施法,可不是什麼高明的舉動。",
 "Don't fight them tonight":
   "今晚別跟他們動手!",
 "For some reason, your mind can't seem to focus enough to cast that spell":
   "不知怎地,你心神無法集中,施展不出那個法術。",
 "Furthermore, an overhead slash can be used to knock an enemy to the ground":
   "此外,由上而下的劈砍能把敵人擊倒在地,還能避開對方迅捷的反擊。",
 "Get the hell out of dodge? Not you":
   "腳底抹油、溜之大吉?那可不是你的作風!",
 "Good sword. Good fight. There be many proud of you":
   "好劍法。好身手。會有不少人以你為榮的。",
 "Maybe you find work for hero here, too":
   "說不定這兒也有適合英雄幹的活兒。",
 # --- 第三批:場景描述 / 問候 / 互動 ---
 "You would try the patience of a dervish! Do something":
   "你連苦行僧的耐性都要磨光了!倒是做點什麼啊!",
 "A beautifully ornate window adorns this area of the wall":
   "牆上這一處鑲著一扇華美雕飾的窗。",
 "A decorative basket adorns the alley":
   "一只裝飾用的籃子點綴著巷子。",
 "A delicately crafted jar of copper and bronze":
   "一只以紅銅與青銅精工打造的罐子。",
 "A derelict window hangs unevenly from its battered frame":
   "一扇破窗歪斜地掛在殘破的窗框上。",
 "A discarded barrel rests nearby. The wood shows heavy signs of rot":
   "附近擱著一只廢棄的木桶,木頭已嚴重腐朽。",
 "A eunuch patrols the parapet":
   "一名宦官在城垛上巡邏。",
 "A feeling of peace and tranquility permeates the area":
   "一股祥和寧靜的氣息瀰漫此地。",
 "A ghastly moan is all you hear from the other side of the door":
   "門的另一側,你只聽見一聲淒厲的呻吟。",
 "A handshake wouldn't do much to change this guy's bad attitude":
   "光握個手,可改變不了這傢伙的臭脾氣。",
 "A large iron grate blocks further passage in this direction":
   "一道巨大的鐵柵欄擋住了這個方向的去路。",
 "A most interesting tale":
   "真是個有意思的故事。",
 "A most prudent decision upon your part":
   "你這決定下得真是明智。",
 "An Acme Lock Pick, suitable for most standard locks and a few squirrely ones":
   "一把「頂尖牌」開鎖器,應付大多數標準鎖綽綽有餘,連幾種刁鑽的也難不倒它。",
 "A pile of heavy wooden crates has been stacked here":
   "這裡堆著一疊沉重的木箱。",
 "A pity we couldn't make an exchange. Perhaps some other time":
   "真可惜,這筆買賣沒談成。那就改日再說吧。",
 "A quick glance at the skyline tells you how much in decline the city is":
   "只消瞄一眼天際線,你便知道這座城市已沒落到何種地步。",
 "A simple yes or no will suffice":
   "答個「要」或「不要」就行了。",
 "A square, flat box lies discarded among the trash":
   "一只方扁的盒子被丟棄在垃圾堆裡。",
 "A strange sort of person, even for a human":
   "真是個怪人——即便以人類的標準來看也一樣。",
 "A topiary expert, you are not":
   "修剪花木的高手,你肯定不是。",
 "A wise choice. I dislike a man who doesn't drink":
   "明智之選。我可不喜歡滴酒不沾的男人。",
 "Greetings, Effendi. Could you spare some alms for one who is not so fortunate":
   "您好,閣下。能否施捨些錢財,給我這不幸之人?",
 "Greetings, friend of the Katta. Perhaps we should look for a way out of here":
   "你好,卡塔族的朋友。或許我們該找條路離開這兒!",
 "Greetings, Hero. Do you wish to engage in another wager with me":
   "你好,英雄。想再跟我賭一把嗎?",
 "Greetings, Hero. I am glad you have come to my aid":
   "你好,英雄。你能來相助,我很欣慰。",
 "Greetings, nimble one. The crowd seems very pleased with your achievement":
   "你好,身手敏捷的傢伙。群眾似乎對你的本事很是滿意。",
 "He doesn't appreciate being looked down upon. Why don't you dismount first":
   "他可不喜歡被人居高臨下地看著。你何不先下坐騎?",
 "He doesn't seem to have any useful items left in stock":
   "他似乎沒剩什麼有用的貨了。",
 "He is one of the local guards":
   "他是本地的衛兵之一。",
 "Hello! Bone jar! Hi, guy! Set a spell, take your shoes off! What may I do to you":
   "哈囉!笨豬有!嗨呀老兄!坐下歇會兒,把鞋脫了吧!有啥能「效勞」你的?",
 # --- 第四批:對白 / 劇情 / 物品 / 戰鬥 ---
 "go the door at the end of 'Askeri Darb,' off 'Saif Darb.' Obey, or you'll regret it":
   "今晚入夜後,去『Saif Darb』岔出的『Askeri Darb』盡頭那扇門。乖乖照辦,否則你會後悔。",
 "Alas, my heart is broken":
   "唉,我的心都碎了。",
 "Ask for a sign another time":
   "改天再來求籤吧。",
 "By golly, it is! There's a silver lining on the underside of Keapon's cloud":
   "我的天,還真是!姬朋這朵烏雲底下,總算透出一線光明。",
 "Don't expect any cutting replies":
   "別指望聽到什麼犀利的回嘴。",
 "For some reason the item seems stuck in your pocket. It appears you have only your magic skills to rely upon here":
   "不知怎地,那件東西像黏在口袋裡似的。看來在這兒,你只能靠魔法了。",
 "Good. I hate to part with it unless there is a very good cause":
   "很好。要不是有天大的理由,我可捨不得割愛。",
 "Hello, Master. You still have one wish left":
   "您好,主人。您還剩一個願望。",
 "I already gave you the bellows, remember":
   "我風箱已經給你啦,記得吧?",
 "I believe, O Hero, that for you I have a pin":
   "英雄啊,我想我這兒有根別針正合你用。",
 "I know only that it is something to be greatly feared":
   "我只知道,那是個極其可怕的東西。",
 "I will need a Griffin's feather. You must add the hair of the victim yourself at the last moment. It must be fresh":
   "我需要一根獅鷲的羽毛。受害者的頭髮得由你在最後一刻親手加進去,而且必須是新鮮的。",
 "If you be tired, we go back to Main Hall. Much more comfortable there":
   "你要是累了,咱們就回大廳去。那兒舒服多了。",
 "Issur's bellows really blow up a storm with the Air Elemental inside":
   "把風元素精靈關進去,伊蘇的風箱當真能颳起一場風暴。",
 "It is my honor, Effendi":
   "這是小的的榮幸,閣下。",
 "It will flame for the battle only, for it draws its strength from mine":
   "它只在戰鬥時燃燒,因為它的力量取自於我。",
 "It's an exotic potted plant":
   "一盆奇特的盆栽。",
 "It's the city of Shapeir inside a glass dome. When the dome is shaken, a sand storm envelops the city":
   "玻璃罩裡是夏皮爾城。一搖那罩子,沙暴便籠罩全城。",
 "Khaveen is anxiously pacing back and forth across the hall":
   "哈維因正焦躁地在大廳裡來回踱步。",
 "May thee be granted a happy evening, Effendi":
   "願您有個愉快的夜晚,閣下。",
 "My name is Larisha":
   "我叫拉莉莎。",
 "Nevertheless, shall we make a deal at forty dinars":
   "不過呢,四十第納爾,這筆買賣成交如何?",
 "Now, please excuse me. I really must get back to my work":
   "好了,失陪了。我真的得回去幹活兒了。",
 "Our fellow Katta promised they would send us support and aid whenever we were in need":
   "我們卡塔族的同胞答應過,只要我們有需要,必定伸出援手。",
 "Please leave the sword with Uhura in the Guild Hall when you are done with it":
   "用完那把劍,請交還給公會大廳的烏胡拉。",
 "Rakeesh's sword arm and reflexes be very quick. Don't be surprised if your attacks miss":
   "拉基什的劍臂和反應都快得很。你的攻擊要是常常落空,可別意外。",
 "Shema just gave you these clothes. It'd be rude to discard them right in front of her":
   "雪瑪才剛把這身衣裳送你,當著她的面丟掉可太失禮了。",
 "Sorry, Chief. With your spell collection this incomplete, you'll only meet with quick defeat":
   "抱歉啦,老大。你這法術學得七零八落,上去也只是速速吃敗仗。",
 "Thank you for the kindness you have shown Julanar. You are a true hero for helping her":
   "謝謝你對茱拉娜爾的善意。肯幫她,你是個真正的英雄。",
 "That would have no effect on the Air Elemental":
   "這對風元素精靈起不了作用。",
 "The Earth Elemental crushes everything in its path":
   "土元素精靈會輾碎一切擋路之物。",
 "The Liontaur is carefully looking you over, almost as if he's analyzing you":
   "那獅人仔細地打量著你,簡直像在分析你似的。",
 "The bag feels pretty heavy and is obviously filled with plenty of coins":
   "這袋子沉甸甸的,顯然裝滿了錢幣。",
 "The crash of boulder upon boulder echoes through the cavern":
   "巨石撞擊巨石的轟響在洞穴中迴盪。",
 "The grate, while damaged and rusty, is still solid enough to withstand your attempts at opening it":
   "那鐵柵雖然殘破生鏽,卻仍夠堅固,任你怎麼弄都打不開。",
 "The magic rope you purchased from the Magic Shop looks like an ordinary rope":
   "你從魔法店買來的魔繩,看著跟普通繩子沒兩樣,只是盤得更緊、也更輕。",
 "The pill makes you thirsty, so you take out your waterskin":
   "藥丸讓你口渴,於是你取出了水袋。",
 "The shop has closed for the night":
   "店家已經打烊了。",
 "The thick layer of dust in this merchant stall suggests it hasn't been used in a long time":
   "這攤位上積了厚厚一層灰,看來已經很久沒人用了。",
 "The wooden door's latch seems to be stuck. It doesn't respond":
   "木門的門閂似乎卡住了,毫無反應。",
 "There is nothing left in the box":
   "盒子裡什麼也不剩了。",
 "There's nobody around to talk to":
   "附近沒有人可以攀談。",
 "This constellation is said to resemble a Saurus":
   "據說這個星座的形狀像一頭索魯斯。",
 "Those guards are well-paid to ignore my friends":
   "那些衛兵收了好處,專門對我的朋友睜一隻眼閉一隻眼。",
 "Utilize the skull-splitter on opponents who use low attacks to quickly end the battle":
   "對付慣使下盤攻擊的對手,用「劈顱式」能速戰速決、占得上風。",
 "Well, young Jackal, may fortune always favor you":
   "好啦,小豺狼,願好運永遠眷顧你。",
 "Who do you call upon to be your sponsor and mentor in these hallowed halls of the Wizard's Institute of Technocery":
   "在這巫師技術學院的神聖殿堂裡,你要請誰當你的引薦人與導師?",
 "You are suddenly, forcefully reminded that \"It isn't the fall that hurts; it's when you hit the ground.\"":
   "你猛地、狠狠地體會到一句話:「摔下來不疼,著地那一下才要命。」",
 "You can now pick (on) locks your own size":
   "現在你可以開(捉弄)跟你差不多大的鎖了!",
 "You can't see a thing. It's too dark":
   "你什麼也看不見,太暗了。",
 "You describe to Zayishah how the Emir was transformed into a Saurus":
   "你向札伊莎描述埃米爾如何被變成了一頭索魯斯,如今正由阿姿莎照料著。",
 "You don't have a use for any of the pots on display":
   "陳列的這些罐子,你都用不上。",
 "You drop the basket into the storage chest":
   "你把籃子放進儲物箱。",
 "You have not answered my question. Who are you that knocks upon my door":
   "你還沒回答我的問題。敲我門的,究竟是何人?",
 "You look at the dangerous-looking guard and think better of it":
   "你看了看那一臉兇相的衛兵,還是打消了念頭。",
 "You really ought to prepare for the departing caravan, Hero":
   "英雄,你真該為即將啟程的商隊做準備了。",
 "You return the reward to Rakeesh and tell him that the city being safe again is enough":
   "你把酬勞退還給拉基什,告訴他城市重歸安寧,這份回報就已足夠。",
 "You should sit down first if you wish to speak with Abdulla":
   "你若想跟阿布杜拉說話,得先坐下。",
 "You still don't have the skill, Phil, so I'll spare you the bill":
   "你火候還不到啊老兄,這筆帳我就先不跟你算清。",
 "You take a careful sip from your waterskin. It tastes great":
   "你小心地就著水袋啜了一口,味道好極了。",
 "You tell the Katta about your friendship with his cousin Shema":
   "你向這位卡塔族人說起你和他表親雪瑪的交情。",
 "You'd just get fingerprints all over it":
   "你只會在上頭按得到處都是指紋!",
 # --- 第五批:對白 / 商店 / 戰鬥 / 物品 ---
 "Alas, you will need to visit the Moneychanger before you can buy anything here":
   "唉,你得先去找錢莊兌換,才買得起這兒的東西。",
 "Aziza does not want anything from you":
   "阿姿莎不需要你任何東西。",
 "Certainly you do not wish for more to eat":
   "你肯定不想再吃了吧!",
 "Don't try to interrupt Uhura's chain of attacks by dodging the first blow and attacking in between":
   "別想著閃過烏胡拉的第一擊、再趁隙還手來打斷她的連段——那行不通。",
 "For you, it will take a mere 18 dinars to loosen my lips":
   "看在你的份上,區區十八第納爾,我這嘴就鬆了。",
 "Greetings, Hero. Do you feel brave and lucky today? Nobody else around here seems willing to take my challenge":
   "你好,英雄。今天覺得自己又勇又走運嗎?這附近可沒人敢接我的挑戰。",
 "Hello, Master. You still have two wishes left":
   "您好,主人。您還剩兩個願望。",
 "I am always glad to be of assistance":
   "能幫上忙,我向來樂意。",
 "I confess I am a bit disappointed in you, sir. It seems I expected too much":
   "老實說,我對你有點失望,先生。看來是我期望太高了。",
 "I love a man who likes to keep in shape":
   "我就喜歡懂得鍛鍊身材的男人。",
 "I wish I had as much time to waste as you do":
   "真希望我也有你這麼多時間可以揮霍。",
 "If you know not whom you seek, you will surely not find that person here":
   "你若連自己要找誰都不知道,在這兒是絕對找不著那人的。",
 "It doesn't look like it would make a very suitable mount":
   "看起來不太適合拿來當坐騎。",
 "It is the finest suit of mail in all the realm. Its value is far beyond you":
   "這是全國最上乘的一副鎖子甲,它的價值遠非你所能企及。",
 "It would be impolite to disturb the Katta musician while he's playing":
   "卡塔族樂師正在演奏,打擾他可不禮貌。",
 "It's empty. This is a good thing as eating leftover scraps would be a very bad idea":
   "空的。這是好事,畢竟吃別人的剩菜殘羹可不是什麼好主意。",
 "It's too dark to see what you're dropping. You'd better not drop anything until you can see properly":
   "太暗了,看不清你要丟什麼。等看得清楚再丟吧。",
 "Lamb falafels and soured cream, along with a rabbit curry, are part of the meal for tonight":
   "今晚的菜色有羊肉炸豆丸佐酸奶,還有一道兔肉咖哩。願它讓你吃得舒坦。",
 "Maybe today you and I get in some practice at fighting. It will be good to feel the spear in my hand again":
   "或許今天你我可以切磋切磋。能再次握握長矛的手感,挺不錯的。",
 "My name is Sashari":
   "我叫薩沙莉。",
 "No response. The residence is either abandoned or the occupant is unwilling to answer you":
   "沒有回應。這宅子若不是早已荒廢,就是裡頭的人不願搭理你。",
 "Oh, it is so good to know my uncle is still alive. He is such a kind and friendly man":
   "啊,得知我叔叔還活著,真是太好了。他是個多麼和善親切的人。",
 "Please, you must sit down and relax before we shall speak of what you seek":
   "來,你得先坐下放鬆,我們再來談你所求之事。",
 "Scoree is the local food merchant":
   "斯科里是本地的食品商。",
 "Since it's forbidden to be out at night, the torches in this city don't seem to have a practical use anymore":
   "既然夜裡禁止外出,這城裡的火把似乎也派不上用場了。",
 "Success! You now have an open nose":
   "成功!你的鼻子現在「暢通無阻」了。",
 "That's one way of getting more fiber in your diet":
   "這倒是替三餐多添點膳食纖維的法子。",
 "The Griffin looks like a cross between a lion and an eagle. It seems to be sleeping":
   "那獅鷲長得像獅子和老鷹的混血,似乎正在熟睡。",
 "The Saurus seems curious and excited":
   "那頭索魯斯顯得既好奇又興奮。",
 "The bellows are a sign of my trade. What about them":
   "風箱是我這行當的招牌。問它做什麼?",
 "The door is locked and barred from within. Your Open spell has no effect":
   "門從裡頭上了鎖、閂得死死的。你的「開啟」術毫無作用。",
 "The money you find there should be more than enough to compensate the price of this little bit of information":
   "你在那兒找到的錢,拿來付這一小條消息的費用,綽綽有餘。",
 "The rings I sell are perfect when you wish to propose to your significant other":
   "我賣的這些戒指,拿來向心上人求婚再合適不過了。",
 "The still, small voice within this ring must be that of a Djinni -- a very weak one":
   "這戒指裡那細微的低語,想必是個鎮尼——而且是非常孱弱的一個。",
 "The western section of the city is visible beyond the roofs of the nearby buildings":
   "越過附近屋頂,可以望見城市的西區。",
 "There is a strong sense of magic beyond the Palace walls":
   "宮牆之外,有一股濃烈的魔法氣息。",
 "There's no point in returning Soulforge before the Earth Elemental has been dispatched permanently":
   "在徹底了結土元素精靈之前,歸還鑄魂劍是沒有意義的。",
 "These traditional windows are square-shaped and have been built into the wall":
   "這些傳統樣式的窗子呈方形,嵌在牆裡。",
 "This is not a good place to practice your Levitate spell":
   "這裡可不是練「飄浮」術的好地方。",
 "This sign has deteriorated to a point where it is no longer even legible":
   "這招牌已殘破到連字都認不出來了。",
 "Ugarte and I are old friends":
   "烏加特和我是老交情了。",
 "When mounting an offense, an inverse swing can be used to follow up a swing for additional damage":
   "進攻時,可以接著一記反向揮砍,追加傷害。",
 "Without water, you would not survive even an hour in the desert":
   "沒有水,你在沙漠裡連一個鐘頭都撐不過。",
 "You are getting really thirsty":
   "你開始覺得非常口渴。",
 "You bet your life you've seen this guy before":
   "你敢拿性命打賭,你以前見過這傢伙。",
 "You can't get a good shot at Ad Avis from where you are":
   "從你現在的位置,瞄不準阿德·阿維斯。",
 "You could never catch the magical mass of swirling wind using just your hands":
   "光憑一雙手,你絕對抓不住那團旋轉的魔法旋風。",
 "You dispose of the incense":
   "你把薰香處理掉了。",
 "You drop a healing pill":
   "你掉了一顆治療藥丸。",
 "You drop the poisonous claws on the ground and grind them to powder with your heel":
   "你把毒爪丟在地上,用腳跟碾成了粉末。",
 "You get a small glass of tepid, stale-tasting water":
   "你拿到一小杯溫吞、走味的水。",
 "You have done all you can to weaken the spell on the tree":
   "削弱那棵樹上法術的事,你已盡力而為了。",
 "You hear the sound of silence from behind the door":
   "門後傳來的,是一片寂靜。",
 "You never need be hungry again":
   "你再也不必挨餓了!",
 "You retrieve the EOF badge from your chest":
   "你從箱子裡取出永恆戰士團的徽章。",
 "You seem to have hit a communication barrier here":
   "你在這兒似乎碰上了溝通的障礙。",
 "You spend an hour checking out the interior of the Apothecary and watching Harik work":
   "你花了一個鐘頭打量藥舖內部,看著哈里克幹活。",
 "You store the incense":
   "你把薰香收了起來。",
 "You tell Harik about the caged beast":
   "你把籠中那頭野獸的事告訴了哈里克。",
 "You will need the magic of a flaming sword to defeat the Earth Elemental":
   "你需要一把燃燒之劍的魔力,才能擊敗土元素精靈。",
 "You're not THAT desperate for a light":
   "你還沒淪落到「那麼」需要一點火光的地步。",
 # --- 第六批:對白 / 旁白 / 諧音 ---
 "Abdulla glances at you and looks a bit uncomfortable. Maybe you shouldn't be picking your nose in public":
   "阿布杜拉瞥了你一眼,神色有些不自在。也許你不該在大庭廣眾下挖鼻孔。",
 "A finely crafted jar of brass and copper. The surface is so shiny and smooth it almost acts like a mirror":
   "一只黃銅與紅銅精製的罐子,表面光亮平滑,幾乎能當鏡子照。",
 "After all we've been through to come to an agreement, and you have the nerve not to have enough money":
   "費了這麼大勁才談攏,你倒好,竟厚著臉皮說錢不夠。",
 "After an hour's rest, you feel better":
   "歇了一個鐘頭,你覺得好多了。",
 "After carefully squeezing the last drop of poison out of the tail, you drop it on the ground":
   "你小心地把尾巴裡最後一滴毒液擠乾,隨手扔在地上。",
 "After the hour of rest, you don't really feel better. In fact, your thirst is worse than ever":
   "歇了一個鐘頭,你並沒覺得好些。事實上,你比先前更渴了。",
 "After you, my friend. I will humbly follow":
   "您先請,朋友。我恭敬地跟在後頭。",
 "Ah, good day. I am busy as always, making up a batch of pills. If you need something, just let me know":
   "啊,你好。我一如往常地忙,正在調一批藥丸。有什麼需要,儘管說。",
 "Ah, I did not notice you come in":
   "啊,我沒注意到你進來。",
 "Ah, men... always coming and going. Always going and coming, and always too soon":
   "唉,男人哪……總是來來去去,去去來來,而且總是走得太早。",
 "Ah, then you are indeed a friend in a place where we both need friends. We need to escape from this prison":
   "啊,那麼在這你我都需要朋友的地方,你果真是個朋友。我們得逃出這座牢獄。",
 "Ah, true love at first sight. And what a sight for Saurus eyes":
   "啊,一見鍾情的真愛。這在索魯斯眼裡,可真是養眼哪。",
 "Alas, you are out of water":
   "唉,你的水喝光了。",
 "Ali Fakir said after you left that he had sold his last Saurus and must be going":
   "你走後,阿里·法基爾說他最後一頭索魯斯也賣掉了,該動身了。",
 "All you hear is a ringing in your own ears":
   "你只聽見自己耳中的嗡嗡聲。",
 "Always happy to be of service, Handsome":
   "隨時樂意效勞,帥哥。",
 "A mere week after Abdulla's arrival, another new face appeared in Spielburg":
   "阿布杜拉抵達不過一週,史畢柏格又出現了一張新面孔。",
 "Announcing that you are a thief would not be a good idea right now":
   "現在嚷嚷自己是個盜賊,可不是什麼好主意。",
 "Antidote pills to magically cure venomous stings and scratches":
   "解毒藥丸,能以魔法治癒毒螫與抓傷。",
 "Anything he says, ain't gonna be much":
   "他就算開口,也說不出什麼名堂。",
 "Are you saying you wish to help me weave baskets, Hero of the North":
   "你是說你想幫我編籃子嗎,北方來的英雄?",
 "Are you sure you want to quit":
   "你確定要離開嗎?",
 "As a favor for getting yourself busted, Jabbar first beat you senseless before cutting off your hand":
   "為「答謝」你害自己被逮,賈巴爾先把你打個半死,才剁了你的手。",
 "As I have said before, there is no room for amateurs in this city":
   "我說過了,這座城市容不下外行人。",
 "As it's getting late, you decide to return to the inn for the night":
   "天色已晚,你決定回客棧過夜。",
 "As you blow into the barrel, a white cloud of mold escapes into the air":
   "你往桶裡一吹,一團白色的黴菌粉塵散入空中。",
 "As you call out, you realize how silent the streets around you are":
   "你一出聲,才驚覺四周街道是何等寂靜。",
 "As you expected, the door is locked and bolted":
   "不出你所料,門上了鎖、還閂著。",
 "As you press your ear to the door, you hear the sound of solid wood":
   "你把耳朵貼上門,聽見的只是一片厚實木頭的悶響。",
 "As you search through your pouch, you discover that you have no more coins from Spielburg to exchange":
   "你翻遍錢囊,發現再也沒有史畢柏格的錢幣可換了。",
 "At any rate, I'm here to sell you a Saurus, and you're ready to buy it, right":
   "總之,我是來賣你一頭索魯斯的,你也準備好要買了,對吧?",
 "A. You don't. You get down off a duck":
   "答:你不「下」大象——鴨絨才是從鴨子身上拔的。",
 "Aziza would most likely be very offended if you tried to mount the enchanted Emir":
   "你要是想騎那位中了魔法的埃米爾,阿姿莎多半會大為光火。",
 "Bad idea. The sound of the coins being shifted into your own purse would surely alert the guards":
   "餿主意。錢幣落進你錢袋的聲響,準會驚動衛兵。",
 "Behind the locked door, you hear a family quarrel. Better not get involved":
   "上了鎖的門後傳來一陣家庭口角。還是別淌這渾水。",
 "Be it ever so humble, there's no face like Gnome's":
   "金窩銀窩,都不如地精的臉窩。",
 "Best of all, they can always find their way back to where they are stabled, so you need never get lost":
   "最妙的是,牠們總能自己找回棚廄,你再也不必擔心迷路。",
 "Better not. His bite is worse than his bark":
   "還是別了。這傢伙咬起人來可比叫得兇。",
 "Beyond the buildings to the south lies the great Shapeirian Desert":
   "南面建築之外,便是浩瀚的夏皮爾大沙漠。",
 "Beyond the door, all is deathly silent":
   "門後是一片死寂。",
 "Boy, did you look silly":
   "老天,你那模樣可真蠢!",
 "Bring it here, quickly. Give it to me":
   "快拿過來,給我!",
 "But sir, we have not yet done business. Surely what I have to tell you is worth five paltry dinars":
   "可是先生,咱們生意還沒談成呢。我要告訴你的,難道不值區區五枚第納爾?",
 "But, wait, perhaps Lasham, the plant merchant, might be able to assist you":
   "不過,等等——或許賣花草的商人拉珊幫得上你。",
 "CAUTION: Do not try this at home":
   "警告:請勿在家嘗試。",
 "Come over here and face me when you talk to me, wimp":
   "跟我說話就過來當面說,膽小鬼。",
 "Darkness will triumph unless you stop the last light":
   "除非你阻止最後一道光熄滅,否則黑暗終將得勝。",
 "Death sting: fatal without antidote":
   "致命螫刺:無解藥即致死",
 "Deflection is your new middle name":
   "「格擋」就是你的新外號!",
 "Discretion is your Friend":
   "謹慎是你的好朋友!",
 "And not a drop to drink":
   "卻沒有一滴水可喝。",
 "Carelessly tossing this gift aside wouldn't be very compassionate of you":
   "把這份禮物隨手一丟,可顯不出你的慈悲心腸。",
 "Better keep it. You're supposed to give it back, remember":
   "還是留著吧。你可是得歸還的,記得嗎?",
 "Beyond the buildings to the north lies the desert you recently crossed to get here":
   "北面建築之外,是你不久前橫越而來的沙漠。",
 # --- 第七批:對白 / 物品名 / 戰鬥標籤 / 諧音 ---
 "And I want to thank you for all the enjoyment you've taken out of it":
   "我還要謝謝你從中得到的那些樂子。",
 "As I said, I really could not give you the little bit that I have":
   "我說過了,我手頭這一點點,實在沒法給你。",
 "As you look the plants over, you realize that you don't have the time or place to keep a potted plant":
   "你把這些花草打量一番,意識到自己既沒時間、也沒地方養盆栽。",
 "As you search through your purse, you realize that you have no more coins to exchange":
   "你翻遍錢袋,發現再也沒有錢幣可兌換了。",
 "At this point, it is merely a sign of deterioration":
   "事到如今,這不過是衰敗的徵兆罷了。",
 "Back to the matter at hand. As a matter of fact, I was just selling you a Saurus, wasn't I":
   "言歸正傳。說真的,我剛才不正在賣你一頭索魯斯嗎?",
 "Bag with magic earth":
   "裝著魔法泥土的袋子",
 "Behind this door, you hear someone cursing about the series finale of The Sopranos":
   "這扇門後,有人正在咒罵《黑道家族》的大結局。",
 "Bellows with air element":
   "封著風元素的風箱",
 "Better hold on to your compass for a while":
   "這羅盤你還是先留著吧。",
 "Better not. You might not be able to get another one so easily":
   "還是別了。你未必能再輕易弄到一個。",
 "Booger like Truth. Man seeks it out, but knows not what to do with it when he gets it":
   "鼻屎好比真理。人人挖空心思去尋,真到手了卻又不知如何是好。",
 "Buon giorno! Good and tag! Buenas dias, Senor Caws. I haven't seen you in so long":
   "日安!勾的摸您!喔啦,烏鴉先生。好久不見啦。",
 "Debug: All locations added to map":
   "除錯:已將所有地點加入地圖。",
 "Does this mean you do not wish to buy my wares, Effendi":
   "閣下,這是說您不想買我的貨了?",
 "Do not give up. The creature may be durable, but it is not indestructible. Not yet":
   "別放棄。這生物或許耐打,卻並非不死之身——還沒到那地步。",
 "Do not trouble yourself with such actions":
   "您不必費這個事。",
 "Don't be such a Chatty Cathy. Get moving":
   "別這麼囉哩囉嗦的。動起來。",
 "Don't bother blowing away the dust. There are other ways to clean up this place":
   "別費勁去吹灰了。要清理這地方,另有別的法子。",
 "Don't bother trying to talk to Merv the Griffin":
   "別費勁跟葛里芬獸默夫搭話了。",
 "Don't bother trying to talk to the funny-lookin' dude":
   "別費勁跟那長相滑稽的傢伙搭話了。",
 "Don't bother trying to talk to this townsperson":
   "別費勁跟這位市民搭話了。",
 "Don't bother trying to talk to your Saurus":
   "別費勁跟你的索魯斯搭話了。",
 "Don't expect any slick replies":
   "別指望聽到什麼油嘴滑舌的回話。",
 "Don't waste any lines on it":
   "別在它身上浪費口舌了。",
 "Do you have a belly ache":
   "你肚子疼嗎?",
 "Do you mind if I'm smoke":
   "你介意我「化作」一縷煙嗎?",
 "Do you need one to capture the Fire Elemental? I can let you have this one":
   "你需要一個來捕捉火元素精靈嗎?這個可以讓給你。",
 "Do your clothes itch? A hero such as yourself should always carry a spare outfit, Effendi":
   "衣裳穿著發癢嗎?像您這樣的英雄,身上總該備一套換洗的,閣下。",
 "Do you suffer an allergic reaction to pollen, Effendi":
   "您對花粉過敏嗎,閣下?",
 "Drain: claws drain hp":
   "吸取:利爪吸取生命力",
 "Elsa could not have wished for a truer friend":
   "艾莎再也求不到比這更真心的朋友了。",
 "Enjoy the sights of Shapeir, O Hero":
   "英雄啊,好好欣賞夏皮爾的風光吧。",
 "Enough. You do not want to make me angry":
   "夠了。你可不會想惹我發火。",
 "Every day, the Astrologer thanks his lucky stars that he has lucky stars":
   "占星師每天都感謝他的幸運星,慶幸自己有幸運星可感謝。",
 "Every hero needs a break now and then":
   "再了不起的英雄,偶爾也得歇口氣。",
 "Everyone here keeps their doors tightly locked and bolted":
   "這兒家家戶戶都把門鎖得緊緊、閂得死死的。",
 "Falafel is pita bread stuffed with spicy roasted lamb. A hearty meal":
   "炸豆丸是夾了香烤辣羊肉的口袋餅,是頓紮實的好料。",
 "Farewell, Effendi. May you have a well-rounded day":
   "再會,閣下。願您有圓圓滿滿的一天。",
 "Farewell, Hero from the North":
   "再會,北方來的英雄。",
 "Farewell, Hero of my people":
   "再會,我族的英雄。",
 "Farewell. I never forget a face, but in your case I'll make an exception":
   "再會。我從不忘記任何一張臉——不過你這張,我願破例。",
 "Farewell is like your footwear: well-worn but to the point":
   "「再會」就像你那雙鞋:穿得舊了,倒也直截了當。",
 "Fenrus, when is a rat not a rat":
   "芬魯斯,老鼠什麼時候不是老鼠?",
 "File could not be created. Disk may be full":
   "無法建立檔案,磁碟可能已滿。",
 "Flowers are sweet, but I prefer diamonds to daisies any day":
   "花兒雖甜美,但要我選,我寧取鑽石,不要雛菊。",
 "Flowers seem to wilt quickly in the desert heat":
   "在沙漠的酷熱下,花兒似乎謝得特別快。",
 "Focus: fast mp recharge":
   "凝神:法力快速回復",
 "Forgive me, but I am not entirely familiar with the customs of humans":
   "請見諒,我對人類的習俗不甚熟悉。",
 "Forgive me, but I have no time for such a thing":
   "請見諒,我沒空理會這種事。",
 "Forgive me, Effendi. I am not worthy of your kindness":
   "請原諒我,閣下。我當不起您的善意。",
 "Do you mind if I'm smoke?":
   "你介意我「化作」一縷煙嗎?",
 "As you expected, the door is locked":
   "不出你所料,門鎖著。",
 # --- 第八批:對白 / 物品 / 戰鬥 / 諧音 / 系統 ---
 "Expect no cheap replies":
   "別指望聽到什麼廉價的回話。",
 "Expect no fancy replies":
   "別指望聽到什麼花俏的回話。",
 "From among the Griffin's feathers, you choose a nice-looking one and pluck it":
   "你從獅鷲的羽毛裡挑了一根好看的,把它拔了下來。",
 "From behind the door, you hear \"Zzzzzz...\"":
   "門後傳來「呼……呼……」的鼾聲。",
 "From the branches of Julanar, you have obtained the Fruit of Compassion":
   "你從茱拉娜爾的枝椏間,取得了慈悲之果。",
 "Game Logging is turned off":
   "遊戲記錄已關閉。",
 "Game Logging is turned on":
   "遊戲記錄已開啟。",
 "Get back on your feet first, Hero":
   "先站起來再說,英雄。",
 "Ghoul claws are horrible things to look at":
   "食屍鬼的爪子看著就讓人發毛。",
 "Give yourself a little room, Hero":
   "給自己留點空間,英雄。",
 "Goodbye? Of course a Saurus is a good buy! Don't leave. You haven't purchased one yet":
   "再見?那頭索魯斯當然「再划算不過」啦!別走嘛,你還沒買呢。",
 "Good day. A pleasant one for those such as myself who like the heat, although most humans might find it hot":
   "你好。對我這種愛熱的傢伙來說是個好天氣,雖說多數人類大概會嫌太熱。",
 "Good day, Hero of Spielburg. I hope you slept well":
   "你好,史畢柏格的英雄。希望你睡得安穩。",
 "Good luck, sir, and I do hope you are as skilled as I suspect":
   "祝你好運,先生。我真心希望你和我猜想的一樣有本事。",
 "Go to the east and then go south when you can. Follow the road and you be finding her":
   "往東走,能往南時就往南。沿著路走,你就會找著她。",
 "Griffins tend to nest near the mountains":
   "獅鷲多半在山邊築巢。",
 "Guards hate knife throwers":
   "衛兵痛恨擲刀的人",
 "Guards hate rock throwers":
   "衛兵痛恨擲石的人",
 "Habari, young adventurer. It is good to have your kind here":
   "你好(Habari),年輕的冒險者。有你這樣的人來,真好。",
 "Hagatha only wishes she knew about this cheat":
   "哈嘎莎要是知道有這個作弊碼,不知會多眼紅!",
 "Hail, fellow, well met! What da ya know, Joe":
   "幸會幸會,老兄!最近如何呀,老喬?",
 "Harik doesn't need the bellows. Besides, you may still need them":
   "哈里克用不著這風箱。再說,你說不定還用得上。",
 "Have a nice nap":
   "好好睡一覺吧。",
 "Ha! You think to win this campaign by slinging mud":
   "哈!你以為靠潑髒水就能贏下這一仗?",
 "Heavy iron bars cover the window. It makes the residence feel like a prison":
   "厚重的鐵條封住了窗,讓這宅子像座牢房。",
 "He just loves it when you talk dirt to him":
   "你跟他說泥巴的事,他可愛聽了。",
 "Hello, handsome. I love a man who knows how to properly address a woman":
   "你好,帥哥。我就喜歡懂得如何得體稱呼女士的男人。",
 "Hello, I must be going. An exit line if ever I heard one":
   "你好,我得走了。要說退場台詞,這可真是一句。",
 "He looks like a charming fellow":
   "他看起來是個討喜的傢伙。",
 "Here is lemon chicken with garlic and lamb stewed with herbs. Eat it in good health":
   "這是蒜香檸檬雞,還有香草燉羊肉。祝您吃得健健康康。",
 "Here is some of our wonderful tea":
   "這是我們上好的茶,請用。",
 "Here is your morning meal of warm bread and honeyed butter, fresh fruit, and tea, just as you prefer":
   "這是您的早餐:溫熱的麵包配蜜奶油、新鮮水果,還有茶,正合您的口味。",
 "Here you are. I just love intimate exchanges like this":
   "給你。我就愛這種親密的交流。",
 "Her house is the first door on the west, at the place where the road is blocked off":
   "她家是西邊第一扇門,就在路被封住的地方。",
 "Hero, please take care of yourself. I worry for you":
   "英雄,請保重自己。我為你擔心。",
 "Hero types don't do that sort of thing more than once":
   "英雄這種人,同樣的蠢事是不會做第二次的。",
 "Her shop is at the south end of Dinar Tarik":
   "她的店在 Dinar Tarik 的南端。",
 "He seems like such a nice man. You would really like to be able to help him":
   "他看起來是個大好人。你真希望自己能幫上他。",
 "He seems to have a sore throat. You get no reply":
   "他似乎喉嚨痛,沒有回應你。",
 "He smiles at you and you are reminded of a weasel. He speaks, and you think of snakes":
   "他朝你一笑,讓你想起黃鼠狼;他一開口,你又想到了蛇。",
 "He's participating in the Persian Golf tournament":
   "他正在參加波斯高爾夫球賽。",
 "He's probably carrying enough junk of his own already":
   "他自己身上大概已經背了夠多破爛了。",
 "He's too busy flexing to talk":
   "他忙著秀肌肉,沒空說話。",
 "Hey! What you think this is, a charity? You ain't gotta the money":
   "喂!你當這是在做慈善哪?你錢都不夠。",
 "Hey you! Come over here if you wanta buy something":
   "喂,你!想買東西就過來這兒!",
 "Highway to the danger zone":
   "通往危險地帶的快車道。",
 "His poetry is very good. I listen to him when he reads in the plaza":
   "他的詩寫得很好。他在廣場上吟詩時,我都會去聽。",
 "His rat friend seemed to get nervous whenever we got close to him":
   "每次我們一靠近他,他那隻老鼠朋友就顯得很緊張。",
 "Hmm... most interesting. The stars say nothing about you having a sudden illness. I'll have to look into that":
   "嗯……真有意思。星象裡可沒提到你會突然得病。我得好好查查。",
 "How do you do, adieu. Good night and don't let the bed bugs bite":
   "您好,再會。晚安,別讓臭蟲咬了!",
 "However, any other guard you meet will not be so discreet":
   "不過,你遇上的其他衛兵可就沒這麼通融了。",
 "How much would you like to drop":
   "你想丟下多少?",
 "How much would you like to store":
   "你想存放多少?",
 "I accept your challenge gladly, my friend":
   "我樂意接受你的挑戰,朋友。",
 "I am always out of Ghoul claws for my experiments. I will pay 15 dinars for the claws of a Ghoul":
   "我做實驗總缺食屍鬼的爪子。一對食屍鬼爪,我出十五第納爾。",
 "I am always out of Scorpion venom to make poison cure pills. I will pay 20 dinars for the tail of a Scorpion":
   "我做解毒藥丸總缺蠍毒。一條蠍尾,我出二十第納爾。",
 "I am an admirer of birds, you see":
   "你瞧,我是個愛鳥之人。",
 "I am called Gharib Ajib":
   "我叫加里布·阿吉布。",
 "I am called Sadik Isfahani":
   "我叫薩迪克·伊斯法罕尼。",
 "He looks like a charming fellow.":
   "他看起來是個討喜的傢伙。",
 # --- 第九批:阿拉伯人名 / 對白 / 起司諧音 / debug ---
 "From Harik you have obtained a quantity of the powder of burning":
   "你從哈里克那兒取得了一些燃燒之粉。",
 "General Room Info was dumped to 'alley.txt' file":
   "房間概況已匯出至 'alley.txt' 檔。",
 "General Room Info was dumped to 'desert.txt' file":
   "房間概況已匯出至 'desert.txt' 檔。",
 "General Room Info was dumped to 'general.txt' file":
   "房間概況已匯出至 'general.txt' 檔。",
 "Get back to your feet first, Hero":
   "先站穩了再說,英雄。",
 "Give yourself some room, Hero":
   "給自己留點餘地,英雄。",
 "Harik would not be pleased if you simply discarded it. You decide to keep the powder of burning":
   "你要是隨手把它丟了,哈里克可不會高興。你決定留著這燃燒之粉。",
 "Here is the meal you ordered. I hope you will enjoy it":
   "這是您點的餐,希望您吃得盡興。",
 "Hey! You don't have the money for this. What you think this is, a charity? Get some money or get lost":
   "喂!你這點錢可買不起。當這是做慈善哪?有錢再來,沒錢就走人。",
 "His shop is at the end of the Tarik of Stars":
   "他的店在「群星之街」(Tarik of Stars)的盡頭。",
 "I am happy you were able to grant her request in time and escape with your life":
   "我很高興你及時達成了她的心願,還保住了性命。",
 "I am having a special sale on my boots. All boots come with a free bottle of wax to polish them":
   "我的靴子正在特價,每雙都附贈一瓶擦靴蠟。",
 "I am here to serve you":
   "我在此為您效勞。",
 "I am honored to aid you":
   "能助您一臂之力,是我的榮幸。",
 "I am known as Jabbar bin Ma'amar":
   "人稱我賈巴爾·賓·馬阿瑪爾。",
 "I am known as Kuzay bin Bishr":
   "人稱我庫宰·賓·比什爾。",
 "I am sorry, but I do not practice much anymore":
   "抱歉,我已經很少練了。",
 "I am sorry, Hero, but I cannot afford to give away all of my wares, lest my family starve":
   "抱歉,英雄,我可不能把貨全送光,否則一家老小就要挨餓了。",
 "I am sorry, I can spare but the one waterskin, Hero":
   "抱歉,英雄,我只能勻出這一個水袋。",
 "I am sorry to hear that you could not help the creature in time. At least it is no longer suffering":
   "聽說你沒能及時救那生物,我很遺憾。至少牠不必再受苦了。",
 "I am trying to develop a pill which will protect against the effect of the claws of the Ghoul":
   "我正試著研發一種藥丸,用來抵禦食屍鬼爪子的效力。",
 "I beg you to be careful when you leave the inn today. The thing of fire grows ever more dangerous":
   "求你今天出客棧時務必小心。那團火焰之物越來越危險了。",
 "I believe I asked you a question, young man":
   "我記得我問了你一個問題,年輕人。",
 "I be needing no more Ghoul heads. If I be putting more on the wall, Simba get plenty frightened":
   "我不需要更多食屍鬼的頭了。再往牆上掛,辛巴會嚇得不輕。",
 "I be seeing you later":
   "回頭見啦。",
 "I cannot make the potion without all the ingredients":
   "材料不齊,我這藥水就調不成。",
 "I do not see strangers who come unbidden":
   "不請自來的生人,我概不接見。",
 "I don't have bellows anymore. Someone must have figured they needed them badly enough to steal them":
   "我沒風箱了。準是有人覺得非要不可,把它偷走了。",
 "I don't much like nosy little twerps":
   "我可不太喜歡愛管閒事的小屁孩。",
 "I fear, Hero, that if I gave away all my dirt then I would have none left with which to pot my plants":
   "英雄啊,我怕要是把泥土全送了,就沒剩半點來種我的花草了。",
 "If I may aid you by giving you some earth, I shall be more than happy to do so. Here, take this":
   "若能贈你些泥土聊表心意,我求之不得。來,拿去吧。",
 "If it is your wish, I will return it to Omar for you with your regards":
   "你若願意,我便替你把它連同問候一併還給奧瑪爾。",
 "If it's time to split...":
   "若是該「開溜」(分裂)的時候了……",
 "If it were larger, you could sit in the shade":
   "它若再大些,你還能坐在陰涼處。",
 "If the time is right, you're in a plight, you can get it across if you give it a toss. Burma Shave":
   "時機若對,你陷困境,輕輕一擲,便能解圍。——Burma Shave",
 "If this bag of cloth will but aid you, it shall be yours":
   "這只布袋若幫得上你,就歸你了!",
 "If weapons don't harm it, there's very little chance your fists will":
   "連武器都傷不了它,你那兩個拳頭就更別指望了。",
 "If you are caught, I will know nothing of your actions, of course":
   "你要是被逮,我對你的所作所為自然一概不知。",
 "If you can but walk from one end to the other, I will give you five dinars":
   "你只要能從這頭走到那頭,我就給你五第納爾。",
 "If you did that, you would be lost in the dark":
   "你要那麼做,就會迷失在黑暗裡。",
 "If you have no further need of me, sir, there are thirsty customers in need of my wares":
   "先生,您若沒別的吩咐,還有些口渴的客人等著買我的貨呢。",
 "If you keep doing that, I'm gonna stick something else up there":
   "你再這樣下去,我可要往那兒塞點別的東西了。",
 "If you need to know more about the future, visit me again when it arrives":
   "你若想多知道些未來的事,等未來到了,再來找我吧。",
 "If you return this to me, I will make you my right-hand man":
   "你若把這個還給我,我就讓你當我的左右手。",
 "If you want to clean up this town, start with your heroic task list first":
   "你想清理這座城?先從你那份英雄任務清單做起吧!",
 "If you want your spell to reach that spot, you should stand on the other side of the wall, Hero":
   "英雄,你若想讓法術打到那個位置,該站到牆的另一邊去。",
 "If you wish to know your fortune, I will need to know your guiding signs":
   "你若想知道自己的命運,我得先知道你的主宰星象。",
 "If you wish to talk, you should have the courtesy to sit down":
   "你若想談,好歹也該有點禮貌坐下來。",
 "I get my lamps from the brass seller at the bazaar":
   "我的燈是跟市集裡賣黃銅的進的。",
 "I grow impatient with your nonsense. Either find a way to make the moon obey you, or you will face my wrath":
   "我對你這些胡鬧已經不耐煩了。要嘛想辦法讓月亮聽你的,要嘛承受我的雷霆之怒!",
 "I guess I bleu it. I'd cheddar be gouda for awhile, right":
   "看來我「起司」(搞砸)了。我還是「乾酪」(乖乖)躲一陣子比較好,對吧?",
 "I have already given you a lamp, Hero. I fear that I cannot spare another":
   "英雄,我已經給過你一盞燈了。恐怕沒法再勻出一盞。",
 "I have been by her house on Sitt Tarik. It has an eye painted upon the door":
   "我去過她在 Sitt Tarik 的家,門上畫著一隻眼睛。",
 "I have been named Abd al-Malik":
   "我名叫阿卜杜勒-馬利克。",
 "I have been named al-Hajjaj":
   "我名叫哈賈吉。",
 "I have been named Badr Basim":
   "我名叫巴德爾·巴西姆。",
 # --- 第十批:商店/對白/諧音 ---
 "If the vine wasn't withering, that is":
   "前提是那藤蔓沒在枯萎啦。",
 "If you wanted one, you'd probably buy a new one":
   "你要是想要一個,大概會去買個新的。",
 "I have heard that even now my cousin Sharaf works with the Underground to free Raseir":
   "我聽說,我表親沙拉夫至今仍與地下組織合作,要解放拉希爾。",
 "I have heard that it was you that vanquished the Fire Elemental. How wondrously brave you must be":
   "我聽說是你擊敗了火元素精靈。你想必勇敢得驚人。",
 "I have made up three potions from what you gave me":
   "我用你給的東西調出了三瓶藥水。",
 "I have many pots for sale that are as practical as they are beautiful":
   "我有許多陶罐出售,既實用又美觀。",
 "I have no use for an empty purse":
   "空錢袋對我沒用。",
 "I haven't got all day. Make it quick":
   "我可沒一整天時間,快點。",
 "I have seen a Griffin flying out over the desert. It must have a nest somewhere near here":
   "我見過一頭獅鷲飛越沙漠。牠的巢一定就在這附近某處。",
 "I have wonderful clothing and robes fit for an emperor":
   "我有上好的衣裳與長袍,連帝王穿了都相稱。",
 "I know this because it was stolen from my very own home the other night":
   "我之所以知道,是因為那晚它就是從我自己家裡被偷走的!",
 "I'll take what's behind door number 3":
   "我選三號門後面那個。",
 "I'm afraid you do not have enough money for the purchase":
   "恐怕你的錢不夠買這個。",
 "I'm a frayed knot":
   "我是個磨破的繩結哪(I'm afraid not 的諧音)。",
 "Imagine! Such a warrior's tail used as a playtoy for a baby":
   "你想想!這麼一條戰士的尾巴,竟拿來給嬰兒當玩具!",
 "I make the finest swords in the city":
   "我打的劍是全城最好的。",
 "I'm not sure either, but I know a way to find out. Care to volunteer":
   "我也不確定,不過我有法子查清楚。想自願試試嗎?",
 "I'm sorry, but I can only accept the coins of Shapeir. You will need to first see the Moneychanger":
   "抱歉,我只收夏皮爾的錢幣。你得先去找錢莊兌換。",
 "I'm terribly sorry. That doesn't seem to be a proper Quest for Glory I save file":
   "非常抱歉,這似乎不是一個有效的《英雄傳奇 I》存檔。",
 "I must know who you are before I can be of service to you. What is your name that I might call you":
   "我得先知道你是誰,才能為你效勞。你叫什麼名字,好讓我稱呼你?",
 "In its formerly legible state, it could have informed YOU what's going on":
   "它要是還認得出字,本來能告訴「你」這是怎麼回事。",
 "Inside, you have stored the essence of the Pizza Elemental":
   "裡頭裝著你封存的「披薩元素精靈」精華。",
 "In some games damaged bricks may indicate a secret door, but that's not the case here":
   "在有些遊戲裡,破損的磚塊可能暗示著密門,不過這裡並非如此。",
 "In Spielburg, these things weren't so friendly":
   "在史畢柏格,這些東西可沒這麼友善。",
 "Instead of dropping the purse, you might try returning it to where you found it":
   "與其把錢袋丟了,你不如試著把它放回原處。",
 "In this land, water is life. You'd be wise to hold on to your last waterskin":
   "在這片土地上,水就是命。留著你最後一個水袋才是明智之舉。",
 "In this place, you must rely on only your magic":
   "在這個地方,你只能仰賴你的魔法。",
 "In your pack is a whirl of the desert Dervish's beard":
   "你的包裡有一撮沙漠苦行僧的鬍鬚。",
 "I overheard that lion guy talking about paladins. How can any respectable fighter be a goody two-shoes":
   "我聽見那個獅子傢伙在談聖騎士。一個像樣的戰士,怎麼能當個假道學的乖寶寶?",
 "I regret it very much, but I can not help you with that":
   "我深感抱歉,但這件事我幫不了你。",
 "I sell bottles of sunscreen for tourists who are not prepared for the desert heat":
   "我賣防曬乳,專給沒備好應付沙漠酷熱的遊客。",
 "I sell fabulous second-hand weaponry that is almost as good as new":
   "我賣的二手兵器棒極了,幾乎跟新的一樣。",
 "I sell giant purses that can hold up to 500 pieces of currency":
   "我賣超大錢袋,最多能裝五百枚錢幣。",
 "I sell oils and ointments that revitalize the skin and make one feel ten years younger":
   "我賣油膏,能活化肌膚,讓人感覺年輕十歲。",
 "I sell pottery renowned around all of Shapeir for its sturdiness":
   "我賣的陶器以堅固聞名全夏皮爾。",
 "I shall find myself missing Ugarte":
   "我會想念烏加特的。",
 "Is it really a basket? Won't know till you ask it":
   "這真是個籃子嗎?不問問它,怎會知道呢?",
 "Is that a refusal, Effendi":
   "這是拒絕的意思嗎,閣下?",
 "I still need the feather of the Griffin. You need to add the victim's hair at the last moment":
   "我還需要那根獅鷲羽毛。受害者的頭髮得由你在最後一刻加進去。",
 "I stock high-quality oil, made from desert snakes. The snakes are especially bred for this purpose":
   "我備有上等的油,用沙漠蛇煉成。那些蛇就是專為此目的培育的。",
 "It ain't much, but the snake calls it home":
   "雖然簡陋,但那蛇管它叫家。",
 "It appears that not only will he not fight with you, your attacks do him no harm":
   "看來他不僅不願跟你動手,你的攻擊對他也毫髮無傷。",
 "It doesn't appear he has time for a quick chat":
   "看來他沒空閒聊幾句。",
 "It doesn't appear she has time for a quick chat":
   "看來她沒空閒聊幾句。",
 "It doesn't need your support":
   "它不需要你的支持。",
 "It drains out your words":
   "它把你的話語都吸了進去。",
 "I tell ya, Mel, my Calm spell would help quell your fell itch well. Try it, it's swell":
   "我跟你說啊老梅,我這「鎮定」術能好好平息你那要命的癢,試試嘛,棒得很!",
 "It grieves me to the last degree that my knowledge of that subject could never be of any use to you":
   "我懂的那點東西對你毫無用處,這讓我難過到了極點。",
 "I thank thee once again. Farewell, friend":
   "我再次謝過你。再會了,朋友。",
 "I thank you on behalf of the Guard for saving Shapeir":
   "我代表衛隊感謝你拯救了夏皮爾。",
 "I sell oils and ointments that revitalize the skin":
   "我賣的油膏能活化肌膚。",
 # --- 第十一批:對白/招牌/物品 ---
 "It has a vague aura of magic":
   "它隱隱透出一絲魔法的氣息。",
 "It has been a pleasure conversing with you. Perhaps we shall share tea again sometime":
   "與你交談十分愉快。或許改日我們能再一同品茶。",
 "It has been a pleasure. I'm sorry we didn't converse at greater length":
   "很高興認識你。可惜沒能多聊一會兒。",
 "I think I have some pills in stock to cure you of that habit":
   "我想我這兒有些藥丸,能治治你那毛病。",
 "It is amazing that anything can survive in the furnace-like desert":
   "在這座熔爐似的沙漠裡居然還有東西能活下來,真是驚人。",
 "It is an experience found nowhere but in Shapeir":
   "這是唯有在夏皮爾才能有的體驗。",
 "It is a pleasure to see you, great Hero":
   "見到您真高興,偉大的英雄。",
 "It is a variety of red Saurus that you never saw in Spielburg":
   "這是一種紅色的索魯斯,你在史畢柏格從沒見過。",
 "It is best that you speak to Signor Ferrari about such matters":
   "這類事情,你最好去找費拉里先生談。",
 "It is cheap at any price":
   "無論開價多少,它都算便宜。",
 "It is foolish to ask that of me":
   "拿這種事問我,未免太傻了。",
 "It is good for Simba to watch us practice. He will need to learn soon enough":
   "讓辛巴看著我們練習是好事。他很快也得學了。",
 "It is good to see one with manners in Raseir. Thank you for aiding my mistress":
   "在拉希爾能見到懂禮數的人,真難得。多謝你相助我家女主人。",
 "It is good to see you, young Hero. A nice day to be adventuring":
   "見到你真好,年輕的英雄。今天是個適合冒險的好日子。",
 "It is hoped that my gift will aid you in saving the city, Hero":
   "但願我這份禮物能助你拯救這座城市,英雄。",
 "It is most polite to eat restaurant meals while seated at a table":
   "在餐館用餐,坐到桌邊吃才最合禮數。",
 "It is my duty to protect this city against monsters that approach it":
   "保護這座城市、抵禦來犯的怪物,是我的職責。",
 "It is my pleasure and my purpose to serve the ways of knowledge":
   "侍奉知識之道,是我的樂事,也是我的本分。",
 "It is rumored that you wish to journey to Raseir. If you do so, please try to find my cousin Sharaf":
   "聽說你想前往拉希爾。你若真去了,請設法找到我表親沙拉夫。",
 "It is said that in Raseir, it is death to break the smallest of laws":
   "據說在拉希爾,哪怕違犯最小的律法,也是死罪。",
 "It is said that the duty of the guards of Raseir is to make certain all people obey the many laws":
   "據說拉希爾衛兵的職責,就是確保所有人都遵守那一條條律法。",
 "It is very dishonorable of you to try that in my home. It would be wise for you to leave at this time":
   "你在我家裡耍這種手段,實在有失體面。你最好現在就離開。",
 "It is very well guarded, and only those whom the Sultan trusts and respects may enter":
   "那裡守衛森嚴,只有蘇丹所信任敬重之人才得入內。",
 "It is your good friend, Abdulla Doo":
   "是你的好朋友,阿布杜拉·杜。",
 "It is your good friend Shameen":
   "是你的好朋友沙明。",
 "It is your good friend Shema":
   "是你的好朋友雪瑪。",
 "It'll take hands more skilled than your own to restore this window to its former state":
   "要讓這扇窗恢復原貌,得靠比你更巧的手才行。",
 "It'll take more than a calm spell to extinguish these flames":
   "光靠一個「鎮定」術,可澆不熄這片火焰。",
 "It looks like the poor man couldn't find an oasis in time":
   "看來這可憐人沒能及時找到綠洲。",
 "It may be hip to be square, but you won't look very suave conversing with these":
   "方方正正或許挺時髦,但你對著這些東西說話,可顯不出什麼風度。",
 "It may have wings and feathers, but the Griffin is not what you'd normally call a bird":
   "牠雖有翅有羽,但獅鷲可不是你一般所說的那種「鳥」!",
 "It remains the property of the Gibson and Phoenix Signs company":
   "它仍屬於「吉布森與鳳凰招牌公司」所有。",
 "It reveals a distinct lack of trust. And you can trust me, my good sir":
   "這分明是信不過人哪。可你大可信我,我的好先生。",
 "I try to be of help":
   "我盡量幫忙。",
 "It's a dead guard":
   "是個死掉的衛兵。",
 "It's a door. No doubt about it":
   "是扇門。這點毫無疑問。",
 "It's a local townsperson":
   "是個本地市民。",
 "It's already on the verge of withering. Uprooting it would kill it":
   "它已經快枯萎了,連根拔起只會要了它的命。",
 "It's always a pleasure. I wish I could see more of you":
   "每次都很愉快。真希望能多見見你。",
 "It's a magical mass of fire":
   "是一團帶著魔法的火焰。",
 "It's a member of the local Katta population":
   "是當地卡塔族的一員。",
 "It's an open and shut case: the window won't talk":
   "這案子明擺著沒戲:窗戶不肯開口。",
 "It's an original Trial by Fire game box. And it's signed by Sloree and Scoree":
   "是一個《烈火試煉》的原版遊戲盒,上頭還有斯洛里和斯科里的簽名!",
 "It's apparent nobody hangs their clothes out in the open anymore":
   "顯然再也沒人把衣服晾在外頭了。",
 "It's a rare blue-skinned desert dwelling frog":
   "是一種罕見的藍皮膚沙漠青蛙。",
 "It's a simple oil lamp that you nabbed from the Blue Parrot Inn":
   "是一盞普通的油燈,你從「藍鸚鵡客棧」順手摸來的。",
 "It's a sublime sign finely designed with care and time":
   "這是塊精雕細琢、用心又費時的絕妙招牌。",
 "It is good to see one with manners":
   "能見到懂禮數的人,真難得。",
 # --- 第十二批 ---
 "It's a simple oil lamp you took from the Blue Parrot Inn":
   "是一盞普通的油燈,你從「藍鸚鵡客棧」拿來的。",
 "It's a writhing funnel of air. What a windbag":
   "是一道扭動翻騰的氣漩。真是個吹牛皮的風袋!",
 "It's best if you just walk carefully":
   "你還是小心走路為妙。",
 "It's beyond your carrying capacity":
   "這超出你能背負的重量了。",
 "It seems to have no effect":
   "似乎毫無作用。",
 "It seems to have no effect on the wall":
   "對那面牆似乎毫無作用。",
 "It's impolite to shout. Get closer if you wish to talk to someone":
   "大吼大叫不禮貌。想跟人說話就走近些。",
 "It's just a mirage":
   "不過是海市蜃樓罷了。",
 "It's just as it appears":
   "它就跟看上去的一樣。",
 "It's just some damaged brickwork. Not some secret passage":
   "只是些破損的磚砌,不是什麼密道。",
 "It's just your average, everyday magic lamp containing a Fire Elemental":
   "就是一盞再平常不過、封著火元素精靈的魔法神燈罷了。",
 "It's like talking to a brick wall":
   "簡直像在對一堵磚牆說話。",
 "It's not a chatterbox":
   "它又不是個多嘴的傢伙。",
 "It's not a talkasaurus":
   "牠又不是「多嘴龍」。",
 "It's not going to help you against the Earth Elemental from inside a chest":
   "把它鎖在箱子裡,可幫不了你對付土元素精靈。",
 "It's not intended for expectorating into":
   "這東西可不是拿來吐口水的。",
 "It's not much to look at":
   "它看起來沒什麼看頭。",
 "It's of no use to you":
   "它對你沒有用處。",
 "It's old news, walked on by old shoes. You can do without it":
   "陳年舊聞,早被踩爛了。沒它你照樣過得去。",
 "It's one of the Raseirian guards":
   "是拉希爾衛兵中的一個。",
 "It sounds as if there's a stream trickling on the other side of the purple door":
   "聽起來,紫色門的另一側有一道淙淙流淌的溪水。",
 "It sounds like a family of rats have taken up residence behind this locked door":
   "聽起來,有一窩老鼠在這上鎖的門後安了家。",
 "It sounds like a very nice place to live":
   "聽起來是個很適合居住的好地方。",
 "It sounds like someone is using the other side of this door as a dartboard":
   "聽起來,有人把這門的另一面當成飛鏢靶了。",
 "It's probably government propaganda. You can do without it":
   "八成是官方的宣傳。沒它你照樣過得去。",
 "It's really hard to get Khaveen to open up":
   "要讓哈維因敞開心扉,可真不容易。",
 "It's Sashanan, the jewelry merchant":
   "是賣珠寶的商人薩沙南。",
 "It's the Djinni of the ring":
   "是戒指裡的鎮尼。",
 "It's the Poet Omar, and his companion and translator, Ja'Afar":
   "是詩人奧瑪爾,還有他的同伴兼翻譯賈法爾。",
 "It's the stall of a Katta merchant who conducts business in the alleyways":
   "是一個在巷弄裡做買賣的卡塔族商人的攤子。",
 "It's too bulky to move":
   "它太笨重,搬不動。",
 "It's too dangerous around here to search the body right now. More guards could arrive at any moment":
   "這附近太危險,現在不宜搜身。隨時可能有更多衛兵趕到。",
 "It's too frail to even put in your pack without damaging it":
   "它太脆弱了,連放進包裡都會弄壞。",
 "It's too heavy to carry around":
   "它太重了,帶不走。",
 "It's too large to put in your backpack":
   "它太大了,塞不進你的背包。",
 "It's too slippery for your Fetch spell":
   "它太滑了,你的「取物」術抓不住。",
 "It swings both ways (or at least it used to in its day.)":
   "它兩邊都能擺動(至少當年是這樣)。",
 "It's your Raseirian visa. Don't leave town without it":
   "是你的拉希爾通行證。沒它別出城。",
 "It's your trusty riding Saurus":
   "是你那頭可靠的坐騎索魯斯。",
 "It takes real muscle to be good at arm wrestling":
   "比腕力要比得好,得有真本事的肌肉。",
 "It took some effort to win Sharaf's trust. You don't want to make him suspicious of you again":
   "好不容易才贏得沙拉夫的信任,你可不想再讓他起疑。",
 "It was cozy enough, but we were saddened to see such a place so dormant and lifeless":
   "這地方倒也舒適,只是見它如此沉寂無生氣,著實令人傷感。",
 "It will flame for you because I wish it to":
   "它會為你燃燒,因為這是我的意願。",
 "It would be a waste to strip this desert of the few plants that still grow here":
   "把這沙漠裡僅存的幾株植物拔光,未免太可惜了。",
 "It would be best to do that under the cover of complete darkness":
   "這事最好趁著一片漆黑時動手。",
 "It wouldn't be wise to disturb a snake-charmer in the middle of his song":
   "在弄蛇人吹奏到一半時打擾他,可不是明智之舉。",
 "It wouldn't really be wise announcing to the local guard that you are of the profession":
   "向本地衛兵宣告你是幹這行的,實在算不上聰明。",
 "It wouldn't survive a trip in your backpack":
   "它經不起在你背包裡顛簸。",
 "It would please me if you would come to my dance this evening":
   "你今晚若肯來看我跳舞,我會很高興。",
 "I've had better luck trying to buy a glow-in-the-dark turban. I think I'll quit while I'm behind":
   "我連買夜光頭巾的運氣都比這好。我看還是趁著沒輸更慘收手吧。",
 "I will ask the questions around here. Learn your place":
   "這兒由我來發問。認清你的身分!",
 "I will be honored to put your Saurus back into the stable for you, Effendi":
   "閣下,我很榮幸替您把索魯斯牽回棚廄。",
 "I will return the purse to Omar for you, although I do not think he will be happy to see it is now empty":
   "我替你把錢袋還給奧瑪爾,不過他見它空了,大概不會高興。",
 "I will return with a splendid meal for you":
   "我這就去替您備一頓豐盛的餐點。",
 "I will return with some tea for you":
   "我這就去替您沏些茶來。",
 "I wish you to bring me a small ornament to prove your skills":
   "我要你帶一件小飾品來,證明你的本事。",
 "I would follow you gladly. But first we must escape this cell":
   "我樂意跟隨你。但我們得先逃出這間牢房。",
 "I wouldn't be doing that. You don't know where that lock pick's been":
   "我可不會那麼做。誰知道那把開鎖器去過什麼地方。",
 "Ja'Afar does not want your money":
   "賈法爾不要你的錢。",
 "Jackalmen are humanoid canines who prefer to travel in packs":
   "豺狼人是人形的犬類,慣於成群行動。",
 "Jackalmen travel in packs and prefer attacking things previously wounded":
   "豺狼人成群結隊,專挑已經受傷的目標下手。",
 "Judging from those crazy colors, this frog just may be toxic. You decide not to suck on it":
   "看那一身瘋狂的顏色,這青蛙八成有毒。你決定還是別舔它。",
 "Just a minute and I'll introduce your Saurus to you":
   "稍等一下,我把你的索魯斯介紹給你。",
 "Just before your eyes close for the very last time, you reconsider the wisdom of abstaining from sleep":
   "就在你的雙眼最後一次闔上之前,你重新斟酌起「不睡覺」這主意到底明不明智……",
 "Keapon doesn't need the bellows. Besides, you may still need them":
   "姬朋用不著這風箱。再說,你說不定還用得上。",
 "Keapon isn't a valid target for spells":
   "姬朋不能當法術的目標。",
 "Keapon Laffin sold you one pair of Ali Fakir's Genuine X-Ray Glasses":
   "姬朋·拉芬賣給你一副阿里·法基爾的正牌透視眼鏡。",
 "Keapon likes to engage in magical games with visitors every so often. You should ask him about it":
   "姬朋偶爾喜歡跟訪客玩玩魔法遊戲。你該問問他這事。",
 "Keep it to yourself":
   "這事你自己知道就好。",
 "Keep it with you for now. It may come in handy":
   "暫且留在身邊吧,說不定派得上用場。",
 "Khaveen can't hear you from here":
   "從這兒哈維因聽不見你。",
 "Kiram is the local clothing merchant":
   "基拉姆是本地的服裝商。",
 "Knocking won't help. The door has been nailed shut":
   "敲也沒用,這門已經被釘死了。",
 "Konnichiwa! Come and tell me who! Hola! How now, brown cow":
   "空你機哇!來告訴我是誰!喔啦!最近如何呀,花斑牛?",
 "Kwa heri, Hero. Come back if you need more information or combat practice":
   "再會(Kwa heri),英雄。需要更多消息或想練練身手,再回來。",
 "Lasham fills your empty pot with dirt from one of her flower pots":
   "拉珊從她的一個花盆裡舀了些土,把你的空罐填滿。",
 "Leave him a loan, shark":
   "放他一馬吧,放高利貸的。",
 "Leave that job to the termites":
   "那活兒就交給白蟻去幹吧。",
 "Leave the window where it is. The occupant would appreciate it":
   "讓那扇窗留在原處吧,屋主會感激你的。",
 # --- 第十三批:人名/諺語/對白 ---
 "Let him out of the pen first":
   "先把牠放出柵欄。",
 "Let's get this story straight":
   "咱們把話說清楚。",
 "Like a lit brass lamp, may you always find your way. Farewell, Effendi":
   "願你如一盞點亮的銅燈,永遠找得到方向。再會,閣下。",
 "Looking back at you with joy, Abdulla makes a gesture of approval towards you with his tea cup":
   "阿布杜拉欣喜地回望你,舉起茶杯朝你比了個讚許的手勢。",
 "Looks like you need to get some more practice today. You be getting plenty good":
   "看來你今天還得多練練。你已經很有長進了。",
 "Magic users are known for their powerful spells and subtle, indirect solutions to problems":
   "法師以強大的法術,以及巧妙迂迴的解題之道聞名。",
 "Man who is always polite finds many people to help him":
   "待人時時有禮者,自有眾人相助。",
 "Man who keep one hand on weapon have difficulty walking in public":
   "手不離兵刃者,難以坦然行於人前。",
 "Man who wrongfully attack peaceful dervish will soon find himself up to his earlobes in wrongful attacks":
   "無故攻擊和平苦行僧者,不久便會發覺自己深陷無故的攻擊裡,直沒到耳根。",
 "Master, please hurry! We don't have much time left":
   "主人,快點!我們時間不多了!",
 "Master, we don't have time for purposeless spells":
   "主人,我們沒空施那些沒用的法術。",
 "Master, we must hurry onward":
   "主人,我們得快點趕路。",
 "Maybe these cases will once again decorate the environment. Better let them where they are":
   "或許這些箱子有天會再次點綴此地。還是讓它們留在原處吧。",
 "May diamonds light your day, Hero-friend":
   "願鑽石照亮你的日子,英雄朋友。",
 "May good fortune favor you, Effendi. Farewell":
   "願好運眷顧您,閣下。再會。",
 "May my lamp serve you well":
   "願我這盞燈好好為你效力。",
 "May you have a good day today":
   "願你今天順心如意。",
 "May you have a good day today, Effendi. Farewell":
   "願您今日順心如意,閣下。再會。",
 "May your day be filled with the scent of sweet flowers, Effendi":
   "願您的一天充滿芬芳花香,閣下。",
 "May you stay safe":
   "願你平安。",
 "Mayzun pays no attention to you":
   "梅尊沒理會你。",
 "Mirak is the local leather merchant":
   "米拉克是本地的皮革商。",
 "Most strange. If you have an upset stomach, perhaps you should buy a healing pill":
   "真奇怪。你若是腸胃不適,或許該買顆治療藥丸。",
 "Move out from behind the cage where there is more room":
   "從籠子後面移到空間大些的地方。",
 "Move out from under the parapet first":
   "先從城垛底下移開。",
 "Move out in front of the balcony first":
   "先移到陽台前方。",
 "Move up to a pillar first":
   "先移到柱子旁。",
 "My collection of perfumes contains fragrances for every occasion you could imagine":
   "我收藏的香水,你想得到的任何場合都有對應的香氣。",
 "My dirt should help you defeat the thing of air":
   "我的泥土應該能助你擊敗那團風之物。",
 "My name is Abd al-Malik":
   "我叫阿卜杜勒-馬利克。",
 "My name is Kadash":
   "我叫卡達什。",
 "My name is Kaleema":
   "我叫卡莉瑪。",
 "My name is Kareem":
   "我叫卡里姆。",
 "My name is Kasheem":
   "我叫卡希姆。",
 "My name is Laram":
   "我叫拉拉姆。",
 "My name is Laree":
   "我叫拉里。",
 "My name is Lira":
   "我叫莉拉。",
 "My name is Liram":
   "我叫里拉姆。",
 "My name is Mareek":
   "我叫馬里克。",
 "My name is Matak":
   "我叫馬塔克。",
 "My name is Neko":
   "我叫內可。",
 "My name is Sareena":
   "我叫薩莉娜。",
 "My name is Sayf al-Maluk":
   "我叫賽夫·馬魯克。",
 "My name is Shareem":
   "我叫沙里姆。",
 "My name is Sillah":
   "我叫希拉。",
 "My name is Sira":
   "我叫希拉。",
 "My name is Sonee":
   "我叫索尼。",
 "My name is Tarah":
   "我叫塔拉。",
 "My name is Tarim":
   "我叫塔里姆。",
 "My name is Tirak":
   "我叫提拉克。",
 "My name is Tracheema":
   "我叫特拉奇瑪。",
 "My pleasure it is to serve you, Effendi":
   "能為您效勞是我的榮幸,閣下。",
 "My pots can be used for anything, from carrying water to housing plants":
   "我的陶罐什麼都能用,從盛水到種花無所不可。",
 "My spear arm is getting tired of just holding Simba. Good thing for you, too, if we practice today":
   "我這持矛的手光抱著辛巴都快累了。今天練一練,對你也是好事。",
 "My sword is called 'Soulforge.' It is a flaming sword":
   "我這把劍名叫「鑄魂」。是一把燃燒之劍。",
 "My thanks, but I have no need for gifts":
   "謝謝你,但我不需要禮物。",
 "My, you are quite the eloquent and articulate one":
   "哎呀,你還真是個能言善道、口齒伶俐的人哪!",
 "Mzuri sana. I accept your challenge. Let's fight":
   "很好(Mzuri sana)。我接受你的挑戰。來打吧。",
 "Name contains invalid characters":
   "名稱含有無效字元。",
 "Nice try, but you'll have to find a more traditional method of opening her heart":
   "想得美,你得用更老派的法子才能打開她的心扉。",
 "Nobody responds to your call":
   "沒有人回應你的呼喚。",
 "Nobody seems to be listening":
   "似乎沒有人在聽。",
 "No fan game would be complete without one of these":
   "少了這個,任何同人遊戲都稱不上完整。",
 "No, Master. You'd only get yourself caught":
   "不,主人。你那麼做只會害自己被逮。",
 "No, Master. You don't need to do that now. Let's go":
   "不,主人。你現在不必那麼做。我們走吧。",
 "No, Master! You need to keep your feet on the ground":
   "不,主人!你得腳踏實地。",
 "No need to blow them dry. The sun can manage quite well on its own":
   "不必把它們吹乾,太陽自己就辦得很好。",
 "No need to buy a new purse. It'd be exactly like your old purse, except with less money in it":
   "不必買新錢袋。那只會跟你舊的一模一樣,只是裡頭錢更少。",
 "No one hears you knocking":
   "沒有人聽見你敲門。",
 "No rest for the weary":
   "累歸累,可沒得歇。",
 "My name is Sharim":
   "我叫沙里姆。",
 # --- 第十四批:地名/系統/諺語/對白 ---
 "No rest for the weary! Something's after you":
   "累歸累,可沒得歇!有東西在追你。",
 "Not now. Get to the pillar":
   "現在不行。先到柱子那兒去。",
 "Not right now. Somebody might get hurt":
   "現在不行,可能會有人受傷。",
 "Not while you're riding your Saurus":
   "你騎著索魯斯時可不行。",
 "No way -- not with your backpack this heavy":
   "門兒都沒有——你背包這麼重哪行!",
 "Now, do we have a deal, or is this a deal":
   "怎麼樣,這筆買賣成不成?",
 "No, when it's e'rat'icated. What did the rat say as he fell 12,000 feet straight down":
   "不,是牠被「鼠」除的時候。那隻老鼠直直墜下一萬兩千呎時,說了什麼?",
 "Now I must get back to my work. If you see something that interests you, let me know":
   "我得回去幹活了。你要是看上了什麼,就告訴我。",
 "Now is not a good time to use your map":
   "現在不適合看地圖。",
 "Now seems like an excellent time for such a venture":
   "現在似乎正是幹這檔事的大好時機。",
 "Now that you've made friends and told tales, it's time to think about escaping":
   "如今你已交了朋友、敘過往事,該想想怎麼脫身了。",
 "Now would not be a good time for that":
   "現在做那件事不是時候。",
 "Occasional bumps and scratches can be heard from behind this door":
   "這門後不時傳來碰撞與抓搔聲。",
 "Of course, such places are hardly suitable for adventurers who wish to be heroes":
   "當然,這種地方可不適合一心想當英雄的冒險者。",
 "Oh, a wise guy, eh":
   "喔,自作聰明是吧?",
 "Oh, is that a pizza? I have never seen such a perfect one before. Did you make it yourself":
   "喔,那是披薩嗎?我從沒見過這麼完美的一個。你親手做的?",
 "Oh, is your pouch deflated? I'm so sorry. Well, I hope you can come again soon":
   "喔,你的錢囊癟了?真遺憾。好吧,希望你很快能再來。",
 "Oh, leaving are you? Farewell, then. Be sure to return if you need any of my pills":
   "喔,要走了?那就再會吧。需要我的藥丸,記得再來。",
 "Okay. What do you want to know":
   "好。你想知道什麼?",
 "Okay. You drop the ceramic container":
   "好。你放下了那只陶罐。",
 "Omar does not need that":
   "奧瑪爾不需要那個。",
 "Omar frowns at your gesture":
   "奧瑪爾對你的舉動皺起了眉。",
 "One of the few living things in the desert":
   "是沙漠裡少數的活物之一。",
 "One thing at a time, Hero":
   "一次一件事,英雄。",
 "Only a Fresno Raisin could love the blazing orange sun of Shapeir":
   "也只有弗雷斯諾的葡萄乾,才會愛夏皮爾那輪炙熱的橘色太陽。",
 "Only a Shapeirian sunset beats my jewelry as far as beauty and splendor are concerned":
   "論美麗與華彩,唯有夏皮爾的落日能勝過我的珠寶。",
 "On the opposite side, you hear deep and heavy shuffling and dragging sounds":
   "另一側傳來沉重的拖曳與挪動聲。",
 "On the other hand, where did you pick these up again":
   "話說回來,你這些又是打哪兒撿來的?",
 "On the other side of the door, heavy breathing and crying are audible":
   "門的另一側,聽得見沉重的喘息與哭泣。",
 "On this shelf are various examples of stuff, things, and megusalems":
   "這架子上擺著各式各樣的玩意兒、東西,還有梅古撒冷。",
 "Opening up nose like opening out heart. Keep a tissue handy for both":
   "敞開鼻孔猶如敞開心扉。兩者都記得備條手帕。",
 "Other than its shape, there's nothing special about this rock":
   "除了形狀,這塊石頭沒什麼特別的。",
 "Ouch! Why do you treat yourself so inappropriately":
   "哎喲!你幹嘛這樣折騰自己?",
 "Our lizard jerky rations are very cheap":
   "我們的蜥蜴肉乾乾糧很便宜。",
 "Our special blend of preservatives lets the rich, full-bodied lizard flavor come through":
   "我們特調的防腐配方,能把那濃郁醇厚的蜥蜴風味完整保留下來。",
 "People will think you've gone fruity":
   "人家會以為你發瘋了!",
 "Perhaps it would be best, Effendi, if you returned it to Omar himself":
   "閣下,或許最好還是由您親自把它還給奧瑪爾。",
 "Perhaps it would be wise to just hide under a rock for a few days or so":
   "或許躲到石頭底下避個幾天,才是明智之舉。",
 "Perhaps you should return when you have learned your name and some manners":
   "等你弄清自己的名字、學會點規矩,再回來吧。",
 "Permit me to loan you my sword, 'Soulforge.'":
   "請容我把我的劍「鑄魂」借給你。",
 "Picking nose like picking fight. Both leave hands dirty":
   "挖鼻孔猶如挑釁打架,兩者都弄髒了手。",
 "Picking your nose like picking your underwear. Better without audience":
   "挖鼻孔猶如挑內褲,沒有觀眾時做比較好。",
 "Pills to magically restore your health":
   "以魔法恢復生命力的藥丸。",
 "Pills to magically restore your spell-casting abilities":
   "以魔法恢復施法能力的藥丸。",
 "Pills to magically restore your stamina":
   "以魔法恢復耐力的藥丸。",
 "Pinned to the Guild wall was a poster requesting a hero for the realm of Spielburg to the west":
   "公會牆上釘著一張海報,為西邊的史畢柏格之地徵求一名英雄。",
 "Pity. Ah, well, there will be others. Good day, sir":
   "可惜。唉,算了,還會有別人的。再會,先生。",
 "Plants thrive beneath this residential window. A decorative awning provides shade from the harsh sun":
   "這扇民宅窗下花草繁茂,一張裝飾用的遮篷擋去了烈日。",
 "Plaza of the Fighters East":
   "戰士廣場 東",
 "Plaza of the Fighters West":
   "戰士廣場 西",
 "Plaza of the Fountain North":
   "噴泉廣場 北",
 "Plaza of the Fountain South":
   "噴泉廣場 南",
 "Plaza of the Palace":
   "王宮廣場",
 "Please don't leave. I need your help":
   "請別走。我需要你的幫助。",
 "Please, Effendi. You must come inside quickly before the guards notice us":
   "拜託,閣下。趁衛兵還沒注意到我們,您得趕快進來。",
 "Please keep it with you for as long as you are our guest":
   "只要你還是我們的客人,就請隨身帶著它。",
 "Please post all queries and comments on our forums at www.AGDInteractive.com":
   "一切疑問與意見,請發表於我們的論壇 www.AGDInteractive.com。",
 "Please select a game to delete":
   "請選擇要刪除的存檔。",
 "Please stand up first to avoid issues when returning to the current room after battle is over":
   "請先站起來,以免戰鬥結束、回到當前房間時出狀況。",
 "Please tell me what happens when you use it. I'm sorry I can't be there, but I have much work to do":
   "請告訴我你用它時發生了什麼。抱歉我不能在場,實在有太多活兒要忙。",
 "Please type a longer description":
   "請輸入較長的描述。",
 "Please type a longer name":
   "請輸入較長的名稱。",
 "Press the key you wish to assign to this action":
   "請按下你想指派給此動作的按鍵。",
 "Pretty jewelry and amulets hang on the stand":
   "架上掛著精美的珠寶與護身符。",
 "Q. How do you get down off a Saurus":
   "問:你要怎麼從索魯斯身上「下」來?",
 "Quiet. Someone might hear you":
   "安靜。可能會被人聽見。",
 "No one seems to be listening.":
   "似乎沒有人在聽。",
 # --- 第十五批:Rakeesh/Shema/系統/諧音 ---
 "Quit blubbering and DO something":
   "別再哭哭啼啼了,倒是做點什麼啊。",
 "Rakeesh bears a grim expression, and there's a hint of shame on his face":
   "拉基什神情嚴峻,臉上隱隱透著一絲羞愧。",
 "Rakeesh' condition seems to have improved since yesterday, but his mood seems unchanged":
   "拉基什的傷勢看來比昨天好些了,心情卻似乎沒什麼變化。",
 "Rakeesh frowns and you realize that sparring will be difficult if you don't return his sword first":
   "拉基什皺起眉,你意識到不先把劍還他,這架是切磋不成的。",
 "Rakeesh has trouble keeping body balanced when getting hit. If you create opening, exploit it":
   "拉基什挨打時不易穩住身形。你若製造出破綻,就好好把握。",
 "Rakeesh just frowns at you. Maybe you shouldn't be picking your nose in public":
   "拉基什只是朝你皺眉。也許你不該在大庭廣眾下挖鼻孔。",
 "Rakeesh looks completely recovered from his battle a few days back and seems to be in quite high spirits":
   "拉基什看來已從幾天前那場戰鬥中完全康復,精神還相當不錯。",
 "Rakeesh relaxes, but his tail stays ever alert":
   "拉基什放鬆了下來,那條尾巴卻始終保持警戒。",
 "Rakeesh sits calmly nearby. The Liontaur seems well-accustomed to this room":
   "拉基什在一旁安然端坐。這獅人似乎對這房間很是熟悉。",
 "Rakeesh wouldn't have loaned it to you if he knew you'd be careless with it":
   "拉基什要是早知道你會這麼粗心,根本不會把它借給你。",
 "Raseir needs your urgent attention. You don't have time to sleep your valuable days away in Shapeir":
   "拉希爾急需你關注。你可沒空在夏皮爾睡掉這些寶貴的日子。",
 "Rather than taking full responsibility for a possible burglary, you decide to hold on to the key":
   "與其為一樁可能的竊案扛下全責,你決定還是把鑰匙留著。",
 "Remember to have the victim drink the potion in order to break the spell":
   "記得讓受害者喝下藥水,才能解除咒語。",
 "Right. At any rate, Wizard-Hero, good luck and farewell":
   "好。總之,巫師英雄,祝你好運,再會了!",
 "Roget the Saurus, is at a loss for words":
   "「羅傑詞」索魯斯,一時語塞,說不出話來。",
 "Run a local script here":
   "在此執行本地腳本。",
 "Run around the balcony? If you were down there, you might try running":
   "繞著陽台跑?你要是在下頭,倒可以試著跑跑。",
 "Salt already has everything he needs in his own workshop":
   "索特在自己的工坊裡,要的東西一應俱全。",
 "Scoree sometimes gets belly aches when he eats too much Saurus jerky":
   "斯科里有時蜥蜴肉乾吃太多會鬧肚子。",
 "Scorpion tails look as venomous as they are":
   "蠍尾看起來有多毒,實際就有多毒。",
 "Select a game to restore:":
   "選擇要讀取的存檔:",
 "Shall we shake hands on forty dinars for the Saurus":
   "這頭索魯斯,四十第納爾,咱們握手成交如何?",
 "Shameen gave you the key to the front door of the Katta's Tail Inn":
   "沙明把「卡塔之尾客棧」前門的鑰匙交給了你。",
 "Shameen looks at you and just scratches his head. Maybe you shouldn't be picking your nose in public":
   "沙明看著你,只是搔了搔頭。也許你不該在大庭廣眾下挖鼻孔。",
 "Shameen spends some time making you familiar with the words that make up the names of Shapeir's streets":
   "沙明花了些時間,讓你熟悉組成夏皮爾街名的那些字詞。",
 "Shapeir is safe for the time being. Concentrate your efforts on Raseir instead":
   "夏皮爾暫時安全了。把心力轉到拉希爾去吧。",
 "Shema has given you a spare suit of clothes for overnight trips, sales meetings, etc":
   "雪瑪給了你一套備用衣裳,供你過夜出行、洽談生意等場合穿。",
 "Shema spends some time explaining the names of the various streets to you":
   "雪瑪花了些時間,向你解釋各條街道的名稱。",
 "Shema will be with you shortly":
   "雪瑪很快就會來招呼你。",
 "Shema will be with you shortly with one of her splendid meals":
   "雪瑪很快就會端著她那豐盛的餐點來招呼你。",
 "Shema will be with you shortly with some of our wonderful tea":
   "雪瑪很快就會端著我們上好的茶來招呼你。",
 "She too will forever have our gratitude for allowing us to return home":
   "她讓我們得以重返家園,我們同樣永遠感念。",
 "Show me something worth bargaining for":
   "拿點值得我討價還價的東西出來瞧瞧。",
 "Sign here! No, sign there! On second thought, don't sign at all":
   "在這兒簽!不,在那兒簽!再想想——還是別簽了。",
 "Silence, infidel. Listen and pay attention or we will use force":
   "住口,異教徒。給我聽好,否則別怪我們動粗。",
 "Silly you! They're right there on the end of your nose":
   "你這傻瓜!它們不就在你鼻尖上嗎!",
 "Simba here is more like a lion. He is having a wonderful time":
   "這位辛巴倒更像頭獅子。他正玩得開心呢。",
 "Since you haven't received any service from Salt, there's no need to pay him for anything":
   "你還沒接受索特任何服務,沒必要付他半文錢。",
 "Since your need is great, this waterskin shall be a gift":
   "既然你急需,這個水袋就送你了。",
 "Sloree is the local meat merchant":
   "斯洛里是本地的肉販。",
 "Sneak around the balcony? If you were down there, you might try sneaking":
   "繞著陽台潛行?你要是在下頭,倒可以試著潛行。",
 "So, Hero of Spielburg, you think you want to go practice some? I could use workout":
   "怎麼樣,史畢柏格的英雄,想去練練嗎?我也正好需要活動活動。",
 "Someone behind this door is repeatedly saying 'Ma fhimt.' You don't understand":
   "這門後有人反覆說著「Ma fhimt」。你聽不懂。",
 "Someone is jiggling the handle on the other side of this locked door":
   "有人在這上鎖的門另一側,不停搖晃著門把。",
 "Someone is whistling a familiar tune in an odd key behind this door":
   "這門後,有人用古怪的調子吹著一首耳熟的曲子。",
 "Someone (or something) behind this door is thumping something as heavy as a pumpkin":
   "這門後有人(或某種東西)正在敲打一件南瓜般沉重的物事。",
 "Someone probably lives behind this door":
   "這門後大概住著人。",
 "Someone with your skills can do without my powder of burning":
   "憑你的本事,沒我這燃燒之粉也行。",
 "Something in the back of your mind tells you that you may need this magical earth at a later date":
   "你腦海深處有個聲音告訴你,日後或許用得上這魔法泥土。",
 "Sorry, boss, all I got is a buncha burnt wood":
   "抱歉啦,老大,我這兒只有一堆燒焦的木頭。",
 "Sorry, Master, but we must get Iblis first":
   "抱歉,主人,但我們得先解決伊布利斯。",
 "Sorry mister, don't have any spare parts for that model lying around. It'll take some time to order them":
   "抱歉先生,那型號的備件我這兒沒現貨,得花些時間訂貨。",
 "Sorry, my little Hero, but you just don't have the cash. You'll have to pay up to play with me":
   "抱歉啦,我的小英雄,你錢就是不夠。想跟我玩,得先付錢。",
 "Sorry, not right now":
   "抱歉,現在不行。",
 "Sounds like there's a whole lot of nothing going on behind this door":
   "聽起來這門後啥事也沒有。",
 "Sounds like work going on behind this door":
   "聽起來這門後有人在幹活。",
 "So what do you say, shall we shake hands and call it a deal":
   "怎麼樣,咱們握個手,這買賣就算成交了?",
 "Speak now the name of FLOWER":
   "現在,說出「花」的名字!",
 "Speak the name of power:":
   "說出力量之名:",
 "Stick to dealing with the kind of trash you're used to. Monsters, murderers, and madmen":
   "還是去對付你慣常那些渣滓吧——怪物、殺人犯,還有瘋子。",
 "Strong boots with soles reinforced with Mirak's toughest leather":
   "結實的靴子,鞋底用米拉克最堅韌的皮革加固過。",
 "Such a shame that we could not make a deal. The pin was truly perfect for you":
   "這筆買賣沒成,真是可惜。那根別針真是再適合你不過了。",
 "Such a thing is not nearly so grand as the Fire Elemental":
   "這種東西可遠遠及不上火元素精靈那般了得。",
 "No rest for the weary":
   "累歸累,可沒得歇。",
 # --- 第十六批 ---
 "Such a thing was done with pleasure, Hero, and needs no mention":
   "舉手之勞,英雄,何足掛齒。",
 "Suddenly, you feel much weaker than before":
   "突然間,你覺得比先前虛弱了許多。",
 "Sure, buddy! What do you want to know":
   "當然啦,老兄!你想知道什麼?",
 "Surely an adventurer gets hungry at times":
   "冒險者總有餓肚子的時候吧。",
 "Surely but a small amount for such a treat":
   "這等美味,這點錢算什麼。",
 "Swinging from them might be fun... if you were in a jungle":
   "抓著它們盪來盪去或許挺有趣……前提是你身在叢林裡。",
 "Take a drink from the fountain, Hero-friend. It will do no end of good":
   "從噴泉喝口水吧,英雄朋友。好處說不完。",
 "Take one pill with water and get plenty of rest":
   "配水服一顆藥丸,再好好休息。",
 "Taking quick stock of your condition, you find the reason -- you're dead. Better aim elsewhere next time":
   "你迅速盤點了一下自己的狀況,找出了原因——你死了。下次最好瞄準別處。",
 "Tarik of Rafir[(Street of the Guard)":
   "拉菲爾之街[(衛兵之街)",
 "Tell me about your past and the things you have done":
   "跟我說說你的過往,還有你做過的事。",
 "Thank you, a thousand thank-yous. It is with your support that I may continue my vital work":
   "謝謝你,千恩萬謝。全靠你的支持,我才能繼續這要緊的工作。",
 "Thank you, but I have no need for such things":
   "謝謝你,但我用不著這些東西。",
 "Thank you, I shall put them somewhere suitable":
   "謝謝你,我會把它們妥善安置。",
 "Thank you. Perhaps someday you'll earn the right to wield such a sword permanently":
   "謝謝你。或許有朝一日,你能掙得永久持有這把劍的資格。",
 "Thank you, thank you, Effendi. You shame me with your kindness":
   "謝謝您,謝謝您,閣下。您的善意讓我受之有愧。",
 "Thank you. They are most beautiful":
   "謝謝你,它們美極了。",
 "Thank you very much. That is most thoughtful of you":
   "非常感謝。你真是體貼。",
 "That feels good; just what you needed to relieve some of the aches and pains of everyday adventuring":
   "這感覺真好,正好替你舒緩了日常冒險帶來的痠痛。",
 "That is most terrifying. I do not know how I might be able to help you":
   "這太可怕了。我不知道自己能幫上你什麼忙。",
 "That is very kind of you. Thank you for not using up more powder than was necessary":
   "你真是太好心了。謝謝你沒用掉多餘的粉末。",
 "That looks and smells delicious, Hero-friend. Shema and I will enjoy this treat. Thank you very much":
   "看著就香,英雄朋友。雪瑪和我會好好享用這份美味。非常感謝你。",
 "That must have been a frightful experience; being turned into a frog and held over a boiling cauldron":
   "那肯定是段駭人的經歷——被變成青蛙,還被吊在滾燙的大鍋上。",
 "That's all well and good, but I'd rather be conducting a little business, if there's any to be conducted":
   "這都很好,不過要是有生意可做,我倒寧願做點買賣。",
 "That's nice of you to show me your money":
   "你把錢秀給我看,真好心。",
 "That's not a good idea":
   "這主意不妙。",
 "That's not the most sanitary of places to stick your hand":
   "把手伸進那種地方,可不怎麼衛生。",
 "That's one thirsty Saurus":
   "這索魯斯可真渴。",
 "That was a great fight you put up! You've got what it takes to be amongst the best members of EOF":
   "你這一仗打得漂亮!你有躋身永恆戰士團頂尖成員的本錢。",
 "That was a waste":
   "真是浪費。",
 "That which I lost[is now returned,[I give you the praise[of gratitude earned":
   "我所失之物[如今已歸還,[我以應得的[感激來頌讚你。",
 "That won't work. The spell Ad Avis placed around the ritual chamber stops all magic from getting in":
   "那行不通。阿德·阿維斯在祭儀室四周下的咒,擋住了一切外來的魔法。",
 "That would be a heated conversation":
   "那會是場「火熱」的對話。",
 "That would give new definition to the term \"lucky dip.\"":
   "那會給「幸運抽抽樂」一詞下個全新的定義。",
 "That would guarantee a quick one-way trip to the dungeon":
   "那準保讓你直送地牢、有去無回。",
 "That would not be a very good idea. You prefer navigating the city without getting lost all the time":
   "那可不是什麼好主意。你還是寧願在城裡走動時別老是迷路。",
 "That wouldn't be a good idea":
   "這主意不妙。",
 "That wouldn't be a good idea right now":
   "現在這麼做不妙。",
 "That wouldn't be very heroic":
   "那可不太像英雄的作為。",
 "That wouldn't do you any good here":
   "在這兒那對你沒半點好處。",
 "That would probably leave you with a permanent case of halitosis":
   "那大概會讓你落下永久性口臭。",
 "The acrobat just frowns at you":
   "那雜耍藝人只是朝你皺眉。",
 "The Adventurer's Guild is on the west end of the Plaza of the Fighters":
   "冒險者公會在戰士廣場的西端。",
 "The Astrologer has gone to bed for the night":
   "占星師已經就寢了。",
 "The barrel contains a pile of rotting fruit. Phew":
   "桶裡裝著一堆腐爛的水果。噁!",
 "The barrier seems to be the only thing around here that's in good shape. You can't budge it":
   "這障礙物似乎是這附近唯一完好的東西。你絲毫撼動不了它。",
 "The beast is much too large to fetch":
   "這野獸太大了,「取物」術搬不動。",
 "The beast is much too large to fetch, and you can't control the spell well enough to get only some fur":
   "這野獸太大,「取物」術搬不動,你也沒法精準到只取一撮毛。",
 "The beast only reacts with a few quick blinks":
   "那野獸只是飛快地眨了幾下眼。",
 "The beast seems at peace for a moment, but not for long":
   "那野獸暫時平靜了一會兒,卻維持不久。",
 "The beggar accepts the food gratefully":
   "乞丐感激地接過了食物。",
 "The beggar accepts the slice of pizza gratefully":
   "乞丐感激地接過了那片披薩。",
 "The beggar gives you a strange look, but says nothing":
   "乞丐古怪地瞅了你一眼,卻什麼也沒說。",
 "The beggar is bawling for dinars (but might settle for centimes)":
   "乞丐扯著嗓子討第納爾(不過給點生丁小錢他大概也認了)。",
 "The bird is kept in a locked cabinet in that room":
   "那隻鳥被鎖在那房間的櫃子裡。",
 "The black bird does not open":
   "那隻黑鳥打不開。",
 "The black bird is too heavy to Fetch. You wonder what it could be made of that would make it so heavy":
   "那隻黑鳥太重,「取物」術搬不動。你納悶它到底是什麼做的,怎會這麼重。",
 "The blazing desert sun beats down fiercely on your head":
   "炙熱的沙漠驕陽狠狠灼烤著你的頭頂。",
 "The blazing desert sun makes it impossible to rest here. The withered tree provides no shade at all":
   "炙熱的沙漠驕陽讓你無法在此歇息,那棵枯樹遮不了半點蔭。",
 "The book itself is labeled \"Warrior's Diary.\" You decide to keep it and use it for your own notes":
   "這本書上頭標著「戰士日記」。你決定留下它,拿來記自己的筆記。",
 "The box is too heavy for your Fetch spell":
   "這箱子太重,你的「取物」術搬不動。",
 "The brass jug is too heavy for your Fetch spell":
   "這黃銅壺太重,你的「取物」術搬不動。",
 "The bread is first fried in olive oil":
   "麵包要先用橄欖油煎過。",
 "The Brigand doesn't respond. That probably means he wants your money AND your life":
   "那強盜沒有回應。這多半表示他既要你的錢,也要你的命。",
 "The Brigand is finally down for good. You wonder how a Brigand ended up in the city in the first place":
   "那強盜終於徹底倒下了。你納悶,一個強盜當初究竟是怎麼混進城裡的。",
 "The Brigand no longer has anything worth taking on him":
   "那強盜身上再也沒什麼值得拿的了。",
 "The city walls are too slick to scale and you'd only get arrested if you tried":
   "城牆太滑,爬不上去,真要試也只會被抓。",
 "The coins of Shapeir are stamped with an image of the Sultan Harun al-Rashid (May He Rule Forever!)":
   "夏皮爾的錢幣上鑄著蘇丹哈倫·拉希德的肖像(願他永世統治!)。",
 "The combat copilot is not available on the highest difficulty setting":
   "在最高難度設定下,無法使用戰鬥輔助。",
 # --- 第十七批:門/元素/衛兵/Katta ---
 "The crates are nailed shut. You have neither the time nor the patience to open them":
   "這些木箱都被釘死了。你既沒時間、也沒耐性去撬開它們。",
 "The Creature of Water prevents any from approaching the fountain. I fear we will soon have no water":
   "那水之造物不准任何人靠近噴泉。我怕我們很快就要沒水了。",
 "The creature's tough, armor-like exterior is certain to render any bare-hand attacks completely useless":
   "這生物堅硬如甲的外殼,肯定讓任何徒手攻擊全然無效。",
 "The desert heat appears to be getting to you, Hero-friend":
   "沙漠的酷熱似乎讓你有點吃不消了,英雄朋友。",
 "The desert is a very dangerous place for any man":
   "對任何人而言,沙漠都是個極其危險的地方。",
 "The Djinni is not interested in any of your possessions":
   "鎮尼對你的任何東西都不感興趣。",
 "The door appears to be locked":
   "門似乎鎖著。",
 "The door defies your attempt to open it":
   "這扇門任你怎麼弄都打不開。",
 "The door does not seem to be magic, but there is a glow behind it":
   "這門看來不帶魔法,門後卻透著一抹微光。",
 "The door has swung out too far. You can't reach it from the pathway":
   "門開得太外了,你從通道上構不著它。",
 "The door is already open":
   "門已經開著了。",
 "The door is barred from the other side. Your Open spell has no effect":
   "門從另一側閂住了。你的「開啟」術毫無作用。",
 "The door is barred. Your Open spell has no effect":
   "門閂著。你的「開啟」術毫無作用。",
 "The door is locked":
   "門鎖著。",
 "The door is locked tight, and the sound of your knocks echoes hollowly in the alley, without response":
   "門鎖得死死的,你的敲門聲在巷子裡空洞地迴響,無人應答。",
 "The druggist seems to keep busy at his trade":
   "那藥販似乎一直忙著做他的生意。",
 "The dry heat of the desert seems to have stunted the plant's growth":
   "沙漠乾燥的酷熱似乎遏止了這株植物的生長。",
 "The duty of a guard in Shapeir is to make certain all people are safe from violence or ill-doing":
   "夏皮爾衛兵的職責,是確保所有人免遭暴力與惡行。",
 "The Earth Elemental is a hulking mass of rock whose very footsteps make the city shake":
   "土元素精靈是一團龐然的岩石,光是踏步就能撼動整座城。",
 "The Elemental dodges easily in the open plaza":
   "在開闊的廣場上,那元素精靈輕易就閃開了。",
 "The Elemental earth keeps slipping through your hands":
   "那元素之土不斷從你指縫間滑落。",
 "The Elemental is not in a good position for that":
   "那元素精靈的位置不適合那麼做。",
 "The Elemental's eyes aren't any more watery than usual":
   "那元素精靈的眼睛並不比平常更濕潤。",
 "The eunuch guard, Abu, paces back and forth":
   "那名宦官衛兵阿布來回踱步。",
 "The eunuch looks like a formidable foe":
   "那宦官看起來是個難纏的對手。",
 "The Fire Elemental seems to like that a lot":
   "火元素精靈似乎很受用。",
 "The flagstones of the street are in sordid condition, just like the rest of the city":
   "街上的石板骯髒不堪,跟這城裡其他地方一個樣。",
 "The flagstones of the street feel smooth":
   "街上的石板摸起來光滑。",
 "The flailing, bloodthirsty swordsman looks like he means business":
   "那揮刀亂砍、嗜血的劍客,看來是來真的。",
 "The footwear isn't really different from what you currently have":
   "這鞋子跟你現在穿的其實沒什麼兩樣。",
 "The Force Bolt is just absorbed. It's obviously not effective against liquid life forms":
   "「力箭」被直接吸收了。對液態生命體顯然起不了作用。",
 "The fountain is the heart of the city":
   "噴泉是這座城市的心臟。",
 "The \"fruit\" in the barrel is covered with a thick layer of mildew. Yuck":
   "桶裡那些「水果」蒙著厚厚一層黴。噁!",
 "The Ghoul's head is probably the most disgusting thing you've ever had the misfortune of carrying around":
   "食屍鬼的頭,大概是你這輩子倒楣帶在身上的東西裡最噁心的一個。",
 "The Ghoul would be delighted to shake hands with you. And suck your strength and stamina while doing so":
   "食屍鬼會很樂意跟你握手——順便在握手時吸乾你的力氣與耐力。",
 "The graffiti communicates to you in a different way":
   "那塗鴉以另一種方式向你傳達訊息。",
 "The Griffin has many feathers. Perhaps you can grab one of them":
   "獅鷲有許多羽毛。或許你能抓走其中一根。",
 "The Griffin's feather is grey-striped with silver at the tip. There is brown fur attached to the quill":
   "這根獅鷲羽毛帶著灰色條紋,尖端泛銀,羽根上還黏著棕色的絨毛。",
 "The guard does not respond":
   "衛兵沒有回應。",
 "The guard gives you a quick nod and then walks on":
   "衛兵朝你飛快地點了個頭,便走開了。",
 "The guard gives you a vicious glare before moving on":
   "衛兵惡狠狠地瞪了你一眼,才繼續往前走。",
 "The guard looks even more stone-faced than usual. Maybe you shouldn't be picking your nose in public":
   "那衛兵的臉比平常更鐵青。也許你不該在大庭廣眾下挖鼻孔。",
 "The guard looks official":
   "那衛兵一副公差模樣。",
 "The guards are too busy guarding the palace to listen to you":
   "衛兵們忙著守衛王宮,沒空理你。",
 "The guards march ceaselessly before the gates to the Palace":
   "衛兵在王宮大門前不停地來回踏步。",
 "The guards of this city look like tough, well-disciplined fighters":
   "這城裡的衛兵看起來是一群剽悍、紀律嚴明的戰士。",
 "The guards stand motionless at the gates":
   "衛兵一動不動地守在大門口。",
 "The Guild Hall was the first place Shema and I visited upon our arrival in Spielburg":
   "公會大廳是雪瑪和我抵達史畢柏格後造訪的第一個地方。",
 "The hot desert air scorches your throat as you breathe":
   "你每吸一口氣,熾熱的沙漠空氣便灼著你的喉嚨。",
 "THE ICONS[[INVENTORY: Choose this when you want to view and select from the items you're carrying":
   "圖示說明[[物品欄:想查看並從你攜帶的物品中挑選時,選這個。",
 "The incense is finely ground and has a sweet smelling scent":
   "這薰香研磨得很細,散發著甜美的香氣。",
 "The invisibility spell on the door has already been removed. Your spell has no further effects":
   "門上的隱形咒已經解除了。你的法術不再有任何作用。",
 "The item Saba sold you is a disk that's made of many small strings of reed carefully woven together":
   "薩巴賣給你的是一個圓盤,用許多細小的蘆葦條精心編織而成。",
 "The jerky is prepared with only the finest, most succulent, rock-flattened lizards":
   "這肉乾只選用最上等、最多汁、用石頭壓扁的蜥蜴製成。",
 "The jewelry I sell will make the woman you adore the most beautiful person in the world":
   "我賣的珠寶,能讓你傾慕的女子成為世上最美的人。",
 "The Katta are again afraid to set up their shops. The Creature of Earth grows ever more powerful":
   "卡塔族又不敢開張做生意了。那土之造物越來越強大。",
 "The Katta are most thankful that you have come to Shapeir":
   "卡塔族對你來到夏皮爾感激不盡。",
 "The Katta gave you this sapphire pin in thanks for your service to their kind":
   "卡塔族送你這枚藍寶石別針,感謝你為他們族人效力。",
 "The Katta is thin and it looks like he's recently been beaten":
   "這卡塔族人瘦削不堪,看樣子近來挨過打。",
 "The Katta just stares suspiciously at you":
   "那卡塔族人只是滿腹狐疑地盯著你。",
 "The Katta merchant has no need of that":
   "那卡塔族商人不需要那個。",
 "The Katta merchants could not set up in the plaza outside because of the fire this morning":
   "因為今早那場火,卡塔族商人沒法在外頭的廣場擺攤。",
 "Shema just gave you this spare change of clothes for Raseir. You do not want to store them now":
   "雪瑪才剛給你這套去拉希爾用的備用衣裳。你現在不想收起來。",
 "Thank you, a thousand thank-yous. It is with your support that I may continue my vital work":
   "謝謝你,千恩萬謝。全靠你的支持,我才能繼續這要緊的工作。",
 "The ice is now very relaxed":
   "那冰塊現在很放鬆。",
 # --- 第十八批 ---
 "The Katta nods to acknowledge your presence":
   "那卡塔族人點頭示意,表示注意到你了。",
 "The Katta quickly bows to acknowledge your greeting and then moves on":
   "那卡塔族人迅速一鞠躬回應你的問候,便走開了。",
 "The Katta's Tail Inn is in the Gate Plaza":
   "「卡塔之尾客棧」在城門廣場。",
 "The Katta's Tail Inn is in this very plaza":
   "「卡塔之尾客棧」就在這座廣場上。",
 "The kitchen is closed already. Your tummy will have to wait until tomorrow morning":
   "廚房已經打烊了。你的肚子只能等到明天早上。",
 "The lamp burns brightly, lighting this otherwise darkened dead-end":
   "那盞燈燃得正旺,照亮了這條原本漆黑的死巷。",
 "The last thing this window needs is a set of greasy fingerprints smeared across its surface":
   "這扇窗最不需要的,就是表面被抹上一排油膩的指紋。",
 "The leather merchant frowns at you":
   "那皮革商朝你皺眉。",
 "The leonine creature before you looks ferocious and kindly at the same time":
   "你面前這頭獅形生物,看起來既兇猛又和善。",
 "The Liontaur looks calmly back at you":
   "那獅人平靜地回望你。",
 "The magic lamp is not useful here":
   "魔法神燈在這兒派不上用場。",
 "The Magic Shop owner might help you with such questions":
   "魔法店的老闆或許能解答你這類問題。",
 "The man gives you a scowl that could sink a sub":
   "那人朝你擺出一張足以擊沉潛艇的臭臉。",
 "The man is built just like an acrobat":
   "那人一身體格活像個雜耍藝人。",
 "The man looks to be dazed for some reason":
   "那人不知怎地一臉茫然。",
 "The map only works in the streets and plazas":
   "地圖只在街道與廣場上管用。",
 "The mechanic doesn't look like he's willing to interact with you, much less shake hands":
   "那技工看來無意搭理你,更別說握手了。",
 "The memory of a poet is long for those who aid him":
   "詩人對助他之人,記性可長著呢。",
 "The merchant looks at you strangely":
   "那商人古怪地看著你。",
 "The mere thought of putting your hand in there disgusts you":
   "光想到要把手伸進那裡頭,你就一陣噁心。",
 "The message reads:[[\"Misfortune will arise when the dinar hits the fountain.\"":
   "上頭寫著:[[「當第納爾落入噴泉,厄運將至。」",
 "The message reads:[[\"Rent your own Harem at Lou's.\"":
   "上頭寫著:[[「到老盧家,租你專屬的後宮。」",
 "The message reads:[[\"Those who dare to walk the fiery road will not return unscathed.\"":
   "上頭寫著:[[「膽敢踏上烈火之路者,難以全身而退。」",
 "The message reads:[[\"Those who turn onto the dark, starry path will face great peril.\"":
   "上頭寫著:[[「轉入那條漆黑星路者,將面臨莫大凶險。」",
 "The musician has no need of your Spielburgian money":
   "那樂師不需要你的史畢柏格錢幣。",
 "The musician nods and smiles while he plays":
   "那樂師一邊演奏,一邊點頭微笑。",
 "The musician seems too busy to answer you":
   "那樂師似乎忙得無暇答理你。",
 "The musician would not be interested in that":
   "那樂師對那個不會感興趣。",
 "Then honey is poured upon it":
   "接著淋上蜂蜜。",
 "Then it is quickly cooked over the brazier there":
   "然後在那邊的炭爐上迅速烤熟。",
 "Then you may leave, mere user of magic":
   "那你可以走了,區區一個耍魔法的。",
 "Then you must choose another sponsor":
   "那你得另選一位引薦人。",
 "The odd character at this stand seems vaguely familiar":
   "這攤子上那個古怪傢伙,看著有點面熟。",
 "The once beautiful pot now lies in ruins":
   "那只曾經精美的陶罐,如今已成一堆碎片。",
 "The only response from the Air Elemental is a low, ominous hum":
   "風元素精靈唯一的回應,是一陣低沉而不祥的嗡鳴。",
 "The only thing it can tell you is that it is in a state beyond repair":
   "它唯一能告訴你的,就是它已經壞到沒法修了。",
 "The only thing they seem interested in is eating straw":
   "牠們似乎唯一感興趣的,就是吃草料。",
 "The palace doors are barred securely from inside":
   "王宮的大門從內側牢牢閂住了。",
 "The Palace is a marvelous place to work":
   "王宮是個極好的做事之處。",
 "The Palace of the Emir looms ominously over the city":
   "埃米爾的宮殿不祥地高踞於城市之上。",
 "The Palace of the Sultan is a truly magnificent sight":
   "蘇丹的宮殿著實是一派恢宏景象。",
 "The pin is a token of the Katta's trust in you, O Hero":
   "英雄啊,這枚別針是卡塔族對你信任的信物。",
 "The place is the window on your left as you first enter the Fountain Plaza from here":
   "那地方,是你從這兒初進噴泉廣場時左手邊的那扇窗。",
 "The plant seems to have adapted to the desert heat":
   "這株植物似乎已經適應了沙漠的酷熱。",
 "The plaza is too open an area to capture and contain a Fire Elemental":
   "廣場太空曠了,沒法捕捉並困住火元素精靈。",
 "The pleasure is all mine, Hero":
   "這是我的榮幸,英雄。",
 "The Poet is bothered more by the thief than by the loss of money":
   "比起損失的錢,詩人更在意那個小偷。",
 "The Poet Omar is honored by your greetings and wishes you the same in return":
   "詩人奧瑪爾很榮幸收到你的問候,也以同樣的祝福回敬你。",
 "The pot you obtained from Toshur is carefully crafted and very smooth":
   "你從托舒爾那兒得來的陶罐做工精細、十分光滑。",
 "The pot you obtained from Toshur is colorful and very smooth":
   "你從托舒爾那兒得來的陶罐色彩繽紛、十分光滑。",
 "The presence of fetid trash piles makes this a less than pleasant area to navigate through":
   "一堆堆惡臭的垃圾,讓這地方走起來實在不怎麼舒坦。",
 "The quantity I have given you should suffice":
   "我給你的份量應該夠了。",
 "The rations are tasteless but filling":
   "這乾糧雖然無味,倒挺管飽。",
 "There are merchants for almost anything in this town":
   "這鎮上幾乎什麼東西都有商人在賣。",
 "There are no clothes hanging around here. Besides, you still have your own":
   "這附近沒晾著衣服。再說,你自己的還在呢。",
 "There are no games to restore":
   "沒有可讀取的存檔。",
 "There are no sounds coming from beyond this door":
   "這門後沒有半點聲響。",
 "There are too many guards to fight":
   "衛兵太多了,打不過。",
 "There doesn't seem to be anyone on the other side":
   "另一側似乎沒有人。",
 "The presence of fetid trash piles make this a less than pleasant area to navigate through":
   "一堆堆惡臭的垃圾,讓這地方走起來實在不怎麼舒坦。",
 "The item Saba sold you is a disk that's made of many small strings of reed carefully woven together":
   "薩巴賣給你的是個圓盤,用許多細小的蘆葦條精心編成。",
 # --- 第十九批 ---
 "There. I do for you what I would not for another. This is a gift for all you have done for the city":
   "好了。我為你做的,是別人求都求不來的。這是給你的禮物,謝你為這座城所做的一切。",
 "There is a certain irony in the fact that you partially returned the favor":
   "你算是部分回報了這份人情,這事透著幾分諷刺。",
 "There is a magical aura around the door":
   "門的四周縈繞著一股魔法氣息。",
 "There is a strong enchantment on the beast and upon the cage":
   "那野獸與牢籠上都施著強大的魔咒。",
 "There is incredibly powerful magic going on in the room beyond the door at the top of the stairs":
   "樓梯頂端那扇門後的房裡,正進行著無比強大的魔法。",
 "There is no answer to your knocking":
   "你敲門,無人應答。",
 "There is no magical trap or lock on the cage door. Your Trigger spell has no effect":
   "籠門上沒有魔法陷阱或鎖。你的「觸發」術毫無作用。",
 "There is no need for that. I am a poet rich in spirit already":
   "不必了。我是個精神上已然富足的詩人。",
 "There is no need to return it yet, Hero-friend. Please keep it until you decide to end your stay here":
   "還不必歸還,英雄朋友。請留著它,直到你決定結束在此的停留。",
 "There is no noise coming from beyond the door. It doesn't sound like the residents are home":
   "門後沒有半點聲響。聽起來屋裡的人不在家。",
 "There is no response from the inside":
   "裡頭沒有回應。",
 "There is nothing in your storage chest to retrieve":
   "你的儲物箱裡沒有可取出的東西。",
 "There is no time to rest. You have a city to save":
   "沒空休息。你還有一座城要救!",
 "There is only silence from beyond the door":
   "門後唯有一片寂靜。",
 "There may be something in this city worth uprooting, but it isn't the local vines":
   "這城裡或許有什麼值得連根拔除,但絕不是這些當地的藤蔓。",
 "There's a thick layer of dust on the sconce":
   "那壁燈座上積了厚厚一層灰。",
 "There's a variety of boots for sale at this stand":
   "這攤子上賣著各式各樣的靴子。",
 "The residence has been abandoned. Nobody will answer your calls":
   "這宅子已經荒廢了,沒人會應你的呼喚。",
 "There's no keyhole on the outside of this door to pick":
   "這門外側沒有可以撬的鑰匙孔。",
 "There's no need. He's already being paid for his services here by Shameen":
   "不必了。他在這兒的服務,沙明已經付過錢了。",
 "There's no need to drop more incense -- the Fire Elemental is well inside the alley now":
   "不必再丟薰香了——火元素精靈現在已經好好待在巷子裡了。",
 "There's no need to go around buying such trinkets unless you're planning on wooing someone":
   "除非你打算追求誰,否則沒必要到處買這種小玩意兒。",
 "There's no need to go licking someone else's boots":
   "沒必要去舔別人的靴子。",
 "There's no need to purchase any more jewelry from the merchant":
   "沒必要再跟那商人買更多珠寶了。",
 "There's no need to throw things around an empty shop":
   "沒必要在一家空店裡亂扔東西。",
 "There's no point in resting here when your own room is a few steps away":
   "你自己的房間就在幾步之遙,何必在這兒歇。",
 "There's no point in trying that here. The door is obviously magical and has no lock to pick":
   "在這兒試那個沒用。這門明顯帶魔法,根本沒鎖可撬。",
 "There's no reason to return the bellows to Issur. Besides, you may still need them":
   "沒理由把風箱還給伊蘇。再說,你說不定還用得上。",
 "There's nothing more inside":
   "裡頭沒別的了。",
 "There's nothing to do there":
   "那兒沒什麼好做的。",
 "There's nothing to Fetch there":
   "那兒沒什麼好「取」的。",
 "There's nothing to open there":
   "那兒沒什麼好開的。",
 "There's nothing worth fetching":
   "沒什麼值得取的。",
 "There's no time for questions. You've got to do something":
   "沒空問東問西。你得做點什麼。",
 "There's no time for that":
   "沒空管那個。",
 "There's no time for that now":
   "現在沒空管那個。",
 "There's no time for that now, Hero":
   "現在沒空管那個,英雄!",
 "There's no time to rest now":
   "現在沒空休息。",
 "There's not much more in stock that's of any use to you":
   "庫存裡再沒什麼對你有用的了。",
 "There's no water left in your waterskin":
   "你的水袋裡一滴水也不剩了。",
 "There's no way you can reach Ad Avis and there is a magical barrier surrounding the room":
   "你根本碰不到阿德·阿維斯,何況這房間四周還圍著一道魔法屏障。",
 "There's only silence coming from the other side":
   "另一側只傳來一片寂靜。",
 "There's still some earth left in this worn case, but there's no sign of any plant life":
   "這只破舊的盆裡還剩些泥土,卻不見半點植物的跡象。",
 "There was talk that the storm was magical in nature and was conjured up":
   "有人說那場風暴本質上是魔法,是被召喚出來的。",
 "There will be a caravan to Raseir in 1 day":
   "一天後將有一支前往拉希爾的商隊。",
 "The rock is made of red sandstone":
   "這塊石頭是紅砂岩做的。",
 "The rock is shaped like the head of a Griffin":
   "這塊石頭形狀像獅鷲的頭。",
 "The rock looks, predictably, much like any other desert rock":
   "不出所料,這塊石頭看起來跟別的沙漠石頭沒兩樣。",
 "The rock reflects the desert heat":
   "這塊石頭反射著沙漠的熱氣。",
 "The rocks shake, but they are still well-supported at the base":
   "那些岩石搖晃著,基座卻依然穩固。",
 "The sapphire pin has a value of 500 dinars. Would you care to bargain":
   "這枚藍寶石別針價值五百第納爾。你想討價還價嗎?",
 "The Saurus can't hear you from here":
   "從這兒索魯斯聽不見你。",
 "The Saurus meat is first dipped in spicy paprika":
   "索魯斯肉要先裹上一層辣紅椒粉。",
 "The save directory is full. You must replace an existing game:":
   "存檔目錄已滿,你必須覆蓋一個現有的存檔:",
 "The searing desert heat seems to draw the water right out of you":
   "灼人的沙漠酷熱,彷彿要把你體內的水分全榨乾。",
 "These impressive hedges have been cleverly manicured to conform with the upward direction of the walls":
   "這些氣派的樹籬經過巧手修剪,順著牆向上的走勢成形。",
 "The Seller of Sauruses will be here tomorrow. Perhaps you can purchase one then":
   "賣索魯斯的明天會來。或許到時你能買一頭。",
 "These look like beautiful but toxic oleander flowers":
   "這些看起來是美麗卻有毒的夾竹桃花。",
 "These make good salad for dinner. That be very kind of you":
   "這些拿來當晚餐的沙拉正好。你真是太好心了。",
 "These ornate scimitars make poor weapons, but a valuable decoration":
   "這些華麗的彎刀當兵器不行,當擺飾倒挺值錢。",
 "These traditional windows are arch-shaped and have been built into the wall":
   "這些傳統樣式的窗子呈拱形,嵌在牆裡。",
 "These traditional windows are square-shaped and have been built into the wall":
   "這些傳統樣式的窗子呈方形,嵌在牆裡。",
 "These traditional wooden windows are square-shaped and have been built into the wall":
   "這些傳統的木窗呈方形,嵌在牆裡。",
 "These vines seem to have been cut off near the root and are now withering away in the harsh sun":
   "這些藤蔓似乎被攔腰齊根斬斷,如今正在烈日下枯萎。",
 "The shiny brass lamp is engraved on the bottom: 'Aladdin Lamp Co.'":
   "這盞亮晶晶的銅燈底部刻著:「阿拉丁神燈公司」。",
 "The shop owner glares back at you. He looks strong and decidedly unfriendly":
   "店主回瞪你一眼。他看起來壯實,而且擺明了不友善。",
 "The shutters are barely managing to remain in place. Don't make matters worse":
   "那百葉窗勉強還掛在原處。別把事情弄得更糟。",
 "The shutters are just fine the way they are":
   "那百葉窗就這樣挺好的。",
 "The shutters on this window look ready to fall out of their hinges at any moment":
   "這扇窗的百葉,看起來隨時會從鉸鏈上掉下來。",
 "The sign looks tattered and worse for wear":
   "那招牌看起來破爛不堪、飽經風霜。",
 # --- 第二十批 ---
 "The sign of the Scorpion":
   "天蠍之象。",
 "The soles of your boots seem unable to withstand any more damage":
   "你靴底似乎再也經不起任何磨損了。",
 "The soles of your boots show signs of heavy deterioration":
   "你的靴底已顯出嚴重磨損的跡象。",
 "The sound of your footsteps seem to echo \"water\" in your ears":
   "你的腳步聲在耳中迴響,彷彿在喊著「水」。",
 "The spell does not seem to affect the wind":
   "這法術似乎對風起不了作用。",
 "The spell on the room prevents the powder from igniting":
   "這房間的咒法使得粉末無法點燃。",
 "The star pattern known as the Dragon":
   "被稱作「巨龍」的星象。",
 "The stars here appear to form a Dark Hand":
   "這裡的星辰似乎排成了一隻「黑手」。",
 "The strong bars prevent any would-be intruders from entering":
   "那堅固的柵欄擋住了任何意圖闖入者。",
 "The stuff inside the barrel would have no trouble crawling out on its own if it was so inclined":
   "桶裡那玩意兒只要願意,自己爬出來毫不費勁。",
 "The Sultan (May He Reign Forever!) is truly wise and powerful":
   "蘇丹(願他永世統治!)著實英明而強大。",
 "The sum doesn't balance. COD or DOA. Pay or go away":
   "帳對不上。貨到付款,否則一拍兩散。給錢,不然走人。",
 "The summer heat is dangerous for those who are not used to it":
   "對不習慣的人來說,這夏日酷熱十分危險。",
 "The sun is bright and the day is hot already this morning":
   "今早陽光刺眼,天氣已經熱了起來。",
 "The supernatural being looks like a skeleton with pieces of rotting flesh still attached to its bones":
   "那超自然之物像具骷髏,骨頭上還黏著一塊塊腐肉。",
 "The surgeon general warns...":
   "衛生署長警告……",
 "The swords are too firmly attached to the wall to Fetch":
   "那些劍牢牢釘在牆上,「取物」術取不下來。",
 "The taste will sell itself":
   "這味道自會替自己招攬生意。",
 "The tenants are either not at home or unwilling to let you in":
   "屋裡的人若不是不在家,就是不願讓你進門。",
 "The Terrorsaurus is too stupid to understand you":
   "那頭恐魯斯蠢得聽不懂你的話。",
 "The Terrorsaurus looks vicious, mean, and quite hungry":
   "那頭恐魯斯看起來兇狠、惡毒,而且相當飢餓。",
 "The tingling sensation is gone. It seems the unguent wore off":
   "那刺麻感消失了。看來藥膏的效力過了。",
 "The townsperson doesn't seem to understand you":
   "那市民似乎聽不懂你的話。",
 "The townsperson looks nondescript":
   "那市民其貌不揚,毫無特徵。",
 "The trash can's aroma suits its appearance very well":
   "那垃圾桶的氣味,跟它的賣相還真相稱。",
 "The tree does not respond":
   "那棵樹沒有反應。",
 "The tree rustles its leaves":
   "那棵樹沙沙地擺動著葉子。",
 "The trip from Shapeir to Sangerhafen had already taken several months and winter was approaching rapidly":
   "從夏皮爾到桑格哈芬這趟路已走了好幾個月,寒冬又迅速逼近。",
 "The wall appears to have a spell placed upon it":
   "那面牆似乎被施了咒。",
 "The wall at the end of the alley appears to have been damaged":
   "巷子盡頭那面牆似乎受了損。",
 "The wall is carrying a torch for you":
   "那面牆對你「情有獨鍾」(還幫你舉著火把呢)。",
 "The Warrior's Diary contains your recorded experiences during battle":
   "「戰士日記」記錄著你在戰鬥中的種種經歷。",
 "The warrior woman cradles baby Simba in her arms":
   "那女戰士懷裡搖著小辛巴。",
 "The warrior woman stands tall and proud":
   "那女戰士站得挺拔而自豪。",
 "The Water Elemental destroys all who go near her":
   "水元素精靈會毀滅一切靠近她的人。",
 "The Water Elemental doesn't seem to be affected by your spell":
   "水元素精靈似乎不受你的法術影響。",
 "The Water Elemental in the fountain of town is the greatest of misfortunes":
   "水元素精靈進了城中的噴泉,正是天大的災禍。",
 "The weapons at this stand resemble the ones the desert brigands use":
   "這攤子上的兵器,跟沙漠強盜用的那些很像。",
 "The wind grows stronger, and the merchants had great difficulty setting up their stands today":
   "風越颳越大,今天商人們擺攤都吃足了苦頭。",
 "The wind no longer blows as fiercely as before":
   "風不再像先前颳得那麼猛了。",
 "The window doesn't open up to you":
   "那扇窗不為你而開。",
 "The window doesn't open up to your words":
   "那扇窗不為你的話語而開。",
 "The window is always open. The climate here is always hot":
   "這扇窗總是開著,這兒的氣候向來炎熱。",
 "The window is barred from the inside":
   "那扇窗從內側閂住了。",
 "The window lacks curtains or shutters you can fiddle with":
   "這扇窗沒有可供你擺弄的窗簾或百葉。",
 "The wise old Dervish gives you a funny look, but says nothing. Now you just feel silly":
   "那睿智的老苦行僧古怪地瞅了你一眼,卻什麼也沒說。這下你只覺得自己很蠢!",
 "The Wizard's Institute of Technocery is for real Wizards rather than the real world":
   "巫師技術學院是給真正的巫師待的,可不是給「真實世界」待的!",
 "The woman is very attractive with her dark, curly hair and lovely figure. She smiles invitingly at you":
   "那女子一頭深色鬈髮、身段曼妙,十分迷人,正朝你嫣然一笑、頗為撩人。",
 "The wooden bars prevent the door from being opened, even if there was someone on the other side":
   "那木栅擋住了門,就算另一側有人也開不了。",
 "The words of departure are what I do hear,[  Farewell 'til the next time you lend me your ear":
   "我聽見的,是道別之語,[  就此別過,待你下回再側耳傾聽。",
 "They do not respond":
   "它們沒有反應。",
 "They obviously improve your looks. Zayishah just giggles at you":
   "它們顯然讓你好看了些。札伊莎只是對你咯咯直笑。",
 "They probably don't want to be petted":
   "牠們大概不想被摸。",
 "They travel very well":
   "牠們很耐遠行。",
 "This beautiful emerald-studded silver bowl was once the property of the silversmith Abu bin Ma'amar":
   "這只鑲著翡翠的精美銀碗,曾是銀匠阿布·賓·馬阿瑪爾的財產。",
 "This business has no major hang-ups... or does it":
   "這買賣沒什麼大「掛」礙……還是有?",
 "This does seem like a good place. You curl up near the pool and soon fall asleep":
   "這地方看來不錯。你在水池邊蜷起身子,很快便睡著了。",
 "This drink sizzles in the glass":
   "這飲料在杯子裡嘶嘶作響。",
 "This guy is the spitting-image of Prince Ali-Ababwa":
   "這傢伙活脫脫就是阿里·阿巴布瓦王子的翻版。",
 "This guy looks like he could play the piano, but strangely":
   "這傢伙看起來會彈鋼琴,只是彈得有點怪。",
 "This guy looks like he's been in the desert too long":
   "這傢伙看起來在沙漠裡待得太久了。",
 "This is a fine sword from the Weapon Shop of Issur":
   "這是一把出自伊蘇兵器店的好劍。",
 "This is a leather waterskin containing the essence of the Water Elemental":
   "這是一個皮水袋,裡頭封著水元素精靈的精華。",
 "This is not a good opportunity to use your rope":
   "現在不是用繩子的好時機。",
 "This is not a good time for that":
   "現在做那個不是時候。",
 "This is not a good time to practice your throwing":
   "現在不是練投擲的好時機。",
 # --- 第二十一批 ---
 "This is not a safe place to rest":
   "這裡不是個安全的歇腳處。",
 "This is not a safe place to sleep":
   "這裡不是個安全的睡覺地方。",
 "This isn't a good moment to socialize":
   "現在不是交際攀談的好時機。",
 "This isn't the best place to practice your Levitate spell":
   "這裡不是練「飄浮」術的好地方。",
 "This is the harem girl's hand mirror":
   "這是那後宮女子的手鏡。",
 "This is the last page":
   "這是最後一頁。",
 "This is your title and registration for your trusty riding Saurus":
   "這是你那頭可靠坐騎索魯斯的所有權證與登記文件。",
 "This key can't be assigned to a combat action":
   "這個按鍵不能指派給戰鬥動作。",
 "This key doesn't fit that lock":
   "這把鑰匙跟那個鎖不合。",
 "This lamp of brass should serve you against the thing of fire. It is now your own":
   "這盞銅燈該能助你對付那團火之物。如今它歸你了。",
 "This leather purse uses a drawstring for closure":
   "這個皮錢袋用束口繩封口。",
 "This local reed basket is simple but elegant":
   "這個當地的蘆葦籃簡樸卻雅致。",
 "This make very fine wall trophy. Asante, Hero of Spielburg":
   "這拿來當牆上的戰利品很不錯。Asante(謝謝),史畢柏格的英雄。",
 "This merchant has various vests for sale":
   "這商人賣著各式背心。",
 "This merchant offers purses for sale":
   "這商人賣著錢袋。",
 "This merchant sells clay pots":
   "這商人賣陶罐。",
 "This ornament is the black figure of a bird, a falcon":
   "這件飾品是一隻黑色鳥形雕像,一隻獵鷹。",
 "This ornate window has lost much of its original beauty":
   "這扇華麗的窗,已失去大半原有的美。",
 "This 'painting' shows the city of Shapeir under a starry sky":
   "這幅「畫」描繪著星空下的夏皮爾城。",
 "This part of the wall seems to be in particularly bad shape":
   "這一段牆似乎特別殘破。",
 "This person isn't interested in the object you offer":
   "這人對你拿出的東西不感興趣。",
 "This residence appears to have been abandoned, as its door has been barred with several wooden planks":
   "這宅子似乎已遭遺棄,門被好幾塊木板封死了。",
 "This sign symbolizes the business owner's trade":
   "這招牌象徵著店主所做的行當。",
 "This square, flat box is made from material that somewhat resembles paper, except it is harder":
   "這只方扁的盒子,材質有點像紙,只是更硬些。",
 "This stand sells golden bracelets, rings, and necklaces":
   "這攤子賣金手鐲、戒指和項鍊。",
 "This street has been barricaded off. The sign reads: \"Road closed by order of Khaveen.\"":
   "這條街被封了起來。告示寫著:「奉哈維因之命,此路封閉。」",
 "This torch is not the light of your life":
   "這支火把可不是你的「此生摯愛」。",
 "This vase houses a lovely plant":
   "這只花瓶裡養著一株可愛的植物。",
 "This wealthy-looking Katta is Tiram, the carpet merchant":
   "這個看來富裕的卡塔族人,是賣地毯的商人提拉姆。",
 "This will only take me one second":
   "我一秒鐘就好。",
 "This will take many hours, so you will need to come back some other day":
   "這得花上好幾個鐘頭,你得改天再來。",
 "This window frame has seen better days":
   "這扇窗框早已風光不再。",
 "Those that can't, tell others what to do":
   "辦不到的人,就只會指使別人怎麼做?",
 "Through this door lies the other side":
   "這門之後,便是另一側。",
 "Through this door's keyhole, a constant mournful wail fills the room":
   "透過這門的鑰匙孔,一陣不止歇的哀號充塞著整個房間。",
 "Throwing knives when guards are around is not the wisest course of action":
   "衛兵在旁時擲刀,可不是什麼明智之舉。",
 "Throwing rocks when guards are around is not the wisest course of action":
   "衛兵在旁時擲石,可不是什麼明智之舉。",
 "Throw it quickly at your target. Try not to miss. It will do a lot of damage when it strikes and ignites":
   "快把它擲向目標,別失手。它擊中並炸開時威力可不小。",
 "Today is good day for fighting practice. Every day is good day for practice":
   "今天是練武的好日子。其實天天都是練武的好日子。",
 "To get past the guards outside, you have only to make the 'sign.'":
   "想通過外頭的衛兵,你只需比出那個「暗號」。",
 "\"Tomorrow night is your last night. You'll get your final orders then. Be seeing you.\"":
   "「明晚是你的最後一晚。到時你會收到最終指令。回頭見。」",
 "Tonight's meal is honeyed lamb with almonds and curried chicken. It is hoped you will enjoy yourself":
   "今晚的菜色是蜜汁杏仁羊肉與咖哩雞。願您吃得盡興。",
 "Top o' the morning to ya! Mar haba! What's new, Pussycat":
   "早安啊您吶!Mar haba(你好)!最近如何呀,小貓咪?",
 "To serve you is an honor":
   "能為您效勞是一種榮幸。",
 "Toshur is the local pottery merchant":
   "托舒爾是本地的陶器商。",
 "Type a name to save as:":
   "輸入要存檔的名稱:",
 "Uh oh. The guards have found you prowling outside at night. You're immediately taken into custody":
   "糟了。衛兵發現你夜裡在外頭遊蕩,你當場就被收押了。",
 "Uh oh. The guards have gotten tired of you hanging around here. You're taken into custody":
   "糟了。衛兵受夠了你在這兒晃來晃去,把你收押了。",
 "Uhura greets you with an ominous glare":
   "烏胡拉以一記不祥的瞪視迎接你。",
 "Uhura isn't interested in that item":
   "烏胡拉對那件東西不感興趣。",
 "Unfortunately, the guard is upon you before your spell takes effect":
   "可惜,你的法術還沒生效,衛兵就撲到你面前了。",
 "Unfortunately, your foe is upon you before your spell takes effect":
   "可惜,你的法術還沒生效,敵人就撲到你面前了。",
 "Unlike a certain King Edward of Daventry, you don't plan on losing this mirror":
   "你可不打算像達文垂的某位愛德華王那樣,把這面鏡子弄丟。",
 "Unlike heads, two layers of unguent are no better than one. But it didn't harm you either":
   "跟頭不一樣,藥膏抹兩層並不比一層好,不過抹了也無妨。",
 "Unlike heads, two poison cure pills are no better than one. But the pill does no harm either":
   "跟頭不一樣,解毒藥丸吃兩顆並不比一顆好,不過吃了也無妨。",
 "Use the counterslash to retaliate against blockable attacks by your adversary":
   "用「反斬」來回擊對手那些可格擋的攻擊。",
 "Use the rising slash to turn the tables on an opponent who relies on high attacks":
   "用「上挑斬」來反制慣使上段攻擊的對手。",
 "Very well, if such is your choice. What is it that you wish to know":
   "好吧,既然你這麼選。你想知道什麼?",
 "Vines cling to the walls, twisting their way skyward":
   "藤蔓攀附在牆上,扭著身子向天空伸展。",
 "Wall: stops two attacks":
   "壁壘:擋下兩次攻擊",
 "Warning! Don't speak to the awning":
   "警告!別跟那遮篷說話。",
 "Warning: items you drop will be lost permanently":
   "警告:你丟下的物品將永久消失。",
 "We are happy you have been our guest and even happier you have been our friend":
   "你做我們的客人,我們很高興;你做我們的朋友,我們更是欣喜。",
 "We are most honored by your presence at our inn, Hero of Spielburg":
   "史畢柏格的英雄,您光臨我們的客棧,我們深感榮幸。",
 "We are very fastidious when working, and you will find no Katta hairs in the dates":
   "我們做事一絲不苟,你在椰棗裡絕找不到半根卡塔族的毛。",
 "We do not accept intruders in our tower":
   "我們的塔不容入侵者。",
 "We do not accept liars in our tower":
   "我們的塔不容說謊者。",
 "Welcome back. If you see something that interests you, let me know":
   "歡迎回來。你要是看上了什麼,就告訴我。",
}

resolved=[]
for sub, zh in BATCH.items():
    hits=[c for c in corpus if sub in c]
    if len(hits)==1:
        resolved.append((hits[0], zh))
    elif len(hits)==0:
        print(f"  ⚠ 找不到: {sub[:45]}", file=sys.stderr)
    else:
        print(f"  ⚠ 命中 {len(hits)} 筆(子串不唯一),跳過: {sub[:40]}", file=sys.stderr)

# disclaimer + 標題 從舊 tsv 保留(含特殊格式,不在 corpus_clean)
keep=[]
for line in open('tools/translation.tsv', encoding='utf-8'):
    line=line.rstrip('\n')
    if line.startswith('DISCLAIMER') or line.startswith('Quest for Glory II\t'):
        keep.append(tuple(line.split('\t',1)))

seen=set(); rows=keep+resolved
with open('tools/translation.tsv','w',encoding='utf-8') as f:
    f.write("# 英雄傳奇II 繁中翻譯  英文原文<TAB>繁體中文\n")
    f.write("# 語感:參照《軟體世界》三大誌生動口語;專名音譯見 CONTEXT.md\n")
    for s,d in rows:
        if s in seen: continue
        seen.add(s); f.write(f"{s}\t{d}\n")
print(f"翻譯總計 {len(seen)} 條(保留 {len(keep)} + 主線批次 {len(resolved)})")
