set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq && apt-get install -y -qq xvfb imagemagick >/dev/null 2>&1
Xvfb :99 -screen 0 640x480x24 >/tmp/xvfb.log 2>&1 &
sleep 2
cd /src
timeout 28 ./scummvm --path=/game --auto-detect 2>/tmp/sv.log &
SVPID=$!
sleep 9;  import -window root /out/shot_09s.png 2>/dev/null || true
sleep 6;  import -window root /out/shot_15s.png 2>/dev/null || true
sleep 6;  import -window root /out/shot_21s.png 2>/dev/null || true
kill $SVPID 2>/dev/null || true
echo "=== scummvm stderr tail ==="; tail -18 /tmp/sv.log
