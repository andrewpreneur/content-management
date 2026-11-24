#!/usr/bin/env python3
"""Upload files to Andrew's Drive (_ENGINE / 02-review / <folder>) through the Apps Script uploader (tools/drive_uploader.gs).

Env (cloud environment settings): DRIVE_UPLOAD_URL (the web app URL), DRIVE_UPLOAD_SECRET (same as the script's UPLOAD_SECRET).
Usage:
  python3 tools/drive_upload.py ping
  python3 tools/drive_upload.py put "2026-11-09 VSL finals" file1.mp4 file2.mp4 ...   # a name already there → saved as "name (2).mp4"
  python3 tools/drive_upload.py put --skip-existing "folder" file.mp4                 # old behaviour: keep the file that's there
Agents: give finished videos a descriptive name ("<Brand> - <title> - <date>.mp4"), never a generic "explainer.mp4", and report
the id this prints (it's always the file you just uploaded, unless --skip-existing).
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


def direct(session, path, size, name, piece=64 * 1024 * 1024):
    """Send the bytes straight to Drive's resumable upload link (the link is the permission; no token needed). Much faster than the relay."""
    if not str(session).startswith('https://www.googleapis.com/upload/drive/'): raise RuntimeError('not a Drive upload session')
    off = 0
    with open(path, 'rb') as f:
        while off < size:
            f.seek(off); buf = f.read(piece); end = off + len(buf) - 1
            for i in range(5):
                try:
                    r = requests.put(session, data=buf, headers={'Content-Range': f'bytes {off}-{end}/{size}'}, timeout=600); break
                except requests.RequestException:
                    if i == 4: raise
                    time.sleep(2 ** i)
            if r.status_code in (200, 201):
                fid = r.json().get('id'); url = f'https://drive.google.com/file/d/{fid}/view'
                print('uploaded', name, url); return url
            if r.status_code != 308: raise RuntimeError(f'Drive said {r.status_code}: {r.text[:200]}')
            rng = r.headers.get('Range'); off = int(rng.split('-')[1]) + 1 if rng else off
    raise RuntimeError('upload did not finish')


def put(folder, path, unique=False):
    """unique=False (engine syncs): a name already in the folder is kept and returned. unique=True (CLI, agents): the new file is
    saved as "name (2).ext", "(3)"… so a generic name can never hand back somebody else's older file."""
    size = os.path.getsize(path); name = os.path.basename(path)
    mt = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    stem, ext = os.path.splitext(name)
    for n in range(1, 30):
        try_name = name if n == 1 else f'{stem} ({n}){ext}'
        s = call(dict(action='start', path=folder, name=try_name, mimeType=mt, size=size))
        if not s.get('skipped'): name = try_name; break
        if not unique:
            print('exists', name, s['url']); return s['url']
    else:
        raise RuntimeError('too many files with this name: ' + name)
    try:
        return direct(s['session'], path, size, name)
    except Exception as e:  # network blocks googleapis.com, or the session refuses: fall back to the script relay
        print('direct upload failed, using the script relay:', str(e)[:200])
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
        args = sys.argv[2:]; skip = '--skip-existing' in args; args = [a for a in args if a != '--skip-existing']
        for p in args[1:]:
            put(args[0], p, unique=not skip)
