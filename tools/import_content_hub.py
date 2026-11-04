#!/usr/bin/env python3
"""Import Andrew's scripts from Cristian's content-hub repo into this repo.

Usage:
  git clone --depth 1 https://github.com/13cristianaguilar-bot/content-hub /tmp/content-hub
  python3 tools/import_content_hub.py /tmp/content-hub

Reads the seed SQL files (Postgres INSERTs with $$ / $tag$ quoting) and the
format vault catalog, and writes:
  content-engine/scripts/<batch>/<NN>-<slug>.md   one file per script
  content-engine/scripts/scripts.json             every script, machine-readable
  content-engine/formats/andrew-format-vault.json Andrew's entry in the vault
  content-engine/formats/hookpoint-spec.md        filming specs per format
Only rows with client_slug = 'andrew' are kept. Other clients are ignored.
"""
import json, re, sys
from pathlib import Path

COLS_RE = re.compile(r"INSERT INTO scripts\s*\(([^)]*)\)\s*VALUES", re.I)


def parse_values(sql, pos):
    """Parse a VALUES list of tuples starting at pos. Returns list of tuples."""
    rows, i, n = [], pos, len(sql)
    while i < n:
        c = sql[i]
        if c == ';':
            break
        if sql.startswith('--', i):
            i = sql.index('\n', i) if '\n' in sql[i:] else n
            continue
        if c == '(':
            row, i = parse_tuple(sql, i + 1)
            rows.append(row)
            continue
        i += 1
    return rows, i


def parse_tuple(sql, i):
    vals = []
    while True:
        while sql[i] in ' \n\r\t,':
            i += 1
        if sql.startswith('--', i):
            i = sql.index('\n', i); continue
        c = sql[i]
        if c == ')':
            return vals, i + 1
        if c == "'":
            j, buf = i + 1, []
            while True:
                if sql[j] == "'" and sql[j + 1:j + 2] == "'":
                    buf.append("'"); j += 2
                elif sql[j] == "'":
                    break
                else:
                    buf.append(sql[j]); j += 1
            vals.append(''.join(buf)); i = j + 1
        elif c == '$':
            m = re.match(r"\$([A-Za-z_]*)\$", sql[i:])
            tag = m.group(0)
            end = sql.index(tag, i + len(tag))
            vals.append(sql[i + len(tag):end]); i = end + len(tag)
        else:
            m = re.match(r"[^,)\n]+", sql[i:])
            tok = m.group(0).strip()
            vals.append(None if tok.upper() == 'NULL' else (int(tok) if tok.isdigit() else tok))
            i += len(m.group(0))


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]


def main(src):
    src = Path(src)
    out = Path(__file__).resolve().parent.parent / 'content-engine'
    scripts = []
    for f in sorted(src.glob('seed_*.sql')) + [src / 'schema.sql']:
        if not f.exists():
            continue
        sql = f.read_text()
        for m in COLS_RE.finditer(sql):
            cols = [c.strip() for c in m.group(1).split(',')]
            rows, _ = parse_values(sql, m.end())
            for r in rows:
                if len(r) != len(cols):
                    print(f'skip malformed row in {f.name}: {r[:2]}', file=sys.stderr); continue
                d = dict(zip(cols, r))
                if d.get('client_slug') == 'andrew':
                    d['source_file'] = f.name
                    scripts.append(d)

    # Apply hookpoint spec appends (format-level filming notes)
    spec = (src / 'hookpoint_spec.sql').read_text() if (src / 'hookpoint_spec.sql').exists() else ''
    specs = {}
    for m in re.finditer(r"editor_notes \|\| E'(.*?)'\s*\nWHERE client_slug = 'andrew' AND format = '([^']+)'", spec, re.S):
        text = m.group(1).encode().decode('unicode_escape').encode('latin-1').decode('utf-8')
        specs[m.group(2)] = text.replace("\\'", "'").strip()
    for s in scripts:
        if s.get('format') in specs and 'HOOKPOINT SPEC' not in (s.get('editor_notes') or ''):
            s['editor_notes'] = (s.get('editor_notes') or '') + '\n\n' + specs[s['format']]

    sdir = out / 'scripts'
    sdir.mkdir(parents=True, exist_ok=True)
    for s in scripts:
        batch = slugify((s.get('batch') or 'unbatched').split('·')[0])
        d = sdir / batch
        d.mkdir(exist_ok=True)
        num = s.get('reel_number') or 0
        p = d / f"{num:02d}-{slugify(s['title'])}.md"
        p.write_text(
            f"# {s['title']}\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Batch | {s.get('batch','')} |\n| Reel # | {num} |\n| Format | {s.get('format','')} |\n"
            f"| Status (in hub) | {s.get('status','')} |\n| Camera | {s.get('camera','')} |\n| CTA | {s.get('cta','')} |\n"
            f"| Reference clip | {s.get('reference_clip') or ''} |\n\n"
            f"## Hook\n\n{s.get('hook','')}\n\n## Script\n\n{s.get('full_script','')}\n\n"
            f"## Editor notes\n\n{s.get('editor_notes') or ''}\n")
    (sdir / 'scripts.json').write_text(json.dumps(scripts, indent=1, ensure_ascii=False))

    fdir = out / 'formats'
    fdir.mkdir(parents=True, exist_ok=True)
    cat = json.loads((src / 'format-vault/catalog.json').read_text())
    mine = [c for c in cat['clients'] if c.get('slug') == 'andrew']
    (fdir / 'andrew-format-vault.json').write_text(json.dumps(mine, indent=1, ensure_ascii=False))
    (fdir / 'hookpoint-spec.md').write_text('# Hookpoint filming spec (per format)\n\nImported from content-hub `hookpoint_spec.sql`.\n\n' +
        '\n\n'.join(f'## {k}\n\n{v}' for k, v in specs.items()) + '\n')
    print(f'{len(scripts)} Andrew scripts, {len(specs)} format specs, vault entries: {len(mine)}')


if __name__ == '__main__':
    main(sys.argv[1])
