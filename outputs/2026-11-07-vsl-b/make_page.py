#!/usr/bin/env python3
"""Build the vsl-b review page from manifest.jsonl + assets.json (render id -> asset url). Usage: make_page.py OUT.html"""
import json, sys, html
from pathlib import Path
D = Path(__file__).parent
man = [json.loads(l) for l in (D / 'manifest.jsonl').read_text().splitlines() if l.strip()]
assets = json.loads((D / 'assets.json').read_text()) if (D / 'assets.json').exists() else {}
VIDEOS = [('v5', 'VIDEO 5', 'AI Studio: vibe coding became word of the year; sell it for $99/mo'),
          ('v6', 'VIDEO 6', 'AI Studio is easier to sell than everything else combined'),
          ('v7', 'VIDEO 7', 'I sell one GHL feature for $99/mo: the 3-step setup'),
          ('convo', 'ConvoAISchedule', 'Working hours for Conversation AI agents (face + screen)'),
          ('dyk', 'DYKCustomAudiences', 'Smart lists as Meta custom + lookalike audiences (face + screen)'),
          ('meet', 'MEETINGROOM', 'HighLevel Meeting Rooms (face + screen)')]
ORDER = ['clean edit', 'clean edit (landscape VSL)', 'clean edit, light theme', 'hook 1', 'hook 2', 'hook 3', 'ad cut', 'motion, no face, original voice', 'text + motion, music only, no voice']
AR = {'9x16': '9 / 16', '4x5': '4 / 5', '16x9': '16 / 9'}
LBL = {'9x16': '9:16', '4x5': '4:5', '16x9': '16:9'}
def card(r):
    url = assets.get(r['id'])
    media = (f'<video controls preload="none" playsinline src="{url}" poster=""></video>' if url else '<div class="pending">Preview uploading</div>')
    hook = f'<p class="hook">“{html.escape(r["hook"].replace("*", ""))}”</p>' if r.get('hook') else ''
    return (f'<article class="clip" data-kind="{html.escape(r["kind"])}" data-ar="{r["aspect"]}"><div class="frame" style="aspect-ratio:{AR[r["aspect"]]}">{media}</div>'
            f'<div class="meta"><div class="row"><span class="id">{r["id"]}</span><span class="len">{r["length"]:.0f}s · {LBL[r["aspect"]]}</span></div>'
            f'<p class="kind">{html.escape(r["kind"])}</p>{hook}<p class="file">render-drop/vsl-b/{r["file"]}</p></div></article>')
secs = []
for key, name, desc in VIDEOS:
    rs = sorted([r for r in man if r['video'] == key], key=lambda r: (ORDER.index(r['kind']) if r['kind'] in ORDER else 99, r['aspect']))
    if not rs: continue
    secs.append(f'<section id="{key}"><header class="sh"><h2>{name}</h2><p>{html.escape(desc)} · {len(rs)} versions</p></header><div class="grid">{"".join(card(r) for r in rs)}</div></section>')
kinds = sorted({r['kind'] for r in man}, key=lambda k: ORDER.index(k) if k in ORDER else 99)
chips = ''.join(f'<button type="button" class="f" data-k="{html.escape(k)}">{html.escape(k)}</button>' for k in kinds)
nav = ''.join(f'<a href="#{k}">{n}</a>' for k, n, _ in VIDEOS if any(r['video'] == k for r in man))
page = (D / 'page_template.html').read_text().replace('{{COUNT}}', str(len(man))).replace('{{SECTIONS}}', ''.join(secs)).replace('{{CHIPS}}', chips).replace('{{NAV}}', nav)
Path(sys.argv[1]).write_text(page)
print('page', len(man), 'renders,', len(assets), 'with previews')
