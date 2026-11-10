# Posting funnel: how every piece of content actually goes out

This is the operating manual for any agent (or person) moving content from "made" to "posted".
Read it with `docs/brand.md` (voice) and `docs/ai-video-rules.md` (AI rules) before touching the queue.

**One page for Andrew:** Content HQ, https://claude.ai/artifact/XfAzpe3aC23M7qAsyDrzsd.
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
1. **Approval gate.** Nothing is scheduled or posted unless Content HQ shows `approved` from Andrew. A "change" note goes back to the caption or edit agent, then back to `needs_approval`.
2. **Sync approvals first.** Before any scheduling run, sync them: ArtifactData `list` on the Content HQ url, collection `approvals`, out_dir `work/approvals`, then `post_queue.py sync work/approvals`.
3. **Social Planner first.** Use GHL Social Planner (HighLevel MCP) for Instagram, Facebook, LinkedIn, YouTube Shorts, TikTok and community.
   - Create posts as `status: draft` first. Andrew can see them in GHL.
   - Schedule only after the first draft of each new format has been checked by hand once.
   - Threads, X, Substack, Skool and email are manual (or Blotato later). For these, `payloads` prints copy-paste text.
4. **Accounts.** Only post to the accounts in `posting/accounts.json` whose route matches.
   - Never post to `studentsuccessshop` or `xxidesignscorp`.
   - Never post the same file on two Instagram accounts; use a Collab post instead.
   - `howtousehighlevel` is for legacy HighLevel tutorials only.
5. **Cadence caps.** Respect the per-day limits in `posting/platforms.json`, and keep 90 minutes or more between posts on the same account. Defaults: 2–3 IG/FB posts, 1–2 LinkedIn, 2 Shorts, 3–4 Threads, plus 1 story sequence a day.
6. **Captions.**
   - One promise per post, in Andrew's voice, following the But/Therefore rule.
   - The first line has to survive the "...more" cut: about 125 characters on IG, 210 on LinkedIn.
   - One ask at the end (comment keyword, follow, or link). Hashtags: 3 on IG, 0–3 on LinkedIn, none on Threads or X.
   - Run ig-human before showing anything: no em dashes, no AI slop words.
   - No invented claims. Numbers must come from Andrew or the source.
7. **AI disclosure.** Tick the platform's AI label for any asset under AI rule 3 or 4. Never post a 100% AI talking head.
8. **Stories.**
   - Story sequences post as story frames with no caption; poll and question stickers are added in the app.
   - A DM keyword in a story needs a matching GHL automation (tag `kw-<KEYWORD>`) before it goes live.
   - Stories are manual in the IG app until the API supports stickers.
9. **Media links.** GHL needs a public media URL. Use a Drive file shared "anyone with link" as `https://drive.usercontent.google.com/download?id=<ID>&export=download`. Items with no Drive id fail lint with `no_media`: upload them with `tools/drive_upload.py` first.
10. **Log.** Every run appends one line to `logs/YYYY-MM-DD.md`: how many were scheduled, posted, or bounced back.

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
