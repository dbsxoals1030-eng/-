#!/usr/bin/env bash
# usage: ./build_bumper.sh outdir   -> outdir/itip-bumper-v.mp4 (1080x1920) and -h.mp4 (1920x1080), 5s each
set -e; O=${1:-.}; W=./_work_bumper; rm -rf $W; mkdir -p $W $O
export NODE_PATH=$(npm root -g)
python3 -I tts.py ko-KR-SunHiNeural +18% +0Hz "잇팁인데요" $W/voice.mp3
python3 -I bumper_audio.py $W/b.wav $W/voice.mp3
for o in v h; do node render_bumper.js $W/f$o $o & done; wait
for o in v h; do ffmpeg -y -v error -framerate 30 -i $W/f$o/%04d.jpg -i $W/b.wav -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 44100 -movflags +faststart -shortest $O/itip-bumper-$o.mp4; done
rm -rf $W
