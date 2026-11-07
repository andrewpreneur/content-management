#!/usr/bin/env python3
"""Write outputs/2026-11-07-catalog/README.md from manifest.csv (every output listed: id, hook, length, format, source, file)."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / 'outputs/2026-11-07-catalog'
REVIEW = 'https://claude.ai/artifact/X7tw3bKS9t6osCF2QX2PAE'

HEAD = f"""# Back catalog: carousels, single images, stories, text (Nov 7 overnight)

**Review page:** {REVIEW}

Drafts only. Nothing was posted anywhere.

## What's here
| Folder | What |
|---|---|
| `carousels/<id>-convo/` | Hormozi podcast-stack carousels, the pod1-05 "Charge less at first" look (real frames, Andrew top, speaker bottom, hook in the band, then the speaker line by line). Feature videos get the same stack: screen moment on top (zoomed so it reads on a phone), Andrew's face below. |
| `carousels/<id>-thread/` | Second carousel per source: real face cover with the hook, then Andrew's take one idea per slide (tweet cards), then one CTA. |
| `singles/` | Quote card, tweet card, stat card. Each at 1080×1350 (IG, Threads, Substack, LinkedIn) and 1200×627 (LinkedIn link-post size). YouTube videos: a feed image built on the real thumbnail. |
| `stories/<videoId>/` | 4-frame IG story per YouTube video: hook, why watch, poll, link sticker. `stories/story-specs.json` has each frame's text and the exact sticker (poll options, link URL). The white button on frame 4 marks where the link sticker goes. |
| `text/` | `linkedin.md`, `threads.md`, `x.md`, `substack-notes.md` (one per YouTube video, link included), `carousel-captions.md`. |
| `manifest.csv` | Every output: id, type, format, platforms, source, hook, length, file. |
| `sources/youtube.json` | The channel's 30 videos (titles, URLs, thumbnails). |

## Why the earlier carousels were bad (and what changed)
Andrew liked pod1-05 "Charge less at first" and disliked the rest. Looking at the Nov 4 feature carousels (`outputs/2026-11-04-funnelstore`, `-switchyard`, `-podcast-ep3`) side by side with pod1-05:
1. **No human.** Every slide was a dark template with a UI screenshot. pod1-05 is two real people on a couch. Now every carousel cover is a real face, and every stack slide has a face.
2. **Tiny screenshots.** The UI sat in a small box with lots of empty space; unreadable on a phone. Now screens are cropped and zoomed to fill half the slide, or left out.
3. **Slide-deck chrome.** Pills, "STEP 1", page counters, footer bars on every slide made it look like a corporate deck. Now: one line of big type per slide, nothing else.
4. **Same layout on every slide.** No rhythm, nothing to swipe for. The stack alternates speaker and caption color (yellow/white) and reads like a conversation.
5. **Manual, not story.** "Step 1, step 2" is a help doc. Thread carousels now follow But/Therefore: problem, turn, consequence, one action.
Never used: V3 "kinetic", AI faces, guest words under Andrew's name.

## Sources used
- **October podcasts** (edited masters, OCTOBER 2026 → VIDEO V+S): Pod1 Andy Griffith (SoloLink), Pod2 Blake Coker (Task Engine), Pod3 HighLevel 2026 interns. 38 clips (pod3-11/12 skipped: 4 people talking over each other). Transcripts from branch `render-kit`.
- **Feature releases** (Oct + Nov 2026 V+S): n8n import, Commerce, new UI (SwitchYard), FunnelStore, Conversation AI working hours, Smart lists → Meta audiences, Meeting Rooms, SaaSSuite branding, SaaSSuite client hub. Downloaded, transcribed with faster-whisper, frames every 12 s.
- **YouTube** @andrewpreneurship: 30 latest videos (titles + thumbnails; YouTube blocked the description scrape after 6, so posts stick to what the title promises).
- Skipped on purpose: SaaSSuite installation and menu-link videos (customer help tutorials, not social content).

## Checks
- Every image looked at by eye on contact sheets (speaker on the right person, no cut-off text, readable screens).
- Speakers in Pod3 identified by mouth movement: Ohaji (black shirt), McKinley (blonde), Ty (green HighLevel sweater). Guests are referred to by name, no pronouns.
- Text linted for em dashes and AI filler words; But/Therefore in every LinkedIn post and thread carousel.
- All JPGs ≤ 400 KB.

## Every output
"""


def main():
    rows = list(csv.DictReader(open(OUT / 'manifest.csv')))
    cnt = {}
    for r in rows: cnt[r['type']] = cnt.get(r['type'], 0) + 1
    s = HEAD.replace('## Every output\n', '## Counts\n' + ' · '.join(f"**{v}** {k}s" for k, v in cnt.items()) + '\n\n## Every output\n')
    s += '| id | type | format | length | hook | source | file |\n|---|---|---|---|---|---|---|\n'
    for r in rows:
        if r['type'] == 'text': continue
        s += f"| {r['id']} | {r['type']} | {r['format']} | {r['length']} | {r['hook'].replace('|', '/')} | {r['source'].replace('|', '/')} | `{r['file']}` |\n"
    s += f"\nText posts ({cnt.get('text', 0)}) are listed in `manifest.csv` and live in `text/`.\n"
    (OUT / 'README.md').write_text(s); print(cnt)


if __name__ == '__main__':
    main()
