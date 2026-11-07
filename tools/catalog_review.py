#!/usr/bin/env python3
"""Nov 7 catalog review page: one HTML page + small preview strips (one per carousel, one per source's single images,
one per story sequence) in /home/user/work/catalog/review/. Publish with the Artifact tool (files = previews/*).

  python3 tools/catalog_review.py
"""
import csv, html, json, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'outputs/2026-11-07-catalog'; R = Path('/home/user/work/catalog/review'); P = R / 'previews'


def strip(files, out, h=360, gap=8):
    ims = [Image.open(f).convert('RGB') for f in files]; ims = [im.resize((int(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); c = Image.new('RGB', (W, h), (255, 255, 255)); x = 0
    for im in ims: c.paste(im, (x, 0)); x += im.width + gap
    c.save(out, quality=72, optimize=True); return out.name


def main():
    P.mkdir(parents=True, exist_ok=True); [f.unlink() for f in P.glob('*.jpg')]
    rows = list(csv.DictReader(open(OUT / 'manifest.csv')))
    src_of = {}; groups = {}
    for r in rows:
        key = re.sub(r'-(convo|thread|story|substack|linkedin|x|threads-\d|quote-.*|tweet-.*|stat-.*|post-.*)$', '', r['id'])
        groups.setdefault(key, dict(source=r['source'], hook=None, car=[], singles=[], story=None)); g = groups[key]
        if r['type'] == 'carousel':
            g['car'].append(dict(id=r['id'], fmt=r['format'], hook=r['hook'], n=r['length'], img=strip(sorted((OUT / r['file']).glob('*.jpg')), P / f"{r['id']}.jpg"), path=r['file']))
            g['hook'] = g['hook'] or r['hook']
        elif r['type'] == 'single image': g['singles'].append(r)
        elif r['type'] == 'story sequence':
            g['story'] = dict(img=strip(sorted((OUT / r['file']).glob('*.jpg')), P / f"{key}-story.jpg", h=480), path=r['file']); g['hook'] = g['hook'] or r['hook']
    for key, g in groups.items():
        if g['singles']:
            port = [OUT / s['file'] for s in g['singles'] if '1080x1350' in s['file']]; land = [OUT / s['file'] for s in g['singles'] if '1200x627' in s['file']]
            a = Image.open(P / strip(port, P / f'{key}-a.jpg', h=360)); b = Image.open(P / strip(land, P / f'{key}-b.jpg', h=200)) if land else None
            c = Image.new('RGB', (max(a.width, b.width if b else 0), a.height + (b.height + 10 if b else 0)), (255, 255, 255)); c.paste(a, (0, 0))
            if b: c.paste(b, (0, a.height + 10))
            c.save(P / f'{key}-singles.jpg', quality=72, optimize=True); (P / f'{key}-a.jpg').unlink(); (P / f'{key}-b.jpg').unlink(missing_ok=True)
            g['single_img'] = f'{key}-singles.jpg'; g['land_img'] = None
            g['n_singles'] = len(g['singles'])
        g.pop('singles')
    text = {}
    for k in ('linkedin', 'threads', 'x', 'substack-notes', 'carousel-captions'):
        md = (OUT / 'text' / f'{k}.md').read_text(); items = []
        for blk in md.split('\n### ')[1:]:
            head, _, body = blk.partition('\n'); src = ''
            m = re.match(r'_(?:Source|Video): (.*?)_\n\n', body)
            if m: src = m.group(1); body = body[m.end():]
            items.append(dict(id=head.strip(), src=src, text=body.strip()))
        text[k] = items
    order = [k for k in groups if k.startswith('pod')] + [k for k in groups if not k.startswith('pod') and groups[k]['car']] + [k for k in groups if groups[k].get('story')]
    data = dict(groups=[dict(key=k, **groups[k]) for k in order], text=text,
                counts=dict(carousels=sum(len(g['car']) for g in groups.values()), singles=sum(g.get('n_singles', 0) for g in groups.values()),
                            stories=sum(1 for g in groups.values() if g.get('story')), text=sum(len(v) for k, v in text.items() if k != 'carousel-captions')))
    tpl = (ROOT / 'tools/catalog_review_template.html').read_text()
    (R / 'index.html').write_text(tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
    print(data['counts'], len(list(P.glob('*.jpg'))), 'preview files', sum(f.stat().st_size for f in P.glob('*.jpg')) // 1024 // 1024, 'MB')


if __name__ == '__main__':
    main()
