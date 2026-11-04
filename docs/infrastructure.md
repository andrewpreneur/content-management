# Infrastructure

## The honest picture
Claude cloud sessions are good for: planning, scripting, research, small edits, database work, calling APIs.
They are **not** a good home for: storing video, heavy rendering, or anything that must run on a schedule without a person starting it.
So the engine needs three always-on pieces outside the chat:

| Piece | Recommendation | Why | Cost (approx) |
|---|---|---|---|
| Database | **Supabase** | Andrew already uses it; Lovable connects to it | Free → $25/mo |
| File storage | **Google Drive now → Cloudflare R2 at volume** | Drive already holds the raw footage folder and has an MCP. At 100+ posts/day, R2 is cheap, fast, no egress fees, and the GHL/Apify/render tools can read from public URLs | Drive: existing. R2: ~$15/TB/mo |
| Render worker | **Remotion + FFmpeg on a small cloud box** (Hetzner/Railway/Render, or GitHub Actions to start) | Does the variant multiplication (speed ±0.1x, mirror, hook/caption/font swaps, half-screen layout) in code, unattended | GitHub Actions: free tier to start. VPS: $20–60/mo |
| Scheduler | **GitHub Actions cron** to start → move to the render box | Kicks off daily scrapes, renders, reports | Free |
| Scraping | **Apify** (existing account) | Covers every platform | Usage-based |
| Posting | **GHL Social Planner API** | Already paid for; HighLevel MCP connected | Existing |
| Review UI | **Lovable app on Supabase** | Andrew's deploy tool; approve/reject drafts on phone | Existing |
| Notify Andrew | **GHL SMS** | "New filming list" / "12 drafts ready to approve" | Existing |

## Footage flow
```
Andrew films → uploads to Drive: Master Raw Software Training Footage/_ENGINE/01-inbox/YYYY-MM-DD/
  → watcher (Drive API, every 15 min) logs the file in Supabase `assets` and notifies the engine
  → transcribe (Whisper) → cut list → render variants → 02-review/
  → Andrew approves in the review app → 03-approved/ → GHL Social Planner schedules → 04-posted/
```
Drive folder ids (created Nov 4, 2026, inside Master Raw Software Training Footage):
| Folder | Id |
|---|---|
| _ENGINE | `1YW2-5GbikdJkdNHsdel58inyA-tHd3-_` |
| 01-inbox | `1B2A_2_3B6Rm060keaIrswnJl1TgtmK5j` |
| 02-review | `1Q_mZBiD75hmFAzm7bux-SCvzmXxsW326` |
| 03-approved | `1JJVr0et0w6xnm9_a-RpeavEp0nE33PcB` |
| 04-posted | `1Lhh7cpdy5FeTvIVU9D5XD04KJ4qzCkQt` |
| brand-kit | `13hgDcfCdYiujykadDgUGtf0v5_C-0BqI` |

## Blockers today
- This session's network policy blocks `*.supabase.co`, the content-hub site, and likely Apify/ElevenLabs/Higgsfield APIs. Andrew must allow them (see `connections.md`).
- No Higgsfield or ElevenLabs connection yet.
- Drive connector can create files but not edit docs it didn't create, and can't upload large video. Video upload/download at volume needs a Google service account (or R2).
