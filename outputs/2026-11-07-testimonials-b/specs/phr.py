import json, re, sys
sys.path.insert(0, '/home/user/content-management/tools')
from testimonial_ad import words_of
_cache = {}
def norm(x): return re.sub(r'[^a-z0-9]', '', x.lower())
def W(tr):
    if tr not in _cache: _cache[tr] = words_of(json.load(open(tr)))
    return _cache[tr]
def seg(tr, a, b, after=0.0):
    """Return [start,end] of the span starting with phrase a and ending with phrase b."""
    ws = W(tr); n = [norm(w['cap']) for w in ws]
    def find(ph, frm):
        p = [norm(x) for x in ph.split() if norm(x)]
        for i in range(frm, len(ws)):
            if ws[i]['s'] < after and frm == 0: continue
            k, j = 0, i
            while k < len(p) and j < len(ws):
                if n[j] == p[k] or (k == len(p)-1 and n[j].startswith(p[k])): k += 1; j += 1
                else: break
            if k == len(p): return i, j - 1
        raise SystemExit(f'phrase not found: {ph} in {tr} after {after}')
    i0, _ = find(a, 0)
    _, j1 = find(b, i0)
    return [ws[i0]['s'], ws[j1]['e']]
def text(tr, a, b):
    return ' '.join(w['cap'] for w in W(tr) if w['s'] >= a - 0.12 and w['e'] <= b + 0.12)
