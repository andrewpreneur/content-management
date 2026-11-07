#!/usr/bin/env python3
"""Transcribe each paragraph back with faster-whisper and flag words that differ from the script.
  python3 check_voice.py onb1 andrew   -> prints per-paragraph diffs, writes build/<id>_<voice>/whisper.json"""
import json, re, sys, difflib
from pathlib import Path
from faster_whisper import WhisperModel
HERE = Path(__file__).parent
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ')).split()
CANON = {'gohighlevel': 'go high level', 'saas': 'sass', 'sas': 'sass', 'ai': 'a i', 'a.i.': 'a i', 'highlevel': 'high level', 'followup': 'follow up', '7': 'seven'}
def canon(words):
    out = []
    for w in words:
        out += CANON.get(w, w).split()
    return out
_model = None
def load16(path):
    import subprocess, numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def model():
    global _model
    if _model is None:
        _model = WhisperModel('small.en', device='cpu', compute_type='int8')
    return _model
def main():
    vid, voice = sys.argv[1], sys.argv[2]
    paras = json.loads((HERE / 'scripts.json').read_text())[vid]['paras']
    d = HERE / 'build' / f'{vid}_{voice}'; res = []
    for i, p in enumerate(paras):
        segs, _ = model().transcribe(load16(d / f'p{i:02d}.wav'), language='en', beam_size=5,
                                     initial_prompt='GoHighLevel, SaaS, Claude, AI, Skool.')
        heard = ' '.join(s.text for s in segs).strip()
        a, b = canon(norm(p)), canon(norm(heard))
        diff = [(op, ' '.join(a[i1:i2]), ' '.join(b[j1:j2])) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes() if op != 'equal']
        res.append({'i': i, 'heard': heard, 'diff': diff})
        print(f'p{i:02d} {"OK" if not diff else "DIFF " + str(diff)}')
    (d / 'whisper.json').write_text(json.dumps(res, indent=1))
if __name__ == '__main__':
    main()
