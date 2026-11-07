#!/bin/bash
# Render + mix + check the 10 Skool teasers (9:16). Usage: bash src/batch_teasers.sh <scratch_dir>
set -e
S=$1; export NODE_PATH=/opt/node22/lib/node_modules
mkdir -p $S/teasers $S/preview-teasers
for f in timing/t??-*.json; do
  set=$(basename $f .json); id=${set%%-*}; who=${set#*-}
  look=$(python3 -c "import json;print(json.load(open('$f'))['look'])")
  name="skool-teaser-${id}_${who}_9x16"
  node src/render.mjs src/$look.html $f v $S/render/${name}_silent.mp4 30 2 4 > /dev/null
  python3 src/mix.py $f $S/vo/$set.wav $S/music/$look.mp3 $S/render/${name}_silent.mp4 $S/teasers/$name.mp4
  python3 src/check_sync.py $S/teasers/$name.mp4 $f 2>/dev/null | tail -1
  ffmpeg -v error -y -i $S/teasers/$name.mp4 -vf scale=720:1280 -c:v libx264 -crf 26 -preset veryfast -c:a aac -b:a 128k -movflags +faststart $S/preview-teasers/$name.mp4
  rm -f $S/render/${name}_silent.mp4
done
echo TEASERS DONE
