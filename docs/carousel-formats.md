# Carousel formats (from Andrew's 18 competitor references, Nov 5)
References: `research/carousels/` (first 2 slides × 3 carousels from @danmartell, @garyvee, @hormozi, @joshsnow, @milamarksonofficial, @niksetting).
Renderer: `tools/carousel_formats.py` (1080×1350, HTML → PNG via `tools/shoot.js`). One video becomes several carousels.

| Format | Ref | Look | Built from |
|---|---|---|---|
| `convo` | Hormozi podcast stack | two video frames stacked, yellow caption on top, white on bottom, each caption on the person who says it | any podcast clip (frames + transcript) |
| `tweet` | Hormozi / Martell | black card, avatar + Andrew George + @andrewpreneurship, big plain text; guest quotes in “quotes” with “— Name” (never put a guest's words under Andrew's name; no fake verified badge) | clip lines, ideas, text bank |
| `notes` | Josh Snow | white card, small avatar row, plain step-by-step text | how-tos, lists |
| `lesson` | GaryVee "LESSON #N" | still on top, white panel, yellow label, bold title, quote, "N lessons from …" | one per podcast (guest's clips only) |
| `sticker` | Mila Markson | photo with white rounded sticker lines + "Here's what … 👉" | clip cover + beats |
| `headline` | Josh Snow news cover | photo, condensed caps headline over a dark fade | clip hook, stats |
| `bigword` + `photo` | Dan Martell recap | photo, huge word ("LEVEL UP"), subline, SWIPE →, then photo slides | event videos (LevelUp) |

Per podcast clip (`clip` command): convo + tweet + sticker + headline = 4 carousels. Per podcast: a lessons carousel. Per event video: a big-word recap.
Not used: AI illustration (GaryVee basketball) and handwriting notebook (Mila) — need hand-made art; aesthetic no-text dumps (Nik Setting) — only for real lifestyle photos.
