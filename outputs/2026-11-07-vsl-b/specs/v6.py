"""VIDEO 6 — AI Studio is easier to sell than everything else in GHL combined (they already want it)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/v6.mp4'; WORDS = '/home/user/work/vb/t6/transcript.json'
base = dict(src=SRC, words=WORDS, face=(0.47, 0.23), source_desc='VSLs/VIDEO 6 (Drive 1_n-UedWGJ7ZQO9VW1QzZxDN7X-i-vmDH)',
            music=str(MUSIC / 'music-1168.mp3'), music_gain=0.07)
AI5 = ['Lovable', 'Claude', 'ChatGPT', 'Replit', 'Base44']
BEATS = [
    dict(at='This one GHL feature', until='combined', card=c_text('Easier to sell than *everything else*', kicker='One GHL feature')),
    dict(at='When you sell a CRM', until='They already want it', card=c_cmp('Selling a CRM', 'You have to *convince* them', 'This feature', 'They *already* want it')),
    dict(at="It's just vibe coding", until='right in the platform', card=c_chat('Build me a booking app', 'Published', t_res=2.2)),
    dict(at="That's why Lovable", until='off of it', card=c_chips(AI5, title='Making *millions*', step=0.32)),
    dict(at='The feature is called', until='logo on it', mode='full', card=c_big('AI Studio', kicker='The feature', sub='Put *your own logo* on it')),
    dict(at='This is the shortcut', until='feature in GHL', card=c_text('The *shortcut* to clients', sub='From just one feature in GHL')),
    dict(at='Tap the link below', until='how it works', card=c_cta('See *exactly* how it works', 'Tap the link below')),
]
FULL = [(0, 36.15)]
END = dict(head='Sell *AI Studio* with your logo', btn='Tap the link below', sub="I'll show you exactly how it works", dur=2.0)
TEXT = [
    dict(dur=2.8, card=c_text('Easier to sell than *everything else*', kicker='One GHL feature')),
    dict(dur=3.2, card=c_cmp('Selling a CRM', 'You have to *convince* them', 'This feature', 'They *already* want it')),
    dict(dur=3.6, card=c_chat('Build me a booking app', 'Published', t_res=1.6)),
    dict(dur=2.8, card=c_chips(AI5, title='Making *millions*', step=0.22)),
    dict(dur=2.8, card=c_big('AI Studio', kicker='Inside GoHighLevel', sub='Put *your own logo* on it')),
    dict(dur=2.6, card=c_text('The *shortcut* to clients', sub='From one feature')),
    dict(dur=3.4, card=c_cta('See *exactly* how it works', 'Tap the link below')),
]
HOOKS = [
    dict(keep=FULL, hook=dict(text="I've sold GHL for years. *This* sells easiest.", dur=3.4), beats=BEATS[1:]),
    dict(keep=[('When you sell a CRM', 'They already want it'), (0, 36.15)], hook=dict(text='Stop selling the *CRM*', dur=3.0)),
    dict(keep=[('The feature is called', 'logo on it'), (0, 36.15)], hook=dict(text='Put *your logo* on vibe coding', dur=3.4)),
]
AD = chain(['This one GHL feature', 'combined', 'When you sell a CRM', 'They already want it', 'You can type what you want', 'right in the platform',
            'The feature is called', 'logo on it', 'Tap the link below', 'how it works'])
VARIANTS = standard('v6', base, BEATS, FULL, AD, HOOKS, TEXT, END, ['one', 'feature', 'convinced', 'want', 'AI', 'Studio', 'logo', 'millions', 'shortcut'],
                    ad_hook=dict(text='The easiest *GHL feature* to sell', dur=2.6))
if __name__ == '__main__':
    main(VARIANTS, 'v6')
