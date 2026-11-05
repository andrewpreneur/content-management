# SOP 10 — Clean up echo and background noise in speech

Tool: `tools/clean_audio.py`. Turns a camera clip's audio into a clearer voice file, then you mix it in with `tools/sound_mix.py`.

1. Clean the part of the clip you need:
   `python3 tools/clean_audio.py SRC.mp4 work/clean/OUT.wav --start 162.88 --dur 35`
   - Default engine `local` = DeepFilterNet3 (free, runs on CPU, ~4 s per 35 s clip) plus a light voice EQ.
   - `--atten 24` (default) sounds natural; `--atten 0` removes as much as possible but can sound dry.
   - `--engine elevenlabs` = ElevenLabs Voice Isolator (best at room echo, uses credits). Blocked until the
     ElevenLabs key is fixed (see SOP 07).
2. Write a voice file pointing at the cleaned WAV. Shift the ranges so they start from `--start`
   (example: `motion/audio/podA.voice.clean.json`).
3. Run `tools/sound_mix.py` with that voice file. Check the result with headphones before approving.

Pod3 Reel A test (no compressor): echo tail after words -7.4 → -10.0 dB; voice-vs-background gap 17.4 → 23.2 dB; words still recognised 95% (raw 96%). If it still sounds roomy by ear, use `--engine elevenlabs` once the key works.
Setup (one time) is in the header of `tools/clean_audio.py`.

## Nov 4 update — clearer voice
- `--gate light|strong` adds a gate after the clean-up that pulls the room echo down between words.
  Pod3 Reel A: echo tail −10.0 dB (current) → −11.6 (light) → −17.9 (strong); word recognition 95% → 94% / 93%.
  Strong can sound choppy: Andrew picks by ear from `voice-compare` (raw / current / light / strong).
- Tried and rejected: Resemble Enhance (generative "studio" restore). It garbled words (speech recognition 96% → 55%) and made the echo tail worse.
- Checked the separate recorder file (`pod3audio.m4a`): it is the same mic the edit already uses (correlation ~0.98, L≈R), so no better source exists for Pod3.
- ElevenLabs Voice Isolator: still 401 "Invalid API key". The key is injected by the environment's **network secret** for api.elevenlabs.io,
  which overrides anything in environment variables. Fix the value there (exact key from ElevenLabs → Profile → API Keys), then start a new session.

## Nov 5 — DECISION: ElevenLabs for everything (Andrew, by ear: "C all the way")
- Default engine is now **ElevenLabs Voice Isolator** via the official SDK (`pip install elevenlabs`, key in `ELEVENLABS_API_KEY`).
  `clean_audio.py` defaults to `--engine elevenlabs`; `clip_bank.py` uses it and only falls back to local DeepFilterNet (no gate) if the API fails.
- The strong gate is retired: it cut words out. Don't use `--gate` on speech for posts.
- Cost: ~12 credits per second of audio (35 s ≈ 424 credits). Pro plan ≈ 1.42M credits/month.
- Key gotchas we hit: a network secret for api.elevenlabs.io overrides the env variable (Andrew removed it); a key can carry a hidden
  0-credit quota (the old "claude" key) → make a new key; ElevenLabs rejects audio shorter than 4.6 s.
