export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get install -y -qq xvfb >/dev/null 2>&1
Xvfb :99 -screen 0 640x480x24 >/dev/null 2>&1 & sleep 2
cd /out; rm -f /out/static.txt
/src/scummvm --config=/out/sv.ini --add --path=/game >/dev/null 2>&1 || true
python3 - <<'PY'
import configparser
c=configparser.ConfigParser(); c.optionxform=str; c.read('/out/sv.ini')
d=c.setdefault('qfg2agdi',{}); d['ags_dump_static']='/out/static.txt'; d.pop('translation',None); d.pop('ags_dump_strings',None)
with open('/out/sv.ini','w') as f: c.write(f)
PY
timeout 25 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/run.log &
sleep 12; pkill -f scummvm; sleep 1
echo "=== static.txt 行數/不重複 ==="; wc -l /out/static.txt 2>/dev/null; sort -u /out/static.txt 2>/dev/null | wc -l
