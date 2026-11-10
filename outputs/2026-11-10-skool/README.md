# Skool About + Onboarding (Nov 10)

**Why new:** the Nov 7 Skool videos (`../2026-11-07-skool/`) were made before the SaaSSuite style was locked (puzzle / build-log / colour-flood looks) and use the AI voice clone, which Andrew doesn't like. They are retired. Plan (Andrew, Nov 10): Andrew records two audio clips; we build full motion-graphic videos on his real voice in the locked style.

## Images (done) — `images/`, 1920×1080, locked style
- `skool-cover.png` — the 4 things you get
- `skool-p1.png` access to me · `skool-p2.png` training · `skool-p3.png` founder calls · `skool-p4.png` first access to new software (dark/premium)
- Source: `images/page.html#<id>`; the chat/lesson text is placeholder example copy.

## Audio (Andrew records voice only; videos are full motion graphics in the locked style)
Record on your phone's voice memo app, in a quiet room, phone about 6 inches away. One take each is fine; pauses get cut.

### 1. Sales / About (~45 s)
If you run an online business and want to utilize AI and software to make more money, this community is for you.

There's a new AI tool every week. But knowing which ones actually make you money, and how to put them to work in your business, is the hard part.

That's why I built this.

Inside, you get direct access to me, step-by-step training, calls with other successful entrepreneurs, and first access to the new software and systems I'm building.

No guessing. Just a clear path to using AI and software to grow your business.

Click join, and I'll see you inside.

### 2. Onboarding (~70 s), goes through the 4 priorities
Welcome in. I'm glad you're here. Let me walk you through the four things you get inside.

Number one: access to me. Post your questions in the community and bring them to the calls. I'll help you work through your offer, your build, or whatever you're stuck on.

Number two: the training. Head into the Classroom and start with the course that matches where you are right now. Go step by step.

Number three: calls with other successful entrepreneurs. Check the calendar and join live. These are people who've already built what you're working on, sharing what actually worked.

Number four: first access to the new software and systems I'm developing. Watch the announcements, because that's where they drop first.

Your first step: make your intro post. Tell us what you do and what you want to build. I'll see you inside.

## Next
- Andrew: record both audio clips, drop in the drop folder. Owner: Andrew.
- Us: build both videos on his audio in the locked style (16:9 + a 9:16 of the About), add to the Review Hub. Owner: main session.

## Videos (done Nov 10) — Andrew's real voice, mistakes cut, locked style
Drive (_ENGINE/02-review/2026-11-10 Skool About + Onboarding):
| File | Length | Link |
|---|---|---|
| skool-sales-about-16x9.mp4 (Skool About page) | 0:57 | https://drive.google.com/file/d/1gYjEp5LottIbw45AQWYdrIc7xhzd_oJZ/view |
| skool-sales-about-9x16.mp4 (reels/ads) | 0:57 | https://drive.google.com/file/d/1SnLRGIC1Iip28HlCkS-ijELk4Q6B188m/view |
| skool-onboarding-16x9.mp4 | 2:08 | https://drive.google.com/file/d/1ycDBBkfr__sFzyURxTMc8LiWKSaiWYOW/view |

- Audio: retakes and stumbles cut (kept the best take of each line; long pauses shortened), light denoise, ElevenLabs ambient bed ducked under the voice, whoosh per scene + click on the end card, −14 LUFS / −1.1 dB TP.
- Visuals: `motion/saassuite/skool/` (engine.js + scenes.js; every scene is keyed to a spoken phrase). Captions karaoke, active word violet. Audio tools: `motion/saassuite/skool/audio/`.
- Check with Andrew: he said "chat GPT in Chrome" (caption + card say "ChatGPT in Chrome"); example chat/DM text in cards is placeholder copy.

## v2 (Nov 10, after Andrew: "audio is awful… clipping didn't work")
- Cause: v1 ran denoise + compression on clean phone audio, whisper missed several retakes, and the music sat ~-40 LUFS (inaudible).
- Fix: ElevenLabs Scribe transcript (`scribe_v1`, word timestamps) → cuts by word (`audio/cut2.py`), no voice processing (gain + peak limiter only), music normalised and ~14 dB under the voice with gentle ducking. Scribe re-check of both finals: no retakes left.
- Drive: sales 16:9 https://drive.google.com/file/d/1tIYpUjQOXG5p9VHuG_8iFcMkEc1K1Hju/view · sales 9:16 https://drive.google.com/file/d/1BkFAEr1nE4Ni4nDS0Go0IxYIRZkuMW9P/view · onboarding https://drive.google.com/file/d/1Z_lZjHlBQEBl5ascNQS1AEoZpQhlvdGC/view
- Lesson: never process Andrew's voice unless asked; use Scribe for edit transcripts.
