#!/usr/bin/env python3
"""Transcribe a finished MP4 (voice + music + SFX) and compare heard word times to the caption timeline.
  python3 check_sync.py <final.mp4> <timing.json>  -> word accuracy, median/95th-percentile offset (ms)"""
import json, sys, difflib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import qc_voice as q
mp4, tj = sys.argv[1:3]
T = json.load(open(tj))
segs, _ = q.model().transcribe(q.pcm(mp4), word_timestamps=True, beam_size=5, initial_prompt='GoHighLevel, Claude, SaaS, AI agents.')
heard = [w for s in segs for w in s.words]
hn = [q.norm(w.word)[0] if q.norm(w.word) else '' for w in heard]
rn = [q.norm(w['w'])[0] if q.norm(w['w']) else '' for w in T['words']]
sm = difflib.SequenceMatcher(None, rn, hn, autojunk=False)
offs = []
for a, b, n in sm.get_matching_blocks():
    for k in range(n): offs.append(heard[b + k].start - T['words'][a + k]['s'])
offs.sort()
acc = sum(n for *_, n in sm.get_matching_blocks()) / len(rn)
print(json.dumps({'file': mp4.rsplit('/', 1)[-1], 'word_match': round(acc, 3), 'median_offset_ms': round(1000 * offs[len(offs) // 2]), 'p95_abs_ms': round(1000 * sorted(abs(o) for o in offs)[int(len(offs) * .95)])}))
