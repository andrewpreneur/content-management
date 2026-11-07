# Example reels teardown (Nov 7, 2026, style worker)

Source: Drive folder `examplereelsandformats` (`1-Zjq7Ha-uzaq6W8RTBFy7DWs2fBcTVEZ`), all 13 reels.
Method: frame strip every 0.5 s (`shots/<id>-sheet.jpg`, 10 frames per row = 5 s per row), first 4 s at 4 fps (`shots/<id>-hook.jpg`),
ffmpeg scene detection (threshold 0.25) for cuts, and a high-band transient count on the audio for SFX hits
(it also catches "s" sounds in speech, so read it as an upper bound; gp's count is the clean one because his voice is soft).
We copy the editing grammar only, never footage, logos or exact designs.

## Why V3 "kinetic" failed (what we got wrong from gp_multimedia)
V3 put a giant multi-colour word on screen **every beat**, with white flashes and whip zooms. The reference does the opposite:
- **Most of the time the caption is one small, quiet word** (sentence case, white, ~40 px at 1080 w, on the chest). See `shots/gp-mid.jpg` bottom row ("completely", "changed", "what's", "for").
- **A big beat only every 3 to 4 s** (gp at 26.7 s has ~8: "MY VIDEOS", "WORK ALL DAY", "10 SECONDS", 450,000 counter, "REACH", "DIDN'T HAPPEN BY ACCIDENT", "ATTENTION", "DM ME VIDEO").
- **Big beats are stacked phrases with a size hierarchy**: small white lead-in on top ("as a", "and that", "but that"), the key word huge in caps and colour (orange or blue), sometimes a third line small (`shots/gp-mid2.jpg`). Letters arrive with a blur-in and a slight stagger. Text sits **above the head / upper chest**, never across the face.
- **Transitions are rack-focus blurs** (the whole frame goes soft for ~0.2 s, then sharp on the new framing), not white flashes.
- **Graphic pop-ins carry the story**: a number counter rolling to 450,000 with red heart badges bursting around it, two floating "phone" cards with a glass border, a logo card, glass pills ("Real Leads", "Real Opportunities") popping beside him, a contact card sliding in at the end, a blue line-icon set drawing on.
- **One grade beat**: a quick black-and-white dip on the "young entrepreneur" line, back to colour on the next beat.
- **Sound**: only ~5 hard hits in 26.7 s (1.9, 3.9, 7.1, 16.8, 22.0 s), all on big beats. SFX are rare and land on the big moments.

## Per reel

| Reel | Len | Cuts (scene det.) | Caption style | Animations / pop-ins | Hook (first 2 s) |
|---|---|---|---|---|---|
| gp_multimedia DdHguJ | 26.7 s | 8 (+ many in-shot graphic changes) | 1 small white word on chest; big stacked phrase every 3–4 s (orange/blue caps, white lead-in) | rack-focus, counter + heart burst, glass cards, B&W dip, icon draw-on, contact card | "I can tell you MY VIDEOS" builds word by word in 3 sizes / 3 colours in 1.5 s |
| adrien.ninet DWzdwb | 47.5 s | 31 (avg 1.5 s) | single lowercase word in a small burnt-orange box on the seam; big serif lowercase on full-face shots | UI cards slide in, chapter cards ("Typography", "Color Contrast") ~1 s each, B-roll of hands/keyboard | split screen from frame 1, a file icon flies to the Claude Code card |
| nick_saraev De4XVv | 35.1 s | 9 | **phrase build**: words appear one at a time and stay ("Claude has now"), the live word pops; accent words blue, *italic serif* | header "Claude Is Insanely Good At" types in word by word, then the accent phrase in a solid blue box that wipes in; terminal types; zoom into the screen | header + typing terminal + caption all start in the first 0.5 s |
| nick_saraev DdeVVl | 35.5 s | 13 | 1–2 words, small bold black on white / white on face | logos pop in (GitHub, ChatGPT…), logo row builds up, big italic number "7 BILLION", circular counter "21% → 60%" | mascot icon + "WITH ALMOST UNLIMITED USAGE" letter-spaced reveal |
| nick_saraev DSm-QQ | 48.5 s | 22 | small bold white 1–3 words | logo hero cards every 1–2 s, italic serif headers ("New AI Coder"), orbit diagram, full-face punch-ins with colour grade swaps | full-face punch-in then logo cards ChatGPT → Cursor in 1.5 s |
| leadgenman DeYcUI | 61.5 s | 0 (one take) | 2–3 words, bold white, previous line fades; key word bigger | top panel changes every ~2 s (phone, folders, counter "71", UI cards with lime glow border); headline line with lime accent word | wall of thumbnails + "The future of Social media research" header |
| leadgenman DeWJZc | 42.9 s | 0 | 1–2 words in a **peach pill**, live word highlighted | warm serif headline + accent word, website card with highlight box drawing on "Start up" | headline + card + pill caption in frame 1 |
| DOAC DfJ5KU | 51.4 s | 15 (camera switches) | 2–3 words, white; second speaker in yellow | white rounded question box on the chest ("WHY DID HE REJECT $3 BILLION?"), **handwritten name note with arrow** ("Snapchat Founder"), DOAC tag top-left | question box from frame 1, cut to guest at 2.0 s |
| DOAC DfMXGO | 36.5 s | 5 | 2 words white | plain caps question with shadow | question from frame 1 |
| DOAC DfNASd | 38.6 s | 0 | lowercase light words, 2-line grid | none (serious tone) | near-square crop, dark grade |
| greglav Dadv | 56.3 s | 1 | one small white word, left third | none; 16:9 band, title fixed top | title + band from frame 1 |
| artem Ddov4N | 7.8 s | 0 | 3 white lines on black boxes | none (loop) | POV text from frame 1 |
| viashaan DfSrDF | 9.4 s | 2 | none | two phone cards RAW vs EDITED | label + both cards frame 1 |

Cut rhythm: 1.5–4 s between visual changes in every animated reel (cut, graphic swap or punch-in). Talking-head shots alone never hold more than ~3 s without something moving.

## The grammar we take for V8 "Animated" (replaces V3)
1. **Captions = phrase build.** 2–4 words per phrase, sentence case, white, bold sans (~64 px at 1080 w) on the chest. Each new word pops in (blur 8→0, scale 0.86→1, 0.14 s) and stays until the phrase ends (saraev). Key words switch to *italic serif* in brand yellow; negative words in coral.
2. **Hook header (0 → end of first sentence):** plain line, then the accent phrase in a solid brand-blue box that wipes in left to right, words blur in one by one (saraev header). Collapses away when the answer starts.
3. **Big beat every ~3.5 s** (gp): small white lead-in + the key word huge in caps, brand gradient, letters staggered with blur-in, placed above the head. Paired with a **punch-in zoom** (spring to 1.14×) and a whoosh. The small caption hides during the beat.
4. **Numbers become counters** (gp 450,000, saraev 21% → 60%): the digits roll up over 0.6 s with a pop.
5. **Callout chips** (gp "Real Leads"): glass pills with a line icon pop beside the speaker for key nouns (clients, tools, money, time). Pop SFX, soft.
6. **Icon burst** on positive/money words (gp hearts): 3–5 small icon badges spring out from behind the speaker and fade.
7. **Rack-focus** dip on every speaker change (gp), with a whoosh. No white flashes.
8. **Name note** (DOAC): handwritten-style label + arrow that draws on, first time each speaker talks.
9. **B&W grade dip** on the strongest negative beat (gp), back to colour on the next beat.
10. **Sound**: whoosh on punch-ins and rack-focus, pop on chips/counters, soft impact on the single strongest beat. SFX on big beats only (gp has ~1 per 5 s), never on every word.
