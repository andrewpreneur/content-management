# Podcast audio — ElevenLabs Voice Isolator (Nov 10, 2026)

Andrew's ask: run the full audio track of all 5 podcasts through the ElevenLabs voice fixer and put the cleaned tracks back in the podcast folder.

**Source:** the separate audio recordings in RAW `1OZbZMppuCXBnX8sUuYSH1FYgqq_C7Hfw` (Master Raw → pod1–pod5). Full, unedited tracks.
**Placed back in:** that same RAW folder (next to the originals), plus a copy in `_ENGINE/02-review/Podcast audio - voice isolated/<pod>`.

## Results

| Ep | Source file (id) | Length orig → cleaned | Sync check (start / mid / end) | Cleaned WAV in podcast folder | MP3 320k in podcast folder | 02-review copies (WAV / MP3) |
|---|---|---|---|---|---|---|
| pod1 | pod1audio.m4a `1YNzpNvmue1fBhnNZUOyridKByd-V2Rcj` | 1715.258 s → 1715.258 s (0.0 ms) | -3 / -1 / +7 ms | [pod1audio - voice isolated.wav](https://drive.google.com/file/d/1lBSltTiowKUCwgV2APkSjVQWffPSU5EZ/view) | [mp3](https://drive.google.com/file/d/1L6p5DsSO2LD_x-gcctkbdleMqlogr3vq/view) | [wav](https://drive.google.com/file/d/1ENTeJAaW2u01BuXU_6f_ET7-kgvmWa1W/view) / [mp3](https://drive.google.com/file/d/1d5BnEAPd-oiHiEWLZDnNaaVOdBo_yif9/view) |
| pod2 | Pod2audio.m4a `1WVNDyfza5rYQ5v1pSWu185lLa6MYE4vY` | 938.645 s → 938.645 s (0.0 ms) | -2 / -2 / -2 ms | [Pod2audio - voice isolated.wav](https://drive.google.com/file/d/1bAUTd6jOLeEW_8zuTYKfCGMYEZMFycQJ/view) | [mp3](https://drive.google.com/file/d/1elRcVBtflPV83I7UkulI1HLOT5Z0SJGj/view) | [wav](https://drive.google.com/file/d/1pZhgmzNjNaoRSDeBfolmjOz2HkvHy9Ry/view) / [mp3](https://drive.google.com/file/d/13M0re10qvxytK1NnIUEyv4fOXuwdWy04/view) |
| pod3 | pod3audio.m4a `1o3pgiW3bZevi5luySUnC1GCZ5hdE4Wkv` | 737.771 s → 737.771 s (0.0 ms) | -3 / -2 / +2 ms | [pod3audio - voice isolated.wav](https://drive.google.com/file/d/1OeOy8azOo16_tXObycbuArwvSBopxRCa/view) | [mp3](https://drive.google.com/file/d/1_fw-jqjEBtnAWM9F6dzlRGP0oMggABbi/view) | [wav](https://drive.google.com/file/d/1pI8zEX-nSHmEWTCNicX6YYsp9OxmuA24/view) / [mp3](https://drive.google.com/file/d/1CvplXHa6tQ_u9_0jcTi-yPXH46D97SQc/view) |
| pod4 | Podcast 4.m4a `1qHr1mk3hpzlWrYM40HQFgPY_pg3hZrdI` | 2018.539 s → 2018.539 s (0.0 ms) | -3 / -2 / 0 ms | [Podcast 4 - voice isolated.wav](https://drive.google.com/file/d/1cgyo9t9z8VjGaSr-CIwrT7JJF4QJIWfh/view) | [mp3](https://drive.google.com/file/d/1lIG-0gBtRoBAguWvsK9GRl3etFQkw5FW/view) | [wav](https://drive.google.com/file/d/1YGa2SfBR2p219iL-LtzF7jIbUU_PhfcX/view) / [mp3](https://drive.google.com/file/d/1OwXpBHn_qaRRJSMZP0AKKLtv0mArmsR9/view) |
| pod5 | Podcast5.m4a `1OtyMLrYHW4mSYyJiKgkEb-FIC67-oj89` | 1348.592 s → 1348.592 s (0.0 ms) | -3 / -1 / +7 ms | [Podcast5 - voice isolated.wav](https://drive.google.com/file/d/17KvoADf3aXYci70g9k7EHeytiwO2hhID/view) | [mp3](https://drive.google.com/file/d/11h6nhxrb0EjLPt7KJ0vmZrJCuHcRCOdT/view) | [wav](https://drive.google.com/file/d/1lfiIBwmsk65foEUIO23GuyLnr-m__7WA/view) / [mp3](https://drive.google.com/file/d/1Ny5Np5R0GiggWqHI1Ymomgx-X3I9jRtP/view) |

Sync check = speech-envelope cross-correlation of each channel, original vs cleaned, over 40 s windows. All offsets are under 8 ms (a video frame is 33 ms at 30 fps), with no drift, so the cleaned track drops onto the video at the same position as the original.

## How it was made
- The originals are stereo with **different content in L and R** (looks like one mic per channel). Each channel was sent through `POST /v1/audio-isolation` on its own, so the per-mic split is kept, then joined back to stereo.
- Each channel went up as one whole file (no chunking, so no seams). The longest was about 34 min, under the API's 1-hour / 500 MB limit. Every call returned 200 on the first try.
- ElevenLabs returns 44.1 kHz mono MP3 (320 kbps). That was decoded, resampled to 48 kHz (soxr), then trimmed or padded at the very end so the length matches the original container duration to the sample.
- No other processing: no EQ, compression or loudness change.
- Outputs: WAV 48 kHz 16-bit stereo, plus an MP3 320k copy.
- Cost: about 24 credits per second of audio (two channels), about 162k credits in total. The Pro plan still has about 1.0M left.
- Scripts: `scripts/process.sh` (per episode), `scripts/envlag.py` (sync check), `scripts/all.sh`.

## Notes
- The edited masters in OCTOBER 2026 → VIDEO V+S (`Pod1.mp4`, `Pod3.mp4`) were **not** re-mixed. Their audio is already edited and mixed into the video. To use the cleaned audio there, the editor swaps the raw audio track for the matching `… - voice isolated.wav` in the project, which stays in sync.
- Pod4 and Pod5 have no edit yet. The cleaned tracks are ready for when they get cut.
