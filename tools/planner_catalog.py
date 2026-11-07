#!/usr/bin/env python3
"""Add the Nov 7 catalog (outputs/2026-11-07-catalog) to the Content Planner, Nov 9–22.

  python3 tools/planner_catalog.py PLAN.json [THUMBS_DIR]     # edits PLAN.json in place (idempotent: replaces cat__* items)

Daily mix (docs/brand.md + main session, Nov 7): LinkedIn 1–2, Threads 3–5, X 2–3, IG carousel 1, single image 1–2, stories.
Existing items stay; catalog items fill each day up to the mix, on their own time slots (never on a reel/clip slot).
"""
import csv, datetime as dt, json, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent; CAT = ROOT / 'outputs/2026-11-07-catalog'; COPY = Path('/home/user/work/catalog/copy')
REVIEW = 'https://claude.ai/artifact/X7tw3bKS9t6osCF2QX2PAE'
START, DAYS = dt.date(2026, 11, 9), 14
SLOT = {'linkedin_post': ['08:15', '13:15'], 'threads_post': ['09:45', '13:30', '20:30', '22:00', '07:30'], 'x_thread': ['11:00', '18:15', '22:15'],
        'carousel': ['18:45'], 'single_image': ['10:15', '15:45'], 'story_sequence': ['12:00']}
TARGET = {'linkedin_post': 2, 'threads_post': 4, 'x_thread': 2, 'carousel': 1, 'single_image': 2, 'story_sequence': 1}  # catalog adds up to these totals
MAX_ADD = {'carousel': 1, 'story_sequence': 1, 'single_image': 2, 'linkedin_post': 1, 'threads_post': 3, 'x_thread': 2}
CAROUSELS = ['levelup', 'pod1-03', 'commerce', 'pod2-04', 'meetingroom', 'pod1-14', 'studioupdate', 'pod2-07', 'n8n', 'pod3-15', 'funnelstore', 'pod1-10', 'convoaischedule', 'pod2-09']
LABEL = {'pod1': 'Pod1 · Andy (SoloLink)', 'pod2': 'Pod2 · Blake (Task Engine)', 'pod3': 'Pod3 · Interns'}


def src_label(k):
    return LABEL.get(k[:4], 'Catalog · ' + k)


def rr(groups):
    """round-robin across sources so each day mixes podcasts, features and YouTube."""
    out = []; groups = [list(g) for g in groups if g]
    while any(groups):
        for g in groups:
            if g: out.append(g.pop(0))
    return out


def main():
    plan_p = Path(sys.argv[1]); thumbs = Path(sys.argv[2]) if len(sys.argv) > 2 else plan_p.parent / 'thumbs'; thumbs.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_p.read_text()); items = [i for i in plan['items'] if not i['id'].startswith('cat__')]
    copy = {}
    for f in ('pod1', 'pod2', 'pod3', 'feature1', 'feature2', 'feature3', 'roundups'):
        for it in json.loads((COPY / f'{f}.json').read_text()): copy[it['id']] = it
    yt = json.loads((COPY / 'youtube.json').read_text()); ytsrc = {v['id']: v for v in json.loads((CAT / 'sources/youtube.json').read_text())}
    caps = {}
    for blk in (CAT / 'text/carousel-captions.md').read_text().split('\n### ')[1:]:
        h, _, b = blk.partition('\n'); caps[h.strip()] = b.strip()

    def thumb(img, key):
        dst = thumbs / f'cat__{key}.jpg'
        if not dst.exists():
            im = Image.open(img).convert('RGB'); im.thumbnail((360, 640)); im.save(dst, quality=78)
        return f'thumbs/{dst.name}'

    pods = [k for k in copy if k.startswith('pod') and 'roundup' not in k]; feats = [k for k in copy if not k.startswith('pod')]
    # pools (best first)
    pool = {}
    pool['carousel'] = [dict(key=k, title=f"Podcast stack: {copy[k]['hook']}", files=f"outputs/2026-11-07-catalog/carousels/{k}-convo/",
                             body=caps.get(f'{k}-convo', '') + f"\n\nFiles: outputs/2026-11-07-catalog/carousels/{k}-convo/ (slides 1–{len(list((CAT / 'carousels' / f'{k}-convo').glob('*.jpg')))})",
                             img=CAT / f'carousels/{k}-convo/slide-01.jpg', src=k) for k in CAROUSELS]
    sing = []
    for k in [x for x in rr([pods, feats]) if (CAT / 'singles' / f'{x}-quote-1080x1350.jpg').exists()]:
        for kind in ('stat', 'quote', 'tweet'):
            f = CAT / 'singles' / f'{k}-{kind}-1080x1350.jpg'
            if f.exists():
                txt = (copy[k]['stat'][0] + ' ' + copy[k]['stat'][1]) if kind == 'stat' else copy[k]['quote'] if kind == 'quote' else copy[k]['tweet']
                sing.append(dict(key=f'{k}-{kind}', title=f"Image ({kind}): {txt[:70]}", src=k, img=f,
                                 files=f"outputs/2026-11-07-catalog/singles/{k}-{kind}-1080x1350.jpg (+ 1200x627 for LinkedIn)",
                                 body=f"{copy[k]['tweet'] if kind != 'tweet' else copy[k]['thread'][0]}\n\nFiles: outputs/2026-11-07-catalog/singles/{k}-{kind}-1080x1350.jpg (IG/Threads) · {k}-{kind}-1200x627.jpg (LinkedIn)"))
                break  # one card per source in the first pass
    # second pass: the other card kinds
    for k in [x for x in rr([pods, feats])]:
        for kind in ('quote', 'tweet'):
            if any(s['key'] == f'{k}-{kind}' for s in sing): continue
            f = CAT / 'singles' / f'{k}-{kind}-1080x1350.jpg'
            if f.exists():
                txt = copy[k]['quote'] if kind == 'quote' else copy[k]['tweet']
                sing.append(dict(key=f'{k}-{kind}', title=f"Image ({kind}): {txt[:70]}", src=k, img=f, files=f"outputs/2026-11-07-catalog/singles/{k}-{kind}-1080x1350.jpg",
                                 body=f"{copy[k]['thread'][0]}\n\nFiles: outputs/2026-11-07-catalog/singles/{k}-{kind}-1080x1350.jpg (IG/Threads) · {k}-{kind}-1200x627.jpg (LinkedIn)"))
                break
    pool['single_image'] = sing
    pool['story_sequence'] = [dict(key=f"{v['id']}-story", title=f"Story → YouTube: {v['hook']}", src='YouTube', img=CAT / f"stories/{v['id']}/{v['id']}-story-1.jpg",
                                   files=f"outputs/2026-11-07-catalog/stories/{v['id']}/ (4 frames)",
                                   body=f"1 {v['hook']}\n2 {v['why']}\n3 Poll: {v['poll'][0]} ({' / '.join(v['poll'][1:])})\n4 Link sticker → {ytsrc[v['id']]['url']} (label: Watch: {v['short']})\n\nFiles: outputs/2026-11-07-catalog/stories/{v['id']}/ · spec: stories/story-specs.json")
                              for v in yt]
    order = rr([[k for k in pods], [k for k in feats if k in copy and not k.endswith('roundup')], ['pod1-roundup', 'pod2-roundup', 'pod3-roundup']])
    pool['linkedin_post'] = [dict(key=f'{k}-li', title='LinkedIn: ' + copy[k]['linkedin'].split('\n')[0][:80], src=k, body=copy[k]['linkedin']) for k in order]
    th = []
    for j in range(3):
        for k in order:
            t = copy[k]['threads']
            if j < len(t): th.append(dict(key=f'{k}-th{j + 1}', title='Threads: ' + t[j].split('\n')[0][:80], src=k, body=t[j]))
    yt_th = [dict(key=f"{v['id']}-th", title='Threads → YouTube: ' + v['threads'][:70], src='YouTube', body=v['threads'] + '\n\n' + ytsrc[v['id']]['url']) for v in yt]
    pool['threads_post'] = rr([th, yt_th])
    pool['x_thread'] = rr([[dict(key=f'{k}-x', title='X: ' + copy[k]['x'].split('\n')[0][:80], src=k, body=copy[k]['x']) for k in order],
                           [dict(key=f"{v['id']}-x", title='X → YouTube: ' + v['x'].split('\n')[0][:70], src='YouTube', body=v['x'] + '\n\n' + ytsrc[v['id']]['url']) for v in yt]])
    TY = {'carousel': 'carousel', 'single_image': 'carousel', 'story_sequence': 'story', 'linkedin_post': 'text', 'threads_post': 'text', 'x_thread': 'text'}
    PL = {'carousel': ['instagram', 'facebook', 'linkedin'], 'single_image': ['instagram', 'threads', 'linkedin'], 'story_sequence': ['instagram', 'facebook'],
          'linkedin_post': ['linkedin'], 'threads_post': ['threads'], 'x_thread': ['x']}
    TAG = {'carousel': 'podcast stack', 'single_image': 'single image', 'story_sequence': 'story', 'linkedin_post': 'linkedin', 'threads_post': 'threads', 'x_thread': 'x'}
    added = []; ptr = {k: 0 for k in pool}
    for n in range(DAYS):
        day = START + dt.timedelta(days=n); ds = day.isoformat()
        have = {}; taken = set(i['time'] for i in items if i['date'] == ds)
        for i in items:
            if i['date'] == ds: have[i['kind']] = have.get(i['kind'], 0) + 1
        have['carousel'] = 0  # existing carousels are other formats; the catalog adds one podcast stack a day
        for kind, tgt in TARGET.items():
            need = min(MAX_ADD[kind], max(0, tgt - have.get(kind, 0)))
            for s in range(need):
                if ptr[kind] >= len(pool[kind]): break
                p = pool[kind][ptr[kind]]; ptr[kind] += 1
                tm = next(t for t in SLOT[kind] + [f'{h:02d}:05' for h in range(7, 23)] if t not in taken); taken.add(tm)
                it = dict(id=f"cat__{p['key']}", date=ds, time=tm, type=TY[kind], kind=kind, title=p['title'], platforms=PL[kind], status='needs_approval', prod='ready',
                          source=src_label(p['src']) if p['src'] != 'YouTube' else 'YouTube', review=REVIEW, body=p['body'], tags=['catalog', TAG[kind]],
                          due=(day - dt.timedelta(days=1)).isoformat())
                if p.get('files'): it['files'] = p['files']
                if p.get('img'): it['thumb'] = thumb(p['img'], p['key'])
                added.append(it)
    items += added; items.sort(key=lambda x: (x['date'], x['time'])); plan['items'] = items
    plan['generated'] = dt.datetime.now().isoformat(timespec='minutes')
    plan_p.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    from collections import Counter
    print(len(added), 'catalog items added', dict(Counter(i['kind'] for i in added)))
    for n in range(DAYS):
        ds = (START + dt.timedelta(days=n)).isoformat(); print(ds, dict(Counter(i['kind'] for i in items if i['date'] == ds)))


if __name__ == '__main__':
    main()
