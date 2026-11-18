#!/usr/bin/env python3
"""Push the style system into Your Content System (Supabase), so it lives in the app, not in Drive or artifacts.

  python3 tools/export_styles.py --clips DIR_WITH_STYLE_CLIPS --samples DIR_WITH_v1..v8.mp4 [--picks DIR_OF_PICK_JSON]

What goes in:
  - styleRefs   : docs/brand-video/library/*.json (64 reference breakdowns)
  - styleClips  : the 5-second moments for the Style lab (cut with tools/style_clips.py OUT 4), uploaded to the app's Storage bucket `library`
  - editingStyles: V1–V8 short-form styles (+ S1–S6 reference styles) with a sample render each (uploaded)
  - motionLib   : docs/brand-video/prompt-motion/library.json (Claude-made motion graphics, credited, streamed from source)
  - docs        : the brand playbook (brand, voice, brand kit, editing styles, hooks, carousels, AI rules, quiz, filming list, research)
  - seed        : Style Picker picks (from the old artifact DB export) + the brand's starting styles
Uploads are cached in posting/style_uploads_supabase.json (file sha1 -> storage path) so re-runs don't upload again.
Needs the engine key (see tools/ycs_sync.py). Brand: $YCS_BRAND (default andrewpreneurship).
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'tools'))
from ycs_sync import call, BRAND  # noqa: E402

CACHE = R / 'posting/style_uploads_supabase.json'

EDITING = [  # key, name, status, family, ref, defines, music, useFor
  ('v1', 'Motion graphics + captions', 'active', 'short-form', "Andrew's approved S1/hook work", 'Camera springs between speakers, grade cards, one-word captions.', 'Upbeat, full from frame 1', 'Podcast clips, talking head'),
  ('v2', 'Story letterbox', 'active', 'short-form', 'greglav', '16:9 band on black, fixed 2-line title, one small white word on the left third, wide/tight/listener cutaways, muted warm grade, one orange light-leak.', 'Low dark drone, loud (~4 dB under speech)', 'Story moments, podcast'),
  ('v3', 'Kinetic (retired)', 'retired', 'short-form', 'gp_multimedia', 'Huge multi-colour words every beat, words behind the person, whip zooms, white flashes. Retired Nov 7: shouted every beat. Replaced by V8.', 'High-energy house', '—'),
  ('v4', 'Question box hook', 'active', 'short-form', 'DOAC', 'Full-screen speaker, white rounded box with a black caps question on the chest for ~4 s, then 2–3-word white captions, second speaker in yellow, listener cutaways.', 'Soft piano, low', 'Interview questions'),
  ('v5', 'Split question start', 'active', 'short-form', "Andrew's brief", 'Speaker 1 top / speaker 2 bottom with the question box on the seam, springs to full screen when the answer lands.', 'Soft piano / ambient', 'Two-person podcast'),
  ('v6', 'Serious crop', 'active', 'short-form', 'DOAC', 'Near-square frame on black, dark desaturated grade, lowercase light words one by one on a loose 2-line grid.', 'Sub-heavy dark drone', 'Serious / emotional moments'),
  ('v7', 'Plain text hook', 'active', 'short-form', 'DOAC', 'Full screen, white caps question with shadow (no box), 2-word captions, tighter framing.', 'Slow cinematic piano', 'Simple strong hooks'),
  ('v8', 'Animated', 'active', 'short-form', 'saraev + gp_multimedia + DOAC', 'Phrase-build captions (2–4 words, blur pop, key words yellow italic serif, negatives coral); hook header with a brand-blue box; a big beat every ~3.5 s (huge gradient word, 1.13× punch-in, whoosh); count-up numbers, glass icon chips, guest name note + arrow.', 'Music −11 dB ducked 8 dB, SFX on big moments', 'Default energetic reel'),
  ('s1', 'Split explainer', 'reference', 'explainer', 'saraev', 'Light canvas, visual top 52%, face card bottom with big rounded corners, one-word captions on the seam, accent words italic serif.', '', 'Screen walkthroughs with face cam, tool lists'),
  ('s2', 'Editorial', 'reference', 'explainer', 'adrien', 'Warm beige paper, floating UI cards, lowercase word in a small burnt-orange box, serif chapter cards, 1.5 s pace.', '', 'Design-y explainers, workflow'),
  ('s3', 'Motion header', 'reference', 'explainer', 'leadgenman', 'Dark canvas, headline + animated UI panel top 40% changing every ~2 s, single-take face below.', '', 'Talking-head explainers'),
  ('s5', 'POV text', 'reference', 'loop', 'artem', 'Screenshot on top, 3 short white-on-black lines, B-roll below, 6–10 s loop.', '', 'Building in public, trial reels, stories'),
  ('s6', 'Raw vs edited', 'reference', 'meta', 'viashaan', 'Two phone cards side by side: RAW vs EDITED BY AI, warm textured background.', '', 'The Engine series'),
]

DOCS = [  # path, title, group, slug
  ('docs/brand.md', 'Brand: positioning, pillars, storytelling', 'Brand', 'brand'),
  ('docs/brand-kit.md', 'Brand kit', 'Brand', 'brand-kit'),
  ('research/brand/2026-11-04-brand-playbook.md', 'Brand playbook (research)', 'Brand', 'brand-playbook'),
  ('docs/brand-video/SAASSUITE-STYLE.md', 'SaaSSuite main video style', 'Style', 'saassuite-style'),
  ('docs/brand-video/quiz.md', 'Style quiz answers', 'Style', 'style-quiz'),
  ('docs/editing-styles.md', 'Editing styles (V1–V8, S1–S6)', 'Style', 'editing-styles'),
  ('docs/hook-system.md', 'Hook system', 'Writing', 'hook-system'),
  ('docs/carousel-formats.md', 'Carousel formats', 'Writing', 'carousel-formats'),
  ('docs/stories.md', 'Stories', 'Writing', 'stories'),
  ('docs/ai-video-rules.md', 'AI video rules', 'Rules', 'ai-video-rules'),
  ('posting/README.md', 'Posting rules', 'Rules', 'posting-rules'),
  ('docs/multiplier.md', 'The 1 → 20 multiplier', 'Engine', 'multiplier'),
  ('research/competitors.md', 'Competitors', 'Research', 'competitors'),
  ('research/ai-content/2026-11-04.md', 'AI content research', 'Research', 'ai-content'),
]


def upload(path: Path, cache: dict) -> str:
    """Upload a file to the app's public `library` bucket; returns its storage path."""
    h = hashlib.sha1(path.read_bytes()).hexdigest()
    if h in cache: return cache[h]
    dest = f'style/files/{h[:16]}{path.suffix.lower()}'
    up = call('mutation', 'ingest:uploadUrl', {'path': dest})
    ct = 'video/mp4' if path.suffix == '.mp4' else 'image/jpeg' if path.suffix in ('.jpg', '.jpeg') else 'application/octet-stream'
    r = requests.put(up['url'], data=path.read_bytes(), headers={'Content-Type': ct, 'x-upsert': 'true'}, timeout=600); r.raise_for_status()
    cache[h] = dest; CACHE.write_text(json.dumps(cache, indent=1))
    return cache[h]


def put_global(table, rows, n=200):
    for i in range(0, max(len(rows), 1), n):
        call('mutation', 'ingest:replaceGlobal', {'table': table, 'rows': rows[i:i + n], 'first': i == 0})
    print(table, len(rows))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--clips'); ap.add_argument('--samples'); ap.add_argument('--picks'); a = ap.parse_args()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    lib = sorted((R / 'docs/brand-video/library').glob('*.json'))
    refs = []
    for f in lib:
        d = json.loads(f.read_text())
        refs.append({'refId': d['id'], 'title': d.get('title', d['id']), 'category': d.get('category'), 'fit': float(d.get('saassuite_fit') or 0), 'summary': d.get('summary'), 'data': d})
    put_global('styleRefs', refs, 40)
    if a.clips:
        cd = Path(a.clips); rows = []
        byref = {r['refId']: r['data'] for r in refs}
        for mp4 in sorted(cd.glob('*__s*.mp4')):
            ref, s = mp4.stem.split('__s'); seg = (byref.get(ref, {}).get('best_segments') or [{}])[int(s)] if s.isdigit() and int(s) < len(byref.get(ref, {}).get('best_segments') or []) else {}
            jpg = mp4.with_suffix('.jpg')
            rows.append({'clipId': mp4.stem, 'refId': ref, 'start': seg.get('start'), 'end': seg.get('end'), 'what': seg.get('what'), 'tests': seg.get('tests'),
                         'storagePath': upload(mp4, cache), **({'posterPath': upload(jpg, cache)} if jpg.exists() else {})})
        put_global('styleClips', rows)
    eds = []
    for i, (k, name, status, fam, ref, defines, music, use) in enumerate(EDITING):
        row = {'key': k, 'name': name, 'status': status, 'family': fam, 'ref': ref, 'defines': defines, 'music': music or None, 'useFor': use, 'order': i}
        if a.samples and (Path(a.samples) / f'{k}.mp4').exists():
            row['samplePath'] = upload(Path(a.samples) / f'{k}.mp4', cache)
            if (Path(a.samples) / f'{k}.jpg').exists(): row['posterPath'] = upload(Path(a.samples) / f'{k}.jpg', cache)
        eds.append(row)
    put_global('editingStyles', eds)
    pm = json.loads((R / 'docs/brand-video/prompt-motion/library.json').read_text())['entries']
    put_global('motionLib', [{'slug': e['slug'], 'title': e['title'], 'creator': e.get('creator'), 'kind': e.get('kind'), 'tags': e.get('tags') or [],
                              'prompt': (e.get('prompt') or e.get('skill_text') or '')[:4000], 'video': (e.get('video') or [None])[0], 'poster': e.get('poster'), 'url': e.get('url')} for e in pm])
    docs = []
    for path, title, group, slug in DOCS:
        p = R / path
        if p.exists(): docs.append({'slug': slug, 'title': title, 'group': group, 'body': p.read_text()[:200_000]})
    for p in sorted((R / 'todo').glob('*.md')):
        docs.append({'slug': f'filming-{p.stem}', 'title': f'Filming list: {p.stem}', 'group': 'Filming list', 'body': p.read_text()[:200_000]})
    print('docs', call('mutation', 'ingest:replace', {'brandKey': BRAND, 'table': 'docs', 'rows': docs, 'first': True}))
    picks = []
    if a.picks:
        for f in Path(a.picks).glob('*.json'):
            d = json.loads(f.read_text()); d = d.get('data', d)
            picks.append({k: d[k] for k in ('a', 'b', 'winner', 'liked', 'disliked', 'note', 'at') if k in d and d[k] is not None} | {'by': 'Andrew'})
    styles = [
        {'name': 'SaaSSuite main (light)', 'useCase': 'No-speaker motion graphics, VSLs, launches, onboarding, statics', 'mode': 'light', 'active': True,
         'palette': {'background': '#F6F5F2', 'ink': '#141418', 'muted': '#6B6F7B', 'accent': '#7B5CFF', 'alt': '#0B0B10', 'captionActive': '#7B5CFF'},
         'fonts': {'display': 'Inter Display 800', 'body': 'Inter'}, 'captions': 'Karaoke: 2–3 white words, spoken word turns violet, lower middle, soft shadow',
         'motion': 'Smooth ease-out, slow 2–4% camera push, floating rebuilt UI cards, one element morphs into the next', 'sound': 'Cinematic ambient ~90 bpm, soft whooshes and UI clicks, −14 LUFS',
         'busyness': 3, 'baseStyles': ['s1'], 'rules': 'One accent colour per frame\nOne violet word per headline\nUI rebuilt as clean floating cards, no device frames\nMorph inside a scene, clean cut between chapters', 'source': 'Style quiz rounds 1–7 + SAASSUITE-STYLE.md'},
        {'name': 'SaaSSuite dark moments', 'useCase': 'Launch reveals, premium moments, CTA end cards', 'mode': 'dark', 'active': True,
         'palette': {'background': '#0B0B10', 'ink': '#F6F5F2', 'muted': '#9A9CA8', 'accent': '#7B5CFF', 'captionActive': '#7B5CFF'},
         'fonts': {'display': 'Inter Display 800', 'body': 'Inter'}, 'captions': 'Same karaoke, violet active word', 'motion': 'Slow camera, soft violet glow 12–18%',
         'sound': 'Ambient swell into the reveal', 'busyness': 2, 'baseStyles': [], 'rules': 'Same font and violet as light\nUse for the hook reveal, the product glow moment and the end card', 'source': 'SAASSUITE-STYLE.md'},
        {'name': 'Short-form yellow captions', 'useCase': 'Podcast clips and reels on proven formats (V1–V8)', 'mode': 'light', 'active': True,
         'palette': {'background': '#000000', 'ink': '#FFFFFF', 'accent': '#FFD23F', 'captionActive': '#FFD23F'}, 'fonts': {'display': 'Inter Tight ExtraBold'},
         'captions': 'Active word yellow #FFD23F (proven: keep it)', 'motion': 'Per format (V1–V8)', 'sound': 'Per format, −16 LUFS', 'busyness': 3,
         'baseStyles': ['v1', 'v2', 'v4', 'v5', 'v6', 'v7', 'v8'], 'rules': "The yellow works: don't recolour\nTrend-driven short form follows the trend's look", 'source': 'Andrew, round 7'},
    ]
    call('mutation', 'styles:seedBrand', {'brandKey': BRAND, 'picks': picks, 'styles': styles})
    print('seeded', len(picks), 'picks,', len(styles), 'brand styles')


if __name__ == '__main__':
    main()
