# MedSpa EMR training design system (v1.0.0)

One look for every interactive walkthrough and every training video. The values
are the ones the EMR's walkthrough uses on screen, so a video and the in-app
tour read as the same product. Machine-readable copy: `design-system.json`.

## Colour
| Token | Hex | Use |
|---|---|---|
| accent | #2563eb | Spotlight ring, arrows, step badges, progress, primary button |
| accentInk | #1d4ed8 | "STEP 2 OF 5" labels, links |
| accentSoft | #e8f0fe | Pill backgrounds, soft panels |
| ink | #0f172a | Titles and body on light backgrounds |
| ink2 | #566173 | Secondary text |
| panel | #ffffff | Cards |
| background | #f3f6fb | Behind cards |
| brandSky | #73bcdd | The brand colour (logo disc); intro card gradient start |
| brandLight | #d9eef8 | Soft brand panels |
| brandDeep | #63b7dc | Logo shadow side |
| scrim | rgba(15, 23, 42, .45) | Dim around a spotlight |

## Type
Font: 'DM Sans' (file in `fonts/`). Fallback: system UI.
- Step count: 11px, 600, uppercase, letter-spacing 0.05em, accentInk. In video scale ×2.
- Title: 18px 600 (compact card 16px).
- Body: 14px, line-height 1.5, ink2.
- Video captions: 28px 600. Intro/outro titles: 56px.

## Spacing and shape
Spacing scale 4 / 8 / 12 / 16 / 24 / 40 px. Card radius 18px, spotlight 14px,
buttons 10px. Card shadow `0 24px 60px -16px rgba(15, 30, 60, .5)`.

## Highlight (the thing to click)
- Spotlight: 6px padding around the element, radius 14px,
  2px accent ring + 7px accent halo at 22%, everything else dimmed to the scrim.
- Arrow: accent, 4px stroke, 56px long, pointing at the ring from the side with more room.
- Step badge: a 28px accent circle with the step number in white, top-left of the ring.
- Motion: 320ms cubic-bezier(.16,1,.3,1) for every move. Nothing bounces.

## Captions
bottom-center, 64px above the bottom edge (desktop) / 120px (phone, clears the home bar). Max 2 lines, ~42 characters a line,
white on rgba(15, 23, 42, .82), radius 12px, padding 10/20px.
Captions are always on (burned in): many staff watch on mute between patients.

## Intro and outro cards
- Intro (3s): linear-gradient(135deg, #73bcdd 0%, #2563eb 100%); logo 96px centred above the feature name (cardTitle, white), one-line promise below (body 24px, white 85%).
- Outro (3s): #ffffff; logo 72px, "You’re all set." (cardTitle, ink), the menu path to the feature (body 24px, ink2), "Questions? Support & chat in the menu.".
- Lower third on each step: step count pill (stepCount style on accentSoft) + step title (titleCompact) on panel, radius 18, shadow card.

## Video formats (two cuts per feature)
Every feature gets two videos, uploaded separately: staff on a computer see the desktop cut, staff on a phone see the
mobile cut (and the other one if only one exists).
| Cut | Size | Aspect | Safe area (top / right / bottom / left) | Source screenshots |
|---|---|---|---|---|
| Desktop | 1920×1080 | 16:9 horizontal | 54 / 96 / 54 / 96 px | 1440x900 @2x, scaled to fit |
| Mobile | 1080×1920 | 9:16 vertical | 220 / 60 / 380 / 60 px | 390x844 @3x, centred in a phone frame |

Nothing that must be read (captions, step pills, highlights, logo) goes outside the safe area.
Desktop: captions sit in the bottom 160px, inside the side margins. Mobile: captions sit just above the bottom safe line (y ≈ 1400–1540).
- Length 30–90s, 30 fps.
- Voice: One calm, friendly voice; second person ("you"); present tense; no jargon; never name the CRM vendor — say "your CRM".
- Music: Light, no vocals, −24 LUFS under the voice; none under the outro card after the first second.
- Cursor: Visible, 1.25× size, click ripple in accent; zoom 1.4× on the target for each click step.
