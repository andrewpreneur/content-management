#!/usr/bin/env python3
"""Nov 7 catalog: feature-release videos (Andrew solo, camera + screen) → convo-style stack carousel, thread carousel, single images.

  python3 tools/catalog_features.py COPY.json TX_DIR FRAMES_DIR OUT_ROOT [--only key,key]

The stack keeps what Andrew liked in pod1-05: every slide has a real human (Andrew's face, big) and one short line in a black
band; the screen moment sits on the other half, zoomed in so it can be read on a phone (never a tiny screenshot).
Frames are 1920-wide stills every 12 s; full-camera frames (Andrew talking to camera) are found by face detection.
"""
import argparse, json, sys
from pathlib import Path
import cv2
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / 'tools'))
import catalog_cards as CC
from catalog_pods import locate

CASC = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def faces_of(frames):
    out = []
    for f in frames:
        g = cv2.imread(str(f), 0)
        if (g > 200).mean() > 0.12: continue
        fs = CASC.detectMultiScale(g, 1.1, 6, minSize=(140, 140))
        if len(fs):
            x, y, w, h = max(fs, key=lambda r: r[2]); sharp = cv2.Laplacian(g[y:y + h, x:x + w], cv2.CV_64F).var()
            out.append((f, dict(x=x + w / 2, y=y + h / 2, face=w), sharp))
    out.sort(key=lambda r: -r[2])  # sharpest face first (cover + cards); blurred mid-gesture frames go last
    return [(f, p) for f, p, _ in out]


def crop(img, cx, cy, cw, W, H):
    im = Image.open(img).convert('RGB'); IW, IH = im.size; ch = cw * H / W
    if ch > IH: ch = IH; cw = ch * W / H
    cx = min(max(cx, cw / 2), IW - cw / 2); cy = min(max(cy, ch / 2), IH - ch / 2)
    return im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)


def face_crop(fr, p, W, H, mult, out, top=0.36):
    cw = min(mult * p['face'], Image.open(fr).width); ch = cw * H / W
    crop(fr, p['x'], p['y'] + (0.5 - top) * ch, cw, W, H).save(out, quality=92); return str(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('copy'); ap.add_argument('tx'); ap.add_argument('frames'); ap.add_argument('out'); ap.add_argument('--only', default='')
    a = ap.parse_args(); only = set(filter(None, a.only.split(',')))
    for it in json.loads(Path(a.copy).read_text()):
        k = it['id']
        if only and k not in only: continue
        T = json.loads((Path(a.tx) / f'{k}.json').read_text()); words = []
        for s in T['segments']:
            ws = s['text'].split(); d = (s['e'] - s['s']) / max(1, len(ws))
            words += [[w, s['s'] + i * d, s['s'] + (i + 1) * d] for i, w in enumerate(ws)]
        frames = sorted(Path(a.frames, k).glob('f_*.jpg')); fc = faces_of(frames)
        if not fc: print(k, 'NO FACE FRAMES'); continue
        screens = [f for f in frames if f not in [x[0] for x in fc]]
        tmp = Path('/home/user/work/catalog/frames_feat') / k; tmp.mkdir(parents=True, exist_ok=True); out = Path(a.out) / k
        step = 12.0; at = lambda t: frames[min(len(frames) - 1, max(0, int(round(t / step))))]
        used = set()
        def screen_at(t):
            f = at(t); pool = [x for x in screens if x not in used] or screens
            if not pool: return f
            g = min(pool, key=lambda s: abs(frames.index(s) - frames.index(f))); used.add(g); return g
        def scr_crop(f, i, W=1080, H=600, zoom=it.get('zoom', 0.70)):
            IW = Image.open(f).width; o = tmp / f'scr{i}.jpg'; crop(f, IW / 2 + it.get('dx', 0), Image.open(f).height / 2 + it.get('dy', 0), IW * zoom, W, H).save(o, quality=92); return str(o)
        f0, p0 = fc[0]
        top0 = face_crop(f0, p0, 1080, 600, 4.4, tmp / 'top0.jpg')
        after = screens[int(len(screens) * 0.8)] if screens else f0
        sl = [dict(format='split', top=top0, bot=scr_crop(after, 'hero'), text=it['hook'], top_label='Andrew George', bot_label=it['title'])]
        for i, line in enumerate(it['lines']):
            s0, s1, r = locate(words, line); sf = screen_at((s0 + s1) / 2)
            ff, pp = fc[i % len(fc)]
            sl.append(dict(format='split', top=scr_crop(sf, i), bot=face_crop(ff, pp, 1080, 600, 4.0 + 0.5 * (i % 3), tmp / f'face{i}.jpg'), text=line, size=48 if len(line) > 48 else 52,
                           bot_label='Andrew George'))
        CC.render(sl, out / 'convo', 1080, 1350)
        face_crop(f0, p0, 1080, 1350, 3.4, tmp / 'portrait.jpg'); face_crop(f0, p0, 430, 627, 3.2, tmp / 'portrait_l.jpg'); face_crop(f0, p0, 240, 240, 2.4, tmp / 'face.jpg', 0.45)
        th = it['thread']; n = len(th) + 1
        ts = [dict(format='facehook', photo=str(tmp / 'portrait.jpg'), text=it['hook'], tag='NEW IN HIGHLEVEL', sub=it['title'])]
        ts += [dict(format='tweet', text=t, num=f'{j + 2}/{n}') for j, t in enumerate(th[:-1])]
        ts.append(dict(format='cta', text=th[-1]))
        CC.render(ts, out / 'thread', 1080, 1350)
        by2 = it['title'] + ' · new in HighLevel'
        cards = [('quote', dict(format='quote', text=it['quote'], label='New in HighLevel', by='Andrew George', by2=by2, avatar=str(tmp / 'face.jpg'), photo=str(tmp / 'portrait_l.jpg'))),
                 ('tweet', dict(format='tweet', text=it['tweet']))]
        if it.get('stat'): cards.append(('stat', dict(format='stat', num=it['stat'][0], label=it['stat'][1], by='Andrew George', by2=it['title'], avatar=str(tmp / 'face.jpg'))))
        nm = [f'{k}-{c}-1080x1350' for c, _ in cards]
        CC.render([s for _, s in cards], out / 'single', 1080, 1350, names=nm)
        CC.render([s for _, s in cards], out / 'single', 1200, 627, names=[x.replace('1080x1350', '1200x627') for x in nm])
        print(k, 'faces', len(fc), 'screens', len(screens), flush=True)


if __name__ == '__main__':
    main()
