# Caption rewrite brief (Nov 27, 2026)

Andrew: "the caption is just the transcription instead of something like 'The HighLevel interns always come with great
advice. KEEP GOING YALL!!!' and then some hashtags. Fix the captions on the posts."

Your input: `in-<X>.json` in this folder. Your output: `out-<X>.json` in this folder (write ONLY that file; don't commit,
don't touch anything else).

## Read first
- `docs/brand.md` (voice, pillars, But/Therefore rule) and `.claude/skills/ig-caption/SKILL.md` + `.claude/skills/ig-human/SKILL.md`.

## What to write
1. **Podcast clips** (`clips`): for EACH clip write **3 different captions** (they rotate across the weekly reposts of the
   same moment, so make them genuinely different: different first line / angle / CTA). They post to Instagram, TikTok,
   YouTube Shorts and Facebook with the same text.
2. **Carousels** (`carousels`): ONE caption per item id (Instagram + LinkedIn + Facebook). Some carousels have no clip
   (LevelUp photo posts etc.): write from their title/headline only.
3. **Text cards** (`text_cards`): ONE caption per item id (mostly LinkedIn): 2-5 short lines that expand the card's line
   into a point, plus 0-2 hashtags.

## Style (Andrew's own example is the bar)
- Sounds like Andrew talking: casual, warm, direct, a little hype is fine ("KEEP GOING Y'ALL!!!"). Short. No essay.
- First line is the hook and must stand alone: **max 100 characters** (it gets cut at "...more").
- Body: 1-3 short lines max. Say who's in it when the clip has a guest (use the name exactly as in `source`/`speaker`;
  if `notes` says to confirm a name, use only the first name or "my guest").
- End with **3-5 relevant hashtags** on their own line (e.g. #gohighlevel #agencyowner #saas #entrepreneur #smallbusiness;
  pick ones that fit the clip). Never more than 5.
- Optional light CTA sometimes ("Save this for later", "Tag a founder who needs this", "Follow for more"). No links,
  no "link in bio" promises, no prices or offers that aren't in the transcript.
- Facts only from the transcript/title. Never invent numbers, results or names.
- Total length under 400 characters for clips and carousels, under 600 for text cards.

## Banned (the app blocks these)
- The em dash character (—). Use a period, comma or colon.
- Words: delve, game-changer, unlock, elevate, leverage, seamless, revolutionize, "in today's fast", tapestry, unleash.
- ALL CAPS whole sentences except a short hype tag at the end like Andrew's example (max one per caption).

## Output format (`out-<X>.json`)
```json
{
  "clips": { "pod1-01": ["caption 1", "caption 2", "caption 3"] },
  "items": { "car__pod1-01__tweet": "caption", "card__pod1-01__linkedin": "caption" }
}
```
Every clip in your input gets 3; every carousel and text card id gets 1. Check before you finish: valid JSON, counts
match the input, no em dashes, no banned words, first line <= 100 characters, 3-5 hashtags on clips/carousels.
