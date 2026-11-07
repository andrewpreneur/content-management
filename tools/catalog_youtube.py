#!/usr/bin/env python3
"""Nov 7 catalog: YouTube videos → 4-frame IG story with a link sticker spec + an image post (1080x1350 + 1200x627).

  python3 tools/catalog_youtube.py COPY.json YT.json THUMBS_DIR OUT_DIR
Story frames: 1 hook over the thumbnail, 2 why-watch, 3 poll, 4 link sticker → the video.
Image post: the real YouTube thumbnail as the hero with one line of copy, so it is a face + a promise, never a slide deck.
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0, str(Path(__file__).parent)); import catalog_cards as CC

CSS_EXTRA = ''


def blur_bg(thumb, out, W, H):
    im = Image.open(thumb).convert('RGB'); r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1)); x = (im.width - W) // 2; y = (im.height - H) // 2
    im.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.45)).save(out, quality=88); return out


def main():
    copy, yt, thumbs, out = sys.argv[1:5]; C = json.loads(Path(copy).read_text()); Y = {v['id']: v for v in json.loads(Path(yt).read_text())}
    out = Path(out); tmp = Path('/home/user/work/catalog/yt_tmp'); tmp.mkdir(parents=True, exist_ok=True); specs = []
    for it in C:
        vid = it['id']; v = Y[vid]; th = Path(thumbs) / f'{vid}.jpg'; d = out / vid
        bg = blur_bg(th, str(tmp / f'{vid}_bg.jpg'), 1080, 1920)
        link = f"youtu.be/{vid}"
        frames = [dict(format='story', bg=f"url(file://{bg}) center/cover", img=str(th), img_top=760, img_h=540, text=it['hook'], text_top=260, size=84 if len(it['hook']) < 40 else 70,
                       sub='New video on my YouTube ↓', sub_top=1360),
                  dict(format='story', bg=f"url(file://{bg}) center/cover", img=str(th), img_top=300, img_h=540, text=it['why'], text_top=920, size=64),
                  dict(format='story', bg=f"url(file://{bg}) center/cover", img=str(th), img_top=220, img_h=540, text='Quick one:', text_top=830, size=64, poll=it['poll'], poll_top=960),
                  dict(format='story', bg=f"url(file://{bg}) center/cover", img=str(th), img_top=420, img_h=540, text='Watch it here 👇', text_top=240, size=80, link='Watch: ' + it['short'], link_top=1180)]
        CC.render(frames, d / 'story', 1080, 1920, names=[f'{vid}-story-{k + 1}' for k in range(4)])
        post = dict(format='ytpost', thumb=str(th), bg=blur_bg(th, str(tmp / f'{vid}_bg45.jpg'), 1080, 1350), text=it['img'])
        CC.render([post], d / 'single', 1080, 1350, names=[f'{vid}-post-1080x1350'])
        land = dict(format='ytland', thumb=str(th), text=it['img'])
        CC.render([land], d / 'single', 1200, 627, names=[f'{vid}-post-1200x627'])
        specs.append(dict(id=vid, url=v['url'], title=v['title'], frames=[
            dict(frame=1, text=it['hook'], sticker=None), dict(frame=2, text=it['why'], sticker=None),
            dict(frame=3, text='Quick one:', sticker=dict(type='poll', question=it['poll'][0], options=it['poll'][1:])),
            dict(frame=4, text='Watch it here', sticker=dict(type='link', url=v['url'], label='Watch: ' + it['short'], placement='center, over the white placeholder'))]))
        print(vid, flush=True)
    (out / '_story_specs.json').write_text(json.dumps(specs, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
