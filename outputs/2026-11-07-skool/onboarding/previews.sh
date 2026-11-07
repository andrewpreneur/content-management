#!/bin/bash
# 720p review copies + poster frames for the review page (build/previews/, not committed)
cd "$(dirname "$0")"; mkdir -p build/previews
for f in renders/*.mp4; do
  b=$(basename "$f" .mp4)
  [ -f build/previews/$b.mp4 ] || ffmpeg -v error -y -i "$f" -vf scale=1280:-2,fps=30 -c:v libx264 -crf 25 -preset medium -c:a aac -b:a 128k -movflags +faststart build/previews/$b.mp4
  [ -f build/previews/$b.jpg ] || ffmpeg -v error -y -ss 1.4 -i "$f" -frames:v 1 -vf scale=960:-2 -q:v 4 build/previews/$b.jpg
done
ls -la build/previews
