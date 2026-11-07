#!/bin/bash
# 540p review previews for every render in DIRs -> /home/user/content-management/.vslprev (scratch, gitignored by name)
P=/home/user/content-management/.vslprev; mkdir -p $P
for d in "$@"; do for f in $d/*.mp4; do b=$(basename $f .mp4); o=$P/$b.mp4
  [ -f $o ] && [ $o -nt $f ] && continue
  ffmpeg -v error -y -i $f -vf "scale='if(gt(iw,ih),-2,540)':'if(gt(iw,ih),540,-2)'" -c:v libx264 -preset veryfast -crf 28 -c:a aac -b:a 96k -movflags +faststart $o && echo $b; done; done
