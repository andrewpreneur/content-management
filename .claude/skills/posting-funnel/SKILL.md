---
name: posting-funnel
description: Move Andrew's content from made → captioned → approved → scheduled → posted across Instagram, Facebook, LinkedIn, YouTube Shorts, TikTok, Threads, X, stories, Skool and email. Use for "what do we post today", scheduling, captions for the queue, syncing approvals from Content HQ, GHL Social Planner posting, or adding new content to the queue.
---
# Posting funnel

Full rules: `posting/README.md` (read it first). Andrew's single page: Content HQ https://claude.ai/artifact/XfAzpe3aC23M7qAsyDrzsd

## Roles (one agent can do all four; keep them as separate steps)
1. **Curator.** Add every new finished piece to `outputs/planner/plan.json` with these fields: `id, date, time, type, kind, title, platforms, body, thumb, drive, review, source`. Pick the date and time with the per-day caps in `posting/platforms.json`.
2. **Captioner.** Write `body` in Andrew's voice (ig-caption + ig-human skills, `docs/brand.md`).
   - Separate per-platform versions with blank-line headers such as `LinkedIn:`, `Threads:` or `X:`.
   - Run `python3 tools/post_queue.py lint --ids <ids>` until it comes back clean.
   - Fix `no_media` by uploading the file with `tools/drive_upload.py` and putting the Drive file link in `drive`.
3. **Approver bridge.**
   - Republish Content HQ with `python3 tools/post_queue.py hub > work/hub.json`. That file is the page's `queue.json`, published to the same URL.
   - Read Andrew's taps: ArtifactData list `approvals` → `work/approvals` → `post_queue.py sync work/approvals`.
   - Never mark anything approved yourself.
4. **Scheduler.**
   - Run `post_queue.py payloads --days 2`.
   - For each social body, call HighLevel MCP `execute_operation` `create-post` (describe it first; locationId `T69cI1milcirIORef4Ib`, `userId` from get-users), with `status: draft` until Andrew says schedule.
   - Then run `post_queue.py mark <id> scheduled --ref <postId>`.
   - Manual platforms (Threads, X, Skool, email, stories): post the printed text yourself, or hand it to Andrew in one message.

## Never
- Post or schedule without `approved` in `posting/state.json`.
- Post to accounts outside the route map in `posting/accounts.json`, or the same file on two IG accounts.
- Make a new Artifact for review. Content HQ is the only page.
