#!/usr/bin/env python3
"""One-feature VSL editor: talking-head source (+ optional screen recording) -> branded edits.

Pipeline: spec (python dict) -> output timeline (keep ranges) -> shots (face punch-ins / split with graphic / full graphic /
screen recording) -> base video via ffmpeg -> HTML overlay (tools/vslb/overlay.html: cards, captions, lower third, hook,
end card) rendered by Playwright and composited in one ffmpeg pass with voice + ducked music.

Styles: 'face'  = talking head with graphics (split/full beats), captions, punch-ins
        'motion'= no face: full-frame motion cards over the original voice (gaps auto-filled with sentence cards)
        'text'  = no face, no voice: timed text + motion cards over music
Used by outputs/2026-11-07-vsl-b/specs/*.py. Run: python3 <spec.py> [variant ...]
"""
import json, math, os, re, subprocess, sys, tempfile, html as H
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / 'fonts'
SFX = HERE.parents[1] / 'vendor/motion-graphics/skills/sound-effects/sfx'
FPS = 30

ASPECTS = {
    # W, H, face box in split, graphic box in split, caption y (face/split/full), cap size, lower third (x,y,size), hook y/size, U
    '9x16': dict(W=1080, H=1920, faceBox=(0, 880, 1080, 1040), splitBox=(0, 0, 1080, 880), capY=dict(face=1290, split=880, full=1560),
                 capSize=74, lt=(56, 1430, 50), hook=(250, 78), U=dict(split=80, full=118), pill=(170, 30)),
    '4x5': dict(W=1080, H=1350, faceBox=(0, 610, 1080, 740), splitBox=(0, 0, 1080, 610), capY=dict(face=1010, split=610, full=1150),
                capSize=62, lt=(48, 1120, 42), hook=(70, 64), U=dict(split=54, full=92), pill=(40, 24)),
    '16x9': dict(W=1920, H=1080, faceBox=(1000, 0, 920, 1080), splitBox=(0, 0, 1000, 1080), capY=dict(face=930, split=930, full=930),
                 capSize=60, lt=(70, 760, 46), hook=(70, 64), U=dict(split=66, full=88), pill=(40, 24)),
}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.stderr.write(' '.join(map(str, cmd))[:600] + '\n' + r.stderr[-3000:]); raise SystemExit(1)
    return r.stdout


def probe(p):
    d = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,codec_type:format=duration', '-of', 'json', p]))
    v = [s for s in d['streams'] if s['codec_type'] == 'video'][0]
    return v['width'], v['height'], float(d['format']['duration'])


def load_words(path):
    d = json.load(open(path)); segs = d['segments'] if isinstance(d, dict) else d
    words, sents = [], []
    for s in segs:
        ws = []
        for w in s['words']:
            t = w['w'].strip()
            if not t: continue
            if t.startswith('-') and ws: ws[-1] = (ws[-1][0] + t, ws[-1][1], w['e']); continue
            ws.append((t, w['s'], w['e']))
        words += ws
        if ws: sents.append((s['start'], s['end'], s['text'].strip(), ws))
    return words, sents


norm = lambda s: re.sub(r"[^a-z0-9$]", '', s.lower())


def find(words, phrase, after=0.0):
    """source time of the first word of `phrase` (first match at/after `after`)."""
    if isinstance(phrase, (int, float)): return float(phrase)
    toks = [norm(x) for x in phrase.split() if norm(x)]
    nw = [norm(w[0]) for w in words]
    for i in range(len(words)):
        if words[i][1] + 1e-3 < after: continue
        if nw[i:i + len(toks)] == toks: return words[i][1]
    raise SystemExit(f'phrase not found: {phrase!r}')


def find_end(words, phrase, after=0.0):
    toks = [norm(x) for x in phrase.split() if norm(x)]
    nw = [norm(w[0]) for w in words]
    for i in range(len(words)):
        if words[i][1] + 1e-3 < after: continue
        if nw[i:i + len(toks)] == toks: return words[i + len(toks) - 1][2]
    raise SystemExit(f'phrase not found: {phrase!r}')


# ---------------------------------------------------------------- card helpers (HTML snippets for overlay.html)
def rich(t):
    """*accent* -> playfair italic yellow"""
    t = H.escape(t)
    return re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)


def c_text(head, kicker=None, sub=None):
    o = []
    if kicker: o.append(f'<div class="k" data-in="0">{H.escape(kicker)}</div><div class="gap"></div>')
    o.append(f'<div class="h" data-in="0.08">{rich(head)}</div>')
    if sub: o.append(f'<div class="gap"></div><div class="s" data-in="0.45">{rich(sub)}</div>')
    return ''.join(o)


def c_big(big, sub=None, kicker=None, count=None, pre='', suf='', yellow=False):
    o = []
    if kicker: o.append(f'<div class="k" data-in="0">{H.escape(kicker)}</div><div class="gap"></div>')
    if count is not None:
        o.append(f'<div class="big{" y" if yellow else ""}" data-in="0.05"><span class="{"y" if yellow else ""}" data-count="0.05" data-to="{count}" data-pre="{pre}" data-suf="{suf}">{pre}0{suf}</span></div>')
    else:
        o.append(f'<div class="big" data-in="0.05">{rich(big)}</div>')
    if sub: o.append(f'<div class="gap"></div><div class="s" data-in="0.4">{rich(sub)}</div>')
    return ''.join(o)


def c_chips(items, title=None, strike=None, on=None, step=0.3, t0=0.1, sub=None):
    """items: list of str; strike: time to strike all; on: {index: time} to highlight"""
    o = []
    if title: o.append(f'<div class="h" data-in="0" style="font-size:calc(var(--u)*0.8)">{rich(title)}</div><div class="gap"></div>')
    o.append('<div class="row">')
    for i, it in enumerate(items):
        x = f'<span class="x" data-strike="{strike + i * 0.12:.2f}"></span>' if strike is not None else ''
        onat = f' data-on="{on[i]:.2f}"' if on and i in on else ''
        o.append(f'<div class="chip" data-in="{t0 + i * step:.2f}"{onat}>{H.escape(it)}{x}</div>')
    o.append('</div>')
    if sub: o.append(f'<div class="gap"></div><div class="s" data-in="{t0 + len(items) * step + 0.2:.2f}">{rich(sub)}</div>')
    return ''.join(o)


def c_toggles(items, title=None, t_off=0.5, step=0.28):
    """items: [(name, final_on)]; switches start ON and flip to final state one by one."""
    o = []
    if title: o.append(f'<div class="k" data-in="0">{H.escape(title)}</div><div class="gap"></div>')
    o.append('<div class="panel" data-in="0.05">')
    k = 0
    for name, fin in items:
        if fin:
            o.append(f'<div class="tg" data-flip="{t_off + len(items) * step:.2f}" data-to="on"><span>{H.escape(name)}</span><div class="sw"><b></b></div></div>')
        else:
            o.append(f'<div class="tg" data-flip="{t_off + k * step:.2f}" data-to="off"><span>{H.escape(name)}</span><div class="sw" style="background:#FFD23F"><b style="left:52%"></b></div></div>')
            k += 1
    o.append('</div>')
    return ''.join(o)


def c_chat(prompt, result='Live in minutes', t_res=None):
    t_res = t_res if t_res is not None else 0.4 + len(prompt) * 0.045 + 0.3
    return (f'<div class="chat"><div class="bubble" data-in="0.05"><span data-type="0.25" data-txt="{H.escape(prompt)}"></span></div>'
            f'<div class="res" data-in="{t_res:.2f}"><div class="bar"><i></i><i></i><i></i></div><div class="bd"><div class="hero"></div>'
            f'<div class="ln" style="width:70%"></div><div class="ln" style="width:92%"></div><div class="ln" style="width:55%"></div></div></div>'
            f'<div style="text-align:center"><span class="live" data-in="{t_res + 0.5:.2f}">● {H.escape(result)}</span></div></div>')


def c_price(amount, per='/mo', sub=None, kicker=None, count=True):
    o = []
    if kicker: o.append(f'<div class="k" data-in="0">{H.escape(kicker)}</div><div class="gap"></div>')
    num = re.sub(r'[^0-9]', '', amount)
    if count and num:
        o.append(f'<div class="price" data-in="0.05"><span data-count="0.05" data-to="{num}" data-pre="$">$0</span><small>{H.escape(per)}</small></div>')
    else:
        o.append(f'<div class="price" data-in="0.05">{H.escape(amount)}<small>{H.escape(per)}</small></div>')
    if sub: o.append(f'<div class="gap"></div><div class="s" data-in="0.45">{rich(sub)}</div>')
    return ''.join(o)


def c_steps(items, title=None, step=0.45, t0=0.15):
    o = []
    if title: o.append(f'<div class="h" data-in="0" style="font-size:calc(var(--u)*0.8)">{rich(title)}</div><div class="gap"></div>')
    o.append('<div class="steps">')
    for i, it in enumerate(items):
        o.append(f'<div class="st" data-in="{t0 + i * step:.2f}"><b>{i + 1}</b><span>{rich(it)}</span></div>')
    o.append('</div>')
    return ''.join(o)


def c_cmp(a_t, a_v, b_t, b_v, title=None):
    o = []
    if title: o.append(f'<div class="h" data-in="0" style="font-size:calc(var(--u)*0.8)">{rich(title)}</div><div class="gap"></div>')
    o.append(f'<div class="cmp"><div class="a" data-in="0.1"><div class="t">{H.escape(a_t)}</div><div class="v">{rich(a_v)}</div></div>'
             f'<div class="bb" data-in="0.5"><div class="t">{H.escape(b_t)}</div><div class="v">{rich(b_v)}</div></div></div>')
    return ''.join(o)


def c_cta(head='Tap the link below', btn='Get the setup', sub=None):
    o = [f'<div class="h" data-in="0">{rich(head)}</div><div class="gap"></div><div class="btn" data-in="0.35">{H.escape(btn)} →</div>']
    if sub: o.append(f'<div class="gap"></div><div class="s" data-in="0.7">{rich(sub)}</div>')
    return ''.join(o)


def c_line(words, t0, accents=()):
    """sentence card: words light up as spoken. words=[(w, s, e)] in output time."""
    acc = {norm(a) for a in accents}
    sp = []
    for w, s, e in words:
        cls = ' class="acc"' if norm(w) in acc else ''
        sp.append(f'<span data-w="{max(0, s - t0):.2f}"{cls}>{H.escape(w)}</span>')
    return f'<div class="line" data-in="0">{" ".join(sp)}</div>'


def c_label(text):
    return f'<div class="k" data-in="0" style="position:absolute;top:calc(var(--u)*0.5);left:0;right:0">{H.escape(text)}</div>'


def end_html(head, btn, sub, U):
    return (f'<div style="--u:{U}px;display:flex;flex-direction:column;align-items:center">'
            f'<div class="k" data-in="0">Andrew George · The One Feature guy</div><div class="gap"></div>'
            f'<div class="h" data-in="0.15">{rich(head)}</div><div class="gap"></div>'
            f'<div class="btn" data-in="0.45">{H.escape(btn)} →</div>'
            + (f'<div class="gap"></div><div class="s" data-in="0.75">{rich(sub)}</div>' if sub else '') + '</div>')


# ---------------------------------------------------------------- timeline
class TL:
    """maps source time <-> output time through keep ranges"""

    def __init__(self, keep):
        self.keep = keep; self.offs = []; o = 0.0
        for a, b in keep: self.offs.append(o); o += b - a
        self.T = o

    def out(self, s):
        for (a, b), o in zip(self.keep, self.offs):
            if a - 1e-3 <= s <= b + 1e-3: return o + (min(max(s, a), b) - a)
        return None


def chunk_words(ow, maxw=3, gap=0.35):
    out, cur = [], []
    for i, w in enumerate(ow):
        cur.append(w); nx = ow[i + 1] if i + 1 < len(ow) else None
        brk = re.search(r'[.,?!]$', w[0]) or len(cur) >= maxw or not nx or nx[1] - w[2] > gap or (len(cur) >= 2 and len(''.join(x[0] for x in cur)) > 16)
        if brk: out.append(cur); cur = []
    ch = []
    for i, c in enumerate(out):
        t0 = c[0][1]; t1 = min(out[i + 1][0][1] if i + 1 < len(out) else c[-1][2] + 0.5, c[-1][2] + 0.6)
        ch.append(dict(t0=round(t0, 3), t1=round(t1, 3), w=[[H.escape(x[0].strip('"')), round(x[1], 3)] for x in c]))
    return ch


def build(spec, outdir, work):
    A = ASPECTS[spec['aspect']]; W, Hh = A['W'], A['H']
    style = spec.get('style', 'face')
    work = Path(work); work.mkdir(parents=True, exist_ok=True)
    vid = spec['id']
    words, sents = load_words(spec['words']) if spec.get('words') else ([], [])
    # ---- keep ranges
    if style == 'text':
        T = sum(b['dur'] for b in spec['beats']); tl = None
    else:
        keep = []
        for a, b in spec['keep']:
            a = find(words, a) if isinstance(a, str) else a
            b = find_end(words, b, a) if isinstance(b, str) else b
            keep.append((max(0, a - 0.06), b + 0.12))
        tl = TL(keep); T = tl.T
    ow = []
    if tl:
        for w, s, e in words:
            o = tl.out(s)
            if o is not None and tl.out(e) is not None: ow.append((w, o, tl.out(e)))
    # ---- beats -> output time
    beats = []
    if style == 'text':
        t = 0
        for b in spec['beats']:
            beats.append(dict(t0=t, t1=t + b['dur'], mode='full', html=b['card'], nocap=True)); t += b['dur']
    else:
        for b in spec.get('beats', []):
            s0 = find(words, b['at'], b.get('after', 0)) if isinstance(b['at'], str) else b['at']
            o0 = tl.out(s0)
            if o0 is None: continue
            if 'until' in b:
                s1 = find_end(words, b['until'], s0) if isinstance(b['until'], str) else b['until']; o1 = tl.out(s1)
            elif 'dur' in b: o1 = o0 + b['dur']
            else:
                o1 = None
            if o1 is None:  # end of the sentence containing s0
                sn = [x for x in sents if x[0] - 0.05 <= s0 <= x[1] + 0.05]
                o1 = tl.out(sn[0][1]) if sn else o0 + 2.5
                if o1 is None: o1 = o0 + 2.5
            o0 = max(0, o0 - b.get('lead', 0.12)); o1 = max(o1 + b.get('tail', 0.15), o0 + b.get('min', 1.6))
            card = b['card'](o0) if callable(b['card']) else b['card']
            beats.append(dict(t0=round(o0, 3), t1=round(min(o1, T), 3), mode=b.get('mode', spec.get('beat_mode', 'split')), html=card,
                              nocap=b.get('nocap', False), src_t=b.get('src_t'), hold=b.get('hold'), scr=b.get('scr')))
        beats.sort(key=lambda x: x['t0'])
        if spec.get('hook') and style == 'face':  # the hook headline owns the opening: no graphic under it
            hd = spec['hook'].get('dur', 3.0)
            for b in beats:
                if b['t0'] < hd: b['t0'] = hd
            beats = [b for b in beats if b['t1'] - b['t0'] > 1.0]
        for i in range(len(beats) - 1):  # no overlaps
            beats[i]['t1'] = min(beats[i]['t1'], beats[i + 1]['t0'])
        beats = [b for b in beats if b['t1'] - b['t0'] > 0.5]
        if style == 'motion':  # fill gaps with sentence cards
            fill, t = [], 0.0
            for b in beats + [dict(t0=T, t1=T)]:
                if b['t0'] - t > 0.6:
                    gw = [w for w in ow if t - 0.01 <= w[1] < b['t0']]
                    # one card per sentence-ish group
                    grp, cur = [], []
                    for i, w in enumerate(gw):
                        cur.append(w)
                        if re.search(r'[.?!]$', w[0]) or len(cur) >= 9 or i == len(gw) - 1: grp.append(cur); cur = []
                    while len(grp) > 1 and len(grp[-1]) < 3: grp[-2] += grp.pop()
                    grp = [g for g in grp if g]
                    i = 1
                    while i < len(grp):
                        if len(grp[i]) < 3: grp[i - 1] += grp.pop(i)
                        else: i += 1
                    gt = t
                    for gi, g in enumerate(grp):
                        g1 = grp[gi + 1][0][1] if gi + 1 < len(grp) else b['t0']
                        fill.append(dict(t0=round(gt, 3), t1=round(g1, 3), mode='full', html=c_line(g, gt, spec.get('accents', ())), nocap=True))
                        gt = g1
                t = max(t, b['t1'])
            beats = sorted(beats + [f for f in fill if f['t1'] - f['t0'] > 0.3], key=lambda x: x['t0'])
            for b in beats: b['mode'] = 'screen' if b['mode'] == 'screen' else 'full'
    # ---- shots
    shots = []
    ZC = spec.get('zooms', [1.0, 1.32, 1.0, 1.55])
    zi = 0
    t = 0.0
    bnds = []
    for b in beats: bnds += [(b['t0'], b)]
    def face_span(a, z_):
        nonlocal zi
        # split [a, z_] into shots at word starts every ~2.2-3.4s
        cuts = [a]
        while z_ - cuts[-1] > 3.6:
            target = cuts[-1] + 2.6
            cand = [w[1] for w in ow if cuts[-1] + 1.8 < w[1] < min(cuts[-1] + 3.4, z_ - 1.2)]
            c = min(cand, key=lambda x: abs(x - target)) if cand else cuts[-1] + 2.6
            cuts.append(c)
        cuts.append(z_)
        for i in range(len(cuts) - 1):
            shots.append(dict(t0=cuts[i], t1=cuts[i + 1], mode='face', zoom=ZC[zi % len(ZC)])); zi += 1
    for b in beats:
        if b['t0'] > t + 0.05: face_span(t, b['t0'])
        if style == 'face':
            shots.append(dict(t0=b['t0'], t1=b['t1'], mode=b['mode'], zoom=spec.get('split_zoom', 1.25), src_t=b.get('src_t'), hold=b.get('hold'), scr=b.get('scr')))
        else:
            shots.append(dict(t0=b['t0'], t1=b['t1'], mode=b['mode'], zoom=1, src_t=b.get('src_t'), scr=b.get('scr'), noface=True))
        t = b['t1']
    if T - t > 0.05:
        if style == 'face': face_span(t, T)
        else: shots.append(dict(t0=t, t1=T, mode='full', zoom=1))
    if tl and len(tl.keep) > 1:  # never let one shot run across a keep-range seam
        new = []
        for s in shots:
            cuts = [s['t0']] + [o for o in tl.offs[1:] if s['t0'] + 0.01 < o < s['t1'] - 0.01] + [s['t1']]
            for a, b in zip(cuts, cuts[1:]):
                n_ = dict(s, t0=a, t1=b)
                if s.get('src_t') is not None: n_['src_t'] = s['src_t'] + (a - s['t0'])
                new.append(n_)
        shots = new
    # frame-quantise
    for s in shots: s['f0'] = round(s['t0'] * FPS); s['f1'] = round(s['t1'] * FPS)
    shots = [s for s in shots if s['f1'] > s['f0']]
    for i in range(1, len(shots)): shots[i]['f0'] = shots[i - 1]['f1']
    shots[-1]['f1'] = round(T * FPS)
    for s in shots: s['t0'] = s['f0'] / FPS; s['t1'] = s['f1'] / FPS
    # screen hole rectangles + screen crop
    for s in shots:
        if s['mode'] == 'screen':
            bx = (0, 0, W, Hh) if s.get('noface') else A['splitBox']; s['box'] = list(bx)
            m = int(min(bx[2], bx[3]) * 0.035); top = int(A['U']['split'] * 1.1)
            w = bx[2] - 2 * m; h = bx[3] - 2 * m - top
            s['hole'] = [bx[0] + m, bx[1] + m + top, w // 2 * 2, h // 2 * 2]
            sw_, sh_ = spec['screen_size']; ar = s['hole'][2] / s['hole'][3]
            cx, cy, wf = s.get('scr') or (0.5, 0.5, 1.0)
            if wf >= 0.99:  # whole screen frame: fit a 16:9 hole inside the box (the SCREEN files carry their own zooms)
                hx, hy, hw, hh = s['hole']; sar = sw_ / sh_
                if hw / hh > sar: nw = int(hh * sar) // 2 * 2; s['hole'] = [hx + (hw - nw) // 2, hy, nw, hh]
                else: nh = int(hw / sar) // 2 * 2; s['hole'] = [hx, hy + (hh - nh) // 2, hw, nh]
                ar = sar
            cw = wf * sw_; ch = cw / ar
            if ch > sh_: ch = sh_; cw = ch * ar
            x = min(max(cx * sw_ - cw / 2, 0), sw_ - cw); y = min(max(cy * sh_ - ch / 2, 0), sh_ - ch)
            s['scrop'] = (int(cw) // 2 * 2, int(ch) // 2 * 2, int(x), int(y))
    # ---- base video
    base = work / f'{vid}.base.mp4'
    render_base(spec, A, shots, T, base, work)
    # ---- audio
    aud = work / f'{vid}.aud.m4a'
    render_audio(spec, tl, T, aud, beats)
    # ---- overlay data
    hook = None
    if spec.get('hook'):
        hk = spec['hook']; hy, hs = A['hook']
        hook = dict(t0=0.0, t1=hk.get('dur', 3.0), html=rich(hk['text']), y=hk.get('y', hy), size=hk.get('size', hs))
    lt = None
    if spec.get('lt', style == 'face'):
        fs = [s for s in shots if s['mode'] == 'face' and s['t0'] >= 1.0 and s['t1'] - s['t0'] > 2]
        if fs:
            s = fs[0]; x, y, sz = A['lt']
            lt = dict(t0=s['t0'] + 0.2, t1=min(s['t1'] - 0.1, s['t0'] + 3.6), x=x, y=y, size=sz, name='Andrew George', title=spec.get('lt_title', 'The One Feature guy · HighLevel SaaS'))
    end = None
    if spec.get('end'):
        e = spec['end']; end = dict(t0=T - e.get('dur', 2.5), html=end_html(e['head'], e.get('btn', 'Get the setup'), e.get('sub'), A['U']['full']))
    pill = None
    if spec.get('pill'):
        py, ps = A['pill']; pill = dict(t0=0, t1=spec['pill'].get('dur', T), text=spec['pill']['text'], y=py, size=ps)
    D = dict(W=W, H=Hh, T=T, FPS=FPS, U=A['U'], splitBox=A['splitBox'], capY=A['capY'], capSize=A['capSize'],
             capStyle=spec.get('cap_style', 'plain'), capSplitX=[A['faceBox'][0], A['faceBox'][2]] if spec['aspect'] == '16x9' else None, capOn=spec.get('caps', style == 'face') and bool(ow),
             chunks=chunk_words(ow) if ow else [], beats=beats, shots=[dict(t0=s['t0'], t1=s['t1'], mode=s['mode'], hole=s.get('hole'), box=s.get('box')) for s in shots],
             lt=lt, hook=hook, end=end, pill=pill, prog=spec.get('prog', False))
    dj = work / f'{vid}.data.json'; dj.write_text(json.dumps(D))
    page = work / 'overlay.html'
    page.write_text((HERE / 'overlay.html').read_text().replace('__FONTS__', 'file://' + str(FONTS)))
    out = Path(outdir) / f'{vid}.mp4'; out.parent.mkdir(parents=True, exist_ok=True)
    ff = ['-i', str(base), '__PIPE__', '-i', str(aud), '-filter_complex', '[0:v]tpad=stop_mode=clone:stop_duration=5[b];[b][1:v]overlay=0:0:format=auto:eof_action=pass,format=yuv420p[v]',
          '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '4000k', '-bufsize', '8000k',
          '-r', str(FPS), '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-t', f'{T:.3f}', str(out)]
    fj = work / f'{vid}.ff.json'; fj.write_text(json.dumps(ff))
    r = subprocess.run(['node', str(HERE / 'render_overlay.js'), str(page), str(dj), str(fj)], capture_output=True, text=True)
    if r.returncode: sys.stderr.write(r.stderr[-3000:]); raise SystemExit(1)
    if not os.environ.get('VSL_KEEP'):
        for p in (base, aud): p.unlink(missing_ok=True)
    return out, T, shots, beats


def crop_for(sw, sh, box_w, box_h, zoom, fx, fy, face_top=0.36):
    ar = box_w / box_h
    ch = sh / zoom; cw = ch * ar
    if cw > sw: cw = sw; ch = cw / ar
    cx = fx * sw; cy = fy * sh + (0.5 - face_top) * ch
    x = min(max(cx - cw / 2, 0), sw - cw); y = min(max(cy - ch / 2, 0), sh - ch)
    return int(cw) // 2 * 2, int(ch) // 2 * 2, int(x), int(y)


def render_base(spec, A, shots, T, out, work):
    W, Hh = A['W'], A['H']
    src = spec.get('src'); scr = spec.get('screen')
    if src: sw, sh, _ = probe(src)
    fx, fy = spec.get('face', (0.5, 0.3))
    parts = []
    for i, s in enumerate(shots):
        n = s['f1'] - s['f0']; p = work / f'shot{i:03d}.mp4'
        if s['mode'] == 'full' or not src:
            run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=0x0B0F1A:s={W}x{Hh}:r={FPS}', '-frames:v', str(n),
                 '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', p])
            parts.append(p); continue
        ss = spec['_src_at'](s['t0'])
        box = (0, 0, W, Hh) if s['mode'] == 'face' else A['faceBox']
        cw, ch, x, y = crop_for(sw, sh, box[2], box[3], s['zoom'], fx, fy, spec.get('face_top', 0.36))
        push = spec.get('push', 0.035)
        d = max(n, 1)
        fc = (f'[0:v]crop={cw}:{ch}:{x}:{y},scale={box[2] * 2}:-2:flags=bicubic,'
              f"zoompan=z='1+{push}*on/{d}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={box[2]}x{box[3]}:fps={FPS},setsar=1[f];"
              f'color=c=0x0B0F1A:s={W}x{Hh}:r={FPS}[bg];[bg][f]overlay={box[0]}:{box[1]}:shortest=1[o]')
        inputs = ['-ss', f'{ss:.3f}', '-i', src]
        if s['mode'] == 'screen' and scr:
            hx, hy, hw, hh = s['hole']; st_ = s['src_t'] if s.get('src_t') is not None else ss + spec.get('screen_offset', 0)
            cw2, ch2, x2, y2 = s['scrop']
            inputs += ['-ss', f'{st_:.3f}', '-i', scr]
            fc = fc.replace('[o]', '[o1]') + f';[1:v]crop={cw2}:{ch2}:{x2}:{y2},scale={hw}:{hh}:flags=lanczos,setsar=1[sc];[o1][sc]overlay={hx}:{hy}:shortest=1[o]'
        if s.get('noface'):
            fc = f'color=c=0x0B0F1A:s={W}x{Hh}:r={FPS}[o1];' + fc.split(';', 3)[3]
        run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-r', str(FPS),
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', p])
        parts.append(p)
    lst = work / 'shots.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out])
    for p in parts: p.unlink()


def render_audio(spec, tl, T, out, beats):
    music = spec.get('music'); mg = spec.get('music_gain', 0.09)
    if tl is None:  # text-only: music only
        run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', music, '-t', f'{T:.3f}', '-af',
             f'afade=t=in:d=0.5,afade=t=out:st={max(0, T - 1.5):.3f}:d=1.5,loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', out]); return
    src = spec['src']; fl = []
    for i, (a, b) in enumerate(tl.keep):
        fl.append(f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[a{i}]')
    fl.append(''.join(f'[a{i}]' for i in range(len(tl.keep))) + f'concat=n={len(tl.keep)}:v=0:a=1,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9[v]')
    inputs = ['-i', src]
    if music:
        inputs += ['-stream_loop', '-1', '-i', music]
        fl.append(f'[v]asplit[v1][v2];[1:a]atrim=0:{T:.3f},volume={mg},afade=t=in:d=1,afade=t=out:st={max(0, T - 2):.3f}:d=2[m];'
                  f'[m][v2]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[v1][md]amix=inputs=2:duration=first:normalize=0[mx]')
        last = '[mx]'
    else: last = '[v]'
    # whoosh on graphic entrances (subtle)
    if spec.get('sfx', True) and beats:
        wsh = str(SFX / 'kit/whoosh.ogg'); k = inputs.count('-i')
        ts = [b['t0'] for b in beats if b['mode'] in ('split', 'full', 'screen')][:40]
        if spec.get('style') == 'motion': ts = ts[::2]
        if ts:
            inputs += ['-i', wsh]
            fl.append(f'[{k}:a]volume={spec.get("sfx_gain", 0.18)},asplit={len(ts)}' + ''.join(f'[w{j}]' for j in range(len(ts))))
            for j, t in enumerate(ts):
                fl.append(f'[w{j}]adelay={int(max(0, t - 0.12) * 1000)}:all=1[wd{j}]')
            fl.append(last + ''.join(f'[wd{j}]' for j in range(len(ts))) + f'amix=inputs={len(ts) + 1}:duration=first:normalize=0[fx]'); last = '[fx]'
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fl), '-map', last, '-t', f'{T:.3f}', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', out])


def make(spec, outdir, work):
    """public entry: resolves keep ranges for base rendering and builds."""
    if spec.get('style') != 'text':
        words, _ = load_words(spec['words'])
        keep = []
        for a, b in spec['keep']:
            a = find(words, a) if isinstance(a, str) else a
            b = find_end(words, b, a) if isinstance(b, str) else b
            keep.append((max(0, a - 0.06), b + 0.12))
        tl = TL(keep)
        def src_at(o):
            for (a, b), off in zip(tl.keep, tl.offs):
                if off - 1e-6 <= o < off + (b - a) - 1e-6: return a + (o - off)
            return tl.keep[-1][1]
        spec['_src_at'] = src_at
    return build(spec, outdir, work)


def sample(mp4, outjpg, n=8):
    """contact sheet of n frames for QA"""
    _, _, d = probe(mp4)
    ts = [d * (i + 0.5) / n for i in range(n)]
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(ts):
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', mp4, '-frames:v', '1', '-vf', 'scale=-2:480', f'{td}/{i:02d}.jpg'])
        run(['ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', f'{td}/*.jpg', '-vf', f'tile={min(n, 8)}x{math.ceil(n / 8)}', '-frames:v', '1', '-q:v', '4', outjpg])
    return outjpg
