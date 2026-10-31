#!/usr/bin/env bash
# usage: ./build.sh episodes/<slug>.json out.mp4   (output = 5s bumper + 40s episode = 45s)   (run inside this folder; needs node+playwright, ffmpeg, python3, edge-tts, certifi)
set -e
EP=${1:?episode json}; OUT=${2:-out.mp4}; W=./_work_$(basename "$EP" .json)
rm -rf "$W"; mkdir -p "$W/frames" "$W/vo"
echo "window.EPISODE=$(cat "$EP");" > episode.js
export NODE_PATH=$(npm root -g)
for i in 0 1 2 3; do s=$((i*300)); node render.js "$W/frames" 30 $s $((s+300)) & done; wait
python3 -I audio.py "$W/music.wav" "$EP"
python3 -I vo_build.py "$W/music.wav" "$W/vo" "$W/mix.wav" "$EP"
ffmpeg -y -v error -framerate 30 -i "$W/frames/%04d.jpg" -i "$W/mix.wav" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 44100 -movflags +faststart -shortest "$OUT"
# thumbnail = settled intro frame at 3.5s (title + characters all visible)
ffmpeg -y -v error -i "$W/frames/0105.jpg" -frames:v 1 "${OUT%.mp4}_thumb.jpg" 2>/dev/null || true
# prepend the 5s channel bumper (set NO_BUMPER=1 to skip)
BUMP=channel/itip-bumper-v.mp4
if [ -f "$BUMP" ] && [ -z "$NO_BUMPER" ]; then
  mv "$OUT" "$W/main.mp4"
  ffmpeg -y -v error -i "$BUMP" -i "$W/main.mp4" -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
    -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 -movflags +faststart "$OUT"
fi
rm -rf "$W"
