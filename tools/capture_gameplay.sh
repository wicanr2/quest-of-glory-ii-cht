export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out; rm -rf gp; mkdir -p gp
python3 -c "import configparser;c=configparser.ConfigParser();c.optionxform=str;c.read('/out/sv.ini');d=c.setdefault('qfg2agdi',{});d['translation']='chinese';[d.pop(k,None) for k in ('ags_dump_static','ags_dump_strings','ags_cjk_size')];c.write(open('/out/sv.ini','w'))"
timeout 90 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/tmp/r.log &
sleep 8
WID=$(xdotool search --onlyvisible --name . 2>/dev/null | tail -1)
xdotool windowactivate --sync "$WID"; xdotool windowfocus "$WID"
xdotool mousemove --sync 512 384; sleep 1; xdotool mousedown 1; sleep 0.3; xdotool mouseup 1; sleep 3
xdotool mousemove --sync 505 465; sleep 1; xdotool mousedown 1; sleep 0.3; xdotool mouseup 1
# 密集擷取沙漠運鏡(每 0.5s)
for i in $(seq 1 36); do import -window root /out/gp/d$(printf %02d $i).png 2>/dev/null; sleep 0.5; done
pkill -f scummvm; sleep 1; echo done
