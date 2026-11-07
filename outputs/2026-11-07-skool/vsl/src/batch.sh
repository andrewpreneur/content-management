#!/bin/bash
# Render + mix + check every VSL. Usage: bash src/batch.sh <scratch_dir> [filter]
set -e
S=$1; F=${2:-.}; export NODE_PATH=/opt/node22/lib/node_modules
mkdir -p $S/final $S/preview
declare -A PRO=([vsl1]=alex [vsl1cut]=alex [vsl2]=joe [vsl3]=brian [vsl3cut]=brian)
for v in vsl1 vsl2 vsl3 vsl1cut vsl3cut; do for who in andrew pro; do for fmt in h v; do
  name="skool-${v}_$([ $who = pro ] && echo ${PRO[$v]} || echo andrew)_$([ $fmt = h ] && echo 16x9 || echo 9x16)"
  echo "$name" | grep -q -- "$F" || continue
  page=src/${v%cut}.html
  node src/render.mjs $page timing/$v-$who.json $fmt $S/render/${name}_silent.mp4 30 2 4 > /dev/null
  python3 src/mix.py timing/$v-$who.json $S/vo/$v-$who.wav $S/music/${v%cut}.mp3 $S/render/${name}_silent.mp4 $S/final/$name.mp4
  python3 src/check_sync.py $S/final/$name.mp4 timing/$v-$who.json 2>/dev/null | tail -1
  if [ $fmt = h ]; then sc=1280:720; else sc=720:1280; fi
  ffmpeg -v error -y -i $S/final/$name.mp4 -vf scale=$sc -c:v libx264 -crf 26 -preset veryfast -c:a aac -b:a 128k -movflags +faststart $S/preview/$name.mp4
  rm -f $S/render/${name}_silent.mp4
done; done; done
echo BATCH DONE
