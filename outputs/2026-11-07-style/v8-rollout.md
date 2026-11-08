# V8 rollout (style worker, Nov 7)

Every planner clip rendered in V8. Reels: branch `render-drop/style` (`<clip>/<clip>-v8.mp4`). Done 39/40.

The table below is the render tracker (due date, then clip id). Post order lives in `outputs/planner/plan.json` (`format: v3` is the V8 slot; V3 kinetic is retired). Nothing here is approved or scheduled.

## Calendar reorder — Nov 8 (planning only)

Andrew, Nov 7, 11:41 PM America/Chicago: "I already told Claude to change [V8 editing] no worries. What I want to do is post one or two reels starting with me first like my face to introduce the audience to this format, then we can do more focused on speaker 2. Can we rearrange the calendar to do that more" and "Claude will know how."

Editing stays with the main session. This reorder does not re-render, change segments, captions, or audio, and does not publish.

### First V8 slots (America/Chicago)

| | Before | After |
|---|---|---|
| 1 | 2026-11-09 08:30 `pod2-01` Blake Coker (Task Engine) | 2026-11-09 08:30 `pod2-08` Andrew |
| 2 | 2026-11-09 10:45 `pod3-04` McKinley | 2026-11-09 10:45 `pod3-04` McKinley (unchanged) |
| 3 | 2026-11-09 12:30 `pod1-06` Andy + Andrew | 2026-11-09 12:30 `pod1-06` Andy + Andrew (unchanged) |
| 4 | 2026-11-09 15:00 `pod2-08` Andrew | 2026-11-09 15:00 `pod2-01` Blake Coker (Task Engine) |

One reel leads, not two. `pod2-08` was already the only solo-Andrew V8 post on Nov 9, so moving it from 15:00 to 08:30 keeps every other slot, the due date (2026-11-08), and the 7-day gap to its other formats. Status stays `rendered`.

### Why these two clips

`pod2-08` is Andrew George on camera for the whole reel.

- `outputs/clip-bank/pod2.json`: `speaker` is exactly `Andrew`. The episode guest is a different person, `guest_name` Blake Coker.
- `outputs/clip-bank/manifest_spec.json` (`pod2_08`): "Speaker: Andrew."
- `tools/speakers_guard.py`: on a two-person episode the host (Andrew) sits leftmost. A label that is exactly `Andrew` (no `+`, no `→`) is the solo host, so the framed face is that host. V8 opens on the first speaker segment.
- Not on the Nov 5 wrong-face list (`pod1-01`, `pod1-04`, `pod1-14`, `pod2-01`, `pod2-02`, `pod2-03`, `pod2-09`). `pod2-01` is Blake, and it was on that list, so it does not lead.

`Andy`, `Andy (SoloLink)`, and `Andy Griffith` are the Pod1 guest, not Andrew. `Andrew + …` does not say who is framed first. `Andrew → …` starts with Andrew's question and then the guest; the guard treats the guest as the dominant face, and no saved `speakers.json` proves the opening frame. Those were not moved.

### Second Andrew reel — pending for main Claude

A second verified solo-Andrew V8 clip exists, but none can take 2026-11-09 10:45 without posting that same clip twice inside Nov 9–15 (Andrew's once-a-week rule):

| Clip | Evidence the face is Andrew | Other post already inside Nov 9–15 |
|---|---|---|
| `pod1-10` | speaker exactly `Andrew`; V8 test reel, frame strips checked; not on the Nov 5 wrong-face list | v2 on 2026-11-14 |
| `pod1-14` | speaker exactly `Andrew`; Nov 5 log: redone with the guard and QA'd, right person on screen | v2 on 2026-11-08 (the day before) |
| `pod1-02`, `pod1-09`, `pod2-06` | speaker exactly `Andrew` | Nov 11, Nov 11, and Nov 10 |

Main Claude: leave slot 2 as `pod3-04` unless Andrew accepts a same-week double. Do not invent a clip id. Do not regenerate the planner over this swap.

### Holds kept

- `pod3-01` (V8 item `clip__pod3-01__w3`) stays 2026-11-21 08:30. HOLD: the shared speaker map frames a listener while Ohaji speaks. Notes on that plan item. Not approved.
- `pod3-12` stays the failed render (stitched source missing). Not promoted.
- No item was set to `approved`. Review page was not edited: https://claude.ai/artifact/4v56ihPm4EtTLbjjFdL4Gj
- Planner page was not republished. Main Claude sees this only after this branch is merged; until then the live planner still has `pod2-01` at 08:30.

## Render tracker

| Due (V3 slot) | Clip | Status |
|---|---|---|
| 2026-11-08 | pod1-06 | done |
| 2026-11-08 | pod1-11 | done |
| 2026-11-08 | pod2-01 | done — posts 2026-11-09 15:00 (was 08:30) |
| 2026-11-08 | pod2-08 | done — posts first, 2026-11-09 08:30 (was 15:00) |
| 2026-11-08 | pod3-04 | done |
| 2026-11-08 | pod3-15 | done |
| 2026-11-14 | pod1-01 | done |
| 2026-11-14 | pod1-08 | done |
| 2026-11-14 | pod1-14 | done |
| 2026-11-14 | pod2-03 | done |
| 2026-11-14 | pod3-06 | done |
| 2026-11-14 | pod3-11 | done |
| 2026-11-20 | pod1-03 | done |
| 2026-11-20 | pod1-10 | done |
| 2026-11-20 | pod2-05 | done |
| 2026-11-20 | pod3-01 | done — HOLD: listener framed while Ohaji speaks; slot not moved |
| 2026-11-20 | pod3-08 | done |
| 2026-11-20 | pod3-14 | done |
| 2026-12-03 | pod1-05 | done |
| 2026-12-03 | pod1-13 | done |
| 2026-12-03 | pod2-07 | done |
| 2026-12-03 | pod3-03 | done |
| 2026-12-03 | pod3-10 | done |
| 2026-12-09 | pod1-07 | done |
| 2026-12-09 | pod2-02 | done |
| 2026-12-09 | pod2-09 | done |
| 2026-12-09 | pod3-05 | done |
| 2026-12-09 | pod3-13 | done |
| 2026-12-15 | pod1-02 | done |
| 2026-12-15 | pod1-09 | done |
| 2026-12-15 | pod1-12 | done |
| 2026-12-15 | pod1-16 | done |
| 2026-12-15 | pod2-04 | done |
| 2026-12-15 | pod3-07 | done |
| 2026-12-21 | pod1-04 | done |
| 2026-12-21 | pod1-15 | done |
| 2026-12-21 | pod2-06 | done |
| 2026-12-21 | pod3-02 | done |
| 2026-12-21 | pod3-09 | done |
| 2026-12-21 | pod3-12 | FAILED: stitched source pod3-12.src.mp4 not in render kit (rebuild with tools/clip_bank.py) |

Note: clips without a clip-bank `emph` list use the heuristic beat picker (weaker words). Adding `emph` and re-rendering improves them.
