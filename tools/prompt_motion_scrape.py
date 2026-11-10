#!/usr/bin/env python3
"""Scrape prompt-motion.com (gallery of Claude-made motion videos) into the motion library.
Usage: python3 tools/prompt_motion_scrape.py OUT_DIR   -> OUT_DIR/library.json + OUT_DIR/README.md
Each entry: slug, url, title, creator, kind (prompt/skill), tags, prompt text, skill links, poster/video urls.
Credit stays with the creators; this is an internal reference library."""
import json, re, sys, time, concurrent.futures as cf
import requests

BASE = 'https://prompt-motion.com'
UA = {'User-Agent': 'Mozilla/5.0 (content-engine research)'}


def flight(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    return ''.join(json.loads('"' + c + '"') for c in chunks)


def jstr(t, key):
    m = re.search(r'"' + key + r'":"((?:[^"\\]|\\.)*)"', t)
    return json.loads('"' + m.group(1) + '"') if m else ''


def entry(slug):
    for i in range(3):
        try:
            r = requests.get(f'{BASE}/{slug}', headers=UA, timeout=30)
            if r.status_code == 200: break
        except Exception:
            pass
        time.sleep(2 ** i)
    else:
        return dict(slug=slug, error='fetch failed')
    h = r.text; t = flight(h)
    title = re.search(r'<title>(.*?)</title>', h); title = title.group(1).replace(' · Prompt Motion', '') if title else ''
    tags = re.search(r'"tags":\[(.*?)\]', t)
    prompts = [json.loads('"' + p + '"') for p in re.findall(r'"prompt":"((?:[^"\\]|\\.)*)"', t)]
    skill = [json.loads('"' + p + '"') for p in re.findall(r'"(?:skill|skillText|skillContent|markdown)":"((?:[^"\\]|\\.)*)"', t)]
    links = sorted(set(re.findall(r'https://(?:github\.com|gist\.github\.com|x\.com|twitter\.com)/[^\s"\'<>\\]+', t + h)))
    media = sorted(set(re.findall(r'https://media\.prompt-motion\.com/[^\s"\'<>\\]+', t + h)))
    creator = re.search(r'by @([A-Za-z0-9_.-]+)', h)
    return dict(slug=slug, url=f'{BASE}/{slug}', title=title, creator=creator.group(1) if creator else '',
                kind='skill' if skill or re.search(r'>Skill<', h) else 'prompt',
                tags=json.loads('[' + tags.group(1) + ']') if tags else [],
                prompt=max(prompts, key=len) if prompts else '', skill_text=max(skill, key=len) if skill else '',
                links=links, video=[m for m in media if m.endswith(('.mp4', '.webm', '.m3u8'))],
                poster=next((m for m in media if 'poster' in m), ''))


def main():
    out = sys.argv[1]
    home = requests.get(BASE + '/', headers=UA, timeout=30).text
    slugs = sorted(set(re.findall(r'href="/([a-z0-9_-]+-[0-9a-f]{6,8})"', home)))
    with cf.ThreadPoolExecutor(3) as ex:
        rows = list(ex.map(entry, slugs))
    json.dump(dict(source=BASE, scraped=time.strftime('%Y-%m-%d'), count=len(rows), entries=rows), open(f'{out}/library.json', 'w'), indent=1, ensure_ascii=False)
    tag_count = {}
    for r in rows:
        for tg in r.get('tags', []): tag_count[tg] = tag_count.get(tg, 0) + 1
    md = [f'# Prompt Motion library ({len(rows)} entries, scraped {time.strftime("%Y-%m-%d")})', '',
          'Source: https://prompt-motion.com (motion videos made with Claude, with the prompt/skill behind each). Credit belongs to each creator; internal reference only.', '',
          'Tags: ' + ', '.join(f'{k} {v}' for k, v in sorted(tag_count.items(), key=lambda x: -x[1])), '',
          '| Title | Creator | Kind | Tags | Prompt (first 160 chars) |', '|---|---|---|---|---|']
    for r in rows:
        p = (r.get('prompt') or r.get('skill_text') or '').replace('\n', ' ').replace('|', '/')[:160]
        md.append(f"| [{r.get('title','')}]({r.get('url','')}) | @{r.get('creator','')} | {r.get('kind','')} | {', '.join(r.get('tags', []))} | {p} |")
    open(f'{out}/README.md', 'w').write('\n'.join(md) + '\n')
    print(len(rows), 'entries;', sum(1 for r in rows if r.get('prompt')), 'with prompt;', sum(1 for r in rows if r.get('skill_text')), 'with skill text;', sum(1 for r in rows if r.get('error')), 'errors')


if __name__ == '__main__':
    main()
