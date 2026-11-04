#!/usr/bin/env python3
"""Long-form review: find repetitions, retakes, false starts, filler and dead air in a transcript, then
write a review report + a cut list, and (optionally) render a rough cut with those parts removed.

Usage:
  python3 tools/longform_review.py transcript.json OUT_DIR [--video SRC.mp4 --render] [--pause 1.2]
transcript.json from tools/transcribe.py (word timestamps).
Output: OUT_DIR/review.md (every issue with timestamps + the words), OUT_DIR/cuts.json (keep ranges),
        OUT_DIR/cuts.csv (in/out for an editor), OUT_DIR/roughcut.mp4 when --render.
Nothing is removed silently: every cut is listed in review.md with a reason, and the editor/Andrew approves.
"""
import argparse, json, re, subprocess
from difflib import SequenceMatcher
from pathlib import Path

FILLERS = {'um', 'uh', 'erm', 'uhm', 'hmm', 'ah'}
SOFT_FILLERS = ['you know', 'i mean', 'kind of', 'sort of', 'like', 'basically', 'right?', 'alright', 'so yeah']


def norm(s):
    return re.sub(r"[^a-z0-9' ]", '', s.lower()).strip()


def ts(t):
    m, s = divmod(t, 60); return f"{int(m)}:{s:05.2f}"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('transcript'); ap.add_argument('out')
    ap.add_argument('--video'); ap.add_argument('--render', action='store_true'); ap.add_argument('--pause', type=float, default=1.2)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d = json.loads(Path(a.transcript).read_text())
    words = [w for s in d['segments'] for w in s['words']]
    # sentences from punctuation
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.!?]$', w['w']):
            sents.append(cur); cur = []
    if cur: sents.append(cur)
    S = [dict(text=' '.join(w['w'] for w in s), n=norm(' '.join(w['w'] for w in s)), s=s[0]['s'], e=s[-1]['e']) for s in sents]
    issues, cuts = [], []
    # 1) repeated / retaken sentences (near-identical within 60 s) -> cut the EARLIER take (the later one is usually the clean retake)
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            if S[j]['s'] - S[i]['e'] > 60: break
            if len(S[i]['n']) < 12: continue
            r = SequenceMatcher(None, S[i]['n'], S[j]['n']).ratio()
            if r > 0.9 and S[j]['s'] - S[i]['e'] < 30:
                issues.append(dict(kind='repeat', s=S[i]['s'], e=S[i]['e'], text=S[i]['text'], note=f"near-identical to {ts(S[j]['s'])} ({r:.0%}); cut the earlier take"))
                cuts.append((S[i]['s'], S[i]['e'], 'repeat'))
            elif r > 0.82:
                issues.append(dict(kind='check', s=S[i]['s'], e=S[i]['e'], text=S[i]['text'], note=f"similar to {ts(S[j]['s'])} ({r:.0%}): retake or a callback? not cut"))
    # 2) false starts / stutters: same 1-3 word phrase immediately repeated ("you fail, you fail", "the the")
    nw = [norm(w['w']) for w in words]
    for k in (3, 2, 1):
        i = 0
        while i + 2 * k <= len(words):
            punct = re.search(r'[,.!?]$', words[i + k - 1]['w'])  # "really, really" / "fail, fail forward" = emphasis, keep
            if nw[i:i + k] == nw[i + k:i + 2 * k] and all(nw[i:i + k]) and not punct and words[i + k]['s'] - words[i + k - 1]['e'] < 0.8:
                txt = ' '.join(w['w'] for w in words[i:i + 2 * k])
                if not any(c[0] <= words[i]['s'] < c[1] for c in cuts):
                    issues.append(dict(kind='stutter', s=words[i]['s'], e=words[i + k - 1]['e'], text=txt, note=f'repeated {k}-word phrase'))
                    cuts.append((words[i]['s'], words[i + k]['s'], 'stutter'))
                i += 2 * k
            else:
                i += 1
    # 3) filler words
    for w in words:
        if norm(w['w']) in FILLERS:
            issues.append(dict(kind='filler', s=w['s'], e=w['e'], text=w['w'], note='filler')); cuts.append((w['s'], w['e'], 'filler'))
    soft = {f: len(re.findall(r'\b' + re.escape(f) + r'\b', ' '.join(nw))) for f in SOFT_FILLERS}
    # 4) dead air
    for p, q in zip(words, words[1:]):
        gap = q['s'] - p['e']
        if gap > a.pause:
            issues.append(dict(kind='pause', s=p['e'], e=q['s'], text=f'{gap:.1f}s silence', note='tighten to 0.35 s'))
            cuts.append((p['e'] + 0.2, q['s'] - 0.15, 'pause'))
    issues.sort(key=lambda x: x['s']); cuts.sort()
    end = words[-1]['e'] + 0.3
    keep, t = [], 0.0
    for s, e, _ in cuts:
        if s > t: keep.append([round(t, 2), round(s, 2)])
        t = max(t, e)
    keep.append([round(t, 2), round(end, 2)])
    removed = end - sum(b - a_ for a_, b in keep)
    Path(out / 'cuts.json').write_text(json.dumps({'keep': keep, 'cuts': cuts}, indent=1))
    Path(out / 'cuts.csv').write_text('in,out,reason\n' + '\n'.join(f'{s:.2f},{e:.2f},{r}' for s, e, r in cuts) + '\n')
    md = [f"# Long-form review — {Path(a.transcript).parent.name}", '',
          f"Length {ts(end)} → rough cut {ts(end - removed)} ({removed:.1f}s removed across {len(cuts)} cuts).", '',
          '| Time | Type | What | Note |', '|---|---|---|---|']
    md += [f"| {ts(i['s'])} | {i['kind']} | {i['text'][:90]} | {i['note']} |" for i in issues]
    md += ['', '**Verbal habits (not auto-cut — fix in delivery or by hand):** ' + ', '.join(f'"{k}" ×{v}' for k, v in soft.items() if v),
           '', 'Note: Whisper drops many "um/uh" sounds, so filler counts are a floor. Check every cut in the rough cut before it ships.']
    Path(out / 'review.md').write_text('\n'.join(md) + '\n')
    print(f"{len(issues)} issues, {len(cuts)} cuts, {removed:.1f}s removed → {out}/review.md")
    if a.render and a.video:
        parts = ''.join(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0, e - s - 0.03)}:d=0.03[a{i}];" for i, (s, e) in enumerate(keep))
        cat = ''.join(f'[v{i}][a{i}]' for i in range(len(keep))) + f'concat=n={len(keep)}:v=1:a=1[v][a]'
        Path(out / 'filter.txt').write_text(parts + cat)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a.video, '-filter_complex_script', str(out / 'filter.txt'), '-map', '[v]', '-map', '[a]',
                        '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24', '-c:a', 'aac', str(out / 'roughcut.mp4')], check=True)
        print('rough cut →', out / 'roughcut.mp4')


if __name__ == '__main__':
    main()
