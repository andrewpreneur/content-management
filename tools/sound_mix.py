#!/usr/bin/env python3
"""Sound pass for talking-head + motion-graphics reels: voice + SFX + music, measured.

Follows vendor/motion-graphics/skills/sound-effects (Vox's sound-pass method, credit @Voxyz_ai): real recorded SFX
from the bundled CC0 kit (never synthesised), one sound per cue, whooshes 2 frames early, risers END on the hit,
music beat-aligned to the hard cuts, priority voice > SFX > music, music ducked under the voice, and loudness
measured on the EXPORTED MP4 (target -16 LUFS integrated, true peak below -4 dBFS). Unlike the skill's script this one
keeps the speaker's voice.

Usage:
  python3 tools/sound_mix.py --video silent.mp4 --voice voice_ranges.json --cues cues.json --music track.mp3 \
      --out out.mp4 [--music-db -12] [--music-source "..."] [--music-license "..."]
voice_ranges.json: {"source": "/path/camera.mp4", "ranges": [[a0, a1], ...]}  (concatenated in order, from t=0)
cues.json: [{"t": 2.68, "type": "reveal", "desc": "..."}, {"t": 8.9, "type": "build_up", "dur": 1.17}, ...]
Writes OUT, OUT.sound.md (cue table, beat errors, LUFS/peak, 5 timestamps to check by ear) and OUT.credits.txt.
"""
import argparse, json, os, random, subprocess, tempfile
from pathlib import Path
import numpy as np, librosa, soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SFX = ROOT / 'vendor/motion-graphics/skills/sound-effects/sfx'
SR = 48000


def run(c):
    return subprocess.run(c, capture_output=True, text=True)


def load(p, mono=False):
    a, _ = librosa.load(str(p), sr=SR, mono=mono)
    a = np.atleast_2d(a)
    if a.shape[0] == 1:
        a = np.vstack([a, a])
    return a.T


def measure(path):
    o = run(['ffmpeg', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
    import re
    tail = o[o.rfind('Summary:'):]
    def grab(key):
        m = re.search(rf'^\s*{key}:\s*(-?[\d.]+|-inf)', tail, re.M)
        return float(m.group(1)) if m and m.group(1) != '-inf' else None
    return grab('I'), grab('Peak')


def main():
    ap = argparse.ArgumentParser()
    for k in ('video', 'voice', 'cues', 'music', 'out'):
        ap.add_argument('--' + k, required=True)
    ap.add_argument('--music-db', type=float, default=-12.0)
    ap.add_argument('--music-source', default=None); ap.add_argument('--music-license', default=None)
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args(); random.seed(a.seed)
    man = json.loads((SFX / 'manifest.json').read_text())
    kit = {e['category']: e for e in man['default_kit']}
    lib = {}
    for e in man.get('bundled', []):
        lib.setdefault(e['category'], []).append(e)
    cmap = man['category_map']
    dur = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.video]).stdout)
    fps = eval(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', a.video]).stdout.strip())
    n = int(dur * SR) + SR

    # ---- voice: concatenate ranges with 15 ms fades (no clicks at the jump cuts)
    vr = json.loads(Path(a.voice).read_text())
    voice = np.zeros((n, 2), np.float32); pos = 0
    with tempfile.TemporaryDirectory() as td:
        for i, (a0, a1) in enumerate(vr['ranges']):
            w = os.path.join(td, f'v{i}.wav')
            run(['ffmpeg', '-y', '-v', 'error', '-ss', str(a0), '-t', str(a1 - a0), '-i', vr['source'], '-vn', '-ac', '2', '-ar', str(SR), w])
            seg = sf.read(w, dtype='float32')[0]
            f = int(0.015 * SR); seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]
            m = min(len(seg), n - pos); voice[pos:pos + m] += seg[:m]; pos += m
    # voice level: bring speech to about -18 LUFS-ish RMS before mixing (final loudnorm happens on export)
    rms = np.sqrt(np.mean(voice[:pos] ** 2)) + 1e-9; voice *= 0.1 / rms

    # ---- SFX: one real sound per cue (kit first, vary takes within a category)
    cues = json.loads(Path(a.cues).read_text())
    sfx = np.zeros((n, 2), np.float32); placed = []; used = {}
    for i, c in enumerate(cues):
        cat = cmap[c['type']]
        pool = [kit[cat]] if cat in kit and kit[cat].get('file') else []
        pool += [e for e in lib.get(cat, []) if e.get('license', '').startswith('CC0')]
        k = used.get(cat, 0); e = pool[k % len(pool)] if c['type'] in ('appear', 'hover_or_small_ui', 'click') else pool[0]
        used[cat] = k + 1
        snd = load(SFX / e['file'])
        gain, pre = 0.0, 0.0
        if c['type'] in ('movement', 'scene_cut'):
            pre, gain = 2 / fps, -4
        if c['type'] in ('appear', 'click', 'hover_or_small_ui'):
            gain = -8 if c['type'] == 'hover_or_small_ui' else -6
        start = c['t'] - pre
        if c['type'] == 'build_up':
            need = int(c.get('dur', 0.8) * SR); snd = snd[-need:] if len(snd) > need else snd; gain = -6
            start = c['t'] + c.get('dur', 0.8) - len(snd) / SR
        gain += c.get('gain', 0)
        i0 = max(0, int(start * SR)); s = snd * 10 ** (gain / 20); m = min(len(s), n - i0); sfx[i0:i0 + m] += s[:m]
        placed.append(dict(c, category=cat, file=e['file'], source_url=e.get('source_url'), license=e.get('license'), credit=e.get('attribution') or e.get('credit'), start=round(start, 3), gain_db=gain))

    # ---- music: beat grid, align hard cuts to beats by choosing where the track starts
    y, _ = librosa.load(a.music, sr=SR, mono=True)
    tempo, bf = librosa.beat.beat_track(y=y, sr=SR); beats = librosa.frames_to_time(bf, sr=SR)
    hard = [c['t'] for c in cues if c['type'] in ('scene_cut', 'reveal')]
    period = float(np.median(np.diff(beats)))
    best = min(((sum(min(abs((beats - s) - t)) for t in hard), s) for s in np.arange(0, min(period * 8, len(y) / SR - dur), 0.005)))
    mstart = float(best[1]); resid = {t: round(float(min(abs((beats - mstart) - t))) * 1000) for t in hard}
    mus = load(a.music)[int(mstart * SR): int(mstart * SR) + n]
    mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))
    mus *= 10 ** (a.music_db / 20) * 0.35
    # duck under voice: smoothed voice envelope -> up to 10 dB reduction
    env = np.abs(voice).max(1); k = int(0.12 * SR); env = np.convolve(env, np.ones(k) / k, 'same')
    duck = 1 - (1 - 10 ** (-10 / 20)) * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
    mus *= duck[:, None]
    f = int(0.5 * SR); end = int(dur * SR); mus[end - f:end] *= np.linspace(1, 0, f)[:, None]; mus[end:] = 0

    mix = (voice + sfx + mus)[:end]
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, 'mix.wav'); sf.write(w, mix, SR)
        gain = 0.0
        for attempt in range(3):
            af = f'volume={gain}dB,alimiter=limit=0.5:level=false'
            run(['ffmpeg', '-y', '-v', 'error', '-i', a.video, '-i', w, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
                 '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', a.out])
            I, P = measure(a.out)
            if I is not None and abs(I + 16) < 0.6 and P is not None and P < -4:
                break
            gain += (-16 - I) if I is not None else 0
    Im, Pm = measure(a.out)
    # ---- report
    risky = sorted(placed, key=lambda c: (c['type'] not in ('build_up', 'reveal', 'typing'), -abs(resid.get(c['t'], 0))))[:5]
    md = [f"# Sound pass — {Path(a.out).name}", '', f"- Integrated loudness: **{Im} LUFS** (target -16); true peak **{Pm} dBFS** (target < -4). Measured on the exported MP4.",
          f"- Music: `{Path(a.music).name}` starts {mstart:.3f}s in, {a.music_db} dB bed, ducked ~10 dB under the voice. Tempo ≈ {float(np.atleast_1d(tempo)[0]):.0f} BPM.",
          f"- Music source: {a.music_source or 'NOT GIVEN'} · licence: {a.music_license or 'LICENCE NOT CONFIRMED — check before publishing'}",
          '- Cut-to-beat error: ' + ', '.join(f'{t:.2f}s={e} ms' for t, e in resid.items()), '', '| t | type | sound | gain | licence |', '|---|---|---|---|---|']
    md += [f"| {c['t']:.2f} | {c['type']} | {c['file']} | {c['gain_db']} dB | {c['license']} |" for c in placed]
    md += ['', '**Check these 5 with headphones:** ' + ', '.join(f"{c['t']:.2f}s ({c['type']})" for c in risky),
           '', 'All SFX are CC0 (bundled kit). Claude cannot hear: these numbers are measurements, not a judgement that it sounds good.']
    Path(a.out + '.sound.md').write_text('\n'.join(md) + '\n')
    cred = sorted({f"{c['file']} — {c.get('credit') or 'see source'} — {c['source_url']} ({c['license']})" for c in placed})
    Path(a.out + '.credits.txt').write_text('Sound effects (CC0):\n' + '\n'.join(cred) + f"\n\nMusic: {a.music_source or Path(a.music).name} ({a.music_license or 'licence not confirmed'})\n")
    print(f'{a.out}  I={Im} LUFS  TP={Pm} dBFS  beat err {resid}')


if __name__ == '__main__':
    main()
