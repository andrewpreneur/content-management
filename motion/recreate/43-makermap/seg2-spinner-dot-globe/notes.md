# 43-makermap · segment 2 (4.6–9.5 s): spinner → check → orange dot "You're on the map" → dotted globe

Files: `index.html` (render(t) = MM.render(4.6 + t)), `../engine.js` (shape, spinner and check, shared with segment 1), `../globe.js` (dot, rings, caption, globe, pins, counter), `../globe-data.js` (land dots and pins).
Compare video: `seg2-spinner-dot-globe-side.mp4`. Per-frame SSIM: `seg2-spinner-dot-globe-ssim.txt`.

## SSIM per round (avg over 147 frames)
| round | change | avg |
|---|---|---|
| 1 | first build (eq 1.6° land grid, pins from the reference) | 0.92937 |
| 2 | wave timing keys, motion-blurred dots, lighter dots, pins ×0.65, halo/ring fixes | 0.93117 |
| 3 | sphere intro retimed (+45 ms), centre path, reveal earlier | 0.93050 |
| 4 | land grid 1.5° (matches the measured 12.2 px dot pitch) | 0.93037 |
| final | check fade, blurred wave ring | **0.93037** |

Split: **4.6–6.7 s (spinner, check, dot, caption) = 0.9935**; **6.7–9.5 s (globe) = 0.883**.

The globe is the limit. Land shapes, rotation, dot pitch, dot tone and pin layout match at the macro level, but the reference's dot lattice could not be identified dot-for-dot. I tried:
- regular lat/lon grids;
- equal-spacing rows (1.5–2.0°, several phase and rounding rules);
- Fibonacci lattices of 16k, 20k and 25k points.

Every one stayed at about a 7 px mean point distance. Misaligned dots kill SSIM in those windows even when the frame looks the same at viewing size.

## Measured values and curves (absolute reference seconds)
**Spinner and check, 4.6–5.65.** Same as segment 1 notes (arc r 75, stroke 15, scale lag, check dash ease).

**Dark circle closes in, 5.625.**
- Diameter 314 → 108 with S(ω 16, ζ 0.7).
- Measured: 312, 280, 236, 191, 156, 132, 116 and 106 at 5.633 / .667 / .7 / .733 / .767 / .8 / .833 / .867.

**Orange dot grows inside it.**
- Diameter = 108·(1 − e^(−(T−5.66)/0.085)), a first-order curve.
- Measured: 12, 33, 56, 75, 88, 97 and 103 at the same steps.

**Group rise.** Centre y = 720 − 65·S(T−5.66, ω 12, ζ 1), ending at 655 at about 6.17.

**Halo.** Orange at 22% (sampled rgb 238,200,190 over the background), diameter = 1.52 × dot (about 164).

**Ring 1.** 5.70–5.95, diameter 250 → 300 (τ 60 ms), 3 px, alpha 0.4 → 0.

**Ring 2.** From 5.95: diameter = 158 + 135·(1 − e^(−(T−5.95)/0.12)). Measured 158, 166, 190, 212, 232, 248, 260, 270, 279, 284, 289 and 291 at 33 ms steps. 4 px stroke, alpha 0.85 (× 0.5 fill), fades 6.30 → 6.45.

**Caption "You're on the map".**
- Inter Tight 600, 55.5 px, #0B0B0C, centred at x 720, baseline 837. Box 491–947 × 796–846; the 'Y' is 29 × 40.
- In 5.87 → 5.97: blur-dissolve plus a 17 px rise with S(14, 1).
- Out 6.43 → 6.50: blur plus a 3 px lift.

**Sphere.**
- Diameter = target·S(T−6.532, 15.85, 0.7045), with target = 1000 + 3000·e^(−τ/0.09). This is the same "relaxing-target spring" recipe as the input morph.
- Measured via the bright-interior extent ÷ 0.72: 904, 1300, 1320, 1247, 1144, 1070, 1032 and 1000 at 6.60 → 7.00 in 50 ms steps.
- Centre: x 718; y = lerp(630, 706, S(T−6.55, 14, 1)).
- Shading: radial-gradient at (40%, 36%) running L 251 → 250 (0.5R) → 246 (0.8R) → 240 (1.0R) → 232 (1.2R) → 228 (1.32R). It is lit from the top left; measured 250 in the centre, about 242 at the top-left rim and about 230 at the bottom-right rim.
- Shadow: `0 22px 50px rgba(40,40,30,.10), 0 4px 12px .06`.
- Intro blur 9 px → 0 over 6.55–6.80.

**Projection.** Orthographic, dot radius Rd = 0.988 × sphere radius (dots fitted R about 494 against a visual R of 500).
- View rotation `ROT` (lon0, lat0) was fitted every 0.1 s by density correlation of detected land dots (r 0.90–0.93).
- It holds Portugal (−9, 39) at 6.5–6.75, swings west to (−74, 24) by 8.3–8.4 (a 3.5° per 0.1 s cruise, then ease), and returns east to (−17, 37) by 9.4.
- Keys are interpolated with monotone cubic.

**Land dots.**
- Equal-spacing rows of 1.5°, n = round(360·cos(lat)/1.5) per row, Natural Earth 50 m land mask, 5,208 dots.
- Dot radius 2.9·(0.55 + 0.45μ)·(Rd/494), where μ = cos of the angle from the view centre.
- Grey L = 245 − 172·(0.4 + 0.6μ). Measured centre-dot min L 58, then 88 at r 0.6, 111 at 0.78, 132 at 0.9 and 151 at 0.98.
- Limb alpha ramp μ 0.02 → 0.14.
- Intro: a radial wipe from the user's pin at 450°/s from 6.655, with a 15° soft edge, and a darkness ramp of 0.55 → 1 over 6.7–7.2.
- Motion blur: when the projected speed exceeds 2.5 px per 1/240 s, the dots are sub-sampled across a 1/120 s shutter (up to 8 samples, alpha/√N). The reference dots visibly smear and lighten during the fast swings (6.9–7.3 and 8.5–8.9).

**User pin.**
- Moves from the caption position into the projected Portugal (−8.6, 39.4) with S(12, 1) from 6.5.
- Diameter 20 + 88·e^(−(T−6.5)/0.14). Measured 103, 87, 68, 52 and 40 at 6.533 → 6.667, settling at 20.
- The halo fades 6.48 → 6.56.

**Wave and pins.**
- A small circle of angular radius θ(T) around the user's pin. Keys (T, θ): 7.0 0°, 7.1 8°, 7.2 18°, 7.3 42°, 7.4 60°, 7.5 72°, 7.6 80°, 7.7 86°, 7.9 95°, 8.3 112°.
- Stroke 5 px at orange alpha 0.42·(1 − θ/110), with a 1.5 px blur.
- Each maker pin pops in when the wave reaches it, scaling with S(18, 0.5).
- The 338 pins were un-projected from the reference frames at 8.1 s, 9.0 s and 9.4 s: orange blobs → lat/lon, radius ÷ μ, clamped to ≤ 22 px and drawn at × 0.65.
- Pin alpha 0.88.

**Counter pill.**
- Ink #16151A, 258 × 76, radius 38, centred at (720, 1200).
- Dot: d 14 at x 618–631.
- Number: Inter Tight 800, 28.2 px, white, starting at x 648.
- "makers": Inter 500, 22.8 px, #B3B4B9, starting at x 739.
- In: 7.12 → 7.24 blur-dissolve, with scale 0.45 → 1 from S(20, 0.75).
- Out: 9.33 → 9.40.
- Count keys: 7.25 1,645; 7.3 1,682; 7.5 ~3,080; 7.7 3,336; 7.9 3,360; 8.1 3,377; 8.3 3,389; 8.5 3,393.

## What still differs
- **Globe dot lattice.** The macro match is good but the dot-level match is not; this costs about 0.1 SSIM on globe frames. The reference generator is most likely a WebGL dotted globe (COBE-style, where the dot texture is sampled from a land map). A version that drew the same lattice would close most of the gap.
- **Pins.** Positions are real, recovered from the reference. Sizes and colour are approximate: the reference's big pins are translucent with lighter rims. The rolling-digit odometer and the vertical-blur digit roll on the counter are not built; the number just steps.
- **Caption.** The reference caption weight looks about 50 lighter than Inter Tight 600.
- **Ring 1.** Slightly fainter than the reference.
- **Sphere intro.** At 6.55–6.6 the reference sphere has a softer, glowier rim.
