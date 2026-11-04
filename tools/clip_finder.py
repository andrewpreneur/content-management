#!/usr/bin/env python3
"""Clip finder: scan a long recording's transcript for moments that stand on their own as short-form clips.

Usage:
  python3 tools/clip_finder.py transcript.json OUT_DIR [--source NAME] [--min 15] [--max 45] [--top 25]
transcript.json from tools/transcribe.py (segments with word timings).
Writes OUT_DIR/candidates.json + OUT_DIR/candidates.md: ranked, non-overlapping, topic-deduplicated windows, each starting
and ending on a sentence boundary, with the opening line scored by the ig-reel hook scorer.

This finds candidates; a human (or Claude reading the list) picks the keepers. Scores are text-only heuristics:
they catch weak openers, context-dependent starts and rambling, not which clip will go viral.
"""
import argparse, importlib.util, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('hookscore', ROOT / 'vendor/instagram-agent-skill/skills/ig-reel/hookscore.py')
hookscore = importlib.util.module_from_spec(spec); spec.loader.exec_module(hookscore)

# openers that lean on something said before the clip
DEPENDENT = {'and', 'but', 'so', 'because', 'which', 'that', 'it', 'it’s', "it's", 'they', 'he', 'she', 'this', 'these', 'those',
             'yeah', 'yes', 'um', 'uh', 'also', 'then', 'or', 'like', 'right', 'exactly', 'totally', 'oh', 'okay', 'mm', 'well'}
FILLER = {'um', 'uh', 'like', 'basically', 'literally', 'kind', 'sort'}
STAKES = re.compile(r"\b(fail\w*|lost|lose|losing|never|always|first|best|worst|biggest|mistake\w*|secret|truth|why|how|money|\$\d|\d+|"
                    r"quit|fired|hired|scared|afraid|hard|easy|simple|insane|crazy|changed|wish|regret|nobody|everyone|friends?|"
                    r"million|thousand|years?|months?|days?)\b", re.I)
STOP = set('the a an and or but so to of in on at for with is are was were be been i you we they he she it that this my your our '
           'me us them his her its as not no yes just really very like um uh know think going get got have has had do did'.split())


def norm(w):
    return re.sub(r"[^a-z0-9'’$]", '', w.lower())


def sentences(words, gap=0.9):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if re.search(r'[.!?]$', w['w']) or (nxt and nxt['s'] - w['e'] > gap):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return [dict(words=s, text=' '.join(x['w'] for x in s).strip(), s=s[0]['s'], e=s[-1]['e']) for s in out]


def score_window(S, i, j):
    first, last = S[i], S[j]
    text = ' '.join(s['text'] for s in S[i:j + 1]); toks = [norm(w['w']) for s in S[i:j + 1] for w in s['words']]
    dur = last['e'] - first['s']
    hook_line = first['text'] if len(first['words']) >= 5 or i == j else first['text'] + ' ' + S[i + 1]['text']
    _, hook, _, flags = hookscore.run(hook_line)
    opener = norm(first['words'][0]['w'])
    dep = 25 if opener in DEPENDENT else 0
    filler = sum(t in FILLER for t in toks) / max(1, len(toks))
    stakes = len(STAKES.findall(text))
    punch = 8 if len(last['words']) <= 9 else 0                     # short closing line = landing
    question = 6 if first['text'].endswith('?') else 0              # a question up front works for question-hook formats
    pace = len(toks) / max(1, dur)                                  # words per second
    pace_pen = 10 if pace < 1.8 else 0
    score = 0.55 * hook + min(20, 3 * stakes) + punch + question - dep - 120 * filler - pace_pen
    return dict(start=round(first['s'], 2), end=round(last['e'], 2), dur=round(dur, 1), score=round(score, 1), hook_score=round(hook),
                hook=hook_line, opener_depends=bool(dep), filler_pct=round(100 * filler, 1), stakes=stakes, words_per_s=round(pace, 2),
                text=text, flags=flags)


def content(text):
    return {t for t in (norm(w) for w in text.split()) if t and t not in STOP and len(t) > 2}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('transcript'); ap.add_argument('out')
    ap.add_argument('--source', default=None); ap.add_argument('--min', type=float, default=15); ap.add_argument('--max', type=float, default=45)
    ap.add_argument('--top', type=int, default=25)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d = json.loads(Path(a.transcript).read_text()); words = [w for s in d['segments'] for w in s['words']]
    S = sentences(words)
    cands = []
    for i in range(len(S)):
        for j in range(i, len(S)):
            dur = S[j]['e'] - S[i]['s']
            if dur > a.max: break
            if dur >= a.min: cands.append(score_window(S, i, j))
    cands.sort(key=lambda c: -c['score'])
    picked = []
    for c in cands:  # non-overlapping, and not the same topic twice
        if any(min(c['end'], p['end']) - max(c['start'], p['start']) > 0.25 * min(c['dur'], p['dur']) for p in picked): continue
        cw = content(c['text'])
        if any(len(cw & content(p['text'])) / max(1, len(cw | content(p['text']))) > 0.35 for p in picked): continue
        picked.append(c)
        if len(picked) >= a.top: break
    src = a.source or Path(a.transcript).parent.name
    for k, c in enumerate(sorted(picked, key=lambda c: c['start'])):
        c['id'] = f"{src}-c{k + 1:02d}"
    picked.sort(key=lambda c: c['start'])
    (out / 'candidates.json').write_text(json.dumps(picked, indent=1, ensure_ascii=False))
    ts = lambda t: f"{int(t // 60)}:{t % 60:05.2f}"
    md = [f'# Clip candidates — {src}', '', f'{len(picked)} non-overlapping windows ({a.min:.0f}–{a.max:.0f} s), best first within time order. '
          'Score = hook (ig-reel hookscore) + stakes + landing − context-dependent opener − filler. Pick by reading, not by score.', '']
    for c in picked:
        md += [f"## {c['id']} · {ts(c['start'])}–{ts(c['end'])} ({c['dur']} s) · score {c['score']} · hook {c['hook_score']}"
               + (' · ⚠ opener depends on context' if c['opener_depends'] else ''), f"> {c['text']}", '']
    (out / 'candidates.md').write_text('\n'.join(md) + '\n')
    print(f"{len(cands)} windows → {len(picked)} candidates → {out}/candidates.md")


if __name__ == '__main__':
    main()
