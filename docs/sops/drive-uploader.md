# Drive uploader — videos go to Drive (set up once by Andrew)

Why: GitHub isn't for video and the Drive connector can't upload video files. This Apps Script web app in Andrew's Google account accepts files from our cloud machines and saves them in Drive.

**Safety:** the script only has Google's `drive.file` permission, so it can see and change only files and folders it created itself, never Andrew's other files. Every request also needs the secret password. Worst case if the URL and password both leaked: someone could upload junk into the "Engine video uploads" folder.

## Andrew's one-time steps (~6 min)
1. Open https://script.google.com signed in as Andrew → **New project**. Click "Untitled project" and name it **Content engine uploader**.
2. Delete the sample code and paste all of `tools/drive_uploader.gs`. Save (Cmd+S).
3. Left sidebar **⚙ Project Settings** → tick **Show "appsscript.json" manifest file in editor**. Back in **< > Editor**, open `appsscript.json`, replace everything with `tools/drive_uploader.appsscript.json`, save. (This limits the permission to "only files this app created".)
4. **⚙ Project Settings** → **Script Properties** → **Add script property**: `UPLOAD_SECRET` = a long made-up password. **Save script properties**.
5. **< > Editor** → open `Code.gs` → function dropdown **authorize** → **Run** → **Review permissions** → your account → **Advanced** → **Go to Content engine uploader (unsafe)** → **Allow**. The permission screen should say it can only see files it creates.
6. Drive now has a new folder **Engine video uploads** in My Drive. Drag it into **_ENGINE → 02-review**.
7. **Deploy** → **New deployment** → gear → **Web app**. Execute as: **Me**. Who has access: **Anyone**. **Deploy** → copy the **Web app URL**.
8. Claude cloud environment (title bar → **CONTENT** → **Edit**) → Environment variables: `DRIVE_UPLOAD_URL` = the Web app URL, `DRIVE_UPLOAD_SECRET` = the password. Save. Tell Claude "done".

## Use (agents)
- `python3 tools/drive_upload.py ping` → confirms access.
- `python3 tools/drive_upload.py put "2026-11-09 VSL finals" file1.mp4 ...` → subfolders under "Engine video uploads", 8 MB pieces, skips files already there, prints Drive links.
- New sessions pick up env vars. Never print the secret or URL.
