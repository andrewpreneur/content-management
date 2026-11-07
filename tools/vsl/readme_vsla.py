#!/usr/bin/env python3
"""README for outputs/2026-11-07-vsl-a from manifest.json."""
import json, sys
from pathlib import Path
O = Path(sys.argv[1]); man = json.load(open(O / 'manifest.json')); url = sys.argv[2]
L = [f'# vsl-a: VSL VIDEO 1–4 cuts (Nov 7, 2026 overnight)', '', f'**Review page:** {url}', '',
     f'**{len(man)} videos.** Full-quality files: branch `render-drop/vsl-a` (`V1/` … `V4/`). Nothing posted.', '',
     '## What each video sells', '- All four pitch the same offer: **AI Studio (vibe coding) inside GHL, white-labeled, sold alone for $99/month**, 30 days free. VIDEO 1 is the teaser (feature not named, "watch the full training").',
     '- Claims Andrew makes on camera (check before running ads): Jensen Huang / NVIDIA CEO quote (All-In podcast: "greatest technology equalizer", "more millionaires in 5 years than the internet in 20"); customers pay $99/month; newest agency has 300 sub-accounts (VIDEO 4); "15 spots" (VIDEO 4); 30-day free trial; free onboarding + sales video (VIDEO 2).',
     '- Graphics never add numbers he did not say. The 15-seat graphic shows empty seats (no fake "spots taken").', '',
     '## Variant key', '| Code | What it is |', '|---|---|',
     '| A | Clean brand-kit edit, 16:9 (landing-page VSL): captions, punch-ins, lower third, motion cards (half-screen and full) |',
     '| V916 / V45 | Same edit for 9:16 and 4:5: cards sit on the top half, Andrew stays on the bottom half |',
     '| H1–H3 (4:5), H1V–H3V (9:16) | Hook tests: a strong line pulled to the front as a cold open + hook box, then the full video |',
     '| S916 / S45 | Short ad cut (20–40 s) from the strongest lines |',
     '| M916 / M169 / M45 | No face: original voice over motion graphics (sentence typography + feature cards) |',
     '| T45 / T916 | No face, no voice: text + motion graphics + music (silent-friendly ad, ~20–35 s) |', '',
     '## Every output', '| id | variant | format | length | opens with | source | file |', '|---|---|---|---|---|---|---|']
for r in man:
    L.append(f"| `{r['id']}` | {r['desc']} | {r['format']} | {r['length']:.0f}s | {r['hook']} | {r['source']} | `{r['file']}` |")
L += ['', '## How it was made', '- Tool: `tools/vsl/` (`specs_vsla.py` holds every cut, card and hook; `vsl.py` renders; `preview.py` for stills). Re-render one: `python3 tools/vsl/specs_vsla.py V2 H1`.',
      '- Source: 4K Drive originals, cropped per shot (wide / tight / close / face-right for half-screen cards). Voice: original audio, high-pass + light compression, -14 LUFS, true peak -1.5 dB. Music: Mixkit tracks from `render-kit` (licence not confirmed, same beds as earlier reels) ducked ~8 dB under the voice. SFX: CC0 kit (whoosh on card entrances).',
      '- Brand kit: navy #0B0F1A, yellow #FFD23F, blue #2E7DFF, Inter Tight + Instrument Serif accents. No V3 kinetic. No AI face anywhere.',
      '- Transcripts: `transcripts/` (whisper small.en; captions fix ChatGPT, GoHighLevel, Base44, AI Studio, "done-for-you", "Tap the link").']
(O / 'README.md').write_text('\n'.join(L) + '\n')
print('README', len(man))
