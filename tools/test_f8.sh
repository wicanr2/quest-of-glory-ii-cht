export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
command -v xdotool >/dev/null || { echo "FATAL: xdotool 仍缺"; exit 1; }
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out
python3 -c "import configparser;c=configparser.ConfigParser();c.optionxform=str;c.read('/out/sv.ini');d=c.setdefault('qfg2agdi',{});d['translation']='chinese';[d.pop(k,None) for k in ('ags_dump_static','ags_dump_strings','ags_cjk_size')];c.write(open('/out/sv.ini','w'))"
timeout 45 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/r.log &
sleep 7;  import -window root /out/f8_0_cht16.png 2>/dev/null
xdotool key --clearmodifiers F8; sleep 2; import -window root /out/f8_1_cht24.png 2>/dev/null
xdotool key --clearmodifiers F8; sleep 2; import -window root /out/f8_2_en.png 2>/dev/null
xdotool key --clearmodifiers F8; sleep 2; import -window root /out/f8_3_cht16.png 2>/dev/null
pkill -f scummvm; sleep 1
echo "=== language mode 切換 log ==="; grep -i "language mode" /tmp/r.log
