#!/usr/bin/env python3
"""Export run / output / clip / episode data as JSON for the app "Your Content System" (content-hq, Supabase).

Usage: python3 tools/export_app.py OUT_DIR        (e.g. outputs/app-export)
Writes runs.json, runOutputs.json, clips.json, podcastEpisodes.json (JSON arrays, null fields omitted)
and unmatched.json (outputs / files that have no Drive match, for follow-up).
No network: Drive ids come from posting/media.json, posting/drive_inventory.json, posting/drive_uploads.json,
posting/audio_clips.json (tools/export_app_audio.py) and Drive links written in the run READMEs.
Docs: tools/export_app.md
"""
import csv, glob, json, mimetypes, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTS = os.path.join(ROOT, 'outputs')
FORMATS = '/home/user/work/formats'
SKIP = {'planner', 'content-hq', 'drive-copy', 'style-quiz', 'clip-bank', 'content-bank', 'carousel-formats', 'app-export'}
MEDIA_EXT = r'(?:mp4|mov|png|jpe?g|m4a|mp3|wav|pdf|webm)'
TEXT_TYPES = {'caption', 'email', 'linkedin_post', 'threads_post', 'x_thread', 'text_card', 'doc'}


def J(p):
    return json.load(open(os.path.join(ROOT, p)))


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if v is not None and v != [] and v != ''}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


def mime(name):
    return mimetypes.guess_type(name)[0] or ('audio/mp4' if name.endswith('.m4a') else 'application/octet-stream')


def f3(d):
    return {'driveId': d['driveId'], 'name': d['name'], 'mimeType': d.get('mimeType') or mime(d['name'])}


# ---------------------------------------------------------------- Drive indexes
PLAN = J('outputs/planner/plan.json')['items']
PLAN_IDS = {i['id']: i for i in PLAN}
MEDIA = J('posting/media.json')
UPLOADS = J('posting/drive_uploads.json')  # local abs path -> {driveId, name, folder, mimeType}
INV = J('posting/drive_inventory.json')
AUDIO = J('posting/audio_clips.json') if os.path.exists(os.path.join(ROOT, 'posting/audio_clips.json')) else {}

BY_NAME = defaultdict(dict)   # name -> {driveId: file}
BY_ID = {}
PARENT = {}
for f in INV['files'] + INV.get('outside_engine', []):
    d = {'driveId': f['id'], 'name': f['title'], 'mimeType': f['mimeType']}
    BY_NAME[f['title']][f['id']] = d; BY_ID[f['id']] = d; PARENT[f['id']] = f.get('parentId')
for p, u in UPLOADS.items():
    if u.get('driveId'):
        d = {'driveId': u['driveId'], 'name': u['name'], 'mimeType': u.get('mimeType') or mime(u['name'])}
        BY_NAME[u['name']][u['driveId']] = d; BY_ID[u['driveId']] = d
UP_BY_PATH = {os.path.realpath(p): u for p, u in UPLOADS.items() if u.get('driveId')}
UNMATCHED = []


def by_path(path):
    u = UP_BY_PATH.get(os.path.realpath(path)) if path else None
    return f3(u) if u else None


def by_name(name):
    """Exact file name, only when exactly one Drive file has it (never guess between two)."""
    c = BY_NAME.get(name) or {}
    return f3(next(iter(c.values()))) if len(c) == 1 else None


def plan_media(item_id):
    m = MEDIA.get(item_id)
    return [f3(f) for f in m['files']] if m and m.get('files') else []


# ---------------------------------------------------------------- helpers
def readme_text(run):
    p = os.path.join(OUTS, run, 'README.md')
    return open(p).read() if os.path.exists(p) else ''


def first_para(md):
    """First prose sentence(s) of a README (skips headings, tables, link-only lines)."""
    for line in md.splitlines():
        s = line.strip()
        if not s or s.startswith(('#', '|', '```', '>', '---')) or re.match(r'^\**review page', s, re.I):
            continue
        s = re.sub(r'\*\*|`', '', s).lstrip('- ').strip()
        if len(s) < 25:
            continue
        sents = re.split(r'(?<=[.!?])\s+', s)
        out = ' '.join(sents[:2])
        return out[:400]
    return None


def heading(md):
    m = re.search(r'^#\s+(.+)$', md, re.M)
    return re.sub(r'[*`]', '', m.group(1)).strip() if m else None


def artifact_urls(run):
    urls = []
    for p in sorted(glob.glob(os.path.join(OUTS, run, '**', '*'), recursive=True)):
        if os.path.isfile(p) and p.endswith(('.md', '.txt', '.json', '.jsonl')) and os.path.getsize(p) < 3_000_000:
            urls += re.findall(r'https://claude\.ai/(?:code/)?artifact/[A-Za-z0-9-]+', open(p, errors='ignore').read())
    return list(dict.fromkeys(urls))


def read_text(path, limit=4000):
    if path and os.path.exists(path) and path.endswith(('.md', '.txt', '.srt')):
        return open(path, errors='ignore').read().strip()[:limit]
    return None


OTYPE = {'reel': 'reel', 'reel_variant': 'reel', 'translation': 'video', 'long_video': 'doc', 'podcast': 'video',
         'linkedin_post': 'linkedin_post', 'threads_post': 'threads_post', 'x_thread': 'x_thread', 'carousel': 'carousel',
         'email': 'email', 'substack': 'doc', 'story_sequence': 'story'}

KIND = {'2026-11-04-funnelstore': 'training', '2026-11-04-switchyard': 'training', '2026-11-04-pod3': 'podcast',
        '2026-11-04-podcast-ep3': 'podcast', '2026-11-04-styles': 'other', '2026-11-04-voice-note': 'other',
        '2026-11-05-levelup-posts': 'carousel', '2026-11-06-levelup-reels': 'other', '2026-11-07-catalog': 'catalog',
        '2026-11-07-meta-ads': 'ads', '2026-11-07-skool': 'vsl', '2026-11-07-style': 'other',
        '2026-11-07-testimonials-a': 'ads', '2026-11-07-testimonials-b': 'ads', '2026-11-07-vsl-a': 'vsl',
        '2026-11-07-vsl-b': 'vsl', '2026-11-09-vsl-final': 'vsl', '2026-11-10-linkedin-banner': 'banner',
        '2026-11-10-podcast-voice-isolated': 'podcast', '2026-11-10-skool': 'other', '2026-11-11-ghl-ads': 'ads',
        '2026-11-12-vsl4-feed': 'ads', '2026-11-13-medspa-deposits': 'training'}

# Source lines for runs whose README has no "Source:" line (written from each README).
SOURCE = {'2026-11-06-levelup-reels': 'Editor-finished reels in Drive (2 LevelUp montages + 6 talking-head reels)',
          '2026-11-07-catalog': 'Back catalog: Pod1-3 clip bank, feature videos and YouTube videos',
          '2026-11-07-meta-ads': 'SaaSSuite offer + testimonials (static and motion ads)',
          '2026-11-07-skool': 'Skool community scripts (motion graphics, voice clone + narrator)',
          '2026-11-07-style': '13 example reels in examplereelsandformats',
          '2026-11-07-testimonials-a': 'Customer testimonial videos (Mark, Lee, Ben, Jessica, Tania)',
          '2026-11-07-testimonials-b': 'Customer testimonial videos (agency owner, Brentney, Rob)',
          '2026-11-07-vsl-a': 'VSL VIDEO 1-4 (4K Drive originals)',
          '2026-11-09-vsl-final': 'VSL VIDEO 1-7 (4K Drive originals)',
          '2026-11-10-linkedin-banner': 'Andrew stage photos (LevelUp)',
          '2026-11-12-vsl4-feed': 'VSL VIDEO 4 "15 people" (4K source)',
          '2026-11-13-medspa-deposits': "Andrew's notes on med spa deposits (script.txt), motion graphics"}

RUNS, OUTPUTS = [], []


def add_out(run, key, type_, title=None, status=None, item=None, media=None, text=None, file=None):
    o = {'runId': run, 'key': key, 'type': type_, 'title': title, 'status': status,
         'itemId': item if item in PLAN_IDS else None, 'media': media or [], 'text': (text or '')[:4000] or None}
    if not o['media'] and type_ not in TEXT_TYPES:
        UNMATCHED.append({'runId': run, 'key': key, 'file': file})
    OUTPUTS.append(o)


def plan_status(item):
    return PLAN_IDS[item]['status'] if item in PLAN_IDS else None


# ---------------------------------------------------------------- run handlers
def run_manifest(run):
    d = os.path.join(OUTS, run)
    man = json.load(open(f'{d}/manifest.json')) if os.path.exists(f'{d}/manifest.json') else None
    spec = json.load(open(f'{d}/manifest_spec.json')) if os.path.exists(f'{d}/manifest_spec.json') else None
    rows = {}
    for o in (spec or {}).get('outputs', []):
        rows[o['key']] = dict(o)
    for o in (man or {}).get('outputs', []):
        r = rows.setdefault(o['key'], {})
        for k, v in o.items():
            if k == 'file':
                r.setdefault('file', v)
            elif v is not None:
                r[k] = v
    src = (spec or man or {}).get('source', {})
    for key, o in rows.items():
        t = OTYPE.get(o.get('output_type'), 'video')
        f = o.get('file') or ''
        if f.endswith(('.mp3', '.wav', '.m4a')):
            t = 'video' if False else 'doc' if False else t
        item = f'txt__{run}__{key}' if f'txt__{run}__{key}' in PLAN_IDS else None
        if not item:
            for cand in (f'lv__{key}', f'txt__{run}__{key.replace("_", "-")}'):
                if cand in PLAN_IDS:
                    item = cand
        path = f if os.path.isabs(f) else None
        if not path or not os.path.exists(path):
            hits = [p for p in glob.glob(f'{d}/**/{os.path.basename(f)}', recursive=True)] if f else []
            if key.split('_')[0] in os.listdir(d) and '_' in key:  # voice-note packs: A-basic-agencies_linkedin
                hits = [p for p in hits if f'/{key.split("_")[0]}/' in p] or hits
            path = hits[0] if len(hits) == 1 else (path if path else None)
        media = []
        if item:
            media = plan_media(item)
        if not media and t in ('carousel', 'story'):
            sub = 'carousel' if t == 'carousel' else 'stories'
            base = os.path.dirname(path) if path and os.path.basename(os.path.dirname(path)) == sub else None
            if not base:
                pref = key.split('_')[0] if '_' in key else ''
                cand = os.path.join(d, pref, sub) if pref and os.path.isdir(os.path.join(d, pref, sub)) else os.path.join(d, sub)
                base = cand if os.path.isdir(cand) else None
            if base:
                media = [m for m in (by_path(p) for p in sorted(glob.glob(f'{base}/*.png')) + sorted(glob.glob(f'{base}/*.jpg'))) if m]
        if not media and path:
            m = by_path(path)
            media = [m] if m else []
        if not media and o.get('drive_id'):
            media = [BY_ID.get(o['drive_id']) or {'driveId': o['drive_id'], 'name': os.path.basename(f), 'mimeType': mime(f)}]
        text = None
        if t in TEXT_TYPES or t == 'doc':
            text = o.get('caption') or read_text(path)
            if not text and item:
                text = PLAN_IDS[item].get('body')
        elif o.get('caption'):
            text = o['caption']
        title = o.get('title') or (PLAN_IDS[item]['title'] if item else None) or o.get('notes') or os.path.basename(f) or key
        add_out(run, key, t, title=str(title)[:200], status=plan_status(item) or o.get('status'), item=item,
                media=media, text=text, file=f)
    return src


def run_levelup_posts(run):
    md = readme_text(run)
    for key, item, t in (('post1', 'car__levelup__lvpost1', 'carousel'), ('post2', 'car__levelup__lvpost2', 'carousel'),
                         ('photos', 'car__levelup__photos', 'carousel'), ('linkedin', 'txt__levelup__linkedin', 'linkedin_post')):
        if item in PLAN_IDS:
            p = PLAN_IDS[item]
            add_out(run, key, t, title=p['title'], status=p['status'], item=item, media=plan_media(item),
                    text=p.get('body') if t in TEXT_TYPES else None)
    return {'title': heading(md), 'summary': first_para(md)}


CAT_TYPE = {'carousel': 'carousel', 'single image': 'single_image', 'story sequence': 'story'}
CAT_TEXT = {'linkedin': ('linkedin.md', 'linkedin_post', '-li'), 'x': ('x.md', 'x_thread', '-x'),
            'threads': ('threads.md', 'threads_post', '-th'), 'substack note': ('substack-notes.md', 'doc', None)}


def md_sections(path):
    out, cur = {}, None
    if not os.path.exists(path):
        return out
    for line in open(path):
        m = re.match(r'^###\s+(\S+)', line)
        if m:
            cur = m.group(1); out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: ''.join(v).strip() for k, v in out.items()}


def run_catalog(run):
    d = os.path.join(OUTS, run)
    secs = {f: md_sections(f'{d}/text/{f}') for f, _, _ in CAT_TEXT.values()}
    for r in csv.DictReader(open(f'{d}/manifest.csv')):
        rid, typ, f = r['id'], r['type'], r['file']
        title = r.get('hook') or rid
        if typ == 'text':
            fn, t, suf = CAT_TEXT.get(r['format'], ('', 'doc', None))
            m = re.match(r'(.+?)-(linkedin|x|threads-(\d)|substack)$', rid)
            src = m.group(1) if m else rid
            n = m.group(3) if m else None
            item = None
            if suf == '-th':
                for c in (f'cat__{src}-th{n}', f'cat__{src}-th' if n == '1' else None):
                    if c in PLAN_IDS:
                        item = c; break
            elif suf and f'cat__{src}{suf}' in PLAN_IDS:
                item = f'cat__{src}{suf}'
            text = secs.get(fn, {}).get(f'{src}-{n}' if n else src)
            if not text and item:
                text = PLAN_IDS[item].get('body')
            add_out(run, rid, t, title=title, status=plan_status(item), item=item, text=text, file=f)
            continue
        t = CAT_TYPE.get(typ, 'image')
        if t == 'carousel':
            item = 'cat__' + rid[:-len('-convo')] if rid.endswith('-convo') else None
        elif t == 'single_image':
            item = 'cat__' + re.sub(r'-\d+x\d+$', '', rid)
        else:
            item = 'cat__' + rid
        item = item if item in PLAN_IDS else None
        full = os.path.join(d, f)
        if os.path.isdir(full):
            files = sorted(glob.glob(f'{full}/*.png') + glob.glob(f'{full}/*.jpg'))
            media = [m for m in (by_path(p) for p in files) if m]
        else:
            m = by_path(full)
            media = [m] if m else []
        if not media and item and t != 'single_image':
            media = plan_media(item)
        if not media and item and t == 'single_image':
            media = [m for m in plan_media(item) if m['name'] == os.path.basename(f)]
        add_out(run, rid, t, title=title, status=plan_status(item), item=item, media=media, file=f)
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def run_csv_ads(run):
    d = os.path.join(OUTS, run)
    for sub in ('', 'round2/'):
        for r in csv.DictReader(open(f'{d}/{sub}manifest.csv')) if os.path.exists(f'{d}/{sub}manifest.csv') else []:
            text = '\n\n'.join(x for x in (r.get('headline'), r.get('primary_text'), r.get('description')) if x)
            files = [r.get('file_4x5'), r.get('file_9x16')]
            media = [m for m in (by_path(os.path.join(d, sub, x)) for x in files if x) if m]
            add_out(run, sub + r['id'], 'ad', title=r.get('headline') or r['id'], media=media, text=text, file=files[0])
        for r in csv.DictReader(open(f'{d}/{sub}videos.csv')) if os.path.exists(f'{d}/{sub}videos.csv') else []:
            text = '\n\n'.join(x for x in (r.get('headline'), r.get('primary_text'), r.get('description')) if x)
            name = os.path.basename(r.get('file') or '') or r['id'] + '.mp4'
            m = by_name(name) or by_name(r['id'] + '.mp4')
            add_out(run, sub + r['id'], 'ad', title=r.get('headline') or r['id'], media=[m] if m else [], text=text, file=name)
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def run_testimonials_a(run):
    d = os.path.join(OUTS, run)
    groups = defaultdict(list)
    meta = {}
    for r in csv.DictReader(open(f'{d}/manifest.csv')):
        groups[r['id']].append(os.path.basename(r['file'])); meta.setdefault(r['id'], r)
    for k, names in groups.items():
        media = [m for m in (by_name(n) for n in names) if m]
        r = meta[k]
        add_out(run, k, 'ad', title=r.get('hook') or r.get('topline') or k, media=media, file=names[0])
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def run_testimonials_b(run):
    d = os.path.join(OUTS, run)
    for s in json.load(open(f'{d}/specs/manifest.json')):  # one row per ad (specs/<id>.json = render specs)
        k = s['id']
        m = by_name(k + '.mp4')
        add_out(run, k, 'ad', title=s.get('hook') or s.get('title') or k, media=[m] if m else [],
                text=s.get('first_line'), file=k + '.mp4')
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def run_vsl_a(run):
    for r in json.load(open(os.path.join(OUTS, run, 'manifest.json'))):
        name = os.path.basename(r.get('file', '')) or r['id'] + '.mp4'
        m = by_name(name)
        add_out(run, r['id'], 'video', title=f"{r.get('video')} {r.get('variant')}: {r.get('desc') or r.get('hook') or ''}"[:200],
                media=[m] if m else [], file=r.get('file'))
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def run_vsl_b(run):
    for line in open(os.path.join(OUTS, run, 'manifest.jsonl')):
        if not line.strip():
            continue
        r = json.loads(line); name = os.path.basename(r.get('file', '')) or r['id'] + '.mp4'
        m = by_name(name)
        add_out(run, r['id'], 'video', title=f"{r.get('video')} {r.get('kind')} {r.get('aspect')}".strip(),
                media=[m] if m else [], file=r.get('file'))
    md = readme_text(run)
    return {'title': heading(md), 'summary': first_para(md)}


def pick_in_folder(name, parents):
    """Two Drive files share a name: take the one in a folder this run already uses, if exactly one is."""
    c = [d for d in (BY_NAME.get(name) or {}).values() if PARENT.get(d['driveId']) in parents]
    return f3(c[0]) if len(c) == 1 else None


def run_readme(run):
    """Outputs = media files the run's READMEs name, plus media files saved in the run folder.
    When a README links Drive files, only the linked files count (other names there are sources)."""
    d = os.path.join(OUTS, run)
    mds = sorted(glob.glob(f'{d}/**/README.md', recursive=True))
    linked, named = {}, []
    tok = re.compile(r'([A-Za-z0-9][\w-]*(?:\.[\w-]+)*\.' + MEDIA_EXT + r')\b')
    for p in mds:
        for line in open(p, errors='ignore').read().splitlines():
            for text, fid in re.findall(r'\[([^\]]+)\]\(https://drive\.google\.com/file/d/([\w-]+)', line):
                name = (BY_ID.get(fid) or {}).get('name') or (text if re.search(r'\.' + MEDIA_EXT + r'$', text, re.I) else None)
                if name:
                    linked[name] = BY_ID.get(fid) or {'driveId': fid, 'name': name, 'mimeType': mime(name)}
            for fid in re.findall(r'(?<!\()https://drive\.google\.com/file/d/([\w-]+)', line):
                name = (BY_ID.get(fid) or {}).get('name')
                if not name:
                    cells = [c for c in line.split('|') if 'drive.google.com/file/d/' + fid in c or tok.search(c)]
                    m = tok.search(line)
                    name = m.group(1) if m and m.group(1) not in linked else None
                if name:
                    linked.setdefault(name, BY_ID.get(fid) or {'driveId': fid, 'name': name, 'mimeType': mime(name)})
                else:
                    UNMATCHED.append({'runId': run, 'key': fid, 'file': 'Drive link with no file name in README'})
            plain = re.sub(r'\[[^\]]*\]\([^)]*\)', ' ', line)
            named += [t for t, u in re.findall(r'\[([^\]]+)\]\(([^)]*)\)', line)
                      if 'drive.google.com' not in u and re.fullmatch(r'[\w.-]+\.' + MEDIA_EXT, t)]
            for m in tok.finditer(plain):
                i = m.start()
                before = plain[max(0, i - 2):i]
                if before[-1:] in '/<>:-_.' or (len(before) == 2 and before[1] == ' ' and before[0].isalnum()):
                    continue  # part of a path, a template, or a name with spaces
                named.append(m.group(1))
            named += re.findall(r'`[\w-]+:([\w.-]+\.' + MEDIA_EXT + r')`', line)
    local = [os.path.basename(p) for p in sorted(glob.glob(f'{d}/*') + glob.glob(f'{d}/images/*'))
             if os.path.isfile(p) and re.search(r'\.' + MEDIA_EXT + r'$', p, re.I)]
    names = list(linked) + [n for n in dict.fromkeys(local + ([] if linked else named)) if n not in linked]
    found = {}
    for name in names:
        m = linked.get(name) or by_path(os.path.join(d, name)) or by_name(name)
        if not m:
            hits = glob.glob(f'{d}/**/{name}', recursive=True)
            m = by_path(hits[0]) if hits else None
        found[name] = m
    parents = {PARENT.get(m['driveId']) for m in found.values() if m} - {None}
    for name, m in found.items():
        m = m or pick_in_folder(name, parents)
        ext = name.rsplit('.', 1)[-1].lower()
        t = {'mp4': 'video', 'mov': 'video', 'webm': 'video', 'png': 'image', 'jpg': 'image', 'jpeg': 'image'}.get(ext, 'doc')
        if KIND.get(run) == 'ads' and t == 'video':
            t = 'ad'
        add_out(run, name, t, title=name, media=[f3(m)] if m else [], file=name)
    md = readme_text(run) or (open(mds[0]).read() if mds else '')
    return {'title': heading(md), 'summary': first_para(md)}


HANDLERS = {'2026-11-05-levelup-posts': run_levelup_posts, '2026-11-07-catalog': run_catalog,
            '2026-11-07-meta-ads': run_csv_ads, '2026-11-07-testimonials-a': run_testimonials_a,
            '2026-11-07-testimonials-b': run_testimonials_b, '2026-11-07-vsl-a': run_vsl_a, '2026-11-07-vsl-b': run_vsl_b}


def build_runs():
    for run in sorted(os.listdir(OUTS)):
        if run in SKIP or not re.match(r'\d{4}-\d{2}-\d{2}-', run) or not os.path.isdir(os.path.join(OUTS, run)):
            continue
        n0 = len(OUTPUTS)
        d = os.path.join(OUTS, run)
        if run in HANDLERS:
            info = HANDLERS[run](run)
        elif os.path.exists(f'{d}/manifest.json') or os.path.exists(f'{d}/manifest_spec.json'):
            src = run_manifest(run)
            info = {'title': src.get('feature') or src.get('label') or src.get('title'), 'source': src.get('title'),
                    'summary': src.get('summary')}
        else:
            info = run_readme(run)
        md = readme_text(run)
        src = info.get('source') or SOURCE.get(run)
        if not src:
            m = re.search(r'^\**Sources?:?\**:?\s*(.+)$', md, re.M | re.I) or re.search(r'Source:\s*([^\n]+)', md)
            src = re.sub(r'[*`]', '', m.group(1)).strip()[:300] if m else None
        urls = artifact_urls(run)
        if not urls:  # runs reviewed on the Review Hub: take the review link of their queue items
            revs = {PLAN_IDS[o['itemId']]['review'] for o in OUTPUTS[n0:] if o.get('itemId') and PLAN_IDS[o['itemId']].get('review')}
            urls = sorted(revs)
        RUNS.append({'runId': run, 'title': info.get('title') or run, 'date': run[:10], 'kind': KIND.get(run, 'other'),
                     'source': src, 'summary': info.get('summary') or first_para(md), 'outputs': len(OUTPUTS) - n0,
                     'reviewArtifact': urls[0] if urls else None})


# ---------------------------------------------------------------- clips + episodes
def first_sentence(text, n=220):
    s = re.split(r'(?<=[.!?])\s+', (text or '').strip())[0]
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


def clip_format_files(cid):
    """{vN: media} for every rendered format with a Drive file. media.json (queue choice) first, then the local
    render's upload, then a unique Drive name."""
    out = {}
    for it in PLAN:
        if it.get('kind') == 'podcast_clip' and it.get('clip') == cid and it.get('format'):
            fm = [m for m in plan_media(it['id']) if m['name'] == f"{cid}-{it['format']}.mp4"]
            if fm:
                out[it['format']] = fm[0]
    for n in range(1, 10):
        v = f'v{n}'
        if v in out:
            continue
        m = by_path(f'{FORMATS}/{cid}/{cid}-{v}.mp4') or by_name(f'{cid}-{v}.mp4')
        if m:
            out[v] = m
    return dict(sorted(out.items(), key=lambda kv: int(kv[0][1:])))


def build_clips():
    clips, eps = [], []
    for ep in ('pod1', 'pod2', 'pod3'):
        b = J(f'outputs/clip-bank/{ep}.json')
        for c in b['clips']:
            fm = clip_format_files(c['id'])
            vid = fm.get('v1') or (next(iter(fm.values())) if fm else None)
            a = AUDIO.get(c['id'])
            clips.append({'clipId': c['id'], 'episode': ep, 'title': (c.get('title') or '').replace('\n', ' '),
                          'speaker': c.get('speaker'), 'guest': b.get('guest_name'), 'startS': c.get('t0'),
                          'durationS': c.get('dur'), 'hook': c.get('hook_q') or c.get('hook_plain'),
                          'quote': first_sentence(c.get('text')), 'status': c.get('status'), 'topic': c.get('topic'),
                          'formats': list(fm), 'video': vid, 'audio': f3(a) if a else None})
    return clips


# Edited masters: Drive OCTOBER 2026 -> VIDEO V+S (1JVEoN5wvfCp81mX_wnKjw5Ck0sUjGn9q), checked with the Drive MCP Nov 17.
# Audio: separate RAW recordings + ElevenLabs voice-isolated MP3 (outputs/2026-11-10-podcast-voice-isolated/README.md).
EP_FILES = {
    'pod1': {'video': ('1o16B2yPjlANHRT6xhp6hvU0dh32pJefg', 'Pod1.mp4', 'video/mp4'),
             'audioRaw': ('1YNzpNvmue1fBhnNZUOyridKByd-V2Rcj', 'pod1audio.m4a', 'audio/mp4'),
             'audio': ('1L6p5DsSO2LD_x-gcctkbdleMqlogr3vq', 'pod1audio - voice isolated.mp3', 'audio/mpeg')},
    'pod2': {'video': ('19oDJJJ-NDbI9FCOE6XBZTuyPGvXiEln0', 'Pod2.mp4', 'video/mp4'),
             'audioRaw': ('1WVNDyfza5rYQ5v1pSWu185lLa6MYE4vY', 'Pod2audio.m4a', 'audio/mp4'),
             'audio': ('1elRcVBtflPV83I7UkulI1HLOT5Z0SJGj', 'Pod2audio - voice isolated.mp3', 'audio/mpeg')},
    'pod3': {'video': ('1sfvECkswOzt0svNs3O-rOQDRGFGyH4qw', 'Pod3.mp4', 'video/mp4'),
             'audioRaw': ('1o3pgiW3bZevi5luySUnC1GCZ5hdE4Wkv', 'pod3audio.m4a', 'audio/mp4'),
             'audio': ('1_fw-jqjEBtnAWM9F6dzlRGP0oMggABbi', 'pod3audio - voice isolated.mp3', 'audio/mpeg')},
    # Pod4/Pod5: RAW, not edited yet (no video master). Audio only for now.
    'pod4': {'audioRaw': ('1qHr1mk3hpzlWrYM40HQFgPY_pg3hZrdI', 'Podcast 4.m4a', 'audio/mp4'),
             'audio': ('1lIG-0gBtRoBAguWvsK9GRl3etFQkw5FW', 'Podcast 4 - voice isolated.mp3', 'audio/mpeg')},
    'pod5': {'audioRaw': ('1OtyMLrYHW4mSYyJiKgkEb-FIC67-oj89', 'Podcast5.m4a', 'audio/mp4'),
             'audio': ('11h6nhxrb0EjLPt7KJ0vmZrJCuHcRCOdT', 'Podcast5 - voice isolated.mp3', 'audio/mpeg')},
}
# ElevenLabs voice-isolated WAV (48 kHz stereo) next to each MP3.
WAV = {'pod1': ('1lBSltTiowKUCwgV2APkSjVQWffPSU5EZ', 'pod1audio - voice isolated.wav'), 'pod2': ('1bAUTd6jOLeEW_8zuTYKfCGMYEZMFycQJ', 'Pod2audio - voice isolated.wav'),
       'pod3': ('1OeOy8azOo16_tXObycbuArwvSBopxRCa', 'pod3audio - voice isolated.wav'), 'pod4': ('1cgyo9t9z8VjGaSr-CIwrT7JJF4QJIWfh', 'Podcast 4 - voice isolated.wav'),
       'pod5': ('17KvoADf3aXYci70g9k7EHeytiwO2hhID', 'Podcast5 - voice isolated.wav')}
for _ep, (_id, _n) in WAV.items():
    EP_FILES[_ep]['audioWav'] = (_id, _n, 'audio/wav')
RAW_DURATION = {'pod4': 2018.5, 'pod5': 1348.6}


def tx_duration(ep):
    p = f'/home/user/work/{ep}/tx/transcript.json'
    try:
        return round(json.load(open(p))['segments'][-1]['end'], 1)
    except Exception:
        return None


def build_episodes(clips):
    eps = []
    for ep in ('pod1', 'pod2', 'pod3'):
        b = J(f'outputs/clip-bank/{ep}.json')
        n = sum(1 for c in clips if c['episode'] == ep)
        topics = list(dict.fromkeys(c['topic'] for c in b['clips'] if c.get('topic')))[:4]
        files = {k: {'driveId': v[0], 'name': v[1], 'mimeType': v[2]} for k, v in EP_FILES[ep].items()}
        eps.append({'episodeId': ep, 'title': f"{ep.capitalize()}: {b.get('guest_name')}" + (f" ({b['guest_org']})" if b.get('guest_org') and b['guest_org'] not in b.get('guest_name', '') else ''),
                    'guest': b.get('guest_name'), 'guestOrg': b.get('guest_org'), 'guestTitle': b.get('guest_title'),
                    'date': None, 'month': '2026-10', 'durationS': tx_duration(ep), **files, 'clips': n,
                    'summary': f"Andrew with {b.get('guest_name')}, {b.get('guest_title')}. {n} clips in the bank" + (f": {', '.join(topics)}." if topics else '.')})
    for ep in ('pod4', 'pod5'):
        files = {k: {'driveId': v[0], 'name': v[1], 'mimeType': v[2]} for k, v in EP_FILES[ep].items()}
        eps.append({'episodeId': ep, 'title': f"{ep.capitalize()} (raw, not edited yet)", 'month': '2026-10', 'durationS': RAW_DURATION[ep], **files, 'clips': 0,
                    'summary': 'Full recording, cleaned with the ElevenLabs voice isolator. No video edit or clips yet.'})
    # Get Real ep. 3 (2026-11-04-podcast-ep3) is a different show from pod3 (interns panel)
    m = json.load(open(os.path.join(OUTS, '2026-11-04-podcast-ep3', 'manifest.json')))
    s = m['source']
    eps.append({'episodeId': 'getreal-ep3', 'title': s.get('title'), 'date': None, 'durationS': s.get('duration_s'),
                'clips': sum(1 for o in m['outputs'] if o['output_type'] == 'reel'), 'runId': '2026-11-04-podcast-ep3',
                'summary': f"{s.get('feature')}. {s.get('summary')}"})
    return eps


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTS, 'app-export')
    os.makedirs(out, exist_ok=True)
    build_runs()
    clips = build_clips()
    eps = build_episodes(clips)
    for name, data in (('runs', RUNS), ('runOutputs', OUTPUTS), ('clips', clips), ('podcastEpisodes', eps), ('unmatched', UNMATCHED)):
        with open(os.path.join(out, name + '.json'), 'w') as f:
            json.dump(clean(data), f, indent=1, ensure_ascii=False)
        print(f'{name}.json: {len(data)}')


if __name__ == '__main__':
    main()
