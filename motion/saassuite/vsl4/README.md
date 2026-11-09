# VSL VIDEO 4 — final edit (warm launch / ClimbX variant, accent #FF692F)

Files: `overlay.html` (scenes, Andrew's words only) · `kit.js` (shared components: kicker, letter-rise headline, card slide, stamp pill + shock ring, rows with strike, typing, site skeleton bar fills, button press, confetti, karaoke captions, HUD, dark end card) · `words.js`/`words.json` (faster-whisper word timings) · `shoot.js` (Playwright → PNG-in-MOV overlay + SFX cue list) · `mix.py` (voice + ducked ElevenLabs bed + SFX, −14 LUFS, TP ≤ −2) · `composite.sh`.

Face zone (tools/face_zone.py): 16:9 head x 632–1147, y 0–655 → graphics panel x 1196–1873, y 210–605; captions y 932. 9:16 crop x 1172–2387 of the 4K source; head y 0–1155 → panel y 1198–1589; captions y 1636.

Render: `node shoot.js overlay.html 169 ov169.mov` (and 916) → `python3 mix.py base169.mp4 music.mp3 ov169.mov.cues.json 67.9 mix.wav` → `./composite.sh base169.mp4 ov169.mov mix.wav 67.9 vsl4-169.mp4`.
Output: `render-drop/vsl-final` → `vsl4-169.mp4`, `vsl4-916.mp4` (67.9 s = 64.8 s of Andrew + 3 s end card).
