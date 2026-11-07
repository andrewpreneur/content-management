"""VIDEO 5 — AI Studio: vibe coding is the word of the year; sell it under your name for $99/mo."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/v5.mp4'; WORDS = '/home/user/work/vb/t5/transcript.json'
FACE = (0.47, 0.25)
SOURCE = 'VSLs/VIDEO 5 (Drive 1-bixWq9KXz0kb-DQsuJKTPGmh7uDrFSn)'

BEATS = [
    dict(at='Nine months', until='word of the year', card=c_big('9 months', sub='Made-up word → *Word of the Year*', kicker='Vibe coding')),
    dict(at="it's just one feature", card=c_text('Just *one* feature')),
    dict(at='inside of a software', until='call it GHL', card=c_text('Inside *GoHighLevel*', kicker='The software', sub='Most people just call it GHL')),
    dict(at='Loveable Claude', until='actively using it', card=c_chips(['Lovable', 'Claude', 'ChatGPT'], title='Making *millions*', sub='Everyone has heard of it')),
    dict(at='But the problem', until='paying them', card=c_chips(['Lovable', 'Claude', 'ChatGPT'], title="You can't *resell* them", strike=0.5, step=0.05, sub="You're just another customer")),
    dict(at="It's called AI Studio", until='your name on it', mode='full', card=c_big('AI Studio', kicker='The one feature', sub='Put *your name* on it')),
    dict(at='So all I did', until='besides AI Studio', card=c_toggles([('CRM', False), ('Automations', False), ('Calendars', False), ('AI Studio', True)], title='Your GHL account', t_off=3.0, step=0.7)),
    dict(at='my customer logs in', until='live in minutes', card=c_chat('Make me a website', 'Live in minutes', t_res=2.0)),
    dict(at='they pay me', until='just one feature', mode='full', card=c_price('$99', '/mo', sub='For *one* feature')),
    dict(at='almost nobody is doing this', until="that won't last", card=c_text('Almost nobody is doing this *yet*')),
    dict(at='So tap the link below', until='completely for free', card=c_cta('Get my *exact setup*', 'Tap the link below', sub='Free when you sign up')),
]
FULL = [(0, 62.6)]
END = dict(head='Sell *AI Studio* for $99/mo', btn='Tap the link below', sub='Get my exact setup free')
base = dict(src=SRC, words=WORDS, face=FACE, beats=BEATS, source_desc=SOURCE, music=str(MUSIC / 'music-1168.mp3'), music_gain=0.07)

AD = ['Nine months', 'word of the year', 'Now what if there was', 'just one feature', "It's called AI Studio", 'your name on it',
      'So my customer logs in', 'just one feature', 'Right now almost nobody', 'for $99 a month']
AD_KEEP = [(AD[i], AD[i + 1]) for i in range(0, len(AD), 2)]

TEXT = [
    dict(dur=2.6, card=c_big('9 months', kicker='Vibe coding', sub='Made-up word → *Word of the Year*')),
    dict(dur=2.4, card=c_text('What if you could *sell* it?')),
    dict(dur=2.6, card=c_chips(['Lovable', 'Claude', 'ChatGPT'], title='Making *millions*')),
    dict(dur=2.6, card=c_chips(['Lovable', 'Claude', 'ChatGPT'], title="You can't *resell* them", strike=0.5, step=0.05)),
    dict(dur=2.8, card=c_big('AI Studio', kicker='One feature inside GoHighLevel', sub='Put *your name* on it')),
    dict(dur=3.4, card=c_toggles([('CRM', False), ('Automations', False), ('Calendars', False), ('AI Studio', True)], title='Turn everything else off', t_off=0.6, step=0.4)),
    dict(dur=3.6, card=c_chat('Make me a website', 'Live in minutes', t_res=1.6)),
    dict(dur=2.8, card=c_price('$99', '/mo', sub='For *one* feature')),
    dict(dur=2.4, card=c_text('Almost nobody is doing this *yet*')),
    dict(dur=3.6, card=c_cta('Get my *exact setup*', 'Tap the link below', sub='Free when you sign up')),
]

VARIANTS = {
    'v5-A-916': dict(base, aspect='9x16', keep=FULL, kind='clean edit', end=END),
    'v5-A-45': dict(base, aspect='4x5', keep=FULL, kind='clean edit', end=END),
    'v5-A-169': dict(base, aspect='16x9', keep=FULL, kind='clean edit (landscape VSL)', end=END),
    'v5-H1-916': dict(base, aspect='9x16', keep=FULL, kind='hook 1', hook=dict(text='*Vibe coding* became the word of the year in 9 months', dur=3.2), beats=BEATS[1:], end=END),
    'v5-H2-916': dict(base, aspect='9x16', keep=[('they pay me', 'just one feature'), (0, 62.6)], kind='hook 2', hook=dict(text='$99/mo for *one* GHL feature', dur=3.3), end=END),
    'v5-H3-916': dict(base, aspect='9x16', keep=[('Loveable Claude', 'making millions off of this'), ('But the problem', 'paying them'), ('Now this one feature is different', 62.6)],
                      kind='hook 3', hook=dict(text="You can't resell *ChatGPT*. You can resell this.", dur=3.6), end=END),
    'v5-AD-916': dict(base, aspect='9x16', keep=AD_KEEP, kind='ad cut', hook=dict(text='Sell *AI Studio* under your name', dur=2.6), end=END, prog=True),
    'v5-AD-45': dict(base, aspect='4x5', keep=AD_KEEP, kind='ad cut', hook=dict(text='Sell *AI Studio* under your name', dur=2.6), end=END, prog=True),
    'v5-M1-916': dict(base, aspect='9x16', keep=FULL, style='motion', kind='motion, no face, original voice', caps=False, end=END,
                      accents=['Nine', 'months', 'one', 'feature', 'AI', 'Studio', '99', 'name', 'nobody']),
    'v5-M1-45': dict(base, aspect='4x5', keep=FULL, style='motion', kind='motion, no face, original voice', caps=False, end=END,
                     accents=['Nine', 'months', 'one', 'feature', 'AI', 'Studio', '99', 'name', 'nobody']),
    'v5-T1-916': dict(aspect='9x16', style='text', beats=TEXT, kind='text + motion, music only', music=str(MUSIC / 'music-130.mp3'), source_desc=SOURCE + ' (script only)'),
    'v5-T1-45': dict(aspect='4x5', style='text', beats=TEXT, kind='text + motion, music only', music=str(MUSIC / 'music-130.mp3'), source_desc=SOURCE + ' (script only)'),
}

for a, n in (('9x16', '916'), ('4x5', '45')):
    VARIANTS[f'v5-L-{n}'] = dict(base, aspect=a, keep=FULL, kind='clean edit, light theme', theme='light', cap_style='pill', end=END)
if __name__ == '__main__':
    main(VARIANTS, 'v5')
