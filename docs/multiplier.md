# The multiplier — 1 filming → 20+ posts

Every filming session is a **source**. Every source runs through this pipeline. Each output is a row in `outputs` (see `supabase/schema.sql`) with a status: draft → review → approved → scheduled → posted.

## Standard pipeline for one 60–90s vertical talking clip

| # | Output | How | Platforms | Count |
|---|---|---|---|---|
| 1 | Master reel | Edit to brand kit: hook text, captions, b-roll/screen rec, AI hook angles (rule 1) | IG, FB, TikTok, YT Shorts, Threads (video) | 1 |
| 2 | Reel variants | Re-render master with one change each: speed +0.1x · speed −0.1x · mirrored · new hook text · new hook font · new caption style · **new first 5s** (alternate verbal hook or AI-angle open) | Spread across pages/days, never same page same day | 6 |
| 3 | Audio | Extract audio → clean → podcast-ready | Podcast | 1 |
| 4 | Extended podcast clip | Transcript → expand to 4–8 min with ElevenLabs Andrew voice (clearly the same ideas, deeper) | Podcast, YouTube (audiogram) | 1 |
| 5 | Long-form explainer | Unique angle on the topic: half-screen AI Andrew + real screen recordings + motion graphics (rule 4) | YouTube long | 1 |
| 6 | LinkedIn posts | Novel-style text, 3 different angles, each with an image from the library | LinkedIn | 3 |
| 7 | Threads posts | 3 angles, short form | Threads (+ X when live) | 3 |
| 8 | Carousel | 6–10 slides from the script's points | IG, LinkedIn (PDF), FB | 1 |
| 9 | Long email | Story + lesson + CTA | GHL email list | 1 |
| 10 | Substack / community post | Email rewritten as an essay | Substack, SaaSSuite community | 2 |
| 11 | Translations | Dub reel + variants via ElevenLabs dubbing, translate captions | Language pages (`expansion.md`) | 1–7 per language |
| | **Total (English only)** | | | **20** |
| | **With 3 languages × master + 2 variants** | | | **29+** |

## Variant rules (avoid duplicate-content penalties)
- Never post the same file twice on the same account. Each variant must change ≥2 things (e.g. hook text + speed, or mirror + caption style + first 5s).
- Space variants on the same page ≥5 days apart; spread across pages first.
- Track which change won (`outputs.variant_changes` + metrics) so we learn which levers matter.

## Getting to 100/day (60-day target)
100 posts/day ≈ 5 sources/day × 20 outputs. Andrew films ~25 clips in one weekly 2-hour session → 5/day. Remaining volume from language pages and the AI page.

## Getting to 1,000/day (90-day target)
Requires: ~12 language/niche pages × 7 platforms ≈ 85 accounts, ~12 posts per account per day (stories, Threads, X, LinkedIn text included), fully automated render + schedule, human review by sampling instead of every post. See `roadmap.md`.
