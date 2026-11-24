# Med Spa EMR training (style pack)

Click-by-click training videos for the MedSpa EMR, made from a feature kit (screenshots + script + brand). Staff watch them
from a "Watch how" button, often on a phone, often on mute. Approved source: the In-Room video (Nov 24),
`example/index.html` (desktop cut). Colours, type and shapes: `design-system.md` / `tokens.json` (the EMR's own walkthrough values).

## Look
- Light page `#f3f6fb`; the app screenshot sits in a white card (radius 18, card shadow), **never covered**:
  step label above the card, captions below it. Nothing is drawn over the app except the cursor and click ripple.
- The screenshots already contain the highlight (ring, numbered badge, arrow). **Do not draw a second box.** If a step's
  screenshot has no highlight, draw one that hugs the measured target (+6–8 px), in the accent ring style.
- Step label: pill "STEP 2 OF 3" (accentSoft / accentInk, uppercase) + step title (ink, 600), top-left above the card.
- Intro card (3 s): sky→accent gradient, logo 96 px, feature name 56 px white, one-line promise. Outro (≈4 s): white, logo 72,
  "You’re all set.", the menu path, "Questions? Support & chat in the menu."
- Font: DM Sans (from the kit). Captions 40 px 600, white on rgba(15,23,42,.82), radius 12, bottom-center 64 px above the
  edge (desktop) / just above y≈1540 (phone). ≤ 2 lines, ≤ 42 characters a line.

## Motion
- One curve for everything: cubic-bezier(.16,1,.3,1). Nothing bounces.
- Each step: crossfade to the screenshot, camera zooms 1.0→1.4× toward the measured target (clamped so the shot fills the
  card), cursor travels ~1 s to the click point, presses (scale .88), accent ripple 0.6 s, holds ≥ 3 s after the click,
  zooms back out as the next step starts.
- The cursor's position is computed from the same camera every frame, so it stays on the target while the camera moves.

## Sound
One calm, friendly ElevenLabs voice (the In-Room video used "Kalala – Calm & Friendly"), one clip per line with word timings;
captions come from those word timings. Light music bed ≈ −24 LUFS under the voice, fading out under the outro. Final mix −16 LUFS.

## Process (SOP 13)
measure (`tools/explainer_measure.py`) → storyboard (`window.STORYBOARD`) → build from `example/` → `tools/explainer_qa.mjs`
must pass → look at `qa/contact.png` next to `reference/` → 10 s test → full render (both cuts).
