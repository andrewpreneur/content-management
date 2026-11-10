/**
 * Content engine → Google Drive uploader (Apps Script web app), least-privilege version.
 *
 * SAFETY: this script only has the Google permission "drive.file" = it can see and change ONLY files and folders
 * it created itself. It cannot read, edit, share or delete any of your other Drive files. Every request must also
 * carry your secret password (Script Property UPLOAD_SECRET).
 *
 * It keeps everything inside one folder it creates, "Engine video uploads". Move that folder wherever you like
 * (e.g. into _ENGINE / 02-review); the script keeps access to it because it created it.
 * Setup steps: docs/sops/drive-uploader.md. Also paste appsscript.json (below the code in that doc) into the manifest.
 */
const API = 'https://www.googleapis.com/drive/v3/files';
const UP = 'https://www.googleapis.com/upload/drive/v3/files';

function doPost(e) {
  try {
    const req = JSON.parse(e.postData.contents);
    const secret = PropertiesService.getScriptProperties().getProperty('UPLOAD_SECRET');
    if (!secret || req.secret !== secret) return out({ ok: false, error: 'bad secret' });
    const root = rootFolder();
    if (req.action === 'ping') return out({ ok: true, root: root });

    if (req.action === 'start') {               // {path:"2026-11-09 VSL finals/16x9", name, mimeType, size}
      const parent = folderFor(root, req.path || '');
      const found = find(req.name, parent, false);
      if (found && !req.overwrite) return out({ ok: true, skipped: true, id: found, url: view(found) });
      const res = UrlFetchApp.fetch(UP + '?uploadType=resumable', {
        method: 'post', contentType: 'application/json; charset=UTF-8',
        headers: auth({ 'X-Upload-Content-Type': req.mimeType || 'video/mp4', 'X-Upload-Content-Length': String(req.size) }),
        payload: JSON.stringify({ name: req.name, parents: [parent] }), muteHttpExceptions: true
      });
      const h = res.getHeaders(); const session = h['Location'] || h['location'];
      if (!session) return out({ ok: false, error: 'no upload session: ' + res.getResponseCode() + ' ' + res.getContentText().slice(0, 300) });
      return out({ ok: true, session: session });
    }

    if (req.action === 'chunk') {               // {session, offset, size, data(base64)}
      if (String(req.session).indexOf('https://www.googleapis.com/upload/drive/') !== 0) return out({ ok: false, error: 'bad session' });
      const bytes = Utilities.base64Decode(req.data);
      const end = req.offset + bytes.length - 1;
      const res = UrlFetchApp.fetch(req.session, {
        method: 'put', contentType: 'application/octet-stream', payload: bytes,
        headers: { 'Content-Range': 'bytes ' + req.offset + '-' + end + '/' + req.size }, muteHttpExceptions: true
      });
      const code = res.getResponseCode();
      if (code === 308) return out({ ok: true, next: end + 1 });
      if (code === 200 || code === 201) { const f = JSON.parse(res.getContentText()); return out({ ok: true, done: true, id: f.id, url: view(f.id) }); }
      return out({ ok: false, error: 'chunk failed: ' + code + ' ' + res.getContentText().slice(0, 300) });
    }
    return out({ ok: false, error: 'unknown action' });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

// The one folder this script owns. Created on first use and remembered.
function rootFolder() {
  const props = PropertiesService.getScriptProperties();
  let id = props.getProperty('ROOT_ID');
  if (id) return id;
  id = create('Engine video uploads', null);
  props.setProperty('ROOT_ID', id);
  return id;
}

function folderFor(root, path) {
  let parent = root;
  path.split('/').map(s => s.trim()).filter(Boolean).forEach(name => { parent = find(name, parent, true) || create(name, parent); });
  return parent;
}

function find(name, parent, isFolder) {
  const q = "name = '" + name.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "' and '" + parent + "' in parents and trashed = false" +
            (isFolder ? " and mimeType = 'application/vnd.google-apps.folder'" : '');
  const r = JSON.parse(UrlFetchApp.fetch(API + '?fields=files(id)&q=' + encodeURIComponent(q), { headers: auth({}) }).getContentText());
  return r.files && r.files.length ? r.files[0].id : null;
}

function create(name, parent) {
  const body = { name: name, mimeType: 'application/vnd.google-apps.folder' };
  if (parent) body.parents = [parent];
  const r = UrlFetchApp.fetch(API + '?fields=id', { method: 'post', contentType: 'application/json', headers: auth({}), payload: JSON.stringify(body) });
  return JSON.parse(r.getContentText()).id;
}

function auth(h) { h.Authorization = 'Bearer ' + ScriptApp.getOAuthToken(); return h; }
function view(id) { return 'https://drive.google.com/file/d/' + id + '/view'; }
function out(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }

/** Run once from the editor: asks Google for permission and creates the "Engine video uploads" folder. */
function authorize() { Logger.log('Folder ready: https://drive.google.com/drive/folders/' + rootFolder()); }
