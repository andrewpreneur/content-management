# SOP 07 — AI clients (Higgsfield, ElevenLabs)
Both clients read keys from env vars, have a `--dry-run`, and log or cap spend. Follow `docs/ai-video-rules.md`.

## One-line tests
- Higgsfield: `python3 tools/higgsfield_client.py test` → `OK` (or `AUTH FAILED — HTTP 401`)
- ElevenLabs: `python3 tools/elevenlabs_client.py test` → `OK — tier …, characters …` (or `AUTH FAILED`)
- Then: `python3 tools/elevenlabs_client.py voices` → confirm Andrew's clone is listed as `CLONE`. Never create a new clone without Andrew.

## Typical use
- AI opener (rule 1): `python3 tools/higgsfield_client.py submit <model_path> payload.json --dry-run` → check → rerun without `--dry-run --wait --out work/ai/`. Cap: `HIGGSFIELD_MAX_SUBMITS` (default 20 per log), every submit logged to `logs/higgsfield-spend.jsonl`.
- Podcast segment voice: `python3 tools/elevenlabs_client.py tts <VOICE_ID> text/podcast-extended-segment.md seg.mp3` (cap `ELEVENLABS_MAX_CHARS`, default 12 000).
- Spanish dub: `python3 tools/elevenlabs_client.py dub master.mp4 es master_es_dub.mp4`.

## Needs Andrew — fix the two keys (≈5 min)
Tonight both services answered **401**: the session proxy sends the keys in the wrong header.
1. On claude.ai/code, open this project's session → click the **environment name** in the title bar → **Edit**.
2. Find **Network secrets** (older apps: "API credentials").
3. **ElevenLabs** (`api.elevenlabs.io`): set the header name to **`xi-api-key`** and the value to your ElevenLabs API key (ElevenLabs → Profile → API Keys). Not `Authorization`.
4. **Higgsfield** (`platform.higgsfield.ai` *and* `api.higgsfield.ai`): header **`Authorization`**, value **`Key <your key id>:<your key secret>`** — the word `Key`, a space, then id and secret joined by a colon. (Higgsfield Cloud → API keys. This is the API key, not your app login.)
5. Save. Start a new session (secrets load at start). Claude runs the two tests above and tells you the result.
Alternative: add them as environment variables `ELEVENLABS_API_KEY` and `HIGGSFIELD_API_KEY` (= `id:secret`) instead; the clients read those too.
