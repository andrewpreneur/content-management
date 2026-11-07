#!/usr/bin/env python3
"""Meta ads batch, Nov 7 2026 (overnight meta-ads worker).

python3 tools/meta_ads_batch_1107.py [--only ID,ID] [--no916]
Writes outputs/2026-11-07-meta-ads/statics/*.jpg and manifest.csv.
Local assets live in /home/user/work/ma (real frames of Andrew from the VSL shoot, cutouts, testimonial frames, GHL UI stills).
"""
import argparse, csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from meta_ads_render import render_all

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'outputs/2026-11-07-meta-ads'
A = Path('/home/user/work/ma')
CUT = A / 'andrew/cut'
CROP = A / 'andrew/crop'
AS = A / 'assets'

ONE = CUT / 'v1_38.png'        # finger up = "one"
TALK = CUT / 'v1_6.png'
TALK2 = CUT / 'v1_14.png'
TALK3 = CUT / 'v1_22.png'
OPEN = CUT / 'v1_2.png'
TEE = CUT / 'dk_10.png'
ARMS = CUT / 'old_B003_V2.png'  # approved B003 cutout (real photo)
AV = AS / 'avatar_andrew.jpg'

LP_A = 'LP-A One Feature breakdown (VSL: "I sell ONE GHL feature for $99/month")'
LP_B = 'LP-B SaaSSuite free account (onboarding + training + support)'

# ---- concept-level copy (primary text body + CTA); each variant adds its own hook line on top
CONCEPTS = {
 'C01': dict(name='One feature, $99/mo', angle='Outcome', lp=LP_A, cta='Learn More',
   body="Most people try to sell all of HighLevel. But nobody buys a 45-minute platform tour, so they stall.\n\nTherefore I sell one feature. The one people already want: they type what they want and the software builds it. Your name on it. $99/mo per user.\n\nWatch the free breakdown: which feature, who buys it, and what to charge."),
 'C02': dict(name='Feature overload', angle='Pain', lp=LP_A, cta='Learn More',
   body="You learned every feature, so you pitch every feature. But 50 features sounds like 50 things to learn, and the prospect says \"let me think about it.\"\n\nOne feature sounds like a yes. Therefore that's all I sell now: one feature, one page, one price.\n\nThe free breakdown shows exactly which one."),
 'C03': dict(name='You became the help desk', angle='Pain (support)', lp=LP_B, cta='Sign Up',
   body="Getting the client felt like the win. But then the texts start: logins, passwords, \"how do I…\". Therefore every new client adds hours, not freedom.\n\nSaaSSuite runs the part nobody talks about: onboarding, training videos, AI answers and a support desk with real humans answering your clients' questions.\n\nStart free and give your nights back to yourself."),
 'C04': dict(name='Customer quotes', angle='Proof / testimonial', lp=LP_B, cta='Learn More',
   body="Don't take my word for it.\n\nAgency owners use SaaSSuite to onboard, train and support their HighLevel clients, so they can keep selling instead of answering tickets.\n\nSee how it works. Start free."),
 'C05': dict(name='Us vs them', angle='Comparison', lp=LP_A, cta='Learn More',
   body="Same platform. Two very different businesses.\n\nOne sells everything and spends its life convincing people. The other sells one thing people already want, therefore nobody has to be convinced.\n\nWatch the free breakdown and pick your side."),
 'C06': dict(name='The one-feature math', angle='Math', lp=LP_A, cta='Learn More',
   body="You don't need 100 clients. You need one feature people already want, at a price nobody argues with.\n\n$99/mo per user. Your name on it. The software does the building, therefore you don't trade hours for it.\n\nThe free breakdown walks through the numbers."),
 'C07': dict(name='SaaSSuite feature callouts', angle='Feature callout', lp=LP_B, cta='Sign Up',
   body="Selling the software is half the job. But the other half (onboarding, training, support) is where SaaS businesses quietly die.\n\nSaaSSuite gives your clients a custom menu and dashboard, training videos, AI that answers questions, and a ticket system with real humans behind it.\n\nStart free."),
 'C08': dict(name='Notes app', angle='Native / notes-app', lp=LP_A, cta='Learn More',
   body="Wrote this down so I'd stop overcomplicating it.\n\nOne feature. One page. One video. $99/mo, my name on it.\n\nThe full breakdown is free. Link below."),
 'C09': dict(name='Tweet-style', angle='Native / tweet', lp=LP_A, cta='Learn More',
   body="Posted this and my DMs blew up, so here's the full version.\n\nThe free breakdown shows which HighLevel feature, who buys it, and what to charge."),
 'C10': dict(name='iMessage', angle='Native / text thread', lp=LP_A, cta='Watch More',
   body="The question I get every day: \"which one?\"\n\nHere's the answer, the setup, and the price. Free breakdown below."),
 'C11': dict(name='Sticky note', angle='Ugly / handwritten', lp=LP_A, cta='Learn More',
   body="The rule I wish I'd learned first.\n\nPeople don't buy platforms. They buy one result. Therefore sell one feature, put your name on it, and charge monthly.\n\nFree breakdown below."),
 'C12': dict(name='Founder photo', angle='Founder / Andrew photo-led', lp=LP_A, cta='Learn More',
   body="I'm Andrew. I teach one thing: sell one HighLevel feature, build a SaaS.\n\nI show you which feature, who pays for it, what to charge, and the build on screen. Then SaaSSuite runs onboarding and support so it scales.\n\nStart with the free breakdown."),
 'C13': dict(name='Contrarian', angle='Contrarian', lp=LP_A, cta='Learn More',
   body="Everyone's telling you to build more: more agents, more features, more automations. But your buyer doesn't want more. They want one thing that works.\n\nTherefore the simplest offer wins: one feature, your name, $99/mo.\n\nSee the one I'd pick. Free breakdown below."),
 'C14': dict(name='Persona callout', angle='Callout', lp=LP_A, cta='Learn More',
   body="If that's you, this is the easiest recurring offer in HighLevel right now.\n\nOne feature people already want. They type, it builds. $99/mo per user with your name on it.\n\nWatch the free breakdown."),
 'C15': dict(name='Search / forum native', angle='Native / search + reddit', lp=LP_A, cta='Learn More',
   body="The question everyone types. My honest answer: stop selling the whole platform.\n\nSell one feature, at one price, with your name on it. Free breakdown below."),
 'C16': dict(name='Mistake list / how-to', angle='Education list', lp=LP_A, cta='Learn More',
   body="Save this for your next sales call.\n\nMost HighLevel resellers don't have a product problem. They have a focus problem. Therefore fix the offer before you fix the ads.\n\nFull breakdown is free."),
}

S = []  # specs


def add(id, concept, hook, headline, desc, tpl, v916=False, **kw):
    S.append(dict(id=id, concept=concept, hook=hook, headline=headline, desc=desc, tpl=tpl, v916=v916, **kw))


# C01 One feature (approved editorial look)
add('C01a', 'C01', 'Direct claim', 'I sell ONE GHL feature for $99/mo', 'Free breakdown inside', 'editorial', True,
    head='I sell *one* HighLevel feature for $99 a month.', sub='Not the whole platform. One feature people already want. Let me show you which one.', cut=ARMS, ph=64)
add('C01b', 'C01', 'Stop/start', 'Stop selling all of HighLevel', 'Sell the one they want', 'editorial', True,
    head='Stop selling all of HighLevel. Sell *one* feature.', sub='Nobody has to be convinced. They already want it. $99/mo per user.', cut=ONE, ph=66, acc='#2E5BFF')
add('C01c', 'C01', 'Reframe the want', 'Clients want one thing that works', '$99/mo, your name on it', 'editorial',
    head="Your clients don't want a CRM. They want *one thing* that works.", sub='So sell them that one thing. $99/mo, your name on it.', cut=TALK, ph=64, size=74)
add('C01d', 'C01', 'Three-beat promise', 'One feature. Your name. $99/mo.', 'They type, it builds', 'editorial',
    head='One feature. Your name on it. *$99 a month.*', sub='Customers type what they want and the software builds it. You get paid every month.', cut=TALK3, ph=64, acc='#6C3BFF')

# C02 Feature overload (pain, dark brand)
add('C02a', 'C02', 'Callout + blame flip', 'Why nobody buys "all of GHL"', 'Sell one result instead', 'dark', True,
    kicker='GHL AFFILIATES', head='Selling *all* of HighLevel is why nobody buys.', sub='50 features sounds like 50 things to learn. One feature sounds like a yes.', bullets=['They already want it', 'One page, one price', '$99/mo per user'], cut=TALK2, ph=50, cta='See the one feature →')
add('C02b', 'C02', 'Demo length pain', 'Your 45-min demo is the problem', 'Nobody buys a tour', 'dark',
    head='Your demo is 45 minutes. *That\'s the problem.*', sub='Nobody buys a platform tour. They buy one result.', bullets=['One feature', 'One page', 'One price: $99/mo'], cut=TALK, ph=50, sw=600)
add('C02c', 'C02', 'Less is more', 'You need one feature that sells', 'Not more features', 'dark',
    head="You don't need more features. You need *one* that sells.", bullets=['They already want it', 'They build it themselves', 'You get $99/mo per user'], cut=ONE, ph=52)
add('C02d', 'C02', 'Hour-long explain', "If it takes an hour, it won't sell", 'Pick the one-page offer', 'dark',
    kicker='HARD TRUTH', head="If you have to explain it for an hour, *it won't sell.*", sub='The offers that sell themselves fit on one page. Here\'s the one I use.', cut=TALK3, ph=48, cta='Watch the breakdown →')

# C03 Support pain (photo-led, real studio frames)
add('C03a', 'C03', 'Identity flip: help desk', 'Stop being the help desk', 'SaaSSuite handles support', 'photo', True,
    photo=CROP / 'v1_14.jpg', tag='For HighLevel SaaS owners', head='Signed the client. Now you\'re their *IT help desk.*', sub='Training videos, AI answers and real humans on support. You get your nights back.')
add('C03b', 'C03', 'Timestamp pain', 'Not your text to answer', 'Real humans answer it', 'photo', True,
    photo=CROP / 'v1_22.jpg', tag='11:47 PM', head='“How do I reset my password?”', sub="That text shouldn't be yours to answer. With SaaSSuite, it isn't.", size=78)
add('C03c', 'C03', 'Hard part is keeping', 'Keeping clients is the hard part', 'Onboarding + support, done', 'photo',
    photo=CROP / 'dk_10.jpg', head='Getting clients was hard. *Keeping them* is harder.', sub='Onboarding, training and support, done for you inside SaaSSuite.')
add('C03d', 'C03', 'Churn myth', "It's not price. It's support.", 'Fix the real churn cause', 'photo',
    photo=CROP / 'v1_6.jpg', head="Your SaaS isn't churning because of price. *It's support.*", sub='Confused clients cancel. Supported clients stay. SaaSSuite gives them both training and humans.', size=76)

# C04 Proof quotes (real words, transcribed from testimonial videos)
add('C04a', 'C04', 'Quote: real humans', '"Real humans" on support', 'Rob, SaaSSuite customer', 'quote', True,
    quote="They have *real humans* on the back answering all of your clients' questions.", name='Rob', role='SaaSSuite customer', face=AS / 't_rob.jpg', fpos='50% 30%')
add('C04b', 'C04', 'Quote: before/after', '"Now I can scale"', 'Brentney, SaaSSuite customer', 'quote', True,
    quote="I didn't know how to support my customers once I got them signed up… *Now I have a clear plan and I can scale.*", name='Brentney', role='SaaSSuite customer', face=AS / 't_brentney.jpg', fpos='50% 25%', size=58, acc='#C2410C')
add('C04c', 'C04', 'Quote: follows through', '"Always follows through"', 'Ben, agency owner', 'quote', True,
    quote='He\'s been a great resource, *always follows through* with what he says he\'s going to do.', name='Ben', role='Agency owner, builds HighLevel for clients', face=AS / 't_ben.jpg', fpos='50% 40%', bg='#EEF3FB', acc='#2E5BFF',
    foot='Real customer, real words', pill='Work with Andrew →')
add('C04d', 'C04', 'Quote: customize dashboard', '"Customize your entire dashboard"', 'Rob on SaaSSuite', 'quote',
    quote='I love how you can customize the menu, love how you can *customize your entire dashboard.*', name='Rob', role='SaaSSuite customer', face=AS / 't_rob.jpg', fpos='50% 30%', bg='#111', fg='#F5F5F5', acc='#FFD23F')
add('C04e', 'C04', 'Quote: on top of it', '"On top of everything for us"', 'Jessica, client', 'quote',
    quote='This has been so helpful. *You\'re on top of everything for us.*', name='Jessica', role='Client, on a call with Andrew', face=AS / 't_jessica.jpg', fpos='50% 35%', bg='#FFF8E7', acc='#C2410C', size=70)

# C05 Us vs them
add('C05a', 'C05', 'Split: all vs one', 'All of GHL vs one feature', 'Pick the easy sale', 'compare', True,
    head='Selling all of GHL vs. selling *one* feature', lt='All of GHL', left=['45-minute demo', 'They need convincing', 'You do the setup', 'They churn in month 2'],
    rt='One feature', right=['One-page pitch', 'They already want it', 'The software builds it', '$99/mo, every month'], foot='Andrew George · The One Feature guy')
add('C05b', 'C05', 'Course vs system', 'A $997 course vs a system', 'Use it tomorrow', 'compare',
    head='A $997 course vs. a system you use *tomorrow*', lt='The course', left=['Learn the theory', 'Figure out the tech', 'Build the offer yourself', 'Support is your problem'],
    rt='SaaSSuite', right=['Offer already built', 'Onboarding done for you', 'Training videos for clients', 'Real humans on support'], foot='SaaSSuite · start free')
add('C05c', 'C05', 'Agency vs SaaS', 'Agency retainer vs one-feature SaaS', 'Recurring without revisions', 'compare',
    head='Agency retainer vs. one-feature *SaaS*', lt='Agency', left=['Custom work for every client', 'Revisions forever', 'Stops when you stop', "You're the bottleneck"],
    rt='One-feature SaaS', right=['Same product for everyone', 'They build it themselves', '$99/mo recurring', 'Support handled for you'], foot='Andrew George · The One Feature guy')
add('C05d', 'C05', 'Build vs resell AI', 'Building AI vs reselling it', 'Skip the code', 'compare',
    head='Building an AI tool vs. *reselling* one', lt='Build it', left=['Learn to code', 'Months before launch', 'You fix every bug', 'You find the buyers'],
    rt='Resell it', right=['No code', 'Live this week', 'HighLevel runs the tech', 'People already want it'], foot='One feature. Your name. $99/mo.')

# C06 Math
add('C06a', 'C06', 'Scale ladder', 'The one-feature math', 'Same feature, more users', 'math', True,
    head='The one-feature math', rh='$99/MO PER USER', rows=[('1 user', '$99/mo'), ('10 users', '$990/mo'), ('25 users', '$2,475/mo'), ('50 users', '$4,950/mo')],
    note='Same feature. Same setup. Your name on it.')
add('C06b', 'C06', 'Niche math: gyms', 'What 20 gym owners pay you', 'Every month', 'math',
    head='What 20 gym owners pay you', rh='ONE FEATURE · ONE NICHE', rows=[('Gym owners', '20'), ('Price per month', '$99'), ('Sites you build', '0'), ('Every month', '$1,980')],
    note='They type what they want. The software builds the site.')
add('C06c', 'C06', 'Goal backsolve', "You don't need 100 clients", '51 users = $5k/mo', 'math',
    head="You don't need 100 clients.", rh='GOAL: $5,000/MO', rows=[('Price per user', '$99/mo'), ('Users needed', '51'), ('Custom builds', '0'), ('Monthly', '$5,049')],
    note='One feature people already want beats a hundred custom projects.', bg='#DDE7F7')
add('C06d', 'C06', 'Yearly value', 'One user = $1,188 a year', 'Recurring, not one-off', 'math',
    head='One user at $99/mo is *$1,188* a year.', rh='PER USER, PER YEAR', rows=[('Setup fee', 'optional'), ('Monthly', '$99'), ('Months', '× 12'), ('Per user / year', '$1,188')],
    note='Now picture that with your name on it, times every client you already have.', size=60)

# C07 SaaSSuite feature callouts (real GHL UI stills)
add('C07a', 'C07', 'After-signup checklist', 'What clients need after they sign', 'All inside SaaSSuite', 'features', True,
    head='Everything your clients need *after* they sign.', shot=AS / 'ui_cs_20.jpg', items=['Custom menu + dashboard', 'Training videos for your clients', 'AI that answers their questions', 'Support tickets, real humans'])
add('C07b', 'C07', 'Hidden half', 'The part nobody shows you', 'Support, handled', 'features',
    head='The part of SaaS nobody shows you: *support.*', shot=AS / 'ui_cs_60.jpg', items=['Onboard new clients', 'Educate with training videos', 'Support with real humans', 'Your brand on all of it'])
add('C07c', 'C07', 'Three verbs', 'Onboard. Educate. Support.', 'Done for you', 'features',
    head='Onboard. Educate. Support. *Done for you.*', shot=AS / 'ui_ds_220.jpg', items=['Clients learn the software', 'Questions get answered', 'You keep selling', 'They keep paying'])
add('C07d', 'C07', 'Division of labour', 'Sell it. SaaSSuite runs the rest.', 'Start free', 'features',
    head='You sell the feature. *SaaSSuite* runs the rest.', shot=AS / 'ui_cs_140.jpg', items=['Onboarding flow', 'Training library', 'AI + human support desk', 'Custom dashboard'])

# C08 Notes app
add('C08a', 'C08', 'Notes: the method', 'How I sell ONE HighLevel feature', 'Free breakdown', 'notes', True,
    head='How I sell ONE HighLevel feature', rows=['-Explain all of GHL', '-Hour-long demos', '+Pick one feature they already want', '+One page. One video.', '+$99/mo, my name on it'])
add('C08b', 'C08', 'Notes: client asks', 'What clients asked me this week', 'They already want it', 'notes',
    head='Things clients asked me this week', rows=['=“Can you build me a website?”', '=“Can it have my logo?”', '=“How much is it?”', '+$99/mo. They type it, it builds.'])
add('C08c', 'C08', 'Notes: old vs now', 'My SaaS to-do list, fixed', 'Support handled', 'notes',
    head='SaaS to-do list', rows=['-Answer support texts at midnight', '-Record onboarding videos', '-Write training docs', '+SaaSSuite handles it', '+Go sign more clients'], date='Monday 7:02 AM')
add('C08d', 'C08', 'Notes: AI money ideas', 'Making money with AI, simplified', 'No code needed', 'notes',
    head='Ways to make money with AI', rows=['-Learn to code', '-Build my own AI agent', '-Start an "AI agency"', '+Resell one feature people already use'])

# C09 Tweet-style
add('C09a', 'C09', 'Tweet: agents vs one', 'Everyone builds agents. I sell one.', 'Free breakdown', 'tweet', True,
    avatar=AV, text="Everyone's out here building AI agents.\n\nI just sell *one* HighLevel feature for $99 a month.", size=70)
add('C09b', 'C09', 'Tweet: unpopular opinion', "Don't sell all of HighLevel", "That's the whole business", 'tweet',
    avatar=AV, text="Unpopular opinion: you don't need to sell all of HighLevel.\n\nPick *one* feature people already want. Put your name on it. Charge $99/mo.\n\nThat's the whole business.", size=56)
add('C09c', 'C09', 'Tweet: keeping clients', 'Keeping clients is the hard part', 'Build support once', 'tweet',
    avatar=AV, dark=True, text="Getting the client: hard.\nKeeping the client: harder.\n\nThe SaaS owners who last don't do support themselves. *They build a support system once.*", size=58)
add('C09d', 'C09', 'Tweet: one that pays', 'Clients care about one feature', 'The one that pays them', 'tweet',
    avatar=AV, text="Your clients don't care that HighLevel has hundreds of features.\n\nThey care about *the one that makes them money.*", size=66)

# C10 iMessage statics (static versions of the B002 SMS videos that were approved)
CARD = (CROP / 'v1_38.jpg', 'I sell ONE GHL Feature for $99/month, and this is how…')
add('C10a', 'C10', 'Text: vibe coding', 'You\'ve heard of vibe coding?', 'I resell it with my name', 'imessage', True,
    avatar=AV, msgs=[('l', "You've heard of vibe coding right"), ('r', 'Yeah why'), ('l', 'I resell it. With my name on it'), ('r', 'How??'), ('card', CARD)])
add('C10b', 'C10', 'Text: which one', 'Easier to sell than everything else', 'Which one? Watch this', 'imessage',
    avatar=AV, msgs=[('l', 'This ONE GHL feature is easier to sell than everything else combined'), ('r', 'Which one'), ('l', 'Watch this'), ('card', CARD)])
add('C10c', 'C10', 'Text: midnight support', 'Stop doing support at midnight', 'Real humans + training videos', 'imessage',
    avatar=AV, msgs=[('r', 'Client texted me at midnight about their password again 😩'), ('l', 'Why are you doing support yourself'), ('r', 'Who else is gonna do it??'), ('l', 'SaaSSuite. Training videos + real humans on support'), ('r', 'Wait that exists?')])
add('C10d', 'C10', 'Text: show me', 'Everyone builds AI agents', 'I sell one feature', 'imessage',
    avatar=AV, msgs=[('l', "Everyone's out here building AI agents"), ('l', 'I just sell ONE feature for $99 a month'), ('r', 'Show me'), ('card', CARD)])

# C11 Sticky notes
add('C11a', 'C11', 'Sticky: stop all', 'Stop selling all of HighLevel', 'Sell one. $99/mo.', 'sticky', True,
    text='Stop selling *all* of HighLevel.', small='Sell one feature. $99/mo.', size=104)
add('C11b', 'C11', 'Sticky: already want', 'They already want it', 'The one-feature rule', 'sticky',
    text='Nobody has to be convinced. *They already want it.*', small='the one-feature rule', cut=ONE, ph=44, size=88, bg='linear-gradient(160deg,#E8E2D6,#CFC6B6)')
add('C11c', 'C11', 'Sticky: churn = confusion', "Clients churn from confusion", 'Fix onboarding first', 'sticky',
    text="Clients don't churn from price. They churn from *confusion.*", small='fix onboarding first', size=90, rot=2)
add('C11d', 'C11', 'Sticky: 3 steps', 'They build. I get paid.', 'The 3-step version', 'sticky',
    text='1. Turn off everything else\n2. One page. One video.\n3. *They build. I get paid.*', small='', size=80, w=880)

# C12 Founder photo-led (real frames)
add('C12a', 'C12', 'Founder: the one', 'The one feature I\'d sell in 2026', 'From the One Feature guy', 'photo', True,
    photo=CROP / 'v1_38.jpg', tag='Andrew George · Founder, SaaSSuite', head='This is *the one* HighLevel feature I\'d sell in 2026.', sub='Who buys it, what to charge, and the setup. Free breakdown.')
add('C12b', 'C12', 'Founder: already want', 'The feature people already want', 'Free breakdown', 'photo',
    photo=CROP / 'v1_2.jpg', head='Here\'s the one HighLevel feature people *already want.*', sub="You don't convince anyone. You just put your name on it.")
add('C12c', 'C12', 'Founder: the promise', 'Which feature, who buys, what to charge', 'All in one breakdown', 'photo', True,
    photo=CROP / 'dk_10.jpg', head="I'll show you which feature, who buys it, and *what to charge.*", sub='Sell one HighLevel feature. Build a SaaS.')
add('C12d', 'C12', 'Founder: one thing', 'I teach one thing', 'Sell one feature, build a SaaS', 'photo',
    photo=CROP / 'cc_5.jpg', tag='Andrew George', head='I teach one thing: *sell one feature, build a SaaS.*', sub='Then SaaSSuite runs onboarding and support so it scales.')

# C13 Contrarian
add('C13a', 'C13', "Contrarian: don't code", "Don't learn to code", 'Get paid when others build', 'dark', True,
    kicker='CONTRARIAN TAKE', head="Don't learn to code. *Get paid when other people vibe code.*", size=84, sub='They type what they want. It builds. You get $99/mo per user.', cut=OPEN, ph=48)
add('C13b', 'C13', 'Contrarian: no agents', 'Stop building AI nobody asked for', 'Sell the one they use', 'editorial',
    head='Stop building AI agents *nobody asked for.*', sub='Sell the one AI feature people are already typing into. $99/mo per user.', cut=TALK3, ph=64, acc='#C2410C')
add('C13c', 'C13', 'Contrarian: fewer', 'More features won\'t save your SaaS', 'Fewer will', 'dark',
    head="More features won't save your SaaS. *Fewer will.*", bullets=['One feature', 'One niche', 'One price'], cut=TALK2, ph=50)
add('C13d', 'C13', 'Contrarian: boring', 'The best SaaS offer is boring', 'One feature, one price', 'editorial',
    head='The best SaaS offer is *boring:* one feature, one price.', sub='Boring sells. Boring renews. Let me show you mine.', cut=ARMS, ph=62, acc='#6C3BFF')

# C14 Persona callouts (big word, approved V13 look)
add('C14a', 'C14', 'Callout: GHL affiliates', 'GHL affiliates: sell ONE feature', 'Easier than everything else', 'bigword', True,
    pre='GHL affiliates:', word='ONE', head='feature is easier to sell than everything else combined.', sub='Nobody has to be convinced.', arrows=['No convincing', 'They already want it', 'Your name on it'], cut=ONE, ph=48)
add('C14b', 'C14', 'Callout: agency owners', 'Agency owners: $99/mo per user', 'One feature, your name', 'bigword',
    pre='Agency owners:', word='$99', head='a month, per user, for one feature with your name on it.', sub='No custom builds. No revisions.', cut=TALK, ph=46, acc='#E5484D', bg='#FFF4EE')
add('C14c', 'C14', 'Callout: coaches', 'Coaches: add recurring revenue', 'One feature, your brand', 'bigword',
    pre='Coaches & consultants:', word='1', wsize=420, head='feature. Your brand. Recurring revenue.', sub='Sell software to the clients you already coach.', cut=TALK3, ph=48, acc='#6C3BFF', bg='#F3EFFF')
add('C14d', 'C14', 'Callout: web designers', 'Web designers: let them type it', 'You get $99/mo', 'bigword',
    pre='Web designers:', word='TYPE.', wsize=250, head="That's all your customer does. The site builds itself.", sub='You get $99/mo per user.', cut=TEE, ph=46, acc='#14804A', bg='#EEF8F1')

# C15 Search / forum native (all results are Andrew's own content)
add('C15a', 'C15', 'Search: make money with GHL', 'How to make money with HighLevel', 'One feature, $99/mo', 'search',
    query='how to make money with gohighlevel', results=[
        ('youtube.com › @andrewpreneurship', 'I sell ONE GHL Feature for $99/month, and this is how…', 'Skip the 45-minute demo. Pick *one feature* people already want, put your name on it and charge monthly.'),
        ('saassuite.ai', 'SaaSSuite: onboard, train and support your HighLevel clients', 'Training videos, AI answers and *real humans* on support, under your brand.')])
add('C15b', 'C15', 'Reddit: AMA', 'I sell one HighLevel feature. AMA.', 'Ask me anything', 'reddit',
    sub='r/gohighlevel', user='u/andrewpreneurship (Andrew George)', title='I sell ONE HighLevel feature for $99/mo per user. AMA.',
    body="Not the whole platform. One feature people already type into: they say what they want, it builds.\n\nNo demo. No convincing. *They already want it.* Ask me which one, who buys it, and what I charge.", ups='2.1k', cm='486')
add('C15c', 'C15', 'Search: client support', 'GHL client support, handled', 'Real humans + training', 'search',
    query='how to support my gohighlevel saas clients', results=[
        ('saassuite.ai', 'SaaSSuite: support your HighLevel clients without doing it yourself', 'Custom dashboard, training videos, AI answers and a ticket desk with *real humans*.'),
        ('youtube.com › @andrewpreneurship', 'Onboard. Educate. Support. The part of SaaS nobody shows you', 'Why clients churn from *confusion*, not price, and the system that fixes it.')])
add('C15d', 'C15', 'Reddit: churn PSA', "PSA: it's not price, it's support", 'Fix churn at the source', 'reddit',
    sub='r/gohighlevel', user='u/andrewpreneurship (Andrew George)', title="PSA: your SaaS clients aren't cancelling because of price",
    body="They cancel because they never learned the software. Therefore the fix isn't a discount, it's *onboarding, training and support.*\n\nI built SaaSSuite to handle exactly that. Happy to answer questions below.", ups='1.3k', cm='207')

# C16 Lists / how-to + retro dialog
add('C16a', 'C16', 'List: why affiliates stall', '3 reasons GHL affiliates stall', 'Save this', 'list',
    kicker='Save this', head='3 reasons GHL affiliates stall', items=[('They sell the whole platform', 'Nobody buys a tour. They buy one result.'),
        ('They do support themselves', 'Every new client adds hours, not freedom.'), ('They price custom work', 'Recurring beats custom. $99/mo, every month.')], foot='Andrew George · The One Feature guy')
add('C16b', 'C16', 'List: 3-step method', 'How I sell one feature in 3 steps', 'They build. I get paid.', 'list', True,
    kicker='The method', head='How I sell one feature, in 3 steps', items=[('Turn off everything else', "Hide what they don't use."),
        ('One page. One video.', 'Show the one result they want.'), ('They build. I get paid.', '$99/mo per user, my name on it.')], foot='Andrew George · The One Feature guy', bg='#F2F6FF', acc='#2E5BFF')
add('C16c', 'C16', 'List: after signup', 'What happens after a client signs', 'SaaSSuite runs it', 'list',
    kicker='After the sale', head='What should happen after a client signs', items=[('Onboarding', 'A guided setup so they see value on day one.'),
        ('Education', 'Training videos so they stop asking you.'), ('Support', 'AI answers first, real humans behind it.')], foot='SaaSSuite runs all three · start free', bg='#F0FAF4', acc='#14804A')
add('C16d', 'C16', 'Retro error: feature overload', 'Error: too many features', 'Try selling one', 'dialog',
    title='GHL ERROR 001: FEATURE OVERLOAD', body='Too many features.\n\nYour prospect stopped listening at feature #4.\n\nTry selling *one*.', buttons=['SELL ONE', 'KEEP DEMOING'])


def _clean(t):
    import re
    return re.sub(r'[*~_]', '', t).replace('\n', ' ').strip()


def primary(s):
    c = CONCEPTS[s['concept']]
    if s['tpl'] == 'quote':
        first = f'"{_clean(s["quote"])}" ({s["name"]}, {s["role"]})'
    elif s['tpl'] in ('tweet',):
        first = _clean(s['text'].split('\n\n')[0])
    elif s['tpl'] == 'imessage':
        first = _clean([m for w, m in s['msgs'] if w != 'card'][0])
    elif s['tpl'] == 'reddit':
        first = _clean(s['title'])
    elif s['tpl'] == 'search':
        first = f'You searched "{s["query"]}".'
    elif s['tpl'] == 'sticky':
        first = _clean(s['text'])
    elif s['tpl'] == 'dialog':
        first = 'Error: too many features.'
    elif s['tpl'] == 'bigword':
        first = f"{_clean(s['pre'])} {_clean(s['word']).rstrip('.')} {_clean(s['head'])}"
    elif s['tpl'] == 'notes':
        first = _clean(s['head']) + ':'
    else:
        first = _clean(s['head'])
    return first + '\n\n' + c['body']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--no916', action='store_true')
    a = ap.parse_args()
    only = set(a.only.split(',')) if a.only else None
    ratios = ('45',) if a.no916 else ('45', '916')
    for s in S:
        if s.get('acc', 1) is None:
            s.pop('acc')
    render_all(S, OUT / 'statics', ratios, only)
    with open(OUT / 'manifest.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'concept_id', 'concept', 'angle', 'hook_name', 'format', 'template', 'file_4x5', 'file_9x16',
                    'headline', 'primary_text', 'description', 'cta_button', 'landing_page'])
        for s in S:
            c = CONCEPTS[s['concept']]
            w.writerow([s['id'], s['concept'], c['name'], c['angle'], s['hook'], 'static', s['tpl'], f"statics/{s['id']}.jpg",
                        f"statics/{s['id']}_916.jpg" if s['v916'] else '', s['headline'], primary(s), s['desc'], c['cta'], c['lp']])
    print(len(S), 'creatives;', sum(1 for s in S if s['v916']), 'with 9:16')


if __name__ == '__main__':
    main()
