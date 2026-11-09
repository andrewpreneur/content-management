#!/bin/bash
# prep.sh WORKDIR : b169.mp4, face169.json, b916.mp4, face916.json from WORKDIR/src.mp4
D=$1; K=$(dirname "$(readlink -f "$0")"); T=$K/../../../tools; cd $D
ffmpeg -v error -y -i src.mp4 -vf scale=1920:1080:flags=lanczos -c:v libx264 -preset veryfast -crf 14 -an b169.mp4
python3 $T/face_zone.py b169.mp4 10 2>/dev/null | tail -1 > face169.json
$K/base916.sh src.mp4 face169.json b916.mp4
python3 $T/face_zone.py b916.mp4 10 2>/dev/null | tail -1 > face916.json
echo done > prep.done
