set -e
export HOME=/tmp XDG_RUNTIME_DIR=/tmp DISPLAY=:99
apt-get update -qq && apt-get install -y -qq xvfb imagemagick x11-utils xdotool >/dev/null 2>&1
Xvfb :99 -screen 0 1024x768x24 >/tmp/xvfb.log 2>&1 &
sleep 2
cd /src
# (A) 純 launcher GUI 當對照
timeout 12 ./scummvm 2>/tmp/sv1.log &
sleep 6
echo "=== windows on :99 ==="; xwininfo -root -tree 2>/dev/null | grep -iE "scummvm|0x[0-9a-f]+ \"" | head
import -window root /out/diag_launcher.png 2>/dev/null || true
pkill -f scummvm; sleep 2
# (B) 遊戲 + 多按幾下鍵跳過 splash
timeout 30 ./scummvm --path=/game --auto-detect 2>/tmp/sv2.log &
sleep 9
for i in 1 2 3 4 5; do xdotool key --clearmodifiers Return space Escape 2>/dev/null; sleep 1.2; done
xdotool mousemove 320 240 click 1 2>/dev/null || true
sleep 2
import -window root /out/diag_game_a.png 2>/dev/null || true
sleep 4; import -window root /out/diag_game_b.png 2>/dev/null || true
pkill -f scummvm 2>/dev/null || true
echo "=== sv2 tail ==="; grep -viE "ALSA|seq_hw" /tmp/sv2.log | tail -12
