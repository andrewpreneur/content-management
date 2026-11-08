#!/usr/bin/env python3
"""Send a content to-do / message to Ysa (Your Software Agent) through Andrew's webhook.

Env (set in the cloud environment settings, never in code or chat):
  YSA_WEBHOOK_URL     the webhook URL
  YSA_WEBHOOK_SECRET  the signing secret
Signing: HMAC-SHA256 over "<timestamp>.<raw JSON body>", sent as
  X-Ysa-Timestamp: <unix seconds>
  X-Ysa-Signature: sha256=<hex digest>
(change SIG_* below if Ysa expects a different scheme)

Usage:
  python3 tools/notify_ysa.py needs_input "Pick a voice for the Skool VSLs" --link https://claude.ai/artifact/... [--due 2026-11-09]
  python3 tools/notify_ysa.py for_ysa "Send the LevelUp post 2 pack to Andrew" --link ...
  python3 tools/notify_ysa.py todo "..."      # any content to-do
  --dry-run prints the payload without sending.
"""
import argparse, hashlib, hmac, json, os, sys, time, urllib.request

SIG_HEADER, TS_HEADER = 'X-Ysa-Signature', 'X-Ysa-Timestamp'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kind', choices=['needs_input', 'for_ysa', 'todo', 'done'])
    ap.add_argument('text')
    ap.add_argument('--link', action='append', default=[])
    ap.add_argument('--due')
    ap.add_argument('--priority', default='normal', choices=['low', 'normal', 'high'])
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    body = dict(source='claude-content-engine', kind=a.kind, text=a.text, links=a.link, due=a.due,
                priority=a.priority, repo='andrewpreneur/content-management', at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    raw = json.dumps(body, ensure_ascii=False).encode()
    if a.dry_run:
        print(raw.decode()); return
    url, secret = os.environ.get('YSA_WEBHOOK_URL'), os.environ.get('YSA_WEBHOOK_SECRET')
    if not url or not secret:
        sys.exit('YSA_WEBHOOK_URL / YSA_WEBHOOK_SECRET not set in this environment yet')
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f'{ts}.'.encode() + raw, hashlib.sha256).hexdigest()
    req = urllib.request.Request(url, data=raw, method='POST', headers={'Content-Type': 'application/json', TS_HEADER: ts, SIG_HEADER: f'sha256={sig}'})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(r.status, r.read(300).decode(errors='replace'))


if __name__ == '__main__':
    main()
