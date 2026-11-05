#!/usr/bin/env python3
"""Build the content plan (plan.json) for the Content Planner page from everything in outputs/.

Usage: python3 tools/planner.py OUT_DIR [--start 2026-11-06]
Writes OUT_DIR/plan.json (+ OUT_DIR/thumbs/*.jpg) and outputs/planner/plan.json (committed copy).

Rules (Andrew, Nov 5):
- Podcast clips: each clip posts ONCE A WEEK for 7 weeks, a different format (V1–V7) each week; never the same clip twice in a week.
  Formats rotate per clip so every day mixes formats and sources. Rotation starts the day after `--start`; rendered clips first.
- Plan BEFORE making (Andrew, Nov 5): every post sits on the calendar with prod = ready / in_production / to_create and a due date
  (the day before it posts). Work the next 24–48 h first; the rest of the month gets made as it comes up.
- Carousels: 2 a day from the clip bank (convo / tweet / sticker / headline), 2 text cards a day (LinkedIn, Threads), lessons per podcast.
- Ready-to-post edits (LevelUp montages, finished reels): LevelUp on the start day; reels one a day after.
- Text: LinkedIn / Threads / X / carousels / email spread across days (one of each kind per day at most).
Nothing here posts anything: the page shows the plan; Andrew's status changes live in the page's db (`edits` collection).
Posting goes through GoHighLevel later (tools/ghl_post.py).
"""
import argparse, datetime as dt, json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = 'https://claude.ai/artifact/AmpkHW9Th4tRMfbMfFmiTH'
THUMBS = Path('/tmp/claude-0/-home-user-content-management/4429a793-2fa7-5e8d-8b75-1d73799d6b30/scratchpad/onetwenty/m')
FORMATS = {'v1': 'Motion graphics', 'v2': 'Story letterbox', 'v3': 'Kinetic', 'v4': 'Question box', 'v5': 'Split question', 'v6': 'Serious crop', 'v7': 'Plain hook'}
SLOTS = ['08:30', '10:45', '12:30', '15:00', '17:30', '19:45', '21:00']
TEXT_SLOT = {'linkedin_post': '09:00', 'carousel': '11:30', 'threads_post': '14:00', 'x_thread': '16:30', 'email': '07:00', 'substack': '07:00'}
TYPE = {'reel': 'video', 'reel_variant': 'video', 'linkedin_post': 'text', 'threads_post': 'text', 'x_thread': 'text', 'carousel': 'carousel', 'email': 'email',
        'substack': 'email', 'story_sequence': 'story'}
PLAT = {'linkedin_post': ['linkedin'], 'threads_post': ['threads'], 'x_thread': ['x'], 'carousel': ['instagram', 'linkedin', 'facebook'], 'email': ['email'], 'substack': ['email']}
SOURCE_LABEL = {'pod1': 'Pod1 · Andy (SoloLink)', 'pod2': 'Pod2 · Blake (Task Engine)', 'pod3': 'Pod3 · Interns'}


def body_of(o, run):
    f = o.get('file')
    if f and f.endswith('.md'):
        p = ROOT / f if not f.startswith('/') else Path(f)
        if p.exists():
            t = re.sub(r'^#.*\n|^_Source:.*\n', '', p.read_text(), flags=re.M).strip(); return t[:1600]
    return (o.get('notes') or '')[:1600]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--start', default='2026-11-06')
    a = ap.parse_args(); out = Path(a.out); (out / 'thumbs').mkdir(parents=True, exist_ok=True)
    start = dt.date.fromisoformat(a.start); monday = start + dt.timedelta(days=(7 - start.weekday()) % 7 or 7)
    items = []
    def thumb(run, key):
        src = THUMBS / run / f'{key}.jpg'
        if src.exists():
            dst = out / 'thumbs' / f'{run}__{key}.jpg'
            if not dst.exists(): shutil.copy(src, dst)
            return f'thumbs/{run}__{key}.jpg'
        return None

    # 1) ready-to-post edits
    lv = json.loads((ROOT / 'outputs/2026-11-06-levelup-reels/manifest_spec.json').read_text())
    day_reel = start + dt.timedelta(days=1)
    for o in lv['outputs']:
        did = re.search(r'Drive (\S+?)\)', o['notes']).group(1); cap = o['notes'].split('Caption:\n', 1)[1]
        if o['key'].startswith('levelup'):
            date, time = start, '11:30' if o['key'].endswith('01') else '18:30'
        else:
            date, time = day_reel, '12:15'; day_reel += dt.timedelta(days=1)
        items.append(dict(id=f"lv__{o['key']}", date=date.isoformat(), time=time, type='video', kind='reel', title=o['title'], platforms=o['platforms'],
                          status='needs_approval', source='LevelUp' if 'levelup' in o['key'] else 'Finished reels', pillar=re.search(r'Pillar: ([^.]+)\.', o['notes']).group(1),
                          body=cap, drive=f'https://drive.google.com/file/d/{did}/view', review=REVIEW, thumb=thumb('2026-11-06-levelup-reels', o['key']),
                          tags=['ready edit'] + (['LevelUp'] if 'levelup' in o['key'] else [])))

    # 2) podcast clips: 7-week format rotation, starting the day after `start`; clips already rendered go first
    WF = Path('/home/user/work/formats'); CAR = Path('/home/user/work/carousels')
    def vprod(cid, f):
        if (WF / cid / f'{cid}-{f}.mp4.sound.md').exists(): return 'ready'
        return 'in_production' if (WF / cid).exists() else 'to_create'
    bank = []
    for s in ('pod1', 'pod2', 'pod3'):
        for c in json.loads((ROOT / f'outputs/clip-bank/{s}.json').read_text())['clips']: bank.append((s, c))
    order = []  # interleave sources so one podcast never clumps
    by = {s: [c for ss, c in bank if ss == s] for s in ('pod1', 'pod2', 'pod3')}
    while any(by.values()):
        for s in ('pod3', 'pod1', 'pod2'):
            if by[s]: order.append((s, by[s].pop(0)))
    done = lambda cid: sum((WF / cid / f'{cid}-v{k}.mp4.sound.md').exists() for k in range(1, 8))
    order.sort(key=lambda x: -done(x[1]['id']))  # stable: rendered clips post first
    rot = start + dt.timedelta(days=1)
    for i, (s, c) in enumerate(order):
        for w in range(7):
            f = f'v{(i + w) % 7 + 1}'; date = rot + dt.timedelta(days=7 * w + i % 7); time = SLOTS[(i // 7) % len(SLOTS)]
            pr = vprod(c['id'], f)
            items.append(dict(id=f"clip__{c['id']}__w{w + 1}", date=date.isoformat(), time=time, type='video', kind='podcast_clip',
                              title=c['title'].replace('\n', ' '), platforms=['instagram', 'tiktok', 'youtube_shorts', 'facebook'],
                              status='rendered' if pr == 'ready' else 'clip_review', prod=pr, make=f"Render {f.upper()} ({FORMATS[f]}) of {c['id']}: tools/formats.py",
                              source=SOURCE_LABEL[s], format=f, format_name=FORMATS[f], week=w + 1,
                              clip=c['id'], speaker=c.get('speaker'), hook_q=c.get('hook_q'), hook_plain=c.get('hook_plain'), body=c.get('text', '')[:600],
                              notes=c.get('notes'), review=REVIEW, thumb=thumb('clip-bank', c['id'].replace('-', '_')) or thumb('2026-11-04-pod3', 'pod3_v1'),
                              tags=['podcast', f'week {w + 1}/7', f.upper()]))

    # 2b) planned carousels + text cards: one video becomes several carousel formats (tools/carousel_formats.py)
    CF = {'convo': ('Podcast stack', ['instagram', 'facebook', 'linkedin']), 'tweet': ('Quote cards', ['instagram', 'linkedin', 'facebook']),
          'sticker': ('Sticker story', ['instagram', 'facebook']), 'headline': ('News cover + quotes', ['instagram', 'linkedin'])}
    def cthumb(png, key):
        if not png.exists(): return None
        dst = out / 'thumbs' / f'car__{key}.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(png), '-vf', 'scale=270:-2', '-q:v', '4', str(dst)], check=True); return f'thumbs/car__{key}.jpg'
    def cprod(d):
        return 'ready' if (d / 'slide-01.png').exists() or (d / 'slide-01.mp4').exists() else ('in_production' if d.parent.exists() else 'to_create')
    end_day = start + dt.timedelta(days=30); d = start + dt.timedelta(days=1); k = 0; fmts = list(CF)
    while d <= end_day:
        for slot, j in (('11:30', 0), ('17:00', 1)):
            s, c = order[(2 * k + j) % len(order)]; f = fmts[(k + j) % len(fmts)]; dd = CAR / c['id'] / f; pr = cprod(dd)
            items.append(dict(id=f"car__{c['id']}__{f}", date=d.isoformat(), time=slot, type='carousel', kind='carousel', title=f"{CF[f][0]}: {c['title'].replace(chr(10), ' ')}",
                              platforms=CF[f][1], status='needs_approval' if pr == 'ready' else 'planned', prod=pr, make=f"Carousel '{f}' from {c['id']}: tools/carousel_formats.py clip",
                              source=SOURCE_LABEL[s], clip=c['id'], format_name=CF[f][0], body=c.get('hook_plain') or '', review=REVIEW,
                              thumb=cthumb(dd / 'slide-01.png', f"{c['id']}_{f}"), tags=['carousel', f]))
        for slot, plat in (('08:15', 'linkedin'), ('13:00', 'threads')):
            s, c = order[(k * 2 + (plat == 'threads') + 11) % len(order)]; dd = CAR / c['id'] / 'textcards'; pr = cprod(dd)
            items.append(dict(id=f"card__{c['id']}__{plat}", date=d.isoformat(), time=slot, type='text', kind='text_card', title=f"Text card: {c['title'].replace(chr(10), ' ')}",
                              platforms=[plat], status='needs_approval' if pr == 'ready' else 'planned', prod=pr, make=f"Text card from {c['id']}: tools/carousel_formats.py clip (textcards)",
                              source=SOURCE_LABEL[s], clip=c['id'], body=c.get('hook_plain') or '', review=REVIEW, thumb=cthumb(dd / 'slide-01.png', f"{c['id']}_card"), tags=['text card', plat]))
        d += dt.timedelta(days=1); k += 1
    for n, (s, day, extra) in enumerate((('pod1', 2, []), ('pod2', 6, []), ('pod3', 9, []))):
        dd = CAR / f'{s}-lessons'; pr = cprod(dd); g = json.loads((ROOT / f'outputs/clip-bank/{s}.json').read_text()).get('guest_name', s)
        items.append(dict(id=f"car__{s}__lessons", date=(start + dt.timedelta(days=day)).isoformat(), time='19:00', type='carousel', kind='carousel', title=f"5 lessons from {g}",
                          platforms=['instagram', 'linkedin', 'facebook'], status='needs_approval' if pr == 'ready' else 'planned', prod=pr, make=f'tools/carousel_formats.py lessons {s}',
                          source=SOURCE_LABEL[s], review=REVIEW, thumb=cthumb(dd / 'slide-01.png', f'{s}_lessons'), tags=['carousel', 'lessons']))
    dd = CAR / 'pod1-05-hybrid'; pr = cprod(dd)
    items.append(dict(id='car__pod1-05__hybrid', date=(start + dt.timedelta(days=3)).isoformat(), time='19:00', type='carousel', kind='carousel', title='Eat a little dirt first (images + clip)',
                      platforms=['instagram', 'linkedin', 'facebook'], status='needs_approval' if pr == 'ready' else 'planned', prod=pr, make='tools/carousel_formats.py hybrid pod1-05',
                      source=SOURCE_LABEL['pod1'], clip='pod1-05', review=REVIEW, thumb=cthumb(dd / 'slide-01.png', 'pod1-05_hybrid'), tags=['carousel', 'hybrid', 'video slide']))
    # LevelUp extras (Nov 6): real-photo dump + LinkedIn recap
    dd = CAR / 'levelup-photos'; pr = cprod(dd)
    items.append(dict(id='car__levelup__photos', date=start.isoformat(), time='14:30', type='carousel', kind='carousel', title="LevelUp photo dump: Hi, I'm Andrew George",
                      platforms=['instagram', 'facebook', 'linkedin'], status='needs_approval' if pr == 'ready' else 'planned', prod=pr, make='tools/carousel_formats.py photos (RAWFROMPHOTOS picks)',
                      source='LevelUp', review=REVIEW, thumb=cthumb(dd / 'slide-01.png', 'levelup_photos'), tags=['carousel', 'LevelUp', 'photo dump'],
                      body=(ROOT / 'outputs/2026-11-06-levelup-reels/photo_dump_caption.md').read_text() if (ROOT / 'outputs/2026-11-06-levelup-reels/photo_dump_caption.md').exists() else ''))
    li = ROOT / 'outputs/2026-11-06-levelup-reels/linkedin_recap.md'
    items.append(dict(id='txt__levelup__linkedin', date=start.isoformat(), time='09:00', type='text', kind='linkedin_post', title='LinkedIn: LevelUp recap (stage + giveaways)',
                      platforms=['linkedin'], status='needs_approval' if li.exists() else 'planned', prod='ready' if li.exists() else 'to_create', make='Write LinkedIn recap post',
                      source='LevelUp', review=REVIEW, body=li.read_text() if li.exists() else '', tags=['LevelUp', 'linkedin']))

    # LevelUp photo carousels from Drive _ENGINE/LEVELUPPOSTS (Andrew, Nov 5): post 1 today, dump #2 tomorrow; no editing
    lp = ROOT / 'outputs/2026-11-05-levelup-posts/README.md'
    if lp.exists():
        ready = '_pending_' not in lp.read_text()
        for pid, d, tm, title in (('lvpost1', '2026-11-05', '18:00', 'LevelUp carousel 1: stage, checks, podcast, team (10 slides)'),
                                  ('lvpost2', '2026-11-06', '18:00', 'LevelUp dump #2 (rest of the photos)')):
            items.append(dict(id=f'car__levelup__{pid}', date=d, time=tm, type='carousel', kind='carousel', title=title, platforms=['instagram', 'facebook', 'linkedin'],
                              status='approved' if pid == 'lvpost1' else 'needs_approval', prod='ready' if ready else 'in_production', make='Match photos to Andrew\'s order (needs LEVELUPPOSTS link-shared)',
                              source='LevelUp', drive=('https://drive.google.com/drive/folders/16g3qkvGZMfFIoEEmidADFvffWDg6ZiBQ' if pid == 'lvpost1' else 'https://drive.google.com/drive/folders/1A9QZwMtj9caXNyzjw2KTBd2GhQynTij3'), review=REVIEW, tags=['carousel', 'LevelUp', 'grokbot hand-off'],
                              body='Hand-off pack: outputs/2026-11-05-levelup-posts/README.md (order, captions). Original photos, no editing.'))

    # 3) text, carousels, email (already written in earlier runs)
    texts = []
    for p in sorted((ROOT / 'outputs').glob('*/manifest_spec.json')):
        run = p.parent.name; d = json.loads(p.read_text())
        if run == 'carousel-formats': continue  # old samples, replaced by the planned carousels above
        for o in d['outputs']:
            if TYPE.get(o['output_type']) in ('text', 'carousel', 'email') and o.get('language', 'en') == 'en':
                texts.append((run, d['source'].get('label', run), o))
    used = {}; day = start + dt.timedelta(days=1)
    for run, label, o in texts:
        k = o['output_type']
        while used.get((day, k)): day += dt.timedelta(days=1)
        d0 = start if o['key'].startswith('levelup') else day
        while used.get((d0, k)): d0 += dt.timedelta(days=1)
        if not o['key'].startswith('levelup'): used[(d0, k)] = 1
        body = body_of(o, run); first = next((ln.strip(' *>#') for ln in body.splitlines() if len(ln.strip(' *>#')) > 12 and not ln.strip().startswith('_')), o['key'])
        label = {'linkedin_post': 'LinkedIn', 'threads_post': 'Threads', 'x_thread': 'X', 'carousel': 'Carousel', 'email': 'Email', 'substack': 'Newsletter'}.get(k, k)
        title = o.get('title') or f"{label}: {first[:70]}{'…' if len(first) > 70 else ''}"
        items.append(dict(id=f"txt__{run}__{o['key']}", date=d0.isoformat(), time='14:30' if o['key'].startswith('levelup') else TEXT_SLOT.get(k, '10:00'), type=TYPE[k], kind=k, title=title,
                          platforms=PLAT.get(k, o.get('platforms', [])), status='needs_approval', prod='ready', source=label, body=body, review=REVIEW,
                          thumb=thumb(run, f"{o['key']}-slide-01") if k == 'carousel' else None, tags=[k.replace('_', ' ')]))
        if sum(1 for (dd, kk) in used if dd == day) >= 4: day += dt.timedelta(days=1)
    for it in items:
        it.setdefault('prod', 'ready')
        dd = dt.date.fromisoformat(it['date']); it['due'] = (dd if dd <= start else dd - dt.timedelta(days=1)).isoformat()
    items.sort(key=lambda x: (x['date'], x['time']))
    plan = dict(generated=dt.datetime.now().isoformat(timespec='minutes'), start=a.start, rotation_start=monday.isoformat(), timezone='America/Chicago', items=items,
                formats=FORMATS)
    (out / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False))
    (ROOT / 'outputs/planner').mkdir(exist_ok=True); (ROOT / 'outputs/planner/plan.json').write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    from collections import Counter
    print(len(items), 'items', dict(Counter(i['type'] for i in items)), dict(Counter(i['prod'] for i in items)), 'days', items[0]['date'], '→', items[-1]['date'])


if __name__ == '__main__':
    main()
