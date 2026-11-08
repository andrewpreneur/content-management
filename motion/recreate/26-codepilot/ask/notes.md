# 26 CodePilot: "Ask" chapter (ref 13.5–18.5 s), recreation notes

Files: `index.html` (calls `../scene.js` with `T0=0`), `ask-side.mp4` (ref | ours | difference), `ssim.txt` (per-frame).
Render: `node motion/recreate/shoot.js motion/recreate/26-codepilot/ask/index.html <out> 5 30 1920 1080`.
The whole 9.5 s run (both segments) is one continuous scene in `../scene.js`. Global time `T = ref_time - 13.5`. Ref frame `f` (1-based, this segment) maps to `T = (f-1)/30`.

## SSIM per round (compare.sh, ffmpeg SSIM "All", 1280 px)
| round | change | SSIM |
|---|---|---|
| 1 | first full build | 0.9765 |
| 2 | font load fix for canvas "Ask", sub/composer text offsets, Bash card sizes | 0.9793 |
| 3 | Ask glyphs re-fitted (Inter 200 + 1.6 px stroke, per-letter dx, k scaleX 1.13); hard-edged streak slabs with sampled colour ramp; planet sink/fade curve for the dissolve; Ask drawn under the window | 0.9808 |
| 4 | claim timing re-fit (affects only the shared scene) | **0.9807** |

Stricter check (grayscale SSIM, skimage, every 2nd frame): mean 0.965, min 0.909 (f22–24, glitch frames).
Worst frames: f20–24 (random glitch slices and streaks) and f59–61 (dissolve). Everything else is ≥0.96.

## Timeline (ref frames, 1-based)
| frames | what |
|---|---|
| 1–15 | tail of the previous "greeting" screen. Slow push: scale 1/1.0128 → 1 about (1046,1132), exponential settle τ = 0.11 s |
| 16 | hard cut to bg `#0a0806` (empty frame) |
| 17–26 | "Ask" glitches in (horizontal slices, x jitter), 5 anamorphic streaks sweep L→R, planet rises and fades in |
| 25–52 | "Ask" letters slowly converge (tracking tighten); subtitle 说出需求 blur-in f28–34 |
| 57–63 | dissolve: Ask scales up, fades, softens; subtitle slides down; planet sinks and fades; UI window fades in while settling from scale 1.074 |
| 64–72 | window settle continues (scale about window top-left) |
| 73–106 | typing into composer, 1 CJK char per 2 frames |
| 122–127 | send: button flashes dark, text clears (f124), button eases back to grey |
| 131–150 | camera move into the tilted 3D window (continues into "say-it"); "Say" claim begins to blur in at f146 |

## Planet / horizon glow (fitted on ref f45 by least squares, RMSE 2.4/255)
- Shape: an **ellipse**, not a circle. cx 959.1, semi-axes a = 1066.1, b = 547.0, top of rim at y = 830.5 (hold). It is a sphere seen at an angle.
- Signed distance `d` from the rim: `g = sqrt(((x-cx)/a)^2 + ((y-cy)/b)^2)`, `d = (g-1)/|∇g|`.
- Outside the rim, the halo is added on top of the bg (10,8,6): `70.8 · exp(-d/59.3) · C(u)` with `u=(x-cx)/a`.
  - C_R(u) = 0.790 + 0.241u − 0.060u², C_G(u) = 1.067 + 0.242u − 0.350u², C_B(u) = 1.256 − 0.074u − 0.060u².
  - This gives blue-violet on the left (u=−0.8 → ×(0.56,0.67,1.28)), teal-grey in the centre, neutral grey on the right.
- Rim line: `120 · max(0, 1 − 2.373u⁴) · exp(-(d/1.907)²) · (0.634, 0.530, 0.508)`. It is a 3–4 px bright line that fades towards the edges.
- Inside the rim: body (3,3,3) plus inner light `106.2 · exp(d/6.49) · (0.85, 1, 1.05)`.
- Measured samples at x=960 (pixel RGB), going up from the rim: rim (151,161,167); −10 (55,70,77); −30 (39,54,59); −60 (29,38,40); −100 (18,19,22); −160 (12,10,8). 20 px inside: (5,5,5).
- Implementation: rendered once per pixel into an offscreen canvas (`buildPlanet`), then `drawImage` with translate/scale/alpha per frame.
- Rise: `top(T) = 830.5 + 120·exp(-5.7·(T−0.5))`. Measured tops: f17 930, f18 913, f19 898, f20 887, f25 852, f30 838, f45 831.
- Fade-in: `easeOutCubic((T−0.51)/0.7)`. Measured rim peak: 31, 55, 69, 90 (f17–20), 129 (f25), 146 (f30), 159 (f45).
- Dissolve: `top += 3·exp(0.86·(f−57))`. Measured: 834, 840, 851, 871 at f57–60. Alpha `1 − (f−56.3)/4.6`. Measured rim alpha: 0.85, 0.56, 0.39, 0.22.

## Streaks (anamorphic flares, f17–27)
- Hard-edged horizontal slabs, no blur. Each head travels **525 px/frame** from x=0.
- Each streak as y / thickness / frame where the head leaves x=0 / fade window:
  - 435.5 / 4 px / 16.0 / fade 22.6–25.6. Extra 17 px slab (y 417–434) on f22–23.
  - 640 / 7 px / 16.75 / fade 23.6–27.2. Extra 17 px slab (y 641–657) on f22–26.
  - 662.5 / 4 px / 17.5 / fade 22.6–25.2.
  - 709 / 6 px / 19.0 / fade 23.2–26.2.
  - 740 / 4.5 px / 19.75 / fade 23.6–27.4.
- Colour ramp is fixed in screen space, sampled on ref f23 row 433 (x: RGB):
  - left (violet): 0: (9,9,6), 240: (48,43,70), 480: (85,80,121), 720: (122,118,168)
  - centre (white peak): 960: (159,158,173), **1120: (255,253,248)**
  - right (gold): 1280: (157,152,122), 1440: (139,136,81), 1600: (130,101,38), 1760: (79,54,26), 1840: (40,32,19)
  - In code the ramp is multiplied ×1.25 for full intensity. The slab alpha is 0.62.

## "Ask" chapter word
- Reference font: SF Pro Display Light. Closest free Google font: **Inter** (weight 200 plus a 1.6 px stroke gives a 16 px stem, matching the ref). File `../fonts/Inter-200.ttf`. Drawn on canvas at 316 px.
- Ink box (f45): y 317–547 (cap height 230). Letter left edges at f50: A 728, s 944, k 1063 (stem).
- Inter's k is narrower, so it gets scaleX 1.13. Per-letter canvas correction dx: A −7, s −26, k −8.
- Converge (tracking tighten), measured f25 → f50: A +9 px, s +2 px, k −5 px, ink height unchanged. Ease: `easeInOutSine((f−22)/30)`.
- Glitch f17–26:
  - The word is cut into horizontal slices 6–28 px tall, seeded per frame.
  - 35 % of slices stay in place; the others jitter in x by ±140·g² px, with g = 1 − (f−17)/9.
  - About 25·g % of slices are dropped. Slice alpha is 0.8–1.0.
  - Global alpha ramps up over f16.3–19.5. Measured max: f17 107, then about 233+.
- Dissolve (dz = (f−56.6)/7):
  - Alpha `exp(−2.1·dz)`. Measured peak: 0.72, 0.52, 0.38, 0.28, 0.20 at f58–62.
  - Scale `1 + 0.6·dz^1.4` about (965, 432 − 37·dz^1.5). Measured width 477 → 570 (f61) → 720 (f63).
  - Blur 4·dz px.
  - The word sits **under** the UI window: the composer occludes it. The window fill becomes opaque over f56.8–58.3.

## Subtitle 说出需求
- Noto Sans SC 500, 40 px, letter-spacing 8 px, colour #e4e4e4. Ink box x 866–1049, y 653–693.
- Per-char blur-in: start at f27.5, 1.4 frames apart, each over 8 frames (easeOutCubic). Blur goes 8 → 0 px.
- Dissolve: translateY +100·dz^1.4 px, alpha 1 − dz/0.85.

## UI window enters (dissolve → settle)
- Window 1683×1112 (local). Flat position: top-left (118, −404) on screen, so the top is off-screen.
- Fill #0b0907, border 1 px rgba(255,255,255,.075), radius 30, shadow 0 30 90 rgba(0,0,0,.55).
- Opacity: easeOutCubic over f56.8–63. Measured composer-border contrast: .33, .40, .50, .75, .93, 1.0 over f58–64.
- Settle: scale about the window's **top-left corner**: `s = 1 + 0.074·(1 − (f−57)/26)^2.2`.
  - Measured composer top: 527 (f58), 509 (f61), 494 (f65), 482 (f70), 476 (f75), 472 (f81), 470 (f90).
  - Measured composer left edge stays at 174–176 the whole time. That is what gives away the top-left anchor.
- Composer (local): (56,874), 1572×203, radius 38, fill #151311, border 1.5 px rgba(255,255,255,.15), shadow 0 12 34 rgba(0,0,0,.45).
  - Placeholder "让 CodePilot 做什么..." (164,164,161), 26.5 px.
  - Typed text: Noto SC 500, 28.5 px, white, ink x 209–694.
  - Toolbar centre y = 1018 local: "+" (134,130,124); "Sonnet 4.6" (173,167,163) 24.5 px; "·默认" 18.5 px; "默认" 23 px; chevrons.
  - Send button: Ø66 at (1568,1018) local. Idle (136,134,132), with text (250,248,246), pressed f122–123 (30,28,26), back to grey by f127.5. Arrow (36,34,32).
- Typing frames: 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 94 (，), 96, 98, 100, 102, 104, 106. Pitch 28.7 px/char.

## Camera move B → A (starts here, finishes in "say-it")
- 3D model, CSS-equivalent: stage `perspective: 4732px`, origin (960,540).
- Window `transform: translate3d(tx,ty,0) rotateY(ry) rotateX(rx) scale(s)`, transform-origin at the centre.
- From (tx 118, ty −404, s 1, ry 0, rx 0) to (376.2, −16.5, 0.81, −10.76°, 3.7°).
- Timing: T 4.452 → 5.148 (0.696 s), **cubic-bezier(0.626, 0.279, 0.251, 0.907)**. Fit error 1.1 % of travel.
- How it was measured: SIFT homography chain, then direct border-edge profiles, then a 5-parameter perspective fit per frame (residual < 1 px).

## Greeting screen (f1–15), simplified
- Title 早上好，需要我做点什么？: Noto SC 700, 47.5 px, from x 719, centre y 309. 5×5 dot-matrix logo at (641,283).
- Composer (336,417) 1262×165: the same component at ≈0.805 scale, plus a "请求批准" item.
- Cards (318|975, 633) 642×146, radius 32, fill #1a1613.

## Fonts
- Inter (Google): stands in for SF Pro. Weights 200/300/400/500/600/700 are in `../fonts`.
- Noto Sans SC (Google): stands in for PingFang SC. Subset to the glyphs used, 400/500/700.
- DejaVu Sans Mono: stands in for Menlo/SF Mono. Menlo is a DejaVu derivative, which is why the `r` has the slab foot like the ref.
- **Chinese text is kept in Chinese**, rendered with Noto Sans SC (CJK-capable). It is not swapped for English.

## What still differs
- Glitch slices are pseudo-random: same density, amplitude and timing as the ref, but not the exact slice pattern. This makes f20–24 the lowest-SSIM frames, about 0.95.
- Streaks: the exact per-frame slab heights only match on the two measured slabs. The colour ramp is fixed in screen space; the ref's white hot-spot shifts a little.
- Dissolve f59–61: the ref Ask also ghosts (double image) slightly. Ours is a single scaled and blurred copy.
- Greeting screen: icons and the egg avatar are approximations. Card and composer text is ±1 px.
- Inter vs SF Pro: the s/k shapes differ slightly. SF's k leg is longer, so the k is stretched 1.13×.
