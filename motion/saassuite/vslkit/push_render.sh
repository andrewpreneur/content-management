#!/bin/bash
# push_render.sh "commit msg" file1.mp4 file2.mp4 ...  -> commit to render-drop/vsl-final (orphan, videos only), push with rebase retries
set -e; MSG=$1; shift; R=/home/user/work/rd; B=render-drop/vsl-final; cd /home/user/content-management
if [ ! -d $R ]; then
  if git fetch -q origin $B 2>/dev/null; then git worktree add -q -B $B $R FETCH_HEAD; else git worktree add -q --detach $R && git -C $R checkout -q --orphan $B && (git -C $R rm -rqf --cached . >/dev/null; git -C $R clean -fdxq); fi
fi
cd $R; cp "$@" .; git add $(for f in "$@"; do basename $f; done)
git commit -qm "$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RoHYRS2fproj3GJPNgnVr2"
for i in 1 2 3 4 5; do
  if git push -q -u origin $B 2>/dev/null; then echo pushed; break; fi
  git fetch -q origin $B && git rebase -q FETCH_HEAD || true; sleep $((2**i))
done
for f in "$@"; do rm -f "$R/$(basename $f)"; done   # keep disk small; files stay in git history
