#!/usr/bin/env bash
# usage: ./build.sh episodes/<slug>.json out.mp4   (run inside this folder; needs node+playwright, ffmpeg, python3, edge-tts, certifi)
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
rm -rf "$W"
