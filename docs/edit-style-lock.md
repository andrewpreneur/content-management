# Edit style LOCK (every video edit, every runner): v2, Nov 25, 2026

Andrew, said many times: **"good clean motion graphics with white text."** No violet text, no yellow, no boxes. This file
wins over any other style note, brand-style JSON, older reference or habit (the Nov 24 Fail V+S intro used violet words:
that was WRONG, never copy it).
Before reporting ANY edited video: `python3 tools/style_check.py OUT.mp4 --baseline CLEAN.mp4 --out check.jpg` must pass
(CLEAN = the same cut with no captions/text, e.g. `reel.py --clean`, so colours already in the footage, like a logo on a
hoodie, don't count). Look at `check.jpg` yourself. Report `data.styleCheck` = its JSON. A failing video is fixed, not reported.

## Captions (all formats: long form, montages, ads, reels)
- Made ONLY by `tools/house_captions.py` (also what `intro_edit.py`, `montage_intro.py` and `reel.py` use).
- Inter Display Bold, **white**, soft dark outline + shadow, **no box, no pill, no band** behind the text.
- 2-4 word phrases broken at punctuation, sentence case (never ALL CAPS). The word being spoken is full white, the rest
  of the phrase slightly dimmed. **No colour on captions at all.**
- Lower area: 16:9 at 86 % height, 9:16 at 80 % height; sized by width on vertical so a line never runs off.

## Text on screen (titles, hooks, CTAs)
- Clean white Inter Display Bold with a soft shadow, straight on the video. No coloured words, no pills, no bands.
- Long form title: left third, 2 short lines, first ~3 s (`intro_edit.py --title/--sub`).
- Ads/reels: hook in the top area for the first ~3.5 s, CTA line at the end, both white.

## Motion graphics (when the edit has them)
- Clean and minimal: white or near-black floating cards (SaaSSuite pack shapes, radius, soft shadow, measured ease-out
  motion), white/ink text. Colour only from the real product UI being shown. No violet fills, no purple scenes, no glow.

## Framing
- Calls and podcasts: faces only, side by side (`--tiles` / `--crops`), the call app's interface never shows; montages
  skip shared-screen moments (default; `--allow-screens` to override).
- Vertical talking head (ads, reels): `reel.py` layout `"full"`: the face fills 9:16, no bands, no square-in-the-middle.

## Sound
Voice untouched (never denoise/compress Andrew's voice), music well under the voice, -16 LUFS for YouTube, -14 for reels.

## Banned
`REEL_LOOK=v0`, `brand_look.py` yellow accents on video, `stylekit.py` styles, uppercase karaoke, raw call UI, any coloured caption or
on-screen text (violet included), the violet-word Fail V+S intro as a reference.
