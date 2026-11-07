#!/usr/bin/env python3
"""QC every paragraph mp3 in a voice dir: whisper transcript vs script, pace (words/s), loudness, max pause.
  python3 qc_voice.py <voice_dir> [<voice_dir> ...]   -> prints a table, writes <dir>/qc.json
Flags: word mismatch (after normalising), pace outside 2.2-3.6 w/s, loudness off median by >3 LU, inner pause > 0.9 s.
"""
import json, re, subprocess, sys
from pathlib import Path
from faster_whisper import WhisperModel

_m = None


def model():
    global _m
    if _m is None:
        _m = WhisperModel('small.en', device='cpu', compute_type='int8')
    return _m


def pcm(path):
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype('float32') / 32768


def norm(s):
    s = s.lower().replace('gohighlevel', 'go high level').replace('highlevel', 'high level').replace('saas', 'sass')
    s = s.replace("'", '').replace('’', '')
    return re.sub(r'[^a-z0-9 ]+', ' ', s).split()


def lufs(path):
    o = subprocess.run(['ffmpeg', '-nostats', '-i', str(path), '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', o)
    return float(m[-1]) if m else None


def qc_dir(d):
    d = Path(d); rows = []
    for mp3 in sorted(d.glob('p*.mp3')):
        meta = json.load(open(mp3.with_suffix('.json')))
        segs, _ = model().transcribe(pcm(mp3), word_timestamps=True, beam_size=5,
                                     initial_prompt='GoHighLevel, Claude, SaaS, AI agents, Skool community.')
        words = [w for s in segs for w in s.words]
        heard = ' '.join(w.word.strip() for w in words)
        ref, hyp = norm(meta['text']), norm(heard)
        import difflib
        sm = difflib.SequenceMatcher(None, ref, hyp)
        diffs = [(' '.join(ref[a:b]), ' '.join(hyp[c:e])) for op, a, b, c, e in sm.get_opcodes() if op != 'equal']
        dur = words[-1].end - words[0].start if words else 0
        pace = len(ref) / dur if dur else 0
        gaps = [words[i + 1].start - words[i].end for i in range(len(words) - 1)]
        rows.append({'p': mp3.stem, 'pace': round(pace, 2), 'lufs': lufs(mp3), 'max_gap': round(max(gaps or [0]), 2),
                     'diffs': diffs, 'heard': heard})
    med = sorted(r['lufs'] for r in rows)[len(rows) // 2]
    for r in rows:
        flags = []
        if r['diffs']: flags.append('WORDS')
        if not 2.2 <= r['pace'] <= 3.6: flags.append('PACE')
        if abs(r['lufs'] - med) > 3: flags.append('LOUD')
        if r['max_gap'] > 0.9: flags.append('PAUSE')
        r['flags'] = flags
        print(f"{d.name:22} {r['p']} pace {r['pace']:.2f} lufs {r['lufs']:.1f} gap {r['max_gap']:.2f} {' '.join(flags)} {r['diffs'] if r['diffs'] else ''}")
    json.dump(rows, open(d / 'qc.json', 'w'), indent=1)


if __name__ == '__main__':
    for d in sys.argv[1:]:
        qc_dir(d)
