#!/usr/bin/env python3
"""Write README.md + the review page data from build/*/mix.json and timing.json. Usage: python3 make_readme.py [REVIEW_URL] [assets.json]"""
import json, sys
from pathlib import Path
HERE = Path(__file__).parent
S = json.loads((HERE / 'scripts.json').read_text())
VOICE = {'andrew': 'Andrew (clone, "Andrew VoiceMail")', 'jessica': 'Jessica (Playful, Bright, Warm)', 'briggs': 'Briggs (Optimistic, Encouraging)',
         'savvy': 'Savvy (Warm, Grounded)', 'ash': 'Ash (Conversational, Kind)', 'alex': 'Alex (Upbeat, Clear)'}
VISUAL = {'onb1': 'Roadmap: scenes slide sideways like moving along a map. 3-path chooser (new / idea / offer) with the camera riding each path, goal card, Classroom, downloads + prompt filling in, Calendar coaching calls, pinned announcements, intro post typed, ends in Classroom.',
          'onb2': 'Feed: scenes scroll vertically like a feed. Post seen by members, training cards, toolkit tiles, three progress posts, a question with Goal / Tried / Stuck and replies, coaching calendar, member gallery with badges, intro post.',
          'onb3': 'Momentum: scenes zoom forward. "Finish." title, 4 target options, dart hits a target, toolkit, course page with "Up next", lesson + your project side by side, question post, new drops push a progress bar, 7-day assignment, week fills, puzzle piece snaps in.',
          'intro': 'Composer: an intro post written live, step by step (1-6), the 7-day assignment, the post getting seen, then Classroom.',
          'ask': 'Question template: post it or bring it to coaching, a workflow with the stuck step flagged, Goal / Tried / Stuck typed in, replies arrive, what you are building + the decision, coaching call.'}
SRC = {'intro': 'Onboarding 1 (start by introducing yourself; where you\'re at / build / goal), Onboarding 2 (first post can be simple; get the most out of it; post the offer / show the product; pick a training), Onboarding 3 (first assignment, 7 days).',
       'ask': 'Onboarding 2 (ask about the part of your workflow; what / tried / stuck; enough context; bring questions into coaching), Onboarding 3 (when you get stuck; include what you\'re building and the decision).'}
from mix import NAMES
url = sys.argv[1] if len(sys.argv) > 1 else '(review page link pending)'
rows = []
for vid in ['onb1', 'onb2', 'onb3', 'intro', 'ask']:
    for v in ['andrew', S[vid]['pro_voice']]:
        d = HERE / 'build' / f'{vid}_{v}'
        m = json.loads((d / 'mix.json').read_text()); t = json.loads((d / 'timing.json').read_text())
        rows.append((vid, v, m, t['duration']))
L = [f"# Skool onboarding videos (Nov 7, 2026)", '', f"**Review page:** {url}", '',
     'Motion-graphic onboarding videos for the Skool community, made from `../scripts.md` (Onboarding 1-3) plus two short how-tos built only from lines in those scripts. '
     'Each one comes in two voices: Andrew\'s ElevenLabs clone and a pro voice. No faces, nothing posted. Drafts for Andrew\'s review.', '',
     '## Outputs', '', '| id | title | voice | length | format | LUFS / true peak | file (branch `render-drop/skool-onboarding`) |', '|---|---|---|---|---|---|---|']
for vid, v, m, dur in rows:
    L.append(f"| {vid} | {S[vid]['title']} | {VOICE[v]} | {int(dur // 60)}:{int(dur % 60):02d} | 16:9 1920x1080 60fps, H.264 CRF 20, AAC 192k | {m['lufs']} / {m['true_peak_db']} dB | `skool-onboarding/{m['file']}` |")
L += ['', '## What each video looks like', '']
for vid in ['onb1', 'onb2', 'onb3', 'intro', 'ask']:
    L.append(f"- **{S[vid]['title']}** ({S[vid]['step']}): {VISUAL[vid]}" + (f" Lines from: {SRC[vid]}" if vid in SRC else ''))
L += ['', 'Series look: same intro sting (navy, yellow "A" mark, title, "Step N of 3" with dots), same top-left step pill, same karaoke captions synced to the voice word timestamps, same navy end card ("Step 1 done. Next up: ..."). Each video has its own accent colour (blue / violet / green) and transition style.', '',
      '## Script changes', '',
      '- **Onboarding 1, 2, 3: word for word.** No wording changed.',
      '- Pronunciation only (spoken text, not on screen): "GoHighLevel" is sent to ElevenLabs as "Go High Level", "SaaS" as "sass".',
      '- The two short how-tos reuse script sentences in a new order (sources above). No new spoken lines.',
      '- On-screen titles and labels are mine (e.g. "Find your starting point", "Pick your path", "Path 1 / I\'m new").', '',
      '## Placeholders to confirm', '',
      '- Community name in the mockups: "Andrew\'s Community" with a yellow "A" mark. Swap for the real name/logo.',
      '- Course names (Start Here, Build: SaaS + AI, Get Clients, GoHighLevel Foundations, Skills + Prompts Library, Coaching Replays), member names, post titles, prompt text and calendar days are example content, not real data.',
      '- The UI is a clean rebuild in the style of a Skool community (Community / Classroom / Calendar / Members tabs). No Skool logo.', '',
      '## How it was made', '',
      '- Voice: ElevenLabs `eleven_multilingual_v2` `with-timestamps`, paragraph by paragraph with previous/next text (`voice.py`). Every paragraph transcribed back with faster-whisper (`check_voice.py`); paragraphs where the clone added a word (an extra "And" or "But") were regenerated until clean. Final MP4s re-transcribed (`check_final.py`): 100% of script words heard over the music.',
      '- Visuals: one HTML page (`skool.html` + `engine.js` + `videos.js`) where `seek(t)` draws any frame; every element is anchored to the voice word timestamps. `render.mjs` renders with Playwright at 60 fps.',
      '- Music: ElevenLabs music API, 4 instrumental beds (onb1 marimba/pluck 112 BPM, onb2 acoustic/ukulele 108, onb3 synth-pop 118, shorts marimba 114). Start offset chosen so scene cuts sit near the beat; ducked 17 dB under speech.',
      '- SFX: CC0 sounds from the `sound-effects` skill library (Freesound/Kenney: whoosh, pop, click, tick, keyboard typing, confirmation ding, soft impact). No synthesized beeps.',
      '- Mix (`mix.py`): -14 LUFS integrated, true peak at or below -1 dB, measured on the exported MP4.',
      '- Rebuild everything: `./build_all.sh` (needs `python3 make_fonts.py` once). Frame check: `node render.mjs onb1 andrew --sheet 1`.', '',
      '## Next', '', '- Andrew picks a voice per video and gives the real community name; then swap the name and re-render (about 2 min per video).',
      '- If Andrew wants 9:16 versions for social, the layout needs a vertical pass.', '']
(HERE / 'README.md').write_text('\n'.join(L))
print('README written')
