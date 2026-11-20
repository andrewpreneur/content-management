# Podcast audio: ElevenLabs voice isolator on the FINAL edits (Nov 20, 2026)

Andrew (Nov 20): never edit or clean the RAW files; clean only the final output.
Source: the edited masters Pod1–Pod5.mp4 in OCTOBER 2026 → VIDEO V+S (`1JVEoN5wvfCp81mX_wnKjw5Ck0sUjGn9q`).
Output folder: `_ENGINE/02-review/Podcast audio - final edits, voice isolated` (made by the Drive bridge).

| Ep | Edited master | Length | Clean MP3 (320k) | Clean WAV (44.1 kHz stereo) |
|---|---|---|---|---|
| pod1 | Pod1.mp4 `1o16B2yPjlANHRT6xhp6hvU0dh32pJefg` | 1307.94 s | [mp3](https://drive.google.com/file/d/17GsCSNO0huT8kECy0AihfQ3fN_L76sNc/view) | [wav](https://drive.google.com/file/d/12lNVssjASyQADAlzIwCTOgjhREsYR1h4/view) |
| pod2 | Pod2.mp4 `19oDJJJ-NDbI9FCOE6XBZTuyPGvXiEln0` | 645.47 s | [mp3](https://drive.google.com/file/d/1rZWbIbNC6uRrr4Pg3d1EotxkyyNXK2aV/view) | [wav](https://drive.google.com/file/d/1eeubkzdCfqgj-y6GiTAmtraAwhEd_ynL/view) |
| pod3 | Pod3.mp4 `1sfvECkswOzt0svNs3O-rOQDRGFGyH4qw` | 539.61 s | [mp3](https://drive.google.com/file/d/14gW4UQ1ya-CwQSAa1vRNR9U2bxjjiffI/view) | [wav](https://drive.google.com/file/d/1kvob2eCxXIJxIMRsCTu3QivduHdWSDgh/view) |
| pod4 | Pod4.mp4 `1afmND5PuIEsqrqZW0kQydATWXmN4gJM6` | 1310.21 s | [mp3](https://drive.google.com/file/d/1N7r-dLNDfVA0gKFGplxHJBIaMbwj7j4y/view) | [wav](https://drive.google.com/file/d/1rAjoOKRav0Rg9AlgeZ2KNPQuLxkkA2G6/view) |
| pod5 | Pod5.mp4 `1Y155YLAkxZclpxhEwQ5fQgWgweHdb2td` | 875.95 s | [mp3](https://drive.google.com/file/d/1Bkn-2kjNEhoo7IXnoXnbEJl50630_wb9/view) | [wav](https://drive.google.com/file/d/12zs48Sg2tn2Pg_bdUtFDTck4TYA6lXQM/view) |

How: the edit's stereo has one mic per side (L−R is as loud as the mix), so each side went through `POST /v1/audio-isolation`
on its own and was joined back to stereo at the edit's 44.1 kHz, trimmed/padded to the exact sample count (all within 3 ms of the
edit's length, so it drops onto the video in sync). No other processing. Script: `clean.sh`.
Check: loudness at the start, middle and end matches the edit within ~2 dB, so no music beds or intros were stripped.
The Nov 10 run (`2026-11-10-podcast-voice-isolated`) cleaned the RAW tracks; it is superseded and no longer used by the app (files left in Drive, untouched).
Video with the clean audio swapped in: not made (4K masters, 1.2–2.8 GB each); the editor can drop the WAV onto the timeline, or ask and we remux.
