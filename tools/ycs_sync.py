#!/usr/bin/env python3
"""Two-way sync between this repo and Your Content System (Convex deployment harmless-ibis-268, app repo content-hq).

  python3 tools/ycs_sync.py pull     # Andrew's taps from the app -> posting/state.json + tracker/marks.json
  python3 tools/ycs_sync.py push     # repo data (library, queue, tracker) -> Convex (never touches approvals)
  python3 tools/ycs_sync.py all      # pull, rebuild tracker, push   (what the weekly task runs)

Needs: a content-hq checkout (default ../content-hq, or $CONTENT_HQ) with node deps, and a Convex deploy key in
~/.convex_deploy_key. If the key file is missing, one is created through the Convex management API with the team
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


def convex(*args, capture=False):
    env = {**os.environ, 'CONVEX_DEPLOY_KEY': key()}
    r = subprocess.run(['npx', 'convex', *args], cwd=HQ, env=env, capture_output=True, text=True)
    if r.returncode: sys.exit(f'convex {args[0]} failed: {r.stderr[-800:]}')
    return r.stdout


def run_query(fn):
    out = convex('run', fn, '{}')
    return json.loads(out[out.index('['):]) if '[' in out else []


def pull():
    st_path = R / 'posting/state.json'; st = json.loads(st_path.read_text()) if st_path.exists() else {}
    n = 0
    for a in run_query('queue:allApprovals'):
        cur = st.get(a['itemId'], {})
        if cur.get('status') in ('scheduled', 'posted'): continue
        if cur.get('status') == a['status'] and cur.get('note', '') == a.get('note', ''): continue
        st[a['itemId']] = {**cur, 'status': a['status'], 'note': a.get('note', ''), 'at': a['at'], 'via': 'app'}; n += 1
    st_path.write_text(json.dumps(st, indent=1))
    mk_path = R / 'tracker/marks.json'; mk = json.loads(mk_path.read_text()) if mk_path.exists() else {}
    m = 0
    for r in run_query('youtube:manualMarks'):
        mk[r['driveId']] = {'status': r['status'], 'yt': r.get('youtubeId'), 'note': r.get('reason', ''), 'at': r.get('markedAt')}; m += 1
    mk_path.write_text(json.dumps(mk, indent=1))
    print(f'pulled {n} new approvals, {m} manual upload marks')


def push_only():
    d = Path(tempfile.mkdtemp(prefix='ycs_'))
    subprocess.run([sys.executable, str(R / 'tools/export_convex.py'), str(d)], check=True)
    for t in ('accounts', 'posts', 'planItems', 'driveVideos', 'syncRuns'):
        convex('import', '--table', t, str(d / f'{t}.jsonl'), '--replace', '-y')
    print('pushed accounts, posts, planItems, driveVideos, syncRuns')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    ensure_hq()
    pull()                       # every command starts by saving Andrew's taps into the repo
    if cmd in ('push', 'all'):
        subprocess.run([sys.executable, str(R / 'tools/yt_tracker.py'), 'match'], check=True)   # applies marks.json
        subprocess.run([sys.executable, str(R / 'tools/yt_tracker.py'), 'hq'], check=True)
        push_only()
