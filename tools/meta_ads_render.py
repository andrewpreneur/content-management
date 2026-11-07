#!/usr/bin/env python3
"""Static Meta ad renderer (HTML templates -> PNG/JPG via tools/shoot.js).

Each creative is a dict: {"id", "tpl", ...template fields}. render_all(specs, out_dir, ratios)
writes <id>.jpg (4:5, 1080x1350) and, if requested, <id>_916.jpg (9:16, 1080x1920, safe zones kept).
Text markup: *word* = accent colour, ~word~ = strike-through, _word_ = underline marker.
Assets are absolute file paths (local only; nothing here is fetched from Drive).
"""
import html, os, re, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,600;6..72,700;6..72,800'
         '&family=Caveat:wght@600;700&family=Archivo+Black&family=Kalam:wght@700&display=block" rel="stylesheet">')

PAPER = '#F2EEE6'
NAVY = '#0B0F1A'
YEL = '#FFD23F'
BLUE = '#2E7DFF'
PURPLE = '#6C3BFF'


def md(s):
    s = html.escape(s)
    s = re.sub(r'\*(.+?)\*', r'<span class="acc">\1</span>', s)
    s = re.sub(r'~(.+?)~', r'<s>\1</s>', s)
    s = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<u>\1</u>', s)
    return s.replace('\n', '<br>')


def img(p):
    return 'file://' + str(p)


BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:%(H)spx;overflow:hidden}
body{font-family:Inter,sans-serif;-webkit-font-smoothing:antialiased}
.c{width:1080px;height:%(H)spx;position:relative;overflow:hidden;display:flex;flex-direction:column}
.serif{font-family:Newsreader,serif}
.hand{font-family:Caveat,cursive}
.acc{color:var(--acc)}
s{text-decoration-thickness:6px;text-decoration-color:#E5484D}
u{text-decoration:none;background:linear-gradient(transparent 62%%,var(--hl,#FFD23F) 62%%)}
.brand{font:600 26px Inter;letter-spacing:.2px;opacity:.75}
.pill{display:inline-block;border-radius:999px;padding:14px 30px;font:700 30px Inter}
"""


def page(H, css, body, acc='#FFD23F'):
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>{BASE_CSS % {"H": H}}'
            f':root{{--acc:{acc}}}{css}</style></head><body><div class="c">{body}</div></body></html>')


def safe(H):
    """top/bottom padding: 9:16 keeps text out of the top ~250 / bottom ~340 px (Reels/Stories UI)."""
    return (250, 340) if H > 1400 else (70, 70)


# ---------------------------------------------------------------- templates
def t_editorial(s, H):
    """Approved look (B003): warm paper, bold serif headline, small sans sub, real Andrew cutout at the bottom."""
    top, bot = safe(H)
    pill = f'<div class="pill pl">{md(s["pill"])}</div>' if s.get('pill') else ''
    css = f"""
.c{{background:radial-gradient(120% 80% at 50% 30%,#FBF9F5,#E7E2D8);color:#111;align-items:center;padding-top:{top}px}}
h1{{font:800 {s.get('size',82)}px/1.04 Newsreader;letter-spacing:-1.5px;text-align:center;padding:0 60px}}
p.sub{{font:500 34px/1.3 Inter;text-align:center;margin-top:22px;padding:0 110px;color:#2a2a2a}}
.ph{{position:absolute;left:50%;bottom:{0 if H < 1400 else bot - 120}px;transform:translateX(-50%);height:{int(s.get('ph',58)*13.5)}px;}}
.pl{{position:absolute;left:50%;transform:translateX(-50%);bottom:{48 if H < 1400 else bot - 60}px;background:#111;color:#fff;white-space:nowrap;font-size:28px}}
.desk{{position:absolute;left:0;right:0;bottom:0;height:{90 if H < 1400 else bot - 110}px;background:linear-gradient(#C9A06B,#B48650)}}
"""
    desk = '<div class="desk"></div>' if s.get('desk', True) else ''
    return page(H, css, f'<h1>{md(s["head"])}</h1><p class="sub">{md(s.get("sub",""))}</p>'
                        f'<img class="ph" src="{img(s["cut"])}">{desk}{pill}', s.get('acc', '#C2410C'))


def t_dark(s, H):
    """Brand dark: navy, Inter black headline with yellow accent, cutout bottom-right, bullets bottom-left."""
    top, bot = safe(H)
    bul = ''.join(f'<li>{md(b)}</li>' for b in s.get('bullets', []))
    kick = f'<div class="pill kk">{md(s["kicker"])}</div>' if s.get('kicker') else ''
    cta = f'<div class="pill cta">{md(s["cta"])}</div>' if s.get('cta') else ''
    css = f"""
.c{{background:radial-gradient(90% 60% at 80% 85%,#1B2A55,{NAVY} 70%);color:#fff;padding:{top}px 64px {bot}px}}
.kk{{background:{BLUE};color:#fff;align-self:flex-start;font-size:26px;letter-spacing:1px;margin-bottom:28px}}
h1{{font:900 {s.get('size',92)}px/1.0 Inter;letter-spacing:-2.5px;max-width:{s.get('hw',960)}px}}
p.sub{{font:500 37px/1.32 Inter;color:#B8C0D4;margin-top:26px;max-width:{s.get('sw',620)}px}}
ul{{list-style:none;margin-top:36px;position:relative;z-index:2}}
li{{font:700 40px/1.25 Inter;margin:18px 0;padding-left:58px;position:relative;max-width:560px}}
li:before{{content:'✓';position:absolute;left:0;top:3px;width:42px;height:42px;border-radius:10px;background:{YEL};color:{NAVY};font:900 28px/42px Inter;text-align:center}}
.ph{{position:absolute;right:{s.get('phr',-40)}px;bottom:0px;height:{int(s.get('ph',56)*13.5)}px}}
.cta{{position:absolute;left:64px;bottom:{60 if H < 1400 else bot-90}px;background:{YEL};color:{NAVY};z-index:3}}
"""
    return page(H, css, f'{kick}<h1>{md(s["head"])}</h1><p class="sub">{md(s.get("sub",""))}</p><ul>{bul}</ul>'
                        f'<img class="ph" src="{img(s["cut"])}">{cta}', s.get('acc', YEL))


def t_photo(s, H):
    """Full-bleed real studio photo, headline at the bottom over a gradient."""
    top, bot = safe(H)
    tag = f'<div class="pill tg">{md(s["tag"])}</div>' if s.get('tag') else ''
    css = f"""
.c{{background:#000 url('{img(s['photo'])}') center {s.get('pos','top')}/cover no-repeat;color:#fff;justify-content:flex-end;padding:{top}px 64px {bot+10}px}}
.c:after{{content:'';position:absolute;inset:0;background:linear-gradient(transparent 38%,rgba(0,0,0,.88) 78%);z-index:0}}
.tg{{position:absolute;top:{top}px;left:64px;background:rgba(255,255,255,.92);color:#111;font-size:26px;z-index:2}}
h1{{font:900 {s.get('size',84)}px/1.02 Inter;letter-spacing:-2px;z-index:1;position:relative}}
p.sub{{font:500 33px/1.32 Inter;color:#E6E6E6;margin-top:22px;z-index:1;position:relative}}
"""
    return page(H, css, f'{tag}<h1>{md(s["head"])}</h1><p class="sub">{md(s.get("sub",""))}</p>', s.get('acc', YEL))


def t_quote(s, H):
    """Testimonial pull-quote card with the customer's real frame."""
    top, bot = safe(H)
    css = f"""
.c{{background:{s.get('bg','#F7F4EE')};color:{s.get('fg','#141414')};padding:{top+10}px 72px {bot}px;justify-content:center}}
.stars{{color:#F5A400;font-size:46px;letter-spacing:6px}}
.q{{font:700 {s.get('size',74)}px/1.1 Newsreader;letter-spacing:-1px;margin-top:22px}}
.q:before{{content:'“';display:block;font:800 150px/0.7 Newsreader;color:{s.get('acc','#6C3BFF')};margin-bottom:6px}}
.who{{display:flex;align-items:center;gap:26px;margin-top:46px}}
.who img{{width:132px;height:132px;border-radius:50%;object-fit:cover;object-position:{s.get('fpos','center')};border:5px solid #fff;box-shadow:0 6px 20px rgba(0,0,0,.15)}}
.nm{{font:800 38px Inter}} .rl{{font:500 29px Inter;opacity:.7;margin-top:4px}}
.ft{{position:absolute;left:72px;right:72px;bottom:{50 if H < 1400 else bot-100}px;display:flex;justify-content:space-between;align-items:center}}
.ft .b{{font:700 26px Inter;opacity:.8}} .ft .p{{background:{s.get('fg','#141414')};color:{s.get('bg','#fff') if s.get('fg') else '#fff'};font-size:26px}}
"""
    return page(H, css, f'<div class="stars">★★★★★</div><div class="q">{md(s["quote"])}</div>'
                        f'<div class="who"><img src="{img(s["face"])}"><div><div class="nm">{md(s["name"])}</div>'
                        f'<div class="rl">{md(s["role"])}</div></div></div>'
                        f'<div class="ft"><span class="b">{md(s.get("foot","SaaSSuite · real customer, real words"))}</span>'
                        f'<span class="pill p">{md(s.get("pill","See how it works →"))}</span></div>', s.get('acc', '#6C3BFF'))


def t_notes(s, H):
    """iPhone Notes screenshot (native/ugly)."""
    top, bot = safe(H)
    rows = ''
    for r in s['rows']:
        kind, txt = r[0], r[1:]
        if kind == '-':
            rows += f'<div class="r"><span class="cb"></span><s class="g">{md(txt)}</s></div>'
        elif kind == '+':
            rows += f'<div class="r on"><span class="cb ok">✓</span><span>{md(txt)}</span></div>'
        else:
            rows += f'<p class="tx">{md(txt)}</p>'
    css = f"""
.c{{background:#FFFFFF;color:#111;padding:{max(top-20,40)}px 56px {bot}px}}
.bar{{display:flex;justify-content:space-between;align-items:center;color:#E0A500;font:500 40px Inter;margin-bottom:40px}}
.bar b{{font:600 34px Inter}}
.dt{{text-align:center;color:#999;font:500 24px Inter;margin-bottom:26px}}
h1{{font:800 {s.get('size',80)}px/1.08 Inter;letter-spacing:-1.5px;margin-bottom:46px}}
.r{{display:flex;align-items:flex-start;gap:26px;font:500 50px/1.28 Inter;margin:34px 0}}
.cb{{flex:none;width:54px;height:54px;border-radius:50%;border:3px solid #BBB;margin-top:4px;text-align:center;font:900 32px/48px Inter;color:#fff}}
.cb.ok{{background:#F2B600;border-color:#F2B600}}
.g{{color:#9a9a9a;text-decoration-thickness:3px;text-decoration-color:#9a9a9a}}
.on span:last-child{{background:#FFF1B8;padding:0 8px}}
.tx{{font:500 48px/1.35 Inter;margin:26px 0;color:#222}}
.kb{{position:absolute;left:0;right:0;bottom:0;height:{70 if H < 1400 else bot-150}px;background:#F4F4F4;border-top:1px solid #e3e3e3}}
"""
    return page(H, css, f'<div class="bar"><span>‹ Notes</span><b>Done</b></div><div class="dt">{s.get("date","Today 9:41 PM")}</div>'
                        f'<h1>{md(s["head"])}</h1>{rows}<div class="kb"></div>', '#D99A00')


def t_tweet(s, H, dark=False):
    top, bot = safe(H)
    bg, fg, mu = ('#000', '#E7E9EA', '#71767B') if s.get('dark') else ('#fff', '#0F1419', '#536471')
    css = f"""
.c{{background:{bg};color:{fg};padding:0 70px;justify-content:center}}
.hd{{display:flex;align-items:center;gap:22px}}
.hd img{{width:110px;height:110px;border-radius:50%;object-fit:cover}}
.nm{{font:800 38px Inter;display:flex;align-items:center;gap:10px}}
.vf{{width:34px;height:34px;border-radius:50%;background:#1D9BF0;color:#fff;font:900 22px/34px Inter;text-align:center}}
.hn{{font:400 32px Inter;color:{mu}}}
.tx{{font:400 {s.get('size',62)}px/1.3 Inter;margin-top:34px;letter-spacing:-.3px}}
.tx .acc{{font-weight:800}}
.mt{{font:400 30px Inter;color:{mu};margin-top:36px;padding-bottom:26px;border-bottom:1px solid {'#2F3336' if s.get('dark') else '#EFF3F4'}}}
.st{{display:flex;gap:46px;font:400 30px Inter;color:{mu};padding-top:24px}} .st b{{color:{fg}}}
"""
    return page(H, css, f'<div class="hd"><img src="{img(s["avatar"])}"><div><div class="nm">{md(s.get("name","Andrew George"))}<span class="vf">✓</span></div>'
                        f'<div class="hn">{md(s.get("handle","@andrewpreneurship"))}</div></div></div>'
                        f'<div class="tx">{md(s["text"])}</div><div class="mt">{s.get("meta","9:41 PM · Nov 6, 2026")}</div>'
                        '<div class="st"><span>💬 Reply</span><span>🔁 Repost</span><span>♡ Like</span><span>🔖 Save</span></div>',
                fg)


def t_imessage(s, H):
    top, bot = safe(H)
    msgs = ''
    for who, txt in s['msgs']:
        if who == 'card':
            msgs += f'<div class="card"><div class="ci" style="background-image:url(\'{img(txt[0])}\')"></div><div class="ct">{md(txt[1])}<span>youtube.com</span></div></div>'
        else:
            msgs += f'<div class="m {who}">{md(txt)}</div>'
    css = f"""
.c{{background:#fff;color:#000;padding-top:{max(top-30,30)}px}}
.top{{text-align:center;border-bottom:1px solid #ececec;padding-bottom:18px;background:#F7F7F7;margin-top:-80px;padding-top:80px}}
.top img{{width:96px;height:96px;border-radius:50%;object-fit:cover}} .top div{{font:500 26px Inter;margin-top:6px}}
.th{{display:flex;flex-direction:column;padding:30px 36px;gap:18px}}
.dt{{text-align:center;color:#8e8e93;font:500 22px Inter;margin-bottom:6px}}
.m{{max-width:80%;font:400 47px/1.26 Inter;padding:20px 32px;border-radius:44px}}
.m.l{{background:#E9E9EB;align-self:flex-start}}
.m.r{{background:#0A84FF;color:#fff;align-self:flex-end}}
.card{{align-self:flex-start;width:78%;border-radius:30px;overflow:hidden;background:#E9E9EB}}
.ci{{height:{400 if H > 1400 else 300}px;background:center 22%/cover}}
.ct{{padding:20px 26px;font:600 34px/1.25 Inter}} .ct span{{display:block;color:#8e8e93;font:400 24px Inter;margin-top:6px}}
.in{{position:absolute;left:30px;right:30px;bottom:{40 if H < 1400 else bot-120}px;border:2px solid #ddd;border-radius:40px;padding:16px 30px;color:#aaa;font:400 30px Inter}}
"""
    return page(H, css, f'<div class="top"><img src="{img(s["avatar"])}"><div>{md(s.get("who","Andrew"))} ›</div></div>'
                        f'<div class="th"><div class="dt">Today 9:41 PM</div>{msgs}</div><div class="in">iMessage</div>')


def t_sticky(s, H):
    top, bot = safe(H)
    ph = f'<img class="ph" src="{img(s["cut"])}">' if s.get('cut') else ''
    css = f"""
.c{{background:{s.get('bg','linear-gradient(160deg,#3A3F47,#1E2126)')};align-items:center;justify-content:{'flex-start' if s.get('cut') else 'center'};padding-top:{top+30}px}}
.n{{width:{s.get('w',820)}px;background:#FFE768;padding:70px 64px 80px;transform:rotate({s.get('rot',-2.5)}deg);box-shadow:0 30px 60px rgba(0,0,0,.45);position:relative;z-index:2}}
.n:before{{content:'';position:absolute;top:-24px;left:50%;width:180px;height:52px;margin-left:-90px;background:rgba(255,255,255,.55);transform:rotate(3deg)}}
.t{{font:700 {s.get('size',84)}px/1.08 Caveat;color:#1a1a1a}}
.t .acc{{color:#D7261E}}
.sm{{font:600 46px/1.15 Caveat;color:#333;margin-top:24px}}
.ph{{position:absolute;bottom:0px;left:50%;transform:translateX(-50%);height:{int(s.get('ph',42)*13.5)}px;z-index:1}}
"""
    return page(H, css, f'<div class="n"><div class="t">{md(s["text"])}</div><div class="sm">{md(s.get("small",""))}</div></div>{ph}')


def t_compare(s, H):
    top, bot = safe(H)
    L = ''.join(f'<li>{md(x)}</li>' for x in s['left'])
    R = ''.join(f'<li>{md(x)}</li>' for x in s['right'])
    css = f"""
.c{{background:#fff;color:#111;padding-top:{top}px}}
h1{{font:900 {s.get('size',66)}px/1.05 Inter;letter-spacing:-1.5px;text-align:center;padding:0 56px 36px}}
.g{{flex:1;display:flex;margin-bottom:{0 if H < 1400 else bot-140}px}}
.col{{flex:1;padding:50px 40px 90px;display:flex;flex-direction:column}}
.col h2{{font:900 46px/1.1 Inter;margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px}}
.a{{background:#FDECEC}} .a h2{{color:#C62828}} .b{{background:#E8F7EE}} .b h2{{color:#14804A}}
ul{{list-style:none;flex:1;display:flex;flex-direction:column;justify-content:space-evenly}} li{{font:700 40px/1.2 Inter;margin:0 0 0 54px;position:relative}}
.a li:before{{content:'✕';position:absolute;left:-50px;color:#C62828;font-weight:900}}
.b li:before{{content:'✓';position:absolute;left:-50px;color:#14804A;font-weight:900}}
.ft{{position:absolute;bottom:{34 if H < 1400 else bot-110}px;left:0;right:0;text-align:center;font:700 28px Inter;color:#333}}
"""
    return page(H, css, f'<h1>{md(s["head"])}</h1><div class="g"><div class="col a"><h2>{md(s["lt"])}</h2><ul>{L}</ul></div>'
                        f'<div class="col b"><h2>{md(s["rt"])}</h2><ul>{R}</ul></div></div><div class="ft">{md(s.get("foot",""))}</div>', '#14804A')


def t_math(s, H):
    """Receipt / calculator style."""
    top, bot = safe(H)
    rows = ''.join(f'<div class="rw {"tot" if i == len(s["rows"]) - 1 and s.get("total", True) else ""}"><span>{md(a)}</span><span>{md(b)}</span></div>'
                   for i, (a, b) in enumerate(s['rows']))
    css = f"""
.c{{background:{s.get('bg','#E9E4DA')};align-items:center;justify-content:center;padding:{top}px 0 {bot}px}}
h1{{font:900 {s.get('size',76)}px/1.04 Inter;letter-spacing:-2px;text-align:center;padding:0 60px 46px;color:#111}}
.rc{{width:800px;background:#fff;padding:54px 56px 60px;font-family:'JetBrains Mono',monospace;color:#111;box-shadow:0 20px 50px rgba(0,0,0,.18);
 -webkit-mask:radial-gradient(14px at 50% 100%,transparent 98%,#000) 50% 100%/40px 100% repeat-x}}
.rc .hd{{text-align:center;font:800 34px 'JetBrains Mono';letter-spacing:2px;border-bottom:3px dashed #999;padding-bottom:22px;margin-bottom:22px}}
.rw{{display:flex;justify-content:space-between;font:500 40px/1.25 'JetBrains Mono';padding:16px 0}}
.rw.tot{{border-top:3px dashed #999;margin-top:14px;padding-top:24px;font-weight:800;font-size:44px}}
.rw.tot span:last-child{{background:{YEL};padding:0 10px}}
.nt{{font:600 34px/1.3 Inter;color:#333;text-align:center;margin-top:40px;padding:0 120px}}
"""
    return page(H, css, f'<h1>{md(s["head"])}</h1><div class="rc"><div class="hd">{md(s.get("rh","THE MATH"))}</div>{rows}</div><p class="nt">{md(s.get("note",""))}</p>', '#B45309')


def t_features(s, H):
    """Dark, real GHL UI screenshot card + feature callouts."""
    top, bot = safe(H)
    items = ''.join(f'<div class="it"><span class="ic">{i+1:02d}</span><span>{md(x)}</span></div>' for i, x in enumerate(s['items']))
    css = f"""
.c{{background:linear-gradient(180deg,#0B0F1A,#121A33);color:#fff;padding:{top}px 60px {bot}px}}
h1{{font:900 {s.get('size',74)}px/1.02 Inter;letter-spacing:-2px}}
.sc{{margin:38px -10px 34px;border-radius:22px;overflow:hidden;border:2px solid #2B3657;box-shadow:0 30px 60px rgba(0,0,0,.5);height:{s.get('sh',470 if H < 1400 else 620)}px;background:url('{img(s['shot'])}') {s.get('spos','left top')}/{s.get('ssize','cover')} no-repeat #fff}}
.it{{display:flex;align-items:center;gap:24px;font:700 42px/1.2 Inter;margin:22px 0}}
.ic{{flex:none;font:800 24px 'JetBrains Mono';color:{NAVY};background:{YEL};border-radius:10px;padding:8px 12px}}
"""
    return page(H, css, f'<h1>{md(s["head"])}</h1><div class="sc"></div>{items}', YEL)


def t_search(s, H):
    top, bot = safe(H)
    res = ''.join(f'<div class="rs"><div class="u">{md(u)}</div><div class="t">{md(t)}</div><div class="d">{md(d)}</div></div>' for u, t, d in s['results'])
    css = f"""
.c{{background:#fff;color:#202124;padding:{top+10}px 56px {bot}px;justify-content:center}}
.lg{{font:500 76px Inter;letter-spacing:-2px;margin-bottom:30px}}
.lg b:nth-child(1){{color:#4285F4}} .lg b:nth-child(2){{color:#EA4335}} .lg b:nth-child(3){{color:#FBBC05}} .lg b:nth-child(4){{color:#4285F4}} .lg b:nth-child(5){{color:#34A853}} .lg b:nth-child(6){{color:#EA4335}}
.bx{{border:1px solid #dfe1e5;border-radius:50px;padding:28px 38px;font:400 42px Inter;box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:44px}}
.rs{{margin-bottom:60px}} .u{{font:400 30px Inter;color:#4d5156}} .t{{font:400 52px/1.2 Inter;color:#1a0dab;margin:10px 0}}
.d{{font:400 37px/1.38 Inter;color:#4d5156}} .d .acc{{font-weight:700;color:#202124}}
"""
    return page(H, css, '<div class="lg"><b>G</b><b>o</b><b>o</b><b>g</b><b>l</b><b>e</b></div>'
                        f'<div class="bx">{md(s["query"])}</div>{res}')


def t_list(s, H):
    top, bot = safe(H)
    items = ''.join(f'<div class="it"><span class="n">{i+1}</span><div><b>{md(a)}</b><p>{md(b)}</p></div></div>' for i, (a, b) in enumerate(s['items']))
    css = f"""
.c{{background:{s.get('bg','#FFF8E7')};color:#111;padding:{top+10}px 66px {bot}px}}
.k{{font:800 32px Inter;letter-spacing:2px;color:{s.get('acc','#C2410C')};text-transform:uppercase;margin-bottom:18px}}
h1{{font:800 {s.get('size',92)}px/1.02 Newsreader;letter-spacing:-2px;margin-bottom:30px}} .its{{flex:1;display:flex;flex-direction:column;justify-content:space-evenly;padding-bottom:80px}}
.it{{display:flex;gap:30px}} .n{{flex:none;width:84px;height:84px;border-radius:50%;background:#111;color:#fff;font:800 42px/84px Inter;text-align:center}}
.it b{{font:800 48px/1.15 Inter}} .it p{{font:500 37px/1.3 Inter;color:#444;margin-top:8px}}
.ft{{position:absolute;left:66px;bottom:{50 if H < 1400 else bot-100}px;font:700 28px Inter;color:#333}}
"""
    return page(H, css, f'<div class="k">{md(s.get("kicker",""))}</div><h1>{md(s["head"])}</h1><div class="its">{items}</div><div class="ft">{md(s.get("foot",""))}</div>', s.get('acc', '#C2410C'))


def t_bigword(s, H):
    top, bot = safe(H)
    css = f"""
.c{{background:{s.get('bg','#EEF3FB')};color:#0E1430;padding:{top}px 66px {bot}px}}
.pre{{font:800 50px Inter}}
.w{{font:900 {s.get('wsize',330)}px/0.86 'Archivo Black';color:{s.get('acc',BLUE)};letter-spacing:-8px;margin:6px 0 14px -10px}}
h1{{font:800 50px/1.15 Inter;max-width:900px}}
p.sub{{font:500 32px/1.35 Inter;color:#3A4160;margin-top:20px;max-width:560px}}
.ph{{position:absolute;right:-30px;bottom:0px;height:{int(s.get('ph',50)*13.5)}px}}
.ar{{font:700 46px/1.5 Caveat;margin-top:30px;color:#0E1430}}
"""
    arr = ''.join(f'<div>{md(x)} ←</div>' for x in s.get('arrows', []))
    return page(H, css, f'<div class="pre">{md(s.get("pre",""))}</div><div class="w">{md(s["word"])}</div><h1>{md(s["head"])}</h1>'
                        f'<p class="sub">{md(s.get("sub",""))}</p><div class="ar">{arr}</div><img class="ph" src="{img(s["cut"])}">', s.get('acc', BLUE))


def t_reddit(s, H):
    top, bot = safe(H)
    css = f"""
.c{{background:#DAE0E6;padding:{top+20}px 40px {bot}px;justify-content:center}}
.p{{background:#fff;border-radius:18px;padding:40px 44px;color:#1c1c1c}}
.hd{{display:flex;align-items:center;gap:16px;font:600 30px Inter;flex-wrap:wrap;color:#576f76}} .hd i{{width:52px;height:52px;border-radius:50%;background:#FF4500;display:inline-block}}
.hd b{{color:#1c1c1c}}
h1{{font:800 {s.get('size',62)}px/1.16 Inter;margin:28px 0 24px}}
.bd{{font:400 41px/1.4 Inter;color:#2a2a2a}} .bd .acc{{font-weight:700;color:#111}}
.ft{{display:flex;gap:40px;margin-top:36px;font:700 32px Inter;color:#576f76}} .ft .up{{color:#FF4500}}
"""
    return page(H, css, f'<div class="p"><div class="hd"><i></i><b>{md(s.get("sub","r/gohighlevel"))}</b> · {md(s.get("user","u/agency_owner_tx"))} · 6h</div>'
                        f'<h1>{md(s["title"])}</h1><div class="bd">{md(s["body"])}</div>'
                        '<div class="ft"><span class="up">▲ Vote</span><span>💬 Comments</span><span>Share</span></div></div>', '#111')


def t_dialog(s, H):
    top, bot = safe(H)
    css = f"""
.c{{background:linear-gradient(#5BA4E6 0%,#9CCBF2 55%,#5FA845 56%,#3E8B2E);align-items:center;justify-content:center;padding:{top}px 0 {bot}px}}
.w{{width:980px;background:#C0C0C0;border:4px solid;border-color:#fff #444 #444 #fff;font-family:'JetBrains Mono',monospace;box-shadow:10px 10px 0 rgba(0,0,0,.25)}}
.tb{{background:linear-gradient(90deg,#000A7A,#1E5AD0);color:#fff;font:800 34px 'JetBrains Mono';padding:12px 18px;display:flex;justify-content:space-between}}
.bd{{padding:50px 50px;font:600 50px/1.35 'JetBrains Mono';color:#111}} .bd .acc{{background:#000A7A;color:#fff;padding:0 8px}}
.bt{{display:flex;gap:30px;padding:0 44px 40px}} .bt div{{flex:1;text-align:center;font:800 40px 'JetBrains Mono';padding:18px;border:4px solid;border-color:#fff #444 #444 #fff}}
.bt div:first-child{{outline:3px dotted #000;outline-offset:-12px}}
"""
    btns = ''.join(f'<div>{md(b)}</div>' for b in s.get('buttons', ['YES', 'NO']))
    return page(H, css, f'<div class="w"><div class="tb"><span>{md(s["title"])}</span><span>✕</span></div><div class="bd">{md(s["body"])}</div><div class="bt">{btns}</div></div>')


TEMPLATES = dict(editorial=t_editorial, dark=t_dark, photo=t_photo, quote=t_quote, notes=t_notes, tweet=t_tweet,
                 imessage=t_imessage, sticky=t_sticky, compare=t_compare, math=t_math, features=t_features,
                 search=t_search, list=t_list, bigword=t_bigword, reddit=t_reddit, dialog=t_dialog)


def render_all(specs, out_dir, ratios=('45',), only=None):
    """specs: list of dicts. ratios: '45' (1080x1350) and/or '916' (1080x1920). Returns list of written files."""
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='mads_'))
    jobs = {'45': [], '916': []}
    for s in specs:
        if only and s['id'] not in only:
            continue
        for r in ratios:
            if r == '916' and not s.get('v916'):
                continue
            H = 1350 if r == '45' else 1920
            h = tmp / f"{s['id']}_{r}.html"
            h.write_text(TEMPLATES[s['tpl']](s, H))
            jobs[r].append((h, tmp / f"{s['id']}_{r}.png"))
    env = dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '/opt/node-tools/node_modules'))
    written = []
    for r, lst in jobs.items():
        H = 1350 if r == '45' else 1920
        for i in range(0, len(lst), 12):
            chunk = lst[i:i + 12]
            subprocess.run(['node', str(ROOT / 'tools/shoot.js'), '1080', str(H)] + [f'{a}:{b}' for a, b in chunk], check=True, env=env)
            from PIL import Image
            for a, b in chunk:
                name = b.stem.replace('_45', '').replace('_916', '_916')
                dst = out_dir / f'{name}.jpg'
                Image.open(b).convert('RGB').save(dst, quality=88, optimize=True)
                written.append(dst)
    return written


def t_hook(s, H):
    """Full-screen hook card used as the first 1.8 s of round-2 video ads."""
    css = f"""
.c{{background:radial-gradient(90% 60% at 50% 45%,#1B2A55,{NAVY} 75%);color:#fff;align-items:center;justify-content:center;text-align:center;padding:0 70px}}
.k{{background:{YEL};color:{NAVY};font:800 28px Inter;letter-spacing:1.5px;border-radius:999px;padding:10px 26px;margin-bottom:40px}}
h1{{font:900 {s.get('size',96)}px/1.02 Inter;letter-spacing:-3px;text-wrap:balance}}
p{{font:600 34px/1.3 Inter;color:#AAB3C8;margin-top:34px}}
"""
    return page(H, css, f'<div class="k">{md(s.get("kicker","REAL CUSTOMER · UNSCRIPTED"))}</div><h1>{md(s["head"])}</h1><p>{md(s.get("sub",""))}</p>', YEL)


TEMPLATES['hook'] = t_hook
