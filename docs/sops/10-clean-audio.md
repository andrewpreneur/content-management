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

Pod3 Reel A test: gap between voice and background went from 17.4 dB to 21.3 dB (22.0 dB with `--atten 0`).
Setup (one time) is in the header of `tools/clean_audio.py`.
