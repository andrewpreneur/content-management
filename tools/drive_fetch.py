#!/usr/bin/env python3
"""Download a Drive file fast through the Drive script (`read`, 8 MB pieces, many at once). Any size, any owner.
  python3 tools/drive_fetch.py <driveId> <out.mp4> [--workers 24]
Measured ~11 MB/s with 24 workers (a 2 GB 4K master in ~3 min) vs ~1.5 MB/s one piece at a time.
Writes in place (no second copy on disk); resumes from <out>.done if a run stops. Needs DRIVE_UPLOAD_URL / DRIVE_UPLOAD_SECRET."""
import argparse, base64, importlib.util, sys, threading, time, concurrent.futures as cf
from pathlib import Path
spec = importlib.util.spec_from_file_location('du', Path(__file__).with_name('drive_upload.py')); du = importlib.util.module_from_spec(spec); spec.loader.exec_module(du)
P = 8388608


def main():
    a = argparse.ArgumentParser(); a.add_argument('id'); a.add_argument('out'); a.add_argument('--workers', type=int, default=24)
    o = a.parse_args()
    meta = du.call(dict(action='meta', id=o.id))
    if not meta.get('ok'): sys.exit(f"Drive script: {meta.get('error')}")
    size = int(meta['size']); n = (size + P - 1) // P
    out = Path(o.out); log = Path(str(out) + '.done')    # pieces already written (so a stopped run resumes)
    have = set(int(x) for x in log.read_text().split()) if log.exists() and out.exists() else set()
    with open(out, 'r+b' if out.exists() else 'w+b') as fh: fh.truncate(size)   # sparse file at full size, no second copy
    t0 = time.time(); lock = threading.Lock(); done = [len(have)]

    def get(i):
        if i in have: return
        want = min(P, size - i * P)
        r = du.call(dict(action='read', id=o.id, offset=i * P, length=want), tries=8)
        b = base64.b64decode(r['data'])
        if len(b) != want: raise RuntimeError(f'piece {i}: got {len(b)} bytes, wanted {want}')
        with lock:
            with open(out, 'r+b') as fh: fh.seek(i * P); fh.write(b)
            with open(log, 'a') as lg: lg.write(f'{i}\n')
            done[0] += 1
            if done[0] % 25 == 0: print(f'  {done[0]}/{n} pieces, {done[0] * P / 1e6 / (time.time() - t0):.1f} MB/s', flush=True)

    with cf.ThreadPoolExecutor(o.workers) as ex:
        for fut in cf.as_completed([ex.submit(get, i) for i in range(n)]): fut.result()
    log.unlink(missing_ok=True)
    dt = time.time() - t0
    print(f'wrote {out} ({size / 1e6:.0f} MB, {meta.get("name")}) in {dt:.0f} s, {size / 1e6 / max(dt, 0.1):.1f} MB/s')


if __name__ == '__main__':
    main()
