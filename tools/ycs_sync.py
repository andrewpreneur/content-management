#!/usr/bin/env python3
"""Two-way sync between this repo and Your Content System (Convex deployment harmless-ibis-268, app repo content-hq).

  python3 tools/ycs_sync.py pull     # Andrew's taps from the app -> posting/state.json + tracker/marks.json
  python3 tools/ycs_sync.py push     # repo data (library, queue, tracker) -> Convex (never touches approvals)
  python3 tools/ycs_sync.py all      # pull, rebuild tracker, push   (what the weekly task runs)

Needs a Convex deploy key in ~/.convex_deploy_key (calls the app's functions over its HTTP API; no checkout needed).
$YCS_BRAND picks the brand this repo feeds (default andrewpreneurship). If the key file is missing, one is created through the Convex management API with the team
token that the cloud environment's proxy injects for api.convex.dev (the key is written to the file, never printed).
"""
import json, os, subprocess, sys, tempfile, datetime as dt
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1]
HQ = Path(os.environ.get('CONTENT_HQ', R.parent / 'content-hq'))
KEYF = Path.home() / '.convex_deploy_key'
DEPLOYMENT = 'harmless-ibis-268'


def key():
    if not KEYF.exists():
        r = requests.post(f'https://api.convex.dev/v1/deployments/{DEPLOYMENT}/create_deploy_key',
                          headers={'Authorization': 'Bearer proxy-injected'}, json={'name': 'agent-sync'}, timeout=60)
        r.raise_for_status(); k = r.json().get('deployKey')
        if not k: sys.exit('Convex did not return a deploy key')
        KEYF.write_text(k); KEYF.chmod(0o600)
    return KEYF.read_text().strip()


def ensure_hq():
    if not (HQ / 'convex').exists():
        subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/andrewpreneur/content-hq', str(HQ)], check=True)
    if not (HQ / 'node_modules').exists():
        subprocess.run(['bun', 'install'], cwd=HQ, check=True)


URL = os.environ.get('CONVEX_URL', f'https://{DEPLOYMENT}.convex.cloud')
BRAND = os.environ.get('YCS_BRAND', 'andrewpreneurship')   # which brand in the app this repo feeds


def call(kind, path, args):
    """Run a Convex function (internal ones included) over the HTTP API with the deploy key."""
    for i in range(4):
        try:
            r = requests.post(f'{URL}/api/{kind}', json={'path': path, 'args': args, 'format': 'json'},
                              headers={'Authorization': f'Convex {key()}'}, timeout=300)
            j = r.json()
            if j.get('status') == 'success': return j['value']
            sys.exit(f'{path} failed: {str(j)[:600]}')
        except requests.RequestException as e:
            if i == 3: raise
            import time; time.sleep(2 ** i)


def pull():
    st_path = R / 'posting/state.json'; st = json.loads(st_path.read_text()) if st_path.exists() else {}
    n = 0
    for a in call('query', 'queue:allApprovals', {'brandKey': BRAND}):
        cur = st.get(a['itemId'], {})
        if cur.get('status') in ('scheduled', 'posted'): continue
        if cur.get('status') == a['status'] and cur.get('note', '') == a.get('note', '') and cur.get('mode') == a.get('mode'): continue
        st[a['itemId']] = {**cur, 'status': a['status'], 'note': a.get('note', ''), 'at': a['at'], 'via': 'app', **({'mode': a['mode']} if a.get('mode') else {})}; n += 1
    st_path.write_text(json.dumps(st, indent=1))
    mk_path = R / 'tracker/marks.json'; mk = json.loads(mk_path.read_text()) if mk_path.exists() else {}
    m = 0
    for r in call('query', 'youtube:manualMarks', {'brandKey': BRAND}):
        mk[r['driveId']] = {'status': r['status'], 'yt': r.get('youtubeId'), 'note': r.get('reason', ''), 'at': r.get('markedAt')}; m += 1
    mk_path.write_text(json.dumps(mk, indent=1))
    st = call('query', 'styles:forEngine', {'brandKey': BRAND})
    (R / 'docs/brand-video/brand-styles.json').write_text(json.dumps(st, indent=1, ensure_ascii=False))
    print(f'pulled {n} new approvals, {m} manual upload marks, {len(st["styles"])} brand styles, {len(st["picks"])} style picks')


def ingest(table, rows, max_bytes=600_000):
    """Replace this brand's rows of one table (approvals, schedule, posting history are never touched)."""
    batch, size, first, total = [], 0, True, 0
    def flush():
        nonlocal batch, size, first, total
        if batch or first:
            total += call('mutation', 'ingest:replace', {'brandKey': BRAND, 'table': table, 'rows': batch, 'first': first})
        batch, size, first = [], 0, False
    for r in rows:
        b = len(json.dumps(r))
        if size + b > max_bytes: flush()
        batch.append(r); size += b
    flush()
    return total


def push_only():
    d = Path(tempfile.mkdtemp(prefix='ycs_'))
    subprocess.run([sys.executable, str(R / 'tools/export_convex.py'), str(d)], check=True)
    subprocess.run([sys.executable, str(R / 'tools/export_app.py'), str(d / 'app')], check=True)
    done = []
    for t in ('accounts', 'posts', 'planItems', 'driveVideos'):
        rows = [json.loads(l) for l in (d / f'{t}.jsonl').read_text().split('\n') if l.strip()]
        print(t, ingest(t, rows)); done.append(t)
    for t in ('runs', 'runOutputs', 'podcastEpisodes', 'clips'):
        f = d / 'app' / f'{t}.json'
        if f.exists(): print(t, ingest(t, json.loads(f.read_text()))); done.append(t)
    call('mutation', 'ingest:finish', {'brandKey': BRAND, 'datasets': done})
    print('pushed', ', '.join(done))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    pull()                       # every command starts by saving Andrew's taps into the repo
    if cmd in ('push', 'all'):
        subprocess.run([sys.executable, str(R / 'tools/yt_tracker.py'), 'match'], check=True)   # applies marks.json
        subprocess.run([sys.executable, str(R / 'tools/yt_tracker.py'), 'hq'], check=True)
        push_only()
