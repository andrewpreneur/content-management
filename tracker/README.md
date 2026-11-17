# YouTube upload tracker

Problem it fixes: finished long-form edits sit in the Drive **V+S** folders and never get uploaded to YouTube.
Page: Content HQ → **YouTube uploads** tab (Not posted / Needs a check / On YouTube / Won't post, with **Mark uploaded**).

## Files
| File | What | Made by |
|---|---|---|
| `channels.json` | our YouTube channels (add new ones here) | by hand |
| `youtube_channel.json` | every video on those channels (long, Shorts, live) + upload dates | `yt_tracker.py scan` (yt-dlp, no API key; public videos only) |
| `drive_vs.json` | every video file in the V+S folders | agent with the Google Drive connector (folder list below) |
| `ai_review.json` | AI decision per Drive file: posted (+ YouTube id) / not_posted / skip, with a reason | AI review step |
| `marks.json` | Andrew/team manual marks (win over everything) | Content HQ `yt_marks` → `yt_tracker.py sync` |
| `youtube_tracker.json` | final answer per file | `yt_tracker.py match` |

## Refresh (weekly scheduled task does this)
1. `python3 tools/yt_tracker.py scan` (+ upload dates).
2. Re-list the V+S folders with the Drive connector into `drive_vs.json` (search `title contains 'V+S' or 'S+V' or 'Ready for Posting'` folders; new month folders get picked up).
3. Export Content HQ marks: ArtifactData `list` on the Content HQ url, collection `yt_marks`, out_dir `work/yt_marks` → `python3 tools/yt_tracker.py sync work/yt_marks`.
4. AI review: for every Drive file without a manual mark or an earlier AI decision, compare the file name (short codes like `AdvBuilderPt2`, `ASBrandVoice`) with the channel titles and upload dates (a video is posted after it's edited, usually within ~8 weeks). Write `ai_review.json`. When unsure, use `check`, never guess `posted`.
5. `python3 tools/yt_tracker.py match && python3 tools/yt_tracker.py hq`, then republish Content HQ with `youtube.json`.
6. Log the counts in `logs/YYYY-MM-DD.md`; tell Andrew only the new "Not posted" count.

## Limits
- yt-dlp sees public videos only. Scheduled/private/unlisted uploads show as not posted until vidIQ is linked to the channel (vidIQ → connect YouTube channel), then `vidiq_user_videos` can list them.
- The Drive connector doesn't return video lengths, so matching is by name + date + AI judgement, not length.
- Folders hold both the editor's cut and Andrew's FINAL of the same video; both get the same answer.
