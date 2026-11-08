# 13-climbx · 12.0–16.0 s · "make it yours." editor + rating card

Reference: `/home/user/work/refs/13-climbx-launch.mp4` (the file is actually **1280×720, 30 fps**; the breakdown says 1080p/60).
All measurements below are in **reference pixels (1280×720)**. The page lays everything out in those units inside a 1280×720 `#stage` scaled `1.5` → renders at 1920×1080.
Frame numbers `fN` are local frames at 30 fps (f0 = 12.000 s).

## SSIM per round (compare.sh, 4 s @ 30 fps)
| round | change | avg SSIM |
|---|---|---|
| 1 | first build (all layout + motion from measurements) | 0.9395 |
| 2 | font → Inter Display (Inter opsz 32) 800, re-measured type sizes, rating row offsets, typing as one wrapping string, intro blur fixed (transform origin bug), pill blur/opacity | 0.9536 |
| 3 | confetti count/speed/fade, exit fade later | 0.9537 |
| 4 | exit: blur starts at 45 % of the exit, bigger x drift | **0.9538** |

Per-frame: 0.96–0.975 for f0–55, 0.94–0.95 during pill/cursor (f60–100), 0.90–0.93 during the 3D exit (f105–113). Final per-frame log: `ssim-final.txt`. Side-by-side: `make-it-yours-side.mp4`.

## Fonts
- Headline: **Inter (variable, opsz 32 = "Inter Display") weight 800**, 83 px, letter-spacing −0.037 em (`fonts/InterVariable-opsz-wght-latin.woff2`). Inter Tight Black was too wide/heavy; glyph runs now match to ±4 px.
- UI text: Inter 400/600/700 (`fonts/Inter-*.ttf`).
- HUD + kicker: **JetBrains Mono** 500/700 (dotted zero matches the timecode).

## Palette (pixel-sampled)
| token | value |
|---|---|
| bg centre | #f8f8f8, flat to r≈0.53 of farthest-corner, linear to #d0d0d0 at corners → `radial-gradient(ellipse farthest-corner at 50% 51%, #f8f8f8 53%, #d0d0d0 100%)` |
| ink | #101010 |
| orange | #ff692f (yours., caret, kicker, emoji icon) |
| editor body text | #050505 |
| dark buttons | #3c3f51, avatar #2b2e40 |
| UI grey | header #7b7a7e, rating labels #8a8a8a, title #6f6e72 |
| rating bars | fill #57b591, track #efeef3 |
| pill / scheduled | #17a04b |
| text highlight | rgba(255,105,47,.18) (= #ffe4da on white) |
| HUD | #858585 |

## Layout (rest state)
- HUD: brackets 9×9 px, 1.5 px, at 13 px from each edge; labels JetBrains Mono 500 9.6 px, tracking 2.4 px, at x=27 / right 27, cap top y≈21 and y≈691. Labels: CLIMBX · 02 / STUDIO · timecode · CLIMBX.SO. Timecode = global frame (`00:00:SS:FF`, 30 fps).
- Kicker "STUDIO": JetBrains Mono 700 13 px, tracking 5.3 px, ink x 103–173, cap y 52–60.
- Headline ink: "make it" x 106–360, k-top 80, baseline 141; "yours." x 376–602.
- Editor card: x 100–805, y 194–525 (705×331), radius 14, bg gradient 98° #f6f6f6 → #fff by 90 px; shadow `0 1px 1px rgba(0,0,0,.05), 0 6px 6px -2px rgba(0,0,0,.08), 0 22px 40px rgba(0,0,0,.08), 0 0 18px rgba(0,0,0,.035)` (contact shadow 215/255 right under the card, fading to bg over ~55 px).
- Avatar 35 px circle at (127,245). Body Inter 400 20.7 px; line 1 cap top 251, paragraph 2 at 295, line height 30 px.
- Header row (Preview / Rate post / Improve): Inter 600 14 px, icons 12 px, ink x 519–778, y 218–231.
- Divider y 461, #efefef. Footer pills 34 px tall at y 475: Save x 446–512, Posted 518–595 (1 px #f5f5f5 ring), Schedule 602–714, Post 722–785 (Inter 700 13.5 px white).
- Rating card: x 848–1180, y 194–396, radius 14. Title Inter 700 11 px tracking 1.4 px at (870,216). Rows every 30 px from y 244: label Inter 400 12.3 px at x 870; bar x 980, 132×8 px r4; % Inter 700 12.5 px right-aligned at 1157.
- Ready-to-post pill: 155×31 px r16, centre (749,190), final rotation +6°, Inter 700 15.5 px + check, glow `0 6px 14px rgba(23,160,75,.28)`.

## Timeline + techniques (how each animation is built)
| t (s) / frames | element | technique + exact numbers |
|---|---|---|
| 0–0.2 (f0–6) | editor card arrival (tail of previous shot) | scale `1 + 0.32·e^(−21.6 t)` about stage point (−71, 358) (card shrinks + slides left); horizontal motion blur `stdDeviation = 4.2·(1 − f/6.5)` px via SVG feGaussianBlur "x 0" |
| f2–10 | HUD "02 / STUDIO" | decode/scramble: char i revealed when i/n < 1.15p − 0.15, p = (f−2)/8, others cycle A–Z0–9 |
| f3.8 + 0.9·j | kicker letters | translateY 9→0 px easeOutCubic 0.12 s, opacity 0.07 s, stagger 0.03 s |
| 0.169 + 0.0453·j s | headline letters (spaces skipped) | **spring** offset y: x0 = +73.5 px (below), v0 = −628 px/s, ζ = 0.47, ω = 15.9 rad/s (fit RMS 1.7 px over 11 letters); rotate = 0.18°·y; opacity 0→1 in 0.07 s; blur = min(3.5, |v|/260) px |
| f7.7–12 | select-all highlight | two rects grow 0→287 px, easeOutCubic 4.3 frames; text deleted at f15 |
| f16–43 | typing | per-frame ink extents measured from ref (≈2.6 chars/frame, ~78 chars/s, bursty by word); one wrapping string so "scree|" wraps to "screenshot." at f41 like the ref; caret 2×21 px orange, 45 % opacity while typing |
| f48+ | caret blink | on for 8 frames, off 8 (16-frame period = 0.533 s), starts f48 |
| f4.6/6.4/7.8/10.2 | footer pills pop | scale 0→1 via spring(ζ 0.6, ω 30) over 4.5 frames, opacity 1.5 frames |
| 0.5 s grid | beat pulse (whole world, not HUD) | scale `1 + 0.0095·e^(−Δt/0.085)` about (700,470) on every 0.5 s (120 BPM) |
| 1.2595 s | rating card slide-in | **spring** x: x0 = +358 px, v0 = 0, ζ = 0.78, ω = 23.8 rad/s (fit residual <1.6 px); horizontal motion blur = 0.45·|v|/30 px |
| f39–45 | "POST RATING" | same decode scramble |
| 1.483 + 0.1333·r s | rating bars | width = final·(1 − e^(−16.9·τ)) (constant 0.57 per-frame decay); % counts with the bar and scales 0.55→1 easeOutCubic 0.14 s; label fades in 0.1 s after a 0.05 s delay |
| 1.985 s (f60) | Ready-to-post pill "stamp" | scale 2.25 → 0.67 easeInOutSine over 6.5 frames (slam), then spring from −0.33 (ζ 0.3, ω 11.5) → overshoot to ~1.24 at f75, settle by f84; rotation 6° + spring(−30°, ζ 0.5, ω 14); blur 2.6→0 px over 4.5 frames; opacity 0.55→1 in 1 frame |
| f60.5 | shock ring | r = 150·(1 − e^(−Δf/3.2)), 2.5 px rgba(120,190,150,.5), opacity 0.9→0 over 13 frames |
| f61 | confetti | 18 seeded particles (dots + 0.7×1.9 bars), colours #17a04b/#7fd3b0/#ff692f/#e5484d/#2f8f5b, radial `d = sp·(1−e^(−7τ))`, sp 45–130 px, x stretched 1.25, gravity 30–80 px/s², spin ±300°/s, fade after 0.45 s over 0.45 s |
| f79.5–87 | cursor | from (820,575) to tip (656,499) easeOutCubic 7.5 frames, velocity motion blur |
| f90–98 | click | cursor scale 0.82 f90–95; button scale 0.94 f90–94; colour #3c3f51 → #17a04b and "Schedule" → "✓ Tue 08:00" crossfade f93–95; ripples r 0→72 (10 frames) and 0→30 (6 frames), 2 px rgba(255,105,47,.45) + 5 % fill |
| 3.43 s (f103) | editor exit | ease-in-cubic over 0.38 s: translate(+220·e, −40·e), perspective 900 rotateX 60°·e, rotateY −8°·e; blur 0 until 45 % then →16 px; fade from 78 % → 0 |
| 3.72 s | rating card exit | opacity 1→0 over 0.22 s, drop 30 px ease-in, blur rising 20 px/s |

## What still differs
- Exit (f105–113, SSIM ~0.90): ref tilt reads as a camera swing (card goes slightly left/down at the end); ours is a cleaner rotateX. Biggest remaining gap.
- Beat-pulse frames (every 15th) score ~0.01 lower: the ref adds a faint zoom blur on the pulse; we only scale.
- Confetti is seeded random, so particle positions don't match one-to-one.
- Header/footer icons are approximations of the ref glyphs (eye / sparkle / wand / image / smile / calendar).
- The ref has a very faint dot grid on the background (not reproduced, invisible at 1×).
