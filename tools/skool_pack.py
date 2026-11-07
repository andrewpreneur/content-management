#!/usr/bin/env python3
"""Skool launch pack (Nov 7): carousels, single images, story frames and text from Andrew's own script lines
(outputs/2026-11-07-skool/scripts.md). Name and link stay {{COMMUNITY_NAME}} / {{LINK}} until we have them.

  python3 tools/skool_pack.py
Photos: real on-camera frames of Andrew from the Oct/Nov feature videos (catalog frames_feat/*/portrait.jpg).
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0, str(Path(__file__).parent)); import catalog_cards as CC

ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'outputs/2026-11-07-catalog/skool-launch'; FF = Path('/home/user/work/catalog/frames_feat')
PH = {k: FF / k / 'portrait.jpg' for k in ('studioupdate', 'webinar', 'meetingroom', 'commerce', 'levelup', 'ssclienthu')}
NAME, LINK = '{{COMMUNITY_NAME}}', '{{LINK}}'

CAROUSELS = {
 'skool-car1-puzzle': dict(photo='studioupdate', hook='Building with AI feels like a puzzle', sub='Why I built a community for it', slides=[
    "Trying to build a business with AI right now can feel like trying to put together a puzzle while somebody keeps adding new pieces.",
    "You've got GoHighLevel, Claude, app builders, AI agents, automations, and a new tool everybody says you need every week.",
    "There's a lot of opportunity. But figuring out what to use, how it all connects, and what someone would actually pay you for gets complicated fast.",
    "That's why I built this community.",
    "We cover how to build something useful, package it into an offer, deliver it, and get customers.",
    "You'll get practical training, downloadable skills, prompts, and resources. Plus coaching and a place to bring questions."],
    cta=f"Come inside, find your starting point, and start building.\n{NAME} · link in bio"),
 'skool-car2-behind-the-scenes': dict(photo='webinar', hook="I'm opening up how I build", sub='AI, SaaS and GoHighLevel, every week', slides=[
    "Every week, I'm working on something in my business that involves AI, SaaS, or GoHighLevel.",
    "Sometimes I'm building a product. Sometimes I'm working on getting customers. Sometimes I'm automating something that takes too much time.",
    "Along the way, I'm finding tools, building skills, testing strategies, and figuring out how these pieces work together.",
    "This community is where I'm opening that up and sharing it with you.",
    "Watching somebody build something is helpful. Being able to understand the decisions, get the resources, and ask questions makes it easier to build your version.",
    "And this keeps evolving. As I find tools worth using, I'll bring them in through exclusive drops and new training."],
    cta=f"Join us inside, share what you're working on, and start applying it alongside us.\n{NAME} · link in bio"),
 'skool-car3-ownership': dict(photo='meetingroom', hook='What problem could you build a business around?', sub='Give that idea somewhere to go', slides=[
    "Maybe you know an industry where leads get ignored. Maybe businesses spend hours on something that could be automated.",
    "Maybe you have an idea for software you wish existed.",
    "With AI and platforms like GoHighLevel, you can start turning those ideas into something people can use.",
    "But the tools are only part of it. You still need to choose a customer, build something they want, create an offer, and learn how to sell and deliver it.",
    "That's what we work on inside this community.",
    "Bring an early idea, a project you've already started, or a business you want to grow. Then work through your next move and keep making progress."],
    cta=f"If you've been thinking about building something of your own, come inside.\n{NAME} · link in bio"),
}
SINGLES = [
 ('quote', 'commerce', "The tools are only part of it."),
 ('quote', 'levelup', "Come inside, find your starting point, and start building."),
 ('quote', 'ssclienthu', "What's a problem you understand well enough to build a business around?"),
 ('tweet', None, "Building with AI right now feels like putting together a puzzle while somebody keeps adding new pieces.\n\nThat's why I built this community."),
 ('tweet', None, "Watching somebody build something is helpful.\n\nUnderstanding the decisions, getting the resources and asking questions is what makes it easier to build your version."),
 ('stat', None, ("5", "steps we work on inside: choose a customer, build, offer, sell, deliver")),
]
STORY = [
 dict(photo='studioupdate', text="Building with AI feels like a puzzle", sub="…while somebody keeps adding new pieces."),
 dict(photo='webinar', text="So I built a community for it.", sub="Strategies, skills, tools, training and coaching for AI, SaaS and GoHighLevel."),
 dict(photo='meetingroom', text="Where are you right now?", poll=["Where are you starting?", "Just an idea", "Already have an agency", "Want AI to run my business"]),
 dict(photo='commerce', text="Inside you get", sub="Practical training · downloadable skills + prompts · coaching · exclusive drops"),
 dict(photo='levelup', text="Come find your starting point.", link=f"Join {NAME}"),
]


def blur(p, W, H, out):
    im = Image.open(p).convert('RGB'); r = max(W / im.width, H / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x, y = (im.width - W) // 2, (im.height - H) // 2; im.crop((x, y, x + W, y + H)).save(out, quality=90); return out


def main():
    tmp = Path('/home/user/work/catalog/skool_tmp'); tmp.mkdir(parents=True, exist_ok=True); made = []
    face = lambda k: str(PH[k])
    av = {}
    for k, p in PH.items():  # small round avatar crops from the same frames
        im = Image.open(p); w = im.width; im.crop((int(w * .28), int(w * .02), int(w * .72), int(w * .46))).resize((240, 240)).save(tmp / f'av_{k}.jpg', quality=90); av[k] = str(tmp / f'av_{k}.jpg')
    for cid, c in CAROUSELS.items():
        n = len(c['slides']) + 2
        sl = [dict(format='facehook', photo=face(c['photo']), text=c['hook'], tag='NEW COMMUNITY', sub=c['sub'])]
        sl += [dict(format='tweet', text=t, num=f'{i + 2}/{n}') for i, t in enumerate(c['slides'])]
        sl.append(dict(format='cta', text=c['cta']))
        made += CC.render(sl, OUT / 'carousels' / cid, 1080, 1350)
    cards, names = [], []
    for i, (kind, ph, t) in enumerate(SINGLES):
        if kind == 'quote':
            s = dict(format='quote', text=t, label='Andrew George · new community', by='Andrew George', by2=f'{NAME}', avatar=av[ph], photo=str(tmp / f'land_{ph}.jpg'))
            im = Image.open(PH[ph]); im.resize((430, int(430 * im.height / im.width))).crop((0, 0, 430, 627)).save(tmp / f'land_{ph}.jpg', quality=90)
        elif kind == 'tweet': s = dict(format='tweet', text=t)
        else: s = dict(format='stat', num=t[0], label=t[1], by='Andrew George', by2=NAME, avatar=av['studioupdate'])
        cards.append(s); names.append(f'skool-single-{i + 1}-{kind}')
    made += CC.render(cards, OUT / 'singles', 1080, 1350, names=[n + '-1080x1350' for n in names])
    made += CC.render(cards, OUT / 'singles', 1200, 627, names=[n + '-1200x627' for n in names])
    fr = []
    for i, s in enumerate(STORY):
        bg = blur(PH[s['photo']], 1080, 1920, tmp / f'st_{i}.jpg')
        f = dict(format='story', full=True, img=bg, text=s['text'], text_top=1180 if not s.get('poll') else 260, size=86, sub=s.get('sub'), sub_top=1400)
        if s.get('poll'): f.update(poll=s['poll'], poll_top=1180, text_top=200)
        if s.get('link'): f.update(link=s['link'], link_top=1500, sub=None)
        fr.append(f)
    made += CC.render(fr, OUT / 'story', 1080, 1920, names=[f'skool-story-{i + 1}' for i in range(len(fr))])
    (OUT / 'story' / 'story-spec.json').write_text(json.dumps([dict(frame=i + 1, text=s['text'], sub=s.get('sub'), sticker=('poll: ' + ' / '.join(s['poll'])) if s.get('poll') else (f'link → {LINK}' if s.get('link') else None)) for i, s in enumerate(STORY)], indent=1, ensure_ascii=False))
    print(len(made), 'images')


if __name__ == '__main__':
    main()
