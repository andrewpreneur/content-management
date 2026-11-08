# 19 Tessel, 11.0–16.0 s: prompt bar, send, UI rearranges

Reference: `/home/user/work/refs/19-tessel-calendar.mp4`. Recreation: `index.html` (`window.render(t)`, t = 0…5). Rendered at 1920×1080, 30 fps. Compare video: `11-16-prompt-side.mp4`. Per-frame SSIM: `ssim-final.txt`. Frame numbers below are 30 fps reference frames, with f1 = 11.000 s.

## SSIM per round
| Round | Change | Avg SSIM |
|---|---|---|
| 1 | full build: P1 bar + typing, P2 click and red circle, P3 band, P4 camera-solved app | 0.9323 |
| 2 | block choreography: explicit lift / move / land frames, Standups lift too, outline flash on landing, now-line in the sidebar | 0.9328 |
| 3 | lift 58, Deep work / Focus drop changes, Gym linear glide | 0.9321 |
| 4 | Deep work / Focus fixed to the measured "hover at the top of frame, then swoop" path, clash counter retimed, Gym retimed | **0.9345** |

Per-frame: P1 typing (f1–62) 0.95–0.97. Camera whip and click (f63–89) 0.95–0.997. Band (f91–95) 0.89–0.93. P4 rearrange (f96–150) 0.87–0.93.

## Phases
| Frames | What happens |
|---|---|
| f1–62 | typing in the prompt bar over a blurred clash calendar, with a slow push-in |
| f60–74 | whip zoom onto the send button |
| f70–78 | cursor arrives and presses |
| f79–90 | red circle expands until it fills the frame |
| f91–101 | the red plane collapses into a tilted band, then into the 3D "now" line of the app |
| f101–150 | tilted app; blocks lift, fly to new slots and land; black focus blocks drop in |

## Method
- **Bar camera:** for each frame I found the largest white (L ≥ 250) connected component, which is the bar. Scale = width/1590 while both ends are visible, then height/140. Pivot is the bar centre. Table `BARCAM` holds 89 frames.
- **Background parallax:** I registered every frame against f1 with a scale+shift fit (Nelder-Mead on a downsampled, blurred image, with the bar masked out). Table `BGCAM`: k 1.000 → 1.079 (f58) → 1.216 (f80), dx 0 → −68 → −104, dy 0 → −14 → −36.
- **Typing:** I transcribed the visible character count for every frame from crops (`NCH`).
- **3D app — camera solve:**
  1. Fit a homography by least squares (rms 0.48 px) to 29 hand-picked points that sit on a known grid: hour labels, day headers, mini-calendar digits.
  2. Unwarped f101 into flat space and measured the whole layout there. 100 flat units = 1 hour, and a day column is 297.16 units.
  3. Used the flat image as a SIFT template and matched it to every frame f92–150 with RANSAC.
  4. Smoothed the 4 projected corners with a Gaussian-weighted local quadratic (σ = 4 frames) to remove the outliers at f111 and f135.
  5. Rebuilt one homography per frame (`HS`) and applied it as CSS `matrix3d(h11,h21,0,h31, h12,h22,0,h32, 0,0,1,0, h13',h23',0,h33')`, with the translation folded in.

## Measured values
**Prompt bar (bar space = f58 screen):**
- Pill x 165–1754, y 520–659 (1590×140, radius 70), white.
- Shadow, measured as a luminance profile: a dark contact band right under the edge (L 230 → 158), then a soft fall-off back to 208 over about 120 px. Modelled as 0 0 0 1.5px rgba(0,0,0,.05), 0 0 9px .10, 0 3px 5px .22, 0 34px 70px .22.
- Logo 45×44 at (215, 568): black 19×43 bar, black 19×19 square, red Ø19 dot.
- Send button Ø95 at centre (1680, 590), #dc143a, white up-arrow (stroke 4.2), glow 0 10px 26px rgba(220,20,58,.32).

**Prompt text:**
- Inter 400 38.6 px, word-spacing −1.5 px. Baseline y = 603.5 (cap top 577, x-height top 583).
- Keyword chips: Inter 600 36.2 px. Chip box 54 px tall (y 563–616), radius 12, #eeeeee, padding 11/11. The period tucks into the chip (margin-right −9).
- Measured word ink x-ranges (ref vs ours) match within ±4 px.
- Placeholder "Tell Tessel what matters..." #a2a2a6.
- Caret: 3×43 px #0a0a0a, 2 px after the last glyph, no blink.

**Typing cadence:**
- About 1 character per frame (30 cps), with doubled characters at spaces (f11, f14, f30, f53, f57) and holds when chips form (f20–22, f36–38, f59, f61–62).
- Characters per frame: f2 1, f3 2, f4 3, f5 4, f6 5, f7 6, f8 7, f9 8, f10 9, f11 11, f13 12, f14 14, … f60 59, f61 60 (full table in `NCH`).

**Character colour:**
- Every new character is born red #dc143a and fades to #0a0a0a over 5 frames (easeOutCubic).
- Keyword characters ("mornings", "Gym Tue + Thu", "Friday") stay red until their closing "." is typed.

**Chip pop-in (on the closing "."):**
- Background alpha 0 → 1 and padding 0 → 11 px over 2 frames (easeOutCubic).
- This shoves the keyword about 11 px to the right.
- Keyword colour goes from (170,20,45) to (20,20,20) over 3 frames.

**Camera, P1 (bar scale / centre):**
- f1 0.860 at (983.5, 638).
- Ease-out to 0.933 at (959, 589.5) by f13: the bar settles into place.
- Slow linear-ish push to 1.000 by f54.
- Whip: f60 1.001 → f64 1.035 → f66 1.129 → f67 1.271 → f68 1.429 → f70 1.514 → f73 1.543, with the centre X going 959 → −6.6. It peaks at ≈ 290 px/frame (f66–67).
- Horizontal motion blur via SVG σx = 0.45·|dX/frame| (cap 60).

**Background (P1):**
- A clash calendar in f1 screen space, blurred 7 px.
- Colours: bg #e9e9ea, blocks #d6d7db and #d2d3d7, clash blocks with a 5 px #ecbfc9 ring, white block #ececec.
- 5 column lines at x 110, 480, 850, 1220, 1590.

**Cursor:**
- macOS arrow, scale 1.42 (about 55 px tall).
- Path: tip (1420,730)@f66 → (1290,668)@68 → (1200,633)@70 → (1142,615)@72 → (1122,608)@74 → (1118,606)@76. That is an ease-out of about 0.33 s, with blur while it moves.

**Send click:**
- f76 → f77 the button presses to 0.82 (Ø146 → 120 on screen).
- The icon fades at f77.5–78.5.
- At f79 the circle takes over.

**Red circle:**
- Diameter d(f) = 146 + 17·1.75^(f−81) px, centred at (1105.5, 590). Measured: f79 152, f80 158, f81 163, f82 175, f83 199, f84 241, f85 313, f86 442, f87 653, f88 1031, f90 full.
- That is a constant ×1.75 per frame: exponential growth.
- Edge blur 0.018·(d−150), pink glow while d < 400.

**Band to now-line (flat space):**
- Top edge = −31 − 700·e^(−Δt/0.048), bottom edge = −31 + 545·e^(−Δt/0.048), with Δt from 14.000 s.
- Measured half-heights per frame: bottom 545, 299, 157, 83, 41, 17, 5, 1. That is ×0.52 per frame.
- The line settles at 2.6 units thick at y = −31.
- Ends retract f98 → f101 (easeOutCubic) to x −330 … 340.
- The sidebar part (−330 → −37) retracts f101 → f110.
- Pill and dot fade in over f98–100.

**App (flat units; homography maps them to screen):**
- Window x −387, y −220, radius 22. Sidebar #fafafa to x = −51. Main #fff. Outside #e5e6eb.
- Block #f0f1f4, radius 9, title Inter 600 16, time Inter 400 15 #9a9a9f.
- Hatched "personal" block: 135° stripes, #fff 9 / #efeff1 4.
- Black focus block #0b0b0b.
- Mini-calendar: origin (−339.28, 31.05), pitch 40.16, header row at y −6.37.
- Hour labels centred at x = 0. Day columns x = 35 + 297.16·k.
- Header "September 2026" at (−20, −188), Inter Display Bold 26.
- Clash pill: #fde9ed on #dc143a. The count steps 12 → 11 → 9 → 7 → 5 → 3 → 1 at f112/120/128/134/140/148.

**Rearrange choreography:**
- **Lift:** every block, Standups included, lifts f102–110 with a stagger of about 1 frame. Lift = translate −58 flat units, scale 1.04, blur 0.5 (out of focus, closer to camera), shadow 0 0.9·lift 30px rgba(0,0,0,.15). Ease: easeOutCubic over 6 frames.
- **Fly (FLIP-style):** each block interpolates left/top/width/height from its old slot rect to its new one (ioCubic). Durations are 9–14 frames, staggered by column: Mon f115–118, Tue f118–120, Wed f118–125. Motion blur = 0.08·speed (cap 9).
- **Land:** easeInOutQuad over 6 frames at Mon f122–126, Tue f132–135, Wed f140–143, Thu f144–146. A dark 1.5 px outline flash peaks 4 frames after landing at α 0.75 and fades over about 10 frames.
- **Black focus blocks:**
  - Q4 deck drops in from 320 units up, scale 1.45, blur 14 → lifted at f122–130, lands f142.
  - Deep work and Tue focus enter from above the frame (f136 / f140), hover at scale 1.45 near the top edge while drifting down 50 units, then swoop down in 3.5 frames (ioCubic, with motion blur): Deep work lands f148, Tue focus about f152 (still in flight at f150, as in the reference).
- **Gym** glides lifted from x 450 to 610 over f145–157.

## What still differs
- **Lift is not true 3D.** In the reference, lifted blocks move by different amounts at different depths. Upper rows shift about 75 units, lower rows less, because the lift is a real translateZ under a perspective camera. My homography-only container shifts every block the same amount in flat space. I could not decompose the solved homography into a pinhole camera: the orthogonality constraint gave negative f², which suggests a cropped or shifted principal point. This is the main remaining error in P4 (SSIM about 0.88).
- **Blocks off-screen at f101.** Their start positions (the Thu column, the late Wed blocks) are estimates. Where a block goes after leaving view (Fri column) is also invented.
- **P1 background.** It is a stylised blurred calendar: rectangles plus text bars. The reference is the real UI blurred about 7 px, so the fine blurred text differs (SSIM 0.95–0.97).
- **The band.** It is a perfectly horizontal flat stripe. The reference band has a slight extra slope (about 0.15 at f92) and a stronger directional blur.
- **App text metrics.** About ±3 % per label. "Week 38", the time labels and the mini-calendar digits are approximate weights.
- **Cursor glyph.** Hand-drawn, so it is not the exact OS cursor.
