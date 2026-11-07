# Editing styles — approved formats (from Andrew's examples, Nov 4 2026)
Source: Drive folder `1-Zjq7Ha-uzaq6W8RTBFy7DWs2fBcTVEZ` (9 reference reels, approved). Breakdown done at 1 frame/sec plus automatic cut detection.
These are **reference styles**, not templates to clone: we copy the editing grammar (layout, pacing, caption treatment), never their footage, logos, branding or exact designs.
Renderer: `tools/stylekit.py --style <id>` (see bottom). Previous engine look (`tools/reel.py`) = "v0 basic" and is retired for main feeds.

## Cut-pace data (scene detection)
| Ref | Length | Detected cuts | Avg shot | Note |
|---|---|---|---|---|
| adrien (editorial split) | 47.5 s | 30 | **1.5 s** | fastest; every 1–2 s the top visual or layout changes |
| saraev DSm-QQ (split, logo-heavy) | 48.5 s | 20 | 2.3 s | plus many in-shot visual swaps the detector misses |
| saraev DdeVVl (split, white) | 35.5 s | 13 | 2.5 s | |
| saraev De4XVv (split, "Tool Number") | 35.1 s | 8 | 3.9 s | top visual animates inside the shot |
| leadgenman DeYcUI (dark motion header) | 61.5 s | 0 | — | single-take face; **top panel changes every ~2 s** |
| leadgenman DeWJZc (warm motion header) | 42.9 s | 0 | — | same, warm palette |
| greglav (podcast letterbox) | 56.3 s | 1* | — | *two-camera switch (front/side) every 3–8 s, similar framing so detector misses it |
| artem (POV text over screen) | 7.8 s | 0 | — | loopable, static |
| viashaan (raw vs edited) | 9.4 s | 0 | — | meta / building-in-public |
**Rule we take:** something on screen changes every **1.5–2.5 s** (cut, layout switch, top-visual swap, or punch-in). Never more than ~3 s static except the podcast format.

## Style S1 — "Split Explainer" (refs: saraev ×3)
- **Canvas:** light background (white, or soft pale-blue/beige gradient). Top ~52%: the *visual* — app logo on white, screen recording in a rounded dark window with a thin accent border, a kinetic title ("Tool Number **One**"), or a stat ("**5,220,123** audio files").
- **Face:** bottom ~48%, face in a card with **large rounded top corners**, slightly inset. Every 3–5 shots: a **full-screen face punch-in** (tighter crop).
- **Captions:** **one word at a time** (two for short words), heavy sans (Inter-style, ~64 px at 1080w), centered on the seam between visual and face. Dark text on light, white on face/dark. **Accent words** switch to *italic serif* in the accent color (blue) — "*insanely*", "*level*", "*studies*".
- **Headers:** optional 2-line header at top for the first beat: plain line + accent phrase in a solid blue box with italic serif ("Claude Is Insanely Good At / **[Motion Graphics]**").
- **Lists:** "Tool Number / [One]" pill cards, logo row that builds up (ChatGPT → Gemini → …).
- **End:** full-face, caption "comment" small + **"KEYWORD"** large in quotes, italic serif, soft glow.
- **Use for:** screen walkthroughs with a face cam (SwitchYard-type), tool lists, news.

## Style S2 — "Editorial" (ref: adrien)
- **Canvas:** warm beige paper (#E6DCCB-ish). Top: screen recordings/UI on a floating card with soft shadow; sometimes full-bleed B-roll (him at the monitor, hands on keyboard).
- **Face:** bottom card with **rounded corners all round**, inset ~30 px, or full-screen face.
- **Captions:** a single **lowercase** word in a **small burnt-orange box** (#C2502F, white text) on the seam. On full-face/B-roll shots: big **serif lowercase** words (white or two-tone tan gradient, Instrument-Serif-like), placed mid-frame.
- **Section cards:** beige full-frame, one serif word/phrase ("Typography", "Color Contrast", "Layout & Spacing"), held ~1 s each — a "chapter" beat.
- **Pace:** fastest (1.5 s). B-roll of the person working is part of the grammar.
- **Use for:** taste/design-y explainers, "my workflow", premium feel.

## Style S3 — "Motion Header" (refs: leadgenman ×2)
- **Canvas:** dark. Variant **green**: black/deep-green glass + lime accent (#B6F36A). Variant **warm**: dark brown + peach accent (#F0A27A), serif headline.
- **Top ~40%:** a **headline line** (bold sans white + accent keyword, or serif white + peach) above an animated UI panel/screenshot card that **changes every ~2 s** to match what's being said ("You scroll for hours" → phone; "Saved into random folders" → folder icons; "$1,000 in API credits" → big number).
- **Face:** bottom ~60%, full width, **single continuous take** (no jump cuts needed), hands/gestures in frame.
- **Captions:** green: 2–3 words, large white bold on the seam (previous line fades). Warm: **one word in a peach pill**.
- **End:** "Comment "KEYWORD"" pill in the headline area + DM promise.
- **Use for:** talking-head explainers where the visual can be built from screenshots/text (voice-note scripts, opinion pieces).

## Style S4 — "Podcast Letterbox" (ref: greglav)
- **Canvas:** black 9:16. **16:9 footage full-width** in the middle (~y 600–1210).
- **Title:** fixed at top, white bold 2 lines (hook + "Pt 2"), same for the whole clip.
- **Captions:** **one word**, small white bold (~40 px), placed on the left third of the video, not centered.
- **Cameras:** cut between angles (front / side / tight) every 3–8 s. With one camera: alternate wide and tight crops.
- **Use for:** podcast and interview clips (Get Real, One Feature Teardown).

## Style S5 — "POV text" (ref: artem)
- Screenshot/dashboard on top, **3 short lines of white text on black boxes** in the middle ("POV: you used X to …", "a → b → c", "find → copy → win"), B-roll of the person at the computer below. 6–10 s, loops. CTA line appears after ~3 s ("comment "X" to get this").
- **Use for:** building-in-public / tool demos, Trial Reels, Stories.

## Style S6 — "Raw vs Edited" (ref: viashaan)
- Textured warm-brown background, tracked uppercase title ("HOW CLAUDE EDITS MY VIDEOS"), date line above. **Two phone cards side by side**: "RAW" (black label) vs "EDITED BY AI" (yellow label), both playing.
- **Use for:** *The Engine* series — show raw footage vs our edit.

## Mapping to our sources
| Source | Primary style | Test against |
|---|---|---|
| Camera + screen walkthrough (SwitchYard) | S1 | S2, S3-green |
| Screen-only walkthrough (FunnelStore) | S1 (logo/screen cards top, no face → full-frame visual) | S2 |
| Podcast / interview | S4 | S3-warm (audio + photo) |
| Talking head opinion (voice-note scripts) | S3 | S1 |
| Building in public (The Engine) | S6, S5 | — |

## Renderer
`python3 tools/stylekit.py EDL.json OUT.mp4 --style s1|s2|s3-green|s3-warm|s4 [--clean]` — same EDL as `tools/reel.py`, plus per-segment `head` (headline/visual text) and EDL-level `accent` words. Sub-shots are generated automatically at the style's pace (layout alternation + screen punch-ins), audio stays continuous.
`python3 tools/stylekit.py --raw-vs-edited RAW.mp4 EDITED.mp4 OUT.mp4` — S6.

---
## Podcast variant set (added Nov 4 evening; refs added to the editing-styles Drive folder)
One podcast clip → 7 versions, all built from the same cut, cleaned voice and word timings (`motion/clips/pod3-*.html`, shared code `motion/clips/pod3-lib.js`, build with `tools/motion_build.py`).

| # | Style | Ref | What defines it | Music bed |
|---|---|---|---|---|
| V1 | Motion graphics + captions | Andrew's approved S1/hook work | camera springs between speakers, grade cards, one-word captions | upbeat, full from frame 1 |
| V2 | **Story letterbox** | greglav | 16:9 band on black, fixed 2-line title, one small white word on the left third, one camera cut like two (wide/tight/listener cutaways), muted warm grade, one orange light-leak | **low dark drone, loud** (bed only ~4 dB under speech in the ref) |
| ~~V3~~ | ~~Kinetic / insane~~ **RETIRED Nov 7 (Andrew: "doesn't look good"), replaced by V8** | gp_multimedia | huge multi-colour words per beat (Inter Tight caps + Playfair italic), big numbers, **words behind the person** (segmentation cutouts), whip zooms with blur, white flash hits, punch-in every beat, tiny white caption word | high-energy house, SFX on every hit |
| V4 | **Question box hook** | DOAC (DfJ5KU) | full-screen speaker, white rounded box + black caps question on the chest for the first ~4 s, then 2–3-word white captions, second speaker's words in yellow, small brand tag top-left, listener cutaways | soft piano, low |
| V5 | **Split question start** | Andrew's brief | speaker 1 top / speaker 2 bottom with the question box on the seam, springs to full screen when the answer lands | soft piano/ambient |
| V6 | **Serious crop** | DOAC (DfNASd) | near-square frame on black, dark desaturated grade, lowercase light-weight words appearing one by one on a loose 2-line grid, clears per phrase, tiny brand tag | **sub-heavy dark drone** (72% of the bed energy under 150 Hz in the ref) |
| V7 | **Plain text hook** | DOAC (DfMXGO) | full screen, white caps question with shadow (no box), 2-word captions, tighter framing | slow cinematic piano |

Rules learned: the hook text/question is on screen from frame 1; music is audible from frame 1 (`sound_mix.py --music-from auto` skips quiet intros); reaction cutaways only on listeners whose mouths are closed; check who is speaking before framing (mouth-motion check or face strip).

**Audio standard (Andrew, Nov 5):** every voice goes through the ElevenLabs Voice Isolator (`tools/clean_audio.py`, default). No gates on speech.

---
## V8 "Animated" (Nov 7, replaces V3)
Teardown of all 13 example reels: `outputs/2026-11-07-style/teardown.md`. V3 failed because it shouted every beat; the refs whisper most of the time and shout every 3–4 s.
- Captions: phrase build (2–4 words), each word pops in with a blur, key words yellow italic serif, negative words coral (saraev).
- Hook header for the first sentence: white line + punch phrase in a brand-blue box that wipes in (saraev).
- Big beat every ~3.5 s: small lead-in + key word huge in a yellow/blue (red for negative) gradient, letters stagger in; punch-in zoom 1.13×, whoosh (gp_multimedia).
- Numbers count up with a pop; glass chips with icons for key nouns; icon bursts on wins/money; handwritten name note + arrow for a named guest (DOAC); rack-focus blur on speaker changes; one B&W dip on the hardest negative beat.
- SFX only on big moments (~1 per 5 s), music -11 dB ducked 8 dB, -16 LUFS.
- Beat words come from the clip bank's `emph` list (see `tools/clip_bank.py`); heuristic fallback otherwise.
- Render: `python3 tools/formats.py outputs/clip-bank/pod1.json pod1-05 --formats v8` (~15 min per 20 s clip on 4 cores with another lane running). `--build-only` builds the HTML for a quick stills check.
