#!/usr/bin/env python3
"""Two-way sync between this repo and Your Content System (Supabase project rchfmtgkfnnyzpbmyxrm, app repo content-hq).

  python3 tools/ycs_sync.py pull     # Andrew's taps from the app -> posting/state.json + tracker/marks.json
  python3 tools/ycs_sync.py push     # repo data (library, queue, tracker) -> the app (never touches approvals)
  python3 tools/ycs_sync.py all      # pull, rebuild tracker, push   (what the weekly task runs)

Talks to the app's `ingest` Edge Function with the engine key: $YCS_INGEST_KEY, else ~/.ycs_ingest_key, else it is read
once from the project's Vault through the Supabase Management API (the cloud proxy injects that token) and cached in
~/.ycs_ingest_key (never printed). $YCS_BRAND picks the brand this repo feeds (default andrewpreneurship).
"""
import json, os, subprocess, sys, tempfile, time, datetime as dt
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1]
PROJECT = os.environ.get('YCS_PROJECT', 'rchfmtgkfnnyzpbmyxrm')
URL = os.environ.get('YCS_INGEST_URL', f'https://{PROJECT}.supabase.co/functions/v1/ingest')
KEYF = Path.home() / '.ycs_ingest_key'
BRAND = os.environ.get('YCS_BRAND', 'andrewpreneurship')   # which brand in the app this repo feeds


def key():
    k = os.environ.get('YCS_INGEST_KEY', '').strip()
    if k: return k
    if not KEYF.exists():
        r = requests.post(f'https://api.supabase.com/v1/projects/{PROJECT}/database/query', headers={'Authorization': 'Bearer proxy-injected'},
                          json={'query': "select decrypted_secret as k from vault.decrypted_secrets where name = 'ycs_ingest_secret'"}, timeout=60)
        if r.status_code >= 300 or not r.json(): sys.exit('No engine key: set YCS_INGEST_KEY (ask the app admin).')
        KEYF.write_text(r.json()[0]['k']); KEYF.chmod(0o600)
    return KEYF.read_text().strip()


# Old Convex function names -> ingest actions (so the other tools keep calling call(kind, path, args)).
ACTIONS = {'queue:allApprovals': 'allApprovals', 'youtube:manualMarks': 'manualMarks', 'styles:forEngine': 'forEngine',
           'styles:seedBrand': 'seedBrand', 'ingest:replace': 'replace', 'ingest:finish': 'finish',
           'ingest:replaceGlobal': 'replaceGlobal', 'ingest:uploadUrl': 'uploadUrl'}


def call(kind, path, args):
    """Run one ingest action in the app (kind is ignored; kept for the older callers)."""
    action = ACTIONS.get(path, path)
    for i in range(4):
        try:
            r = requests.post(URL, json={'action': action, 'args': args}, headers={'x-ingest-secret': key()}, timeout=300)
            j = r.json() if r.text else {}
            if r.ok and 'result' in j: return j['result']
            if r.status_code < 500: sys.exit(f'{action} failed: {str(j)[:600]}')
            if i == 3: sys.exit(f'{action} failed: {str(j)[:600]}')
        except requests.RequestException:
            if i == 3: raise
        time.sleep(2 ** i)


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


def ingest(table, rows, max_bytes=2_000_000):
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
