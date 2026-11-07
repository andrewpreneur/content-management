#!/usr/bin/env python3
"""Meta ads round 2 (Nov 7, 2026): 20 statics from exact testimonial quotes + 15 video ads built from the finished
testimonial ads on render-drop/testimonials-a|b (Tania and Mason skipped until Andrew OKs them).
Each video = a 1.8 s hook card (distinct hook) + the finished testimonial ad (its own captions + end card).
python3 tools/meta_ads_round2.py  -> outputs/2026-11-07-meta-ads/round2/{statics/*.jpg, manifest.csv, videos.csv}
                                     videos -> /home/user/work/ma/r2videos (pushed to render-drop/meta-ads by hand)
Quotes are copied from outputs/2026-11-07-testimonials-{a,b}/quote-bank.md word for word.
"""
import csv, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import meta_ads_render as R
import meta_ads_batch_1107 as B

OUT = B.OUT / 'round2'
W = Path('/home/user/work/ma')
AS = W / 'assets'
SRC = W / 'r2src'
VOUT = W / 'r2videos'
MUSIC = W / 'music/music-130.mp3'
LP_C = 'LP-C Work with Andrew 1:1 (URL needed from Andrew)'

# photo crops (4:5) from raw testimonial frames
def crop45(src, dst, y):
    im = Image.open(src); w, h = im.size; ch = int(w * 1.25)
    im.crop((0, y, w, y + ch)).resize((1080, 1350), Image.LANCZOS).save(dst, quality=92)

crop45(W / 'testi/fr/brentney.jpg', AS / 'p_brentney.jpg', 60)
crop45(W / 'testi/fr/ben.jpg', AS / 'p_ben.jpg', 330)

ROB, BRE, BEN, JES = AS / 't_rob.jpg', AS / 't_brentney.jpg', AS / 't_ben.jpg', AS / 't_jessica.jpg'
LEE, MARK = AS / 't_lee_face.jpg', AS / 't_mark_initials.jpg'

BODY_B = ("Real SaaSSuite customers, unscripted.\n\nYou can sign SaaS clients all day. But if nobody onboards, trains and supports them, "
          "they cancel. Therefore SaaSSuite runs that part: training videos, AI answers, and real humans on support.\n\nSee how it works. Start free.")
BODY_C = ("Real client, real words, no script.\n\nAndrew works 1:1 with a few business owners on getting clients online. "
          "Results are individual and depend on the work you put in.\n\nIf you want the same plan for your business, apply below.")

S = []
def st(id, concept, hook, headline, desc, tpl, lp, who, **kw):
    S.append(dict(id=id, concept=concept, hook=hook, headline=headline, desc=desc, tpl=tpl, lp=lp, who=who, v916=False, **kw))

# R2-A: classic quote cards (proof), one per person
st('R2S01', 'R2-A', 'Quote: walked me through', '"Walked me through every step"', 'Brentney, SaaSSuite customer', 'quote', B.LP_B, 'Brentney',
   quote='He literally walked me *through every step* of the way.', name='Brentney', role='SaaSSuite customer', face=BRE, fpos='50% 25%', acc='#C2410C')
st('R2S02', 'R2-A', 'Quote: SaaSSuite is amazing', '"SaaSSuite is amazing"', 'Rob, SaaSSuite customer', 'quote', B.LP_B, 'Rob',
   quote='Just wanted to hop on, say that *SaaSSuite is amazing.*', name='Rob', role='SaaSSuite customer', face=ROB, fpos='50% 30%', bg='#EEF3FB', acc='#2E5BFF', size=80)
st('R2S03', 'R2-A', 'Quote: built for clients + us', '"For our clients. For ourselves."', 'Ben, agency owner', 'quote', B.LP_B, 'Ben',
   quote='We use them to help build out GoHighLevel *for our clients.* We use them to help build it out *for ourselves.*', name='Ben', role='Agency owner', face=BEN, fpos='50% 40%', size=62)
st('R2S04', 'R2-A', 'Quote: so helpful', '"So helpful"', 'Jessica Garcia, client', 'quote', B.LP_B, 'Jessica',
   quote="I'm sure you have so many other people that you're working for. *So just so on top of it.*", name='Jessica Garcia', role='Client, on a call with Andrew', face=JES, fpos='50% 35%', bg='#111', fg='#F5F5F5', acc='#FFD23F', size=62)

# R2-B: Rob's own feature list (feature proof)
st('R2S05', 'R2-B', 'Rob lists the features', 'What Rob named in 20 seconds', 'Menu, dashboard, training, AI, support', 'features', B.LP_B, 'Rob',
   head='“The training videos, the AI, the *support ticket system.*” · Rob', shot=AS / 'ui_cs_20.jpg', size=60,
   items=['Customize the menu', 'Customize your entire dashboard', 'Training videos + AI', 'Support tickets, real humans'])
st('R2S06', 'R2-B', 'Rob: real humans (big)', '"Real humans" answer your clients', 'Rob, SaaSSuite customer', 'dark', B.LP_B, 'Rob',
   kicker='ROB · SAASSUITE CUSTOMER', head='“They have *real humans* on the back answering all of your clients\' questions.”', size=70,
   sub='Not a chatbot. People.', cut=B.TALK2, ph=46, cta='See how it works →')
st('R2S07', 'R2-B', 'Notes: what clients said', 'Things clients have said', 'Their words, word for word', 'notes', B.LP_B, 'Jessica, Brentney, Lee, Rob',
   head='Things clients have said to me', rows=['=“You\'re on top of everything for us.” (Jessica)', '=“He literally walked me through every step of the way.” (Brentney)',
                                               '=“Absolutely worth it.” (Lee)', '=“Highly recommend.” (Rob)'], size=74)
st('R2S08', 'R2-B', 'List: 3 SaaSSuite customers', 'What 3 customers said', 'Rob, Brentney, Ben', 'list', B.LP_B, 'Rob, Brentney, Ben',
   kicker='Unscripted', head='3 customers, in their own words', size=84, foot='SaaSSuite · start free', bg='#F2F6FF', acc='#2E5BFF',
   items=[('“Real humans… answering all of your clients\' questions.”', 'Rob, SaaSSuite customer'),
          ('“Now I have a clear plan and idea, and I can move forward and I can scale.”', 'Brentney, SaaSSuite customer'),
          ('“Always follows through with what he says he\'s going to do.”', 'Ben, agency owner')])

# R2-C: Brentney's before/after (pain → relief)
st('R2S09', 'R2-C', 'Photo: clear plan', '"Now I have a clear plan"', 'Brentney, SaaSSuite customer', 'photo', B.LP_B, 'Brentney',
   photo=AS / 'p_brentney.jpg', tag='Brentney · SaaSSuite customer', head='“Now I have a *clear plan*… and I can scale.”', size=82)
st('R2S10', 'R2-C', 'Before/after in her words', 'Before vs after, her words', 'Brentney, SaaSSuite customer', 'compare', B.LP_B, 'Brentney',
   head='Brentney, before and after (her words)', lt='Before', rt='After', size=60, foot='Brentney · SaaSSuite customer · word for word',
   left=['“I was so confused.”', '“I didn\'t know how to support my customers once I got them signed up”', '“It actually slowed down my business growth.”'],
   right=['“He literally walked me through every step of the way.”', '“Now I have a clear plan and idea”', '“I can move forward and I can scale.”'])
st('R2S11', 'R2-C', 'Sticky: I was so confused', '"I was so confused."', 'Then she got a plan', 'sticky', B.LP_B, 'Brentney',
   text='“I was so confused.”', small='Brentney, SaaSSuite customer, before', size=110)
st('R2S12', 'R2-C', 'Dark: slowed growth', 'Support was slowing her growth', 'Brentney, SaaSSuite customer', 'dark', B.LP_B, 'Brentney',
   kicker='BRENTNEY · SAASSUITE CUSTOMER', head='“It actually *slowed down* my business growth.”', size=82,
   sub='Not knowing how to support customers after they signed up. Here\'s what fixed it.', cut=B.TALK3, ph=44, cta='See how it works →')

# R2-D: Ben, agency owner (trust)
st('R2S13', 'R2-D', 'Photo: follows through', '"Always follows through"', 'Ben, agency owner', 'photo', B.LP_B, 'Ben',
   photo=AS / 'p_ben.jpg', tag='Ben · agency owner', head='“Always *follows through* with what he says he\'s going to do.”', size=76)
st('R2S14', 'R2-D', 'Editorial: highly recommend', '"I highly recommend it"', 'Ben, agency owner', 'editorial', B.LP_B, 'Ben',
   head="“If you're thinking about working with him, *I highly recommend it.*”", sub='Ben, agency owner. Unscripted, filmed in his car.', cut=B.ARMS, ph=58, size=70)
st('R2S15', 'R2-D', 'Quote: good care', '"Taken really good care of us"', 'Ben, agency owner', 'quote', B.LP_B, 'Ben',
   quote="He's been a great resource… *he's taken really good care of us.*", name='Ben', role='Agency owner', face=BEN, fpos='50% 40%', bg='#FFF8E7', acc='#C2410C')

# R2-E: Andrew 1:1 clients (Mark, Lee) → LP-C, flagged
st('R2S16', 'R2-E', 'Big number: 5 clients', '5 online clients in under a month', 'Mark Cleary, personal trainer', 'bigword', LP_C, 'Mark',
   pre='Personal trainer, 12 years:', word='5', wsize=420, head='online clients in less than a month.', acc='#14804A', bg='#EEF8F1',
   sub="“He's helped me land five online clients, which is amazing.” Mark Cleary. Individual result.", cut=B.TALK, ph=44)
st('R2S17', 'R2-E', 'Quote: less like a sales call', '"Less like a sales call"', 'Mark Cleary, personal trainer', 'quote', LP_C, 'Mark',
   quote="It feels a lot less like a sales call. People can tell when you're just trying to sell them something. *We're just offering our help.*",
   name='Mark Cleary', role='Personal trainer · @mark_cleary_fitness', face=MARK, size=56, acc='#14804A', foot='Real client, real words', pill='Work with Andrew →')
st('R2S18', 'R2-E', 'Quote: tremendous', '"Tremendous" support', 'Lee Knaz, coach', 'quote', LP_C, 'Lee',
   quote="The support I've been receiving from Andrew has been *tremendous.*", name='Lee Knaz', role='Coach · @leeknaz888', face=LEE, fpos='50% 40%', bg='#F3EFFF', acc='#6C3BFF', size=74, foot='Real client, real words', pill='Work with Andrew →')
st('R2S19', 'R2-E', 'Editorial: knows + cares', '"Knows what he\'s doing and cares"', 'Lee Knaz, coach', 'editorial', LP_C, 'Lee',
   head="“Someone who *knows what he's doing* and cares about who he's working with.”", sub='Lee Knaz, coach', cut=B.TALK, ph=58, size=70, acc='#6C3BFF')
st('R2S20', 'R2-E', 'Sticky: absolutely worth it', '"Absolutely worth it."', 'Lee Knaz, coach', 'sticky', LP_C, 'Lee',
   text='“Absolutely *worth it.*”', small='Lee Knaz, coach, after working with Andrew', size=120, rot=2)

CONCEPTS2 = {
    'R2-A': ('Customer quote cards', 'Proof / testimonial', BODY_B),
    'R2-B': ('Rob + client lines: what SaaSSuite does', 'Proof + feature', BODY_B),
    'R2-C': ("Brentney's before/after", 'Proof: pain → relief', BODY_B),
    'R2-D': ('Ben, agency owner: trust', 'Proof: trust', BODY_B),
    'R2-E': ('Andrew 1:1 clients (Mark, Lee)', 'Proof: results (individual)', BODY_C),
}

# ---------------------------------------------------------------- videos
V = [  # id, source file, hook text, sub, kicker, LP, who, concept
    ('R2V01', 'rob-02-45.mp4', 'Who answers your clients\' questions at *11 PM?*', 'A SaaSSuite customer on support', None, 'B', 'Rob', 'R2-V1'),
    ('R2V02', 'rob-03.mp4', 'Menu. Dashboard. Training. AI. *Support.*', 'One customer, 20 seconds, unscripted', None, 'B', 'Rob', 'R2-V1'),
    ('R2V03', 'rob-05.mp4', 'Still answering client support *yourself?*', '', None, 'B', 'Rob', 'R2-V1'),
    ('R2V04', 'brentney-02-45.mp4', 'You signed the client. *Then what?*', '', None, 'B', 'Brentney', 'R2-V2'),
    ('R2V05', 'brentney-07.mp4', 'Support was *slowing her growth.*', 'Here\'s what changed', None, 'B', 'Brentney', 'R2-V2'),
    ('R2V06', 'brentney-10.mp4', 'Walked through *every single step.*', '', None, 'B', 'Brentney', 'R2-V2'),
    ('R2V07', 'clients-02.mp4', '3 SaaS owners. *No script.*', '', 'REAL CUSTOMERS · UNSCRIPTED', 'B', 'Brentney, Ben, Rob', 'R2-V3'),
    ('R2V08', 'clients-05.mp4', 'Thinking about SaaSSuite? *Hear it from them.*', '', 'REAL CUSTOMERS · UNSCRIPTED', 'B', 'Ben, Brentney, Rob', 'R2-V3'),
    ('R2V09', 'agency-02-45.mp4', 'Agency owners: who builds your clients\' *HighLevel?*', '', None, 'B', 'Ben', 'R2-V3'),
    ('R2V10', 'agency-06.mp4', 'Built for his clients. *And for his own agency.*', '', None, 'B', 'Ben', 'R2-V3'),
    ('R2V11', 'jessica-01-45.mp4', 'Overheard on a *client call:*', '', 'REAL CLIENT CALL', 'B', 'Jessica', 'R2-V4'),
    ('R2V12', 'ben-01-45.mp4', 'The rarest thing in this industry: *follow-through.*', '', None, 'B', 'Ben', 'R2-V4'),
    ('R2V13', 'lee-01-45.mp4', 'Brand new to social media. *No plan.*', 'A coach on working with Andrew', 'REAL CLIENT · UNSCRIPTED', 'C', 'Lee', 'R2-V5'),
    ('R2V14', 'mark-01-45.mp4', '12 years a trainer. *Stuck on leads.*', 'Individual result', 'REAL CLIENT · UNSCRIPTED', 'C', 'Mark', 'R2-V5'),
    ('R2V15', 'supercut-01-916.mp4', '4 clients. 4 businesses. *One name.*', '', 'REAL CLIENTS · UNSCRIPTED', 'C', 'Mark, Lee, Ben, Jessica', 'R2-V5'),
]
VCON = {'R2-V1': 'Rob: support + features (video)', 'R2-V2': 'Brentney: signed → supported (video)', 'R2-V3': 'Agency + multi-customer (video)',
        'R2-V4': 'Short trust clips (video)', 'R2-V5': 'Andrew 1:1 clients (video)'}
HOOK_LEN = 1.8


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:]); raise SystemExit('failed')


def build_video(vid, src, hook, sub, kicker, lp, who, concept):
    srcp = SRC / src
    w, h = map(int, subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(srcp)],
                                   capture_output=True, text=True).stdout.strip().split(','))
    H = 1350 if h == 1350 else 1920
    tmp = Path(tempfile.mkdtemp(prefix=vid))
    card = R.render_all([dict(id='card', tpl='hook', head=hook, sub=sub, kicker=kicker or 'REAL CUSTOMER · UNSCRIPTED', v916=True, size=96 if H == 1350 else 104)],
                        tmp, ('45',) if H == 1350 else ('916',))[0]
    out = VOUT / f'{vid}.mp4'
    fc = (f"[0:v]scale=1080:{H},fps=30,trim=duration={HOOK_LEN},setsar=1,format=yuv420p[c];"
          f"[2:a]atrim=0:{HOOK_LEN},volume=0.5,afade=t=in:d=0.2,afade=t=out:st={HOOK_LEN-0.3}:d=0.3,aresample=48000,aformat=channel_layouts=stereo[ca];"
          f"[1:v]fps=30,setsar=1,format=yuv420p[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];"
          f"[c][ca][v1][a1]concat=n=2:v=1:a=1[v][a]")
    run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-t', str(HOOK_LEN), '-i', str(card), '-i', str(srcp), '-ss', '20', '-i', str(MUSIC),
         '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(out)])
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out)], capture_output=True, text=True).stdout)
    prev = W / 'r2prev'; prev.mkdir(exist_ok=True)
    pw, ph = (720, 900) if H == 1350 else (540, 960)
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf', f'scale={pw}:{ph}', '-c:v', 'libx264', '-crf', '25', '-preset', 'fast', '-c:a', 'aac', '-b:a', '96k',
         '-movflags', '+faststart', str(prev / f'{vid}.mp4')])
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.9', '-i', str(out), '-frames:v', '1', '-vf', f'scale={pw//4*2}:-2', '-q:v', '4', str(prev / f'{vid}.jpg')])
    return dict(id=vid, src=src, dur=round(dur, 1), fmt='4:5' if H == 1350 else '9:16', H=H)


def main():
    OUT.mkdir(parents=True, exist_ok=True); VOUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else None
    if not only or any(x.startswith('R2S') for x in only):
        R.render_all(S, OUT / 'statics', ('45',), only)
    with open(OUT / 'manifest.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'concept_id', 'concept', 'angle', 'hook_name', 'format', 'template', 'file_4x5', 'file_9x16', 'headline', 'primary_text',
                    'description', 'cta_button', 'landing_page', 'person'])
        for s in S:
            name, angle, body = CONCEPTS2[s['concept']]
            first = B._clean(s.get('quote') or s.get('head') or s.get('text') or '')
            w.writerow([s['id'], s['concept'], name, angle, s['hook'], 'static', s['tpl'], f"round2/statics/{s['id']}.jpg", '', s['headline'],
                        first + '\n\n' + body, s['desc'], 'Learn More', s['lp'], s['who']])
    rows = []
    for v in V:
        if only and v[0] not in only:
            continue
        print(v[0], flush=True)
        m = build_video(*v)
        vid, src, hook, sub, kicker, lp, who, concept = v
        body = BODY_B if lp == 'B' else BODY_C
        rows.append([vid, concept, VCON[concept], 'testimonial + hook card', m['dur'], m['fmt'], B._clean(hook), src + (' (render-drop/testimonials-a)' if src[:3] in ('jes', 'ben', 'lee', 'mar', 'sup') else ' (render-drop/testimonials-b)'),
                     B._clean(hook), B._clean(hook) + '\n\n' + body, who, 'Learn More' if lp == 'C' else 'Sign Up',
                     {'B': B.LP_B, 'C': LP_C}[lp], f'branch render-drop/meta-ads: meta-ads/round2/{vid}.mp4', f'r2previews/{vid}.mp4'])
    if not only:
        with open(OUT / 'videos.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'concept_id', 'concept', 'kind', 'duration_s', 'format', 'hook_name', 'source', 'headline', 'primary_text', 'description',
                        'cta_button', 'landing_page', 'file', 'preview'])
            w.writerows(rows)


if __name__ == '__main__':
    main()
