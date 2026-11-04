#!/usr/bin/env python3
"""DRY RUN ONLY: turn approved reviews into GHL Social Planner create-post payloads and print them.
It never calls the API. Posting live stays a manual, Andrew-approved step (docs/sops/05-posting.md).

Usage:
  python3 tools/ghl_post.py --reviews REVIEWS --run outputs/2026-11-04-switchyard [--run ...]
        [--accounts config/ghl_accounts.json] [--media-base https://<public host>/<path>] [--status draft]

REVIEWS: the review page's `reviews` collection, exported with ArtifactData
  (action "list", collection "reviews", out_dir work/reviews) -> a directory of <id>.json files,
  or a single JSON file {"<run>__<key>": {"status": "approved", "note": ""}, ...}.
Only status "approved" is used. "change" / "rejected" / "pending" are skipped and listed.

Payload shape = GHL `POST /social-media-posting/{locationId}/posts` (operation create-post):
  one request per platform so each keeps its own caption length.
Account ids come from --accounts ({"instagram": "<accountId>", ...}); missing ones print as <ACCOUNT_ID:platform>.
Media URLs must be public (Drive/R2); --media-base + file name, else <MEDIA_URL:file>.
"""
import argparse, json, re
from pathlib import Path

TYPES = {  # platform -> (post type, extra platform block builder)
    'instagram': 'ig', 'facebook': 'fb', 'tiktok': 'tt', 'youtube_shorts': 'yt', 'youtube': 'yt',
    'threads': 'plain', 'linkedin': 'li', 'x': 'plain',
}
NOT_SOCIAL = {'ghl_email': 'GHL email campaign (not Social Planner)', 'substack': 'Substack (manual)',
              'saassuite_community': 'GHL Communities post (manual for now)', 'podcast': 'RSS.com (manual / API on Network plan)',
              'instagram_trial': 'Instagram app → Trial reel (not in API)', 'all_es': 'captions file, attach to the Spanish reel'}


def load_reviews(p):
    p = Path(p)
    if p.is_dir():
        out = {}
        for f in p.rglob('*.json'):
            d = json.loads(f.read_text()); out[f.stem] = d.get('data', d)
        return out
    return json.loads(p.read_text())


def section(md, title_prefix):
    m = re.search(rf"^## {re.escape(title_prefix)}[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else None


def body_text(path):
    lines = [l for l in Path(path).read_text().splitlines() if not l.startswith('# ') and not l.startswith('_')]
    return '\n'.join(lines).strip()


def caption_for(run_dir, o):
    caps = (run_dir / 'text' / 'reel-captions.md')
    md = caps.read_text() if caps.exists() else ''
    k, t = o['key'], o['output_type']
    if t in ('linkedin_post', 'threads_post', 'x_thread', 'email', 'substack'):
        return body_text(o['file'])
    if k.startswith('reedit'):
        return section(md, f'Re-edit {k[-1]}') or section(md, 'Master')
    return section(md, 'Master')


def payload(platform, o, caption, media, a):
    acc = a.accounts.get(platform) or f'<ACCOUNT_ID:{platform}>'
    is_video = any(m['type'].startswith('video') for m in media)
    ptype = 'story' if o['output_type'] == 'story_sequence' else ('reel' if is_video and platform in ('instagram', 'facebook', 'tiktok') else 'post')
    p = {'accountIds': [acc], 'summary': '' if ptype == 'story' else caption, 'media': media, 'type': ptype,
         'status': a.status, 'userId': a.user_id or '<GHL_USER_ID>'}
    if a.status in ('scheduled', 'in_review'):
        p['scheduleDate'] = '<ISO_DATETIME>'
    kind = TYPES.get(platform)
    if kind == 'ig':
        p['instagramPostDetails'] = {'type': ptype}
    elif kind == 'fb':
        p['facebookPostDetails'] = {'type': ptype}
    elif kind == 'tt':
        p['tiktokPostDetails'] = {'privacyLevel': 'PUBLIC_TO_EVERYONE', 'enableComment': True}
    elif kind == 'yt':
        p['youtubePostDetails'] = {'type': 'short' if platform == 'youtube_shorts' else 'video', 'privacyLevel': 'public',
                                   'title': (caption.splitlines()[0] if caption else o['key'])[:100]}
    elif kind == 'li' and o['output_type'] == 'carousel':
        p['linkedinPostDetails'] = {'postAsPdf': True, 'pdfTitle': 'Carousel'}
    if platform == 'x' and o['output_type'] == 'x_thread':
        p['_note'] = 'X is not in GHL Social Planner yet; post via Blotato or manually. Thread split below.'
        p['_thread'] = [s.strip() for s in re.split(r'\n(?=\d+/ )', caption) if s.strip()]
    return {'method': 'POST', 'path': '/social-media-posting/{locationId}/posts', 'body': p}


def media_for(run_dir, o, base):
    f = o.get('file') or ''
    def url(name):
        return f"{base.rstrip('/')}/{run_dir.name}/{name}" if base else f'<MEDIA_URL:{run_dir.name}/{name}>'
    if f.endswith('.mp4'):
        return [{'url': url(Path(f).name), 'type': 'video/mp4'}]
    if o['output_type'] == 'carousel':
        return [{'url': url(p.name), 'type': 'image/png'} for p in sorted(Path(f).parent.glob('slide-*.png'))]
    if o['output_type'] == 'story_sequence':
        return [{'url': url(p.name), 'type': 'image/png'} for p in sorted(Path(f).parent.glob('frame-*.png'))]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reviews', required=True); ap.add_argument('--run', action='append', required=True)
    ap.add_argument('--accounts'); ap.add_argument('--media-base'); ap.add_argument('--user-id')
    ap.add_argument('--status', default='draft', choices=['draft', 'scheduled', 'in_review'])
    a = ap.parse_args()
    a.accounts = json.loads(Path(a.accounts).read_text()) if a.accounts else {}
    reviews = load_reviews(a.reviews)
    out, skipped, manual = [], [], []
    for rd in a.run:
        rd = Path(rd); spec = json.loads((rd / 'manifest_spec.json').read_text())
        for o in spec['outputs']:
            rid = f"{rd.name}__{o['key']}"; rv = reviews.get(rid, {})
            if rv.get('status') != 'approved':
                skipped.append(f"{rid}: {rv.get('status', 'no review')}"); continue
            cap = caption_for(rd, o) or ''
            media = media_for(rd, o, a.media_base)
            for pl in o.get('platforms', []):
                if pl in NOT_SOCIAL or pl.endswith('_es') or pl.endswith('_stories'):
                    if pl.endswith('_stories'):
                        out.append({'output': rid, 'platform': pl, 'request': payload(pl.split('_')[0], o, '', media, a)})
                    else:
                        manual.append(f"{rid} → {pl}: {NOT_SOCIAL.get(pl, 'language page not connected yet')}")
                    continue
                out.append({'output': rid, 'platform': pl, 'request': payload(pl, o, cap, media, a)})
    print(json.dumps({'DRY_RUN': True, 'note': 'Nothing was sent. Review, then post via GHL with Andrew\'s OK.',
                      'payloads': out, 'manual_steps': manual, 'skipped_not_approved': skipped}, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
