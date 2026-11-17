#!/usr/bin/env python3
"""Map every queued post (outputs/planner/plan.json) to its finished file(s) in Google Drive -> posting/media.json.

Usage:
  python3 tools/media_map.py                 # rebuild posting/media.json from the inventory + upload log (no network)
  python3 tools/media_map.py --upload        # also upload local files that are not in Drive yet (tools/drive_upload.py)
  python3 tools/media_map.py --upload --kind podcast_clip   # only one kind

Inputs:
  posting/drive_inventory.json  Drive listing of _ENGINE (refresh with the Google Drive MCP, see posting/media-README.md)
  posting/drive_uploads.json    what this script uploaded: local path -> {driveId, name, folder, sizeBytes, mimeType, status}
Local renders: /home/user/work/formats/<clip>/<clip>-<vN>.mp4 (podcast clips), /home/user/work/carousels/<clip>/<fmt>/slide-NN.png
(carousel formats + text cards), outputs/** (catalog, text-pack carousels). Uploads go to _ENGINE/02-review/<folder>.
"""
import argparse, json, mimetypes, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = Path('/home/user/work')
INV = ROOT / 'posting/drive_inventory.json'
UPL = ROOT / 'posting/drive_uploads.json'
OUT = ROOT / 'posting/media.json'
MEDIA_KINDS = ('podcast_clip', 'reel', 'carousel', 'single_image', 'text_card', 'story_sequence')
V8_REELS = '1PhRIQUOv2hOnr3LBkrqOn6zkSzlTgC3V'  # _ENGINE/02-review/2026-11-07 V8 reels/<clip>/<clip>-vN.mp4
LEVELUP_FOLDERS = {'car__levelup__lvpost1': '16g3qkvGZMfFIoEEmidADFvffWDg6ZiBQ', 'car__levelup__lvpost2': '1A9QZwMtj9caXNyzjw2KTBd2GhQynTij3'}


def slides(d):
    d = Path(d)
    return sorted(p for p in d.glob('slide-*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg')) if d.is_dir() else []


def save_uploads(key, rec):
    """Merge one record into posting/drive_uploads.json under a lock (several upload runs can work in parallel)."""
    import fcntl
    with open(str(UPL) + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = json.loads(UPL.read_text()) if UPL.exists() else {}
        cur[key] = rec
        tmp = UPL.with_suffix('.tmp'); tmp.write_text(json.dumps(cur, indent=1)); tmp.replace(UPL)


def mime(name):
    return mimetypes.guess_type(name)[0] or 'application/octet-stream'


def plan_item(it, by_id, v8):
    """-> (drive_files or None, local_paths, upload_folder, missing_note)"""
    k, iid = it['kind'], it['id']
    if k == 'podcast_clip':
        name = f"{it['clip']}-{it['format']}.mp4"
        f = v8.get(name)
        if f: return [f], [], None, None
        p = WORK / 'formats' / it['clip'] / name
        return None, [p] if p.exists() else [], f"Podcast clips V1-V7/{it['clip']}", f"re-render {it['clip']} {it['format']} with tools/formats.py"
    if k == 'reel':
        m = re.search(r'/d/([^/]+)', it.get('drive') or '')
        f = by_id.get(m.group(1)) if m else None
        return ([f] if f else None), [], None, 'finished edit not found in Drive: ask the editor for the export'
    if k == 'carousel':
        if iid in LEVELUP_FOLDERS:
            fs = sorted((x for x in by_id.values() if x.get('parentId') == LEVELUP_FOLDERS[iid]), key=lambda x: x['title'])
            return (fs or None), [], None, 'LevelUp photos folder is empty'
        m = re.match(r'car__(pod\d-\d\d)__(convo|tweet|sticker|headline)$', iid)
        if m:
            c, f = m.groups()
            return None, slides(WORK / 'carousels' / c / f), f'Carousel formats/{c}/{f}', f"render with tools/carousel_formats.py clip {c} ({f})"
        m = re.match(r'car__(pod\d)__lessons$', iid)
        if m:
            return None, slides(WORK / 'carousels' / f'{m.group(1)}-lessons'), f'Carousel formats/{m.group(1)}-lessons', f"render with tools/carousel_formats.py lessons {m.group(1)}"
        if iid == 'car__pod1-05__hybrid':
            return None, slides(WORK / 'carousels/pod1-05-hybrid'), 'Carousel formats/pod1-05-hybrid', 'render with tools/carousel_formats.py hybrid pod1-05 (image slides + clip)'
        if iid == 'car__levelup__photos':
            return None, slides(WORK / 'carousels/levelup-photos'), 'Carousel formats/levelup-photos', 'render with tools/carousel_formats.py photos'
        m = re.search(r'Files: (outputs/\S+?)/? ', (it.get('body') or '') + ' ') or re.match(r'(outputs/\S+?)/? ', (it.get('files') or '') + ' ')
        if m:
            rel = m.group(1).rstrip('/')
            return None, slides(ROOT / rel), rel.replace('outputs/', '', 1), f're-render {rel} (tools/catalog_*.py)'
        m = re.match(r'txt__(.+)__(.*?)_?carousel$', iid)
        if m:
            run, sub = m.groups()
            d = ROOT / 'outputs' / run / sub / 'carousel' if sub else ROOT / 'outputs' / run / 'carousel'
            rel = d.relative_to(ROOT / 'outputs').as_posix()
            return None, slides(d), rel, f're-render outputs/{rel} (tools/carousel.py)'
        return None, [], None, 'no file hint on this item'
    if k == 'text_card':
        c = it['clip']; s = slides(WORK / 'carousels' / c / 'textcards')[:1]  # a text card is one image: slide-01 (the queue thumbnail)
        return None, s, f'Carousel formats/{c}/textcards', f'render with tools/carousel_formats.py clip {c} (textcards)'
    if k == 'single_image':
        m = re.match(r'(outputs/\S+?\.(?:jpg|png))', it.get('files') or '')
        if not m: return None, [], None, 'no file hint on this item'
        p = ROOT / m.group(1); li = Path(str(p).replace('1080x1350', '1200x627'))
        ps = [x for x in (p, li) if x.exists()]  # file 1 = IG/Threads 1080x1350, file 2 = LinkedIn 1200x627
        return None, ps, p.parent.relative_to(ROOT / 'outputs').as_posix(), f're-render {m.group(1)} (tools/catalog_cards.py)'
    if k == 'story_sequence':
        m = re.match(r'(outputs/\S+?)/? ', (it.get('files') or '') + ' ')
        d = ROOT / m.group(1) if m else None
        fr = sorted(d.glob('*-story-*.jpg'), key=lambda p: int(re.search(r'-story-(\d+)', p.name).group(1))) if d and d.is_dir() else []
        return None, fr, (d.relative_to(ROOT / 'outputs').as_posix() if d else None), f're-render story frames {m.group(1) if m else ""} (tools/story.py)'
    return None, [], None, 'unknown kind'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--upload', action='store_true'); ap.add_argument('--kind'); ap.add_argument('--match', help='only upload items whose id matches this regex')
    a = ap.parse_args()
    inv = json.loads(INV.read_text())
    by_id = {f['id']: f for f in inv['files'] + inv.get('outside_engine', [])}
    v8 = {}
    for f in inv['files']:
        if re.fullmatch(r'pod\d-\d\d-v\d\.mp4', f['title']) and f['parentId'] != '1KgDGUTmRGDJyKUYSzInSJk1sxRwpgtPD':  # skip "Reels v2" (pod1-02-v2 = reel version 2, not format V2)
            v8[f['title']] = f
    upl = json.loads(UPL.read_text()) if UPL.exists() else {}
    if a.upload:
        sys.path.insert(0, str(ROOT / 'tools')); import drive_upload
    items = [i for i in json.loads((ROOT / 'outputs/planner/plan.json').read_text())['items'] if i['kind'] in MEDIA_KINDS]
    media = json.loads(OUT.read_text()) if OUT.exists() else {}
    for it in items:
        drive, local, folder, note = plan_item(it, by_id, v8)
        if drive:
            media[it['id']] = dict(files=[dict(driveId=f['id'], name=f['title'], mimeType=f['mimeType'], sizeBytes=f.get('fileSize')) for f in drive], status='in_drive',
                                   note=('Drive: editor export (outside _ENGINE)' if it['kind'] == 'reel' else
                                         'Drive: _ENGINE/02-review/2026-11-07 V8 reels (style re-render, newer than the Nov 5 render)' if it['kind'] == 'podcast_clip' else
                                         'Drive: _ENGINE LevelUp post folder, Andrew\'s order (01, 02, ...)'))
            continue
        if not local:
            media[it['id']] = dict(files=[], status='missing', note=note); continue
        if a.upload and (not a.kind or a.kind == it['kind']) and (not a.match or re.search(a.match, it['id'])):
            for p in local:
                key = str(p)
                if key in upl: continue
                cur = json.loads(UPL.read_text()) if UPL.exists() else {}
                if key in cur: upl[key] = cur[key]; continue  # another run already did it
                url = drive_upload.put(folder, str(p))
                fid = re.search(r'/d/([^/]+)', url).group(1)
                upl[key] = dict(driveId=fid, name=p.name, folder=folder, sizeBytes=p.stat().st_size, mimeType=mime(p.name), status='uploaded')
                save_uploads(key, upl[key])
        if all(str(p) in upl for p in local):
            rec = [upl[str(p)] for p in local]
            st = 'uploaded' if any(r.get('status') == 'uploaded' for r in rec) else 'in_drive'
            media[it['id']] = dict(files=[dict(driveId=r['driveId'], name=r['name'], mimeType=r['mimeType'], sizeBytes=r['sizeBytes']) for r in rec], status=st,
                                   note=f"Drive: _ENGINE/02-review/{folder}" + (' · file 1 = 1080x1350 (IG/Threads), file 2 = 1200x627 (LinkedIn)' if it['kind'] == 'single_image' and len(rec) == 2 else '')
                                   + (' · slide-01 of the clip\'s textcards' if it['kind'] == 'text_card' else ''))
        else:
            media[it['id']] = dict(files=[], status='missing', note=f"local file(s) ready, not uploaded yet: run tools/media_map.py --upload ({len(local)} file(s) → 02-review/{folder})")
    OUT.write_text(json.dumps(media, indent=1, ensure_ascii=False))
    from collections import Counter
    kinds = {i['id']: i['kind'] for i in items}
    print(Counter((kinds[k], v['status']) for k, v in media.items() if k in kinds))


if __name__ == '__main__':
    main()
