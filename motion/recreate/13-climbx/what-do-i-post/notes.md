# 13-climbx · 1.5–5.5 s · flag zoom → orange compose-card field "what do I post today?" → iris → ClimbX logo

Reference: `/home/user/work/refs/13-climbx-launch.mp4` (**1280×720, 30 fps**). All values are in reference px; the page scales a 1280×720 `#stage` by 1.5 → 1920×1080. `fN` = local frame (f0 = 1.500 s).

## SSIM per round (compare.sh, 4 s @ 30 fps)
| round | change | avg SSIM |
|---|---|---|
| 1 | first build: 5 phases | 0.9058 |
| 2 | line mountain = fill outline + group scale; zoom centre/curve refit; word scale became a spring; logo letters inline; icon widened | 0.9056 |
| 3 | camera curve softened, card fade-out f63.5–66, word zoom ×0.035, logo stagger 1.8 f | 0.9127 |
| 4 | iris words z-order fix, card DOF blur 0.6/1.0 px | 0.9134 |
| 5 | icon "slam" scale (2.0 → 0.55 → spring to 1), iris words blur 3 px | 0.9135 |
| 6–7 | word start times re-timed from frames (+0.5–1.5 f) | **0.9131** (kept; visually closer on "today?") |

Per-frame (final): dark intro 0.92–0.96, zoom-into-flag f11–13 ~0.86, orange field 0.88–0.91 (f15–45) and 0.83–0.86 (f48–63, fly-through), iris 0.87–0.995, logo 0.93–0.96. Log: `ssim-final.txt`. Side-by-side: `what-do-i-post-side.mp4`.

## Fonts
- "what do I post today?" + "ClimbX": **Inter variable opsz 32 (Inter Display)**; words 800 / 103 px / −0.04 em; logo 900 / 120 px / −0.035 em (cap height 87 px; ink x 546–1006, top 272).
- Tagline: Inter Display 700 42 px −0.035 em, ink x 393–884, y 449–488; "X" orange #ff6a2f.
- Cards: Inter 600 15.5 px (at card width 254). HUD: JetBrains Mono 500 9.6 px.

## Phases, measurements, techniques
### 1 · Dark flag intro (f0–12)
- bg #06060e + 70 seeded stars (0.5–1.4 px, 15–50 % white).
- Glow disc centre (636,330) r 330: radial #4a1d0a → #3d1909 22 % → #2f1409 38 % → #22100b 52 % → #170d0d 66 % → #0e0a10 82 % → transparent (banded look).
- Mountain (rest, f6): white #efece6 polygon 403–866 × 308–522, peak (636,308); orange #ff6a1f pole 9×108 r4.5 at x 632, y 203; wavy flag to x 759. Dark facets #0d0e1a fade in f6.5–8.
- **Line → fill**: orange 3 px outline (same polygon) + flag start at group scale 1.45 about (636,290), `s = 1 + 0.45·e^(−f/1.2)`; fill revealed by a clip rect rising from y 530 → 295 (easeOutCubic over f1.6–5); outline fades f3–5.
- Grey ring: r = 78 + 222·(1 − e^(−f/1.4)), border 30 → 3 px over 2.5 frames (starts as a grey concentric disc under the peak), 30 % → 0 over f4–8.
- **Zoom-through with echo trails**: world scale `e^(0.41·(f − 8.3))` about (624,372) (1.33 @f9, 2.0 @f10, 3.0 @f11); 3 ghost copies lagging 0.45 frame each at opacity 0.45 / 0.28 / 0.16 make the stepped trail. Flood to #fe6210 over f11.5–12.5.

### 2 · Orange field (f12.5–68)
- bg `radial-gradient(ellipse 72% 78% at 50% 47%, #ff8a4c 0, #ff7a33 10%, #fe6a1c 20%, #fe6210 34%, #f05b10 50%, #e05410 62%, #d24b0b 75%, #c3440a 88%, #b33c06 100%)` (sampled: centre #fe6210…#ff8344 behind text, corners #c64306–#d7520e).
- 17 "What's happening?" compose cards (positions/sizes/rotations measured at f28 in the HTML `CARDS` table): bg #fdf6f0, r 9, shadow `0 8px 16px rgba(120,40,0,.16)`, placeholder avatar 18 px #e2ddd9 + 72×4 line, grey #8f8c92 text, orange caret on some; far cards at 72 % opacity; DOF blur 0.6 px (near) / 1.0 px (far).
- **Camera dolly (parallax by size)**: each card's inverse depth q = width/254; screen scale `1/(1 − u·q)` about (630,365) with `u(f) = 0.0098·(f − 28) + 0.00018·max(0, f − 50)³` (linear creep, then cubic fly-through). Extra blur `(scale − 1.5)·2.2` px; cards hidden when 1 − u·q < 0.12; all cards fade f63.5–66. (Fit from three tracked cards: zoom centre (627,368), card scale ∝ width.)
- **Word slam-in**: each word appears at scale 2.25 and settles with a spring: `scale = 1 + spring(τ; x0 = 1.25, v0 = 0, ζ = 0.48, ω = 15.4)` (undershoots to ~0.8 at +7 frames, as measured on "what"/"do"); blur = 12·|scale − 1| px (max 14); opacity over 1.6 frames. Starts: what f14.5, do f22.5, I f32, post f38.5, today? f45; "today?" also slides −28 px after landing (τ 5 frames, decay 3 frames). Whole line drifts with the dolly at q = 0.035.
- RGB split building f61–66: two drop-shadows ±3 px (rgba(255,40,60,.55) / rgba(60,220,255,.55)) + 1.2 px blur.

### 3 · Iris to dark (f69–74)
- Banded orange disc centred (640,365): radius 640 → 283 → 6 at f69/70/71 (very fast, ~2 frames), 8 concentric bands (each 7.5 % of R, #fe6a1c → #3a160c outward); words clipped inside, RGB split ±4 px, 3 px blur, 80 %; ends as a 10 px orange dot with a 14 px glow at f71–74.

### 4 · Logo (f75–119)
- bg same light radial as segment 12–16 s (#f8f8f8 → #d0d0d0).
- Burst at (412,318): 22 orange rays #ff7a3c 2.4 px growing r 20 → ~220 (easeOutCubic 7 frames) fading f78–82; thin orange ring r 120 → 360 (10 frames); grey ring 9 → 2 px, r 55 → 130; faint grey ring r 130 → 330 later.
- Particles: 70 seeded specks (orange #ff6a2f / #2b2b30 / #9a9aa0, dots and bars), radial `d = sp·(1 − e^(−3.2τ))·0.69`, sp 80–340 px, drift down 18 px/s, fade after 0.7 s.
- **Icon slam** (same move as the Ready pill): scale 2.0 → 0.55 easeInOutSine over 8.5 frames, then spring(−0.45, ζ 0.55, ω 11) to 1; blur (6 − g)·0.8 px.
- **Letters "ClimbX"** rise with the headline spring: y0 = 70 px, v0 = −500 px/s, ζ 0.42, ω 13, rotate 0.35°·y, stagger 1.8 frames from f77.
- Tagline f104.5–108.5: translateY 10 → 0 easeOutCubic + fade.

## What still differs
- Fly-through f48–63 (SSIM 0.83–0.86): the ref field also slides sideways slightly and has more depth layers; our card table is from one frame (f28) so later relative positions drift a few px; the ref's cards are softer.
- Zoom into the flag (f11–13): ref zoom centre moves toward the pole; ours zooms about a fixed point, so f12 shows peak instead of pole. Ref f13 has wavy dark orange bands during the flood (not built).
- Icon/logo: icon is a hand-drawn SVG approximation of the ClimbX mark; facet shapes differ.
- Particles/stars are seeded random (no one-to-one match).
