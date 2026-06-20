export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out
/src/scummvm --config=/out/sv.ini --add --path=/game >/dev/null 2>&1 || true
python3 - <<'PY'
import configparser
c=configparser.ConfigParser(); c.optionxform=str; c.read('/out/sv.ini')
d=c.setdefault('qfg2agdi',{})
d['translation']='chinese'
d.pop('ags_dump_strings',None)
with open('/out/sv.ini','w') as f: c.write(f)
PY
timeout 30 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/run.log &
sleep 4;  import -window root /out/cht_04s.png 2>/dev/null
sleep 2;  import -window root /out/cht_06s.png 2>/dev/null
sleep 3;  import -window root /out/cht_09s.png 2>/dev/null
pkill -f scummvm; sleep 1
echo "=== CJK 載入訊息 / translation ==="; grep -iE "CJK|translation|chinese|\.tra|trans" /tmp/run.log | head
