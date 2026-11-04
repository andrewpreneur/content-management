# Status — read this second (after CLAUDE.md)

_Last updated: Nov 5, 2026 early AM (CT), overnight run_

## Working
- **1 → 20 pipeline tested end to end (Nov 4 overnight)** on two real sources: SwitchYard (camera + screen, 9 min) and FunnelStore (screen, 2:39). 27 draft outputs each (54 total), all on the "One → Twenty" review page with Approve / Change / Reject saved to the page's database. Runs: `outputs/2026-11-04-switchyard/`, `outputs/2026-11-04-funnelstore/`.
- Push-button tools: `tools/transcribe.py` (faster-whisper), `tools/reel.py` (EDL → 9:16 reel: screen / split / face layouts, word captions, hook + CTA, Spanish via `--translations`), `tools/variants.py` (6 Trial Reels, screen-safe), `tools/carousel.py`, `tools/story.py`, `tools/manifest.py`, `tools/review_page.py` (+ template). Step-by-step: `docs/sops/`.
- Brand look proposed (`docs/brand-kit.md`, `tools/brand_look.py`) — Andrew to confirm colors/fonts.
- Story strategy: `docs/stories.md`. Photo library: `research/brand/photo-library.md` (12 picks; no desk/office photos yet).
- Cristian's content hub imported: 45 Andrew scripts (Batch-02: 15, Batch-03: 30), format vault, hookpoint specs → `content-engine/`
- Reel variant renderer v1 (`tools/variants.py`): 6 variants from one master (speed ±0.1x, mirror, zoom, 2 hooks × 2 fonts, 2 caption styles, new first 5s). Tested on synthetic video.
- Engine docs: pages, connections, infrastructure, multiplier, AI rules, expansion, roadmap
- Supabase schema drafted (`supabase/schema.sql`), not applied yet
- Filming list #1 ready (`todo/2026-11-04-film-list.md`)

## Blocked on Andrew
0. **ElevenLabs + Higgsfield keys are rejected** (401) when the proxy injects them: ElevenLabs needs header `xi-api-key: <key>`; Higgsfield needs `Authorization: Key <key_id>:<key_secret>`. Re-save the secrets in the environment's Network secrets with those header formats. Until then: no AI opens, no voice clone, no Spanish dub.
1. Allow network hosts + add secrets (Apify, Supabase, YouTube API) — `docs/connections.md` → "What Andrew needs to do"
2. TikTok handle; confirm which platforms @aiandrewpreneurship is on
3. Which GHL sub-account runs Social Planner; connect pages there
4. Higgsfield connected Nov 4 (Ultra plan, ~221 credits) but the connector is **read-only**: it can browse past generations, models and balance, not generate. Generating needs Higgsfield's API key (secret `HIGGSFIELD_API_KEY` + host allowed) or Andrew generates in the app from our prompts. ElevenLabs still to connect.
5. Film list #1

## Not imported yet
- Live edits in the content hub's database (site + Supabase are blocked by network policy). The seed files may be behind what's in the hub UI. Re-run `tools/import_content_hub.py` once hosts are allowed.

## Research done (Nov 4)
- `research/competitors.md` (21 creators, top angles, format priority) and `research/ai-content/2026-11-04.md` (tools, prompts, platform rules).
- Key change: speed/mirror variants don't count as original on IG → multiplier rules updated.
- HighLevel pays clippers $10/clip — niche will flood with HighLevel footage; Andrew's edge is being the face who implements.
- Option to evaluate: Blotato API as posting layer (X support, used by high-volume creators) alongside GHL Social Planner.

## Research done (Nov 4, round 2)
- `research/tools/2026-11-04-ai-content-platforms.md` — Ripping (getripping.com, Ben Zogby): Claude Code IG system for SaaS founders, $19/$99/mo; copy its analytics→hook loop, don't buy. Brody Automates product not found (FounderOS/Merydian?) — ask Andrew for link. Buy: Blotato ($29) for posting; Higgsfield API (separate USD balance, not Ultra credits).
- `research/brand/2026-11-04-brand-playbook.md` — recommended positioning "The One Feature guy"; signature series "Sell This Feature"; 5 pillars; weekly rhythm adds one real 45–60 min long-form. Biggest gap: no real long-form source in our plan.
- **Decided Nov 4:** positioning "The One Feature guy" + weekly real long-form *Sell This Feature* → `docs/brand.md`.

## Next (agents)
- Brand kit/editing style doc (fill TBD values)
- Caption auto-generation (Whisper) + half-screen template
