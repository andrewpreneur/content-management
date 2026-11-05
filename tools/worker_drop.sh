#!/bin/bash
# Cloud render worker: push one finished reel to branch render-drop/$WORKER (temporary; the main session collects it with
# tools/collect_drops.sh and deletes the branch). Usage: WORKER=w1 bash tools/worker_drop.sh CLIP_ID FORMAT
set -e; cid=$1; f=$2; W=/home/user/work/formats/$cid; D=/home/user/work/drop; B="render-drop/$WORKER"
exec 9>/home/user/work/drop.lock; flock 9   # the worker's two lanes share one drop repo
if [ ! -d "$D/.git" ]; then mkdir -p "$D"; git -C "$D" init -q; git -C "$D" remote add origin "$(git -C /home/user/content-management remote get-url origin)"; fi
cd "$D"; git fetch -q origin "$B" 2>/dev/null && git reset -q FETCH_HEAD || true
mkdir -p "$cid"
# delivery encode: H.264 CRF 21 capped at 3.5 Mb/s (keeps pushes small), audio untouched
ffmpeg -v error -y -i "$W/$cid-$f.mp4" -c:v libx264 -preset slow -crf 21 -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -c:a copy -movflags +faststart "$cid/$cid-$f.mp4"
cp "$W/$cid-$f.mp4.sound.md" "$cid/"; cp "$W/$cid-$f.mp4.credits.txt" "$cid/" 2>/dev/null || true
git add "$cid"; git -c user.name="Claude render worker $WORKER" -c user.email=noreply@anthropic.com commit -qm "render $cid $f ($WORKER)"
for i in 1 2 3 4; do git push -q origin "HEAD:refs/heads/$B" && break; sleep $((2**i)); done
echo "dropped $cid $f"
