#!/usr/bin/env python3
"""Library of everything we've posted, on every platform: title, length, date, views, link and a saved thumbnail.

  python3 tools/social_scrape.py scrape [--only yt_andrewpreneurship,tt_...]   # yt-dlp accounts (YouTube, TikTok); no API keys
  python3 tools/social_scrape.py import-vidiq <account_key> <file.json>         # Instagram reels fetched by an agent with vidIQ (vidiq_ig_profile_reels)
  python3 tools/social_scrape.py stats

Accounts: library/accounts.json (method yt-dlp | vidiq). Output: library/posts.json (merged, never loses old posts)
and library/thumbs/<platform>/<id>.jpg (320 px wide). This is the data the Lovable app will load into Supabase (table posts).
"""
import io, json, subprocess, sys, datetime as dt
from pathlib import Path
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]; L = ROOT / 'library'; POSTS = L / 'posts.json'
now = lambda: dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')


def load():
    return {p['uid']: p for p in json.loads(POSTS.read_text())} if POSTS.exists() else {}


def save(db):
    rows = sorted(db.values(), key=lambda p: (p['platform'], p['account'], p.get('published') or ''), reverse=True)
    POSTS.write_text(json.dumps(rows, indent=0, ensure_ascii=False))


def thumb(platform, pid, url):
    out = L / 'thumbs' / platform / f'{pid}.jpg'
    if out.exists() or not url: return str(out.relative_to(ROOT)) if out.exists() else None
    try:
        r = requests.get(url, timeout=20); r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert('RGB'); im.thumbnail((320, 568))
        out.parent.mkdir(parents=True, exist_ok=True); im.save(out, 'JPEG', quality=72)
        return str(out.relative_to(ROOT))
    except Exception:
        return None


def ytdlp(acc, db):
    tabs = ['videos', 'shorts', 'streams'] if acc['platform'] == 'youtube' else ['']
    n = 0
    for tab in tabs:
        url = acc['url'].rstrip('/') + (f'/{tab}' if tab else '')
        r = subprocess.run(['yt-dlp', '--flat-playlist', '-J', url], capture_output=True, text=True)
        try: entries = json.loads(r.stdout).get('entries') or []
        except json.JSONDecodeError: print('  failed', url); continue
        for e in entries:
            pid = e['id']; uid = f"{acc['platform']}:{pid}"; old = db.get(uid, {})
            if acc['platform'] == 'youtube':
                kind = {'videos': 'long', 'shorts': 'short', 'streams': 'live'}[tab]; link = f'https://youtu.be/{pid}'
                th = f'https://i.ytimg.com/vi/{pid}/mqdefault.jpg'; title = e.get('title')
            else:
                kind = 'short'; link = e.get('url') or e.get('webpage_url'); title = (e.get('title') or e.get('description') or '').strip()
                th = (e.get('thumbnails') or [{}])[0].get('url')
            ts = e.get('timestamp'); pub = dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime('%Y-%m-%d') if ts else old.get('published')
            db[uid] = {**old, 'uid': uid, 'platform': acc['platform'], 'account': acc['key'], 'id': pid, 'kind': kind, 'title': title, 'url': link,
                       'duration_s': e.get('duration') or old.get('duration_s'), 'published': pub, 'views': e.get('view_count') or old.get('views'),
                       'thumb': old.get('thumb') or thumb(acc['platform'], pid, th), 'seen_at': now()}
            n += 1
    return n


def youtube_dates(db):
    """Flat YouTube lists have no dates: reuse tracker/youtube_channel.json, then fetch the rest (long + live only)."""
    known = {v['id']: v.get('upload_date') for v in json.loads((ROOT / 'tracker/youtube_channel.json').read_text()).get('videos', [])} if (ROOT / 'tracker/youtube_channel.json').exists() else {}
    for p in db.values():
        if p['platform'] != 'youtube' or p.get('published'): continue
        p['published'] = known.get(p['id'])
        if not p['published'] and p['kind'] != 'short':
            r = subprocess.run(['yt-dlp', '--skip-download', '--no-warnings', '--print', '%(upload_date)s', p['url']], capture_output=True, text=True).stdout.strip()
            p['published'] = f'{r[:4]}-{r[4:6]}-{r[6:]}' if len(r) == 8 else None


def num(x):
    import re
    m = re.match(r'([\d.]+)\s*([KM]?)', x or ''); return int(float(m.group(1)) * {'': 1, 'K': 1e3, 'M': 1e6}[m.group(2)]) if m else None


def parse_vidiq_text(raw):
    """Parse the Markdown that vidiq_ig_profile_reels returns ('### <shortcode> — 178.1K plays, …, 72s, posted 2026-05-14')."""
    import re; out = []
    for blk in re.split(r'\n(?=### )', raw):
        m = re.match(r'### (\S+) — ([\d.]+[KM]?) plays.*?(\d+)s, posted (\d{4}-\d{2}-\d{2})', blk)
        if not m: continue
        cap = '\n'.join(l[2:] for l in blk.splitlines() if l.startswith('> ')).strip().strip('"')
        out.append({'shortcode': m.group(1), 'plays': num(m.group(2)), 'duration': int(m.group(3)), 'timestamp': m.group(4), 'caption': cap})
    return out


def import_vidiq(key, path, db):
    acc = next(a for a in json.loads((L / 'accounts.json').read_text()) if a['key'] == key)
    raw = Path(path).read_text()
    try: data = json.loads(raw); reels = data.get('reels') or data.get('items') or data
    except json.JSONDecodeError: reels = parse_vidiq_text(raw)
    for r in reels:
        sc = r.get('shortcode') or r.get('id'); uid = f'instagram:{sc}'; old = db.get(uid, {})
        ts = r.get('timestamp') or r.get('takenAt') or r.get('taken_at')
        pub = ts[:10] if isinstance(ts, str) else dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime('%Y-%m-%d') if ts else old.get('published')
        db[uid] = {**old, 'uid': uid, 'platform': 'instagram', 'account': key, 'id': sc, 'kind': 'reel', 'title': (r.get('caption') or '').strip()[:300],
                   'url': f'https://www.instagram.com/reel/{sc}/', 'duration_s': r.get('duration') or r.get('videoDuration') or old.get('duration_s'), 'published': pub,
                   'views': r.get('playCount') or r.get('plays') or r.get('views') or old.get('views'),
                   'thumb': old.get('thumb') or thumb('instagram', sc, r.get('thumbnailUrl') or r.get('coverUrl') or r.get('thumbnail')), 'seen_at': now()}
    print(f'{len(reels)} reels imported for {key}')


def stats(db):
    from collections import Counter
    c = Counter((p['account'], p['kind']) for p in db.values())
    for (a, k), n in sorted(c.items()): print(f'{a:24} {k:6} {n}')
    print('thumbs saved:', sum(1 for p in db.values() if p.get('thumb')), 'of', len(db))


if __name__ == '__main__':
    a = sys.argv[1:]; db = load()
    if a[0] == 'scrape':
        only = set(a[a.index('--only') + 1].split(',')) if '--only' in a else None
        for acc in json.loads((L / 'accounts.json').read_text()):
            if acc['method'] != 'yt-dlp' or (only and acc['key'] not in only): continue
            print(acc['key'], ytdlp(acc, db)); save(db)
        youtube_dates(db); save(db); stats(db)
    elif a[0] == 'import-vidiq': import_vidiq(a[1], a[2], db); save(db)
    elif a[0] == 'stats': stats(db)
