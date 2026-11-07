#!/usr/bin/env python3
"""Render one clip from the clip bank in the 7 approved formats (V1–V7, docs/editing-styles.md) — automatically.

Usage:
  python3 tools/formats.py outputs/clip-bank/pod1.json pod1-05 [--formats v1,v2,...] [--keep-frames]
Needs the clip resolved by tools/clip_bank.py (WORK/<id>.words.json + WORK/<id>.voice.wav = ElevenLabs voice).
Steps: 4K frames → speakers (tools/speakers.py: who sits where + who talks when) → a shot plan per format (face framing,
listener cutaways, splits, letterbox, kinetic beats) → motion/templates/vN.html filled with the clip → render (motion-broll
engine) → sound pass (tools/sound_mix.py: voice + music + SFX, -16 LUFS). Output: /home/user/work/formats/<id>/<id>-vN.mp4.
Hooks/titles come from the bank entry (title, hook_q, hook_plain). Check the first few of every new podcast set-up by eye.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / 'motion/templates'; DIST = ROOT / 'motion/dist'; FR_ROOT = Path('/home/user/work/frames'); OUT_ROOT = Path('/home/user/work/formats')
DF_PY = '/home/user/work/dfenv/bin/python'; AUD = Path('/home/user/work/motion/audio')
ENGINE = ROOT / 'vendor/motion-graphics/skills/motion-broll/engine'
NEG = re.compile(r"^(fail\w*|bad|lost|lose|losing|never|hate|hard|scared|afraid|quit|mistakes?|wrong|worst|desperate|impossible|broke|depressed|lonely|stuck|left)$", re.I)
POS = re.compile(r"^(good|win\w*|success\w*|simple|easy|best|love|confidence|growth|grow\w*)$", re.I)
KEY = re.compile(r"^(\d[\d,.%$k]*|one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|million|first|biggest|insane|crazy|"
                 r"secret|money|free|referral\w*|customers?|clients?|agency|ai|automation|banks?|friends?|strangers?|content|years?|months?)$", re.I)
STOP = set('the a an and or but so to of in on at for with is are was were be been i you we they he she it that this my your our me us them his her its as '
           'not no yes just really very like um uh know think going get got have has had do did dont can will would could there what when how who '
           'if then than about from into out up some all more most also too even only much many'.split())
BIGSTOP = STOP | set('want wanted getting gonna going think thinking know really actually maybe little thing things kind sort something because would could should there their theyre these those which where right yeah okay well just like need needs make made said says say look'.split())
MUSIC = {  # format → candidate beds (rotated per clip for variety), dB, duck
    'v1': ([('music-1168.mp3', '"Coffee or Tea" by Michael Ramir C., Mixkit #1168'), ('music-130.mp3', '"Tech House vibes" by Alejandro Magaña (A. M.), Mixkit #130')], -10, 7),
    'v2': ([('cand/m565.mp3', 'Mixkit #565 "Echoes"'), ('cand/m580.mp3', 'Mixkit #580 "Silent Descent"')], -7, 5),
    'v3': ([('music-130.mp3', '"Tech House vibes" by Alejandro Magaña (A. M.), Mixkit #130'), ('music-1168.mp3', '"Coffee or Tea" by Michael Ramir C., Mixkit #1168')], -9, 7),
    'v4': ([('cand/m688.mp3', 'Mixkit #688 "Piano Reflections"'), ('cand/m714.mp3', 'Mixkit #714 "Staring at the Night Sky"')], -11, 8),
    'v5': ([('cand/m714.mp3', 'Mixkit #714 "Staring at the Night Sky"'), ('cand/m688.mp3', 'Mixkit #688 "Piano Reflections"')], -11, 8),
    'v6': ([('cand/m580.mp3', 'Mixkit #580 "Silent Descent"'), ('cand/m565.mp3', 'Mixkit #565 "Echoes"')], -6, 4),
    'v8': ([('music-130.mp3', '"Tech House vibes" by Alejandro Magaña (A. M.), Mixkit #130'), ('music-1168.mp3', '"Coffee or Tea" by Michael Ramir C., Mixkit #1168')], -11, 8),
    'v7': ([('cand/m606.mp3', 'Mixkit #606 "The Long Road"'), ('cand/m688.mp3', 'Mixkit #688 "Piano Reflections"')], -11, 8)}
SUBFRAMES = {'v1': 2, 'v3': 2, 'v5': 2, 'v8': 2}


def run(c, **k):
    return subprocess.run(c, check=True, **k)


def norm(w):
    return re.sub(r"[^a-z0-9'$%]", '', w.lower())


class Frame:  # face framing helpers in source pixels
    def __init__(s, spk):
        s.W, s.H = spk['W'], spk['H']; s.P = {p['id']: p for p in spk['people']}

    def win(s, pid, kind, ratio):
        p = s.P[pid]; f = p['face']
        mult, top = {('tight', 'tall'): (4.2, .33), ('med', 'tall'): (5.6, .33), ('tight', 'band'): (7.0, .42), ('med', 'band'): (9.0, .42),
                     ('med', 'square'): (5.5, .36), ('tight', 'square'): (4.4, .36), ('med', 'half'): (5.2, .40)}[(kind, s.shape(ratio))]
        sw = min(s.W, mult * f); return [round(p['x']), round(p['y'] + (0.5 - top) * sw * ratio), round(sw)]

    def wide(s, ratio=608 / 1080):
        xs = [p['box'][0] for p in s.P.values()] + [p['box'][2] for p in s.P.values()]
        sw = min(s.W, (max(xs) - min(xs)) * 1.08); ys = [p['y'] for p in s.P.values()]
        return [round((max(xs) + min(xs)) / 2), round(sum(ys) / len(ys) + 0.10 * sw * ratio), round(sw)]

    @staticmethod
    def shape(r):
        return 'tall' if r > 1.5 else 'band' if r < 0.7 else 'square' if r > 0.95 else 'half'


def listener_for(segs, P, pid):
    share = {}
    for a, b, l in segs:
        if l != pid: share[l] = share.get(l, 0) + b - a
    if share: return max(share, key=share.get)
    others = [q for q in P if q != pid]
    return min(others, key=lambda q: abs(P[q]['x'] - P[pid]['x'])) if others else None


def shot_list(F, segs, ratio, kinds, sub, cutaway):
    out = []
    for a, b, pid in segs:
        t, i, done = a, 0, False; lis = listener_for(segs, F.P, pid)
        while t < b - 0.3:
            if cutaway and lis is not None and not done and b - a > 6.5 and t - a >= (b - a) * 0.45:
                out.append([round(t, 2)] + F.win(lis, 'med' if F.shape(ratio) != 'band' else 'tight', ratio)); t += 1.1; done = True; continue
            k = kinds[i % len(kinds)]; out.append([round(t, 2)] + (F.wide(ratio) if k == 'wide' else F.win(pid, k, ratio))); t += sub; i += 1
    return out or [[0] + F.wide(ratio)]


def flags(words, title):
    tw = {norm(x) for x in title.split() if norm(x) not in STOP}; out, last = [], -9
    for w, s, e in words:
        n = norm(w); f = 0
        if NEG.match(n): f = 2
        elif KEY.match(n) or (n in tw and len(n) > 3) or POS.match(n): f = 1
        if f and s - last < 1.0 and f == 1: f = 0
        if f: last = s
        out.append([w, s, f])
    return out


def hook_end(words):
    for w, s, e in words:
        if 2.5 <= e <= 4.6 and re.search(r'[.?!]$', w): return round(e + 0.1, 2)
    best = min(words, key=lambda x: abs(x[2] - 3.5)); return round(min(4.6, max(2.5, best[2] + 0.1)), 2)


def two_lines(s, n=18):
    ws = s.split(); best = (99, s, '')
    for i in range(1, len(ws)):
        a, b = ' '.join(ws[:i]), ' '.join(ws[i:]); d = abs(len(a) - len(b))
        if d < best[0]: best = (d, a, b)
    return f"{best[1]}<br>{best[2]}" if len(s) > n and best[2] else s


def beats(W, segs, F):
    COL = ['#FF8A1F', '#2F8CFF', '#43E8FF', '#FFFFFF', '#2BD46B']; out, cur, ci = [], [], 0
    sw = [s[0] for s in segs[1:]]
    def flush(nxt_t):
        nonlocal cur, ci
        if not cur: return
        cand = sorted(cur, key=lambda w: (-(w[2] == 2) * 2 - (w[2] == 1), -len(norm(w[0]))))
        big = next((w for w in cand if norm(w[0]) not in BIGSTOP and len(norm(w[0])) >= 3), next((w for w in cand if norm(w[0]) not in STOP), cand[0]))
        txt = re.sub(r"[.,?!]", '', big[0]); n = len(txt); num = bool(re.match(r'^\d', txt))
        size = 520 if (num and n <= 3) else min(260, int(1000 / (0.62 * max(n, 1))))
        italic = (len(out) % 4 == 3) and not num
        color = '#FF3B30' if big[2] == 2 else '#2BD46B' if POS.match(norm(txt)) else COL[ci % len(COL)]; ci += 1
        bh = f"<i>{txt.lower()}</i>" if italic else txt.upper()
        rest = [re.sub(r"[.,?!]", '', w[0]) for w in cur if w is not big][:3]
        pid = next((l for a, b, l in segs if a <= cur[0][1] < b), segs[0][2])
        shot = F.win(pid, 'tight' if len(out) % 2 else 'med', 1920 / 1080)
        behind = size >= 170 and len(out) % 2 == 1
        items = []
        if rest: items.append([' '.join(rest).lower(), 470 if big is not cur[0] else 900, 84, '#FFFFFF', 0, ''])
        items.append([bh, 640, size, color, 1 if behind else 0, ''])
        out.append([round(cur[0][1], 2), round(nxt_t, 2), shot, items]); cur = []
    for i, w in enumerate(W):
        cur.append(w); nx = W[i + 1] if i + 1 < len(W) else None
        dur = (nx[1] if nx else w[1] + 0.6) - cur[0][1]
        brk = (re.search(r'[.?!,]$', w[0]) and dur > 0.6) or len(cur) >= 4 or dur >= 1.3 or (nx and any(w[1] < t <= nx[1] for t in sw))
        if brk or not nx: flush(nx[1] if nx else w[1] + 0.8)
    for i in range(len(out) - 1): out[i][1] = out[i + 1][0]
    return out


# ---- V8 "Animated" (replaces V3, Nov 7): grammar from the example reels, see outputs/2026-11-07-style/teardown.md
NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
        'fifteen': 15, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'hundred': 100, 'thousand': 1000, 'million': 1000000}
CHIPS = [  # key word -> (chip label, icon) ; icons live in motion/templates/v8.html (IC8)
    (r"^(clients?|customers?|members?|accounts?)$", 'users'), (r"^(money|paid|pay|price\w*|revenue|cash|dollars?|ticket)$", 'dollar'),
    (r"^(hours|months|years|weeks)$", 'clock'), (r"^(automation|automate\w*|ai|agents?|systems?|systemi[sz]e)$", 'bolt'),
    (r"^(content|videos?|posts?|posting|post)$", 'video'), (r"^(banks?)$", 'bank'), (r"^(referrals?|friends?|strangers?|people)$", 'heart'),
    (r"^(tools?|software|apps?|saas)$", 'layers'), (r"^(agency|agencies|business\w*|company)$", 'briefcase'), (r"^(grow\w*|growth|scale\w*)$", 'trend'),
    (r"^(emails?|dms?|messages?)$", 'mail'), (r"^(college|school|learn\w*)$", 'cap')]
BURST = re.compile(r"^(win\w*|success\w*|love|growth|grow\w*|money|paid|free|best|confidence|referral\w*|support\w*|easy|simple)$", re.I)


FILLER = set('hey okay yeah sure fine honestly literally basically opinion general having stuff use now anyways anyway thing things guys individual able kind'.split())


def emph_beats(raw, Wf, emph, Th, T):
    """Clip-bank `emph`: ["lead words|KEY WORDS", ...] picked when the clip is written (LLM or human). KEY must be spoken
    (contiguous); the lead is shown small above it. Numbers become counters; number words become digits."""
    toks = [norm(w) for w, s, e in raw]; out, last = [], -9.0
    p0 = next((k for k, r in enumerate(raw) if r[1] >= Th - 0.3), 0); found = []
    for item in emph:
        lead, key = item.split('|') if '|' in item else ('', item)
        kw = [norm(x) for x in key.split() if norm(x)]
        occ = [k for k in range(p0, len(toks) - len(kw) + 1) if toks[k:k + len(kw)] == kw]
        lw = [norm(x) for x in lead.split() if norm(x)][-2:]
        j = next((k for k in occ if lw and toks[max(0, k - len(lw)):k] == lw), occ[0] if occ else None)
        if j is None: print('emph not found after the hook:', item); continue
        found.append((j, lead, key, kw))
    for j, lead, key, kw in sorted(found):
        ks, ke = raw[j][1], raw[j + len(kw) - 1][2]; lw = [norm(x) for x in lead.split() if norm(x)]
        li = next((k for k in range(max(0, j - len(lw) - 3), j) if lw and toks[k:k + len(lw)] == lw), None)
        b0 = raw[li][1] if li is not None and ks - raw[li][1] < 1.6 else max(0, ks - 0.3)
        if b0 - last < 2.6 or b0 < Th - 0.05: b0 = max(b0, ks - 0.3, last + 2.6, Th - 0.05)
        if b0 > ks + 0.05 or b0 > T - 1.2: continue
        lead = ' '.join(lead.split()[-4:])
        b1 = min(max(ke + 0.8, b0 + 1.3), b0 + 2.4, T - 0.25)
        words = [re.sub(r"[.,?!\"]", '', x) for x in key.split()]; words = [str(NUMW.get(w.lower(), w)) if len(words) > 1 else w for w in words]
        num, tail = None, ''
        m = re.match(r'^\$?(\d[\d,]*)(%?)$', words[0])
        if m and len(words) <= 3 and not any(re.match(r'^\d', w) for w in words[1:]): num = float(m.group(1).replace(',', '')); tail = ' '.join(words[1:]).lower(); words = words[:1]
        elif words[0].lower() in NUMW and len(words) == 1: num = float(NUMW[words[0].lower()]); words = [str(int(num))]
        neg = any(Wf[k][2] == 2 for k in range(j, j + len(kw)))
        out.append(dict(s=round(b0, 2), k=round(ks, 2), e=round(b1, 2), lead=lead.lower(), key=' '.join(words).upper(), tail=tail, num=num if num and num >= 2 else None,
                        col='r' if neg else ('b' if len(out) % 2 else 'y'), _j=j + len(kw) - 1))
        last = b0
    return out


def v8_plan(raw, Wf, segs, F, Th, T, c):
    """Big beats (every ~3.5 s), counters, callout chips, icon bursts, name notes, rack-focus times, one B&W dip."""
    def numval(n):
        m = re.match(r'^\$?(\d[\d,]*\.?\d*)(k|%)?$', n)
        if m: v = float(m.group(1).replace(',', '')); return (v * 1000 if m.group(2) == 'k' else v), ('%' if m.group(2) == '%' else '')
        return (NUMW[n], '') if n in NUMW else (None, '')
    tw = {norm(x) for x in c.get('title', '').split() + c.get('hook_q', '').split()}
    score = []
    for i, (w, s, e) in enumerate(raw):
        n = norm(w); f = Wf[i][2]; v, _ = numval(n)
        if v is not None and n != 'one': score.append(6); continue
        if n in BIGSTOP or n in FILLER or len(n) < 3 or ("'" in n and f != 2): score.append(0); continue
        sc = 1 + (2 if re.search(r'[.?!,]$', w) else 0) + (2 if n in tw else 0) + (2 if f == 1 else 3 if f == 2 else 0) + (1 if len(n) >= 6 else 0)
        score.append(sc)
    beats, i, last = [], 0, -9.0
    if c.get('emph'): beats = emph_beats(raw, Wf, c['emph'], Th, T); i = len(raw)
    starts = [r[1] for r in raw]
    while i < len(raw):
        s = raw[i][1]
        if s < Th + 0.15 or s - last < 3.0 or s > T - 1.6: i += 1; continue
        win = [j for j in range(i, len(raw)) if raw[j][1] <= s + 2.4]
        used = {norm(b['key']) for b in beats}
        j = max(win, key=lambda k: (score[k] * (norm(raw[k][0]) not in used), -raw[k][1]))
        if score[j] < 3: i = win[-1] + 1; continue
        w, ks, ke = raw[j]; n = norm(w); v, suf = numval(n)
        lead = []
        for k in (j - 1, j - 2, j - 3):
            if k < 0 or (beats and k <= beats[-1]['_j']) or ks - raw[k][1] >= 1.1 or re.search(r'[.?!,]$', raw[k][0]) or not norm(raw[k][0]): break
            lead.insert(0, re.sub(r"[.,?!]", '', raw[k][0]).lower())
        tail = ''
        if v is not None and j + 1 < len(raw) and norm(raw[j + 1][0]) not in STOP: tail = re.sub(r"[.,?!]", '', raw[j + 1][0]).lower()
        b0 = raw[j - len(lead)][1] if lead else ks
        b1 = min(max(ke + 0.9, b0 + 1.3), b0 + 2.1, T - 0.3)
        key = re.sub(r"[.,?!\"]", '', w).upper()
        if v is not None: key = ('$' if w.startswith('$') else '') + (f"{int(v):,}" if v == int(v) else str(v)) + suf
        col = 'r' if Wf[j][2] == 2 else ('b' if len(beats) % 2 else 'y')
        beats.append(dict(s=round(b0, 2), k=round(ks, 2), e=round(b1, 2), lead=' '.join(lead), key=key, tail=tail, num=v if v is not None and v >= 2 else None, col=col, _j=j))
        last = b0; i = j + 1
    chips, bursts, busy = [], [], [(b['s'] - 0.3, b['e'] + 0.2) for b in beats]
    free = lambda t, d: t > Th + 0.2 and t + d < T - 0.4 and all(not (a < t + d and t < b) for a, b in busy)
    bk = {norm(x) for b in beats for x in (b['key'] + ' ' + b['tail']).split()}
    for i, (w, s, e) in enumerate(raw):
        n = norm(w)
        if n in bk: continue
        for rx, ic in CHIPS:
            if re.match(rx, n) and free(s, 1.7) and (not chips or s - chips[-1]['t'] > 4.5) and not any(ch['label'].lower() == n for ch in chips):
                lab = re.sub(r"[.,?!]", '', w); lab = lab.upper() if n in ('ai', 'saas', 'dms') else lab[:1].upper() + lab[1:]
                pv = norm(raw[i - 1][0]) if i else ''
                if i and (re.match(r'^\d', pv) or pv in NUMW): lab = f"{NUMW.get(pv, pv)} {lab.lower()}"
                chips.append(dict(t=round(s, 2), e=round(s + 1.7, 2), label=lab, icon=ic, side='l' if len(chips) % 2 else 'r')); busy.append((s, s + 1.7)); break
        if BURST.match(n) and (not bursts or s - bursts[-1]['t'] > 5) and all(abs(s - ch['t']) > 0.8 for ch in chips) and s > Th:
            bursts.append(dict(t=round(s, 2), icon='heart' if n.startswith(('love', 'referral', 'support')) else 'dollar' if n in ('money', 'paid', 'free') else 'star'))
    neg = [b for b in beats if b['col'] == 'r']
    bw = [neg[0]['k'], neg[0]['e']] if neg else None
    # name notes: first time a named speaker talks (solo-speaker clips with a real name only)
    lab = (c.get('speaker') or '').strip(); notes = []
    named = lab and not re.search(r'intern|→|\+|,', lab, re.I)
    if named:
        tot = {}
        for a, b, pid in segs: tot[pid] = tot.get(pid, 0) + b - a
        dom = max(tot, key=tot.get); nm = lab.replace('(', '· ').replace(')', '')
        if nm.lower().startswith('andrew'): nm = 'Andrew George'
        t0 = next(a for a, b, pid in segs if pid == dom)
        nt = max(t0, Th + 0.3)
        for b in sorted(beats, key=lambda b: b['s']):  # never under a big beat
            if b['s'] - 0.2 < nt + 2.0 and nt < b['e'] + 0.2: nt = b['e'] + 0.25
        if nt + 2.0 < T: notes.append(dict(t=round(nt, 2), e=round(nt + 2.0, 2), pid=dom, text=nm))
    for b in beats: b.pop('_j')
    return dict(beats=beats, chips=chips, bursts=bursts, bw=bw, notes=notes, racks=[round(s[0], 2) for s in segs[1:]])


def v8_cues(C):
    """SFX on big moments only (gp: ~1 hit per 5 s): whoosh on punch-ins + rack focus, pop on chips/counters/bursts, one soft impact."""
    P = C['v8']; q = [{'t': 0.05, 'type': 'appear', 'gain': -6}]
    q += [{'t': r, 'type': 'movement', 'gain': -5} for r in P['racks']]
    for i, b in enumerate(P['beats']):
        q.append({'t': b['k'], 'type': 'reveal', 'gain': -6} if (b['num'] or b['col'] == 'r') and i == next((k for k, x in enumerate(P['beats']) if x['num'] or x['col'] == 'r'), -1)
                 else {'t': b['s'], 'type': 'movement', 'gain': -4})
    q += [{'t': ch['t'], 'type': 'appear', 'gain': -4} for ch in P['chips']] + [{'t': x['t'], 'type': 'success', 'gain': -6} for x in P['bursts']]
    q = sorted(q, key=lambda x: x['t']); out = []
    for x in q:  # never two hits within 0.35 s
        if not out or x['t'] - out[-1]['t'] > 0.35: out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('clip')
    ap.add_argument('--formats', default='v1,v2,v4,v5,v6,v7,v8'); ap.add_argument('--keep-frames', action='store_true')
    ap.add_argument('--build-only', action='store_true', help='build motion/dist/<id>-vN.html for a stills check, no render')
    a = ap.parse_args(); S = json.loads(Path(a.spec).read_text()); c = next(x for x in S['clips'] if x['id'] == a.clip)
    idx = [x['id'] for x in S['clips']].index(a.clip); work = Path(S['work']); cid = c['id']; SRC = c.get('src', S['source'])
    words = json.loads((work / f'{cid}.words.json').read_text()); voice = work / f'{cid}.voice.wav'
    fr = FR_ROOT / cid; out = OUT_ROOT / cid; fr.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    link = ROOT / 'motion/frames'
    if not link.exists():
        try: link.symlink_to(FR_ROOT)
        except FileExistsError: pass  # the other render lane created it first
    nf = int(c['dur'] * 30)
    if len(list(fr.glob('f*.jpg'))) < nf - 2:
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(c['t0']), '-t', str(c['dur']), '-i', SRC, '-vf', 'fps=30', '-q:v', '4', '-start_number', '0', str(fr / 'f%04d.jpg')])
    nf = len(list(fr.glob('f*.jpg')))
    spk_p = out / 'speakers.json'
    if not spk_p.exists():
        run([DF_PY, str(ROOT / 'tools/speakers.py'), SRC, str(spk_p), '--start', str(c['t0']), '--dur', str(c['dur']), '--words', str(work / f'{cid}.words.json')], capture_output=True)
    spk = json.loads(spk_p.read_text())
    sys.path.insert(0, str(ROOT / 'tools')); from speakers_guard import check_label
    spk, swapped = check_label(spk, c.get('speaker', ''))
    if swapped: print('speaker map swapped to match the clip bank label:', c.get('speaker'))
    F = Frame(spk); segs = spk['segments']
    W = flags(words, c.get('title', '')); Th = hook_end(words); T = round(c['dur'], 2)
    tall, band = 1920 / 1080, 608 / 1080
    first = segs[0][2]; other = listener_for(segs, F.P, first)
    keys = []
    for a_, b_, pid in segs:
        keys.append([a_] + F.win(pid, 'med', tall))
        if b_ - a_ > 5: keys.append([round(a_ + (b_ - a_) / 2, 2)] + F.win(pid, 'tight', tall))
    Tb = round(min(T - 3.5, Th + 4.7), 2) if T > Th + 6 else round(Th + (T - Th) / 2, 2)
    B = beats(W, segs, F); whips = sorted({round(s[0], 2) for s in segs[1:]} | {b[0] for i, b in enumerate(B) if i and i % 5 == 0})
    flashes = sorted({round(s[0], 2) for s in segs[1:]} | {next((b[0] for b in B if any(it[3] == '#FF3B30' for it in b[3])), 0)} - {0})
    fmts = a.formats.split(',')
    cut = []
    if 'v3' in fmts:
        for b in B:
            if any(it[4] for it in b[3]): cut += [n for n in range(int(b[0] * 30) - 2, int(b[1] * 30) + 3) if 0 <= n < nf and n % 2 == 0]
        cut = sorted(set(cut))
        if cut: run([DF_PY, str(ROOT / 'tools/cutouts.py'), str(fr), ','.join(map(str, cut))], capture_output=True)
    brand = c.get('brand', 'HIGHLEVEL'); sub = c.get('brand_sub', 'Podcast')
    CLIP = dict(id=cid, T=T, FR=30, NF=nf, IW=spk['W'], IH=spk['H'], W=W, people=spk['people'], segs=segs, Th=Th, Tb=Tb,
                title=(c.get('title', '') + '\n').split('\n')[:2], hook_q=c.get('hook_q', ''), hook_plain=c.get('hook_plain', ''),
                hook_q_html=two_lines(c.get('hook_q', '')), hook_plain_html=two_lines(c.get('hook_plain', '')), brand=brand, brand_sub=sub,
                wide=F.wide(band), leak=round(segs[1][0] if len(segs) > 1 else min(T / 3, 7.4), 2),
                shots=dict(v2=shot_list(F, segs, band, ['wide', 'tight'], 3.8, True), v4=shot_list(F, segs, tall, ['med', 'tight'], 3.2, True),
                           v5=shot_list(F, segs, tall, ['med', 'tight'], 3.2, True), v6=shot_list(F, segs, 1060 / 1080, ['med'], 99, False),
                           v7=shot_list(F, segs, tall, ['tight', 'med'], 2.8, True)),
                split=dict(top=F.win(first, 'med', 960 / 1080), bot=F.win(other if other is not None else first, 'med', 960 / 1080)),
                keys=dict(v1=keys), beats=B, v8=v8_plan(words, W, segs, F, Th, T, c) if 'v8' in fmts else None,
                v8shots=[[a_] + F.win(pid, 'med', tall) for a_, b_, pid in segs], whips=whips, flashes=flashes, cutFrames=cut)
    (out / 'clip.json').write_text(json.dumps(CLIP))
    lib = (TPL / 'lib.js').read_text()
    for f in fmts:
        if not a.build_only and (out / f'{cid}-{f}.mp4').exists() and (out / f'{cid}-{f}.mp4.sound.md').exists(): print(f, 'done already'); continue  # resume after a stop
        frag = (TPL / f'{f}.html').read_text().replace('/*CLIP*/null', json.dumps(CLIP)).replace('//@include lib.js', lib)
        if f != 'v3': frag = frag.replace('"cutFrames": [', '"cutFrames_unused": [')
        tmp = out / f'{cid}-{f}.html'; tmp.write_text(frag)
        run([sys.executable, str(ENGINE / 'build.py'), str(DIST), str(tmp)], capture_output=True)
        if a.build_only: print('built', DIST / tmp.name); continue
        silent = out / f'{cid}-{f}_silent.mp4'
        env = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules', MB_SUBFRAMES=str(SUBFRAMES.get(f, 1)))
        r = subprocess.run(['node', str(ENGINE / 'render.js'), str(DIST / tmp.name), str(silent), '30'], env=env, capture_output=True, text=True)
        if r.returncode: print(f, 'RENDER FAILED', r.stderr[-400:]); continue
        cues = {'v1': [{'t': 0.0, 'type': 'appear'}] + [{'t': k[0], 'type': 'movement'} for k in keys[1:]] + [{'t': Th, 'type': 'scene_cut'}, {'t': Tb, 'type': 'scene_cut'}],
                'v2': [{'t': CLIP['leak'], 'type': 'movement', 'gain': -6}], 'v4': [{'t': Th, 'type': 'appear', 'gain': -4}], 'v7': [{'t': Th, 'type': 'appear', 'gain': -4}],
                'v5': [{'t': Th, 'type': 'movement'}], 'v6': [],
                'v8': v8_cues(CLIP) if f == 'v8' else [],
                'v3': [{'t': 0.0, 'type': 'reveal', 'gain': -4}] + [{'t': w, 'type': 'scene_cut'} for w in whips] + [{'t': x, 'type': 'reveal', 'gain': -4} for x in flashes if x not in whips]
                      + [{'t': b[0], 'type': 'appear'} for i, b in enumerate(B) if i % 3 == 1][:8]}[f]
        cues = sorted([q for q in cues if q['t'] < T - 0.3], key=lambda q: q['t'])
        (out / f'{f}.cues.json').write_text(json.dumps(cues)); (out / 'voice.json').write_text(json.dumps({'source': str(voice), 'ranges': [[0, T]]}))
        beds, db, duck = MUSIC[f]; mfile, msrc = beds[idx % len(beds)]
        r = subprocess.run([sys.executable, str(ROOT / 'tools/sound_mix.py'), '--video', str(silent), '--voice', str(out / 'voice.json'), '--cues', str(out / f'{f}.cues.json'),
                            '--music', str(AUD / mfile), '--music-db', str(db), '--duck-db', str(duck), '--music-source', msrc,
                            '--music-license', 'Mixkit Free License (not re-confirmed)', '--out', str(out / f'{cid}-{f}.mp4')], capture_output=True, text=True)
        print(f, (r.stdout.strip().splitlines() or ['?'])[-1][:110] if r.returncode == 0 else 'MIX FAILED ' + r.stderr[-300:])
    if not a.keep_frames: shutil.rmtree(fr, ignore_errors=True)


if __name__ == '__main__':
    main()
