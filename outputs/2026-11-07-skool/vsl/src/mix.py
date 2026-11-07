#!/usr/bin/env python3
"""Mix voice + ElevenLabs music + CC0 SFX for one VSL and mux with the silent render.
  python3 mix.py <timing.json> <voice.wav> <music.mp3> <silent.mp4> <out.mp4>
Cues come from <silent>.cues.json (written by render.mjs). Music is end-aligned so the track's own ending lands on
the end card, ducked about 11 dB under the voice. SFX are real recorded CC0 files from the sound-effects skill.
Master: two-pass loudnorm to -14 LUFS, true peak -1.5 dBTP; then the exported MP4 is measured and printed.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np

SR = 48000
SFX = Path(__file__).resolve().parents[4] / '.claude/skills/sound-effects/sfx'
BANK = {   # type -> files (all CC0, bundled with the sound-effects skill)
    'whoosh': ['kit/whoosh.ogg', 'whoosh/fs-683101-quick-woosh.ogg', 'transition/fs-702773-swipe-wav.ogg', 'whoosh/fs-169867-swoosh.ogg'],
    'pop': ['kit/pop.ogg', 'pop/kenney-interface-pluck-001.ogg', 'pop/kenney-interface-pluck-002.ogg', 'pop/fs-824189-pop-in-sfx.ogg'],
    'click': ['kit/click.ogg', 'click/kenney-interface-click-001.ogg', 'click/kenney-interface-select-001.ogg'],
    'tick': ['kit/tick.ogg', 'tick/fs384187.ogg', 'tick/fs528561.ogg'],
    'impact': ['kit/impact.ogg', 'impact/kenney-impact-impactsoft-heavy-000.ogg'],
    'glitch': None, 'typing': None,
}
LEVEL = {'whoosh': -21, 'pop': -19, 'click': -17, 'tick': -19, 'impact': -15, 'glitch': -24, 'typing': -26}
MAXLEN = {'whoosh': 0.7, 'pop': 0.5, 'click': 0.35, 'tick': 0.3, 'impact': 1.4, 'glitch': 0.6, 'typing': 0.12}


def load(path, mono=False):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1' if mono else '2', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    return a if mono else a.reshape(-1, 2)


def db(x): return 10 ** (x / 20)


def rms_db(a): return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)


_cache = {}


def sfx(kind, k):
    files = BANK.get(kind)
    if kind == 'glitch':
        files = sorted(p.relative_to(SFX).as_posix() for p in (SFX / 'glitch').glob('*.ogg'))[:3]
    if kind == 'typing':
        files = BANK['click'][1:] + BANK['tick']
    f = files[k % len(files)]
    if f not in _cache:
        a = load(SFX / f)
        # trim leading silence
        env = np.abs(a).max(1); idx = np.where(env > env.max() * 0.05)[0]
        a = a[idx[0]:] if len(idx) else a
        _cache[f] = a
    a = _cache[f][:int(MAXLEN[kind] * SR)].copy()
    n = min(len(a), int(0.06 * SR)); a[-n:] *= np.linspace(1, 0, n)[:, None]
    a /= (np.abs(a).max() + 1e-9)
    return a * db(LEVEL[kind] + 6)


def main():
    timing, voice, music, silent, out = sys.argv[1:6]
    T = json.load(open(timing)); C = json.load(open(silent.replace('.mp4', '.cues.json')))
    dur = C['duration']; N = int(dur * SR)
    mix = np.zeros((N, 2), np.float32)
    # voice: light high-pass + gentle compression
    vtmp = out + '.voice.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', voice, '-af', 'highpass=f=80,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=90:makeup=2', '-ar', str(SR), '-ac', '1', vtmp], check=True)
    v = load(vtmp, mono=True); Path(vtmp).unlink()
    v = v[:N]; v *= db(-18 - rms_db(v[np.abs(v) > 0.01]) + 0) if len(v) else 1
    mix[:len(v)] += v[:, None]
    # music: end-aligned, ducked under speech
    m = load(music)
    off = max(0, len(m) - N - int(0.4 * SR)) if len(m) > N else 0
    m = m[off:off + N]
    if len(m) < N: m = np.vstack([m, np.zeros((N - len(m), 2), np.float32)])
    m *= db(-18 - rms_db(m))          # music around -18 dB RMS, then ducked
    speak = np.zeros(N, np.float32)
    for w in T['words']:
        a, b = int((w['s'] - 0.05) * SR), int((w['e'] + 0.25) * SR); speak[max(0, a):min(N, b)] = 1
    # smooth envelope (attack 80 ms, release 350 ms) at 100 Hz control rate
    hop = SR // 100; ctl = speak[::hop]; g = np.zeros_like(ctl); cur = 0.0
    for i, x in enumerate(ctl):
        k = 0.12 if x > cur else 0.03; cur += (x - cur) * k; g[i] = cur
    gain_db = -10.5 * np.repeat(g, hop)[:N] - 2.5   # music RMS: ~-31 dB under voice (voice -18), ~-20.5 between lines
    gain_db[int(T['duration'] * SR):] = np.minimum(gain_db[int(T['duration'] * SR):], -4)
    fi = int(0.25 * SR); fo = int(1.2 * SR)
    env = db(gain_db); env[:fi] *= np.linspace(0, 1, fi); env[-fo:] *= np.linspace(1, 0, fo)
    mix += m * env[:, None]
    # SFX: one per cue, de-duplicated
    last = {}; used = []
    for i, c in enumerate(C['cues']):
        kind = c['type']
        if kind not in LEVEL: continue
        if c['t'] - last.get(kind, -9) < (0.35 if kind == 'whoosh' else 0.1): continue
        last[kind] = c['t']
        if kind == 'typing':
            for j in range(10):
                a = sfx('typing', i + j) * 0.5; s0 = int((c['t'] + j * 0.075) * SR)
                if 0 <= s0 < N: mix[s0:s0 + len(a)] += a[:N - s0]
            continue
        a = sfx(kind, i) * c.get('gain', 1)
        s0 = int(c['t'] * SR) - (int(0.05 * SR) if kind == 'whoosh' else 0)
        if 0 <= s0 < N: mix[s0:s0 + len(a)] += a[:N - s0]; used.append(kind)
    wav = out + '.mix.wav'
    import wave
    pk = np.abs(mix).max()
    if pk > 0.98: mix *= 0.98 / pk
    with wave.open(wav, 'wb') as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes())
    # two-pass loudnorm to -14 LUFS / -1.5 dBTP
    o = subprocess.run(['ffmpeg', '-nostats', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    js = json.loads(o[o.rindex('{'):o.rindex('}') + 1])
    ln = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', wav, '-map', '0:v', '-map', '1:a', '-af', ln + ',aresample=48000',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', out], check=True)
    Path(wav).unlink()
    m2 = subprocess.run(['ffmpeg', '-nostats', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', m2)[-1]; TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', m2)[-1]
    print(json.dumps({'out': out, 'lufs': float(I), 'true_peak': float(TP), 'sfx': len(used), 'music_offset_s': round(off / SR, 2)}))


if __name__ == '__main__':
    main()
