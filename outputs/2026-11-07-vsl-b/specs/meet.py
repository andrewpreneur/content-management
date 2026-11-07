"""MEETINGROOM — HighLevel Meeting Rooms: native meeting links, recording, transcripts, Ask AI (face + synced screen)."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent))
from common import *  # noqa

SRC = '/home/user/work/vb/src/meet.mp4'; SCR = '/home/user/work/vb/src/meet_s.mp4'; WORDS = '/home/user/work/vb/tmeet/transcript.json'
base = dict(src=SRC, screen=SCR, screen_size=(3840, 2160), words=WORDS, face=(0.48, 0.28), zooms=[1.0, 1.2, 1.0, 1.35], split_zoom=1.1,
            source_desc='VSLs/MEETINGROOM + _SCREEN (Drive 1zE5pfiK45gSHlPMdwAHbENyxgQ6oT3iy / 1rPifZJSNU9DPInicxsDk9aA3RARGGg0M)',
            music=str(MUSIC / 'm688.mp3'), music_gain=0.06, lt_title='HighLevel · Meeting Rooms')
S = lambda at, until, scr, label: dict(at=at, until=until, mode='screen', scr=scr, card=c_label(label), lead=0.05)
USES = ['Calendars', 'Communities', 'Courses', 'Events', 'Webinars']
BEATS = [
    dict(at='Meeting rooms are now here', until='other third-party apps', card=c_text('Meeting rooms are *here*', kicker='New in HighLevel', sub='No third-party apps')),
    dict(at='These links we can use for calendars', until='transcripts', card=c_chips(['Calendars', 'Websites', 'Live streams', 'Recording', 'Transcripts'], title='One link for', step=0.38)),
    S('Now this is immediately going', 'custom slug at the end', (0.5, 0.5, 1.0), 'Your own room link'),
    S('So by turning this on', 'into the meeting', (0.5, 0.5, 1.0), 'Passcode + waiting room'),
    S("So now we're actually in the meeting", 'Check this out', (0.5, 0.5, 1.0), 'Inside the meeting'),
    S('We can record straight from here', 'which is awesome', (0.5, 0.5, 1.0), 'One-click recording'),
    dict(at="there's active noise cancellation", until='inside of the meeting rooms', card=c_text('Active *noise cancellation*', kicker='Built in')),
    S('We can do a minimal', 'you can do that', (0.5, 0.5, 1.0), 'Blur + pro backdrops'),
    S('We actually have the ability', 'absolutely awesome', (0.5, 0.5, 1.0), 'Live transcripts + Ask AI'),
    dict(at="It's brandless", until='with this experience', card=c_text("It's *brandless*", sub='Your clients only see you')),
    S('you can see recordings right here', 'access to our transcripts', (0.5, 0.5, 1.0), 'Recordings + transcripts'),
    dict(at='So we can actually connect the calendar', until='zoom or Google meet', card=c_cmp('Zoom / Google Meet', 'Another *app* to pay for', 'Meeting rooms', 'Inside *HighLevel*')),
    dict(at='This is another awesome feature', until='with high level instead', card=c_chips(USES, title='Works with', step=0.3)),
]
FULL = chain([0, 'how it works', 'Now this is immediately going', 'custom slug at the end', 'So by turning this on', 'into the meeting',
              "So now we're actually in the meeting", 'Check this out', 'We can record straight from here', 'which is awesome',
              "there's active noise cancellation", 'inside of the meeting rooms', 'We can do a minimal', 'you can do that',
              'We actually have the ability', 'absolutely awesome', "It's brandless", 'with this experience', 'you can see recordings right here',
              'access to our transcripts', 'So we can actually connect the calendar', 'zoom or Google meet', 'This is another awesome feature', 'with high level instead'])
AD = chain([0, 'other third-party apps', 'We can record straight from here', 'which is awesome', 'We actually have the ability', 'absolutely awesome',
            "It's brandless", 'with this experience', 'So we can actually connect the calendar', 'zoom or Google meet', 'This is another awesome feature', 'with high level instead'])
END = dict(head='Replace Zoom with *Meeting Rooms*', btn='Save this for your setup', sub='HighLevel · Meeting Rooms', dur=2.2)
TEXT = [
    dict(dur=2.6, card=c_text('Meeting rooms are *here*', kicker='New in HighLevel', sub='No third-party apps')),
    dict(dur=3.0, card=c_chips(['Calendars', 'Websites', 'Live streams', 'Recording', 'Transcripts'], title='One link for', step=0.25)),
    dict(dur=3.2, card=c_toggles([('Waiting room', True), ('Guest users', True), ('Open room', False)], title='Security', t_off=0.5, step=0.4)),
    dict(dur=3.0, card=c_steps(['One-click *recording*', 'Live *transcripts*', 'Ask *AI* about the call'], title='Inside the call', step=0.5)),
    dict(dur=2.4, card=c_text('Active *noise cancellation*', kicker='Built in')),
    dict(dur=2.4, card=c_text("It's *brandless*", sub='Your clients only see you')),
    dict(dur=3.0, card=c_cmp('Zoom / Google Meet', 'Another *app* to pay for', 'Meeting rooms', 'Inside *HighLevel*')),
    dict(dur=2.8, card=c_chips(USES, title='Works with', step=0.25)),
    dict(dur=3.0, card=c_cta('Replace Zoom with *Meeting Rooms*', 'Save this')),
]
HOOKS = [
    dict(keep=FULL, hook=dict(text='HighLevel just replaced *Zoom*', dur=3.2)),
    dict(keep=[('So we can actually connect the calendar', 'zoom or Google meet')] + FULL, hook=dict(text='Cancel your *Zoom* subscription?', dur=3.2)),
    dict(keep=[('We actually have the ability', 'absolutely awesome')] + FULL, hook=dict(text='Live transcripts + *Ask AI*, inside HighLevel', dur=3.4)),
]
VARIANTS = standard('mr', base, BEATS, FULL, AD, HOOKS, TEXT, END, ['meeting', 'rooms', 'record', 'transcripts', 'AI', 'brandless', 'Zoom', 'HighLevel', 'webinars'],
                    ad_hook=dict(text='HighLevel just replaced *Zoom*', dur=2.6), text_music='music-1168.mp3')
if __name__ == '__main__':
    main(VARIANTS, 'meet')
