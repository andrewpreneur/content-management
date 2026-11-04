# Status — read this second (after CLAUDE.md)

_Last updated: Nov 4, 2026 (CT)_

## Working
- Cristian's content hub imported: 45 Andrew scripts (Batch-02: 15, Batch-03: 30), format vault, hookpoint specs → `content-engine/`
- Reel variant renderer v1 (`tools/variants.py`): 6 variants from one master (speed ±0.1x, mirror, zoom, 2 hooks × 2 fonts, 2 caption styles, new first 5s). Tested on synthetic video.
- Engine docs: pages, connections, infrastructure, multiplier, AI rules, expansion, roadmap
- Supabase schema drafted (`supabase/schema.sql`), not applied yet
- Filming list #1 ready (`todo/2026-11-04-film-list.md`)

## Blocked on Andrew
1. Allow network hosts + add secrets (Apify, Supabase, YouTube API) — `docs/connections.md` → "What Andrew needs to do"
2. TikTok handle; confirm which platforms @aiandrewpreneurship is on
3. Which GHL sub-account runs Social Planner; connect pages there
4. Connect Higgsfield + ElevenLabs to Claude
5. Film list #1

## Not imported yet
- Live edits in the content hub's database (site + Supabase are blocked by network policy). The seed files may be behind what's in the hub UI. Re-run `tools/import_content_hub.py` once hosts are allowed.

## Next (agents)
- Competitor + AI-content research (running) → `research/`
- Brand kit/editing style doc (fill TBD values)
- Caption auto-generation (Whisper) + half-screen template
