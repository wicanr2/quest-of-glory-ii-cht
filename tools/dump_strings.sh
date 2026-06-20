set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq && apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/tmp/xvfb.log 2>&1 &
sleep 2
cd /out
rm -f /out/ags_dump.txt
CFG=/out/sv.ini; rm -f "$CFG"
/src/scummvm --config="$CFG" --add --path=/game >/tmp/add.log 2>&1 || true
TARGET=qfg2agdi
# dump 路徑放在 target domain
python3 - "$CFG" <<'PY'
import sys,configparser
c=configparser.ConfigParser(); c.optionxform=str; c.read(sys.argv[1])
if 'qfg2agdi' not in c: c['qfg2agdi']={}
c['qfg2agdi']['ags_dump_strings']='/out/ags_dump.txt'
with open(sys.argv[1],'w') as f: c.write(f)
PY
# 啟動,進 Introduction(按 i)觸發劇情文字,再回選單
timeout 45 /src/scummvm --config="$CFG" "$TARGET" 2>/tmp/run.log &
sleep 9
xdotool key --clearmodifiers Return; sleep 1
xdotool key --clearmodifiers i; sleep 6          # Introduction 劇情
import -window root /out/intro.png 2>/dev/null || true
for i in $(seq 1 8); do xdotool key --clearmodifiers Return space; sleep 1.5; done
import -window root /out/intro2.png 2>/dev/null || true
pkill -f scummvm 2>/dev/null || true; sleep 1
echo "=== dump 行數/不重複 ==="; wc -l /out/ags_dump.txt 2>/dev/null; echo "unique:"; sort -u /out/ags_dump.txt 2>/dev/null | wc -l
echo "=== 不重複字串(前 80)==="; sort -u /out/ags_dump.txt 2>/dev/null | head -80
