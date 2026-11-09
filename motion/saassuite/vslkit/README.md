# vslkit — full-length speaker VSL edits (overlay on Andrew's footage)
Per video dir `motion/saassuite/vsl<N>/`: `overlay.html` (window.render(t), uses `kit.js` + saassuite-motion `lib.js`), `words.js`, `beats.md`.
Work dir `/home/user/work/vsl<N>/`:
1. `curl … -o src.mp4`; `ffmpeg -i src.mp4 -vf scale=1920:1080 -crf 14 -an b169.mp4`; `ffmpeg -i src.mp4 -vn -ac 2 -ar 48000 voice.wav`
2. `python3 words.py voice.wav words.json` → `echo "const WORDS=$(cat words.json);" > vsl<N>/words.js`
3. `python3 tools/face_zone.py b169.mp4 10 | tail -1 > face169.json`; `base916.sh src.mp4 face169.json b916.mp4`; face_zone on b916 → face916.json
4. `python3 music.py music.mp3 SECONDS "prompt"`
5. `check.sh overlay.html WORK 169 "t1,t2"` (stills over base with head box) → fix → `node shoot.js overlay.html 169 WORK/ov169 4` (also 916)
6. `compose.sh WORK 169 vsl<N>` (mix.py: voice + ducked music + SFX cues, −14 LUFS, TP −1.5) → `qa.sh file.mp4` (sheet every 2 s + loudness)
7. `push_render.sh "msg" files…` → branch render-drop/vsl-final
Gotcha: an overlay frame that is fully opaque is saved as RGB and breaks the ffmpeg overlay; kit.js keeps the end card at 0.996 opacity.
