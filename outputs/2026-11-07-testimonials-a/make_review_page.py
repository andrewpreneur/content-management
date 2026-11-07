#!/usr/bin/env python3
"""Build the testimonials-a review page (HTML) from manifest.csv + uploaded preview asset URLs.
Usage: python3 make_review_page.py assets.json OUT.html   (assets.json: {"<file stem>": "<asset url>"})"""
import csv, html, json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
assets = json.load(open(sys.argv[1])); out = sys.argv[2]
rows = list(csv.DictReader(open(f'{H}/manifest.csv')))
people = {'mark': 'Mark Cleary', 'lee': 'Lee Knaz', 'ben': 'Ben', 'jessica': 'Jessica Garcia', 'tania': 'Tania Cazin', 'multi': 'Supercuts'}
items = []
for r in rows:
    stem = os.path.basename(r['file'])[:-4]
    items.append({'stem': stem, 'id': r['id'], 'person': r['person'], 'fmt': r['format'], 'len': r['length_s'],
                  'cls': r['class'], 'type': r['hook_type'], 'hook': r['hook'], 'url': assets.get(stem, '')})
data = json.dumps(items)
page = r'''<title>Testimonial Ads Review</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a contact-sheet of phone-shaped previews, grouped by client, with a pick bar per clip */
:root{
  --bg:#f3f4f7; --panel:#ffffff; --ink:#0b0f1a; --muted:#5b6478; --line:#dfe2ea;
  --accent:#ffd23f; --accent-ink:#0b0f1a; --blue:#2e7dff; --ok:#1f9d57; --no:#c8323c;
  --display:"Archivo",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0b0f1a;--panel:#161c2c;--ink:#eef1f7;--muted:#a0aabe;--line:#283048;--ok:#3cc47a;--no:#ef5a63;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0b0f1a;--panel:#161c2c;--ink:#eef1f7;--muted:#a0aabe;--line:#283048;--ok:#3cc47a;--no:#ef5a63;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--display);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 64px}
.wrap{max-width:1240px;margin:0 auto;display:flex;flex-direction:column;gap:28px}
header{display:flex;flex-direction:column;gap:10px}
.kick{font:500 12px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
h1{font:900 clamp(30px,5vw,52px)/1 var(--display);margin:0;letter-spacing:-.02em;text-wrap:balance}
h1 mark{background:var(--accent);color:var(--accent-ink);padding:0 .15em}
.lede{max-width:66ch;color:var(--muted);margin:0}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{font:700 13px/1 var(--display);border:1.5px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:9px 14px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.chip:focus-visible,button:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.tally{font:500 13px/1.4 var(--mono);color:var(--muted);margin-left:auto}
section{display:flex;flex-direction:column;gap:14px}
h2{font:900 22px/1.1 var(--display);margin:0;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
h2 small{font:500 12px/1 var(--mono);color:var(--muted);letter-spacing:.06em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.card.approved{border-color:var(--ok);box-shadow:0 0 0 2px var(--ok) inset}
.card.skipped{opacity:.55}
.vid{background:#000;aspect-ratio:9/16;max-width:100%;display:block;width:100%;object-fit:contain}
.card[data-fmt="4:5"] .vid{aspect-ratio:4/5}
.meta{padding:10px 12px 12px;display:flex;flex-direction:column;gap:6px;min-width:0}
.id{font:500 12px/1.2 var(--mono);color:var(--muted);display:flex;gap:6px;flex-wrap:wrap}
.tag{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px 6px}
.tag.t{background:var(--accent);color:var(--accent-ink);border-color:transparent}
.hook{font:700 14px/1.3 var(--display);margin:0;overflow-wrap:anywhere}
.picks{display:flex;gap:6px}
.picks button{flex:1;font:700 12px/1 var(--display);padding:9px 0;border-radius:8px;border:1.5px solid var(--line);background:transparent;color:var(--ink);cursor:pointer}
.picks button[aria-pressed="true"].ok{background:var(--ok);border-color:var(--ok);color:#fff}
.picks button[aria-pressed="true"].no{background:var(--no);border-color:var(--no);color:#fff}
.note{font:500 12px/1.4 var(--mono);color:var(--muted)}
footer{font:500 12px/1.6 var(--mono);color:var(--muted)}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<div class="wrap">
<header>
  <span class="kick">Testimonials A · drafts · Nov 7, 2026</span>
  <h1>56 testimonial ads from <mark>5 clients</mark></h1>
  <p class="lede">Real client footage only. Each ad has a different hook (stat, quote, question, headline or a text card first), word captions, name lower third and an end card with a call to book. Tap <b>Approve</b> or <b>Skip</b> under each one; your picks are saved for the team. Nothing here is posted.</p>
  <div class="bar" role="toolbar" aria-label="Filter">
    <span id="filters" class="bar"></span>
    <span class="tally" id="tally"></span>
  </div>
  <p class="note" id="dbnote">Picks: connecting…</p>
</header>
<div id="groups"></div>
<footer>Full-quality files: branch render-drop/testimonials-a in the content-management repo. Specs, transcripts and quote bank: outputs/2026-11-07-testimonials-a/. Music: Mixkit (free license).</footer>
</div>
<script>
const ITEMS = __DATA__;
const NAMES = __NAMES__;
const NOTES = {tania:"Recorded support call, camera off: her real photo + call audio. Get her OK before paid ads.", jessica:"9-second clip from a call, so 4 hook versions.", ben:"23-second video, so versions differ by hook and order.", mark:"88-second selfie video.", lee:"82-second video.", multi:"Mark, Lee, Ben and Jessica in one ad."};
let filter = 'all', fmt = 'all', picks = {}, db = null;
const $ = s => document.querySelector(s);
function chip(label, on, fn){const b=document.createElement('button');b.className='chip';b.textContent=label;b.setAttribute('aria-pressed',on);b.onclick=fn;return b}
function renderFilters(){
  const f=$('#filters'); f.textContent='';
  f.append(chip('All', filter==='all', ()=>{filter='all';render()}));
  Object.keys(NAMES).forEach(p=>f.append(chip(NAMES[p], filter===p, ()=>{filter=p;render()})));
  f.append(chip('9:16', fmt==='9:16', ()=>{fmt=fmt==='9:16'?'all':'9:16';render()}));
  f.append(chip('4:5', fmt==='4:5', ()=>{fmt=fmt==='4:5'?'all':'4:5';render()}));
}
function card(it){
  const c=document.createElement('article'); c.className='card'; c.dataset.fmt=it.fmt; c.id='c-'+it.stem;
  const st=(picks[it.stem]||{}).status; if(st==='approved')c.classList.add('approved'); if(st==='skipped')c.classList.add('skipped');
  const v=document.createElement('video'); v.className='vid'; v.controls=true; v.preload='metadata'; v.playsInline=true;
  if(it.url){v.src=it.url+'#t=2.5'}
  const m=document.createElement('div'); m.className='meta';
  const id=document.createElement('div'); id.className='id';
  [it.stem, it.fmt, it.len+'s'].forEach(t=>{const s=document.createElement('span');s.className='tag';s.textContent=t;id.append(s)});
  const ty=document.createElement('span'); ty.className='tag t'; ty.textContent=it.type; id.append(ty);
  const h=document.createElement('p'); h.className='hook'; h.textContent=it.hook;
  const pk=document.createElement('div'); pk.className='picks';
  const ok=document.createElement('button'); ok.className='ok'; ok.textContent='Approve'; ok.setAttribute('aria-pressed',st==='approved');
  const no=document.createElement('button'); no.className='no'; no.textContent='Skip'; no.setAttribute('aria-pressed',st==='skipped');
  ok.onclick=()=>setPick(it.stem, st==='approved'?'none':'approved'); no.onclick=()=>setPick(it.stem, st==='skipped'?'none':'skipped');
  pk.append(ok,no); m.append(id,h,pk); c.append(v,m); return c;
}
function render(){
  renderFilters(); const g=$('#groups'); g.textContent='';
  Object.keys(NAMES).forEach(p=>{
    if(filter!=='all'&&filter!==p) return;
    const list=ITEMS.filter(i=>i.person===p&&(fmt==='all'||i.fmt===fmt)); if(!list.length) return;
    const s=document.createElement('section'); const h=document.createElement('h2'); h.textContent=NAMES[p];
    const sm=document.createElement('small'); sm.textContent=list.length+' clips · '+NOTES[p]; h.append(sm);
    const gr=document.createElement('div'); gr.className='grid'; list.forEach(i=>gr.append(card(i)));
    s.append(h,gr); g.append(s);
  });
  const a=Object.values(picks).filter(x=>x.status==='approved').length, k=Object.values(picks).filter(x=>x.status==='skipped').length;
  $('#tally').textContent=ITEMS.length+' clips · '+a+' approved · '+k+' skipped';
}
async function setPick(stem, status){
  picks[stem]={status}; render();
  if(!db){$('#dbnote').textContent='Picks only show on this screen (could not reach the shared store).';return}
  try{await db.doc('picks/'+stem).set({status, at:new Date().toISOString()});$('#dbnote').textContent='Picks saved for the team.'}
  catch(e){$('#dbnote').textContent='Could not save that pick ('+(e&&e.code||'error')+'). You may only have view access.'}
}
render();
(async()=>{
  try{db=await window.claude?.use?.('db')}catch(e){db=null}
  if(!db){$('#dbnote').textContent='Picks only show on this screen (shared store not available here).';return}
  const t=setTimeout(()=>{$('#dbnote').textContent='Picks: store is slow to answer; you can still pick.'},10000);
  db.collection('picks').onSnapshot(snap=>{clearTimeout(t);picks={};snap.docs.forEach(d=>{picks[d.id]=d.data()});$('#dbnote').textContent='Picks are shared with the team.';render()},
    e=>{clearTimeout(t);$('#dbnote').textContent='Could not load saved picks.'});
})();
</script>
'''
page = page.replace('__DATA__', data).replace('__NAMES__', json.dumps(people))
open(out, 'w').write(page)
print('wrote', out, len(items), 'items,', sum(1 for i in items if i['url']), 'with video')
