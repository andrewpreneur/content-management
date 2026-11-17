#!/usr/bin/env python3
"""Export the repo's data as JSONL for Convex (Your Content System, repo andrewpreneur/content-hq).
  python3 tools/export_convex.py OUT_DIR
then in content-hq:  npx convex import --table <name> OUT_DIR/<name>.jsonl --replace -y   (tools/import.sh does all tables)
Tables: accounts, posts, planItems, driveVideos, syncRuns. Approvals live only in Convex (the app writes them)."""
import json, sys, datetime as dt
from pathlib import Path
R = Path(__file__).resolve().parents[1]; out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
def clean(x):
    if isinstance(x, dict): return {k: clean(v) for k, v in x.items() if v is not None}
    return x
def w(name, rows):
    with open(out / f'{name}.jsonl', 'w') as f:
        for r in rows: f.write(json.dumps(clean(r), ensure_ascii=False) + '\n')
    print(name, len(rows))
num = lambda x: float(x) if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit()) else None

w('accounts', [{'key': a['key'], 'platform': a['platform'], 'handle': a['handle'], 'url': a['url'], 'method': a['method'], 'note': a.get('note')} for a in json.loads((R / 'library/accounts.json').read_text())])
w('posts', [{'uid': p['uid'], 'platform': p['platform'], 'account': p['account'], 'postId': str(p['id']), 'kind': p['kind'], 'title': p.get('title'), 'url': p.get('url'),
             'durationS': num(p.get('duration_s')), 'published': p.get('published'), 'views': num(p.get('views')),
             'thumb': ('/' + p['thumb'].replace('library/', '')) if p.get('thumb') else None} for p in json.loads((R / 'library/posts.json').read_text())])
q = json.loads((R / 'outputs/content-hq/queue.json').read_text())
mp = R / 'posting/media.json'; media = json.loads(mp.read_text()) if mp.exists() else {}
med = lambda iid: [{'driveId': f['driveId'], 'name': f['name'], 'mimeType': f['mimeType']} for f in (media.get(iid) or {}).get('files', [])] or None
w('planItems', [{'itemId': i['id'], 'date': i['d'], 'time': i['t'], 'kind': i['k'], 'type': i.get('ty'), 'title': i['ti'], 'platforms': i.get('pl') or [], 'caption': i.get('c') or None,
                 'captionOverrides': i.get('co') or None, 'thumb': i.get('th'), 'drive': i.get('dr'), 'review': i.get('rv'), 'source': i.get('src'),
                 'lint': [x for x in (i.get('lint') or []) if not x.startswith('no_media')] or None, 'stage': i['st'], 'media': med(i['id'])} for i in q])
t = json.loads((R / 'tracker/youtube_tracker.json').read_text())
w('driveVideos', [{'driveId': r['drive_id'], 'name': r['name'], 'folderLabel': r['folder_label'], 'subpath': r.get('subpath') or None, 'durationS': num(r.get('duration_s')),
                   'created': r.get('created'), 'url': r['url'], 'status': r['status'], 'source': r['source'], 'youtubeId': r.get('yt'), 'youtubeTitle': r.get('yt_title'),
                   'reason': r.get('reason') or None,
                   'candidate': ({'id': r['candidates'][0]['id'], 'title': r['candidates'][0]['title'], 'durDiff': r['candidates'][0]['dur_diff'], 'titleSim': r['candidates'][0]['title_sim']}
                                 if r['candidates'] else None)} for r in t['items']])
now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
w('syncRuns', [{'dataset': d, 'at': now, 'note': 'exported from content-management'} for d in ('posts', 'planItems', 'driveVideos', 'accounts')])
