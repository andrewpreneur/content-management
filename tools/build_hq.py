#!/usr/bin/env python3
"""Rebuild Content HQ data: post_queue.py hub -> compact captions -> embed small thumbnails.
  python3 tools/build_hq.py THUMBS_DIR   (thumbs/<name>.jpg as referenced by plan.json 'thumb')
Writes outputs/content-hq/queue.json; then publish outputs/content-hq/index.html to the Content HQ url with files {queue.json}."""
import json, sys, io, base64, subprocess, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.loads(subprocess.run([sys.executable, os.path.join(ROOT, 'tools/post_queue.py'), 'hub'], capture_output=True, text=True, check=True).stdout)
tdir = sys.argv[1] if len(sys.argv) > 1 else None; cache = {}
for h in H:
    caps = h.pop('cap'); vals = list(caps.values()); main = max(set(vals), key=vals.count) if vals else ''
    h['c'] = main; ov = {k: v for k, v in caps.items() if v != main}
    if ov: h['co'] = ov
    t = h.get('th'); h['th'] = None
    if t and tdir:
        p = os.path.join(tdir, t[len('thumbs/'):] if t.startswith('thumbs/') else t)
        if t not in cache and os.path.exists(p):
            im = Image.open(p).convert('RGB'); im.thumbnail((200, 250)); b = io.BytesIO(); im.save(b, 'JPEG', quality=72)
            cache[t] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
        h['th'] = cache.get(t)
json.dump(H, open(os.path.join(ROOT, 'outputs/content-hq/queue.json'), 'w'), separators=(',', ':'))
print(len(H), 'items,', len(cache), 'thumbs')
