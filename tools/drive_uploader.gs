/**
 * SaaSSuite content engine → Google Drive uploader (Apps Script web app).
 * Lives in Andrew's Google account. Claude's cloud machines send finished videos here and it saves them into
 * _ENGINE / 02-review / <folder path>. Large files are uploaded in pieces (Drive resumable upload).
 *
 * Setup: paste this whole file into a new Apps Script project, add a Script Property named UPLOAD_SECRET,
 * then Deploy → New deployment → Web app (Execute as: Me, Who has access: Anyone). See docs/sops/drive-uploader.md.
 */
const ROOT_FOLDER_ID = '1Q_mZBiD75hmFAzm7bux-SCvzmXxsW326'; // _ENGINE / 02-review

function doPost(e) {
  try {
    const req = JSON.parse(e.postData.contents);
    const secret = PropertiesService.getScriptProperties().getProperty('UPLOAD_SECRET');
    if (!secret || req.secret !== secret) return out({ ok: false, error: 'bad secret' });

    if (req.action === 'ping') return out({ ok: true, root: DriveApp.getFolderById(ROOT_FOLDER_ID).getName() });

    if (req.action === 'start') {               // {path:"2026-11-09 VSL finals/16x9", name, mimeType, size}
      const folder = folderFor(req.path || '');
      const existing = folder.getFilesByName(req.name);
      if (existing.hasNext() && !req.overwrite) {
        const f = existing.next();
        return out({ ok: true, skipped: true, id: f.getId(), url: f.getUrl() });
      }
      const res = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true', {
        method: 'post', contentType: 'application/json; charset=UTF-8',
        headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken(), 'X-Upload-Content-Type': req.mimeType || 'video/mp4', 'X-Upload-Content-Length': String(req.size) },
        payload: JSON.stringify({ name: req.name, parents: [folder.getId()] }), muteHttpExceptions: true
      });
      const session = res.getHeaders()['Location'] || res.getHeaders()['location'];
      if (!session) return out({ ok: false, error: 'no upload session: ' + res.getResponseCode() + ' ' + res.getContentText().slice(0, 300) });
      return out({ ok: true, session: session });
    }

    if (req.action === 'chunk') {               // {session, offset, size, data(base64)}
      const bytes = Utilities.base64Decode(req.data);
      const end = req.offset + bytes.length - 1;
      const res = UrlFetchApp.fetch(req.session, {
        method: 'put', contentType: 'application/octet-stream', payload: bytes,
        headers: { 'Content-Range': 'bytes ' + req.offset + '-' + end + '/' + req.size }, muteHttpExceptions: true
      });
      const code = res.getResponseCode();
      if (code === 308) return out({ ok: true, next: end + 1 });
      if (code === 200 || code === 201) {
        const f = JSON.parse(res.getContentText());
        return out({ ok: true, done: true, id: f.id, url: 'https://drive.google.com/file/d/' + f.id + '/view' });
      }
      return out({ ok: false, error: 'chunk failed: ' + code + ' ' + res.getContentText().slice(0, 300) });
    }
    return out({ ok: false, error: 'unknown action' });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

function folderFor(path) {
  let folder = DriveApp.getFolderById(ROOT_FOLDER_ID);
  path.split('/').map(s => s.trim()).filter(Boolean).forEach(name => {
    const it = folder.getFoldersByName(name);
    folder = it.hasNext() ? it.next() : folder.createFolder(name);
  });
  return folder;
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** Run this once from the editor (select "authorize" → Run) so Google asks for permission. */
function authorize() {
  DriveApp.getFolderById(ROOT_FOLDER_ID).getName();
  UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/about?fields=user', { headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() } });
}
