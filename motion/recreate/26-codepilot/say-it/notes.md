# 26 CodePilot: "Say it. It gets done." (ref 18.5–23.0 s), recreation notes

Files: `index.html` (calls `../scene.js` with `T0=5`), `say-it-side.mp4` (ref | ours | difference), `ssim.txt`.
Render: `node motion/recreate/shoot.js motion/recreate/26-codepilot/say-it/index.html <out> 4.5 30 1920 1080`.
Ref frame `f` (1-based) → `T = 5 + (f−1)/30`. The segment is 135 frames: 18.5 + 4.5 s ends at 23.0. The ref file cuts to a different film (a light calendar UI) at 23.0 s, so that cut is outside this segment.

## SSIM per round (compare.sh, ffmpeg SSIM "All")
| round | change | SSIM |
|---|---|---|
| 1 | first build | 0.9618 |
| 2 | Deny/Allow buttons placed inside card; Edit row timing f25; claim font sizes re-fit (ink boxes within ±2 px); answer typing per-char frame list; card/row font sizes | 0.9690 |
| 3 | (ask-only changes) | 0.9690 |
| 4 | output box grows on f100 (56 → 107 px); cursor 1.5× bigger; ripple opacity √ falloff; claim blur-in re-timed | **0.9691** |

Stricter check (grayscale SSIM, every 2nd frame): mean 0.944, min 0.891.
The remaining gap is spread evenly over the window: font and anti-aliasing differences (Inter/DejaVu vs SF/Menlo) on small UI text. It is not motion or layout.

## Camera / 3D window
- Same window as in "ask" (1683×1112 local). Stage `perspective: 4732px`, origin (960,540).
- Move: T 4.452 → 5.148, cubic-bezier(0.626, 0.279, 0.251, 0.907).
  - From (tx 118, ty −404, s 1, ry 0°, rx 0°) to (tx 376.2, ty −16.5, s 0.81, ry −10.76°, rx 3.7°).
  - Lands at ref A f8–10.
- Slow orbit afterwards (linear, A f30 → f130): ry +4.72° (−10.76 → −6.04), tx +4.6 px, s −0.01. This is the gentle parallax.
- Measured window edges: L/R at rows 300/700, T/B at cols 800/1500.
  - A f10: L 563/556, T 100/87, B 984/997, R ≈1912.
  - A f135: L 561/557, T 101/94, B 981/988, R 1905/1906.
  - Ours matches within 1–3 px on all frames checked (1, 10, 30, 110).
- Method: SIFT homography, then border profiles, then a 5-parameter CSS-perspective least-squares fit per frame. P was fitted once (4732) on A f20 with all 8 edge points (residual 0.4 px). The fitted model is also used to **un-warp the ref frames into flat window coordinates**, which is how every UI measurement below was taken.

## Window content (local px, flat)
- Window fill #0b0907. Glass sheen: a diagonal light band whose edge runs x ≈ 175 − 0.3y, +3…+7 levels. Done as `linear-gradient(106deg, rgba(255,255,255,.022) 0, .026 150px, 0 151px)`.
- User bubble: (1090,38) 553×90, radius 45, fill #282322. Text Noto SC 500, 29.5 px, white, from x 1123.
- Thread line: x 51, 2 px, #1c1a18. From y 215, 52 / 110 / 285 px long by stage.
- Tool rows (centres y 239 / 297 / 355), left x 88:
  - icon, then label Inter 600 25 px (167,165,163), then file name in mono 24 px (107,105,103).
  - Right side: path in mono 22.4 px (76,74,72), right-aligned to x 1552. Status at x 1580: dotted spinner, then a green ring check (71,137,91).
- Separator: y 346, 2 px, (32,30,28).
- Bash card: (88,374) 1506×265, radius 24, fill #1c1714, border 1.5 px rgba(255,255,255,.10).
  - "Bash": Inter 600, 27 px, (169,164,161).
  - Code pill: (33,92) 168×64, radius 7, #231e1b, "npm test" mono 700 24 px.
  - Buttons: Deny (1127,174) 122×66 and Allow Once (1266,174) 204×66, radius 33, fill #1b1613, border 1.5 px rgba(255,255,255,.12), Inter 700 26 px.
- Output box: (70,393) 1542 × 56 → 107 (grows on f100), radius 18, fill #191413.
  - "$ npm test": mono 700, 21 px, (186,184,182).
  - "Tests: 24 passed, 24 total": mono 20 px, (110,105,104).
- Answer line: x 38, centre y 548, Noto SC 700, 28.5 px, white.
- Composer: same as in "ask".

## UI event timeline (A frame, 1-based)
| frame | event |
|---|---|
| 1 | Read row with spinner; bubble present |
| 10 | Read ✓ |
| 25 | Edit row appears (spinner) |
| 40 | Edit ✓ |
| 55 | separator + Bash permission card (instant, no fade) |
| 65.6–71 | cursor enters from (1760,800) local to Allow Once tip (1461,586). Per-frame approach factor 0.4: `p = 1 − 0.4^(f−65.6)` |
| 75.5–79 | press highlight Ø28, grey 35 % |
| 79 | card → "npm test" row (spinner) + output box. Ripple expands r 16 → 52 easeOutCubic over 9 frames, alpha 0.38·√(1−p) |
| 95.5–100.5 | cursor exits down-right: ease-in, power 2.2, to (1700,940) |
| 100 | npm ✓, "Tests: …" line, box grows |
| 113–139 | answer typed. Char frames: 113, 114, 115, 116, 117, 119, 120, 121, 122, 124, 125, 126, 128, 129, 130, 131, 132, 134, 135 … |

## Claim (screen space, left)
- Line 1: "Say it. It gets done."
  - Reference font: SF Pro Display Bold. Ours: **Inter 700**, 52 px, letter-spacing −1.75 px, top 438.
  - Ink box: ref x 102–548, y 447–495; ours x 103–547, y 449–499.
- Line 2: 说出需求，它自己动手 — Noto SC 700, 42 px, white. Ink box: ref 101–517 × 526–569; ours 102–519 × 528–569.
- Line 3: 每一步都看得见，跑命令前先问你。 — Noto SC 400, 26 px, #aaa8a5. Ink box: ref 101–499 × 607–632; ours 102–499 × 607–631.
- **Text blur-in sweep**: each character runs `p = easeOutCubic((T − t0 − x/1230)/0.6)`, with opacity = p and blur = (1−p)·10 px.
  - x is the character's offset in its line; the sweep front moves at 1230 px/s.
  - t0 = 4.89 / 5.19 / 5.54 s for the three lines. Measured per-column progress: line 1 bin0 reaches 0.5 at A f3; line 2 at f11; line 3 at f21.5.
- Chinese is kept as Chinese (Noto Sans SC). It is not swapped for English.

## What still differs
- Small UI text: Inter/DejaVu metrics vs SF/Menlo give ±1–2 px glyph differences. This is most of the remaining SSIM gap.
- Icons (file, pencil, terminal, spinner, Anthropic mark) are hand-drawn SVG approximations.
- The ref's cursor is the macOS pointer with a soft shadow; ours is a flat outlined arrow at 1.5×.
- Ripple shape and colour are approximate (ref: grey disc, then expanding ring).
- Composer border and text in the ref are a little brighter. Composer text is about 1 px smaller in ours.
- The slow orbit is modelled as linear. The ref drift is slightly uneven (fit noise ±0.3°).
