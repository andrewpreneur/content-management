# Style packs

A style pack is everything an editor (Claude Code, Your Software Agent, any AI) needs to make a video **look like ours**
without having been in the room when we built it. Prompts alone don't carry a look; working code and pictures do.

Every job that makes a video carries exactly one pack (Your Content System won't send without one). Packs are published
to the toolkit as `style-<id>.tar.gz` (`python3 tools/publish_toolkit.py`), and the job input links the chosen one.

## What's in a pack
| File | What it is | How the editor uses it |
|---|---|---|
| `STYLE.md` | The look in words: colours, type, layout, motion, captions, sound, do / don't | Read first, follow exactly |
| `SCRIPT.md` | How the video talks: the shape of the script, sentence rules, an example, the pace | Rewrite the kit's draft lines into it; it wins over the kit's wording (the kit keeps the facts) |
| `tokens.json` | The same values as data | Use these values, never guessed ones |
| `reference/*.jpg` | Stills from a finished, approved video | **Look at them** before designing; the test version must look like a sibling |
| `example/` | The source of that approved video | Copy its patterns (layout, motion helpers, captions, timing); don't start from a blank page |
| `lib.js` (some packs) | Measured motion curves | Use for every move |
| `fonts/` (some packs) | The font files | Embed them; never fall back to a system font |

## Packs
| id | Name | Use for | Approved source |
|---|---|---|---|
| `medspa-emr-training` | Med Spa EMR training | Click-by-click training videos from EMR screenshot kits (any feature) | `motion/explainers/emr-in-room` (Nov 24) |
| `medspa-marketing` | Med Spa Marketing | Med spa staff training and marketing explainers that are not screenshot walkthroughs | `motion/medspa/deposits` (Nov 13) |
| `saassuite` | SaaSSuite main | SaaSSuite / Andrew George explainers, VSLs, onboarding, Skool | `motion/saassuite/skool` v5 (Nov 2026) |

## Rules for every pack
1. Words: the pack's `SCRIPT.md` decides how the video talks and its pace; the zip's script decides what's true (steps, labels,
   words to avoid). A pack without SCRIPT.md: follow the zip's wording.
2. If the job's zip has its own design system (`brand/design-system.md`), its colours, fonts and layout win; the pack still
   supplies motion, captions, the checking steps and the example to copy.
3. Every screenshot walkthrough follows the storyboard contract and passes `tools/explainer_qa.mjs` (SOP 13).
4. The 10-second test is compared side by side with `reference/` before anyone is asked to approve it.

## Making a new style (when nothing fits)
Chat's "Make a new style" does this first, as its own short job, before the video:
1. Collect 3–6 references (videos or stills the person likes; their logo, colours, fonts).
2. Write `STYLE.md` + `tokens.json` from them (measure colours from the pictures; name the fonts).
3. Build ONE 8–10 s sample scene in the new style with the closest pack's `example/` as the starting point.
4. Render 4 stills into `reference/`, look at them, fix, and send the sample for approval.
5. Once approved, save the pack (`styles/<id>/`) and publish it; the video job then uses it.
