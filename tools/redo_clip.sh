#!/bin/bash
# Mark clips for a full re-render (e.g. wrong speaker on screen): removes local reels, previews and carousels, and stops
# tools/collect_drops.sh from pulling the old versions back. Usage: [FROM=w1] bash tools/redo_clip.sh pod1-04 pod2-01 ...
# FROM: only that worker's render-drop branch may deliver the new versions.
for cid in "$@"; do W=/home/user/work/formats/$cid; [ -d "$W" ] || continue
  rm -f "$W"/$cid-v?.mp4 "$W"/$cid-v?.mp4.sound.md "$W"/$cid-v?.mp4.credits.txt "$W"/$cid-v?_silent.mp4 /home/user/work/reelprev/$cid-v?.*
  rm -rf "/home/user/work/carousels/${cid:?}"; date +%s > "$W/.redo_after"; [ -n "$FROM" ] && echo "$FROM" > "$W/.redo_from"; echo "redo $cid"; done
