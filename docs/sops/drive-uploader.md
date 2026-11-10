# Drive uploader — videos go to _ENGINE / 02-review (set up once by Andrew)

Why: GitHub isn't for video and the Drive connector can't upload video files. This Apps Script web app in Andrew's Google account accepts files from our cloud machines and saves them in Drive.

## Andrew's one-time steps (~5 min)
1. Open https://script.google.com signed in as Andrew → **New project**.
2. Delete the sample code, paste all of `tools/drive_uploader.gs`, click the project name ("Untitled project") and call it **Content engine uploader**. Save (Ctrl/Cmd+S).
3. Left sidebar **⚙ Project Settings** → scroll to **Script Properties** → **Add script property**: Property `UPLOAD_SECRET`, Value: make up a long password (e.g. three random words + numbers). **Save script properties**.
4. Left sidebar **< > Editor** → in the toolbar, pick the function **authorize** → **Run** → **Review permissions** → pick your account → **Advanced** → **Go to Content engine uploader (unsafe)** → **Allow**. ("Unsafe" only means Google hasn't reviewed your own private script.)
5. Top right **Deploy** → **New deployment** → gear next to "Select type" → **Web app**. Execute as: **Me**. Who has access: **Anyone**. **Deploy** → copy the **Web app URL**.
6. Claude cloud environment (title bar → environment **CONTENT** → **Edit**) → Environment variables → add `DRIVE_UPLOAD_URL` = the Web app URL and `DRIVE_UPLOAD_SECRET` = the same password from step 3. Save.
7. Tell Claude "done".

## Use (agents)
- `python3 tools/drive_upload.py ping` → should print the 02-review folder name.
- `python3 tools/drive_upload.py put "2026-11-09 VSL finals/16x9" vsl1-169.mp4 ...` → creates the folder path under _ENGINE/02-review, uploads in 8 MB pieces, skips files already there, prints the Drive links.
- New sessions pick up env vars; a running session needs a restart (or use a fresh worker).
- Never print the secret or URL.
