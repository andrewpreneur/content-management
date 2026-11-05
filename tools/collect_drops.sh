#!/bin/bash
# Main session: pull finished reels from every render-drop/* branch into /home/user/work/formats/<clip>/ (skips ones already there).
cd /home/user/content-management; git fetch -q origin '+refs/heads/render-drop/*:refs/remotes/origin/render-drop/*' || exit 1
n=0
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/render-drop/); do
  for f in $(git ls-tree -r --name-only "$b" | grep '\.mp4$'); do
    cid=$(dirname "$f"); out=/home/user/work/formats/$f
    [ -f "$out.sound.md" ] && continue
    ra=/home/user/work/formats/$cid/.redo_after   # clip marked for re-render: only accept files pushed after the mark
    rf=/home/user/work/formats/$cid/.redo_from      # optional: only this worker's branch may deliver the redo
    if [ -f "$rf" ] && [ "$b" != "origin/render-drop/$(cat "$rf")" ]; then continue; fi
    if [ -f "$ra" ]; then ct=$(git log -1 --format=%ct "$b" -- "$f"); [ "${ct:-0}" -gt "$(cat "$ra")" ] || continue; fi
    mkdir -p "/home/user/work/formats/$cid"; git show "$b:$f" > "$out"; git show "$b:$f.sound.md" > "$out.sound.md"
    git show "$b:$f.credits.txt" > "$out.credits.txt" 2>/dev/null || rm -f "$out.credits.txt"; n=$((n+1)); echo "got $f"
  done
done
echo "collected $n"
