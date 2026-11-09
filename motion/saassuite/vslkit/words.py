#!/usr/bin/env python3
"""Word timings for a VSL. Usage: python3 words.py voice.wav out.json
faster-whisper (small.en) fed a numpy array (its own decoder is broken here). Writes [[word,start,end],...]."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
m = WhisperModel('small.en', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5, vad_filter=False)
W = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
json.dump(W, open(out, 'w'))
print(len(W), 'words, last end', W[-1][2])
print(' '.join(w[0] for w in W))
