#!/usr/bin/env python3
"""Ad specs for the testimonials-a stream (Nov 7, 2026). Writes specs.json next to this file.
Times are source seconds, picked from word timestamps in transcripts/<person>.json."""
import json, os
W = '/home/user/work/ta'
H = os.path.dirname(os.path.abspath(__file__))
people = {
 'mark': dict(src=f'{W}/src/mark.raw', tx=f'{W}/tx/mark/transcript.json', crop=[216, 256, 650, 1156], face=[0.5, 0.36],
              name='Mark Cleary', role='Personal trainer · @mark_cleary_fitness', first='Mark'),
 'lee': dict(src=f'{W}/src/lee.raw', tx=f'{W}/tx/lee/transcript.json', crop=[170, 220, 740, 1316], face=[0.5, 0.3],
             name='Lee Knaz', role='Coach · @leeknaz888', first='Lee'),
 'ben': dict(src=f'{W}/src/ben.raw', tx=f'{W}/tx/ben/transcript.json', crop=[0, 0, 1080, 1920], face=[0.42, 0.38],
             name='Ben', role='Agency owner', first='Ben'),
 'jessica': dict(src=f'{W}/src/jessica.raw', tx=f'{W}/tx/jessica/transcript.json', crop=[772, 0, 607, 1080], face=[0.5, 0.45],
                 name='Jessica Garcia', role='Client', first='Jessica'),
 'tania': dict(src=f'{W}/src/tania2.raw', tx=f'{W}/tx/tania2/transcript.json', layout='call', screen=[0, 225, 1440, 765],
               face_img=f'{W}/tania_face.png', andrew_img=f'{W}/andrew_face.png',
               name='Tania Cazin', role='Sales trainer · Stalwart Sales', first='Tania'),
}
music = [
 {'file': f'{W}/music/m714.mp3', 'offset': 6, 'credit': 'Mixkit #714 "Staring at the Night Sky"'},
 {'file': f'{W}/music/m606.mp3', 'offset': 4, 'credit': 'Mixkit #606 "The Long Road"'},
 {'file': f'{W}/music/music-1168.mp3', 'offset': 10, 'credit': '"Coffee or Tea" by Michael Ramir C., Mixkit #1168'},
 {'file': f'{W}/music/m565.mp3', 'offset': 8, 'credit': 'Mixkit #565 "Echoes"'},
 {'file': f'{W}/music/music-130.mp3', 'offset': 16, 'credit': '"Tech House vibes" by Alejandro Mañaga (A. M.), Mixkit #130'},
]
M = dict(five=[4.90, 9.32], five_s=[6.78, 9.32], trainer=[9.40, 12.50], stuck=[13.12, 15.95], sys1=[16.30, 17.25],
         sys2=[18.76, 22.70], reply=[23.02, 25.95], salescall=[28.45, 35.80], longterm=[35.92, 39.50], posts=[42.30, 52.35],
         no1=[53.45, 54.90], no2=[57.55, 58.98], no3=[59.25, 65.80], former=[66.10, 72.98], alldrew=[73.60, 77.20],
         nextyear=[78.70, 80.55], wrong=[83.98, 85.95], thanks=[86.10, 87.90])
L = dict(tremendous=[0.0, 3.25], expand=[3.45, 7.25], noidea=[7.80, 12.45], plan=[12.78, 18.45], planfull=[12.78, 26.10],
         skills=[26.90, 38.70], understand=[38.95, 45.95], cares=[50.40, 58.45], cares_s=[53.78, 58.45],
         chance=[60.60, 70.50], kindest=[70.62, 72.55], worth=[77.05, 80.95], worth_s=[79.95, 80.95])
Bn = dict(shout=[0.0, 2.75], helpful=[2.85, 6.95], build=[7.45, 13.55], resource=[14.15, 18.15], care=[18.50, 20.46],
          recommend=[20.46, 22.85], full=[0.0, 22.85])
J = dict(helpful=[0.0, 0.95], top=[1.60, 2.98], many=[3.05, 4.98], ontop=[5.25, 7.95], thanks=[8.05, 8.95])
T = dict(hours=[426.10, 428.80], simple=[432.90, 436.50], fix=[243.15, 245.78], why=[251.55, 261.80], believe=[479.75, 483.40],
         promise=[555.40, 556.95], sendall=[559.65, 568.30], nm1=[736.92, 738.70], nm2=[741.18, 744.25], nm3=[746.30, 748.20],
         knowledge=[749.80, 756.40], dealt=[758.20, 759.42], expert=[802.05, 809.95], expert_s=[804.95, 809.95],
         love=[1049.20, 1051.75])
T['notmarketer'] = None
S = {'mark': M, 'lee': L, 'ben': Bn, 'jessica': J, 'tania': T}


def segs(p, names):
    out = []
    for n in names.split():
        if p == 'mark' and n == 'saidno': out += [M['no1'], M['no2'], M['no3']]; continue
        if p == 'mark' and n == 'system': out += [M['sys1'], M['sys2']]; continue
        if p == 'tania' and n == 'notmarketer': out += [T['nm1'], T['nm2'], T['nm3']]; continue
        out.append(S[p][n])
    return out


def hook(t, text='', sub='', card=''):
    return {'type': t, 'text': text, 'sub': sub, 'card': card}


ads = []
def ad(i, p, names, h, top, cls, asp=('916',)):
    ads.append({'id': i, 'person': p, 'segs': segs(p, names), 'hook': h, 'topline': top, 'class': cls,
                'aspect': list(asp), 'music': len(ads) % len(music), 'moments': names})

B45 = ('916', '45')
# ---- Mark Cleary (88 s selfie testimonial)
ad('mark-01', 'mark', 'five stuck system', hook('stat', '5', 'online clients in *under a month*'), '5 CLIENTS IN UNDER A MONTH', '15s', B45)
ad('mark-02', 'mark', 'five_s stuck system', hook('quote', "He's helped me land *five online clients*"), "MARK'S FIRST MONTH", '15s')
ad('mark-03', 'mark', 'stuck system five_s', hook('question', 'Stuck on *bringing in new leads?*'), 'A NEW LEAD SYSTEM', '15s')
ad('mark-04', 'mark', 'salescall longterm', hook('headline', "Sales calls that *don't feel* like sales calls"), 'HELP, NOT A PITCH', '15s')
ad('mark-05', 'mark', 'saidno alldrew', hook('card', card='They said *no* to the sale. Then this happened.'), '', '15s', B45)
ad('mark-06', 'mark', 'former alldrew', hook('quote', "That was all *Andrew's idea.*"), 'A FORMER CLIENT, RE-SIGNED', '15s')
ad('mark-07', 'mark', 'trainer stuck system reply five wrong', hook('stat', '12 yrs', 'a personal trainer. *Stuck on leads.*'), 'FROM STUCK TO 5 CLIENTS', '30s')
ad('mark-08', 'mark', 'posts reply longterm five_s', hook('question', 'Do your DMs *turn into clients?*'), 'POSTS → DMS → CLIENTS', '30s')
ad('mark-09', 'mark', 'stuck five system reply salescall', hook('headline', 'Stuck on leads → *5 new clients* in under a month'), '5 CLIENTS IN UNDER A MONTH', '30s', B45)
ad('mark-10', 'mark', 'saidno former wrong', hook('quote', 'They said *no to the sale.* Then they signed.'), '2 CLIENTS WON BACK', '30s')
ad('mark-11', 'mark', 'five trainer stuck system reply salescall longterm posts saidno wrong',
   hook('card', card='How a personal trainer landed *5 clients* in under a month'), '', '60s', B45)
ad('mark-12', 'mark', 'five stuck system saidno former nextyear wrong', hook('stat', '5', 'new clients in a month. *Plus 2 won back.*'), '5 NEW + 2 WON BACK', '45s')
ad('mark-13', 'mark', 'trainer five wrong', hook('question', 'Personal trainer? *Watch this.*'), '5 CLIENTS IN UNDER A MONTH', '15s')
ad('mark-14', 'mark', 'wrong five stuck system salescall', hook('quote', "You definitely *can't go wrong.*"), 'MARK, 1 MONTH IN', '30s')
# ---- Lee Knaz (82 s)
ad('lee-01', 'lee', 'tremendous noidea plan', hook('quote', 'The support has been *tremendous*'), 'A COACH, BRAND NEW TO SOCIAL', '15s', B45)
ad('lee-02', 'lee', 'noidea plan worth_s', hook('question', "No idea what you're doing *on social media?*"), 'A PLAN THAT WORKS', '15s')
ad('lee-03', 'lee', 'expand noidea plan', hook('headline', 'A coach, *brand new* to social media'), 'FROM NO IDEA TO A PLAN', '15s')
ad('lee-04', 'lee', 'kindest tremendous cares_s worth_s', hook('quote', 'One of the *kindest humans* you would meet'), 'LEE KNAZ, COACH', '15s')
ad('lee-05', 'lee', 'expand noidea worth', hook('card', card='Brand new to social media? *Watch this.*'), '', '15s')
ad('lee-06', 'lee', 'noidea planfull cares_s worth_s', hook('headline', 'No plan → *a plan that works*'), 'EFFECTIVE AND EASY TO FOLLOW', '30s', B45)
ad('lee-07', 'lee', 'chance kindest tremendous plan worth', hook('question', 'Looking for *real guidance* on social media?'), 'GIVE ANDREW A CHANCE', '30s')
ad('lee-08', 'lee', 'cares expand noidea plan', hook('quote', "He *knows what he's doing* and *cares*"), 'A COACH, BRAND NEW TO SOCIAL', '30s')
ad('lee-09', 'lee', 'tremendous expand noidea planfull understand cares chance kindest worth',
   hook('card', card='What happened when a coach got *real guidance* on social media'), '', '60s', B45)
ad('lee-10', 'lee', 'skills understand planfull worth_s', hook('headline', 'Expert skills. *A plan a beginner can follow.*'), 'MET WHERE HE WAS', '45s')
ad('lee-11', 'lee', 'worth tremendous plan', hook('quote', '*Absolutely worth it.*'), 'LEE KNAZ, COACH', '15s')
ad('lee-12', 'lee', 'expand noidea plan understand kindest worth_s', hook('question', 'Need a plan for *social media?*'), 'A PLAN THAT WORKS', '30s')
# ---- Ben (23 s)
ad('ben-01', 'ben', 'resource build recommend', hook('quote', 'Always follows through with *what he says*'), 'AGENCY OWNER, HIGHLEVEL BUILD', '15s', B45)
ad('ben-02', 'ben', 'build resource recommend', hook('question', 'Need help building out *GoHighLevel?*'), 'BUILT FOR US AND OUR CLIENTS', '15s')
ad('ben-03', 'ben', 'helpful build recommend', hook('headline', "An agency owner on *Andrew's team*"), 'AGENCY OWNER, HIGHLEVEL BUILD', '15s')
ad('ben-04', 'ben', 'shout helpful build', hook('card', card="What agency owners say about *Andrew's team*"), '', '15s')
ad('ben-05', 'ben', 'care shout helpful build resource recommend', hook('quote', "He's taken *really good care* of us"), 'AGENCY OWNER, HIGHLEVEL BUILD', '30s', B45)
ad('ben-06', 'ben', 'build helpful resource care recommend', hook('headline', 'HighLevel built out *for us and our clients*'), 'AGENCY OWNER', '30s')
ad('ben-07', 'ben', 'recommend resource care helpful', hook('question', 'Thinking about *working with Andrew?*'), 'AGENCY OWNER', '15s')
ad('ben-08', 'ben', 'full', hook('card', card='Real agency. *Real build.*'), '', '30s', B45)
ad('ben-09', 'ben', 'recommend build care', hook('quote', '*I highly recommend it.*'), 'AGENCY OWNER, HIGHLEVEL BUILD', '15s')
ad('ben-10', 'ben', 'build resource', hook('headline', 'Builds for *our clients* and for *us*'), 'AGENCY OWNER', '15s')
# ---- Jessica Garcia (9 s call clip)
ad('jessica-01', 'jessica', 'top helpful many ontop thanks', hook('quote', "You're *on top of everything* for us"), 'CLIENT CALL', '15s', B45)
ad('jessica-02', 'jessica', 'helpful top many ontop thanks', hook('question', "Want a team that's *actually on top of it?*"), 'CLIENT CALL', '15s')
ad('jessica-03', 'jessica', 'helpful top many ontop thanks', hook('card', card='*Unscripted.* Straight from a client call.'), '', '15s')
ad('jessica-04', 'jessica', 'helpful ontop top thanks', hook('headline', '*So helpful.* So on top of it.'), 'CLIENT CALL', '15s')
# ---- Tania Cazin (17-min recorded support call, camera off: her real photo + call audio)
ad('tania-01', 'tania', 'hours fix believe simple', hook('card', card='She was *20 hours in.* Then she got on a call.'), '', '15s', B45)
ad('tania-02', 'tania', 'love hours fix believe', hook('quote', "I don't know you, but *I love you so much*"), '20 HOURS STUCK, ONE CALL', '15s')
ad('tania-03', 'tania', 'hours fix why', hook('question', '20 hours stuck in *GoHighLevel?*'), 'ONE TRIGGER LINK', '15s')
ad('tania-04', 'tania', 'knowledge dealt expert_s', hook('quote', 'They have to have *your knowledge*'), 'SALES TRAINER ON HIRING HELP', '15s')
ad('tania-05', 'tania', 'notmarketer expert_s', hook('headline', '*Not a marketer?* Hire an actual expert.'), 'SALES TRAINER ON HIRING HELP', '15s')
ad('tania-06', 'tania', 'sendall love', hook('quote', 'I will send *everybody* to you'), 'SALES TRAINER, STALWART SALES', '15s')
ad('tania-07', 'tania', 'hours fix why believe simple love', hook('card', card="A sales trainer's *real call* with Andrew"), '', '30s', B45)
ad('tania-08', 'tania', 'notmarketer knowledge dealt expert_s promise', hook('question', 'Spending *a bazillion dollars* on marketing?'), 'HIRE THE EXPERT', '30s')
ad('tania-09', 'tania', 'hours simple fix why believe knowledge expert_s love', hook('headline', '*20 hours* stuck. One call.'), 'THE TRIGGER LINK FIX', '45s', B45)
ad('tania-10', 'tania', 'hours fix believe simple', hook('stat', '20 hrs', 'stuck on one setup. *Fixed on one call.*'), 'ONE TRIGGER LINK', '15s')
ad('tania-11', 'tania', 'promise sendall knowledge love', hook('quote', 'I promise you, *this is going to pay off*'), 'SALES TRAINER, STALWART SALES', '30s')
ad('tania-12', 'tania', 'hours simple fix why believe notmarketer knowledge dealt expert sendall love',
   hook('card', card='Inside *a real client call*'), '', '60s')
json.dump({'people': people, 'music': music, 'ads': ads}, open(f'{H}/specs.json', 'w'), indent=1)
print(len(ads), 'ads,', sum(len(a['aspect']) for a in ads), 'renders')
