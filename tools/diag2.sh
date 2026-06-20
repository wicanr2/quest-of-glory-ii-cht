export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
which xdotool import >/dev/null || echo "WARN: 工具缺"
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out; rm -f /out/ags_dump.txt
/src/scummvm --config=/out/sv.ini --add --path=/game >/dev/null 2>&1 || true
python3 - <<'PY'
import configparser
c=configparser.ConfigParser(); c.optionxform=str; c.read('/out/sv.ini')
c.setdefault('qfg2agdi',{})['ags_dump_strings']='/out/ags_dump.txt'
open('/out/sv.ini','w').write(''); 
with open('/out/sv.ini','w') as f: c.write(f)
PY
timeout 40 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/run.log &
sleep 9; xdotool key Return; sleep 1; xdotool key i; sleep 7
import -window root /out/intro.png 2>/dev/null
for i in $(seq 1 10); do xdotool key Return space; sleep 1.3; done
pkill -f scummvm; sleep 1
echo "=== CHT-DIAG ==="; grep -i "CHT-DIAG" /tmp/run.log | head
echo "=== dump ==="; wc -l /out/ags_dump.txt 2>/dev/null && { echo "unique:"; sort -u /out/ags_dump.txt | wc -l; } || echo 無檔
