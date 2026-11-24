# LumeClick
Clean, confident explainers for LumeClick (marketing for home service businesses): warm light-grey canvas, one big two-line headline on the left with ONE navy keyword, real-looking product cards floating on the right, a word-synced caption pill at the bottom. Built from the motion-library video "Voice agent SaaS launch" (reference/looks-like-…-sheet.jpg) in LumeClick's own colours.

## Look
- Canvas: soft radial #fbfbfa → #f4f4f2 → #ecebe8. Never pure white, never dark scenes (the dark stat cards are the one exception).
- Left: eyebrow pill (white, 1.5 px border, amber dot, 21 px caps, wide tracking) → headline 104 px Inter Display Bold, -0.035em, two short lines, keyword in navy #175892 → optional grey sub line.
- Right: white cards (radius 30, soft long shadow), notification rows (radius 18). Contractor examples: phone calls, Google search, map pack, website, review texts, pipeline, case-study numbers.
- Colour jobs: navy = brand + the keyword; amber #f59f0a = stars, "start here", highlights; green = calls answered; red = missed calls. One accent per frame.
- End card: LC mark + wordmark, one line ("No contracts. You own everything."), navy "Get your free audit →" pill + white "lumeclick.com" pill, phone number.

## Motion (see example/index.html, all pure functions of time)
- Headline words rise 46 px with blur, 0.055 s apart. Cards pop (spring 17/0.72, from 0.94 scale + 34 px). Rows slide from the right (spring 19/0.8).
- One live thing per scene: phone rings then turns missed, search text types, page-speed ring fills, the brand climbs the map pack, pipeline nodes light on the spoken word, review phrases get an amber highlighter on the spoken word, bars spring up.
- Scenes dissolve out in 0.42 s (blur 10, up 18 px) while the next headline rises.

## Sound
ElevenLabs "Chris" at 1.08 speed, plain contractor talk. Music bed ducked under the voice, soft whoosh on every scene change, quiet pop when a card lands. Final -16 LUFS, peaks ≤ -1 dB.

## Facts
Only from the site, the owner, or Google reviews (example/facts.md). Never invent prices, numbers or quotes. Example businesses on screen ("Mike's Plumbing") are clearly illustrative.
