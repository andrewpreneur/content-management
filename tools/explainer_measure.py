#!/usr/bin/env python3
"""Measure the highlight already drawn on each screenshot (ring + numbered badge + arrow) so the video points at
exactly the right element. No guessing, no AI: pixels only.

  python3 tools/explainer_measure.py KIT_DIR            # reads KIT_DIR/screenshots/manifest.json (or every PNG)
  python3 tools/explainer_measure.py a.png b.png ...    # any screenshots
Options: --out targets.json (default KIT_DIR/targets.json), --ring "#1b4094" --accent "#2563eb", --preview DIR

Writes targets.json: { "<file>": { "w","h", "ring":{x,y,w,h}, "target":{x,y,w,h}, "click":[x,y],
  "badge":{cx,cy,r}|null, "arrow":{"tail":[x,y],"tip":[x,y]}|null, "found":"ring"|"spotlight"|null, "note" } }
All numbers are screenshot pixels (the PNG's own size). "target" is the element itself (inside the ring),
"click" its centre: put the cursor there, zoom toward "target", and if you draw anything, hug "target" (+8 px).
--preview writes <name>.measured.png with the boxes drawn, so a person (or an agent) can see the result.
Exit code 1 if any screenshot had no highlight found (the step then needs a hand-measured box in the storyboard).
"""
import json, sys, argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def near(px, rgb, tol):
    return np.sqrt(((px - rgb) ** 2).sum(-1)) < tol


def comps(mask, min_px=30):
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        m = lab[sl] == i
        cnt = int(m.sum())
        if cnt < min_px:
            continue
        y0, x0, y1, x1 = sl[0].start, sl[1].start, sl[0].stop, sl[1].stop
        out.append(dict(x=x0, y=y0, w=x1 - x0, h=y1 - y0, n=cnt, fill=cnt / ((x1 - x0) * (y1 - y0)), mask=m, sl=sl))
    return out


def lum(px):
    return px @ np.array([0.299, 0.587, 0.114], dtype=np.float32)


def find_ring(px, ring_rgb):
    """A hollow outline in the ring colour whose inside is brighter than the dimmed page around it."""
    H, W, _ = px.shape
    L = lum(px)
    best = None
    for c in comps(near(px, ring_rgb, 48), 60):
        if c['w'] < 24 or c['h'] < 16 or c['fill'] > 0.35:
            continue
        x, y, w, h = c['x'], c['y'], c['w'], c['h']
        inner = L[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4].mean()
        pad = max(8, min(w, h) // 6)
        ring_out = np.concatenate([L[max(0, y - pad):y, x:x + w].ravel(), L[y + h:min(H, y + h + pad), x:x + w].ravel(),
                                   L[y:y + h, max(0, x - pad):x].ravel(), L[y:y + h, x + w:min(W, x + w + pad)].ravel()])
        outer = ring_out.mean() if ring_out.size else 0
        score = (inner - outer) * np.sqrt(w * h)
        if inner > outer + 8 and (best is None or score > best[0]):
            best = (score, c)
    if not best:
        return None
    c = best[1]
    # ring thickness: ring pixels in from each side along the middle row/column
    m = near(px, ring_rgb, 48)
    def run(line):
        k = 0
        while k < len(line) and line[k]:
            k += 1
        return k
    my, mx = c['y'] + c['h'] // 2, c['x'] + c['w'] // 2
    tl = run(m[my, c['x']:c['x'] + c['w']]); tr = run(m[my, c['x']:c['x'] + c['w']][::-1])
    tt = run(m[c['y']:c['y'] + c['h'], mx]); tb = run(m[c['y']:c['y'] + c['h'], mx][::-1])
    gap = 4  # the ring sits a few px outside the element
    ring = dict(x=c['x'], y=c['y'], w=c['w'], h=c['h'])
    target = dict(x=c['x'] + tl + gap, y=c['y'] + tt + gap, w=c['w'] - tl - tr - 2 * gap, h=c['h'] - tt - tb - 2 * gap)
    return ring, target


def find_spotlight(px):
    """Fallback: the page is dimmed except the highlighted element. Largest bright rectangle-ish region."""
    L = lum(px)
    bright = L > np.percentile(L, 50) + 40
    cs = [c for c in comps(bright, 400) if c['w'] > 30 and c['h'] > 20 and c['fill'] > 0.5]
    if not cs:
        return None
    c = max(cs, key=lambda c: c['n'])
    t = dict(x=c['x'], y=c['y'], w=c['w'], h=c['h'])
    return dict(t), t


def badge_and_arrow(px, accent_rgb, ring):
    acc = comps(near(px, accent_rgb, 40), 40)
    rx0, ry0, rx1, ry1 = ring['x'], ring['y'], ring['x'] + ring['w'], ring['y'] + ring['h']
    def dist_to_ring(x, y):
        dx = max(rx0 - x, 0, x - rx1); dy = max(ry0 - y, 0, y - ry1)
        return (dx * dx + dy * dy) ** 0.5
    badge = None
    for c in acc:
        r = (c['w'] + c['h']) / 4
        if 0.75 < c['w'] / max(1, c['h']) < 1.33 and c['fill'] > 0.5 and 6 < r < 80:
            cx, cy = c['x'] + c['w'] / 2, c['y'] + c['h'] / 2
            corner = min(((cx - a) ** 2 + (cy - b) ** 2) ** 0.5 for a in (rx0, rx1) for b in (ry0, ry1))
            if corner < 3 * r and (badge is None or corner < badge[0]):
                badge = (corner, dict(cx=round(cx), cy=round(cy), r=round(r)))
    arrow = None
    for c in acc:
        long_side, short_side = max(c['w'], c['h']), min(c['w'], c['h'])
        if long_side < 30 or c['fill'] > 0.5 or (badge and abs(c['x'] + c['w'] / 2 - badge[1]['cx']) < badge[1]['r'] and abs(c['y'] + c['h'] / 2 - badge[1]['cy']) < badge[1]['r']):
            continue
        ys, xs = np.nonzero(c['mask'])
        xs = xs + c['x']; ys = ys + c['y']
        d = np.array([dist_to_ring(x, y) for x, y in zip(xs[::7], ys[::7])])
        if d.min() > 0.6 * max(ring['w'], ring['h']) + 60:
            continue
        i_tip, i_tail = int(np.argmin(d)), int(np.argmax(d))
        a = dict(tip=[int(xs[::7][i_tip]), int(ys[::7][i_tip])], tail=[int(xs[::7][i_tail]), int(ys[::7][i_tail])])
        if arrow is None or d.min() < arrow[0]:
            arrow = (d.min(), a)
    return (badge[1] if badge else None), (arrow[1] if arrow else None)


def measure(path, ring_rgb, accent_rgb):
    im = Image.open(path).convert('RGB')
    px = np.asarray(im, dtype=np.float32)
    H, W, _ = px.shape
    got, how = find_ring(px, ring_rgb), 'ring'
    if not got:
        got, how = find_spotlight(px), 'spotlight'
    if not got:
        return dict(w=W, h=H, ring=None, target=None, click=None, badge=None, arrow=None, found=None,
                    note='No highlight found: measure this step by hand in the storyboard.')
    ring, target = got
    badge, arrow = badge_and_arrow(px, accent_rgb, ring) if how == 'ring' else (None, None)
    # wide fields (search boxes, bars): people click near the left, not the middle
    cx = target['x'] + (min(target['w'] // 2, 3 * target['h']) if target['w'] > 4 * target['h'] else target['w'] // 2)
    click = [cx, target['y'] + target['h'] // 2]
    return dict(w=W, h=H, ring=ring, target=target, click=click, badge=badge, arrow=arrow, found=how,
                note='Baked-in highlight measured; do not draw a second box unless it hugs "target".')


def preview(path, r, out):
    im = Image.open(path).convert('RGB'); d = ImageDraw.Draw(im)
    if r['target']:
        t = r['target']; d.rectangle([t['x'], t['y'], t['x'] + t['w'], t['y'] + t['h']], outline=(255, 0, 160), width=4)
        c = r['click']; d.ellipse([c[0] - 10, c[1] - 10, c[0] + 10, c[1] + 10], outline=(255, 0, 160), width=4)
    if r.get('badge'):
        b = r['badge']; d.ellipse([b['cx'] - b['r'], b['cy'] - b['r'], b['cx'] + b['r'], b['cy'] + b['r']], outline=(0, 200, 0), width=4)
    if r.get('arrow'):
        a = r['arrow']; d.line([*a['tail'], *a['tip']], fill=(0, 200, 0), width=4)
    im.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--out'); ap.add_argument('--preview')
    ap.add_argument('--ring', default='#1b4094'); ap.add_argument('--accent', default='#2563eb')
    a = ap.parse_args()
    base, files = None, []
    if len(a.paths) == 1 and Path(a.paths[0]).is_dir():
        base = Path(a.paths[0])
        man = base / 'screenshots' / 'manifest.json'
        files = [base / s['file'] for s in json.loads(man.read_text())['screenshots']] if man.exists() else sorted(base.rglob('*.png'))
    else:
        files = [Path(p) for p in a.paths]
    ring_rgb, accent_rgb = hexrgb(a.ring), hexrgb(a.accent)
    res, missing = {}, 0
    for f in files:
        key = str(f.relative_to(base)) if base else str(f)
        r = measure(f, ring_rgb, accent_rgb); res[key] = r
        missing += r['found'] is None
        if a.preview:
            Path(a.preview).mkdir(parents=True, exist_ok=True)
            preview(f, r, Path(a.preview) / (key.replace('/', '_').replace('.png', '') + '.measured.png'))
        print(f"{key}: {r['found'] or 'NOT FOUND'} target={r['target']} click={r['click']}")
    out = Path(a.out) if a.out else (base / 'targets.json' if base else Path('targets.json'))
    out.write_text(json.dumps(res, indent=1))
    print('wrote', out)
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
