#!/usr/bin/env python3
"""YouTube upload tracker: which finished edits in the Drive V+S folders are (not) on our YouTube channels.

  python3 tools/yt_tracker.py scan            # yt-dlp every channel in tracker/channels.json -> tracker/youtube_channel.json (no API key)
  python3 tools/yt_tracker.py match           # tracker/drive_vs.json + channel + reviews/marks -> tracker/youtube_tracker.json
  python3 tools/yt_tracker.py report [--all]  # print what is NOT posted (or everything)
  python3 tools/yt_tracker.py hq              # compact copy for Content HQ -> outputs/content-hq/youtube.json
  python3 tools/yt_tracker.py sync DIR        # merge Content HQ marks exported with ArtifactData (collection yt_marks) into tracker/marks.json
  python3 tools/yt_tracker.py mark <drive_id> posted|not_posted|skip [--yt <videoId>] [--note ..]   # manual decision

Inputs
  tracker/drive_vs.json      inventory of videos in the V+S folders (refreshed by an agent with the Drive connector, see tracker/README.md)
  tracker/ai_review.json     {drive_id: {status, yt, reason}} decisions from the AI review of uncertain matches
  tracker/marks.json         {drive_id: {status, yt, note, at}} manual marks (also synced from Content HQ, collection yt_marks)
Priority: manual mark > AI review > automatic match.
Automatic match: video length within 2 s of a channel video (strong), plus title similarity between the Drive file name and the YouTube title.
"""
import json, re, subprocess, sys, datetime as dt
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; T = ROOT / 'tracker'
rd = lambda p, d: json.loads(p.read_text()) if p.exists() else d
STOP = set('the a an and or of to for in on with how your you my v s vs final edit edited video export new version ready posting post v2 v3 mp4 mov'.split())


def norm(s):
    s = re.sub(r'\.(mp4|mov|m4v)$', '', s, flags=re.I)
    s = re.sub(r'[_\-\.\[\]\(\)|:!?,"\'#+]', ' ', s).lower()
    s = re.sub(r'\b(19|20)\d{2}\b|\b\d{1,2}\b', ' ', s)
    return ' '.join(w for w in s.split() if w not in STOP)


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return 0.0
    wa, wb = set(a.split()), set(b.split())
    jac = len(wa & wb) / max(1, min(len(wa), len(wb)))
    return max(SequenceMatcher(None, a, b).ratio(), jac)


def scan():
    out = []
    for ch in rd(T / 'channels.json', []):
        for tab in ('videos', 'shorts', 'streams'):
            r = subprocess.run(['yt-dlp', '--flat-playlist', '--print', '%(id)s\t%(duration)s\t%(title)s', f"https://www.youtube.com/channel/{ch['channel_id']}/{tab}"], capture_output=True, text=True)
            for line in r.stdout.splitlines():
                vid, dur, title = (line.split('\t', 2) + ['', ''])[:3]
                out.append({'channel': ch['key'], 'tab': tab, 'id': vid, 'duration_s': float(dur) if dur not in ('NA', '', 'None') else None, 'title': title, 'url': f'https://youtu.be/{vid}'})
    (T / 'youtube_channel.json').write_text(json.dumps({'scanned_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'videos': out}, indent=1))
    print(f'{len(out)} channel videos saved')


def best_match(d, yt):
    cands = []
    for v in yt:
        s_t = sim(d['name'], v['title']); s_d = 0; dd = None
        if d.get('duration_s') and v.get('duration_s'):
            dd = abs(d['duration_s'] - v['duration_s'])
            s_d = 60 if dd <= 2 else 40 if dd <= 6 else 15 if dd <= 20 else 0
        score = s_d + 40 * s_t
        if score > 20: cands.append((score, dd, s_t, v))
    cands.sort(key=lambda c: -c[0])
    return cands[:3]


def match():
    drive = rd(T / 'drive_vs.json', []); yt = rd(T / 'youtube_channel.json', {}).get('videos', [])
    ai = rd(T / 'ai_review.json', {}); marks = rd(T / 'marks.json', {}); ytmap = {v['id']: v for v in yt}; rows = []
    for d in drive:
        c = best_match(d, yt); top = c[0] if c else None
        auto = 'posted' if top and top[0] >= 70 else 'check' if top and top[0] >= 35 else 'not_posted'
        row = {**{k: d.get(k) for k in ('drive_id', 'name', 'folder_label', 'subpath', 'duration_s', 'created', 'url')},
               'auto': auto, 'score': round(top[0]) if top else 0,
               'candidates': [{'id': v['id'], 'title': v['title'], 'tab': v['tab'], 'duration_s': v['duration_s'], 'score': round(s), 'dur_diff': None if dd is None else round(dd, 1), 'title_sim': round(st, 2)} for s, dd, st, v in c]}
        src, status, yid, why = 'auto', auto, (top[3]['id'] if top and auto == 'posted' else None), ''
        if d['drive_id'] in ai: a = ai[d['drive_id']]; src, status, yid, why = 'ai', a['status'], a.get('yt'), a.get('reason', '')
        if d['drive_id'] in marks: m = marks[d['drive_id']]; src, status, yid, why = 'manual', m['status'], m.get('yt'), m.get('note', '')
        row.update(status=status, source=src, yt=yid, yt_url=f'https://youtu.be/{yid}' if yid else None, yt_title=ytmap.get(yid, {}).get('title') if yid else None, reason=why)
        rows.append(row)
    summary = {s: sum(r['status'] == s for r in rows) for s in ('posted', 'not_posted', 'check', 'skip')}
    (T / 'youtube_tracker.json').write_text(json.dumps({'built_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'summary': summary, 'items': rows}, indent=1))
    print(summary)


def report(all_=False):
    rows = rd(T / 'youtube_tracker.json', {}).get('items', [])
    for r in rows:
        if all_ or r['status'] in ('not_posted', 'check'):
            m = f" ~ {r['candidates'][0]['title']} ({r['candidates'][0]['score']})" if r['candidates'] else ''
            print(f"[{r['status']:10}] {r['folder_label']} / {r['name']}{m}")


def mark(did, status, yt=None, note=''):
    m = rd(T / 'marks.json', {}); m[did] = {'status': status, 'yt': yt, 'note': note, 'at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}
    (T / 'marks.json').write_text(json.dumps(m, indent=1)); match()


def hq():
    t = rd(T / 'youtube_tracker.json', {}); ch = rd(T / 'youtube_channel.json', {})
    items = [{'id': r['drive_id'], 'n': r['name'], 'f': r['folder_label'], 'sp': r.get('subpath') or '', 'l': r.get('duration_s'), 'd': (r.get('created') or '')[:10], 'u': r['url'],
              's': r['status'], 'yt': r.get('yt'), 'yt_t': r.get('yt_title'), 'r': r.get('reason') or '',
              'c': [{'id': c['id'], 't': c['title'], 'dd': c['dur_diff'], 'ts': c['title_sim']} for c in r['candidates'][:1]]} for r in t.get('items', [])]
    order = {s: i for i, s in enumerate(['not_posted', 'check', 'posted', 'skip'])}
    items.sort(key=lambda x: (x['f'], order.get(x['s'], 9), x['n']))
    out = ROOT / 'outputs/content-hq/youtube.json'
    out.write_text(json.dumps({'scanned': ch.get('scanned_at', ''), 'built': t.get('built_at', ''), 'items': items}, separators=(',', ':')))
    print(f'{len(items)} items -> {out}')


def sync(d):
    m = rd(T / 'marks.json', {}); n = 0
    for f in Path(d).rglob('*.json'):
        v = json.loads(f.read_text()); v = v.get('data', v); did = v.get('drive_id') or f.stem
        if v.get('status') in ('posted', 'not_posted', 'skip'): m[did] = {'status': v['status'], 'yt': v.get('yt'), 'note': v.get('note', ''), 'at': v.get('at')}; n += 1
    (T / 'marks.json').write_text(json.dumps(m, indent=1)); print(f'synced {n} marks'); match()


if __name__ == '__main__':
    a = sys.argv[1:]; cmd = a[0] if a else 'report'
    if cmd == 'scan': scan()
    elif cmd == 'match': match()
    elif cmd == 'report': report('--all' in a)
    elif cmd == 'hq': hq()
    elif cmd == 'sync': sync(a[1])
    elif cmd == 'mark':
        yt = a[a.index('--yt') + 1] if '--yt' in a else None; note = a[a.index('--note') + 1] if '--note' in a else ''
        mark(a[1], a[2], yt, note)
