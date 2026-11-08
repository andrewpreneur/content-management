# 43-makermap · segment 1 (0.0–5.5 s): logo pill → button → input → card → spinner

Reference: `/home/user/work/refs/43-makermap-shapes.mp4` (1440×1440, 60 fps). Recreation renders at 1440×1440 and 30 fps.
Files: `index.html` (the page), `../engine.js` (the whole state machine, pure `render(T)`), `../makermap.css`, `../fonts/`, `../avatar.png`.
Compare video: `seg1-morph-chain-side.mp4` (ref | ours | diff). Per-frame SSIM: `seg1-morph-chain-ssim.txt`.

## SSIM per round (compare.sh, 1280 px, avg over 165 frames)
| round | change | avg SSIM |
|---|---|---|
| 1 | first build from measured values | 0.99288 |
| 2 | baseline fix, card→circle refit, spinner scale lag | 0.99268 |
| 3 | edge-measured card→circle springs, row stagger + rise, monotone cursor path | 0.99327 |
| 4 | button→input "relaxing-target" spring, content-in earlier, morph blur | 0.99314 |
| 5 | avatar pop, That's-me button colour, radius catch-up | 0.99318 |
| final | check fade timing | **0.99315** (worst frame 0.978 at 3.6 s, card rows settling) |

The average is high because most of the frame is background. The worst frames are the card rows settling (3.5–3.7 s), where text edges are 1–2 px off.

## Measured values
**Canvas.** Warm off-white radial gradient centred at (720, 600): L = 244 − 12·(r/1000)^1.5 and B = L − 5. That gives #F4F4EF at the centre, #ECECE7 at the sides and #E8E8E3 in the corners.
**Palette (pixel-sampled).** Pill ink #16151A; spinner circle #14151A; input #FCFCFC; card #FDFDFD; orange #E2552A. Logo dot ring: orange at 32% over ink. Enter key at rest #F1F1EE with a #A5A5A5 icon, and #17171C with a white icon on hover.
Card greys: "Is this you?" #6F6F6F, handle #707176, Portugal #6E6F74, Not me #6C7074, bio #28272A.

**Shape boxes (all centred at 720, 720).**
| state | w × h | radius |
|---|---|---|
| logo pill | 594 × 168 | 84 (h/2) |
| logo on hover | ×1.024 (608 × 172) | |
| button | 748.8 × 161 | h/2 |
| button pressed | ×0.954 (712 × 154) | |
| input | 924–926 × 134.5 | 67 (h/2) |
| card | 824 × 552 | 46 |
| spinner circle | 314 × 314 | 157 |

**Fonts.** Inter and Inter Tight from Google Fonts. The TTFs are in `../fonts`. The reference looks like Inter Display, so Inter Tight stands in for the display cuts.
| text | font | size | colour | measured box |
|---|---|---|---|---|
| MakerMap | Inter 700 | 64 px, +0.8 px tracking | white | cap 46, x 586–920 |
| Put me on the map | Inter Tight 600 | 51.5 px | white | 432 wide |
| @verbove | Inter 500 | 39 px, +0.3 px tracking | @ #9C9DA1 | text starts left + 91 |
| Is this you? | Inter 600 | 27 px | | |
| Martijn Verbove | Inter Tight 800 | 47.5 px | | |
| handle | Inter 500 | 27 px | | |
| bio | Inter 400 | 31 px | | line pitch 45 |
| Portugal / Not me | Inter 500 | 28 / 27 px | | |
| That's me | Inter 600 | 29.3 px | | |

Baseline placement: with line-height 1, the baseline sits at top + 0.952·size for these TTFs in Chromium (measured, not 0.864).

**Card layout (from the card's top-left corner, 824 × 552).**
- Is-this-you: x 51, baseline 76.
- Avatar: circle d 142 centred at (121, 183).
- Name: x 229, baseline 178. Handle: x 225, baseline 218.
- Bio: x 52, baselines 327 and 372.
- Orange dot: d 16 at (59.5, 454). Portugal: x 79. Not me: x 384. Both on baseline 464.
- Button: (514, 407), 259 × 94, radius 47.

**Input layout.**
- Content is anchored to the LEFT edge: '@' at left + 52, baseline at centre + 14.
- Caret: 4 × 52, orange, 7 px after the text, top at baseline − 40.
- Enter key: 88 × 88, radius 23, anchored 23 px from the RIGHT edge. Icon: lucide corner-down-left, ×2, stroke 4.2.

**Shadows.**
- Dark elements: `0 34px 70px rgba(30,30,25,.17), 0 6px 14px rgba(30,30,25,.12)`. Measured −40 L at +8 px below the edge, back to background by +160.
- Light elements: `0 26px 60px rgba(30,30,25,.07), 0 4px 10px rgba(30,30,25,.05)`. Measured −16 L at +8 px, background by +100.
- The two shadows are interpolated with the fill colour (`shadowDark`).

**Cursor.** macOS arrow: black fill with a 4.5 px white stroke, scaled ×1.06; the black fill box is 19 × 31. Drop shadow 0 1.5px 2px at 28%.
- Path (tip px, monotone-cubic in time) is in `CUR` in engine.js.
- It enters from the bottom right at 0.55 s, parks on the pill, drifts to 1114,741 for the enter key, moves to 945,899 for That's me, then exits bottom right by 5.3 s.
- Click squish: scale 0.85 about the tip. Clicks run 1.52→1.58→1.68, 3.02→3.07→3.16 and 4.24→4.31→4.42.

## Timeline and curves
`S(τ, ω, ζ)` is the damped-spring step response, mass 1, so stiffness k = ω² and damping c = 2ζω. All fits are least squares on per-frame edges at 60 fps.

**Hover, 0.85 → 0.97.** Scale 1 → 1.024, ease-in-out over 0.12 s.

**Logo → button, t0 = 0.995.**
- Width 594 → 748.8 with S(ω 16.36, ζ 0.594), i.e. k 268, c 19.4. It overshoots to 764 at 1.233 (12.6%). Fit rms 1.4 px.
- Height 168 → 161 on the same spring.
- Logo content blur-dissolves out 0.90 → 1.00 (blur 0 → 12 px).
- The label blur-dissolves in 1.10 → 1.20.

**Press, 1.50 → 1.60.** Scale 1.024 → 0.954 (power-2 ease-out), then release with S(ω 22, ζ 0.85) back to 0.998.

**Button → input, t0 = 1.878.** This is the signature "relaxing-target" spring:
- Width = lerp(748.8, target(τ), S(τ, 16.67, 0.625)), with target(τ) = 926 + 186·e^(−τ/0.161).
- Result: a fast 38% overshoot to about 991 at 2.06, then a slow settle to 924 by 2.5. Fit rms 2.1 px; a plain spring could only reach rms 17 px.
- Height 161 → 134.5 with S(16, 0.9).
- Fill colour ink → #FCFCFC with a critically damped spring, ω 22.4.
- Shape blur up to 5 px (sine pulse, 1.87 → 2.06). The label blurs out 1.84 → 1.90.

**Input content and typing.**
- Content blurs in 1.95 → 2.05.
- Typing at 8 chars/s: v 2.000, e 2.125, r 2.25, b 2.375, o 2.5, v 2.625, e 2.75. Each character appears instantly.
- Because the content is anchored to the left edge, the text slides right while the width settles. That slide is in the reference.
- Caret blink-off 2.94 → 2.99.

**Enter key.**
- Hover colour 2.81 → 3.03 (power-2 ease-out, 0.22 s).
- Press 3.02 → 3.10 to 0.875, release with S(20, 0.8) to 0.96.
- Input content blurs out 3.18 → 3.25.

**Input → card, t0 = 3.253.**
- Width 926.8 → 824 with S(16.45, 0.964), i.e. k 271, c 31.7.
- Height 134.5 → 552 with S(16.03, 0.778), i.e. k 257, c 24.9. Peak 561 at 3.55 (2% overshoot).
- Radius 67 → 46 follows the height progress. Morph blur pulse 3 px over 3.26 → 3.46.

**Card rows stagger in.**
- Rows start at 3.34, 3.40, 3.48 and 3.50 (Is-this-you, avatar+name, bio, footer).
- Each row: blur-dissolve 0.12 s (blur 10 → 0) plus a 16 px rise with a critically damped spring, ω 14.
- Avatar pops from scale 0.55 to 1 with S(13, 0.6).
- That's-me button fill goes grey (150) → ink with a critically damped spring, ω 20, from 3.54.

**That's-me press.** 4.24 → 4.33 to 0.93, release with S(20, 0.8). All card content blurs out 4.44 → 4.54.

**Card → spinner circle.**
- Width 824 → 314 with S(14.09, 0.613) from 4.506.
- Height 552 → 314 with S(14.96, 0.487) from 4.524. Undershoot to about 272 at 4.78, settled by 5.07.
- Radius = lerp(46, min(w, h)/2, S(τ, 24, 1)), so it becomes a full circle by about 4.72.
- Fill #FDFDFD → #14151A with a critically damped spring, ω 19.8, from 4.49.
- Shape blur sine pulse, peak 7 px over 4.50 → 4.74. The grey, blurred rounded rectangle at 4.55–4.6 comes from this.

**Spinner, 4.61 → 5.65.**
- Arc radius 75, stroke 15, round caps, centred.
- Spinner scale lags the shape: 1 − 0.2·e^(−(T−4.7)/0.09).
- Tail angle (0° = 3 o'clock, clockwise): 140° at 4.70, rising +20° per 50 ms to 305° at 5.10.
- Head angle: 315 / 310 / 310 / 315 / 320 / 335 / 350 / 375 / 405° at the same 50 ms steps. The span shrinks 175° → 90° and then grows.
- Arc fades 5.08 → 5.20.

**Check.**
- Path (in the 314 box) M103.5 162.5 L137.5 196.5 L211.5 122.5, stroke 15.
- Drawn with stroke-dashoffset, power-2.5 ease-out over 0.27 s from 5.09. Measured progress: 0.44, 0.74, 0.91 and 0.97 at +0.06, +0.11, +0.16 and +0.21 s.
- Blur-fades out 5.55 → 5.64.

## Techniques used
- One absolutely positioned `#shape` whose left, top, width, height, radius, background, box-shadow, filter and transform are all set from `render(T)`, with `overflow:hidden`. Content layers inside it are re-anchored every frame (centre, left edge, right edge or top-left), so they ride the morph.
- Content swaps are blur-dissolves: opacity 0→1 while blur goes 10–12 px → 0 over 0.08–0.12 s. The outgoing content leaves before the shape starts moving, and the incoming content arrives as the spring passes about 80%.
- Colour changes between ink and paper use a critically damped spring, ω about 20–22 rad/s. During that colour flip the whole shape gets a short blur pulse of 4–7 px.

## What still differs
- Font: Inter and Inter Tight are close stand-ins for the reference's display face (probably Inter Display / SF). Glyph widths match within 1%, but stroke weight differs slightly, which shows as edge lines in the diff.
- The avatar is cropped from the reference frame as a placeholder. Swap in a real asset for production.
- Card text sits 1–2 px off in places, and the reference rows have a slightly different settle.
- The cursor shape is drawn by hand. It is about 1 px smaller than the reference cursor on the dark pill, where the reference shows a slightly larger hover cursor.
- The background gradient is a fitted radial. The reference may add a faint extra glow around the element, which is at most about 2 L.
