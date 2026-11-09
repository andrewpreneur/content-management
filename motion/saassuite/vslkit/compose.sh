#!/bin/bash
# compose.sh WORKDIR VARIANT(169|916) NAME   -> WORKDIR/NAME-VARIANT.mp4
# Needs WORKDIR/{b<V>.mp4, voice.wav, music.mp3, ov<V>/*.png, cues.json, duration.txt}
set -e; D=$1; V=$2; N=$3; K=$(dirname "$0")
dur=$(cat $D/duration.txt)
python3 $K/mix.py $D $dur
ffmpeg -v error -y -i $D/b$V.mp4 -framerate 30 -i $D/ov$V/%05d.png -i $D/mix.wav \
  -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=6,trim=duration=$dur,setpts=PTS-STARTPTS[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -t $dur -c:v libx264 -preset medium -crf 20 -r 30 -c:a aac -b:a 192k -movflags +faststart $D/$N-$V.mp4
echo "$D/$N-$V.mp4"
