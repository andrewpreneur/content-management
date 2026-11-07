"""DYKCustomAudiences — smart lists as Meta custom + lookalike audiences in HighLevel Ad Manager (face + synced screen)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/dyk.mp4'; SCR = '/home/user/work/vb/src/dyk_s.mp4'; WORDS = '/home/user/work/vb/tdyk/transcript.json'
base = dict(src=SRC, screen=SCR, screen_size=(3840, 2160), words=WORDS, face=(0.475, 0.24),
            source_desc='VSLs/DYKCustomAudiences_VIDEO + _SCREEN (Drive 1sgq7xj_JrEX2udQDijnNqPDYjQk4Ce0s / 1oRWDEsuJHPnCtyqWxR5T8kdfN6qy__8O)',
            music=str(MUSIC / 'm714.mp3'), music_gain=0.06, lt_title='HighLevel · Ad Manager')
S = lambda at, until, scr, label: dict(at=at, until=until, mode='screen', scr=scr, card=c_label(label), lead=0.05)
STEPS3 = c_steps(['Marketing → *Ad Manager*', 'Settings → *Audiences*', 'Customer list → *Use smart list*'], title='Set it up', step=0.6)
BEATS = [
    dict(at='Did you know that you can use smart lists', until='Ad Manager', card=c_text('Smart lists → *custom audiences*', kicker='Did you know?')),
    dict(at='make a custom or look like', until='straight from HighLevel', card=c_steps(['Pick a *smart list*', 'Make a custom or *lookalike*', 'Send it to *Meta*'], step=0.7, t0=0.1)),
    dict(at="Now if you haven't used custom audiences", until='one specific group of people', card=c_text('Market to *one specific group*', kicker='Custom audiences')),
    S('All we have to do is click Audiences', 'in this list', (0.6, 0.4, 0.6), 'Settings → Audiences'),
    S("What we're going to do is we're going to click", 'or Customer List', (0.5, 0.5, 0.45), 'Create a custom audience'),
    S('So we just click Customer List', 'inside of our CRM', (0.5, 0.55, 0.45), 'Customer list → Use smart list'),
    dict(at='This just means as someone gets added', until='custom audience in meta', card=c_steps(['Contact joins your *smart list*', 'Meta audience *updates itself*'], title='Dynamic updates', step=0.9)),
    dict(at="Let's say we want to make a lookalike", until='off of this custom one', mode='full', card=c_big('Lookalike', kicker='Then scale it', sub='Built off your *custom audience*')),
    dict(at='So the lowest percentage', until='keeping this at 1 for now', card=c_cmp('0 to 1%', '*Closest* match', '1 to 5%', '*Bigger*, broader', title='Audience size')),
    dict(at='Think about things like your email', until='custom audience', card=c_text('Opened an email in the last *30 days*', sub='Auto-added to your Meta audience')),
    dict(at='again just go to Marketing', until='as smart lists', card=STEPS3),
]
FULL = chain([0, 'how this works', "Now if you haven't used custom audiences", 'one specific group of people', 'All we have to do is click Audiences', 'in this list',
              "What we're going to do is we're going to click", 'or Customer List', 'So we just click Customer List', 'inside of our CRM',
              'This just means as someone gets added', 'super crazy valuable', "Let's say we want to make a lookalike", 'off of this custom one',
              'So the lowest percentage', 'similar to this one', "I'd recommend keeping", 'keeping this at 1 for now',
              'Think about things like your email', 'custom audience', 'again just go to Marketing', 'as smart lists'])
AD = chain([0, 'straight from HighLevel', 'So we just click Customer List', 'inside of our CRM', 'This just means as someone gets added', 'custom audience in meta',
            "Let's say we want to make a lookalike", 'off of this custom one', 'Think about things like your email', 'custom audience'])
END = dict(head='Turn smart lists into *Meta audiences*', btn='Save this for your next campaign', sub='HighLevel · Ad Manager', dur=2.2)
TEXT = [
    dict(dur=2.6, card=c_text('Smart lists → *custom audiences*', kicker='Did you know?')),
    dict(dur=3.2, card=c_steps(['Pick a *smart list*', 'Make a custom or *lookalike*', 'Send it to *Meta*'], step=0.5, t0=0.1)),
    dict(dur=3.6, card=STEPS3),
    dict(dur=3.2, card=c_toggles([('Only current contacts', False), ('Include dynamic updates', True)], title='Advanced conditions', t_off=0.6, step=0.5)),
    dict(dur=2.6, card=c_steps(['Contact joins your *smart list*', 'Meta audience *updates itself*'], title='Dynamic updates', step=0.6)),
    dict(dur=2.6, card=c_big('Lookalike', kicker='Then scale it', sub='Built off your *custom audience*')),
    dict(dur=3.0, card=c_cmp('0 to 1%', '*Closest* match', '1 to 5%', '*Bigger*, broader', title='Audience size')),
    dict(dur=3.0, card=c_text('Opened an email in the last *30 days*', sub='Auto-added to your Meta audience')),
    dict(dur=3.0, card=c_cta('Turn smart lists into *Meta audiences*', 'Save this')),
]
HOOKS = [
    dict(keep=FULL, hook=dict(text='Your *smart lists* can feed your Meta ads', dur=3.4)),
    dict(keep=[('Think about things like your email', 'custom audience')] + FULL, hook=dict(text='Retarget everyone who opened your *last email*', dur=3.4)),
    dict(keep=[('So this is a huge huge bonus', 'super crazy valuable')] + FULL, hook=dict(text='The best reason to run ads *inside HighLevel*', dur=3.4)),
]
VARIANTS = standard('dyk', base, BEATS, FULL, AD, HOOKS, TEXT, END, ['smart', 'list', 'custom', 'audience', 'audiences', 'lookalike', 'Meta', 'dynamic', 'email'],
                    ad_hook=dict(text='Smart lists → *Meta audiences*', dur=2.6), text_music='m565.mp3')
if __name__ == '__main__':
    main(VARIANTS, 'dyk')
