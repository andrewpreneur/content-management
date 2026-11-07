#!/usr/bin/env python3
"""Mix voice + music + SFX for one render and mux the final MP4.

  python3 mix.py onb1 andrew   -> renders/<name>.mp4 (H.264 CRF 20 video copied from silent.mp4, AAC 192k, -14 LUFS, TP <= -1 dB, faststart)

Music: ElevenLabs music API beds (build/music/bed_*.mp3). The music start offset is chosen so scene cuts sit
closest to the beat grid (librosa). Music ducks ~10 dB under the voice. SFX: bundled CC0 kit from the
sound-effects skill (.claude/skills/sound-effects/sfx), one sound per cue from the page's cue list.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

HERE = Path(__file__).parent
SFX = HERE / '../../../.claude/skills/sound-effects/sfx'
SR = 48000
MUSIC = {'onb1': 'bed_a', 'onb2': 'bed_b', 'onb3': 'bed_c', 'intro': 'bed_d', 'ask': 'bed_d'}
NAMES = {'onb1': 'onboarding-1-find-your-starting-point', 'onb2': 'onboarding-2-share-as-you-build', 'onb3': 'onboarding-3-your-first-7-days',
         'intro': 'quick-guide-intro-post', 'ask': 'quick-guide-ask-a-question'}
# cue type -> (files to rotate through, gain dB)
KIT = {
    'whoosh': (['kit/whoosh.ogg', 'whoosh/fs-683101-quick-woosh.ogg', 'whoosh/fs-169867-swoosh.ogg'], -17),
    'pop': (['kit/pop.ogg', 'pop/kenney-interface-pluck-001.ogg', 'pop/fs-824189-pop-in-sfx.ogg', 'pop/kenney-interface-pluck-002.ogg'], -15),
    'click': (['kit/click.ogg'], -12),
    'tick': (['kit/tick.ogg', 'tick/fs528561.ogg'], -16),
    'typing': (['typing/fs-447909-keyboard-typing.ogg'], -24),
    'ding': (['ding/kenney-interface-confirmation-001.ogg', 'ding/fs-571513-soft-notifications-bell-ding-d.ogg'], -13),
    'impact': (['kit/impact.ogg'], -10),
}


def load(path, mono=False):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1' if mono else '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a if mono else a.reshape(-1, 2)


def db(x): return 10 ** (x / 20)


def ramp_env(n, spans, lo, hi, r=.3):
    """gain curve: hi outside spans, lo inside, linear ramps of r seconds."""
    g = np.full(n, hi, np.float32)
    t = np.arange(n) / SR
    for a, b in spans:
        k = np.clip(np.minimum((t - (a - r)) / r, ((b + r) - t) / r), 0, 1)
        g = np.minimum(g, hi - (hi - lo) * k)
    return g


def main():
    vid, voice = sys.argv[1], sys.argv[2]
    d = HERE / 'build' / f'{vid}_{voice}'
    timing = json.loads((d / 'timing.json').read_text()); cues = json.loads((d / 'cues.json').read_text())
    dur = timing['duration']; n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    # voice
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    v = load(d / 'voice.wav'); out[:min(n, len(v))] += v[:n]
    vL = meter.integrated_loudness(v)
    rel = vL - (-22.0)          # SFX gains in KIT are tuned for a -22 LUFS voice track
    # music: pick offset so whoosh (scene cut) cues land near beats
    import librosa
    mpath = HERE / 'build/music' / f'{MUSIC[vid]}.mp3'
    y, msr = librosa.load(str(mpath), sr=22050, mono=True)
    _, beats = librosa.beat.beat_track(y=y, sr=msr, units='time')
    period = float(np.median(np.diff(beats)))
    cuts = np.array([c['t'] + .25 for c in cues if c['type'] == 'whoosh'])  # visual cut lands ~TR after the whoosh cue
    best, berr = 0.0, 9
    for off in np.arange(0, min(8.0, len(y) / msr - dur - .5) if len(y) / msr > dur + .5 else .01, .01):
        bt = beats - off; bt = bt[bt > 0]
        if not len(bt): continue
        err = np.mean([np.min(np.abs(bt - c)) for c in cuts]) if len(cuts) else 0
        if err < berr: best, berr = off, err
    m = load(mpath)[int(best * SR):]
    if len(m) < n: m = np.concatenate([m] * (n // len(m) + 1))
    m = m[:n].copy()
    mL = meter.integrated_loudness(m)
    spans = [(p['start'] - .05, p['end'] + .1) for p in timing['paras']]
    g = ramp_env(n, spans, db(vL - 17 - mL), db(vL - 6 - mL), r=.35)   # music 17 dB under speech, 6 dB under when nobody talks
    fade = np.clip((dur - np.arange(n) / SR) / 1.6, 0, 1)
    out += m * (g * fade)[:, None]
    # sfx
    cache, last, rot = {}, {}, {}
    for c in cues:
        typ = c['type']
        if typ not in KIT: continue
        files, gdb = KIT[typ]
        if c.get('soft'): gdb -= 5
        if typ in last and c['t'] - last[typ] < .09: continue
        last[typ] = c['t']
        i = rot.get(typ, 0); rot[typ] = i + 1
        f = files[i % len(files)]
        if f not in cache: cache[f] = load(SFX / f)
        s = cache[f]
        if typ == 'typing':
            L = int(min(c.get('dur', 1), 3) * SR)
            s = np.concatenate([s] * (L // len(s) + 1))[:L].copy()
            fl = min(len(s), int(.08 * SR)); s[:fl] *= np.linspace(0, 1, fl)[:, None]; s[-fl:] *= np.linspace(1, 0, fl)[:, None]
        a = int(max(0, c['t'] - (.03 if typ == 'whoosh' else 0)) * SR)
        b = min(n, a + len(s))
        if b > a: out[a:b] += s[:b - a] * db(gdb + rel)
    pk = np.max(np.abs(out))
    if pk > .99: out *= .99 / pk
    sf.write(d / 'mix.wav', out, SR, subtype='FLOAT')
    # final: two-pass loudnorm to -14 LUFS / -1.5 dBTP (keeps true peak under -1 dB after AAC)
    renders = HERE / 'renders'; renders.mkdir(exist_ok=True)
    final = renders / f"{NAMES[vid]}_{voice}.mp4"
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(d / 'mix.wav'), '-af', 'loudnorm=I=-14:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'],
                          capture_output=True, text=True).stderr
    j = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
    ln = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(d / 'silent.mp4'), '-i', str(d / 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-af', ln + ',aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', str(final)], check=True)
    r = subprocess.run(['ffmpeg', '-nostats', '-i', str(final), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = [l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1]
    P = [l for l in r.splitlines() if l.strip().startswith('Peak:')][-1].split()[1]
    rep = {'file': final.name, 'music': MUSIC[vid], 'music_offset_s': round(best, 2), 'beat_period_s': round(period, 3),
           'cut_to_beat_err_ms': round(berr * 1000), 'lufs': float(I), 'true_peak_db': float(P)}
    (d / 'mix.json').write_text(json.dumps(rep)); print(json.dumps(rep))


if __name__ == '__main__':
    main()
