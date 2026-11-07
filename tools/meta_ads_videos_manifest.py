#!/usr/bin/env python3
"""Write outputs/2026-11-07-meta-ads/videos.csv from /home/user/work/ma/videos/videos.json + the copy below."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import meta_ads_batch_1107 as B

OUT = B.OUT
META = json.load(open('/home/user/work/ma/videos/videos.json'))

ONE = B.CONCEPTS['C01']['body']
SUITE = B.CONCEPTS['C03']['body']
COPY = {
 'V01': ("You've heard of vibe coding, right? I resell it. With my name on it.", 'I resell vibe coding, with my name on it', 'Watch the free breakdown', ONE),
 'V02': ('This ONE GHL feature is easier to sell than everything else combined.', 'Easier to sell than everything else', 'Which one? Watch this', ONE),
 'V03': ('Your client texted you at midnight about their password again?', 'Stop doing support at midnight', 'Real humans + training videos', SUITE),
 'V04': ("Everyone's out here building AI agents. I just sell ONE feature for $99 a month.", 'Everyone builds agents. I sell one.', 'Show me how', ONE),
 'V05': ('How I sell ONE HighLevel feature (the whole method fits in a note):', 'How I sell ONE HighLevel feature', 'One page. One video. $99/mo.', ONE),
 'V06': ('The one-feature math: $99/mo per user, same feature, same setup.', 'The one-feature math', '50 users = $4,950/mo', B.CONCEPTS['C06']['body']),
 'V07': ('Selling all of GHL vs. selling one feature.', 'All of GHL vs one feature', 'Pick the easy sale', B.CONCEPTS['C05']['body']),
 'V08': ('1. Turn off everything else. 2. One page, one video. 3. They build, I get paid.', 'They build. I get paid.', 'The 3-step version', B.CONCEPTS['C11']['body']),
 'V09': ('Error: too many features. Your prospect stopped listening at feature #4.', 'Too many features', 'Try selling one', B.CONCEPTS['C02']['body']),
 'V10': ("Everyone's out here building AI agents. I just sell one HighLevel feature for $99 a month.", 'Everyone builds agents. I sell one.', 'Free breakdown', B.CONCEPTS['C09']['body']),
 'V11': ('What should happen after a client signs: onboarding, education, support.', 'What happens after a client signs', 'SaaSSuite runs all three', B.CONCEPTS['C07']['body']),
 'V12': ('Everything your clients need after they sign, inside SaaSSuite.', 'What clients need after they sign', 'Start free', B.CONCEPTS['C07']['body']),
 'V13': ('"I\'m gonna show you how you can sell just one high-demand GHL feature and get rid of everything else."', 'Sell ONE GHL feature for $99/mo', 'Watch the full training', ONE),
 'V14': ("Not AI emails. Not AI agents. Something simpler, and that's the key difference.", 'Something simpler than AI agents', 'Watch the full training', ONE),
 'V15': ('I kept this behind closed doors for six weeks because it worked so well.', 'Kept behind closed doors for 6 weeks', 'Watch the full training', ONE),
 'V16': ('"They have real humans on the back answering all of your clients\' questions." (Rob, SaaSSuite customer)', '"Real humans" on support', 'Rob, SaaSSuite customer', B.CONCEPTS['C04']['body']),
 'V17': ('"I didn\'t know how to support my customers once I got them signed up… now I can scale." (Brentney, SaaSSuite customer)', '"Now I can scale"', 'Brentney, SaaSSuite customer', B.CONCEPTS['C04']['body']),
 'V18': ('"They\'ve been super helpful with everything that we do for our agency." (Ben, agency owner)', '"Super helpful with everything"', 'Ben, agency owner', B.CONCEPTS['C04']['body']),
}


def main():
    with open(OUT / 'videos.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'kind', 'duration_s', 'format', 'hook_name', 'source', 'headline', 'primary_text', 'description', 'cta_button',
                    'landing_page', 'file', 'preview'])
        for vid in sorted(META):
            m = META[vid]
            hook, head, desc, body = COPY[vid]
            ek = m['endcard']
            src = (f"static {m['source_static']} animated" if m['kind'] == 'motion'
                   else f"{m['source']} " + ' + '.join(f'{a:.1f}–{b:.1f}s' for a, b in m['segments']))
            w.writerow([vid, m['kind'], f"{float(m['dur']):.1f}", '1080x1350 (4:5) H.264', m['hook'], src, head, hook + '\n\n' + body, desc,
                        'Learn More' if ek == 'A' else 'Sign Up', B.LP_A if ek == 'A' else B.LP_B,
                        f'branch render-drop/meta-ads: meta-ads/{vid}.mp4', f'previews/{vid}.mp4'])
    print('videos.csv', len(META))


if __name__ == '__main__':
    main()
