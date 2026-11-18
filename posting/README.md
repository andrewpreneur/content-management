# Posting funnel: how every piece of content actually goes out

This is the operating manual for any agent (or person) moving content from "made" to "posted".
Read it with `docs/brand.md` (voice) and `docs/ai-video-rules.md` (AI rules) before touching the queue.

**One app for Andrew:** **Your Content System** (Lovable app, repo `andrewpreneur/content-hq`, data in Supabase). Approvals are made there.
Sync taps into this repo first: `python3 tools/ycs_sync.py pull` (writes `posting/state.json` + `tracker/marks.json`); push fresh data back with `python3 tools/ycs_sync.py all`.
(The older Content HQ artifact https://claude.ai/artifact/XfAzpe3aC23M7qAsyDrzsd stays as a backup view.)
It lists every piece of content, its caption, and its platforms, with Approve / Change / Skip buttons.
Do not make other review pages. Add new work to the queue and republish Content HQ.

## The funnel (each piece moves left to right)

| Stage | Meaning | Who moves it | How |
|---|---|---|---|
| `made` | File exists (rendered, written) but not checked | maker agent | adds the item to `outputs/planner/plan.json` |
| `captioned` | Caption written for every target platform and passes lint | caption agent | `python3 tools/post_queue.py lint`, using the ig-caption + ig-human skills |
| `needs_approval` | In Content HQ waiting for Andrew | caption agent | republish Content HQ |
| `approved` / `change` / `skip` | Andrew tapped a button | Andrew | Content HQ writes to its `approvals` collection |
| `scheduled` | Draft or scheduled post exists in GHL Social Planner | scheduler agent | `post_queue.py payloads` → HighLevel MCP `create-post` |
| `posted` | Live; the post id is saved | scheduler agent | `post_queue.py mark <id> posted --ref <ghl id>` |
| `measured` | 7-day numbers pulled | reporter agent | weekly, into `research/` and the next plan |

**Hard rules**
1. **Approval gate → smart calendar (Andrew, Nov 17).** In Your Content System, Andrew watches the post, checks the caption and taps **Approve for scheduling** (or "As trial reel"). The app's scheduler (Convex `scheduler.ts`) puts it on the content calendar: variety first (never the same moment within 7 days, kinds mixed, max 2 of a kind a day), per-platform daily caps, trial vs regular reels, today first if today is empty, AI ordering when an AI key is connected. The poster (`poster.ts`, every 5 min, only when Settings → Posting is On) sends each slot via vidIQ / GoHighLevel / browser agent, or marks it "by hand". The weekly scrape confirms each post is live (two-way check). Nothing posts without that tap.
2. **Sync approvals first.** Before any scheduling run: `python3 tools/ycs_sync.py pull` (Your Content System → `posting/state.json`).
3. **Trial Reels (vidIQ).** An item Andrew approved with **Approve as trial reel** (`mode: "trial"` in `posting/state.json`) goes out as an Instagram Trial Reel through vidIQ, not Social Planner. Steps: skill `vidiq`.
4. **Social Planner first.** Use GHL Social Planner (HighLevel MCP) for Instagram, Facebook, LinkedIn, YouTube Shorts, TikTok and community.
   - Routing per platform (vidIQ account, GHL account or by hand) is set on Connectors → Auto-post. vidIQ is preferred where the account is connected there.
   - Agents no longer create GHL drafts by hand for approved items: the auto-poster does it. Agents fix media links and captions.
   - Threads, X, Substack, Skool and email are manual (or Blotato later). For these, `payloads` prints copy-paste text.
5. **Accounts.** Only post to the accounts in `posting/accounts.json` whose route matches.
   - Never post to `studentsuccessshop` or `xxidesignscorp`.
   - Never post the same file on two Instagram accounts; use a Collab post instead.
   - `howtousehighlevel` is for legacy HighLevel tutorials only.
6. **Cadence caps.** Respect the per-day limits in `posting/platforms.json`, and keep 90 minutes or more between posts on the same account. Defaults: 2–3 IG/FB posts, 1–2 LinkedIn, 2 Shorts, 3–4 Threads, plus 1 story sequence a day.
7. **Captions.**
   - One promise per post, in Andrew's voice, following the But/Therefore rule.
   - The first line has to survive the "...more" cut: about 125 characters on IG, 210 on LinkedIn.
   - One ask at the end (comment keyword, follow, or link). Hashtags: 3 on IG, 0–3 on LinkedIn, none on Threads or X.
   - Run ig-human before showing anything: no em dashes, no AI slop words.
   - No invented claims. Numbers must come from Andrew or the source.
8. **AI disclosure.** Tick the platform's AI label for any asset under AI rule 3 or 4. Never post a 100% AI talking head.
9. **Stories.**
   - Story sequences post as story frames with no caption; poll and question stickers are added in the app.
   - A DM keyword in a story needs a matching GHL automation (tag `kw-<KEYWORD>`) before it goes live.
   - Stories are manual in the IG app until the API supports stickers.
10. **Media links.** GHL needs a public media URL. Use a Drive file shared "anyone with link" as `https://drive.usercontent.google.com/download?id=<ID>&export=download`. Items with no Drive id fail lint with `no_media`: upload them with `tools/drive_upload.py` first.
11. **Log.** Every run appends one line to `logs/YYYY-MM-DD.md`: how many were scheduled, posted, or bounced back.

## Daily loop (any agent can run it)
```
python3 tools/post_queue.py status                 # counts per stage
python3 tools/post_queue.py sync work/approvals    # after exporting Content HQ approvals
python3 tools/post_queue.py lint                   # caption + media problems
python3 tools/post_queue.py next --days 2          # what should go out next (approved only)
python3 tools/post_queue.py payloads --days 2 > work/payloads.json   # GHL create-post bodies (dry run)
#   → HighLevel MCP: execute_operation create-post with each body (status draft), save the returned id
python3 tools/post_queue.py mark <item_id> scheduled --ref <ghl_post_id>
python3 tools/post_queue.py hub > work/hub.json    # data file for republishing Content HQ
```

## Where things live
- Queue: `outputs/planner/plan.json`, one item per post: date, time, kind, platforms, body/caption, files/drive/thumb.
  - State overlay (approvals, scheduled ids, posted ids): `posting/state.json`. Never hand-edit plan.json statuses.
- Accounts: `posting/accounts.json`. Platform rules: `posting/platforms.json`.
- Agent skill: `.claude/skills/posting-funnel/SKILL.md`.
- Older SOPs (kept): `docs/sops/04-review-and-approve.md`, `05-posting.md`, `03-stories.md`.

## Blocked / needs Andrew
- Confirm the routing in `accounts.json`: is personal content going to `realandrewgeorge` + "Andrew G." FB? Main IG `@andrewpreneurship` is **not connected** to Social Planner.
- Reconnect in GHL → Marketing → Social Planner → Settings: both TikToks (expired), and YouTube `@ghlwithandrew` (token expires Nov 10).
- Threads and X are not in Social Planner (manual, or connect Blotato).
