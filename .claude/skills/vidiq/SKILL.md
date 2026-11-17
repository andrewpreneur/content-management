---
name: vidiq
description: Use vidIQ (MCP https://mcp.vidiq.com/mcp) for what only it can do in this engine - publish Instagram TRIAL REELS (shown to non-followers first), publish/schedule to IG, TikTok, YouTube, Facebook and X from one draft, Instagram owner insights, outlier and trending research, title/thumbnail scoring, keyword research and transcripts. Use for "trial reel", "test this reel on non-followers", posting through vidIQ, or vidIQ research.
---

# vidIQ in the content engine

Server: `vidiq` in `.mcp.json` (`https://mcp.vidiq.com/mcp`, OAuth sign-in as andrew@dna-media.net, no key in git).
Tools appear as `mcp__vidIQ__vidiq_*`. Credits: most research costs 5; publishing to IG/TikTok/YT/FB is free, X costs 5-40.

## Approval gate (non-negotiable)
Nothing is published unless Andrew approved that exact item in **Your Content System** (`python3 tools/ycs_sync.py pull`
→ `posting/state.json` status `approved`). The approval's `mode` decides how it goes out:
- `mode: "trial"` → Instagram **Trial Reel** via `vidiq_instagram_publish_reel` with `trialParams.graduationStrategy`:
  `SS_PERFORMANCE` (Instagram shares it to followers automatically if it does well; default) or `MANUAL` (Andrew decides).
- anything else → normal posting lane (GHL Social Planner first, see `posting/README.md`).

## Trial Reel steps
1. `vidiq_social_account_list` (platform INSTAGRAM): pick the account the item's route maps to (`posting/accounts.json`); it must have `publishingAvailable`/`canPublish`. If not connected: `vidiq_social_account_connect` (INSTAGRAM, oauth) and ask Andrew to sign in. Never post to studentsuccessshop or xxidesignscorp.
2. Video: the item's Drive file (public link `https://drive.usercontent.google.com/download?id=<ID>&export=download`) → `vidiq_video_upload` → use its media URL. Or a YouTube link.
3. `vidiq_instagram_publish_reel` with platformAccountId, videoUrl, caption (the approved IG caption, exactly), `trialParams`, and `isAiGenerated: true` only for AI-rule 3/4 assets (docs/ai-video-rules.md).
   It returns `mcpJobId` (poll `vidiq_job_poll` until ready, then call again with mcpJobId) or `containerId` (call again until PUBLISHED). Never retry a failed call blindly; never create a replacement container.
4. `python3 tools/post_queue.py mark <item_id> posted --ref <permalink>` and log it. Trial reels count toward the IG daily cap.

## Other vidIQ-only features we use
- `vidiq_instagram_owner_insights`, `vidiq_channel_analytics`: real numbers for the weekly report (needs the accounts connected).
- `vidiq_outliers`, `vidiq_instagram_tiktok_outlier_search`, `vidiq_trending_videos`: hooks/topics that beat their channel average.
- `vidiq_score_title`, `vidiq_score_thumbnail`, `vidiq_generate_titles`: before a YouTube upload from the V+S tracker.
- `vidiq_keyword_research`, `vidiq_video_transcript`, `vidiq_ig_profile_reels`, `vidiq_tiktok_profile_videos`: research + library refresh.
- `vidiq_social_post_draft_create` → show Andrew → `vidiq_social_post_publish` only after he says yes (cross-post one draft to several platforms).
