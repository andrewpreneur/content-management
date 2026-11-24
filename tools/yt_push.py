#!/usr/bin/env python3
"""Send a video file to a YouTube resumable upload link at full speed (from a Supercomputer / any runner).
  python3 tools/yt_push.py --session "<https://www.googleapis.com/upload/youtube/...>" --file video.mp4 [--piece-mb 64]
The app opens the upload (title, description, privacy) through the customer's Drive script and hands the runner the link;
the link itself is the permission, so no Google login is needed here. Resumes from what YouTube already has.
Prints {"videoId": "..."} when done. Exit code 1 if YouTube refuses."""
import argparse, json, sys, time, urllib.request, urllib.error
from pathlib import Path


def put(url, headers, body=None):
    req = urllib.request.Request(url, data=body if body is not None else b'', method='PUT', headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=600) as r: return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def confirmed(session, size):
    code, h, body = put(session, {'Content-Range': f'bytes */{size}', 'Content-Length': '0'})
    if code in (200, 201): return size, json.loads(body or b'{}').get('id')
    if code == 308:
        rg = h.get('Range') or h.get('range'); return (int(rg.split('-')[1]) + 1 if rg else 0), None
    sys.exit(f'YouTube refused the upload link: {code} {body[:300]!r}')


def main():
    a = argparse.ArgumentParser(); a.add_argument('--session', required=True); a.add_argument('--file', required=True); a.add_argument('--piece-mb', type=int, default=64)
    o = a.parse_args()
    if not o.session.startswith('https://www.googleapis.com/upload/youtube/'): sys.exit('not a YouTube upload link')
    f = Path(o.file); size = f.stat().st_size; P = o.piece_mb * 1024 * 1024 // (256 * 1024) * (256 * 1024)
    off, vid = confirmed(o.session, size); t0 = time.time(); start = off
    with open(f, 'rb') as fh:
        while vid is None and off < size:
            fh.seek(off); b = fh.read(min(P, size - off))
            for attempt in range(6):
                code, h, body = put(o.session, {'Content-Range': f'bytes {off}-{off + len(b) - 1}/{size}', 'Content-Type': 'application/octet-stream'}, b)
                if code in (200, 201): vid = json.loads(body or b'{}').get('id'); off = size; break
                if code == 308:
                    rg = h.get('Range') or h.get('range'); off = int(rg.split('-')[1]) + 1 if rg else off; break
                if code >= 500 or code == 429:
                    time.sleep(2 ** attempt); off, vid = confirmed(o.session, size); break
                print(json.dumps({'error': f'YouTube stopped the upload: {code} {body[:300]!r}'})); sys.exit(1)
            print(f'  {off / 1e6:.0f}/{size / 1e6:.0f} MB, {(off - start) / 1e6 / max(time.time() - t0, 0.1):.1f} MB/s', file=sys.stderr, flush=True)
    print(json.dumps({'videoId': vid, 'bytes': size, 'seconds': round(time.time() - t0)}))


if __name__ == '__main__':
    main()
