# AI video rules

The human is the product. AI makes real footage go further; it never replaces it.

## Never
- A full-frame AI avatar of Andrew talking for the whole video (e.g. 30s 9:16 avatar). Bad. Do not make it.
- Standalone 100% AI-generated videos posted as content.

## Allowed uses (only these four)
1. **Extra angles for a visual hook.** From one real shot, generate alternate camera angles (push-in, side angle, overhead) so the first 1–3s has cuts. Tool: Higgsfield.
2. **Filler that makes a real clip flow.** Extend a clip by a second or two, alter the start or end, create a hook beat or a bridge between two real clips.
3. **Environment changes that keep the human.** Background, setting, outfit, lighting swaps. Andrew's face, voice and delivery stay real.
4. **Half-screen format** (the only full AI talking-head case):
   - Voice: ElevenLabs clone of Andrew. Face: Higgsfield using Andrew's character sheet.
   - Andrew's AI face/head occupies **≤50% of the frame for ≥90% of the runtime** — a small rectangle, usually bottom half.
   - The top half (and full-screen moments) carry the value: real screen recordings, screenshots, motion graphics, canvas animations.
   - Edit moves between half/half and full-screen graphics; avatar never goes full-frame for long.

## Half-screen template (9:16, 1080×1920)
```
┌──────────────┐  0–960px: value layer — screen recording / motion graphic / screenshot
│  VALUE LAYER │  hook text overlaid in first 3s
├──────────────┤
│  AI ANDREW   │  960–1920px: avatar crop, max 50% of frame
│  + captions  │  captions sit on the seam or over the avatar's chest
└──────────────┘
Transitions: half/half ↔ full-screen value layer every 3–6s. Avatar full-frame: never more than 10% of runtime.
```

## Labeling
Follow each platform's AI disclosure rules (IG/FB "AI info", TikTok AI-generated label, YouTube "altered or synthetic content" checkbox) for anything using rule 4, and for rule 3 when a change is realistic. See `research/ai-content/` for current platform rules.

## Tools needed (not yet connected)
- Higgsfield MCP — angles, extensions, environment swaps, character sheet.
- ElevenLabs — voice clone, dubbing for translation pages.
