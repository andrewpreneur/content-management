"""VIDEO 7 — I sell one GHL feature (AI Studio) for $99/mo: the 3-step setup."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/v7.mp4'; WORDS = '/home/user/work/vb/t7/transcript.json'
base = dict(src=SRC, words=WORDS, face=(0.475, 0.28), source_desc='VSLs/VIDEO 7 (Drive 1YHs1Kz6wIOM59hlYzCvHF5idNUvgHQHT)',
            music=str(MUSIC / 'music-1168.mp3'), music_gain=0.07)
BEATS = [
    dict(at='I sell one GHL feature', until='this is how', card=c_price('$99', '/mo', kicker='One GHL feature', sub="Here's how")),
    dict(at='The feature is AI Studio', until="It's vibe coding", mode='full', card=c_big('AI Studio', sub="It's *vibe coding*")),
    dict(at='You type make me a website', until='builds it for you', card=c_chat('Make me a website', 'Built for you', t_res=1.4)),
    dict(at="That's why Lovable", until='off of it', card=c_chips(['Lovable', 'ChatGPT', 'Claude'], title='Making *millions*')),
    dict(at='The problem is', until='resell this', card=c_chips(['Lovable', 'ChatGPT'], title="You can't *resell* them", strike=0.9, step=0.05, sub='You *can* resell this')),
    dict(at="It's inside a white label", until='Go High Level', card=c_text('Inside *GoHighLevel*', kicker='White-label software')),
    dict(at='Step one', until='one button', card=c_toggles([('CRM', False), ('Calendars', False), ('Automations', False), ('AI Studio', True)], title='Step 1 · Turn everything else off', t_off=1.6, step=0.5)),
    dict(at='Step two', until='start building', card=c_steps(['One page', 'One video', 'One sign-up button'], title='Step 2', step=0.6, t0=0.5)),
    dict(at='Step three', until='set the markup', card=c_cmp('Your cost', 'Barely *anything*', 'Your price', 'You set the *markup*', title='Step 3')),
    dict(at='So they pay me', until='every time they build', card=c_text('Paid *every month*', sub='Plus a little more every build')),
    dict(at='Right now literally nobody', until='going to be thousands', card=c_cmp('Today', 'Almost *nobody*', 'Next year', '*Thousands*')),
    dict(at='Tap the link below', until='screen by screen', card=c_cta('Set it up *screen by screen*', 'Tap the link below')),
]
FULL = [(0, 48.5)]
END = dict(head='Sell *one feature* for $99/mo', btn='Tap the link below', sub='Screen-by-screen setup', dur=2.0)
TEXT = [
    dict(dur=2.6, card=c_price('$99', '/mo', kicker='One GHL feature', sub="Here's how")),
    dict(dur=2.4, card=c_big('AI Studio', sub="It's *vibe coding*")),
    dict(dur=3.2, card=c_chat('Make me a website', 'Built for you', t_res=1.4)),
    dict(dur=2.8, card=c_chips(['Lovable', 'ChatGPT'], title="You can't *resell* them", strike=0.9, step=0.05, sub='You *can* resell this')),
    dict(dur=3.4, card=c_toggles([('CRM', False), ('Calendars', False), ('Automations', False), ('AI Studio', True)], title='Step 1 · Turn everything else off', t_off=0.6, step=0.4)),
    dict(dur=3.0, card=c_steps(['One page', 'One video', 'One sign-up button'], title='Step 2', step=0.45, t0=0.3)),
    dict(dur=3.0, card=c_cmp('Your cost', 'Barely *anything*', 'Your price', 'You set the *markup*', title='Step 3')),
    dict(dur=2.6, card=c_text('Paid *every month*', sub='Plus a little more every build')),
    dict(dur=2.8, card=c_cmp('Today', 'Almost *nobody*', 'Next year', '*Thousands*')),
    dict(dur=3.4, card=c_cta('Set it up *screen by screen*', 'Tap the link below')),
]
HOOKS = [
    dict(keep=FULL, hook=dict(text='I sell *one* GHL feature for $99/mo', dur=3.6)),
    dict(keep=[('The problem is', 'resell this'), (0, 48.5)], hook=dict(text='Lovable makes millions. *You* can\'t resell it.', dur=3.0)),
    dict(keep=[('Right now literally nobody', 'going to be thousands'), (0, 48.5)], hook=dict(text='Nobody is doing this *yet*', dur=3.4)),
]
AD = chain(['I sell one GHL feature', 'this is how', 'The feature is AI Studio', 'builds it for you', 'The problem is', 'resell this',
            'Step one', 'one button', 'Step two', 'start building', 'So they pay me', 'every time they build', 'Tap the link below', 'screen by screen'])
VARIANTS = standard('v7', base, BEATS, FULL, AD, HOOKS, TEXT, END, ['one', 'feature', '$99', 'AI', 'Studio', 'resell', 'Step', 'logo', 'markup', 'nobody', 'thousands'],
                    ad_hook=dict(text='$99/mo from *one* GHL feature', dur=2.6))
if __name__ == '__main__':
    main(VARIANTS, 'v7')
