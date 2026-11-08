# SaaSSuite main video style — v1 (from Andrew's picks, Nov 8, 2026)

This is the **main** style: the default for SaaSSuite VSLs, product/feature launches, onboarding and explainer videos, ads built from motion graphics, and on-brand statics.
It does **not** replace formats that already perform: the yellow-caption short-form reels and trend formats keep their own look (see Exceptions).
Source of every decision: `quiz.md` (Andrew's answers) and the reference breakdowns in `library/`.

## Tokens
| Token | Value | Use |
|---|---|---|
| Background (light, default) | `#F6F5F2` off-white | every scene unless the scene is a "dark moment" |
| Ink | `#141418` | headlines, UI text |
| Muted | `#6B6F7B` | sublines, labels |
| Card | `#FFFFFF`, 1px `#E6E4EF` border, soft shadow `0 20px 60px rgba(20,20,40,.10)`, radius 20 | floating UI cards |
| **Accent: violet** | `#7B5CFF` | ONE word per headline, active caption word, buttons, progress, the one moving dot |
| Background (dark, alternate) | `#0B0B10` with a soft violet glow `#7B5CFF` at 12–18% | launches, premium reveals, CTA end cards |
| Display font | **Inter Tight ExtraBold** (`tools/fonts/InterTight-ExtraBold.ttf`), tight tracking (-2%) | headlines, captions |
| Body font | Inter Regular/SemiBold | sublines, UI copy |

Rules: one accent colour per frame; never a second bright colour. Headlines are short, lowercase-friendly sentence case, with the key word in violet (e.g. "one place for your **clients.**").

## Format 1 — No-speaker motion graphics (VSL, launch, onboarding, feature drop)
Reference DNA: 13 ClimbX (bold sans + one colour word over rebuilt UI), 43 MakerMap (one element morphing on light), 26 CodePilot (dark UI glow, slow camera), 19 Tessel (light prompt bar).
- **Layout:** headline left or centred, floating UI card(s) beside or below. UI is **rebuilt** as clean cards (no device frames, no raw screenshots unless zoomed/cropped).
- **Motion:** smooth ease-out (power3/expo), slow camera push (2–4% over a scene), cards slide/scale in with a soft shadow, one element **morphs** into the next inside a scene (button → card → checklist → "done ✓").
- **Transitions:** morph inside a scene; clean cut on the beat between chapters.
- **Busyness:** in between. Mostly one headline + one card at a time; one busy moment per video (cards stacking, logo wall, stat counters) for emphasis.
- **Dark moments:** use the dark alternate for the hook reveal, the product "glow" moment and the end card. Same violet, same font.
- **Sound:** cinematic ambient bed (~90 bpm, slow build, swells into chapter changes), soft whooshes on cuts, soft UI clicks on card/morph events. No hard slams. Mix −14 LUFS, true peak ≤ −1 dB.
- **Story:** problem → feature → proof (numbers, real UI) → CTA, joined with But/Therefore.

## Format 2 — Speaker + captions (Andrew on camera: VSL, YouTube clips, ads)
- **Captions: karaoke.** 2–3 words per phrase, Inter Tight ExtraBold ~90px on 1080×1920, white with a soft drop shadow, the spoken word turns **violet**, lower middle (y ≈ 65% of height). Break phrases on pauses > 0.35 s.
- **Cutaways:** floating UI cards (Format 1 style) pop over or beside the speaker on key claims; 1 every 4–6 s at default busyness.
- **Sound:** same ambient bed, ducked well under the voice; soft whoosh on cutaways.
- Demo on Andrew's footage: `/home/user/work/capdemo/make.py` style A (`outputs/style-quiz/r5-captions.mp4`).

## Format 3 — Statics and carousels (main style)
- Off-white background, Inter Tight ExtraBold headline with one violet word, floating UI cards, violet buttons/pills. Dark alternate for covers that need contrast.
- The podcast-stack carousel and real-face covers can adopt the fonts/violet, but performing formats keep their look (Exceptions).

## Dials
| Andrew says | Change, in this order |
|---|---|
| "do more" | more UI shown (extra cards, more screens) → more motion (more moves/morphs, quicker holds) → more graphics (icons, callouts, pop-ins) |
| "make it simpler" | fewer graphics → text-led (headlines/captions carry it, minimal UI) |
Default sits in the middle; each step is one notch, never jump to extremes.

## Exceptions (keep as they are)
- Short-form reels on proven formats with **yellow captions** (`#FFD23F` active word) — the yellow works; don't recolour.
- Trend-driven short form follows the trend's look.
- Retired: V3 kinetic, Bold-colour pastel family (ruled out in round 1).

## Not yet decided
- Logo/wordmark treatment and end-card lockup.
- Exact music source (licensed library vs generated); current beds are placeholders.
