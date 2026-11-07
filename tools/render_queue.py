#!/usr/bin/env python3
"""Make content in calendar order: whatever posts soonest gets made first (Andrew, Nov 5: "focus on the next 24-48 hours").

Reads outputs/planner/plan.json, takes every item that is not made yet, sorts by due date then post time, and makes them one by one.
  python3 tools/render_queue.py video LANE NLANES   # V1–V7 renders; a clip always lands in the same lane, so lanes never collide
  python3 tools/render_queue.py carousel            # carousels + text cards (tools/carousel_formats.py clip, all formats per clip)
Re-reads the plan after every job and skips anything already made, so it can be stopped and restarted at any time.
Env: RQ_CLIPS=a,b (only these clips), RQ_SKIP=a,b (never these), RQ_DROP=1 (cloud worker: push each finished reel to branch render-drop/$WORKER).
Run detached: setsid nohup python3 tools/render_queue.py video 0 2 >> /home/user/work/rq_v0.log 2>&1 & disown
"""
import json, os, subprocess, sys, time, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF, CAR = Path('/home/user/work/formats'), Path('/home/user/work/carousels')
BANK = {p: ROOT / f'outputs/clip-bank/{p}.json' for p in ('pod1', 'pod2', 'pod3')}


def jobs(kind, lane, n):
    items = json.loads((ROOT / 'outputs/planner/plan.json').read_text())['items']
    out, seen = [], set()
    for it in sorted(items, key=lambda x: (x.get('due', x['date']), x['time'])):
        cid = it.get('clip')
        if not cid: continue
        only, skip = os.environ.get('RQ_CLIPS'), os.environ.get('RQ_SKIP', '')
        if (only and cid not in only.split(',')) or cid in skip.split(','): continue
        if kind == 'video' and it['kind'] == 'podcast_clip':
            if (only.split(',').index(cid) if only else zlib.crc32(cid.encode())) % n != lane: continue
            key = (cid, it['format'])
            if key in seen or (WF / cid / f"{cid}-{it['format']}.mp4.sound.md").exists(): continue
        elif kind == 'carousel' and it['kind'] in ('carousel', 'text_card') and it['id'].startswith(('car__pod', 'card__')) and not it['id'].endswith(('__lessons', '__hybrid')):
            key = (cid,)
            if key in seen or (CAR / cid / 'tweet/slide-01.png').exists(): continue
        else:
            continue
        seen.add(key); out.append((it.get('due'), key))
    return out


def main():
    kind = sys.argv[1]; lane, n = (int(sys.argv[2]), int(sys.argv[3])) if kind == 'video' else (0, 1)
    failed = set()
    while True:
        todo = [j for j in jobs(kind, lane, n) if j[1] not in failed]
        if not todo: print('ALL DONE', flush=True); return
        due, key = todo[0]; cid = key[0]; spec = str(BANK[cid.split('-')[0]])
        print(f"== {cid} {key[1] if len(key) > 1 else 'carousels'} due {due} {time.strftime('%H:%M')}", flush=True)
        if kind == 'video':
            r = subprocess.run([sys.executable, str(ROOT / 'tools/formats.py'), spec, cid, '--formats', key[1]], cwd=ROOT, capture_output=True, text=True)
            ok = (WF / cid / f'{cid}-{key[1]}.mp4.sound.md').exists()
            if ok and all((WF / cid / f'{cid}-{k}.mp4.sound.md').exists() for k in ('v1', 'v2', 'v4', 'v5', 'v6', 'v7', 'v8')):
                subprocess.run(['rm', '-rf', f'/home/user/work/frames/{cid}'])  # all 7 done: free the frame cache (≈0.5 GB per clip)
            if ok and os.environ.get('RQ_DROP'):  # cloud worker: send the finished reel back to the main session
                subprocess.run(['bash', str(ROOT / 'tools/worker_drop.sh'), cid, key[1]], cwd=ROOT)
        else:
            r = subprocess.run([sys.executable, str(ROOT / 'tools/carousel_formats.py'), 'clip', spec, cid, str(CAR / cid)], cwd=ROOT, capture_output=True, text=True)
            ok = (CAR / cid / 'tweet/slide-01.png').exists()
        if not ok:
            failed.add(key); print('FAILED', key, (r.stdout + r.stderr)[-600:], flush=True)


if __name__ == '__main__':
    main()
