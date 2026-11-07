#!/bin/bash
# Push finished vsl renders to branch render-drop/$STREAM (orphan, one commit per batch). Usage: STREAM=vsl-a bash tools/vsl/drop.sh DIR_WITH_MP4S...
set -e; B="render-drop/${STREAM:?}"; D=/home/user/work/drop-$STREAM
if [ ! -d "$D/.git" ]; then mkdir -p "$D"; git -C "$D" init -q; git -C "$D" remote add origin "$(git -C /home/user/content-management remote get-url origin)"; fi
cd "$D"
if git fetch -q origin "$B" 2>/dev/null; then git checkout -q -B drop FETCH_HEAD; else git checkout -q --orphan drop 2>/dev/null || true; fi
n=0
for dir in "$@"; do sub=$(basename "$dir"); mkdir -p "$sub"
  for f in "$dir"/*.mp4; do [ -f "$f" ] || continue; b=$(basename "$f")
    if [ ! -f "$sub/$b" ] || ! cmp -s "$f" "$sub/$b"; then cp "$f" "$sub/$b"; n=$((n+1)); fi; done; done
git add -A; if git diff --cached --quiet; then echo "nothing new"; exit 0; fi
git -c user.name="Claude vsl-a worker" -c user.email=noreply@anthropic.com commit -qm "vsl-a renders: $n files"
for i in 1 2 3 4; do git push -q origin "HEAD:refs/heads/$B" && break; sleep $((2**i)); done
echo "dropped $n files to $B"
