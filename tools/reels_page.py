#!/usr/bin/env python3
"""Build data for the "Podcast Reels" review page: every finished V1–V7 reel, grouped by clip.

Usage: python3 tools/reels_page.py PAGE_DIR
  - makes 540p previews + poster frames in /home/user/work/reelprev (skips existing)
  - reads PAGE_DIR/assets.json ({"pod1-05-v1.mp4": "<asset url>", ...}: urls returned by the Artifact asset upload)
  - writes PAGE_DIR/reels.json and copies posters to PAGE_DIR/p/
  - prints the previews that still need uploading (not in assets.json)
Videos live in the page's asset store (the version size cap is too small for hundreds of reels); posters are published files.
Andrew's taps land in the page db, collection `reels`, doc "<clip>__<vN>": {status: approved|change|rejected, note, at}.
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF, PREV = Path('/home/user/work/formats'), Path('/home/user/work/reelprev')
FORMATS = {'v1': 'Motion graphics', 'v2': 'Story letterbox', 'v8': 'Animated', 'v4': 'Question box', 'v5': 'Split question', 'v6': 'Serious crop', 'v7': 'Plain hook'}  # V3 kinetic retired Nov 7 (Andrew), V8 takes its slot
SOURCE = {'pod1': 'Pod1 · Andy Griffith (SoloLink)', 'pod2': 'Pod2 · Blake Coker (Task Engine)', 'pod3': "Pod3 · HighLevel's 2026 interns"}


def main():
    page = Path(sys.argv[1]); (page / 'p').mkdir(parents=True, exist_ok=True); PREV.mkdir(exist_ok=True)
    assets = json.loads((page / 'assets.json').read_text()) if (page / 'assets.json').exists() else {}
    clips, todo = [], []
    for s in ('pod1', 'pod2', 'pod3'):
        for c in json.loads((ROOT / f'outputs/clip-bank/{s}.json').read_text())['clips']:
            reels = {}
            for f in FORMATS:
                src = WF / c['id'] / f"{c['id']}-{f}.mp4"
                if not (src.exists() and Path(f'{src}.sound.md').exists()): continue
                b = f"{c['id']}-{f}"; mp4, jpg = PREV / f'{b}.mp4', PREV / f'{b}.jpg'
                if not mp4.exists():
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', 'scale=540:960', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '28', '-maxrate', '1200k',
                                    '-bufsize', '2400k', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(mp4)], check=True)
                if not jpg.exists():
                    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', str(mp4), '-frames:v', '1', '-vf', 'scale=270:480', '-q:v', '5', str(jpg)], check=True)
                shutil.copy(jpg, page / 'p' / jpg.name)
                if mp4.name in assets: reels[f] = dict(video=assets[mp4.name], poster=f'p/{jpg.name}')
                else: todo.append(str(mp4))
            clips.append(dict(id=c['id'], title=c['title'].replace('\n', ' '), speaker=c.get('speaker', ''), source=SOURCE[s], hook=c.get('hook_q', ''), reels=reels))
    (page / 'reels.json').write_text(json.dumps(dict(formats=FORMATS, clips=clips), ensure_ascii=False))
    print(json.dumps(todo))
    print(sum(len(c['reels']) for c in clips), 'reels on page,', len(todo), 'to upload', file=sys.stderr)


if __name__ == '__main__':
    main()
