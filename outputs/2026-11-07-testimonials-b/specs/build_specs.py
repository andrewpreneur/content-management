import json, os, sys
sys.path.insert(0, '/home/user/work/tb/bin')
from phr import seg, text
T = '/home/user/work/tb'
MUS = [f'{T}/music/norm/{m}' for m in ['music-130.mp3', 'm688.mp3', 'm714.mp3', 'music-1168.mp3', 'm580.mp3']]
P = {
 'brentney': dict(src=f'{T}/src/brentney.bin', tr=f'{T}/tr/brentney/transcript.json', name='Brentney', biz='SaaSSuite client', crop={'cx':0.5,'cy':0.5}),
 'rob': dict(src=f'{T}/src/rob.bin', tr=f'{T}/tr/rob/transcript.json', name='Rob', biz='SaaSSuite customer', crop={'cx':0.5,'cy':0.5}),
 'agency': dict(src=f'{T}/src/tellus1.bin', tr=f'{T}/tr/tellus1/transcript.json', name='Agency owner', biz='Builds HighLevel for his clients', crop={'cx':0.5,'cy':0.5}, first='him'),
 'mason': dict(src=f'{T}/src/masontestimonial.bin', tr=f'{T}/tr/masontestimonial/transcript.json', name='Andrew George × Mason', biz='Real 1:1 coaching call', stars=False, first='Mason', mode='frame', crop={'cx':0.40,'cy':0.5}),
}
# moments: (start phrase, end phrase)
M = {
 'brentney': dict(a=('Oh my goodness','is amazing'), b=('He literally','of the way'), c=('I was so confused','business growth'),
                  d=('Now I have','I can scale'), e=("I'm so happy",'so much Andrew'), e2=("I'm so happy","I'm so happy")),
 'rob': dict(a=('Just wanted','is amazing'), b=('I love how','entire dashboard'), c=('the training','ticket system'),
             d=('I mean','is fantastic'), d2=('they have real','questions'), e=('And just shout','with SaaSSuite'), f=('Highly','recommend')),
 'agency': dict(a=('Hey just want','for our agency'), b=('We use them','for ourselves'), c=("He's been a great",'good care of us'),
                c1=("He's been a great",'going to do'), d=('So if',"recommend it")),
}
END = {
 'brentney': [dict(line='Want a *clear plan* like Brentney?', sub='We help you onboard, support and keep your SaaS clients.'),
              dict(line='Stop guessing. *Start scaling.*', sub='SaaSSuite walks you through every step.')],
 'rob': [dict(line='Want *real humans* supporting your clients?', sub='SaaSSuite: your SaaS on HighLevel, support included.'),
         dict(line='Your SaaS. *Fully supported.*', sub='Custom menus, dashboards, training, AI and a real support team.')],
 'agency': [dict(line='Want a team that *follows through?*', sub='We build HighLevel for you and your clients.'),
            dict(line='Build your agency on *HighLevel*, with backup.', sub='Andrew and the SaaSSuite team help you build it out.')],
 'mason': [dict(line="Want a call like *Mason's?*", sub='Get 1:1 help building your SaaS on HighLevel.'),
           dict(line='Get your *own* game plan.', sub='1:1 help building your SaaS on HighLevel.')],
}
ADS = []
def ad(pid, n, order, hook, aspect='916', end=0, extra=None):
    p = P[pid]
    if pid == 'mason':
        segs = order
    else:
        segs = [seg(p['tr'], *M[pid][k]) for k in order]
    s = dict(id=f'{pid}-{n:02d}' + ('-45' if aspect == '45' else ''), source=p['src'], transcript=p['tr'], aspect=aspect,
             crop=p.get('crop', {}), segments=segs, hook=hook, name=p['name'], biz=p['biz'], stars=p.get('stars', True),
             first=p.get('first', p['name'].split()[0]), end=dict(END[pid][end], cta='Tap Learn More'),
             music=MUS[(len(ADS)) % len(MUS)], mode=p.get('mode', 'fill'))
    if extra: s.update(extra)
    ADS.append(s)
card = lambda t, k='REAL CLIENT', d=2.0: dict(style='card', text=t, kicker=k, dur=d)
bar = lambda t, k=None, d=3.0: dict(style='bar', text=t, kicker=k, dur=d)
none = dict(style='none')

# ---------------- Brentney ----------------
ad('brentney', 1, 'abcde', bar('Real client. *Unscripted.*', 'TESTIMONIAL', 2.6))
ad('brentney', 2, 'cde', card('She signed clients up. *Then what?*'))
ad('brentney', 3, 'cd', bar('Signed SaaS clients but can\'t *support them?*', None, 3.2), end=1)
ad('brentney', 4, 'dce', none)                       # result line first
ad('brentney', 5, 'bcd', bar('He walked me through *every step*', 'REAL CLIENT', 2.8))
ad('brentney', 6, 'ade', card('From confused to *ready to scale*'), end=1)
ad('brentney', 7, 'cd', card('Support was *slowing down* her growth', 'REAL CLIENT', 2.2))
ad('brentney', 8, 'abde', bar('What a *real* SaaS mentor changes', None, 2.8), end=1)
ad('brentney', 9, 'abcde', card('Her words, *not ours.*', 'TESTIMONIAL', 1.8))
ad('brentney', 10, 'bde', card('Every. Single. *Step.*', 'REAL CLIENT', 1.8), end=1)
ad('brentney', 11, ['c', 'd'], none)
ad('brentney', 12, 'ce', bar('This was *slowing her business* down', None, 2.8))
# ---------------- Rob ----------------
ad('rob', 1, 'abcdef', bar('Rob, *SaaSSuite customer.* Unscripted.', 'TESTIMONIAL', 2.6))
ad('rob', 2, 'df', card('Who answers your SaaS clients\' *questions?*'))
ad('rob', 3, 'bcdf', bar('Everything your SaaS clients need, *in one place*', None, 3.0), end=1)
ad('rob', 4, 'dabcf', none)
ad('rob', 5, 'cdf', bar('Tired of being your clients\' *support desk?*', None, 3.0))
ad('rob', 6, 'aef', card('5 stars from *Rob*', 'TESTIMONIAL', 1.6), end=1)
ad('rob', 7, 'bcf', card('5 things Rob loves about *SaaSSuite*', 'REAL CUSTOMER', 2.0), end=1)
ad('rob', 8, 'adef', card('Real humans. *Real support.*'))
ad('rob', 9, 'abcdef', card('Why Rob runs his SaaS on *SaaSSuite*', 'REAL CUSTOMER', 2.0), end=1)
ad('rob', 10, 'dbcf', bar('*Real humans* answer your clients', None, 2.6))
ad('rob', 11, 'ad', none, end=1)
ad('rob', 12, 'bcef', bar('Custom menu. Custom dashboard. *Your brand.*', None, 3.0), end=1)
# ---------------- Agency owner ----------------
ad('agency', 1, 'abcd', bar('An agency owner on *working with Andrew*', 'TESTIMONIAL', 2.6))
ad('agency', 2, 'cd', card('*Follows through.* Every time.'))
ad('agency', 3, 'bcd', bar('Need HighLevel *built for your clients?*', None, 3.0), end=1)
ad('agency', 4, 'cabd', none)
ad('agency', 5, 'abd', card('What agency owners say about *Andrew\'s team*', 'REAL CLIENT', 2.2), end=1)
ad('agency', 6, 'bd', bar('Built for his clients. *And for him.*', None, 2.6))
ad('agency', 7, ['c1', 'd'], card('Does what he says *he\'ll do*'), end=1)
ad('agency', 8, 'abcd', card('Thinking about working with Andrew? *Watch this.*', 'REAL CLIENT', 2.2), end=1)
ad('agency', 9, 'bcd', none)
ad('agency', 10, 'cd', bar('The best thing a client can say: *he follows through*', None, 3.0), end=1)

# ---------------- Mason call (frame mode) ----------------
MT = P['mason']['tr']
def ms(a, b, after=0.0): return seg(MT, a, b, after)
def mad(n, segs, title, hook, end=0, aspect='916'):
    ad('mason', n, segs, hook, aspect=aspect, end=end, extra=dict(title=title, kicker='REAL 1:1 CALL'))
mad(1, [ms('ask AI in the top', 'standalone feature'), ms('find contacts that', 'step one of AI agents')],
    'Sell *Ask AI* as its own feature', bar('This HighLevel button is a *sellable feature*', None, 2.8))
mad(2, [ms('there\'s agent studio', 'all sorts of things'), ms('AI agents are so easy', 'build the instructions for it'), ms('you can literally just sell', 'whatever it may be')],
    'Super Agents: *sell them as a service*', bar('AI agents are *so easy* to build now', None, 2.6))
mad(3, [ms('So I would give her this system', 'my might end up') if False else ms('So I would give her this system', 'you or she might not'), ms('Yeah, no, I like that', 'That\'s cool')],
    'The *30-day free* close', card('Give it away for *30 days.* Then this happens.', 'REAL 1:1 CALL', 2.2), end=1)
mad(4, [ms('the trigger, you can make', 'the whole workflow'), ms('Wow', 'that\'s crazy', 640), ms('just two steps', 'and such')],
    'A *2-step* workflow that pings her phone', bar('2 steps. Her phone *pings.* Leads get called.', None, 3.0))
mad(5, [ms('As of now, there\'s nothing stopping', 'lowest plan and do it'), ms('Wow', 'super easy', 800), ms('set up your domain', 'all that jazz')],
    'White label HighLevel on the *lowest plan*', card('You can white label HighLevel *today*', 'REAL 1:1 CALL', 2.0), end=1)
mad(6, [ms('if you establish', 'resell a point'), ms('That\'s a good point', 'start doing that'), ms('Go do it', 'Go do it, man')],
    'Every business owner *needs this.* Be the one who sells it.', bar('How to get *HighLevel clients* without ads', None, 2.6))
mad(7, [ms('buying a phone number getting', 'all friction'), ms('when in reality, she can just text', 'super valuable still')],
    'Skip the friction. *Start simple.*', bar('Don\'t make clients wait *2 weeks* for a phone number', None, 3.0), end=1)
mad(8, [ms('you can just use it as a management', 'off to the races')],
    'HighLevel as an *interactive spreadsheet*', card('The easiest way to get a client *using HighLevel*', 'REAL 1:1 CALL', 2.2))
mad(9, [ms('I like to view Ask AI', 'in your account'), ms('Wow', 'Okay', 200)],
    'Find the *missing money* in your account', bar('Ask your CRM: *who should I follow up with?*', None, 3.0), end=1)
mad(10, [ms('it\'s really not that complicated', 'and then use it'), ms('Yeah, it\'s pretty easy', 'Wow', 873)],
    'It\'s *not that complicated*', card('HighLevel isn\'t hard. *The good stuff is buried.*', 'REAL 1:1 CALL', 2.2))
mad(11, [ms('really you should do homework', 'CRM play with it'), ms('So what starts a workflow', 'the workflow do')],
    'Your *HighLevel homework*', bar('Learning HighLevel? *Start with these 4.*', None, 2.8), end=1)
mad(12, [ms('All of my courses', 'two hour course'), ms('I\'ve posted over 1000', 'on YouTube')],
    '*1,000+ free* HighLevel videos', card('Every course I make is *free*', 'REAL 1:1 CALL', 1.8), end=1)
mad(13, [ms('you can literally just sell', 'whatever it may be'), ms('That\'s crazy', 'that\'s cool', 380)],
    'Sell an *AI agent system*', card('"Our AI agent system books you *appointments*"', 'REAL 1:1 CALL', 2.4))
mad(14, [ms('if you establish', 'resell a point'), ms('That\'s a good point', 'start doing that'), ms('Go do it', 'Go do it, man'), ms('You can, you can always text me', 'happy to help')],
    'The *50 business owners* rule', card('Know 50 business owners? *They all need this.*', 'REAL 1:1 CALL', 2.4), end=1)

mad(15, [ms('ask AI in the top', 'standalone feature'), ms('find contacts that', 'step one of AI agents'), ms('I like to view Ask AI', 'in your account'), ms('Wow', 'Okay', 200)],
    '*Ask AI*: the feature you can sell first', card('The first HighLevel feature I\'d *sell*', 'REAL 1:1 CALL', 2.2))
mad(16, [ms('there\'s agent studio', 'all sorts of things'), ms('AI agents are so easy', 'build the instructions for it'), ms('you can literally just sell', 'whatever it may be'), ms('the trigger, you can make', 'the whole workflow'), ms('Wow', 'that\'s crazy', 640)],
    'Build and *sell* AI agents in HighLevel', bar('AI agents are *so easy* to sell now', None, 2.6), end=1)

# 4:5 versions of the best ones
BEST45 = ['brentney-02', 'brentney-04', 'rob-02', 'rob-08', 'agency-02', 'agency-04', 'mason-06', 'mason-03']
for b in BEST45:
    s = dict(next(x for x in ADS if x['id'] == b)); s['id'] = b + '-45'; s['aspect'] = '45'
    if s['hook'].get('style') == 'bar' and s['mode'] == 'fill':
        s['hook'] = dict(s['hook'], style='card')
    ADS.append(s)

os.makedirs(f'{T}/specs/all', exist_ok=True)
for s in ADS:
    json.dump(s, open(f"{T}/specs/all/{s['id']}.json", 'w'), indent=1)
    if '--show' in sys.argv:
        print(s['id'], '|', ' // '.join(text(s['transcript'], a, b) for a, b in s['segments']), '|', round(sum(b - a for a, b in s['segments']), 1))
print(len(ADS), 'specs')
