#!/usr/bin/env python3
"""Nov 7 catalog: podcast clips → convo carousel (pod1-05 style), thread carousel, single images.

  python3 tools/catalog_pods.py COPY.json BANK.json SRC.mp4 OUT_ROOT [--seats SEATS.json] [--only id,id]

COPY.json: hand-written copy per clip (hook, lines, thread, quote, stat, tweet, who, linkedin, threads, x).
Seats: {"host": {"x","y","face"}, "guest": {...}, "<name>": {...}} positions in the 4K wide shot (static camera).
Each convo line is placed on whoever says it: single-speaker clips use the bank label; mixed clips (→ / +) use
mouth/hand motion in each seat over the line's time span.
"""
import argparse, json, re, subprocess, sys
from difflib import SequenceMatcher
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT / 'tools'))
import carousel_formats as CF, catalog_cards as CC

RK = Path('/home/user/work/catalog/rk/bank')


def norm(w):
    return re.sub(r"[^a-z0-9]", '', w.lower())


def locate(words, line):
    """best (start, end) seconds of `line` inside the clip's word list."""
    toks = [norm(w) for w in line.split() if norm(w)]; W = [norm(w[0]) for w in words]; n = len(toks); best = (0, 0, 0)
    for i in range(0, max(1, len(W) - n + 1)):
        for L in (n - 2, n, n + 3):
            seg = W[i:i + max(1, L)]; r = SequenceMatcher(None, toks, seg).ratio()
            if r > best[0]: best = (r, i, i + max(1, L) - 1)
    r, a, b = best; b = min(b, len(words) - 1)
    return words[a][1], words[b][2], r


def grab(src, t, out):
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', src, '-frames:v', '1', '-q:v', '2', out], check=True); return out


def motion(src, t0, t1, seats):
    """mean abs frame diff in each seat's face+hands box over [t0,t1] → seat name with most motion."""
    ts = np.linspace(t0, max(t0 + 0.4, t1), 6); fr = []
    for k, t in enumerate(ts):
        p = f'/tmp/claude-0/mo_{k}.jpg'; subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', src, '-frames:v', '1', '-vf', 'scale=960:-2', p], check=True)
        fr.append(np.asarray(Image.open(p).convert('L'), dtype=np.float32))
    sc = {}
    for name, p in seats.items():
        s = 0.25; x, y, f = p['x'] * s, p['y'] * s, p['face'] * s
        x0, x1, y0, y1 = int(x - f * .45), int(x + f * .45), int(y), int(y + f * .7)  # lower face (mouth/jaw)
        sc[name] = float(np.mean([np.abs(fr[i + 1][y0:y1, x0:x1] - fr[i][y0:y1, x0:x1]).mean() for i in range(len(fr) - 1)]))
    return max(sc, key=sc.get), sc


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('copy'); ap.add_argument('bank'); ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--seats', required=True); ap.add_argument('--only', default=''); a = ap.parse_args()
    COPY = json.loads(Path(a.copy).read_text()); B = json.loads(Path(a.bank).read_text()); seats = json.loads(Path(a.seats).read_text())
    clips = {c['id']: c for c in B['clips']}; pod = Path(a.bank).stem; only = set(filter(None, a.only.split(',')))
    g, org, gt = B.get('guest_name', ''), B.get('guest_org', ''), B.get('guest_title', '')
    report = []
    for it in COPY:
        cid = it['id']
        if only and cid not in only: continue
        c = clips[cid]; words = json.loads((RK / pod / f'{cid}.words.json').read_text()); out = Path(a.out) / cid; fr = Path('/home/user/work/catalog/frames_pod') / cid; fr.mkdir(parents=True, exist_ok=True)
        sp = c.get('speaker', ''); mixed = '→' in sp or '+' in sp
        who = it.get('who') or ('Andrew George' if sp.startswith('Andrew') and not mixed else g)
        main_seat = 'host' if who == 'Andrew George' else (it.get('seat') or ('guest' if 'guest' in seats else who))
        other = 'guest' if main_seat == 'host' and 'guest' in seats else 'host'
        if main_seat == 'host' and 'guest' not in seats: other = it.get('other_seat', [k for k in seats if k != 'host'][0])
        T = lambda t: c['t0'] + t
        # convo carousel
        hook_t = locate(words, it['lines'][0]); r0 = grab(a.src, T((hook_t[0] + hook_t[1]) / 2), str(fr / 'r0.jpg'))
        sl = [dict(format='split', top=CF.single(r0, seats['host'], 1080, 600, str(fr / 'top.jpg'), 4.6),
                   bot=CF.single(r0, seats[main_seat if main_seat != 'host' else other], 1080, 600, str(fr / 'bot.jpg'), 4.6), text=it['hook'],
                   top_label='Andrew George', bot_label=(who if main_seat != 'host' else (g if other == 'guest' else other)) + (f' · {org}' if org and main_seat != 'host' and who == g else ''))]
        placed = []
        for k, line in enumerate(it['lines']):
            s0, s1, r = locate(words, line); seat = main_seat
            if 'line_seats' in it: seat = {'h': 'host', 'g': main_seat if main_seat != 'host' else other}.get(it['line_seats'][k], it['line_seats'][k])
            im = grab(a.src, T((s0 + s1) / 2), str(fr / f'l{k}.jpg'))
            sl.append(dict(format='single', img=CF.single(im, seats[seat], 1080, 1350, str(fr / f'one{k}.jpg'), 3.8), text=line, color='#FFE14D' if k % 2 == 0 else '#FFFFFF'))
            placed.append((round(s0, 1), seat, round(r, 2)))
        CC.render(sl, out / 'convo', 1080, 1350)
        # faces for cards
        spk = seats[main_seat]; face = CF.crop_person(r0, spk, 240, 240, 2.6, 0.45); face.save(fr / 'face.jpg', quality=92)
        CF.crop_person(r0, spk, 1080, 1350, 3.2, 0.36).save(fr / 'portrait.jpg', quality=92)
        CF.crop_person(r0, spk, 430, 627, 3.0, 0.36).save(fr / 'portrait_l.jpg', quality=92)
        where = (f'{org} · on my podcast' if org and who == g else 'on my podcast') if who != 'Andrew George' else f'on my podcast with {g}'
        if who != 'Andrew George' and who != g: where = 'HighLevel 2026 intern · on my podcast'
        label = (f'A lesson from a {gt}' if gt and who == g else 'From my podcast') if who != 'Andrew George' else 'From my podcast'
        if who != 'Andrew George' and who != g: label = "A lesson from HighLevel's 2026 interns"
        # thread carousel: real face cover → Andrew's take, one idea per slide → CTA
        th = it['thread']; n = len(th) + 1
        ts = [dict(format='facehook', photo=str(fr / 'portrait.jpg'), text=it['hook'], tag='FROM MY PODCAST', sub=f'{who}' + (f', {org}' if org and who == g else ''), size=None)]
        ts += [dict(format='tweet', text=t, num=f'{k + 2}/{n}') for k, t in enumerate(th[:-1])]
        ts.append(dict(format='cta', text=th[-1]))
        CC.render(ts, out / 'thread', 1080, 1350)
        # single images
        sg = []; nm = []
        q = dict(format='quote', text=it['quote'], label=label, by=who, by2=where, avatar=str(fr / 'face.jpg'), photo=str(fr / 'portrait_l.jpg'))
        tw = dict(format='tweet', text=it['tweet'])
        cards = [('quote', q), ('tweet', tw)]
        if it.get('stat'):
            cards.append(('stat', dict(format='stat', num=it['stat'][0], label=it['stat'][1], by=who, by2=where, avatar=str(fr / 'face.jpg'))))
        for k, s in cards: sg.append(s); nm.append(f'{cid}-{k}-1080x1350')
        CC.render(sg, out / 'single', 1080, 1350, names=nm)
        CC.render(sg, out / 'single', 1200, 627, names=[x.replace('1080x1350', '1200x627') for x in nm])
        report.append(dict(id=cid, who=who, main=main_seat, placed=placed))
        print(cid, who, placed, flush=True)
    Path(a.out, f'_{pod}_report.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
