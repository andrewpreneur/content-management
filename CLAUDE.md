# Content engine — operating rules for every agent

This repo is the content engine for Andrew George's brands. Read this file first, then `docs/STATUS.md`.

## The goal
- 30 days (by Dec 4, 2026): the 1 → 20+ multiplier pipeline works end to end and is tested.
- 60 days (by Jan 3, 2027): engine can post **100 times a day** across all pages.
- 90 days (by Feb 2, 2027): engine can post **1,000 times a day**.
See `docs/roadmap.md` for the math.

## How Andrew wants to work
- Don't narrate. Do the work. Only bring something to Andrew when it is risky or truly needs him, in as few words as possible.
- Andrew's only job: film what's on the filming list (`todo/`), upload it to the drop folder, approve outputs. Everything else is ours.
- Andrew is not deeply technical. When he must click something, give exact steps.
- Approval gate: nothing posts live without Andrew's approval (for now). Drafts go to the review queue.

## Logging (required)
1. **Repo log:** append to `logs/YYYY-MM-DD.md` (CT dates) — what you did, what's next, who owns it.
2. **Second Brain log:** one Google Doc per day per topic in the Second Brain **Log** folder
   (Drive folder id `1DvsqMaCZpL2YYS91aVpFjjrNpB7BDEA5`), titled `Log — <Mon D, YYYY> — Content engine (Claude)`.
   The Drive connector can create docs but usually can't edit docs it didn't create. If today's doc exists and is read-only, create `… (2)`.
3. Durable facts (brand kit, voice, editing style, competitors) go into the Second Brain **Docs** folder
   (`11T57FhNS04uzq89Ws_yD55Ibmj5Y5QaD`) and mirrored here under `docs/`.

Second Brain root: https://drive.google.com/drive/folders/1ZafNUIjTnyC6_PKUaP89Y058SILFP3en
(Index doc: `18JbAxQSSnR-vBdKTK-_B7h4aZrs-U3pvLsHunwhBIjc`. Brand voice, Identity, Ideal client, Best content, Market and competitors live in Docs.)

## Files and footage
- Raw footage: Drive folder **Master Raw Software Training Footage** `1kfxSfAFp17WUJQgneBNFl7FvmPEYnWN2`.
- Drop folder for new filming and finished edits: see `docs/infrastructure.md` (to be created inside the raw footage folder).

## AI video rules (non-negotiable) — full detail in `docs/ai-video-rules.md`
Never publish a 100% AI talking-head video. Allowed: extra angles for a visual hook; filler/extensions to make a real clip flow; background/outfit/environment swaps that keep the human; and the **half-screen** format (AI Andrew ≤50% of the frame, ≥90% of the runtime, with real screen recordings/motion graphics carrying the value).

## Higgsfield
- CLI `higgsfield` (npm `@higgsfield/cli`) + skills in `.agents/skills/` (symlinked in `.claude/skills/`).
- Login needs a browser on the same machine and `*.higgsfield.ai` network access; cloud sessions are blocked today. The MCP connector is read-only (browse/balance), no generation.
- Never use `higgsfield-faceless-video` for Andrew's main pages: it conflicts with the AI video rules.

## Agents
- Hard cap: **5 new sub-agents per day** across all sessions. Record each spawn in the day's log (`Agents spawned: n/5`).
- Give each agent a narrow brief and have it write results into this repo.

## Repo map
- `content-engine/` — Cristian's content hub, imported (scripts, formats, hookpoint specs). Re-import: `tools/import_content_hub.py`.
- `docs/` — how the engine works: pages, connections, infrastructure, multiplier, AI rules, expansion, roadmap.
- `research/` — competitors, weekly AI-content research.
- `supabase/` — database schema for the engine.
- `todo/` — Andrew's filming lists.
- `logs/` — daily logs.
