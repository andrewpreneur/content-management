#!/usr/bin/env python3
"""Weekly brand report (docs/brand.md → "Brand metrics"). Markdown out.

Usage: python3 tools/weekly_report.py [--metrics config/weekly_metrics.json] [--week 2026-W45] [--out reports/]

Two kinds of numbers, never mixed up:
- REAL: production counts from outputs/*/manifest.json (drafts, approved, posted per type).
- METRICS: follower growth, profile visits, email subscribers, inbound invites, branded search, SaaSSuite trials.
  Until GHL / Apify / Search Console / Stripe are connected these come from a metrics JSON. With no file,
  the template fills in clearly labeled PLACEHOLDER values so the layout can be reviewed — never report them as real.
"""
import argparse, datetime, glob, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = {
    '_placeholder': True,
    'handles': {  # handle: [followers_start, followers_end, profile_visits]
        'IG @andrewpreneurship': [0, 0, 0], 'IG @aiandrewpreneurship': [0, 0, 0], 'YouTube Andrewpreneurship': [0, 0, 0],
        'TikTok (handle TBD)': [0, 0, 0], 'LinkedIn Andrew George': [0, 0, 0], 'Threads': [0, 0, 0]},
    'email_subscribers': [0, 0], 'inbound_invites': 0, 'branded_search_impressions': [0, 0], 'saassuite_trials_from_content': 0,
    'top_posts': [],
}
SOURCES = {
    'Followers / profile visits': 'GHL Social Planner stats API (per connected account) or Apify scrape',
    'Email subscribers': 'GHL contacts with tag `newsletter` (count at week start/end)',
    'Inbound podcast / collab invites': 'GHL Conversations tagged `invite` (manual tag for now)',
    'Branded search ("Andrew George HighLevel")': 'Google Search Console (needs access) / YouTube search terms',
    'SaaSSuite trials from content': 'Stripe/SaaSSuite trials with UTM source = social, or GHL attribution',
}


def production():
    rows = []
    for m in glob.glob(str(ROOT / 'outputs' / '*' / 'manifest.json')):
        rows += json.loads(Path(m).read_text())['outputs']
    by_status = Counter(r['status'] for r in rows)
    by_type = Counter(r['output_type'] for r in rows)
    return len(rows), by_status, by_type


def delta(a, b):
    d = b - a
    return f"{b:,} ({'+' if d >= 0 else ''}{d:,})"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--metrics'); ap.add_argument('--week'); ap.add_argument('--out', default=str(ROOT / 'reports'))
    a = ap.parse_args()
    m = json.loads(Path(a.metrics).read_text()) if a.metrics else PLACEHOLDER
    ph = m.get('_placeholder', False)
    wk = a.week or datetime.date.today().strftime('%G-W%V')
    total, st, ty = production()
    tag = ' — ⚠️ PLACEHOLDER, not real data' if ph else ''
    L = [f"# Weekly brand report — {wk}{tag}", '']
    if ph:
        L += ['> **These audience numbers are placeholders (zeros).** The layout is real; the numbers are not. '
              'Connect the sources below, then run with `--metrics`.', '']
    L += ['## 1. Audience (brand metrics from docs/brand.md)' + tag, '', '| Handle | Followers (Δ week) | Profile visits |', '|---|---|---|']
    for h, (s, e, v) in m['handles'].items():
        L.append(f"| {h} | {delta(s, e)} | {v:,} |")
    es = m['email_subscribers']; bs = m['branded_search_impressions']
    L += ['', f"- Email subscribers (GHL list): {delta(es[0], es[1])}",
          f"- Inbound podcast / collab invites: {m['inbound_invites']}",
          f"- Branded search impressions: {delta(bs[0], bs[1])}",
          f"- SaaSSuite trials from content: {m['saassuite_trials_from_content']}", '']
    L += ['## 2. Production (REAL — from outputs/*/manifest.json)', '', f"- Outputs made: **{total}**",
          '- By status: ' + ', '.join(f"{k} {v}" for k, v in sorted(st.items())),
          '- By type: ' + ', '.join(f"{k} {v}" for k, v in sorted(ty.items())), '']
    L += ['## 3. Top posts' + tag, '']
    L += [f"- {p}" for p in m.get('top_posts', [])] or ['- (none yet — needs posting + metrics)']
    L += ['', '## 4. What we change next week', '- (Claude fills this from the numbers: winning hooks → more of that format; losing pillars → fewer.)', '',
          '## Data sources', ''] + [f"- **{k}:** {v}" for k, v in SOURCES.items()]
    out = Path(a.out); out.mkdir(exist_ok=True)
    f = out / f"weekly-{wk}{'-PLACEHOLDER' if ph else ''}.md"
    f.write_text('\n'.join(L) + '\n'); print(f)


if __name__ == '__main__':
    main()
