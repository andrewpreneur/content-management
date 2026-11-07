#!/usr/bin/env python3
"""Build README.md from the batch log + ffprobe. python3 gen_readme.py <scratch> <review_url>"""
import json, subprocess, sys
from pathlib import Path
S, URL = sys.argv[1], sys.argv[2]
HERE = Path(__file__).resolve().parent.parent
log = [json.loads(l) for l in open(f'{S}/batch.log') if l.startswith('{')]
mix = {Path(r['out']).name: r for r in log if 'lufs' in r}
syn = {r['file']: r for r in log if 'word_match' in r}
HOOK = {'vsl1': 'Building a business with AI feels like a puzzle while someone keeps adding pieces',
        'vsl2': "Every week I'm working on something with AI, SaaS or GoHighLevel",
        'vsl3': "What's a problem you understand well enough to build a business around?"}
LOOK = {'vsl1': 'The puzzle (dark navy, yellow/blue pieces)', 'vsl2': 'Build log (warm paper, notebook, serif accents)', 'vsl3': 'Make it yours (bold colour floods, caps)'}
rows = []
for f in sorted(Path(f'{S}/final').glob('*.mp4')):
    n = f.name; v, voice, fmt = n[6:-4].split('_')
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)
    m, s = mix.get(n, {}), syn.get(n, {})
    rows.append(f"| `{n[:-4]}` | {'VSL ' + v[3] + (' cut' if 'cut' in v else '')} | {HOOK[v[:4]]} | {d:.0f} s | {fmt.replace('x', ':')} | {voice.capitalize()} | {LOOK[v[:4]]} | {m.get('lufs')} / {m.get('true_peak')} | {s.get('word_match', 0) * 100:.1f}% | `render-drop/skool-vsl:{n}` |")
md = f"""# Skool VSLs: motion graphics, two voices each

**Review page (watch all 20 here):** {URL}

20 MP4s: VSL 1, 2, 3 (full, about 70 to 90 s) plus 30 to 45 s cuts of VSL 1 and VSL 3, each in Andrew's own voice clone and in a pro narrator, each in 16:9 (1920×1080, Skool About page) and 9:16 (1080×1920, ads).
No faces anywhere. All motion graphics, kinetic type, icons and clean rebuilt UI mockups (GoHighLevel pipeline, Claude chat, Skool-style community, classroom and calendar).

## Outputs

Files live on branch **`render-drop/skool-vsl`** (H.264 CRF 20, AAC 192k, faststart, 30 fps). 720p previews are on the review page.

| File | Video | Hook (first line) | Length | Format | Voice | Look | LUFS / true peak (dB) | Whisper word match | Location |
|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(rows) + f"""

**Why VSL 1 and VSL 3 for the short cuts:** both open on a hook that works cold (a picture of the problem, a direct question). VSL 2 leans on "if you follow my content", so it needs context and works best as the full About-page video.

## The three looks
- **VSL 1, The puzzle.** Brand navy with yellow and blue jigsaw pieces. Pieces assemble, then extra pieces rain in ("somebody keeps adding new pieces"), tool names land on pieces, wires tangle ("complicated fast"), then the board snaps together on "That's why I built this community". Ends with the last piece dropping in on "start building". Snappy pop-up transitions.
- **VSL 2, Build log.** Warm paper canvas with a faint grid, ink type, blue serif italics for the human words, yellow marker highlights. A week planner, stamps, a notebook that ticks itself off, a GoHighLevel pipeline, an automation, a coaching call (initials only, no faces), a post being written in the community. The camera glides sideways from page to page.
- **VSL 3, Make it yours.** Bold colour floods (blue, navy blueprint grid, yellow, white), each scene grows out of the last as a circle. Uppercase heavy type, an ignored-leads inbox, a clock that flips to "Automated", a Customer → Build → Offer → Sell → Deliver path, blocks stacking on a GoHighLevel foundation, an idea flying through a door on "give that idea somewhere to go".

Every video: a new visual beat every 1.5 to 3 s, captions synced word by word to the ElevenLabs timestamps (line shows dim, each word lights up as it is spoken), end card "Join the community" / "Join us inside" with a cursor click. No invented numbers, logos or testimonials. Example UI content (lead names, post titles) is placeholder.

## Script changes
Full VSLs are word for word from `../scripts.md`. Only the cuts changed:
- **VSL 1 cut:** kept paragraphs 1, 2, 4, 5, 7 (shortened), 11. Paragraph 7 became: "You'll get practical training, downloadable skills, prompts, and coaching, plus a place to bring questions as you work through it." (merged two sentences so it flows without "resources you can use in your own business").
- **VSL 3 cut:** kept paragraphs 1, 2 (first two "Maybe" lines), 3, 4+5 joined, 6, 12. No words changed inside kept sentences.
- Mockup copy is my own (course names, post titles, notification text). The UI says the community is called "AI + SaaS Builders" / "Behind the build" / "Builders inside" as placeholders: **tell me the real community name** and I'll swap it in.

## Voices
See `voices.md`. Andrew's clone "Andrew VoiceMail" plus one pro narrator per VSL (VSL 1 Alex, VSL 2 Joe Inglewood, VSL 3 Brian). `eleven_multilingual_v2`, paragraph by paragraph with previous/next text, every line transcribed back with whisper and re-rolled when a word was wrong. No new clone created.

## Sound
- **Music:** composed per VSL with the ElevenLabs Music API (`music_v1`, instrumental, ~105 s each; prompts in `music-prompts.txt`). VSL 1 playful marimba/pizzicato 112 BPM, VSL 2 warm lo-fi house 118 BPM, VSL 3 driving synth-pop 122 BPM. The track is end-aligned so its own ending lands on the end card. Music generated on Andrew's ElevenLabs Pro plan; check ElevenLabs' music terms for paid ads before running them as ads.
- **Mix:** voice first; music ducks about 12 dB under speech and lifts between lines and on the end card. Two-pass loudnorm to **-14 LUFS**, true peak ≤ -1 dB, measured on the exported MP4 (table above).
- **SFX:** light whooshes on scene changes, pops/ticks on items landing, clicks on cursor presses, a soft impact on the big moments. All real recorded CC0 files from the `sound-effects` skill library (Freesound CC0 and Kenney CC0), no synthesised beeps. Sources and licences can change, so check the source pages now and then. Credits: `CREDITS.txt`.
- I can't hear, so these are measured, not judged. **Please check with headphones:** VSL 1 at 0:07 (pieces raining in, busiest SFX moment), VSL 1 at the "That's why I built this community" snap, VSL 2 at the coaching call (waveform + music under the voice), VSL 3 first 5 s (hook + music start), and any end card (music swell + click).

## Checks done
- Frames sampled every second (contact sheets) for both formats: text readable, nothing off-screen, no overlap between captions and visuals.
- Whisper transcription of every finished MP4: word match vs script (table) and caption timing vs heard audio (median offset about -70 ms, inside whisper's own error).
- Loudness and true peak measured on every exported file.

## Drive
**Not uploaded to Drive.** The Drive connector in this session only takes file content inline (base64 in the tool call), which can't carry 10 to 25 MB videos. Get them from the review page or from branch `render-drop/skool-vsl` (GitHub → branch → file → Download).

## Rebuild
```
python3 src/tts.py scripts/vsl1.txt <voice_id> <dir>     # voice, paragraph by paragraph
python3 src/qc_voice.py <dir> && python3 src/fix.py <dir> # whisper QC + re-roll
python3 src/stitch.py <dir> voice.wav timing/<set>.json   # one track + word timing
bash src/batch.sh <scratch>                               # render (Playwright) + mix + checks for all 20
```
Pages: `src/vsl1.html`, `src/vsl2.html`, `src/vsl3.html` (+ `engine.js`, `components.js`, `base.css`). Open one in a browser with `?timing=../timing/vsl1-pro.json` (add `&fmt=v` for 9:16) to scrub it.

## Next
- Andrew: watch, pick a voice per VSL, say what to change. Then I re-render only what changed.
- Swap in the real community name, price or link for the end card when known.
"""
(HERE / 'README.md').write_text(md)
print('ok', len(rows))
