# Hook system — the first 10 seconds (from the vendored skills, Nov 4 2026)
Sources: `vendor/instagram-agent-skill/skills/ig-reel` (hook formulas, scoring, beat timing) and `vendor/motion-graphics/skills/{motion-broll,sound-effects}` (spring motion engine, measured sound pass). Andrew's direction: re-edit **only the first 10 s** for now and make it deliberate.

## Structure (ig-reel "the shape", applied to 10 s)
| Time | Job | Rules |
|---|---|---|
| 0.0–~3.0 | **Hook** — the claim | Spoken line + on-screen line written separately. On-screen ≤ 6 words, up at **frame 1**. Motion in the first frame (never a static face). Numbers over adjectives. No greeting/intro ("Welcome to…" scored 5/100). |
| ~3–7 | **Stake** — why it matters to the viewer | One line. Change the frame on it (layout switch / full-face punch). Use a *but* turn (But/Therefore rule). |
| ~7–10 | **Open loop** — the question that keeps them | Show the payoff is coming ("1 layout → every client") and end on a pointer ("Here's how ↓"). Therefore-beat. |

**Pick the hook with data:** write 3+ candidate spoken lines from the real transcript, run `python3 vendor/instagram-agent-skill/skills/ig-reel/hookscore.py hooks.txt`, shoot/cut the top one (≥ 50 or it isn't a hook). Formulas: `hooks.json` (26, e.g. #5 Time Collapse, #13 Before/After, #24 The Reveal). Then `beats.py` to check no beat > 4 s.
**Safe zone (1080×1920):** keep text inside y 230–1440 and clear of the right 230 px.

## Visual hook = motion graphics, not skip cuts
- One scene for the whole 10 s in the motion engine (`motion/clips/*.html`, built with `vendor/.../motion-broll/engine/build.py`, rendered with `render.js` = 4 sub-frames/frame motion blur).
- **One shape that never cuts** carries the idea: it morphs (springs) from state to state on the spoken word (e.g. 6 AI tab pills → one "AI" pill on "one"; nav menu → rows hide on each click; layout card → fans out to sub-accounts).
- Face is real footage inside the scene (frame-accurate JPEG sequence), and the **face card springs** between split and full screen — that is the transition, no hard cuts.
- Captions one word at a time, pop-in spring, accent words italic serif (S1 style). Headline per beat.
- Never invent numbers/results: labels come from the transcript or real UI (tab names, nav sections).

## Sound (sound-effects skill, adapted)
- Real recorded CC0 SFX from the kit (never synthesised): whoosh on layout moves (2 frames early), pop on appear, click on cursor clicks, riser that **ends** on the hit, impact on the reveal.
- Music bed (Mixkit, downloaded at runtime, never committed) beat-aligned to the hard moves, **-12 dB and ducked ~10 dB under the voice**. Priority voice > SFX > music.
- Measure the exported MP4: **-16 LUFS integrated, true peak < -4 dBFS** (stereo + mono). `tools/sound_mix.py` does all of this and writes `*.sound.md` + `*.credits.txt` with 5 timestamps to check by ear.

## Commands (hook v1 example)
```
python3 vendor/motion-graphics/skills/motion-broll/engine/build.py motion/dist motion/clips/sy-hook-01.html
NODE_PATH=/opt/node-tools/node_modules node vendor/motion-graphics/skills/motion-broll/engine/render.js motion/dist/sy-hook-01.html out_silent.mp4 30
python3 tools/sound_mix.py --video out_silent.mp4 --voice voice.json --cues cues.json --music music.mp3 --out sy-hook-01.mp4
```
