#!/usr/bin/env python3
"""VSL editor: one talking-head source -> many cuts (clean edit, hook variants, short ad cut, 9:16 / 4:5, no-face motion).

Library used by tools/vsl/specs_*.py. Pipeline per output:
  1. shots (source ranges + framing preset) -> base video (ffmpeg crop/scale per shot from the 4K source, concat)
  2. voice = same ranges cut from the source audio (8 ms fades), cleaned, loudness-normalised; optional music bed
     ducked under the voice + subtle SFX on card entrances; final two-pass loudnorm to -14 LUFS / -1.5 dBTP
  3. overlay (captions, hook box, lower third, motion-graphic cards) = tools/vsl/overlay.html rendered frame by frame in
     Chromium (tools/vsl/frames.js) and composited over the base video. Motion/text-only modes render the page opaque.
Brand: navy #0B0F1A, yellow #FFD23F, blue #2E7DFF, Inter Tight ExtraBold + Instrument Serif italic accents.
"""
import json, os, re, subprocess, shutil, tempfile
from pathlib import Path
import numpy as np, soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
VSL = Path(__file__).resolve().parent
FPS = 30
SR = 48000
SFX = ROOT / 'vendor/motion-graphics/skills/sound-effects/sfx/kit'

# ---------------------------------------------------------------- framing
FACE = (0.49, 0.315)   # Andrew's face centre in the VSL frames (normalised), same set-up for VIDEO 1-4
PRESETS = {
    # name: (zoom, face_x_out, face_y_out)
    'W': (1.0, 0.5, 0.36), 'T': (1.3, 0.5, 0.36), 'C': (1.72, 0.5, 0.40), 'R': (1.5, 0.70, 0.38),
}
VPRE = {'W': (1.0, 0.5, 0.30), 'T': (1.2, 0.5, 0.33), 'C': (1.5, 0.5, 0.36)}
SPLIT = {'9x16': 0.5, '4x5': 0.46}
DIMS = {'16x9': (1920, 1080), '9x16': (1080, 1920), '4x5': (1080, 1350)}


def crop_for(aspect, f, W0=3840, H0=2160, face=FACE):
    W, H = DIMS[aspect]
    place = (0, 0, W, H)
    if f == 'B':  # bottom box for split layouts (card on top)
        sp = SPLIT[aspect]; py0 = round(H * sp); place = (0, py0, W, H - py0)
        A = W / (H - py0); z, fx, fy = (1.45 if aspect == '9x16' else 1.25), 0.5, 0.42
    else:
        A = W / H
        z, fx, fy = (PRESETS if aspect == '16x9' else VPRE)[f]
    if A < W0 / H0: ch, cw = H0, H0 * A
    else: cw, ch = W0, W0 / A
    cw, ch = cw / z, ch / z
    cx = min(max(face[0] * W0 - fx * cw, 0), W0 - cw)
    cy = min(max(face[1] * H0 - fy * ch, 0), H0 - ch)
    ev = lambda v: int(round(v / 2) * 2)
    return (ev(cw), ev(ch), ev(cx), ev(cy)), place


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(' '.join(map(str, cmd))[:400] + '\n' + r.stderr[-2000:])
    return r


# ---------------------------------------------------------------- words
FIX_SEQ = [  # (lowercased token sequence, replacement)
    (['chat', 'gpt'], 'ChatGPT'), (['go', 'high', 'level'], 'GoHighLevel'), (['base', '44'], 'Base44'),
    (['ai', 'studio'], 'AI Studio'), (['all', 'in'], 'All-In'), (['an', 'edit'], 'and edit'),
    (['a', 'dump', 'for', 'your'], 'a done-for-you'), (['voice', 'in'], 'voice and'), (['sub', 'accounts'], 'sub-accounts'),
]
FIX_WORD = {'chatgbt': 'ChatGPT', 'loveable': 'Lovable', 'top': None, 'nvidia\'s': "NVIDIA's", 'gonna': 'gonna'}


def load_words(tjson):
    d = json.load(open(tjson))
    ws = [dict(w=w['w'], s=w['s'], e=w['e']) for s in d['segments'] for w in s['words']]
    out, i = [], 0
    norm = lambda x: re.sub(r'[^a-z0-9\']', '', x.lower())
    while i < len(ws):
        hit = None
        for seq, rep in FIX_SEQ:
            n = len(seq)
            if [norm(x['w']) for x in ws[i:i + n]] == seq:
                tail = re.sub(r'^.*?([.,?!;:]*)$', r'\1', ws[i + n - 1]['w'])
                hit = (n, dict(w=rep + tail, s=ws[i]['s'], e=ws[i + n - 1]['e'])); break
        if hit:
            out.append(hit[1]); i += hit[0]; continue
        w = dict(ws[i]); k = norm(w['w'])
        if k in FIX_WORD and FIX_WORD[k]:
            tail = re.sub(r'^.*?([.,?!;:]*)$', r'\1', w['w']); w['w'] = FIX_WORD[k] + tail
        if k == 'top' and i + 1 < len(ws) and norm(ws[i + 1]['w']) == 'the':
            w['w'] = 'Tap'
        out.append(w); i += 1
    return out


def tighten(words, a, b, gap=0.42, keep=0.16):
    """Split source range [a,b] at pauses longer than `gap` (keeps `keep` s of each pause)."""
    inside = [w for w in words if w['s'] >= a - 0.01 and w['e'] <= b + 0.05]
    if not inside: return [[a, b]]
    rs, cur = [], [a, None]
    for x, y in zip(inside, inside[1:]):
        if y['s'] - x['e'] > gap:
            cur[1] = x['e'] + keep / 2; rs.append(cur); cur = [y['s'] - keep / 2, None]
    cur[1] = b; rs.append(cur)
    return rs


def q(t): return round(t * FPS) / FPS


# ---------------------------------------------------------------- timeline builder
class Cut:
    """Ordered list of source ranges -> output timeline, words, framing."""

    def __init__(self, words, ranges, do_tighten=True):
        self.words = words
        rr = []
        for a, b in ranges:
            rr += tighten(words, a, b) if do_tighten else [[a, b]]
        self.segs = []  # (src_in, src_out, out_start)
        t = 0.0
        for a, b in rr:
            a, b = q(a), q(b)
            if b - a < 1 / FPS: continue
            self.segs.append((a, b, t)); t = q(t + b - a)
        self.dur = t

    def to_out(self, s, which='last'):
        hits = [o + (s - a) for a, b, o in self.segs if a - 0.02 <= s <= b + 0.02]
        if not hits: return None
        return hits[-1] if which == 'last' else hits[0]

    def out_words(self, accent=()):
        out = []
        for a, b, o in self.segs:
            for w in self.words:
                mid = (w['s'] + w['e']) / 2
                if a <= mid < b:
                    k = re.sub(r'[^a-z0-9$]', '', w['w'].lower())
                    out.append(dict(w=w['w'], s=round(o + max(w['s'], a) - a, 3), e=round(o + min(w['e'], b) - a, 3),
                                    acc=1 if k in accent else 0))
        return out

    def shots(self, pattern=('W', 'T', 'W', 'C', 'T', 'W'), overrides=(), min_len=1.0, every=None):
        """Framing per output time. pattern cycles at each segment boundary (and every `every` s inside long segments).
        overrides: [(t0, t1, preset)] in output time (cards with half layouts)."""
        bounds = []
        for a, b, o in self.segs:
            bounds.append(o)
            if every:
                n = int((b - a) // every)
                for k in range(1, n):
                    if (b - a) - k * every > min_len: bounds.append(q(o + k * every))
        bounds = sorted(set(bounds))
        fr, k = [], 0
        for i, s in enumerate(bounds):
            e = bounds[i + 1] if i + 1 < len(bounds) else self.dur
            if fr and e - s < min_len and fr[-1][1] == s:
                fr[-1][1] = e; continue
            fr.append([s, e, pattern[k % len(pattern)]]); k += 1
        # apply overrides
        for t0, t1, p in overrides:
            t0, t1 = q(t0), q(t1); nf = []
            for s, e, f in fr:
                if e <= t0 or s >= t1: nf.append([s, e, f]); continue
                if s < t0: nf.append([s, t0, f])
                nf.append([max(s, t0), min(e, t1), p])
                if e > t1: nf.append([t1, e, f])
            fr = nf
        # merge equal neighbours, then cut by segment boundaries -> shot list with source in
        mf = []
        for s, e, f in fr:
            if mf and mf[-1][2] == f and abs(mf[-1][1] - s) < 1e-6: mf[-1][1] = e
            else: mf.append([s, e, f])
        shots = []
        for a, b, o in self.segs:
            oe = q(o + b - a)
            for s, e, f in mf:
                s2, e2 = max(s, o), min(e, oe)
                if e2 - s2 >= 0.5 / FPS:
                    shots.append(dict(src=q(a + s2 - o), out=q(s2), dur=q(e2 - s2), f=f))
        return shots


# ---------------------------------------------------------------- render steps
def base_video(src, aspect, shots, out, tmp):
    W, H = DIMS[aspect]
    parts = []
    for i, sh in enumerate(shots):
        (cw, ch, cx, cy), (px, py, pw, ph) = crop_for(aspect, sh['f'])
        n = round(sh['dur'] * FPS)
        if n <= 0: continue
        p = Path(tmp) / f'shot{i:03d}.mp4'
        vf = f'crop={cw}:{ch}:{cx}:{cy},scale={pw}:{ph}:flags=lanczos,setsar=1'
        if (pw, ph) != (W, H): vf += f',pad={W}:{H}:{px}:{py}:color=0x0B0F1A'
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{sh["src"]:.4f}', '-i', src, '-frames:v', str(n), '-vf', vf, '-an',
             '-r', str(FPS), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', str(p)])
        parts.append(p)
    lst = Path(tmp) / 'shots.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', out])


_wav_cache = {}


def src_wav(src, tmp):
    if src not in _wav_cache:
        w = Path(tmp).parent / (Path(src).stem + '.48k.wav')
        if not w.exists():
            run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '2', '-ar', str(SR), str(w)])
        _wav_cache[src] = str(w)
    return _wav_cache[src]


def loudnorm(inp, out, I=-14, TP=-1.5, extra=''):
    m = run(['ffmpeg', '-hide_banner', '-i', inp, '-af', f'{extra}loudnorm=I={I}:TP={TP}:LRA=11:print_format=json', '-f', 'null', '-']).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    af = (f"{extra}loudnorm=I={I}:TP={TP}:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    run(['ffmpeg', '-v', 'error', '-y', '-i', inp, '-af', af, '-ar', str(SR), out])


def read_any(path):
    t = tempfile.mktemp(suffix='.wav')
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(path), '-ac', '2', '-ar', str(SR), t])
    a, _ = sf.read(t, dtype='float32'); os.remove(t)
    return a if a.ndim == 2 else np.stack([a, a], 1)


def build_audio(cut, src, out, tmp, music=None, sfx=(), voice=True, dur=None):
    """cut: Cut or None. music: dict(file, db, start). sfx: [(t, name, db)]."""
    total = dur if dur else cut.dur
    N = int(round(total * SR))
    mix = np.zeros((N, 2), np.float32)
    v = np.zeros((N, 2), np.float32)
    if voice and cut is not None:
        a, _ = sf.read(src_wav(src, tmp), dtype='float32')
        fade = int(0.008 * SR)
        for s0, s1, o in cut.segs:
            i0, i1, j0 = int(round(s0 * SR)), int(round(s1 * SR)), int(round(o * SR))
            seg = a[i0:i1].copy(); n = min(len(seg), N - j0)
            seg = seg[:n]
            if n > 2 * fade:
                r = np.linspace(0, 1, fade, dtype=np.float32)[:, None]; seg[:fade] *= r; seg[-fade:] *= r[::-1]
            v[j0:j0 + n] += seg
        raw = Path(tmp) / 'voice_raw.wav'; sf.write(raw, v, SR)
        cl = Path(tmp) / 'voice.wav'
        loudnorm(str(raw), str(cl), I=-16, TP=-2, extra='highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,')
        v, _ = sf.read(cl, dtype='float32'); v = v[:N] if len(v) >= N else np.pad(v, ((0, N - len(v)), (0, 0)))
        mix += v
    if music:
        m = read_any(music['file'])
        st = int(music.get('start', 0) * SR); m = m[st:st + N]
        if len(m) < N: m = np.pad(m, ((0, N - len(m)), (0, 0)))
        g = 10 ** (music.get('db', -20) / 20)
        m = m / (np.sqrt(np.mean(m ** 2)) + 1e-9) * 0.1  # normalise to ~-20 dBFS rms before gain
        env = np.ones(N, np.float32)
        if voice and cut is not None:
            hop = int(0.05 * SR); rms = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, N, hop)])
            act = (rms > 0.01).astype(np.float32)
            duck = 10 ** (music.get('duck', -9) / 20); tgt = 1 - (1 - duck) * act
            sm = np.copy(tgt)
            for i in range(1, len(sm)):
                k = 0.5 if tgt[i] < sm[i - 1] else 0.12
                sm[i] = sm[i - 1] + (tgt[i] - sm[i - 1]) * k
            env = np.repeat(sm, hop)[:N]
        fo = int(1.5 * SR); fi = int(0.05 * SR)
        env[:fi] *= np.linspace(0, 1, fi); env[-fo:] *= np.linspace(1, 0, fo)
        mix += m * g * env[:, None]
    for t, name, db in sfx:
        p = SFX / f'{name}.ogg'
        if not p.exists(): continue
        s = read_any(p) * (10 ** (db / 20)); j = int(round(t * SR))
        if j >= N: continue
        if j < 0: s = s[-j:]; j = 0
        n = min(len(s), N - j); mix[j:j + n] += s[:n]
    pre = Path(tmp) / 'mix_pre.wav'; sf.write(pre, mix, SR)
    loudnorm(str(pre), out, I=-14, TP=-1.5)


def render(plan, out, src=None, cut=None, aspect='16x9', shots=None, music=None, sfx=(), mode='overlay', keep=None, workers=3):
    """plan: overlay plan dict (events, words...). mode overlay -> needs src/cut/shots. motion|text -> opaque page."""
    W, H = DIMS[aspect]
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='vsl_', dir=str(out.parent)))
    try:
        dur = cut.dur if cut is not None else plan['dur']
        plan = dict(plan, W=W, H=H, dur=dur, mode=mode if mode != 'text' else 'motion')
        html = (VSL / 'overlay.html').read_text().replace('__FONTS__', 'file://' + str(ROOT / 'tools/fonts')).replace('__PLAN__', json.dumps(plan))
        page = tmp / 'page.html'; page.write_text(html)
        wav = tmp / 'mix.wav'
        build_audio(cut, src, str(wav), tmp, music=music, sfx=sfx, voice=(mode != 'text'), dur=dur)
        base = None
        if mode == 'overlay':
            base = tmp / 'base.mp4'; base_video(src, aspect, shots, str(base), tmp)
        N = round(dur * FPS)
        # split frames into chunks rendered in parallel, each composited to its own segment, then concat
        k = max(1, min(workers, N // 150))
        bounds = [round(N * i / k) for i in range(k + 1)]
        procs = []
        for i in range(k):
            f0, f1 = bounds[i], bounds[i + 1]
            seg = tmp / f'part{i}.mp4'
            node = ['node', str(VSL / 'frames.js'), str(page), str(W), str(H), str(FPS), f'{dur:.4f}', '1' if mode == 'overlay' else '0', str(f0), str(f1)]
            enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p']
            if mode == 'overlay':
                ff = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{f0 / FPS:.4f}', '-i', str(base), '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
                      '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto:shortest=1[v]', '-map', '[v]', '-frames:v', str(f1 - f0), *enc, str(seg)]
            else:
                ff = ['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-', '-frames:v', str(f1 - f0), *enc, str(seg)]
            pn = subprocess.Popen(node, stdout=subprocess.PIPE, stderr=open(tmp / f'node{i}.log', 'w'), env=dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '')))
            pf = subprocess.Popen(ff, stdin=pn.stdout, stderr=open(tmp / f'ff{i}.log', 'w'))
            pn.stdout.close(); procs.append((pn, pf, i))
        for pn, pf, i in procs:
            pf.wait(); pn.wait()
            if pn.returncode or pf.returncode:
                raise RuntimeError(f'chunk {i} failed: node {pn.returncode} ff {pf.returncode}\n' + (tmp / f'node{i}.log').read_text()[-1500:] + (tmp / f'ff{i}.log').read_text()[-1500:])
        lst = tmp / 'parts.txt'; lst.write_text(''.join(f"file '{tmp}/part{i}.mp4'\n" for i in range(k)))
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(wav), '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-r', str(FPS),
             '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', str(out)])
        if keep: shutil.copy(page, keep)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def contact(video, out, n=12, cols=4, width=360):
    d = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)]).stdout)
    rows = (n + cols - 1) // cols
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-vf', f'fps={n / d:.5f},scale={width}:-2,tile={cols}x{rows}', '-frames:v', '1', '-q:v', '4', str(out)])
    return d
