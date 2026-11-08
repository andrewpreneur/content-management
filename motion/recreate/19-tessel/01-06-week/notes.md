# 19 Tessel, 1.0–6.0 s: "Your week / doesn't fit."

Reference: `/home/user/work/refs/19-tessel-calendar.mp4` (1920×1080, 60 fps). Recreation: `index.html` (`window.render(t)`, t = 0…5 local, offset +1.0 s inside). Rendered at 1920×1080, 30 fps. Compare video: `01-06-week-side.mp4` (ref | ours | diff). Per-frame SSIM: `ssim-final.txt`.

## SSIM per round
| Round | Change | Avg SSIM |
|---|---|---|
| 1 | first build from the measurements below | 0.9316 |
| 2 | headline bbox refit (±3 px), grid lines 2 px, labels 400 weight, three block fixes (Demo 10:30 added, Vendor call +5, Roadmap lands f87) | 0.9378 |
| 3 | "doesn't fit." push curve refit, DOF opacity of grey blocks (0.8), late blocks fade in over 0.6 s, collapse refit (0.19 s, u^2.9), line retract refit | **0.9388** |

Per-frame: 0.98–0.998 for f1–20 (grid build), 0.94–0.97 for f20–80 (pile-up), 0.88–0.92 for f90–140 (DOF and headline phase), and 0.999 after the collapse.

## Method
- Frames came out at 30 fps (`ffmpeg -ss 1 -t 5 -vf fps=30`). I also took 60 fps frames to study the fast block drops.
- Camera: I tracked the grid lines in every frame (column-darkness peaks), so camera scale = column spacing / 275.6.
- Blocks: I annotated them by hand in 5 key frames (f40, f50, f70, f92, f130), changed them to world coordinates with the camera scale, then got each landing frame automatically. The test was the first frame where the title patch, sampled in world space, matched (NCC > 0.85) its reference frame.
- Text: ink bbox per frame (threshold < 80), plus ink mass and centroid per word for the blur-in.

## Measured values (world space = screen space at camera scale 1.0, origin of scale = (960, 540))
**Palette (pixel-sampled):** bg #ffffff · red #dc143a (220,20,58) · ink #0a0a0a · grey block #eeeef1 (237,238,241) · black block #0a0a0a · vertical grid #e9e9e9, 2 px · horizontal grid #e7e7e7, 2 px · hour labels #8e8e8e · pill fill red with white text.

**Grid:** columns at x = 271 + 275.6·k. Hour lines at y = 456 + (h−8)·120.6, so 08:42 lands exactly on y = 540 (the red line). Hour labels: left x = 79, centre 21 px below the hour line, Inter 400 19.5 px.

**Red line:** 2.4 px tall, y = 540. It grows from the centre: start 0.762 s, easeOutExpo, 0.64 s, half-length 960. Measured half-lengths per 30 fps frame: 131, 371, 554, 674, 760, 820, 861, 892, 914, 929, 940, 948, 954, 958, 960.

**Dot:** Ø 28 at (960, 540). Pop at 1.02 s: scale 1 → 1.33 in 12 ms, then exp decay τ = 0.10 s (Ø measured 36, 34, 32, 30, 30, 29, 28). At the end it grows to Ø 34 (×1.2, easeOutCubic 0.15 s from 5.68 s).

**"08:42" pill:** 69×32, radius 7, left x = 73 (world). Appears at 1.022 s: opacity easeOutCubic over 0.10 s, and slides in from +19 px over 0.20 s (easeOutCubic).

**Grid draw-on:**
- Horizontal lines grow from x = 960 outwards. Half-length = 1000·easeOutCubic((t − 1.0 − rank/60)/0.4), where rank = order of |y − 540|, so the stagger is 1/60 s per line.
- Vertical lines grow linearly from y = 540 at 3600 px/s, up to a half-length of 520. Start 1.0228 s + [0, 0.033, 0.10, 0.14] s by rank of |x − 960|.
- Labels fade in linearly from 1.29 s over 0.12 s.

**Camera push:** column spacing per frame (f = 30 fps frame, f1 = 1.0 s): f10 275.6, f20 276.4, f30 277.8, f40 279.8, f50 282.8, f60 286.0, f70 288.6, f80 290.4, f90 291.6, f100 292.6, f110 293.0, f120 293.4, f130 293.4. That is +6.5 % over about 3.7 s, an in-out curve with its fastest point at f55 (≈ 2.8 s). Implemented as monotone-cubic interpolation of the measured table.

**Blocks:** 44 blocks in total. Each record is x, y, w, h, style, title, time, rotation and landing frame (in `BL`). Rotations run from −2.5° to +2°.
- Width ≈ 263 (column width − 13). Heights: 54–57 (title only), 62–90, 108–120, 176–183.
- Radius 12. Padding 15/17. Title Inter 600 22 px. Time Inter 400 17 px #8c8c8f.
- Styles:
  - Grey: #eeeef1, shadow 0 0 0 1px rgba(0,0,0,.035) + 0 10px 22px rgba(0,0,0,.07).
  - Outline: white fill, 2.2 px #0b0b0b border.
  - Black: #0a0a0a, shadow 0 10px 22px rgba(0,0,0,.14).
- **Entry (slam):** drops 150 px over 0.12 s with easeOutQuart, starting 0.07 s before the landing frame. Opacity reaches 1 at 35 % of the drop. Vertical motion blur is an SVG feGaussianBlur σy = v/60/2.2 (v in px/s, capped at 40), which reproduces the "barcode" streak of text at 60 fps. Measured on "Offsite" at 60 fps: about 100–150 px of travel in 3–4 frames (50–67 ms), with blur on the first 2 frames.
- Landing frames sit at an irregular cadence of about 1–3 per 0.1 s from f16 to f112. Stacked blocks pile on the same slot with small offsets.

**"Your week":** Inter Display Bold. The ink bbox (world) is x 664.8–1251, cap top 333 to baseline 425.6, so font ≈ 129.6 px with fitted tracking (≈ −0.044 em).
- Per-word reveal: "Your" at 2.00 s, "week" at 2.15 s (stagger 0.15 s).
- Each word: opacity easeOutCubic 0.15 s, blur 14 → 0 px over 0.25 s, translateY +28 → 0 over 0.25 s (all easeOutCubic). The measured centroid fell 410 → 384 over 6 frames, and sharp pixels appear 4 frames after the start.
- The line moves up 40 px (easeOutCubic, 0.14 s) at 3.925 s, just before line 2 arrives.

**"doesn't fit.":** Inter Display Bold. Ink bbox (world, at own scale 1) x 215.6–1708.6, top 662.4 to baseline 903.2, font ≈ 326 px.
- Arrives at 4.00 s: opacity 0 → 1 over 0.07 s, blur 18·(1−u)² over 0.10 s, scale 1.07 → 1.00 over 0.20 s (easeInOutCubic).
- Then a slow push 1.000 → 1.049 from 4.233 s to 5.30 s (easeInOutSine). Measured own-scale: f100 1.000, f110 1.014, f120 1.039, f126 1.046, f130 1.049.

**Depth of field on the background:** starts at 4.1 s and runs 0.2 s (easeOutCubic). The block layer blurs 0 → 2.7 px (10–90 % edge width went 1 → 7 px). Black blocks go to opacity 0.75 (#0a → #48, measured 72). Grey blocks go to 0.8 (237 → 241). The grid and labels stay sharp.

**Collapse to the dot (5.633 s, 0.19 s):**
- World scale k = 1 − u^2.9.
- Rotation −10·u² degrees.
- Blur 14·u px, opacity fades over the last 8 %.
- The red line retracts on its own, starting at 5.665 s for 0.115 s (u^2.2).
- Measured content width: f141 1861, f142 1764, f143 1597, f144 1267, f145 592, f146 gone.

## Fonts
The reference display face is a tight neo-grotesk. The closest free match is **Inter Display** (Inter opsz = 32). I downloaded the variable Inter from Google Fonts and instanced it to static TTFs (`InterDisplay-Bold.ttf`, `-SemiBold`, `-Medium`). UI text uses Inter Regular, Medium and SemiBold (Google Fonts TTFs).

## What still differs
- Block choreography is about 85 % right. Some blocks in the pile are approximations: titles in stacked piles, exact landing order, and the transient blocks that are covered later. Small rotations are estimated.
- The reference has a short global shake when "doesn't fit." lands (f91–92 vertical blur on Offsite). Not reproduced.
- Late black blocks (Retro, Offsite 08:30) render as soft grey gradients in the reference, because they arrive inside the DOF. Ours are flatter grey.
- The collapse uses an isotropic blur. The reference has a true zoom/radial blur with some spin smear.
- Headline glyphs are within about 3 px. Inter Display is close, but the tracking had to be fitted per line (−0.044 em and −0.026 em), which suggests the original font is slightly narrower.
