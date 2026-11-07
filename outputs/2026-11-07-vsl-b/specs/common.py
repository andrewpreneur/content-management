"""Shared runner for vsl-b specs. Each spec module defines SRC, WORDS, VARIANTS = {id: spec}; run:
python3 outputs/2026-11-07-vsl-b/specs/v5.py [variant ...]   (no args = all)
Renders to $VSL_OUT (default /home/user/work/vb/out), writes a QA contact sheet per render and appends to manifest.jsonl."""
import json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/vslb'))
import vsl  # noqa
from vsl import *  # noqa

OUT = Path(os.environ.get('VSL_OUT', '/home/user/work/vb/out'))
QA = Path(os.environ.get('VSL_QA', '/home/user/work/vb/qa'))
MUSIC = Path('/home/user/work/vb/music')
MAN = Path(__file__).resolve().parent.parent / 'manifest.jsonl'


def main(variants, video):
    want = sys.argv[1:] or list(variants)
    for vid in want:
        spec = dict(variants[vid]); spec['id'] = vid
        t = time.time()
        out, T, shots, beats = vsl.make(spec, OUT / video, f'/home/user/work/vb/tmp/{vid}')
        QA.mkdir(parents=True, exist_ok=True)
        vsl.sample(str(out), str(QA / f'{vid}.jpg'), 8)
        rec = dict(id=vid, video=video, file=f'{video}/{vid}.mp4', aspect=spec['aspect'], style=spec.get('style', 'face'),
                   kind=spec.get('kind', ''), hook=spec.get('hook_desc') or (spec.get('hook') or {}).get('text', ''), length=round(T, 1),
                   source=spec.get('source_desc', ''), shots=len(shots), beats=len(beats), mb=round(out.stat().st_size / 1e6, 1))
        lines = [l for l in (MAN.read_text().splitlines() if MAN.exists() else []) if json.loads(l)['id'] != vid]
        MAN.write_text('\n'.join(lines + [json.dumps(rec)]) + '\n')
        print(f'{vid}: {T:.1f}s {len(shots)} shots {len(beats)} beats {rec["mb"]}MB in {time.time() - t:.0f}s', flush=True)


def standard(v, base, beats, full, ad_keep, hooks, text, end, accents, ad_hook, text_music='music-130.mp3', extra=None):
    """the standard 12-render set per video: A (916/45/169), H1-H3 (916), AD (916/45), M1 (916/45), T1 (916/45).
    hooks: [dict(keep=..., hook=dict(text, dur), beats=optional)]"""
    V = {}
    for a, n in (('9x16', '916'), ('4x5', '45'), ('16x9', '169')):
        V[f'{v}-A-{n}'] = dict(base, aspect=a, keep=full, beats=beats, kind='clean edit' + (' (landscape VSL)' if n == '169' else ''), end=end)
    for i, h in enumerate(hooks, 1):
        V[f'{v}-H{i}-916'] = dict(base, aspect='9x16', keep=h['keep'], beats=h.get('beats', beats), kind=f'hook {i}', hook=h['hook'], end=end)
    for a, n in (('9x16', '916'), ('4x5', '45')):
        V[f'{v}-AD-{n}'] = dict(base, aspect=a, keep=ad_keep, beats=beats, kind='ad cut', hook=ad_hook, end=end, prog=True)
        V[f'{v}-M1-{n}'] = dict(base, aspect=a, keep=full, beats=beats, style='motion', kind='motion, no face, original voice', caps=False, end=end, accents=accents)
        V[f'{v}-T1-{n}'] = dict(aspect=a, style='text', beats=text, kind='text + motion, music only, no voice', music=str(MUSIC / text_music),
                               source_desc=base['source_desc'] + ' (script only)')
    for a, n in (('9x16', '916'), ('4x5', '45')):
        V[f'{v}-L-{n}'] = dict(base, aspect=a, keep=full, beats=beats, kind='clean edit, light theme', theme='light', cap_style='pill', end=end)
    V.update(extra or {})
    return V


def chain(pairs):
    return [(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]
