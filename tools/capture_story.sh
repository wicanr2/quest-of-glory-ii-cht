export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq xvfb xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out; rm -f /out/story.txt
/src/scummvm --config=/out/sv.ini --add --path=/game >/dev/null 2>&1 || true
python3 - <<'PY'
import configparser
c=configparser.ConfigParser(); c.optionxform=str; c.read('/out/sv.ini')
d=c.setdefault('qfg2agdi',{})
d['ags_dump_strings']='/out/story.txt'
d.pop('translation',None)   # 抓原文,先不套翻譯
with open('/out/sv.ini','w') as f: c.write(f)
PY
timeout 150 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/run.log &
sleep 9
xdotool key --clearmodifiers Return; sleep 1          # 過 disclaimer
xdotool key --clearmodifiers i; sleep 2               # 選 Introduction
# 旁白一頁頁推進(space/Return/click),抓滿
for i in $(seq 1 60); do xdotool key --clearmodifiers space Return; xdotool click 1; sleep 1.6; done
pkill -f scummvm 2>/dev/null; sleep 1
echo "=== story.txt 不重複字串數 ==="; sort -u /out/story.txt 2>/dev/null | wc -l
echo "=== 較長的字串(>30 字元,劇情旁白)==="
sort -u /out/story.txt 2>/dev/null | awk 'length>30' | head -40
