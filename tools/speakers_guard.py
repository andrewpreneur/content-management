"""Speaker-map sanity check shared by formats.py and carousel_formats.py (no heavy imports)."""
def check_label(spk, label):
    """Guard against the tracker picking the wrong face when only one person talks (Nov 5: Blake's solo answers showed Andrew).
    Two-person podcasts only: host (Andrew) sits leftmost. If the clip bank says only the guest talks but the voice was mapped
    to the host (or the reverse), swap the two people in every segment. Returns (spk, swapped)."""
    P = sorted(spk['people'], key=lambda p: p['x'])
    if len(P) != 2 or not label: return spk, False
    host, guest = P[0]['id'], P[1]['id']; lab = label.lower()
    solo_host = lab.startswith('andrew') and '→' not in lab and '+' not in lab
    solo_guest = 'andrew' not in lab or ('→' in lab and not lab.split('→')[-1].strip().startswith('andrew'))  # 'Andrew → Blake': Blake answers, so Blake dominates
    tot = {}
    for a, b, i in spk['segments']: tot[i] = tot.get(i, 0) + b - a
    dom = max(tot, key=tot.get) if tot else None
    if (solo_guest and dom == host) or (solo_host and dom == guest):
        sw = {host: guest, guest: host}
        spk = dict(spk, segments=[[a, b, sw.get(i, i)] for a, b, i in spk['segments']], main=sw.get(spk.get('main'), spk.get('main')), swapped=True)
        return spk, True
    return spk, False
