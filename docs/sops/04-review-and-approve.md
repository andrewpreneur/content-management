# SOP 04 — Review and approve
**Nothing posts without Andrew's approval.**

1. Engine puts drafts in Drive `_ENGINE/02-review/<run>/` and publishes the run's review page (Artifact "One → Twenty") with every output playable/readable.
2. **Andrew (on phone, ~10 min per run):** open the page → for each output tap ✅ approve / ✏️ change (one line why) / ❌ reject. Until the review app exists, reply in chat or comment on the page.
3. Engine applies changes, moves approved files to `03-approved/`, sets `status = approved` in the manifest (later: Supabase `outputs`).
4. Every change Andrew makes to wording → captured in Second Brain "Brand voice" so the next run is approved first time.
5. Later (Lovable review app on Supabase): same three buttons, writes `outputs.status` + `review_notes`.
