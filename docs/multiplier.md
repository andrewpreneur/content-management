# The multiplier — 1 filming → 20+ posts

Every filming session is a **source**. Every source runs through this pipeline. Each output is a row in `outputs` (see `supabase/schema.sql`) with a status: draft → review → approved → scheduled → posted.

## Standard pipeline for one 60–90s vertical talking clip

| # | Output | How | Platforms | Count |
|---|---|---|---|---|
| 1 | Master reel | Edit to brand kit: hook text, captions, b-roll/screen rec, AI hook angles (rule 1) | IG, FB, TikTok, YT Shorts, Threads (video) | 1 |
| 2a | Trial Reel variants | Mechanical tweaks via `tools/variants.py`: speed ±0.1x, flip, hook text/font, caption style. **IG Trial Reels only** (non-followers) to test which hook text/look wins | IG Trial Reels | 6 |
| 2b | Re-edits | **New opening hook** (first 3–5s): alt spoken hook Andrew filmed, or a Higgsfield-generated open (new angle, environment, motion) leading into the real clip. This is what makes it a new post | Main feeds, one per platform/account | 3+ |
| 3 | Audio | Extract audio → clean → podcast-ready | Podcast | 1 |
| 4 | Extended podcast clip | Transcript → expand to 4–8 min with ElevenLabs Andrew voice (clearly the same ideas, deeper) | Podcast, YouTube (audiogram) | 1 |
| 5 | Long-form explainer | Unique angle on the topic: half-screen AI Andrew + real screen recordings + motion graphics (rule 4) | YouTube long | 1 |
| 6 | LinkedIn posts | Novel-style text, 3 different angles, each with an image from the library | LinkedIn | 3 |
| 7 | Threads posts | 3 angles, short form | Threads (+ X when live) | 3 |
| 8 | Carousel | 6–10 slides from the script's points | IG, LinkedIn (PDF), FB | 1 |
| 9 | Long email | Story + lesson + CTA | GHL email list | 1 |
| 10 | Substack / community post | Email rewritten as an essay | Substack, SaaSSuite community | 2 |
| 11 | Translations | Dub reel + variants via ElevenLabs dubbing, translate captions | Language pages (`expansion.md`) | 1–7 per language |
| | **Total (English only)** | | | **23** (incl. 6 trial reels) |
| | **With 3 languages × master + 2 variants** | | | **29+** |

## Variant rules (avoid unoriginal-content penalties) — updated Nov 4 after research
Instagram (since Apr 30, 2026) cuts recommendations for accounts that mostly post unoriginal content, and says **speed changes, watermarks and credited reposts do not make a post original**. YouTube's "inauthentic content" rule hits mass-produced, near-identical videos channel-wide. So:
- **Decided with Andrew (Nov 4):** speed/flip/font/caption swaps = **Trial Reels only**. A main-feed variant = a **different opening hook** (alt spoken hook or Higgsfield-made open). Every filming list asks for 2–3 spoken hooks per clip.
- **Never** upload identical or near-identical files to two of Andrew's accounts. Use IG **Collab posts** when one asset should hit two accounts.
- Clean masters only (no TikTok/CapCut watermarks).
- Use IG **Trial Reels** (shown to non-followers first) to test hook variants without hurting the main feed.
- Rotate formats so YouTube Shorts don't look like a template farm.
- Disclose realistic AI (YouTube toggle, TikTok label, Meta AI info).
- Track which change won (`outputs.variant_changes` + metrics) so we learn which levers matter.
Full source list: `research/ai-content/2026-11-04.md` §4.

## Getting to 100/day (60-day target)
100 posts/day ≈ 5 sources/day × 20 outputs. Andrew films ~25 clips in one weekly 2-hour session → 5/day. Remaining volume from language pages and the AI page.

## Getting to 1,000/day (90-day target)
Requires: ~12 language/niche pages × 7 platforms ≈ 85 accounts, ~12 posts per account per day (stories, Threads, X, LinkedIn text included), fully automated render + schedule, human review by sampling instead of every post. See `roadmap.md`.
