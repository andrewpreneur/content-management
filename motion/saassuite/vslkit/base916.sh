#!/bin/bash
# 9:16 base from the 4K source, crop centred on the head x measured on the 16:9 base.
# base916.sh src.mp4 face169.json out.mp4
src=$1; face=$2; out=$3
cx=$(tail -1 "$face" | python3 -c "import json,sys;d=json.load(sys.stdin);h=d['head'];print(round((h[0]+h[2])/2*3840/d['W']))")
x=$(python3 -c "print(max(0,min(3840-1216,$cx-608))//2*2)")
echo "crop x=$x (head cx 4K=$cx)"
ffmpeg -v error -y -i "$src" -vf "crop=1216:2160:$x:0,scale=1080:1920:flags=lanczos" -c:v libx264 -preset veryfast -crf 14 -an "$out"
