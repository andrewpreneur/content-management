#!/usr/bin/env python3
"""Content bank: turn bank.json (copy written from existing scripts) into files, rendered carousels and a manifest.

Usage: python3 tools/content_bank.py outputs/content-bank/bank.json
bank.json = [{"key", "script", "feature", "keyword", "claims": [...], "linkedin", "threads": [a, b], "x",
              "slides": [[kicker, title, body], ...]}]   (*word* = accent; last slide renders as the big CTA)
Writes outputs/content-bank/<key>/{linkedin.md, threads-1.md, threads-2.md, x.md, carousel/slide-*.png + carousel.pdf}
plus outputs/content-bank/manifest_spec.json (review page) and manifest.json (Supabase outputs shape).
Rules: copy follows docs/brand.md (voice + But/Therefore). Numbers come only from the source script; each is listed in
"claims" for Andrew to verify before approving.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(bank_path):
    bank_path = Path(bank_path); out = bank_path.parent
    raw = json.loads(bank_path.read_text()); outputs = []
    items = raw['items'] if isinstance(raw, dict) else raw  # dict form adds a 'source' block
    for it in items:
        d = out / it['key']; d.mkdir(parents=True, exist_ok=True)
        head = f"_Source: `{it['script']}` · feature: {it['feature']}_\n"
        (d / 'linkedin.md').write_text(f"# LinkedIn — {it['feature']}\n{head}\n{it['linkedin']}\n")
        for i, t in enumerate(it['threads'], 1):
            (d / f'threads-{i}.md').write_text(f"# Threads {i} — {it['feature']}\n{head}\n{t}\n")
        (d / 'x.md').write_text(f"# X post — {it['feature']}\n{head}\n{it['x']}\n")
        slides = []
        for n, (k, t, b) in enumerate(it['slides']):
            s = {'kicker': k, 'title': t}
            if b:
                s['body'] = b
            if n == 0 or n == len(it['slides']) - 1:
                s['big'] = True
            slides.append(s)
        cd = d / 'carousel'; cd.mkdir(exist_ok=True)
        (cd / 'spec.json').write_text(json.dumps({'slides': slides}, indent=1, ensure_ascii=False))
        subprocess.run([sys.executable, str(ROOT / 'tools' / 'carousel.py'), str(cd / 'spec.json'), str(cd), '--pdf'], check=True)
        note = f"{it['feature']} · keyword {it['keyword']}" + (f" · VERIFY: {' '.join(it['claims'])}" if it['claims'] else '')
        base = dict(platforms=[], parent=None, variant_changes=[], language='en', notes=note)
        k = it['key']
        outputs += [dict(base, key=f'{k}_linkedin', output_type='linkedin_post', file=str(d / 'linkedin.md'), platforms=['linkedin'], title=f'{it["feature"]} · LinkedIn')]
        outputs += [dict(base, key=f'{k}_threads{i}', output_type='threads_post', file=str(d / f'threads-{i}.md'), platforms=['threads'], title=f'{it["feature"]} · Threads {i}') for i in (1, 2)]
        outputs += [dict(base, key=f'{k}_x', output_type='x_thread', file=str(d / 'x.md'), platforms=['x'], title=f'{it["feature"]} · X')]
        outputs += [dict(base, key=f'{k}_carousel', output_type='carousel', file=str(cd / 'carousel.pdf'), platforms=['instagram', 'linkedin', 'facebook'], title=f'{it["feature"]} · Carousel')]
    src = raw.get('source') if isinstance(raw, dict) else None
    spec = {'source': src or {'title': f'{len(items)} Batch-03 scripts (content hub)', 'label': 'Content bank', 'kind': 'scripts',
                       'feature': 'Content bank: 10 scripts → text + carousels', 'duration_s': 0, 'cta_keyword': 'per item',
                       'summary': 'Written from the imported Batch-03 scripts. Numbers are from the scripts; anything to verify is flagged on the card.'},
            'outputs': outputs}
    (out / 'manifest_spec.json').write_text(json.dumps(spec, indent=1, ensure_ascii=False))
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'manifest.py'), str(out), '--spec', str(out / 'manifest_spec.json')], check=True)


if __name__ == '__main__':
    main(sys.argv[1])
