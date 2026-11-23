#!/usr/bin/env python3
"""Serve any Drive file over local HTTP with Range support, read through the Drive script (`read` action, 8 MB pieces).
  python3 tools/drive_range_proxy.py [--port 8765] &     then use http://127.0.0.1:8765/<driveId> with ffmpeg/ffprobe.
Needs DRIVE_UPLOAD_URL / DRIVE_UPLOAD_SECRET (the Drive script, v4+ so it can read any file you can open)."""
import argparse, base64, importlib.util, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
spec = importlib.util.spec_from_file_location('du', Path(__file__).with_name('drive_upload.py')); du = importlib.util.module_from_spec(spec); spec.loader.exec_module(du)
P = 8388608; cache = {}; order = []; lock = threading.Lock(); sizes = {}


def piece(fid, i):
    k = (fid, i)
    with lock:
        if k in cache: return cache[k]
    r = du.call(dict(action='read', id=fid, offset=i * P, length=P), tries=6); b = base64.b64decode(r['data'])
    with lock:
        cache[k] = b; order.append(k)
        while len(order) > 12: cache.pop(order.pop(0), None)
    return b


def size(fid):
    if fid not in sizes: sizes[fid] = int(du.call(dict(action='meta', id=fid))['size'])
    return sizes[fid]


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_HEAD(self): self.go(False)
    def do_GET(self): self.go(True)

    def go(self, body):
        fid = self.path.strip('/'); n = size(fid); a, b = 0, n - 1; rg = self.headers.get('Range')
        if rg and rg.startswith('bytes='):
            s, e = rg[6:].split('-'); a = int(s or 0); b = int(e) if e else n - 1
        self.send_response(206 if rg else 200)
        self.send_header('Content-Type', 'video/mp4'); self.send_header('Accept-Ranges', 'bytes'); self.send_header('Content-Length', str(b - a + 1))
        if rg: self.send_header('Content-Range', f'bytes {a}-{b}/{n}')
        self.end_headers()
        if not body: return
        pos = a
        try:
            while pos <= b:
                i = pos // P; d = piece(fid, i); chunk = d[pos - i * P: pos - i * P + (b - pos + 1)]
                if not chunk: break
                self.wfile.write(chunk); pos += len(chunk)
        except (BrokenPipeError, ConnectionResetError): pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--port', type=int, default=8765)
    ThreadingHTTPServer(('127.0.0.1', ap.parse_args().port), H).serve_forever()
