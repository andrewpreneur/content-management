# SOP 05 — Posting (GHL Social Planner)
**Rule:** only `approved` outputs; never post live without Andrew's OK (for now).

1. Approved files in `_ENGINE/03-approved/`. Each has platform + caption in the manifest.
2. Schedule through **GHL Social Planner** (HighLevel MCP / API): one post per output per account; Trial Reels are posted from the IG app as "Trial reel" (API support not confirmed).
3. Never the same file on two accounts. Use IG Collab posts to share one asset.
4. AI disclosure: tick the platform's AI label for anything using AI rule 3 (realistic) or 4.
5. After posting: status `posted`, `ghl_post_id` saved, file moved to `04-posted/`.
6. Podcast: RSS.com has a public API (`api.rss.com/v4`, beta) that can create episodes and upload audio, **but only on RSS.com Network plans** (keys: Account → API Access). Until then upload in the RSS.com dashboard.

**Blocked today:** which GHL sub-account runs Social Planner; pages not connected yet.

## Dry run: approved reviews → GHL payloads (`tools/ghl_post.py`)
Nothing is sent. It prints the exact `create-post` requests so we can check them before anything goes live.
1. Export the review page's taps: ArtifactData `list` on the page URL, collection `reviews`, `out_dir` `work/reviews` (Claude does this).
2. Run: `python3 tools/ghl_post.py --reviews work/reviews --run outputs/2026-11-04-switchyard --run outputs/2026-11-04-funnelstore [--accounts config/ghl_accounts.json] [--media-base https://<public files>]`
3. Output: one payload **per platform** (so each keeps its own caption length: Threads 500, IG/TikTok 2,200, LinkedIn 3,000), `status: draft` by default, plus `manual_steps` (email, Substack, podcast, IG Trial Reels, language pages) and `skipped_not_approved`.
4. Placeholders to fill once known: `<ACCOUNT_ID:platform>` (Get Accounts API for the Social Planner sub-account), `<GHL_USER_ID>`, `<MEDIA_URL:…>` (needs public file hosting: Drive service account or R2).
5. Going live later = same payloads through HighLevel `create-post` with Andrew's OK, starting with `status: draft` so they appear in Social Planner for a final look.
Notes: Stories carry no caption (GHL rule). X isn't in Social Planner → payload shows the thread split for Blotato/manual. Reels need exactly one video.
