# Saved edit templates (approved by Andrew, Nov 26, 2026)

These are the finished, approved edits to copy. Every new edit of the same kind matches them. They sit on top of
`docs/edit-style-lock.md`; the reference frames are in `docs/brand-video/reference/`.

## T1 "Instagram basic ad" (reels and ads, vertical talking head)
Approved: the Black Friday ad set. **APPROVED versions (Nov 27) = the "- FINAL" files** in
`_ENGINE/02-review/2026-11-26-Blackfridayad-APPROVED-proof` (the Nov 25 files in `2026-11-25-Blackfridayad` are the drafts).
Frames: `docs/brand-video/reference/template-instagram-basic-ad.jpg`.
- `reel.py` EDL: `"look": "ig"`, `"headline": "<2-6 words, the offer or the hook>"`, every segment `"layout": "full"`.
- Headline: black Barlow Condensed on a white rounded card, the whole video. **It moves to stay off the face**: top
  when the face is low, chest height when the face is high (Andrew: "the moving is perfect").
- Captions: white bold, thin black stroke, 1-3 words, lower middle. Nothing coloured anywhere.
- The set: master (strongest hook first), 3 re-edits each opening on a different real line, trial variants, 4:5 feed.
- Retakes cut (keep his last take of each line), no music when the source has none, ad copy with `[Andrew: …]` gaps.
- style_check with `--baseline` passes on every file.
- **Tight cuts (ads only)**: `python3 tools/tighten_cuts.py IN OUT` trims the silence at every cut to ~0.05-0.1 s so
  the lines almost touch (never clipping a word). Not for long form.
- **Proof collage beat** (Andrew, Nov 26-27): starts on "**just like the hundreds of agencies** I work with" (not earlier on
  "pays the bills"). ~18-20 proof screenshots, **straight on, no borders**, a **pop** on each landing (`--sfx` kit/pop.ogg), (Drive folder `1xhTAZZ1-lp19Kd4ebpg9WQUSLiupcX3M`: revenue, invoices, MRR, user charts,
  comments) pop in scattered, many sizes, overlapping, slow then faster (t = 2.6 s × (i/N)^(1/2.6)), covering nearly the
  whole frame, held to the end of the line, 0.2 s fade. Pace approved. Order: tighten_cuts → transcribe → collage.
  `python3 tools/proof_collage.py IN OUT --shots DIR --start S --end E --sfx vendor/motion-graphics/skills/sound-effects/sfx/kit/pop.ogg`.
  Use the same beat on any ad where he makes a proof claim.

## T2 "Podcast montage" (long form cold open: calls, podcasts, coaching)
Approved: GoHighLevel Live Coaching montage, Nov 25 ("GoHighLevel Live Coaching - intro.mp4").
Frames: `docs/brand-video/reference/template-podcast-montage.jpg`.
- `montage_intro.py`: hooks from across the WHOLE video (at most one from the first 5 minutes), 30-45 s, 8-10 clips,
  mixed speakers; `--plan-only` → look at each pick → `crops.json` → `--crops`: faces only, side by side, never the call
  app or a shared screen (screens are skipped automatically).
- Captions: clean white (house captions), no colour, no boxes. Plain white title card with the video name.
- Riser/whoosh/dip into the ORIGINAL video from 0:00, untouched. -16 LUFS.
