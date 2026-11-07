#!/usr/bin/env python3
"""Review page for the vsl-a stream. python3 tools/vsl/review_page_vsla.py manifest.json assets.json out.html"""
import html, json, sys

man = json.load(open(sys.argv[1]))
assets = json.load(open(sys.argv[2])) if len(sys.argv) > 3 else {}
out = sys.argv[-1]

INFO = {
 'V1': ('VIDEO 1 · "Greatest advancement since ChatGPT"', 'Teaser VSL. Feature is not named; sends people to the full training.',
        ['Kept behind closed doors for 6 weeks', 'Brand-new account started a few months ago', 'Built in one live training']),
 'V2': ('VIDEO 2 · "Jensen Huang said…"', 'AI Studio (vibe coding) in GHL, white-labeled, sold alone for $99/month.',
        ['Jensen Huang quote, All-In podcast (check wording before ads)', 'Customers pay $99/month for one feature', '30-day free trial + free onboarding and sales video']),
 'V3': ('VIDEO 3 · "Sell the shovels"', 'Gold-rush angle: everyone digs, you sell the shovel (AI Studio, $99/month).',
        ['NVIDIA CEO: more millionaires in 5 years than the internet in 20', 'Customers pay $99/month for one feature', 'Free to start for 30 days']),
 'V4': ('VIDEO 4 · "Looking for 15 people"', 'Scarcity angle: 15 spots, AI Studio sold for $99/month.',
        ['Newest agency has 300 sub-accounts on this one feature', '15 spots', '$99/month, start free for 30 days']),
}
ORDER = ['A', 'V916', 'V45', 'H1', 'H2', 'H3', 'H1V', 'H2V', 'H3V', 'S916', 'S45', 'M916', 'M169', 'M45', 'T45', 'T916']
GROUP = {'A': 'Clean edit', 'V916': 'Clean edit', 'V45': 'Clean edit', 'H1': 'Hook tests', 'H2': 'Hook tests', 'H3': 'Hook tests',
         'H1V': 'Hook tests', 'H2V': 'Hook tests', 'H3V': 'Hook tests', 'S916': 'Short ad cut', 'S45': 'Short ad cut',
         'M916': 'No face', 'M169': 'No face', 'M45': 'No face', 'T45': 'No face', 'T916': 'No face'}


def card(r):
    url = assets.get(r['id'])
    ar = {'16:9': '16 / 9', '9:16': '9 / 16', '4:5': '4 / 5'}.get(r['format'], '16 / 9')
    media = (f'<video src="{html.escape(url)}" controls preload="metadata" playsinline style="aspect-ratio:{ar}"></video>' if url
             else f'<div class="ph" style="aspect-ratio:{ar}">Preview uploading</div>')
    return f'''<article class="clip f{r['format'].replace(':', '')}">
  {media}
  <div class="meta"><div class="row"><code>{r['id']}</code><span class="pill">{r['format']}</span><span class="len">{r['length']:.0f}s</span></div>
  <p class="desc">{html.escape(r['desc'])}</p>
  <p class="hook"><span>Opens with</span> {html.escape(r['hook'])}</p></div>
</article>'''


secs = []
for vid in ('V1', 'V2', 'V3', 'V4'):
    rows = sorted([r for r in man if r['video'] == vid], key=lambda r: ORDER.index(r['variant']) if r['variant'] in ORDER else 99)
    if not rows: continue
    t, sub, claims = INFO[vid]
    groups = []
    for g in ('Clean edit', 'Hook tests', 'Short ad cut', 'No face'):
        rs = [r for r in rows if GROUP.get(r['variant']) == g]
        if rs: groups.append(f'<h3>{g} <small>{len(rs)}</small></h3><div class="grid">{"".join(card(r) for r in rs)}</div>')
    secs.append(f'''<section id="{vid.lower()}"><header class="vh"><h2>{html.escape(t)}</h2><p>{html.escape(sub)}</p>
<ul class="claims">{"".join(f"<li>{html.escape(c)}</li>" for c in claims)}</ul></header>{"".join(groups)}</section>''')

n = len(man)
page = f'''<title>VSL Cuts · Videos 1–4</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;700;800&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet">
<style>
/* Layout: one column of sections, one per source VSL; each section groups its cuts into rows of players. Brand kit, dark only. */
:root{{--bg:#0B0F1A;--panel:#141A29;--line:#232B40;--fg:#F3F5FA;--mut:#9AA4BA;--y:#FFD23F;--blue:#2E7DFF;
  --sans:'Inter Tight',system-ui,-apple-system,Segoe UI,sans-serif;--serif:'Instrument Serif',Georgia,serif;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:15px;line-height:1.45}}
.wrap{{max-width:1240px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:32px 64px}}
.top h1{{font-size:clamp(30px,5vw,52px);font-weight:800;letter-spacing:-.02em;margin:0;text-wrap:balance}}
.top h1 i{{font-family:var(--serif);font-weight:400;color:var(--y)}}
.top p{{color:var(--mut);max-width:70ch;margin:10px 0 0}}
.kick{{display:inline-block;background:var(--blue);color:#fff;font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px;border-radius:30px;margin-bottom:14px}}
nav{{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 8px}}
nav a{{color:var(--fg);text-decoration:none;border:1px solid var(--line);padding:7px 14px;border-radius:30px;font-weight:700;font-size:13px}}
nav a:hover,nav a:focus-visible{{border-color:var(--y);outline:none}}
.legend{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin-top:18px}}
.legend div{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--mut);font-size:13.5px}}
.legend b{{color:var(--fg);display:block;margin-bottom:2px}}
section{{margin-top:56px}}
.vh h2{{font-size:clamp(22px,3vw,30px);margin:0;font-weight:800;letter-spacing:-.01em;text-wrap:balance}}
.vh p{{color:var(--mut);margin:6px 0 0}}
.claims{{display:flex;flex-wrap:wrap;gap:6px;list-style:none;padding:0;margin:12px 0 0}}
.claims li{{font-size:12.5px;border:1px solid var(--line);border-radius:8px;padding:4px 9px;color:var(--mut)}}
h3{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--y);margin:28px 0 12px}}
h3 small{{color:var(--mut);font-size:12px;margin-left:6px}}
.grid{{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}}
.clip{{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;min-width:0;width:270px;max-width:100%}}
.clip.f169{{width:480px}}
.clip video,.clip .ph{{display:block;width:100%;max-width:100%;background:#000}}
.ph{{display:grid;place-items:center;color:var(--mut);font-size:13px}}
.meta{{padding:10px 12px 12px}}
.row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
code{{font-size:12.5px;color:var(--fg);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
.pill{{font-size:11px;font-weight:700;background:var(--line);border-radius:20px;padding:2px 8px}}
.len{{font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums;margin-left:auto}}
.desc{{margin:6px 0 0;font-size:13.5px}}
.hook{{margin:6px 0 0;font-size:13px;color:var(--mut)}}
.hook span{{color:var(--y);font-weight:700;margin-right:4px}}
@media (max-width:560px){{.clip,.clip.f169{{width:100%}}}}
</style>
<div class="wrap">
<header class="top"><span class="kick">vsl-a · Nov 7 overnight</span>
<h1>Four VSLs, <i>{n} cuts</i></h1>
<p>Every cut uses Andrew's real footage and voice, or no face at all. Nothing is posted. Pick the ones you like and tell Claude the ids.
Full-quality files are on the <code>render-drop/vsl-a</code> branch; these players are smaller previews.</p>
<nav>{''.join(f'<a href="#{v.lower()}">Video {v[1]}</a>' for v in ('V1', 'V2', 'V3', 'V4') if any(r['video'] == v for r in man))}</nav>
<div class="legend"><div><b>Clean edit</b>Brand-kit edit of the talking video: captions, punch-ins, lower third, motion cards. 16:9, 9:16, 4:5.</div>
<div><b>Hook tests</b>Same body, three different cold opens with a hook box. Test these against each other.</div>
<div><b>Short ad cut</b>20 to 40 seconds, built from the strongest lines.</div>
<div><b>No face</b>Original voice over motion graphics, or text and music only.</div></div>
</header>
{''.join(secs)}
</div>'''
open(out, 'w').write(page)
print('wrote', out, n)
