"""ConvoAISchedule — working hours for Conversation AI agents (talking head + synced screen recording)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/convo.mp4'; SCR = '/home/user/work/vb/src/convo_s.mp4'; WORDS = '/home/user/work/vb/tconvo/transcript.json'
base = dict(src=SRC, screen=SCR, screen_size=(3840, 2160), words=WORDS, face=(0.46, 0.24),
            source_desc='VSLs/ConvoAISchedule_VIDEO + _SCREEN (Drive 1SBnkwrzd8tB_3-OgOC9u5jJ85eBdGiNm / 11eKLLz6jM0vNwC3zWior1Ogkfclg0nQZ)',
            music=str(MUSIC / 'm688.mp3'), music_gain=0.06, lt_title='HighLevel · Conversation AI')
S = lambda at, until, scr, label: dict(at=at, until=until, mode='screen', scr=scr, card=c_label(label), lead=0.05)
BEATS = [
    dict(at='Your conversation AI agent', until='every single day', card=c_chips(['Texts', 'DMs', '24/7'], title='Your AI agent handles', step=0.45, t0=0.6)),
    dict(at='But what if you wanted', until='during the day', card=c_text('Only on at *specific times*?')),
    dict(at='set up working hours', until='when you want it to be', card=c_big('Working hours', kicker='Conversation AI', sub='On only when *you* want it')),
    S('So all we have to do', 'different channels for our agent', (0.5, 0.5, 1.0), 'Turn on active hours'),
    S('So this is a standard', 'active during these hours', (0.5, 0.5, 1.0), 'Set the schedule'),
    dict(at='but after working hours', until='to your customers', card=c_text('After hours, *no missed texts*')),
    S('So with this setup', 'being handled', (0.5, 0.5, 1.0), 'Night shift: 5 PM → 9 AM'),
    dict(at='You can even set it up', until='during lunch', card=c_text('Or just cover *lunch*')),
    S('continue ongoing conversations', 'after scheduled hours end', (0.5, 0.5, 1.0), 'Keep live chats going'),
    dict(at="You don't want to just ghost", until='maintain that existing one', card=c_text("Don't *ghost* them", sub='Finish the chat. Skip new ones.')),
    S('So if we want our AI agent', 'auto reply message just like this', (0.5, 0.5, 1.0), 'Off-hours auto-reply'),
    dict(at='You can also do a send notification', until='off hours message is received', card=c_text('Alert your *team*', sub='When an off-hours message comes in')),
    S('You can then use follow up', 'working hours start again', (0.5, 0.5, 1.0), 'Follow up when hours resume'),
]
FULL = chain([0, 'how this works', 'So all we have to do', 'different channels for our agent', 'So this is a standard', 'active during these hours',
              'Now this can be really helpful', 'to your customers', 'So with this setup', 'being handled', 'You can even set it up', 'during lunch',
              'continue ongoing conversations', 'after scheduled hours end', "You don't want to just ghost", 'maintain that existing one',
              'So if we want our AI agent', 'auto reply message just like this', 'You can also do a send notification', 'off hours message is received',
              'You can then use follow up', 'working hours start again'])
AD = chain([0, 'when you want it to be', 'So all we have to do', 'turn this on right here', 'So with this setup', 'being handled',
            'continue ongoing conversations', 'after scheduled hours end', 'So if we want our AI agent', 'auto reply message just like this'])
END = dict(head='Give your AI agent *working hours*', btn='Save this for your setup', sub='Conversation AI · HighLevel', dur=2.2)
TEXT = [
    dict(dur=2.6, card=c_chips(['Texts', 'DMs', '24/7'], title='Your AI agent handles', step=0.3, t0=0.3)),
    dict(dur=2.4, card=c_text('Only want it on at *specific times*?')),
    dict(dur=2.8, card=c_big('Working hours', kicker='Conversation AI', sub='On only when *you* want it')),
    dict(dur=3.4, card=c_steps(['Open your agent → *Deploy*', 'Turn on *active hours*', 'Pick channels + schedule'], title='Set it up', step=0.5)),
    dict(dur=3.0, card=c_cmp('9 to 5', 'You handle it', '5 PM to 9 AM', 'Your *AI agent*', title='The night shift')),
    dict(dur=2.4, card=c_text('Or just cover *lunch*')),
    dict(dur=3.4, card=c_toggles([('Continue live chats', True), ('Off-hours auto-reply', True), ('Alert your team', True), ('Follow up at open', True)], title='Advanced settings', t_off=0.4, step=0.35)),
    dict(dur=2.6, card=c_text("Never *ghost* a lead again")),
    dict(dur=3.0, card=c_cta('Give your agent *working hours*', 'Save this for your setup')),
]
HOOKS = [
    dict(keep=FULL, hook=dict(text='Your AI agent needs *working hours*', dur=3.4)),
    dict(keep=[('So with this setup', 'being handled')] + FULL, hook=dict(text='Hire an AI for the *night shift*', dur=3.2)),
    dict(keep=[("You don't want to just ghost", 'maintain that existing one')] + FULL, hook=dict(text='Is your AI agent *ghosting* leads at 5 PM?', dur=3.4)),
]
VARIANTS = standard('cv', base, BEATS, FULL, AD, HOOKS, TEXT, END, ['AI', 'agent', 'working', 'hours', 'night', 'lunch', 'ghost', 'auto', 'reply', 'follow'],
                    ad_hook=dict(text='Give your AI agent *working hours*', dur=2.6))
if __name__ == '__main__':
    main(VARIANTS, 'convo')
