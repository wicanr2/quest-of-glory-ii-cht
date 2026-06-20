export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq xvfb imagemagick xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2
cd /out; mkdir -p /out/demo
setcfg(){ python3 -c "import configparser,sys;c=configparser.ConfigParser();c.optionxform=str;c.read('/out/sv.ini');d=c.setdefault('qfg2agdi',{});
[d.pop(k,None) for k in ('ags_dump_static','ags_dump_strings','ags_cjk_size','translation')]
import json
kv=json.loads(sys.argv[1])
d.update(kv); c.write(open('/out/sv.ini','w'))" "$1"; }

cap(){ # $1=cfgjson $2=outpng
  setcfg "$1"
  timeout 16 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/dev/null &
  sleep 6; import -window root "$2" 2>/dev/null
  pkill -f scummvm; sleep 1
}
cap '{"translation":"chinese"}'                       /out/demo/m_cht16.png
cap '{"translation":"chinese","ags_cjk_size":"24"}'   /out/demo/m_cht24.png
cap '{}'                                              /out/demo/m_en.png

# 進遊戲嘗試(繁中16):過 disclaimer → 選單 → Start New Hero
setcfg '{"translation":"chinese"}'
timeout 40 /src/scummvm --config=/out/sv.ini qfg2agdi 2>/dev/null &
sleep 6; xdotool key --clearmodifiers Return; sleep 2     # 過 disclaimer 到選單
import -window root /out/demo/g_menu.png
xdotool key --clearmodifiers s; sleep 4                   # Start New Hero
import -window root /out/demo/g_newhero1.png
xdotool key --clearmodifiers Return space; sleep 3
import -window root /out/demo/g_newhero2.png
xdotool click 1; sleep 3; import -window root /out/demo/g_newhero3.png
pkill -f scummvm
echo "=== 產物 ==="; ls -la /out/demo/*.png | awk '{print $5,$NF}'
