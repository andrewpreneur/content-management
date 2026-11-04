# SOP 06 — Agents: who does what
**Hard cap: 5 new sub-agents per day across all sessions.** Log every spawn (`Agents spawned: n/5`).

| Role | Does | Writes to |
|---|---|---|
| Main session (Claude) | Runs SOPs 01–05, renders, writes text, QA, logs, commits | `outputs/`, `logs/`, `docs/` |
| Research agent | One narrow question (competitors, story frameworks, a tool's API) with sources | `research/…` or one `docs/` file |
| Library agent | Catalogues photos/footage in Drive (read-only), picks + notes | `research/brand/photo-library.md` |
| Overnight worker | Follows `todo/overnight-*.md`, commits hourly | everything above |

Rules: narrow brief, one output file, no commits/pushes from sub-agents (main session commits), never touch Andrew's original Drive files, never spend credits without a cap in the brief.
