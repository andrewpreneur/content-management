#!/usr/bin/env python3
"""Posting funnel queue tool (see posting/README.md).
Queue = outputs/planner/plan.json (items). State overlay = posting/state.json {item_id: {status, note, ref, at}}.

  status                      counts per stage
  sync DIR                    merge Content HQ approvals exported with ArtifactData (collection 'approvals')
  lint [--ids a,b]            caption/media problems per item and platform
  next [--days N]             approved items due in the next N days (default 2)
  payloads [--days N]         GHL Social Planner create-post bodies for approved items (dry run, JSON)
  mark ID STATUS [--ref X] [--note Y]
  hub                         compact JSON for Content HQ (queue + stage + captions)
"""
import argparse, json, re, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'outputs/planner/plan.json'
STATE = ROOT / 'posting/state.json'
ACC = json.loads((ROOT / 'posting/accounts.json').read_text())
PLAT = json.loads((ROOT / 'posting/platforms.json').read_text())
SOCIAL = {'instagram', 'facebook', 'linkedin', 'youtube_shorts', 'tiktok'}
SLOP = ['delve', 'game-changer', 'unlock', 'elevate', 'leverage', 'seamless', 'revolutioniz', 'in today\'s fast', 'tapestry', 'unleash']


def load():
    plan = json.loads(PLAN.read_text()); st = json.loads(STATE.read_text()) if STATE.exists() else {}
    return plan, st


def stage(it, st):
    s = st.get(it['id'], {}).get('status')
    if s: return s
    base = it.get('status', 'made')
    return {'rendered': 'needs_approval', 'planned': 'made'}.get(base, base)


def captions(it):
    """Split the planner body into per-platform captions. Body may contain 'LinkedIn:' / 'Threads:' / 'X:' sections."""
    body = (it.get('body') or '').strip()
    parts = re.split(r'\n\s*\n(LinkedIn|Threads|X|TikTok|YouTube):\s*\n', body)
    main = parts[0].strip(); out = {}
    for i in range(1, len(parts) - 1, 2): out[parts[i].lower()] = parts[i + 1].strip()
    main = re.sub(r'\n?\[Attach:[^\]]*\]\s*$', '', main).strip()
    main = re.sub(r'\n\nFiles:.*$', '', main, flags=re.S).strip()
    for p in it['platforms']:
        key = {'youtube_shorts': 'youtube'}.get(p, p)
        out.setdefault(key, main)
    return out


def media_url(it):
    d = it.get('drive') or ''
    m = re.search(r'/d/([A-Za-z0-9_-]{20,})', d) or re.search(r'id=([A-Za-z0-9_-]{20,})', d)
    return f'https://drive.usercontent.google.com/download?id={m.group(1)}&export=download' if m else None


def lint_item(it):
    probs = []; caps = captions(it)
    if it['kind'] != 'story_sequence' and not (it.get('body') or '').strip(): probs.append('no_caption')
    for p in it['platforms']:
        c = caps.get({'youtube_shorts': 'youtube'}.get(p, p), ''); lim = PLAT.get(p, {}).get('caption_max')
        if lim and len(c) > lim: probs.append(f'{p}:too_long({len(c)}>{lim})')
        if p == 'instagram' and c.count('#') > 5: probs.append('instagram:too_many_hashtags')
        if p in ('threads', 'x') and '#' in c: probs.append(f'{p}:hashtags')
        if '—' in c: probs.append(f'{p}:em_dash')
        low = c.lower(); bad = [w for w in SLOP if w in low]
        if bad: probs.append(f'{p}:slop({",".join(bad)})')
    if set(it['platforms']) & SOCIAL and it['kind'] not in ('linkedin_post',) and not media_url(it):
        probs.append('no_media(drive link missing)')
    return probs


def due(items, st, days, only='approved'):
    today = dt.date.today(); end = today + dt.timedelta(days=days)
    return [i for i in items if stage(i, st) == only and today.isoformat() <= i['date'] <= end.isoformat()]


def payload(it):
    caps = captions(it); out = []; url = media_url(it)
    for p in it['platforms']:
        if p in SOCIAL:
            acc = next((a for a in ACC['accounts'] if a['key'] == ACC['route_by_platform'].get(p)), None)
            body = {'type': 'post', 'accountIds': [acc['id']] if acc else [f'<ACCOUNT:{p}>'], 'summary': caps.get({'youtube_shorts': 'youtube'}.get(p, p), ''),
                    'media': [{'url': url, 'type': 'video/mp4' if it['type'] == 'video' else 'image/jpeg'}] if url else [],
                    'status': 'draft', 'scheduleDate': f"{it['date']}T{it['time']}:00-06:00", 'userId': '<GHL_USER_ID>'}
            if p == 'youtube_shorts': body['ytPostDetails'] = {'title': (it.get('hook_plain') or it['title'])[:100], 'privacyLevel': 'public', 'type': 'short'}
            if p == 'instagram' and it['type'] == 'video': body['igPostDetails'] = {'type': 'reel'}
            if acc and not acc.get('active', True): body['_blocked'] = f"account {acc['name']} expired"
            out.append({'item': it['id'], 'platform': p, 'operation': 'create-post', 'body': body})
        else:
            out.append({'item': it['id'], 'platform': p, 'manual': PLAT.get(p, {}).get('via', 'manual'), 'text': caps.get(p, '')})
    return out


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status'); s = sub.add_parser('sync'); s.add_argument('dir')
    l = sub.add_parser('lint'); l.add_argument('--ids')
    n = sub.add_parser('next'); n.add_argument('--days', type=int, default=2)
    p = sub.add_parser('payloads'); p.add_argument('--days', type=int, default=2)
    m = sub.add_parser('mark'); m.add_argument('id'); m.add_argument('status'); m.add_argument('--ref'); m.add_argument('--note')
    sub.add_parser('hub')
    a = ap.parse_args(); plan, st = load(); items = plan['items']
    if a.cmd == 'status':
        from collections import Counter
        c = Counter(stage(i, st) for i in items); print(json.dumps(dict(c), indent=1))
    elif a.cmd == 'sync':
        n = 0
        for f in Path(a.dir).rglob('*.json'):
            d = json.loads(f.read_text()); d = d.get('data', d); iid = d.get('item') or f.stem
            if d.get('status') in ('approved', 'change', 'skip'):
                cur = st.get(iid, {})
                if cur.get('status') in ('scheduled', 'posted'): continue
                st[iid] = {**cur, 'status': d['status'], 'note': d.get('note', ''), 'at': d.get('at')}; n += 1
        STATE.write_text(json.dumps(st, indent=1)); print(f'synced {n}')
    elif a.cmd == 'lint':
        ids = set(a.ids.split(',')) if a.ids else None; bad = 0
        for i in items:
            if ids and i['id'] not in ids: continue
            pr = lint_item(i)
            if pr: bad += 1; print(i['id'], '|', '; '.join(pr))
        print(f'# {bad} items with problems of {len(items)}', file=sys.stderr)
    elif a.cmd == 'next':
        for i in sorted(due(items, st, a.days), key=lambda x: (x['date'], x['time'])): print(i['date'], i['time'], i['id'], ','.join(i['platforms']), '|', i['title'])
    elif a.cmd == 'payloads':
        print(json.dumps([x for i in due(items, st, a.days) for x in payload(i)], indent=1))
    elif a.cmd == 'mark':
        st[a.id] = {**st.get(a.id, {}), 'status': a.status, **({'ref': a.ref} if a.ref else {}), **({'note': a.note} if a.note else {}), 'at': dt.datetime.utcnow().isoformat() + 'Z'}
        STATE.write_text(json.dumps(st, indent=1)); print('ok', a.id, a.status)
    elif a.cmd == 'hub':
        out = [{'id': i['id'], 'd': i['date'], 't': i['time'], 'k': i['kind'], 'ty': i['type'], 'ti': i['title'], 'pl': i['platforms'], 'st': stage(i, st),
                'cap': captions(i), 'th': i.get('thumb'), 'dr': i.get('drive'), 'rv': i.get('review'), 'src': i.get('source'), 'lint': lint_item(i)} for i in items]
        print(json.dumps(out, separators=(',', ':')))


if __name__ == '__main__':
    main()
