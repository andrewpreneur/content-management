# Script rules: Med Spa EMR training

These rules decide **how the video talks**. The kit's `script.md` decides **what is true** (the steps, the on-screen labels,
words to avoid). Use the kit for facts; rewrite its draft lines into this shape. These rules win over the kit's wording.

## The shape (always this order)
1. **Open (intro card):** "Today I'm going to show you the <Feature> feature on the EMR."
2. **Why (first screen, one sentence):** what it's for, in the clinic's words. "It's built for <who / where>, so <the 2–4
   things it lets them do> <where or how>."
3. **Steps:** one sentence per step, each a single action with the exact on-screen label, joined by sequence words:
   "First, click <Label> in the <place>." → "Then <action>." → "Next, …" → "Finally, …".
   Phone cut: "tap" instead of "click"; if the step starts in the menu, "open the menu and tap <Label>".
4. **Payoff (the screen that matters):** "Here you'll see <what's on screen>. You can <X>, <Y>, or <Z>."
5. **Close (outro card):** "And that's it. If you get stuck, open Support and chat from the menu."

## Sentences
- Full, spoken sentences that flow into each other, like a calm colleague showing you over your shoulder.
  First person for the narrator ("I'm going to show you"), "you" for the viewer, present tense, contractions.
- 7–22 words a sentence. No fragments ("Chair-side tools."), no "Step 2:", no reading out the step titles.
- Name every button exactly as it's written on screen. Never name the CRM vendor ("your CRM"). No jargon.
- Only what's on screen: never invent a feature, number or result.

## Example (In-Room)
> Today I'm going to show you the In-Room feature on the EMR.
> It's built for the treatment chair, so check-in, photos, notes and check-out all happen right from your phone or tablet.
> First, click In-Room in the left menu.  *(phone: First, open the menu and tap In-Room.)*
> Then search for the patient who's in your chair.
> Here you'll see everything for that patient. You can take photos, dictate the note, send forms, or book their next visit.
> And that's it. If you get stuck, open Support and chat from the menu.

## Pace (brisk; no dead air)
- ElevenLabs `voice_settings.speed` **1.1** (≈ 2.5–2.7 words a second on screen overall), stability ≈ 0.5, style ≈ 0.15.
- Gaps between lines ≤ 0.15 s. The voice starts 0.15 s into each step; the click lands ~1 s in; cursor travel 0.7 s.
- Hold after a click **≥ 2 s** (the storyboard's `minHold: 2`), and until the line is finished.
- Intro card ≥ 2.2 s (or its line + 0.15 s); outro line + 0.5 s.
- Measure each clip's real speech end (ElevenLabs alignment) and time from that, not from the file length.
