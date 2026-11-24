# SaaSSuite main (style pack)

SaaSSuite / Andrew George explainers, VSLs, onboarding and Skool videos. Approved source: the Skool explainers v5
(`example/engine2.js` + `scenes2.js`, 25 scene types), with Andrew's Nov 24 correction: **clean white and black, white
captions, violet only as a small accent.** Full background: `docs/brand-video/SAASSUITE-STYLE.md`.

## Look
- Off-white `#F6F5F2` scenes (default) and near-black `#0B0B10` "dark moments" (hook reveal, product glow, end card).
- Ink `#141418`, muted `#6B6F7B`. Cards white, 1 px `#E6E4EF`, radius 20, shadow `0 20px 60px rgba(20,20,40,.10)`.
- Accent violet `#7B5CFF` for ONE thing per frame: a word, a pill, a ripple, a progress bar. Never captions, backgrounds or cards.
- Font: **Inter Display** (files in `fonts/`), 800 headlines at −0.037em, 500–700 UI.
- UI is rebuilt as clean floating cards (no device frames, no raw screenshots unless zoomed and cropped).
- Captions: white pill (light scenes) or dark pill (dark scenes), Inter Display 700, the spoken word in violet.

## Motion (`lib.js`, every curve measured)
Smooth ease-out (outCubic / outExpo), slow camera push 2–4 % per scene, cards slide + scale in with soft shadow, one
element morphs into the next inside a scene; clean cut between chapters. One busy moment per video at most.

## Sound
Cinematic ambient bed (~90 bpm), soft whooshes on cuts, soft UI clicks on card events; voice on top; −14 LUFS.

## Don't
Purple-heavy scenes, violet captions, yellow captions (those are only for the short-form reel format), bouncy motion.
