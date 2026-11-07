import json, sys
sys.path.insert(0, '/home/user/work/tb/bin')
from phr import seg
import build_specs as B   # reuses P, M, MUS
T='/home/user/work/tb'
clips = {k: dict(source=B.P[k]['src'], transcript=B.P[k]['tr'], crop=B.P[k]['crop'], name=B.P[k]['name'], biz=B.P[k]['biz']) for k in ('brentney','rob','agency')}
def S(k, m): return seg(B.P[k]['tr'], *B.M[k][m]) + [k]
end = dict(line='Want this for *your* SaaS?', sub='Real clients. Real support. Built on HighLevel.', cta='Tap Learn More')
COMP = [
 ('clients-01', [S('brentney','c'), S('rob','d2'), S('agency','c1'), S('brentney','d')], dict(style='card', text='The part of SaaS *nobody talks about*', kicker='3 REAL CLIENTS', dur=2.2)),
 ('clients-02', [S('brentney','b'), S('agency','c'), S('rob','e'), S('agency','d')], dict(style='bar', text='What clients say about *working with Andrew*', kicker='REAL CLIENTS', dur=3.0)),
 ('clients-03', [S('brentney','a'), S('brentney','c'), S('brentney','d'), S('rob','b'), S('rob','c'), S('rob','d'), S('agency','b'), S('agency','c'), S('agency','d')],
  dict(style='card', text='3 clients. *Unscripted.*', kicker='TESTIMONIALS', dur=2.0)),
 ('clients-04', [S('rob','d'), S('brentney','c'), S('brentney','d'), S('agency','c1'), S('rob','f')], dict(style='none')),
 ('clients-05', [S('agency','d'), S('brentney','a'), S('rob','a'), S('brentney','d'), S('agency','c1')], dict(style='bar', text='Thinking about *SaaSSuite?*', kicker=None, dur=2.6)),
]
out = []
for i, (cid, segs, hook) in enumerate(COMP):
    for asp in (['916', '45'] if cid in ('clients-01', 'clients-04') else ['916']):
        s = dict(id=cid + ('-45' if asp == '45' else ''), clips=clips, aspect=asp, segments=segs,
                 hook=(dict(hook, style='card') if asp == '45' and hook['style'] == 'bar' else hook),
                 first='them', end=end, music=B.MUS[i % len(B.MUS)], mode='fill')
        json.dump(s, open(f"{T}/specs/all/{s['id']}.json", 'w'), indent=1); out.append(s['id'])
        print(s['id'], round(sum(b - a for a, b, _ in segs), 1))
