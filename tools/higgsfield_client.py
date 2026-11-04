#!/usr/bin/env python3
"""Minimal Higgsfield API client (image / video generation), with a dry-run mode and a spend cap.

Auth: header `Authorization: Key <key_id>:<key_secret>`.
  Env: HIGGSFIELD_API_KEY="<key_id>:<key_secret>"  (or HIGGSFIELD_KEY_ID + HIGGSFIELD_KEY_SECRET)
  Host: HIGGSFIELD_HOST (default https://platform.higgsfield.ai)
  In a Claude cloud session the proxy may inject the header for you; then any dummy key works.

Usage:
  python3 tools/higgsfield_client.py test                       # auth check (no credits spent)
  python3 tools/higgsfield_client.py submit MODEL_PATH payload.json [--dry-run] [--wait] [--out DIR]
  python3 tools/higgsfield_client.py status REQUEST_ID
Examples of MODEL_PATH: higgsfield-ai/soul/standard (image), check the Higgsfield docs/models list for video.

RULES (docs/ai-video-rules.md): only rule 1–4 uses. Never a full-frame AI talking head.
Spend: every submit is logged to logs/higgsfield-spend.jsonl; set HIGGSFIELD_MAX_SUBMITS (default 20) per run.
"""
import argparse, json, os, sys, time, datetime
from pathlib import Path

HOST = os.environ.get('HIGGSFIELD_HOST', 'https://platform.higgsfield.ai').rstrip('/')
LOG = Path(__file__).resolve().parent.parent / 'logs' / 'higgsfield-spend.jsonl'


def key():
    k = os.environ.get('HIGGSFIELD_API_KEY')
    if not k and os.environ.get('HIGGSFIELD_KEY_ID'):
        k = f"{os.environ['HIGGSFIELD_KEY_ID']}:{os.environ.get('HIGGSFIELD_KEY_SECRET', '')}"
    return k or 'dummy:dummy'  # proxy-injected auth replaces this


def headers():
    return {'Authorization': f'Key {key()}', 'Content-Type': 'application/json', 'Accept': 'application/json'}


def masked():
    k = key(); return '(dummy — proxy-injected)' if k.startswith('dummy') else k[:4] + '…'


def req(method, path, body=None, dry=False):
    url = f"{HOST}/{path.lstrip('/')}"
    if dry:
        print(json.dumps({'DRY_RUN': True, 'method': method, 'url': url,
                          'headers': {'Authorization': f'Key {masked()}'}, 'body': body}, indent=1))
        return None
    import requests
    r = requests.request(method, url, headers=headers(), json=body, timeout=60)
    try:
        data = r.json()
    except ValueError:
        data = {'text': r.text[:500]}
    if r.status_code >= 400:
        raise SystemExit(f"Higgsfield {r.status_code}: {data}")
    return data


def cmd_test(_):
    """Auth check: a status lookup of a nil request id. 401 = bad key; 404/422 = key works."""
    import requests
    r = requests.get(f"{HOST}/requests/00000000-0000-0000-0000-000000000000/status", headers=headers(), timeout=30)
    ok = r.status_code not in (401, 403)
    print(f"{'OK' if ok else 'AUTH FAILED'} — HTTP {r.status_code} from {HOST} — {r.text[:200]}")
    sys.exit(0 if ok else 1)


def cmd_submit(a):
    body = json.loads(Path(a.payload).read_text())
    cap = int(os.environ.get('HIGGSFIELD_MAX_SUBMITS', '20'))
    spent = sum(1 for _ in LOG.open()) if LOG.exists() else 0
    if not a.dry_run and spent >= cap:
        raise SystemExit(f"Spend cap reached ({spent}/{cap} submits logged). Raise HIGGSFIELD_MAX_SUBMITS deliberately.")
    res = req('POST', a.model, body, dry=a.dry_run)
    if a.dry_run:
        return
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open('a') as f:
        f.write(json.dumps({'at': datetime.datetime.utcnow().isoformat() + 'Z', 'model': a.model, 'response': res}) + '\n')
    print(json.dumps(res, indent=1))
    rid = (res or {}).get('request_id') or (res or {}).get('id')
    if a.wait and rid:
        wait_and_fetch(rid, a.out)


def wait_and_fetch(rid, out=None, every=5, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = req('GET', f'requests/{rid}/status')
        st = (s.get('status') or '').lower()
        print('status:', st)
        if st in ('completed', 'succeeded', 'success'):
            urls = []
            for k in ('images', 'videos', 'outputs'):
                for it in s.get(k) or []:
                    urls.append(it.get('url') if isinstance(it, dict) else it)
            if s.get('video', {}) and isinstance(s['video'], dict):
                urls.append(s['video'].get('url'))
            if out:
                import requests
                Path(out).mkdir(parents=True, exist_ok=True)
                for i, u in enumerate(filter(None, urls)):
                    p = Path(out) / f"{rid}_{i}{Path(u.split('?')[0]).suffix or '.bin'}"
                    p.write_bytes(requests.get(u, timeout=120).content); print('saved', p)
            print(json.dumps(s, indent=1)); return s
        if st in ('failed', 'error', 'nsfw', 'cancelled'):
            raise SystemExit(f"Generation {st}: {s}")
        time.sleep(every)
    raise SystemExit('Timed out waiting for Higgsfield')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('test')
    s = sub.add_parser('submit'); s.add_argument('model'); s.add_argument('payload')
    s.add_argument('--dry-run', action='store_true'); s.add_argument('--wait', action='store_true'); s.add_argument('--out')
    st = sub.add_parser('status'); st.add_argument('request_id')
    a = ap.parse_args()
    if a.cmd == 'test':
        cmd_test(a)
    elif a.cmd == 'submit':
        cmd_submit(a)
    else:
        print(json.dumps(req('GET', f'requests/{a.request_id}/status'), indent=1))


if __name__ == '__main__':
    main()
