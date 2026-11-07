#!/usr/bin/env python3
"""Write README.md for the vsl-b stream from manifest.jsonl."""
import json
from pathlib import Path
D = Path(__file__).parent
man = [json.loads(l) for l in (D / 'manifest.jsonl').read_text().splitlines() if l.strip()]
PAGE = (D / 'page_url.txt').read_text().strip() if (D / 'page_url.txt').exists() else '(pending)'
NAMES = {'v5': 'VIDEO 5', 'v6': 'VIDEO 6', 'v7': 'VIDEO 7', 'convo': 'ConvoAISchedule', 'dyk': 'DYKCustomAudiences', 'meet': 'MEETINGROOM'}
o = [f'# vsl-b: one-feature VSL edits (Nov 7, 2026 overnight)', '', f'**Review page (previews):** {PAGE}', '',
     f'**Videos:** branch `render-drop/vsl-b` (full-quality H.264 CRF 21, ≤4 Mb/s). {len(man)} renders so far. Nothing posted anywhere.', '',
     '## What each version is',
     '- **A** clean edit: full message, brand kit (navy/yellow, Inter Tight + Playfair accents), word captions, punch-ins every 2-3 s, lower third, motion cards in a split layout, screen-recording cutaways (feature pairs), end card. 9:16, 4:5 and 16:9 (landscape VSL).',
     '- **L** same clean edit in a light theme with pill captions. 9:16 and 4:5.\n- **H1-H3** three different openings on the same body (hook headline + a line pulled from later in the video, then the full message). 9:16.',
     '- **AD** 30-45 s ad cut with hook headline and progress bar. 9:16 and 4:5.',
     '- **M1** no face: full-frame motion cards and screen recordings over Andrew\'s original voice. 9:16 and 4:5.',
     '- **T1** no face, no voice: text + motion cards on music (script condensed from the video). 9:16 and 4:5.', '',
     'How it was made: `tools/vslb/` (ffmpeg face edit + HTML motion overlay rendered with Playwright). Specs per video in `specs/`. Re-render one: `python3 outputs/2026-11-07-vsl-b/specs/v5.py v5-AD-916`.', '',
     '## Every output', '', '| id | source | version | format | length | hook / opening | file |', '|---|---|---|---|---|---|---|']
for r in man:
    hook = r.get('hook', '').replace('*', '').replace('|', '/')
    o.append(f"| {r['id']} | {NAMES.get(r['video'], r['video'])} | {r['kind']} | {r['aspect'].replace('x', ':')} | {r['length']:.0f}s | {hook} | `render-drop/vsl-b:{r['file']}` |")
o += ['', 'Sources (Drive, read-only): ' + '; '.join(sorted({r['source'] for r in man if r.get('source')}))]
(D / 'README.md').write_text('\n'.join(o) + '\n')
print('README', len(man))
