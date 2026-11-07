#!/usr/bin/env python3
"""Stitch paragraph mp3s into one voice track + word timing.
  python3 stitch.py <voice_dir> <out.wav> <timing.json> [--lead 0.6] [--gap 0.30]
- trims each paragraph to its speech (alignment + energy), evens loudness to -18 LUFS per paragraph,
- shortens any pause inside a paragraph longer than 0.6 s down to 0.45 s,
- joins paragraphs with a short gap, starting after `lead` seconds.
timing.json: {duration, words:[{w, s, e, p}], paras:[{s, e, text}]}
"""
import argparse, json, subprocess
from pathlib import Path
import numpy as np
import pyloudnorm as pyln

SR = 44100


def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def words_from(al):
    ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    out, cur = [], None
    for c, s, e in zip(ch, st, en):
        if c.isspace():
            if cur: out.append(cur); cur = None
            continue
        if cur is None: cur = {'w': c, 's': s, 'e': e}
        else: cur['w'] += c; cur['e'] = e
    if cur: out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('out'); ap.add_argument('timing')
    ap.add_argument('--lead', type=float, default=0.6); ap.add_argument('--gap', type=float, default=0.30)
    a = ap.parse_args()
    meter = pyln.Meter(SR)
    track = [np.zeros(int(a.lead * SR), np.float32)]; t = a.lead
    words, paras = [], []
    files = sorted(Path(a.dir).glob('p*.mp3'))
    for i, f in enumerate(files):
        meta = json.load(open(f.with_suffix('.json')))
        x = load(f)
        ws = words_from(meta['alignment'])
        # display words come from the written text (same count unless SAY changed tokens)
        disp = meta['text'].split()
        if len(disp) == len(ws):
            for w, d in zip(ws, disp): w['w'] = d
        # speech window: alignment start, energy-based end
        a0 = max(0.0, ws[0]['s'] - 0.04)
        env = np.convolve(np.abs(x), np.ones(441) / 441, 'same')
        thr = 0.012 * env.max()
        idx = np.where(env > thr)[0]
        a1 = min(len(x) / SR, max(ws[-1]['e'] + 0.05, (idx[-1] / SR if len(idx) else ws[-1]['e']) + 0.04))
        # keep-segments, shrinking long pauses
        keeps, cur = [], a0
        for j in range(len(ws) - 1):
            g0, g1 = ws[j]['e'], ws[j + 1]['s']
            if g1 - g0 > 0.6:
                keeps.append((cur, g0 + 0.22)); cur = g1 - 0.23
        keeps.append((cur, a1))
        # time map src->dst
        def remap(ts):
            acc = 0.0
            for k0, k1 in keeps:
                if ts <= k1: return acc + max(0.0, ts - k0)
                acc += k1 - k0
            return acc
        pieces = []
        for k0, k1 in keeps:
            seg = x[int(k0 * SR):int(k1 * SR)].copy()
            fade = min(len(seg) // 2, int(0.008 * SR))
            if fade > 0:
                seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
            pieces.append(seg)
        y = np.concatenate(pieces)
        loud = meter.integrated_loudness(y.astype(np.float64)) if len(y) > SR * 0.5 else -20
        y = y * (10 ** ((-18 - loud) / 20))
        for w in ws:
            words.append({'w': w['w'], 's': round(t + remap(w['s']), 3), 'e': round(t + remap(w['e']), 3), 'p': i})
        paras.append({'s': round(t, 3), 'e': round(t + len(y) / SR, 3), 'text': meta['text']})
        track.append(y.astype(np.float32)); t += len(y) / SR
        gap = a.gap if i < len(files) - 1 else 0.0
        track.append(np.zeros(int(gap * SR), np.float32)); t += gap
    out = np.concatenate(track)
    peak = np.abs(out).max()
    if peak > 0.95: out *= 0.95 / peak
    import wave
    with wave.open(a.out, 'wb') as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
    json.dump({'duration': round(t, 3), 'words': words, 'paras': paras}, open(a.timing, 'w'))
    print(Path(a.dir).name, 'duration', round(t, 2), 'words', len(words))


if __name__ == '__main__':
    main()
