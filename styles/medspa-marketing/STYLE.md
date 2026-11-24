# Med Spa Marketing (style pack)

Warm, calm, premium: what a good med spa feels like. For staff training and marketing explainers that are not
screenshot walkthroughs (for those, use `medspa-emr-training`). Approved source: "How to collect payments & deposits"
(Nov 13), `example/` (`msp.js` = every scene; `index.html?fmt=h|v`).

## Look
- Background warm cream `#FBF6F2` with a soft rose glow behind the subject. Ink `#241F1D`, muted `#8B817B`.
- Accent **rose** `#C2657A` (soft `#F6E3E6`) for one word, an icon, a highlight; **sage** `#3F8B65` (soft `#E2F0E8`) only
  for "done / paid / yes". Red `#D64545` only for a warning. White cards: border `#EDE3DC`, radius 28, shadow
  `0 2px 2px rgba(36,31,29,.04), 0 24px 60px rgba(36,31,29,.10)`.
- Headlines: **Fraunces** 600–700 serif, tight (−0.02em), key words in rose. Labels: Inter 800, 22 px, letter-spacing .22em, rose, uppercase.
  Body and UI: Inter 600–800.
- Art lives on a 1080×1080 stage, centred in 16:9 (zoomed 1.18×) and in the middle band of 9:16. Rebuilt UI cards and simple
  line icons (`ICON` in msp.js); no raw screenshots unless the job is a walkthrough.
- Captions: Inter 800 44 px, white on a dark pill, the spoken word coloured rose (word-by-word from ElevenLabs timings).

## Motion (`lib.js`)
- `pop` (spring 15, damping .55) for icons and pills, `rise` (outQuart .45 s, 40 px, blur 8→0) for text and cards,
  `outAt` (0.25 s fade + blur) to leave. One idea on screen at a time; scenes change on the voice's sentence breaks.

## Sound
ElevenLabs voice (calm, warm), word timings drive captions and cues. Light music bed under the voice; −16 LUFS final.

## Don't
Purple, neon, dark scenes, stock photos of faces, more than one accent colour per frame.
