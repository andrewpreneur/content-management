#!/usr/bin/env python3
"""Build outputs/<run>/manifest.json: one row per output, shaped like supabase `outputs`.

Usage: python3 tools/manifest.py RUN_DIR --spec RUN_DIR/manifest_spec.json
manifest_spec.json = {"source": {...}, "outputs": [{"key": "master", "output_type": "reel", "file": "...",
    "platforms": [...], "parent": null, "variant_changes": [], "language": "en", "caption": "...", "drive_id": null}]}
Adds uuid ids, parent_output_id links, status 'draft', created_at, file size.
"""
import argparse, json, os, uuid, datetime
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('run'); ap.add_argument('--spec', required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ids = {o['key']: str(uuid.uuid5(uuid.NAMESPACE_URL, f"{a.run}/{o['key']}")) for o in spec['outputs']}
    rows = []
    for o in spec['outputs']:
        f = o.get('file')
        size = os.path.getsize(f) if f and os.path.exists(f) else None
        rows.append({
            'id': ids[o['key']], 'key': o['key'], 'script_id': None,
            'parent_output_id': ids.get(o.get('parent')) if o.get('parent') else None,
            'page_id': None, 'output_type': o['output_type'], 'variant_changes': o.get('variant_changes', []),
            'language': o.get('language', 'en'), 'caption': o.get('caption'), 'asset_id': None,
            'status': 'draft', 'review_notes': None, 'scheduled_for': None, 'ghl_post_id': None,
            'posted_post_id': None, 'created_at': now,
            # engine extras (not DB columns yet)
            'file': os.path.basename(f) if f else None, 'bytes': size, 'platforms': o.get('platforms', []),
            'drive_id': o.get('drive_id'), 'notes': o.get('notes'),
        })
    out = {'run': os.path.basename(os.path.normpath(a.run)), 'source': spec['source'], 'count': len(rows), 'outputs': rows}
    Path(a.run, 'manifest.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"{len(rows)} outputs → {a.run}/manifest.json")


if __name__ == '__main__':
    main()
