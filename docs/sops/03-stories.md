# SOP 03 — Story sequences
Strategy and templates: `docs/stories.md`. Photo picks: `research/brand/photo-library.md`.

1. Choose the sequence for the day (`docs/stories.md` cadence). Default for a feature drop: **hook → authority → proof → value (poll) → value (question) → DM keyword CTA**.
2. Visuals: real photos from the library for hook/authority/CTA; real screenshots (4K frames from the source) for proof/value. AI lifestyle images of Andrew (Higgsfield Soul) only as backgrounds that match his real look (see photo-library "Andrew's look"), never as fake proof.
3. Write `stories/spec.json` (fields in `tools/story.py`). Text ≤15 words/frame, hook ≤8, inside x 64–1016 / y 250–1580.
4. Render: `python3 tools/story.py spec.json stories/`.
5. Stickers are placeholders (dashed box). Andrew/VA adds the real poll/question sticker in the IG app at the same spot when posting.
6. DM keyword (e.g. STORE) must have a matching GHL automation before the story goes live (tag `kw-<KEYWORD>`, send the resource, ask for email).
