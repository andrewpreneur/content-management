#!/usr/bin/env python3
"""vsl-a stream (Nov 7, 2026): one-feature VSLs VIDEO 1-4 -> iterations.
  python3 tools/vsl/specs_vsla.py V2 A H1 H2 ...     (variant ids below; 'all' = every variant)
Variants: A clean 16:9 · V916 / V45 clean vertical / feed · H1-H3 hooks (4:5) · S916 / S45 short ad cut ·
          M916 voice + motion graphics, no face (9:16) · M169 same 16:9 · T45 text-only + music (4:5) · T916
Sources: /home/user/work/vsla/src/vN.mp4 (4K Drive originals), transcripts /home/user/work/vsla/tN/transcript.json.
"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import vsl

WORK = Path('/home/user/work/vsla')
OUT = WORK / 'out'
MUSIC = WORK / 'music'

ACC = {'one', '1', '99', '$99', 'free', 'ai studio', 'aistudio', 'vibe', 'shovels', 'shovel', 'billions', 'millions', '300', '15', 'simple', 'resell'}
JENSEN = dict(type='quote', text='AI is the greatest technology *equalizer* of all time.', by='JENSEN HUANG, NVIDIA CEO · ALL-IN PODCAST', size=88)
COMPARE = dict(type='compare', title='More millionaires in *5 years* than the internet made in 20',
               bars=[dict(label='The internet', value='20 years', pct=100), dict(label='AI', value='5 years', pct=25, hi=1)])
LOGOS = ['Lovable', 'ChatGPT', 'Claude', 'Base44']
CTA = dict(type='cta', kicker='FREE FOR 30 DAYS', title='See exactly how I sell *one feature*', button='Tap the link below', sub='Start free for 30 days')
AI_STUDIO = dict(type='statement', kicker="IT'S CALLED", lines=['AI *Studio*'], size=150, ky=1)
APP_GENERIC = dict(type='app', title='You type. *AI builds it.*', brand='AI Builder', url='ai-builder.app', prompt='Make me a website for my business', type_at=0.5, type_dur=1.4)
APP_WHITE = dict(type='app', title='Your logo. *One button.*', brand='YourBrand', url='app.yourbrand.com', prompt='Make me a website for my gym', type_at=0.9, type_dur=1.6)
STAT99 = dict(type='stat', kicker='WHAT THEY PAY ME', value=99, prefix='$', suffix='/month', label='for *one* feature', ky=1)

V = {
 'V1': dict(dur=43.9, music='music-1168.mp3', mstart=0.3,
   cards=[
     dict(at=5.30, dur=5.6, layout='left', type='strike', title="I'm not talking about", items=['Writing emails', 'Social posts', 'Voice AI agents'], times=[0.5, 2.5, 3.9], final='Something *simpler*', final_at=8.3 - 5.3, end_src=10.9),
     dict(at=13.08, dur=2.4, type='statement', lines=['This is *simple*.', "That's the difference."], size=104),
     dict(at=16.44, dur=4.4, layout='left', type='statement', kicker='KEPT QUIET', lines=['Behind closed doors', 'for *6 weeks*'], size=92),
     dict(at=27.92, dur=2.9, layout='left', type='statement', kicker='PROOF', lines=['A *brand new* account', 'started a few months ago'], size=80),
     dict(at=31.04, dur=4.4, type='statement', lines=['Built in *one*', 'live training'], size=120),
     dict(at=37.16, dur=4.2, layout='left', type='strike', title='Sell just one feature', items=['The CRM', 'Calendars', 'Automations'], times=[0.5, 1.5, 2.5], final='*One* high-demand feature', final_at=3.0),
     dict(at=41.74, dur=2.2, type='cta', kicker='FULL TRAINING', title='Sell *one* GHL feature', button='Click below', sub='Watch the full training'),
   ],
   hooks={'H1': ([36.10, 41.30], 'Sell *1 feature*. Delete the rest.'),
          'H2': ([16.44, 20.80], 'I kept this *secret* for 6 weeks'),
          'H3': ([13.08, 15.45], 'Not another AI agent. *Simpler.*')},
   short=[[0.0, 4.95], [15.54, 22.5], [27.92, 35.4], [35.74, 41.3], [41.74, 43.9]],
 ),
 'V2': dict(dur=94.8, music='music-1168.mp3', mstart=0.3,
   cards=[
     dict(at=2.76, dur=3.4, **JENSEN),
     dict(at=6.32, dur=4.4, layout='left', **COMPARE),
     dict(at=19.00, dur=3.5, type='statement', lines=['I think I cracked the code:', '*One* feature.'], size=96),
     dict(at=26.46, dur=1.3, **dict(type='statement', kicker='THE FEATURE', lines=['Vibe *coding*'], size=150, ky=1)),
     dict(at=31.68, dur=4.9, **APP_GENERIC),
     dict(at=36.76, dur=6.0, layout='left', type='chips', title='All making *millions*', items=LOGOS, times=[0.15, 0.5, 1.4, 1.7], foot='Demand is *insane*', foot_at=5.0),
     dict(at=46.04, dur=3.5, layout='left', type='statement', lines="Don't just use it.|*Resell* it.".split('|'), size=104),
     dict(at=49.72, dur=1.4, **AI_STUDIO),
     dict(at=53.94, dur=3.2, layout='left', type='statement', lines=['Your brand on it.', 'Sold as *your own*.'], size=92),
     dict(at=57.22, dur=6.5, type='strike', title="I don't sell", items=['All of GHL', 'The CRM', 'Calendars', 'Automations'], times=[0.3, 2.3, 3.3, 4.3], final='Just *one* feature', final_at=5.4),
     dict(at=63.78, dur=6.7, **dict(APP_WHITE, prompt='Make me a website for my business', type_at=4.4, type_dur=1.4)),
     dict(at=70.80, dur=3.4, **STAT99),
     dict(at=74.30, dur=3.4, layout='left', type='statement', lines=['Today: *no one*.', 'In a year: thousands.'], size=96),
     dict(at=83.94, dur=3.2, layout='left', type='stat', kicker='TRY IT', value=30, label='days *free*', ky=1),
     dict(at=87.26, dur=4.4, type='chips', title='Plus, free:', items=['Onboarding video', 'Sales video'], times=[1.0, 2.0], foot='The exact setup *I use*', foot_at=3.4),
     dict(at=91.80, dur=3.0, **CTA),
   ],
   hooks={'H1': ([70.94, 73.95], '$99 a month for *ONE* feature'),
          'H2': ([74.30, 77.30], 'Nobody is doing this *yet*'),
          'H3': ([63.78, 67.50], 'My customers see *one button*')},
   short=[[0.0, 10.55], [22.66, 27.70], [46.04, 51.05], [63.78, 74.10], [77.92, 82.40], [83.94, 86.90]],
 ),
 'V3': dict(dur=81.1, music='music-1168.mp3', mstart=0.3,
   cards=[
     dict(at=3.36, dur=1.9, layout='left', type='statement', lines=['The money was in', 'selling *shovels*.'], size=96),
     dict(at=5.40, dur=5.5, layout='left', **COMPARE),
     dict(at=13.26, dur=7.6, type='chips', title='Everyone is *digging*', items=['AI agents', 'Automation agencies', 'Websites, one client at a time'], times=[2.9, 3.9, 5.6]),
     dict(at=21.14, dur=11.3, layout='left', type='strike', title='Selling the whole toolbox', items=['The CRM', 'Automations', 'Calendars', 'Everything'], times=[3.7, 4.3, 4.95, 5.5], final='They want *one tool*', final_at=9.6),
     dict(at=34.22, dur=2.9, type='statement', lines=['I sell just', '*one* GHL feature.'], size=110),
     dict(at=37.28, dur=1.3, **AI_STUDIO),
     dict(at=39.50, dur=3.2, **dict(APP_GENERIC, type_at=0.3, type_dur=1.2)),
     dict(at=42.94, dur=5.1, layout='left', type='chips', title='Worth *billions*', items=['Lovable', 'Claude', 'ChatGPT', 'Base44'], times=[0.1, 0.45, 0.95, 1.7], foot='They sell the *shovel*', foot_at=4.3),
     dict(at=48.14, dur=4.9, type='versus', a=dict(head='Theirs', items=["Can't put your name on it", "Can't resell it"]), b=dict(head='AI Studio', items=['*Your* name on it', 'Resell it']), b_at=3.1),
     dict(at=55.28, dur=7.4, **dict(APP_WHITE, title='Your logo. *One button.*', prompt='Make me a website for my bakery', type_at=4.2, type_dur=1.4)),
     dict(at=62.90, dur=2.9, **STAT99),
     dict(at=65.92, dur=2.0, layout='left', type='statement', lines=['Sell it to', '*as many people* as you want'], size=84),
     dict(at=68.10, dur=4.3, type='statement', lines=["Don't dig.", '*Hand out shovels.*'], size=120),
     dict(at=72.58, dur=2.2, layout='left', type='statement', lines=['Almost nobody', 'is doing this *yet*.'], size=96),
     dict(at=78.30, dur=2.8, **CTA),
   ],
   hooks={'H1': ([62.98, 65.70], '$99 a month for *ONE* feature'),
          'H2': ([68.10, 72.30], 'Stop digging. *Sell shovels.*'),
          'H3': ([21.24, 27.05], 'Stop selling *the whole toolbox*')},
   short=[[0.0, 4.95], [34.22, 38.98], [48.14, 53.0], [55.28, 65.55], [68.10, 72.30], [74.98, 80.9]],
 ),
 'V4': dict(dur=64.8, music='music-1168.mp3', mstart=0.3,
   cards=[
     dict(at=2.62, dur=1.9, layout='left', type='seats', title='Looking for *15 people*', n=15, foot='who want in on AI'),
     dict(at=4.64, dur=4.2, layout='left', type='statement', lines=['Every day:', '*the next big thing*.'], size=96),
     dict(at=11.82, dur=1.8, type='statement', lines=['Just *one* feature.'], size=130),
     dict(at=16.86, dur=1.6, **STAT99),
     dict(at=18.50, dur=4.7, layout='left', type='strike', title="It's not", items=['A course', 'A bunch of features', 'A done-for-you service'], times=[0.3, 1.1, 2.0], final='*One* feature I resell', final_at=3.4),
     dict(at=23.34, dur=0.85, **dict(type='statement', kicker='THE FEATURE', lines=['Vibe *coding*'], size=150, ky=1)),
     dict(at=27.20, dur=3.4, **dict(APP_GENERIC, type_at=0.3, type_dur=1.3)),
     dict(at=30.70, dur=3.1, layout='left', type='chips', title='Making *billions*', items=['Lovable', 'ChatGPT', 'Claude'], times=[0.1, 0.5, 1.1]),
     dict(at=33.90, dur=4.6, type='versus', a=dict(head='Them', items=["Can't resell"]), b=dict(head='AI Studio', items=['*You* can resell']), b_at=2.3),
     dict(at=38.78, dur=7.9, **dict(APP_WHITE, title='Your name. Your logo. *Your colors.*', type_at=5.6, type_dur=1.4)),
     dict(at=49.38, dur=4.5, type='counter', kicker='MY NEWEST AGENCY', value=300, label='sub-accounts on *one feature*', dots=300, cols=20, count=1.8),
     dict(at=53.92, dur=4.5, layout='left', type='seats', title='Helping *15 people*', n=15, foot="When the spots are gone, they're gone"),
     dict(at=58.52, dur=6.3, **CTA),
   ],
   hooks={'H1': ([49.38, 53.80], '*300 sub-accounts.* One feature.'),
          'H2': ([46.90, 49.15], 'I kept this *quiet*. It worked too well.'),
          'H3': ([44.14, 46.70], 'Type one sentence. *Get a website.*')},
   short=[[0.0, 4.5], [11.82, 18.4], [36.20, 38.70], [38.78, 46.7], [49.38, 53.8], [53.92, 58.45], [58.52, 64.8]],
 ),
}

LAYOUT_V = {'left': 'top'}  # half-screen cards on vertical canvases sit on top, face below


def words_of(vid):
    return vsl.load_words(WORK / f't{vid[1]}' / 'transcript.json')


def place_cards(cfg, cut, aspect, mode, skip_before=0.0):
    """Source-anchored cards -> output-time events."""
    evs = []
    for c in cfg['cards']:
        o = cut.to_out(c['at'])
        if o is None or o < skip_before - 0.01: continue
        e = {k: v for k, v in c.items() if k not in ('at', 'dur', 'end_src')}
        e.update(k='card', s=round(o, 3), e=round(o + c['dur'], 3))
        lay = e.get('layout', 'full')
        if mode != 'overlay': lay = 'full'
        elif aspect != '16x9': lay = 'full' if e['type'] == 'cta' else 'top'
        e['layout'] = lay
        if lay == 'top':
            e['capY'] = vsl.SPLIT[aspect] + 0.005
            if e['type'] == 'app': e['w'] = 980
        evs.append(e)
    evs.sort(key=lambda e: e['s'])
    for a, b in zip(evs, evs[1:]):  # no overlaps
        if a['e'] > b['s'] - 0.05: a['e'] = round(b['s'] - 0.05, 3)
    for e in evs: e['e'] = min(e['e'], cut.dur)
    return [e for e in evs if e['e'] - e['s'] > 0.5]


def fill_words(evs, words, dur):
    """Motion mode: every stretch not covered by a module card gets a 'words' scene (sentence typography)."""
    out = list(evs)
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if w['w'][-1:] in '.?!' or len(cur) >= 11: sents.append(cur); cur = []
    if cur: sents.append(cur)
    covered = lambda t: any(e['s'] - 0.05 <= t < e['e'] for e in evs)
    for s in sents:
        ws = [w for w in s if not covered((w['s'] + w['e']) / 2)]
        if not ws: continue
        # split around cards
        groups, g = [], [ws[0]]
        for a, b in zip(ws, ws[1:]):
            if any(a['e'] <= e['s'] < b['s'] for e in evs): groups.append(g); g = [b]
            else: g.append(b)
        groups.append(g)
        for g in groups:
            out.append(dict(k='card', type='words', layout='full', s=round(max(0, g[0]['s'] - 0.12), 3), e=round(g[-1]['e'] + 0.25, 3),
                            ws=[dict(w=x['w'], s=x['s'], acc=x['acc']) for x in g], tin=0.12, tout=0.1, size=None))
    out.sort(key=lambda e: e['s'])
    for a, b in zip(out, out[1:]):
        if a['e'] > b['s']: a['e'] = b['s']
        if b['s'] - a['e'] < 0.6 and a['type'] == 'words': a['e'] = b['s']  # hold sentence until next scene
    for e in out:
        if e['type'] == 'words': e.pop('size', None)
    if out: out[-1]['e'] = dur
    return out


def make(vid, var):
    cfg = V[vid]; words = words_of(vid); src = str(WORK / 'src' / f'v{vid[1]}.mp4')
    aspect = {'A': '16x9', 'V916': '9x16', 'V45': '4x5', 'H1': '4x5', 'H2': '4x5', 'H3': '4x5', 'S916': '9x16', 'S45': '4x5',
              'M916': '9x16', 'M169': '16x9', 'M45': '4x5', 'T45': '4x5', 'T916': '9x16', 'H1v': '9x16', 'H2v': '9x16', 'H3v': '9x16'}[var]
    mode = 'motion' if var.startswith('M') else ('text' if var.startswith('T') else 'overlay')
    full = [[0.0, cfg['dur']]]
    hook = None
    if var.startswith('H'):
        hr, htxt = cfg['hooks'][var[:2]]; ranges = [hr] + full; hook = (hr, htxt)
    elif var.startswith('S'):
        ranges = cfg['short']
    else:
        ranges = full
    if mode == 'text':
        return make_text(vid, var, cfg, aspect)
    cut = vsl.Cut(words, ranges)
    ow = cut.out_words(ACC | {'ai studio'})
    for w in ow:
        k = w['w'].lower().strip('.,?!')
        if k in ('ai studio',): w['acc'] = 1
    body0 = 0.0
    if hook:
        # first segment that starts at source 0 after the hook = body start
        starts = [o for a, b, o in cut.segs if a < 0.05]
        body0 = starts[-1] if starts else body0
    evs = place_cards(cfg, cut, aspect, mode, skip_before=body0)
    if mode == 'motion':
        evs = fill_words(evs, ow, cut.dur)
        if hook: evs.insert(0, dict(k='hook', s=0.0, e=body0, text=hook[1]))
    else:
        evs.append(dict(k='lower3', s=round(body0 + 1.2, 2), e=round(body0 + 5.2, 2)))
        if hook: evs.append(dict(k='hook', s=0.0, e=round(body0 - 0.05, 2), text=hook[1]))
    overrides = []
    for e in evs:
        if e.get('k') == 'card' and e['layout'] == 'left': overrides.append((e['s'], e['e'], 'R'))
        if e.get('k') == 'card' and e['layout'] == 'top': overrides.append((e['s'], e['e'], 'B'))
    pattern = ('W', 'T', 'W', 'C', 'T', 'W') if aspect == '16x9' else ('W', 'T', 'C', 'W', 'T', 'C')
    if hook: overrides.insert(0, (0, body0, 'C'))
    shots = cut.shots(pattern=pattern, overrides=overrides, every=3.2)
    sfx = [(e['s'] - 0.07, 'whoosh', -26) for e in evs if e.get('k') == 'card' and e['type'] != 'words']
    sfx += [(e['s'] + 0.3, 'pop', -24) for e in evs if e.get('k') == 'card' and e['type'] in ('stat', 'counter', 'cta')]
    music = dict(file=str(MUSIC / cfg['music']), db=-6 if mode == 'overlay' else -3, duck=-8, start=cfg['mstart'])
    plan = dict(words=ow, events=evs, mode=mode)
    if mode == 'motion':
        plan['capY'] = {'9x16': 0.80, '4x5': 0.84, '16x9': 0.86}[aspect]
        for e in evs:
            if e.get('k') == 'card' and e['type'] != 'words' and aspect == '9x16': e.setdefault('scale', 1.15)
            if e.get('type') == 'app' and aspect != '16x9': e['w'] = 940
    for e in evs:
        if e.get('type') == 'stat' and 'count' not in e: e['count'] = min(0.9, max(0.4, (e['e'] - e['s']) * 0.35))
    return dict(plan=plan, cut=cut, src=src, aspect=aspect, shots=shots, music=music, sfx=sfx, mode=mode)


TEXT = {  # text-only + music scripts (no voice): scene list (dur seconds, card)
 'V1': [(2.4, dict(type='statement', kicker='NOT ANOTHER AI AGENT', lines=['The *simplest* AI', 'business right now'], size=96)),
        (3.4, dict(type='strike', title='Not this', items=['Writing emails', 'Social posts', 'Voice AI agents'], times=[0.3, 0.9, 1.5], final='Something *simpler*', final_at=2.3)),
        (2.6, dict(type='statement', kicker='KEPT QUIET', lines=['Behind closed doors', 'for *6 weeks*'], size=96)),
        (3.0, dict(type='strike', title='Sell just one feature', items=['The CRM', 'Calendars', 'Automations'], times=[0.3, 0.8, 1.3], final='*One* high-demand GHL feature', final_at=1.9)),
        (2.4, dict(type='statement', lines=['Built in *one*', 'live training'], size=120)),
        (3.4, dict(type='cta', kicker='FULL TRAINING', title='Sell *one* GHL feature', button='Watch the training', sub='Link below'))],
 'V2': [(3.0, dict(JENSEN)), (3.0, dict(COMPARE)), (2.2, dict(type='statement', kicker='THE FEATURE', lines=['Vibe *coding*'], size=150, ky=1)),
        (3.4, dict(APP_GENERIC, type_at=0.4, type_dur=1.2)), (2.6, dict(type='chips', title='All making *millions*', items=LOGOS, times=[0.3, 0.5, 0.7, 0.9], foot='You can *resell* it', foot_at=1.7)),
        (2.0, dict(AI_STUDIO)), (3.2, dict(type='strike', title="I don't sell", items=['All of GHL', 'The CRM', 'Calendars', 'Automations'], times=[0.2, 0.6, 1.0, 1.4], final='Just *one* feature', final_at=2.0)),
        (3.6, dict(APP_WHITE, prompt='Make me a website for my business', type_at=0.8, type_dur=1.3)), (2.6, dict(STAT99, count=0.7)),
        (3.4, dict(CTA))],
 'V3': [(2.6, dict(type='statement', lines=['In every gold rush,', 'sell the *shovels*.'], size=100)), (3.0, dict(COMPARE)),
        (3.0, dict(type='chips', title='Everyone is *digging*', items=['AI agents', 'Automation agencies', 'One-off websites'], times=[0.3, 0.6, 0.9])),
        (3.0, dict(type='strike', title='Stop selling the whole toolbox', items=['The CRM', 'Automations', 'Calendars'], times=[0.3, 0.7, 1.1], final='Sell *one tool*', final_at=1.8)),
        (2.0, dict(AI_STUDIO)), (3.6, dict(APP_WHITE, prompt='Make me a website for my bakery', type_at=0.8, type_dur=1.3)),
        (2.4, dict(STAT99, count=0.7)), (2.4, dict(type='statement', lines=["Don't dig.", '*Hand out shovels.*'], size=120)), (3.4, dict(CTA))],
 'V4': [(2.4, dict(type='seats', title='Looking for *15 people*', n=15, foot='who want in on AI')),
        (2.2, dict(type='statement', lines=['Just *one* feature.'], size=130)), (2.6, dict(STAT99, count=0.7)),
        (3.0, dict(type='strike', title="It's not", items=['A course', 'A bunch of features', 'A done-for-you service'], times=[0.3, 0.7, 1.1], final='*One* feature I resell', final_at=1.8)),
        (2.0, dict(AI_STUDIO)), (3.6, dict(APP_WHITE, title='Your name. Your logo. *Your colors.*', type_at=0.8, type_dur=1.3)),
        (3.0, dict(type='counter', kicker='MY NEWEST AGENCY', value=300, label='sub-accounts on *one feature*', dots=300, cols=20, count=1.4)),
        (3.4, dict(CTA))],
}


def make_text(vid, var, cfg, aspect):
    evs, t = [], 0.0
    for d, c in TEXT[vid]:
        e = copy.deepcopy(c); e.update(k='card', layout='full', s=round(t, 3), e=round(t + d, 3)); evs.append(e); t += d
    dur = round(t, 3)
    sfx = [(e['s'] - 0.07, 'whoosh', -20) for e in evs[1:]] + [(e['s'] + 0.3, 'pop', -20) for e in evs if e['type'] in ('stat', 'counter', 'cta')]
    music = dict(file=str(MUSIC / 'music-130.mp3'), db=0, duck=0, start=0.5)
    plan = dict(words=[], events=evs, mode='motion', noCaptions=True, dur=dur)
    if aspect == '9x16':
        for e in evs: e.setdefault('scale', 1.15)
    return dict(plan=plan, cut=None, src=None, aspect=aspect, shots=None, music=music, sfx=sfx, mode='text')


ALL = ['A', 'V916', 'V45', 'H1', 'H2', 'H3', 'S916', 'S45', 'M916', 'T45']

if __name__ == '__main__':
    vid = sys.argv[1]; vars_ = ALL if sys.argv[2:] == ['all'] else sys.argv[2:]
    import time
    for var in vars_:
        t0 = time.time(); s = make(vid, var)
        out = OUT / vid / f'{vid.lower()}-{var.lower()}.mp4'
        vsl.render(s['plan'], out, src=s['src'], cut=s['cut'], aspect=s['aspect'], shots=s['shots'], music=s['music'], sfx=s['sfx'], mode=s['mode'],
                   keep=str(out) + '.html')
        json.dump(dict(plan=s['plan'], shots=s['shots'], aspect=s['aspect'], mode=s['mode']), open(str(out) + '.spec.json', 'w'))
        print(f'{out.name} {time.time() - t0:.0f}s', flush=True)
