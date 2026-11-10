#!/usr/bin/env python3
"""Upload files to Andrew's Drive (_ENGINE / 02-review / <folder>) through the Apps Script uploader (tools/drive_uploader.gs).

Env (cloud environment settings): DRIVE_UPLOAD_URL (the web app URL), DRIVE_UPLOAD_SECRET (same as the script's UPLOAD_SECRET).
Usage:
  python3 tools/drive_upload.py ping
  python3 tools/drive_upload.py put "2026-11-09 VSL finals" file1.mp4 file2.mp4 ...   # skips names already in that folder
Files are sent in 8 MB pieces, so any size works.
"""
import base64, json, mimetypes, os, sys, time
import requests

CHUNK = 8 * 1024 * 1024  # multiple of 256 KB, as Drive requires


def call(payload, tries=4):
    url, secret = os.environ.get('DRIVE_UPLOAD_URL'), os.environ.get('DRIVE_UPLOAD_SECRET')
    if not url or not secret:
        sys.exit('DRIVE_UPLOAD_URL / DRIVE_UPLOAD_SECRET are not set in this environment')
    payload = dict(payload, secret=secret)
    for i in range(tries):
        try:
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'text/plain'}, timeout=300)
            j = r.json()
            if j.get('ok'):
                return j
            err = j.get('error')
        except Exception as e:  # network blip or non-JSON page
            err = str(e)[:200]
        time.sleep(2 ** i)
    raise RuntimeError(err)


def put(folder, path):
    size = os.path.getsize(path); name = os.path.basename(path)
    mt = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    s = call(dict(action='start', path=folder, name=name, mimeType=mt, size=size))
    if s.get('skipped'):
        print('exists', name, s['url']); return s['url']
    off = 0
    with open(path, 'rb') as f:
        while off < size:
            buf = f.read(CHUNK)
            r = call(dict(action='chunk', session=s['session'], offset=off, size=size, data=base64.b64encode(buf).decode()))
            if r.get('done'):
                print('uploaded', name, r['url']); return r['url']
            off = r['next']
    raise RuntimeError('upload did not finish: ' + name)


if __name__ == '__main__':
    if sys.argv[1] == 'ping':
        print(call(dict(action='ping')))
    elif sys.argv[1] == 'put':
        for p in sys.argv[3:]:
            put(sys.argv[2], p)
