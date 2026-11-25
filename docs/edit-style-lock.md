# Edit style LOCK (every video edit, every runner): v1, Nov 25, 2026

Andrew has corrected this more than once. This file wins over any other style note, brand-style JSON or habit.
Approved reference: the Fail V+S edited intro (Nov 24), frames in `docs/brand-video/reference/approved-captions.jpg`.
Before reporting ANY edited video: `python3 tools/style_check.py OUT.mp4 --baseline CLEAN.mp4 --out check.jpg` must pass (CLEAN = the same cut with no captions/text,
e.g. `reel.py --clean`, so colours already in the footage, like a logo on a hoodie, don't count), and you look at
`check.jpg` (your frames on top, the approved reference below). Report `data.styleCheck` = its JSON. A video that fails is
not reported as done: fix it and check again.

## Captions (all formats: long form, montages, ads, reels)
- Made ONLY by `tools/house_captions.py` (also what `intro_edit.py`, `montage_intro.py` and `reel.py` use).
- Inter Display Bold, **white**, soft dark outline + shadow, **no box, no pill, no band** behind the text.
- 2-4 word phrases broken at punctuation; the word being spoken is **violet #7B5CFF**; sentence case (never ALL CAPS).
- Lower area: 16:9 at 86 % height, 9:16 at 80 % height; sized by width on vertical so a line never runs off.
- Never yellow (that is the retired v0 look), never black text on a white box, never another font or colour.

## Text on screen (titles, hooks, CTAs)
- White Inter Display Bold with a soft shadow, straight on the video; ONE accent word violet (`*word*` in reel.py).
- Long form title: left third, 2 short lines, first ~3 s (`intro_edit.py --title/--sub`).
- Ads/reels hook: top area, first ~3.5 s; CTA: white line + one small violet pill. No navy bands, no series pill.

## Framing
- Calls and podcasts: faces only, side by side (`--tiles` / `--crops`), the call app's interface never shows; montages
  skip shared-screen moments (default; `--allow-screens` to override).
- Vertical talking head (ads, reels): `reel.py` layout `"full"`: the face fills 9:16, no bands, no square-in-the-middle.
- Graphics (only when asked): SaaSSuite pack (`styles/saassuite`): off-white/near-black floating cards, violet ONLY as a
  small accent (< 5 % of the frame).

## Sound
Voice untouched (never denoise/compress Andrew's voice), music well under the voice, -16 LUFS for YouTube, -14 for reels.

## Banned
`REEL_LOOK=v0`, `brand_look.py` yellow accents on video, `stylekit.py` styles, uppercase karaoke, raw call UI, any caption
colour except white + violet.
