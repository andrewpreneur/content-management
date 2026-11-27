#!/usr/bin/env python3
"""Merge out-A/B/C.json captions into outputs/planner/plan.json (Nov 27 caption rewrite).
Podcast clips: week w uses caption ((w-1) % 3); the transcript moves to `transcript`. Carousels / text cards: new caption,
old line kept in `headline`. Checks every caption against the app's rules first."""
import json, re, glob, sys
from pathlib import Path
D = Path(__file__).parent; R = D.parents[1]
SLOP = ["delve", "game-changer", "unlock", "elevate", "leverage", "seamless", "revolutioniz", "in today's fast", "tapestry", "unleash"]
clips, items = {}, {}
for f in sorted(glob.glob(str(D / 'out-*.json'))):
    o = json.load(open(f)); clips.update(o.get('clips', {})); items.update(o.get('items', {}))
bad = []
def check(k, c):
    if '—' in c: bad.append((k, 'em dash'))
    if any(w in c.lower() for w in SLOP): bad.append((k, 'slop word'))
    if len(c.split('\n')[0]) > 125: bad.append((k, 'first line'))
    if len(c) > 2200: bad.append((k, 'too long'))
for k, v in clips.items():
    if len(v) != 3: bad.append((k, f'{len(v)} variants'))
    for c in v: check(k, c)
for k, c in items.items(): check(k, c)
if bad: print('PROBLEMS', bad[:30]); sys.exit(1)
P = R / 'outputs/planner/plan.json'; plan = json.load(open(P)); n = {'clip': 0, 'item': 0}; missing = set()
for it in plan['items']:
    if it.get('kind') == 'podcast_clip':
        v = clips.get(it.get('clip'))
        if not v: missing.add(it.get('clip')); continue
        if not it.get('transcript'): it['transcript'] = it.get('body')
        it['body'] = v[((it.get('week') or 1) - 1) % 3]; n['clip'] += 1
    elif it.get('kind') in ('carousel', 'text_card'):
        c = items.get(it['id'])
        if not c: missing.add(it['id']); continue
        if 'headline' not in it: it['headline'] = it.get('body')
        it['body'] = c; n['item'] += 1
json.dump(plan, open(P, 'w'), indent=1, ensure_ascii=False)
# Keep them for the planner (tools/planner.py reads posting/captions.json, so a re-plan never brings transcripts back).
CF = R / 'posting/captions.json'; old = json.load(open(CF)) if CF.exists() else {'clips': {}, 'items': {}}
old['clips'].update(clips); old['items'].update(items); json.dump(old, open(CF, 'w'), indent=1, ensure_ascii=False)
print('updated', n, 'missing', sorted(missing))
