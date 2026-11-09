#!/bin/bash
# qa.sh FILE.mp4 -> FILE.sheet.jpg (frame every 2 s with timestamps) + loudness/peak line
f=$1; d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
w=$(ffprobe -v error -select_streams v -show_entries stream=width -of csv=p=0 $f)
if [ "$w" = 1920 ]; then sc=384:216; cols=6; else sc=216:384; cols=10; fi
ffmpeg -v error -y -i $f -vf "fps=0.5,scale=$sc,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x6" -frames:v 1 ${f%.mp4}.sheet.jpg
ffmpeg -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tr -s ' ' | tr '\n' ' '; echo " dur=$d"
