#!/usr/bin/env python3
"""Build the Meta ads review page (outputs/2026-11-07-meta-ads/review.html) from manifest.csv + videos.csv."""
import csv, html, json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'outputs/2026-11-07-meta-ads'


def esc(s):
    return html.escape(s or '')


def main():
    rows = list(csv.DictReader(open(OUT / 'manifest.csv')))
    vids = list(csv.DictReader(open(OUT / 'videos.csv'))) if (OUT / 'videos.csv').exists() else []
    concepts = {}
    for r in rows:
        concepts.setdefault(r['concept_id'], r)
    data = dict(statics=rows, videos=vids)
    chips = ''.join(f'<button class="chip" data-c="{cid}" type="button">{cid} · {esc(r["concept"])}</button>' for cid, r in concepts.items())
    page = TEMPLATE.replace('__CHIPS__', chips).replace('__DATA__', json.dumps(data).replace('</', '<\\/')) \
        .replace('__NS__', str(len(rows))).replace('__N916__', str(sum(1 for r in rows if r['file_9x16']))) \
        .replace('__NV__', str(len(vids))).replace('__NC__', str(len(concepts)))
    (OUT / 'review.html').write_text(page)
    print('review.html', len(rows), len(vids))


TEMPLATE = r"""<title>Meta Ad Batch Nov 7</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:opsz,wght@6..72,700;6..72,800&display=swap">
<style>
/* Layout: sticky filter bar over a contact-sheet grid; each card = creative + its ad copy, grouped by concept (one ABO ad set each) */
:root{--bg:#F4F5F8;--surface:#FFFFFF;--ink:#0B0F1A;--muted:#5A6275;--line:#DDE1EA;--accent:#FFD23F;--blue:#2E5BFF;
 --display:'Newsreader',Georgia,serif;--body:'Inter',system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B0F1A;--surface:#141A2A;--ink:#EEF1F7;--muted:#9AA3B8;--line:#252D42;--accent:#FFD23F;--blue:#7C9BFF;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0B0F1A;--surface:#141A2A;--ink:#EEF1F7;--muted:#9AA3B8;--line:#252D42;--accent:#FFD23F;--blue:#7C9BFF;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.wrap{max-width:1280px;margin:0 auto}
header{padding-block:36px 18px;display:flex;flex-direction:column;gap:10px}
h1{font:800 clamp(30px,5vw,48px)/1.05 var(--display);letter-spacing:-.5px;text-wrap:balance;margin:0}
.lede{color:var(--muted);max-width:68ch;margin:0}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;font-weight:600;font-variant-numeric:tabular-nums}
.stats b{background:var(--accent);color:#0B0F1A;padding:0 6px;border-radius:4px}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding-block:12px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:10px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip,.tab{font:600 13px var(--body);border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 12px;cursor:pointer}
.chip[aria-pressed="true"],.tab[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.chip:focus-visible,.tab:focus-visible,button:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.scroller{overflow-x:auto;display:flex;gap:8px;padding-bottom:2px}
.scroller .chip{white-space:nowrap}
h2{font:800 28px/1.15 var(--display);margin:34px 0 4px;text-wrap:balance}
.sub{color:var(--muted);margin:0 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.card img,.card video{display:block;width:100%;height:auto;background:#000;max-width:100%}
.meta{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.id{display:flex;justify-content:space-between;gap:8px;font:700 12px var(--body);letter-spacing:.6px;text-transform:uppercase;color:var(--muted)}
.hl{font-weight:700;font-size:15px;line-height:1.3}
.ds{color:var(--muted);font-size:13px}
.lp{font-size:12px;color:var(--muted)}
details{font-size:13px} summary{cursor:pointer;font-weight:600;color:var(--blue)}
details pre{white-space:pre-wrap;font:13px/1.45 var(--body);margin:8px 0 0;color:var(--ink)}
.copy{align-self:flex-start;font:600 12px var(--body);border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:6px;padding:4px 10px;cursor:pointer}
.tag{display:inline-block;font:700 11px var(--body);padding:2px 7px;border-radius:4px;background:var(--accent);color:#0B0F1A}
.concept-h{grid-column:1/-1;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin-top:14px;padding-top:14px;border-top:1px solid var(--line)}
.concept-h b{font:800 20px var(--display)} .concept-h span{color:var(--muted);font-size:13px}
.note{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;max-width:80ch}
.note ol{margin:6px 0 0;padding-left:20px}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
</style>
<div class="wrap">
<header>
 <h1>Meta ad batch · Nov 7</h1>
 <p class="lede">New creatives for the One Feature offer ($99/mo per user) and SaaSSuite (onboarding, training, support). Every face is real Andrew or a real customer; every quote is word for word. Drafts only, nothing is live.</p>
 <div class="stats"><span><b>__NS__</b> statics (4:5)</span><span><b>__N916__</b> also in 9:16</span><span><b>__NV__</b> video ads</span><span><b>__NC__</b> concepts</span></div>
 <div class="note"><b>How to test:</b> one concept = one new ABO ad set with its 4–5 variants. Hands off for 72 hours, judge at 3–5× target cost per result. LP-A = the One Feature breakdown (VSL). LP-B = SaaSSuite free account.</div>
</header>
<div class="bar">
 <div class="row"><button class="tab" data-v="statics" aria-pressed="true" type="button">Statics</button><button class="tab" data-v="videos" aria-pressed="false" type="button">Videos</button>
  <span style="flex:1"></span><button class="tab" id="r45" aria-pressed="true" type="button">4:5</button><button class="tab" id="r916" aria-pressed="false" type="button">9:16 only</button></div>
 <div class="scroller" id="chips"><button class="chip" data-c="" aria-pressed="true" type="button">All concepts</button>__CHIPS__</div>
</div>
<section id="statics"><div class="grid" id="sgrid"></div></section>
<section id="videos" hidden><h2>Video ads</h2><p class="sub">6–15 s, 4:5, captions burned in, end card with the CTA. Motion ads have a quiet music bed; footage ads keep the real voice.</p><div class="grid" id="vgrid"></div></section>
</div>
<script>
const D=__DATA__;
let C='',R='45';
const $=s=>document.querySelector(s);
function e(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
function copyBtn(txt){return `<button class="copy" type="button" data-t="${encodeURIComponent(txt)}">Copy ad copy</button>`}
function adcopy(r){return `Primary text:\n${r.primary_text}\n\nHeadline: ${r.headline}\nDescription: ${r.description}\nCTA: ${r.cta_button}\nLanding page: ${r.landing_page}`}
function renderS(){
 let h='',last='';
 for(const r of D.statics){
  if(C&&r.concept_id!==C)continue;
  if(R==='916'&&!r.file_9x16)continue;
  if(r.concept_id!==last){last=r.concept_id;h+=`<div class="concept-h"><b>${r.concept_id} · ${e(r.concept)}</b><span>${e(r.angle)} · ${e(r.landing_page.split(' (')[0])}</span></div>`}
  const src=R==='916'?r.file_9x16:r.file_4x5;
  h+=`<article class="card"><img loading="lazy" src="${src}" alt="${e(r.headline)}" width="1080" height="${R==='916'?1920:1350}">
  <div class="meta"><div class="id"><span>${r.id}</span><span>${e(r.template)}${r.file_9x16?' · <span class="tag">9:16</span>':''}</span></div>
  <div class="hl">${e(r.headline)}</div><div class="ds">${e(r.hook_name)} · ${e(r.description)} · ${e(r.cta_button)}</div>
  <details><summary>Primary text</summary><pre>${e(r.primary_text)}</pre></details>${copyBtn(adcopy(r))}</div></article>`;
 }
 $('#sgrid').innerHTML=h||'<p class="sub">No creatives match this filter.</p>';
}
function renderV(){
 $('#vgrid').innerHTML=D.videos.map(v=>`<article class="card"><video controls preload="metadata" playsinline muted src="${v.preview}" poster="${v.preview.replace('.mp4','.jpg')}" width="720" height="900"></video>
 <div class="meta"><div class="id"><span>${v.id}</span><span>${e(v.kind)} · ${e(v.duration_s)} s</span></div><div class="hl">${e(v.headline)}</div>
 <div class="ds">${e(v.hook_name)} · ${e(v.source)}</div><details><summary>Primary text</summary><pre>${e(v.primary_text)}</pre></details>${copyBtn(adcopy({...v,cta_button:v.cta_button}))}</div></article>`).join('');
}
document.addEventListener('click',ev=>{
 const t=ev.target.closest('button');if(!t)return;
 if(t.classList.contains('copy')){const s=decodeURIComponent(t.dataset.t);navigator.clipboard.writeText(s).then(()=>{t.textContent='Copied'},()=>{t.textContent='Select the text above to copy'});return}
 if(t.dataset.v){document.querySelectorAll('[data-v]').forEach(b=>b.setAttribute('aria-pressed',b===t));$('#statics').hidden=t.dataset.v!=='statics';$('#videos').hidden=t.dataset.v!=='videos';$('#chips').hidden=t.dataset.v!=='statics';$('#r45').hidden=$('#r916').hidden=t.dataset.v!=='statics';return}
 if(t.classList.contains('chip')){C=t.dataset.c;document.querySelectorAll('.chip').forEach(b=>b.setAttribute('aria-pressed',b===t));renderS();return}
 if(t.id==='r45'||t.id==='r916'){R=t.id==='r45'?'45':'916';$('#r45').setAttribute('aria-pressed',R==='45');$('#r916').setAttribute('aria-pressed',R==='916');renderS()}
});
renderS();renderV();
</script>
"""

if __name__ == '__main__':
    main()
