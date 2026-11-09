#!/bin/bash
# composite.sh <base.mp4> <overlay.mov> <mix.wav> <dur> <out.mp4>
# Base video held on its last frame to <dur> (end card covers it), overlay on top, mixed audio. H.264 CRF 20, AAC 192k, faststart.
set -e
B=$1; O=$2; A=$3; D=$4; OUT=$5
BD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$B")
PAD=$(python3 -c "print(max(0.1, $D - $BD + 0.2))")
ffmpeg -v error -y -i "$B" -i "$O" -i "$A" -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=$PAD,fps=30[b];[b][1:v]overlay=format=auto:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 2:a -t "$D" -c:v libx264 -crf 20 -preset medium -profile:v high -c:a aac -b:a 192k -movflags +faststart "$OUT"
