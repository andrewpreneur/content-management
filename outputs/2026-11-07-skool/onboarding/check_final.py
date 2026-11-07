#!/usr/bin/env python3
"""Whisper the final MP4 (voice over music + SFX) and report word accuracy vs the script, plus first-word sync.
  python3 check_final.py onb1 jessica"""
import json, sys, difflib
from pathlib import Path
from check_voice import load16, model, norm, canon
from mix import NAMES
HERE = Path(__file__).parent
vid, voice = sys.argv[1], sys.argv[2]
f = HERE / 'renders' / f'{NAMES[vid]}_{voice}.mp4'
paras = json.loads((HERE / 'scripts.json').read_text())[vid]['paras']
timing = json.loads((HERE / 'build' / f'{vid}_{voice}' / 'timing.json').read_text())
segs, _ = model().transcribe(load16(f), language='en', beam_size=5, word_timestamps=True, initial_prompt='GoHighLevel, SaaS, AI.')
segs = list(segs)
heard = ' '.join(s.text for s in segs)
a, b = canon(norm(' '.join(paras))), canon(norm(heard))
sm = difflib.SequenceMatcher(None, a, b)
acc = sum(x.size for x in sm.get_matching_blocks()) / len(a)
w0 = segs[0].words[0].start if segs and segs[0].words else None
print(json.dumps({'file': f.name, 'word_match': round(acc, 3), 'first_word_heard_s': w0, 'first_word_timing_s': timing['paras'][0]['start'],
                  'diffs': [(op, ' '.join(a[i1:i2]), ' '.join(b[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal'][:8]}))
