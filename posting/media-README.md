# Post media in Google Drive (`posting/media.json`)

Every queued post that needs a picture or video (outputs/planner/plan.json, kinds podcast_clip, reel, carousel,
single_image, text_card, story_sequence) mapped to its finished file(s) in Google Drive. Built Nov 17, 2026.

`media.json`: `{"<itemId>": {"files": [{driveId, name, mimeType, sizeBytes}], "status": "in_drive" | "uploaded" | "missing", "note"}}`.
File order = posting order (carousel slides 01, 02, ...; story frames 1-4). One video per video item.
`tools/export_convex.py` copies the files into each planItems row as `media` (driveId, name, mimeType).

## Counts (447 unique item ids; 487 queue rows, some carousels and text cards repeat)

| Kind | in_drive | uploaded | missing | total |
|---|---|---|---|---|
| podcast_clip | 10 | 270 | 0 | 280 |
| reel | 8 | 0 | 0 | 8 |
| carousel | 2 | 65 | 10 | 77 |
| single_image | 0 | 28 | 0 | 28 |
| text_card | 0 | 34 | 6 | 40 |
| story_sequence | 0 | 14 | 0 | 14 |
| **all** | **20** | **411** | **16** | **447** |

768 files (3.2 GB) uploaded to `_ENGINE / 02-review` (`Engine video uploads`):
`Podcast clips V1-V7/<clip>/`, `Carousel formats/<clip>/<format>/`, `2026-11-07-catalog/{carousels,singles,stories}/...`,
`2026-11-04-*/.../carousel/`, `content-bank/<n>/carousel/`. Nothing was shared, moved or deleted.

## Matching rules
- **podcast_clip**: clip id AND format must match exactly: `pod3-01` + `v4` → `pod3-01-v4.mp4`. The 10 already in Drive are the
  Nov 7 style re-renders in `02-review/2026-11-07 V8 reels/<clip>/` (newer than the Nov 5 local render). `02-review/2026-11-09 Reels v2/pod1-02-v2.mp4`
  is a reel *version 2*, not format V2, so it is ignored. The rest came from `/home/user/work/formats/<clip>/<clip>-<vN>.mp4`.
- **reel**: the item's `drive` link (editor exports, outside _ENGINE).
- **carousel**: LevelUp posts 1/2 = the ordered photo folders in _ENGINE (01, 02, ...). Clip formats = `/home/user/work/carousels/<clip>/<fmt>/slide-NN.png`.
  Catalog = the `Files:` folder. Text-pack carousels = `outputs/<run>/[<sub>/]carousel/slide-NN.png` (PDF not uploaded).
- **text_card**: slide-01 of `/home/user/work/carousels/<clip>/textcards/` (the same image as the queue thumbnail).
- **single_image**: file 1 = 1080x1350 (IG/Threads), file 2 = 1200x627 (LinkedIn).
- **story_sequence**: `<id>-story-1..4.jpg` from the catalog stories folder.

## Missing (16): nothing rendered yet
- Clip carousels: `car__pod1-01__tweet`, `car__pod2-09__tweet`, `car__pod3-12__convo`, `car__pod3-14__sticker`, `car__pod1-14__sticker`, `car__pod1-16__convo`
  → `tools/carousel_formats.py clip <clip>` (no `/home/user/work/carousels/<clip>/` folder yet).
- Text cards: `card__pod1-01__linkedin`, `card__pod1-14__threads`, `card__pod1-16__linkedin`, `card__pod2-09__threads`, `card__pod3-12__linkedin`, `card__pod3-14__linkedin`
  → same command (textcards).
- Lessons carousels: `car__pod1__lessons`, `car__pod2__lessons`, `car__pod3__lessons` → `tools/carousel_formats.py lessons podN` (pod1 has frames only).
- Hybrid: `car__pod1-05__hybrid` → `tools/carousel_formats.py hybrid pod1-05`.

## Re-run
1. Refresh `posting/drive_inventory.json` with the Google Drive MCP: `search_files` with
   `'1YW2-5GbikdJkdNHsdel58inyA-tHd3-_' in ancestors and mimeType contains 'video/'` (then `'image/'`, then everything else),
   `excludeContentSnippets: true`, `pageSize: 100`, follow `nextPageToken`; keep id, title, mimeType, fileSize, parentId.
   (Folder-only queries come back 5 per page, so folders are not listed.)
2. `python3 tools/media_map.py --upload` uploads anything local that is not in Drive yet (skips names already there; records
   ids in `posting/drive_uploads.json`) and rebuilds `media.json`. `--kind podcast_clip` / `--match 'clip__pod2'` narrow it;
   several runs can go in parallel. Without `--upload` it only rebuilds `media.json` (no network).
3. `python3 tools/export_convex.py OUT` then the content-hq import, so Your Content System sees the media.
