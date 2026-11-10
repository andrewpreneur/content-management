---
name: saassuite-motion
description: Make SaaSSuite / Andrew George videos, reels, VSLs, onboarding and motion-graphic ads in the locked SaaSSuite main style (light default, violet accent, Inter Display, floating UI cards, measured spring motion, cinematic ambient sound). Use for any SaaSSuite motion graphic, product launch, feature video, Skool video, or speaker reel with captions. Not for yellow-caption trend reels (those keep their own format).
---

# SaaSSuite motion style

Brand decisions come from Andrew's in-chat quiz (`docs/brand-video/quiz.md`) and are summarised in `docs/brand-video/SAASSUITE-STYLE.md`. Read that first.
Every motion value below was **measured** by rebuilding reference videos frame by frame (`motion/recreate/<ref>/notes.md`, SSIM 0.91–0.99). Use them as given; don't invent new easing.

## Non-negotiables
- Background `#F6F5F2` (light, default) · dark alternate `#0B0B10` + violet glow for hook reveals, premium moments, end cards.
- Ink `#141418`, muted `#6B6F7B`, cards white with 1px `#E6E4EF`, radius 20–36, shadow `0 30px 80px rgba(20,20,40,.12)`.
- **One accent: violet `#7B5CFF`** (on video/dark use `#9B83FF` for legibility). One accent word per headline. Never a second bright colour.
- Headlines: **Inter Display 800** (variable `tools/fonts/InterVariable-opsz-wght-latin.woff2`, opsz 32; or `InterDisplay-Bold.ttf`), letter-spacing −0.037em, sentence/lowercase, full stop on the accent word. Body: Inter 400/600.
- UI is **rebuilt** as floating cards (no device frames). Show the product, big and readable.
- Transitions: **morph inside a scene, clean cut on the beat between chapters**.
- Busyness: in between (one headline + one card most of the time, one busy moment per video).
- Sound: cinematic ambient bed (~90 bpm, slow build, swells into chapter cuts), soft whooshes on cuts, soft UI clicks/pops on card events, ding on checks. No hard slams. Voice videos: bed ducked well under voice. Master −14 LUFS, TP ≤ −1 dB.
- Story: problem → feature → proof → CTA, joined with But/Therefore. End on the dark card: `SaaSSuite.` wordmark (violet full stop) + violet pill CTA.

## Dials
- "do more" → more UI shown → more motion → more graphics (one notch at a time).
- "make it simpler" → fewer graphics → text-led.

## Motion library — `lib.js` (this folder)
Pure functions of time, so pages expose `window.render(t)` and render deterministically. Include with `<script src=".../lib.js">` and call `SS.<fn>`.
| Move | Function | Measured from | Key numbers |
|---|---|---|---|
| Headline letters spring up | `letterRise` | ClimbX | stagger 0.0453s, start 73.5px below, v0 −628px/s, ω15.9 ζ0.47, rot 0.18°/px, blur ≤3.5px |
| Soft word rise | `wordRise` | sample/Tessel | 40px + 10px blur, 0.55s outQuart, 0.11s stagger |
| Card slide-in | `cardSlide` | ClimbX | from 358px, ω23.8 ζ0.78, x-motion-blur 0.45·|v|/30 |
| Pill/logo stamp | `stamp` | ClimbX | 2.25→0.67 in 6.5f, spring ω11.5 ζ0.3 overshoot ~1.24, −24°→+6°, optional shock ring |
| Word slam | `wordSlam` | ClimbX | scale 1+spring(1.25, ω15.4, ζ0.48), blur 12·|s−1| |
| **Morph one shape** | `morph`, `relaxTo` | MakerMap | separate w/h springs (w: ω16.4 ζ0.59; h: ω16 ζ0.78), pill radius h/2, card→circle radius spring ω24 |
| Content swap during morph | `dissolveOut` | MakerMap | old out 0.08s with 11px blur; new in at 80% of the spring; rows 60ms stagger, rise 16px |
| Dark↔light flip | (colour spring) | MakerMap | fill on critically damped spring ω22, 5–7px blur pulse, blend dark/light shadows |
| Press / cursor | `press`, `cursorSquish` | MakerMap | press 0.954 then spring ω22 ζ0.85; cursor 0.85 squish; hover 1.024 |
| Typing | `typing` | Tessel | ~30 chars/s; new char born in accent, fades to ink over 5 frames; keyword → chip on its full stop; solid caret, no blink |
| Click → colour wipe | `clickWipe` | Tessel | diameter 146+17·1.75^frame, collapses into the next scene's accent line |
| Big headline settle | `bigSettle` | Tessel | blur 18(1−u)² over 0.1s, scale 1.07→1 over 0.2s, then slow push +5% |
| Text sweep sharpen | `sweepChar` | CodePilot | 10px blur → 0 over 0.6s, sweep 1230px/s |
| Keynote 3D camera | `keynoteCam` | CodePilot | 0.696s bezier(.626,.279,.251,.907): scale→0.81, rotY −10.76°, rotX 3.7°, then +4.7° drift / 3.3s, perspective 4732 |
| Beat pulse | `beatPulse` | ClimbX | scene scale 1+0.0095·e^(−dt/0.085) every beat (use 90 bpm to match the ambient bed) |
| Bars / counters | `barFill` | ClimbX | width·(1−e^(−16.9t)), rows 0.133s apart, % counts with bar |
Dark-mode extras (horizon glow ellipse, anamorphic streaks, glitch chapter word, dissolve into UI): exact recipes in `motion/recreate/26-codepilot/ask/notes.md`. Spinner→check→dot, rearrange FLIP, depth-field push: `43-makermap/*/notes.md`, `19-tessel/*/notes.md`, `13-climbx/*/notes.md`.

## Formats
1. **No-speaker (VSL, launch, onboarding, feature drop)** — 16:9 primary, 9:16 cut. Template: `motion/saassuite/sample-15s.html` (+ `shoot.js`).
2. **Speaker reel** — 9:16 crop on Andrew (speaker boxes in `/home/user/work/formats/<clip>/speakers.json`), **karaoke captions**: 2–3 words (break on >0.35s pause or punctuation), Inter Display/Tight 800 ~92px white with 4px hard shadow, active word `#9B83FF`, y≈1400/1920. Hook line on the chest area (not the face) for the first ~3s. Floating card cutaways sit over the body (y 640–1240), never over the face; one per 4–6s. Template: `motion/saassuite/reel-pod1-02/overlay.html` (transparent overlay rendered with Playwright `omitBackground`, then ffmpeg overlay on the cropped clip).
3. **Statics/carousels** — same tokens and type; performing formats (yellow captions, podcast stack) keep their look.

## Workflow
1. Write the beats (But/Therefore) and pick moves from the table. Default busyness.
2. Build `index.html` with `window.render(t)` — no CSS transitions, timers or `Date`. Fonts via @font-face from `tools/fonts`.
3. Render: `node motion/recreate/shoot.js page.html frames DUR 30 W H` → `ffmpeg -framerate 30 -i frames/%04d.png ...`.
4. Sound: ElevenLabs music (`/v1/music`, key in `$ELEVENLABS_API_KEY`) with the ambient prompt; SFX from `vendor/motion-graphics/skills/sound-effects/sfx/` (kit/whoosh, kit/click, pop/kenney-*, ding/kenney-interface-confirmation-*). Loudnorm −14.
5. QA: contact sheet of frames; text never over faces; nothing off-frame; one accent per frame.
6. To match a new reference exactly: `motion/recreate/README.md` (render + `compare.sh` for ref | ours | diff + SSIM).
7. Need ideas or prompt wording for a new piece? Search the scraped Prompt Motion library: `docs/brand-video/prompt-motion/library.json` (238 Claude-made motion videos with their prompts; filter by `tags`, e.g. `product-ui`, `kinetic-type`, `charts`). Borrow structure and wording, never another brand's look. Refresh: `python3 tools/prompt_motion_scrape.py`.
