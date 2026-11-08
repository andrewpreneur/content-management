# Reference video breakdown — one JSON per video in docs/brand-video/library/<NN-slug>.json

Brand context (from Second Brain): SaaSSuite = white-label client portal on top of HighLevel for agencies and SaaS founders (onboard, educate, support). Andrew George = "The One Feature guy". Voice: plain, direct, founder energy, simplifier, visual teacher ("show the screen"). Audience: B2B agency owners. No hype, no fluff. Brand colours are still TBD (current placeholder: navy #0B0F1A, yellow #FFD23F, blue #2E7DFF).

```json
{
  "id": "01-kinetic-showreel",
  "title": "Kinetic Motion Design Showreel",
  "duration_s": 15.1, "aspect": "16:9", "fps": 60,
  "summary": "2-3 sentences: what it is, how it feels.",
  "category": "product-launch | ui-explainer | speaker-captions | kinetic-type | showreel | 3d-product | illustrated | character | ugc | other",
  "use_cases": ["no-speaker product/launch", "speaker + captions", "explainer/tutorial", "static (carousels/images)"],
  "saassuite_fit": 1-5, "fit_reason": "one line",
  "palette": {"background": "#hex", "text": "#hex", "accents": ["#hex"], "mood": "dark premium / light airy / high-contrast / pastel ..."},
  "typography": {"display": "font look (e.g. grotesk heavy, serif italic, mono)", "case": "sentence/upper", "size_behaviour": "huge centred / small caption / mixed", "notes": ""},
  "text_animation": ["e.g. word-by-word slide up with blur", "mask reveal", "scale punch", "typewriter", "per-letter stagger"],
  "captions": "none | word-by-word | phrase | karaoke highlight — position, box/no box, highlight colour",
  "motion": ["camera push-in", "3D device rotate", "spring pop", "morphing shape", "parallax", "speed ramp"],
  "transitions": ["hard cut on beat", "whip pan", "mask wipe", "zoom through", "match cut"],
  "graphic_elements": ["UI cards", "cursor clicks", "icons", "charts", "3D devices", "gradients/glow", "grain", "shapes"],
  "ui_treatment": "how product UI is shown (floating cards, device mockup, zoomed crop, rebuilt UI, none)",
  "pacing": {"cuts_per_10s": 0, "feel": "calm / medium / frantic", "hold_time_s": "typical"},
  "sound": {"music": "genre/tempo or none", "sfx": "whooshes/clicks/none", "voiceover": "yes/no + style", "sync": "cuts on beat?"},
  "signature_moves": ["the 2-4 things that make this video recognisable"],
  "best_segments": [{"start": 3.0, "end": 8.0, "what": "what this 5 s shows", "tests": ["colors","text","motion","graphics","captions","sound","pacing"]}],
  "recreate": {"difficulty": "easy/medium/hard", "how": "HTML+GSAP / Remotion / ffmpeg / needs 3D renders / needs AI video; key steps", "prompt": "a short prompt that would reproduce the look"}
}
```
Give 2-4 best_segments per video for fit >= 3 (each 4-6 s, a self-contained moment that shows one style idea well), 1 for fit <= 2.
