#!/usr/bin/env python3
"""Nov 7 catalog: gather rendered images + hand-written copy into outputs/2026-11-07-catalog/ (files, text per platform, CSV manifest).

  python3 tools/catalog_assemble.py
"""
import csv, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent; W = Path('/home/user/work/catalog'); OUT = ROOT / 'outputs/2026-11-07-catalog'
YT = {v['id']: v for v in json.loads((OUT / 'sources/youtube.json').read_text())}
PODS = {}
for p in ('pod1', 'pod2', 'pod3'):
    for c in json.loads((ROOT / f'outputs/clip-bank/{p}.json').read_text())['clips']: PODS[c['id']] = c
SRC_LABEL = {'pod1': 'Pod1 (Andy Griffith, SoloLink), Oct 2026', 'pod2': 'Pod2 (Blake Coker, Task Engine), Oct 2026', 'pod3': "Pod3 (HighLevel 2026 interns), Oct 2026"}
FEAT_SRC = {'n8n': 'N8N V+S.mp4 (Nov 2026 V+S)', 'commerce': 'Commerce V+S.mp4 (Nov 2026 V+S)', 'switchyard': 'SwitchYard V+S.mp4 (Nov 2026 V+S)', 'funnelstore': 'FunnelStore V+S.mp4 (Nov 2026 V+S)',
            'convoaischedule': 'ConvoAISchedule V+S.mp4 (Oct 2026 V+S)', 'dykcustomaudiences': 'DYKCustomAudiences V+S.mp4 (Oct 2026 V+S)', 'meetingroom': 'MEETINGROOM.mp4 (Oct 2026 V+S)',
            'ssbranding': 'SSBranding.mp4 (Oct 2026 V+S)', 'ssinstallation': 'SSInstallation.mp4 (Oct 2026 V+S)', 'ssclienthu': 'SSClientHu.mp4 (Oct 2026 V+S)', 'ssmenulink': 'SSMenuLink.mp4 (Oct 2026 V+S)',
            'webinar': 'WebinarVideo.mp4 (Oct 2026 V+S)', 'studioupdate': 'StudioUpdate.mp4 (Oct 2026 V+S)', 'khalifwebinar': 'KhalifWebinar.mp4 (Nov 2026 V+S)', 'levelup': 'levelup V+S.mp4 (Nov 2026 V+S)'}
TAGS = {'pod': '#gohighlevel #saas #agencyowner', 'feat': '#gohighlevel #highlevel #saas', 'yt': '#gohighlevel #youtube #saas'}


def load(name):
    p = W / 'copy' / f'{name}.json'; return json.loads(p.read_text()) if p.exists() else []


def lint(t):
    bad = [w for w in ('—', 'delve', 'leverage', 'game-changer', 'unlock', 'elevate', 'seamless', 'robust', 'in today', 'revolutioniz') if w in t.lower() or w in t]
    return bad


def main():
    for d in ('carousels', 'singles', 'stories', 'text'):
        if (OUT / d).exists(): shutil.rmtree(OUT / d)
        (OUT / d).mkdir(parents=True)
    rows = []; text = {k: [] for k in ('linkedin', 'threads', 'x', 'substack-notes', 'carousel-captions')}; problems = []

    def add_car(kind, src_dir, cid, hook, source, caption):
        files = sorted(src_dir.glob('*.jpg'))
        if not files: return
        dst = OUT / 'carousels' / f'{cid}-{kind}'; dst.mkdir(parents=True); [shutil.copy(f, dst / f.name) for f in files]
        rows.append(dict(id=f'{cid}-{kind}', type='carousel', format={'convo': 'Hormozi podcast stack (pod1-05 style)', 'thread': 'face cover + tweet thread'}[kind], platforms='instagram;facebook;linkedin',
                         source=source, hook=hook, length=f'{len(files)} slides', file=str(dst.relative_to(OUT)) + '/'))
        text['carousel-captions'].append(f"### {cid}-{kind}\n{caption}\n")

    def add_singles(src_dir, cid, hook, source):
        for f in sorted(src_dir.glob('*.jpg')):
            shutil.copy(f, OUT / 'singles' / f.name); size = '1200x627' if '1200x627' in f.name else '1080x1350'
            kind = f.name.replace(cid + '-', '').split('-')[0]
            rows.append(dict(id=f.stem, type='single image', format=kind + ' card', platforms='linkedin' if size == '1200x627' else 'instagram;linkedin;threads;substack', source=source, hook=hook, length=size, file='singles/' + f.name))

    def add_text(cid, it, source):
        for k in ('linkedin', 'x'):
            if it.get(k): text[k].append(f"### {cid}\n_Source: {source}_\n\n{it[k]}\n"); rows.append(dict(id=f'{cid}-{k}', type='text', format=k, platforms={'x': 'x', 'linkedin': 'linkedin'}[k], source=source, hook=it[k].split('\n')[0][:90], length=f"{len(it[k])} chars", file=f'text/{k}.md'))
        th = it.get('threads') or []
        if isinstance(th, str): th = [th]
        for j, t in enumerate(th):
            text['threads'].append(f"### {cid}-{j + 1}\n_Source: {source}_\n\n{t}\n"); rows.append(dict(id=f'{cid}-threads-{j + 1}', type='text', format='threads', platforms='threads', source=source, hook=t.split('\n')[0][:90], length=f'{len(t)} chars', file='text/threads.md'))
        for k in ('linkedin', 'x'):
            if lint(it.get(k, '')): problems.append((cid, k, lint(it[k])))
        for t in th:
            if lint(t): problems.append((cid, 'threads', lint(t)))

    # podcasts
    for pod in ('pod1', 'pod2', 'pod3'):
        for it in load(pod):
            cid = it['id']; c = PODS[cid]; src = f"{SRC_LABEL[pod]} · clip {cid} ({c['t0']:.0f}s, {c['dur']:.0f}s)"; d = W / 'out/pod' / cid
            cap = f"{it['thread'][0]}\n\n{it['thread'][-1]}\n\n{TAGS['pod']}"
            add_car('convo', d / 'convo', cid, it['hook'], src, cap); add_car('thread', d / 'thread', cid, it['hook'], src, cap)
            add_singles(d / 'single', cid, it['hook'], src); add_text(cid, it, src)
    # feature releases
    for name in ('feature1', 'feature2', 'feature3', 'feature4'):
        for it in load(name):
            cid = it['id']; src = FEAT_SRC.get(cid, cid); d = W / 'out/feat' / cid
            if not d.exists(): continue
            cap = f"{it['thread'][0]}\n\n{it['thread'][-1]}\n\n{TAGS['feat']}"
            add_car('convo', d / 'convo', cid, it['hook'], src, cap); add_car('thread', d / 'thread', cid, it['hook'], src, cap)
            add_singles(d / 'single', cid, it['hook'], src); add_text(cid, it, src)
    # youtube
    specs = json.loads((W / 'out/yt/_story_specs.json').read_text()); (OUT / 'stories/story-specs.json').write_text(json.dumps(specs, indent=1, ensure_ascii=False))
    for it in load('youtube'):
        vid = it['id']; v = YT[vid]; src = f"YouTube: {v['title']} ({v['url']})"; d = W / 'out/yt' / vid
        sd = OUT / 'stories' / vid; sd.mkdir(parents=True); [shutil.copy(f, sd / f.name) for f in sorted((d / 'story').glob('*.jpg'))]
        rows.append(dict(id=f'{vid}-story', type='story sequence', format='4 frames: hook, why, poll, link sticker', platforms='instagram;facebook', source=src, hook=it['hook'], length='4 frames', file=f'stories/{vid}/'))
        add_singles(d / 'single', vid, it['img'], src)
        text['substack-notes'].append(f"### {vid}\n_Video: {v['title']} · {v['url']}_\n\n{it['note']}\n\n{v['url']}\n")
        rows.append(dict(id=f'{vid}-substack', type='text', format='substack note', platforms='substack', source=src, hook=it['note'][:90], length=f"{len(it['note'])} chars", file='text/substack-notes.md'))
        add_text(vid, dict(linkedin=it['linkedin'] + f"\n\n{v['url']}", threads=[it['threads'] + f"\n\n{v['url']}"], x=it['x'] + f"\n\n{v['url']}"), src)
        if lint(it['note']): problems.append((vid, 'substack', lint(it['note'])))
    heads = {'linkedin': 'LinkedIn posts', 'threads': 'Threads posts', 'x': 'X posts', 'substack-notes': 'Substack notes (one per YouTube video, link included)', 'carousel-captions': 'Carousel captions (IG / FB / LinkedIn)'}
    for k, items in text.items():
        (OUT / 'text' / f'{k}.md').write_text(f"# {heads[k]} · Nov 7 catalog · {len(items)} drafts\nDrafts for Andrew's review. Nothing is posted.\n\n" + '\n'.join(items))
    with open(OUT / 'manifest.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'type', 'format', 'platforms', 'source', 'hook', 'length', 'file']); w.writeheader(); w.writerows(rows)
    cnt = {}
    for r in rows: cnt[r['type']] = cnt.get(r['type'], 0) + 1
    big = [p for p in OUT.rglob('*.jpg') if p.stat().st_size > 400_000]
    print(json.dumps(cnt), 'text files:', {k: len(v) for k, v in text.items()}, 'over400KB:', len(big), 'lint:', problems)
    (W / 'counts.json').write_text(json.dumps(dict(rows=cnt, text={k: len(v) for k, v in text.items()}, problems=problems)))


if __name__ == '__main__':
    main()
