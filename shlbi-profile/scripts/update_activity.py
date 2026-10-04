#!/usr/bin/env python3
"""Refresh the latest public default-branch commit of three curated repositories.

Only public metadata and each commit's first subject line are saved. No email
addresses, private repositories, contribution totals, or invented events.
The profile repository is never queried. An API failure leaves the last-good
snapshot unchanged and exits nonzero. Python 3.10+; no third-party packages.

  python scripts/update_activity.py              # read GitHub's API
  python scripts/update_activity.py --from-cache # redraw the checked-in snapshot
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from build_art import svg, txt, line, rect, BG, BONE, LIME, MUTED, LINE

ROOT = Path(__file__).resolve().parents[1]
REPOS = {'shlbi/graft': 'REPOT', 'shlbi/kinetic': 'Kinetic', 'shlbi/osmo': 'OSMO'}
START, END = '<!-- ACTIVITY:START -->', '<!-- ACTIVITY:END -->'


def api(path: str) -> object:
    """Fetch a known API path, with bounded retries; never log credentials."""
    if not path.startswith('/repos/'):
        raise ValueError('Only repository API paths are allowed.')
    headers = {'Accept': 'application/vnd.github+json',
               'User-Agent': 'shlbi-profile-build-pulse',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = Request('https://api.github.com' + path, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(req, timeout=25) as response:
                return json.loads(response.read(4_000_000).decode('utf-8'))
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f'GitHub API returned HTTP {exc.code} for {path}; previous snapshot preserved.') from exc
        except (URLError, TimeoutError) as exc:
            if attempt == 2:
                raise RuntimeError('GitHub API could not be reached; previous snapshot preserved.') from exc
        time.sleep(2 ** attempt)
    raise RuntimeError('GitHub API retry budget exhausted.')


def validate(data: dict) -> dict:
    if data.get('schema') != 1:
        raise ValueError('Unsupported activity snapshot schema.')
    datetime.fromisoformat(data['checked_at'].replace('Z', '+00:00'))
    records = data.get('repositories', [])
    if len(records) != len(REPOS) or {r.get('repo') for r in records} != set(REPOS):
        raise ValueError('Snapshot must contain each of the three curated repositories exactly once.')
    for record in records:
        repo = record['repo']
        if record.get('public') is not True:
            raise ValueError('Only explicitly public repositories may appear.')
        if record.get('label') != REPOS[repo]:
            raise ValueError('Unexpected repository label.')
        if not re.fullmatch(r'[a-f0-9]{40}', record['sha']):
            raise ValueError('Invalid commit SHA.')
        if record['url'] != f"https://github.com/{repo}/commit/{record['sha']}":
            raise ValueError('Unexpected commit URL.')
        datetime.fromisoformat(record['committed_at'].replace('Z', '+00:00'))
        subject = record['subject']
        if not isinstance(subject, str) or not subject or '\n' in subject or '\r' in subject or len(subject) > 500:
            raise ValueError('Invalid commit subject.')
        if not isinstance(record.get('branch'), str) or not record['branch']:
            raise ValueError('Missing default branch.')
    return data


def fetch_snapshot() -> dict:
    records = []
    for repo, label in REPOS.items():
        metadata = api(f'/repos/{repo}')
        if not isinstance(metadata, dict) or metadata.get('private') is not False or metadata.get('visibility') != 'public':
            raise ValueError(f'{repo} is not confirmed public; snapshot not updated.')
        commits = api(f'/repos/{repo}/commits?per_page=1')
        if not isinstance(commits, list) or not commits:
            raise ValueError(f'No default-branch commit returned for {repo}.')
        c = commits[0]
        subject = c['commit']['message'].splitlines()[0].strip()[:500]
        records.append({'repo': repo, 'label': label, 'public': True,
                        'branch': metadata['default_branch'], 'sha': c['sha'],
                        'subject': subject, 'committed_at': c['commit']['committer']['date'],
                        'url': c['html_url']})
    return validate({'schema': 1, 'checked_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                     'scope': 'Latest default-branch commit per featured public repository; not a personal contribution total.',
                     'repositories': records})


def short(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[:limit-1].rstrip() + '…'


def draw(data: dict, mobile: bool = False) -> str:
    w, h = (480, 486) if mobile else (960, 354)
    stamp = datetime.fromisoformat(data['checked_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M UTC')
    b = txt(28, 36, '04 / BUILD PULSE', 12, LIME, mono=True, spacing=1)
    b += txt(28, 61, 'LATEST PUBLIC REPO COMMITS', 10, MUTED, mono=True, spacing=.5)
    if not mobile:
        b += txt(932, 37, 'SNAPSHOT / NOT LIVE', 10, MUTED, mono=True, anchor='end', spacing=.6)
    b += line(28, 77, w-28, 77)
    desc = []
    for i, record in enumerate(data['repositories']):
        when = datetime.fromisoformat(record['committed_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
        sha = record['sha'][:7]
        subject = record['subject']
        desc.append(f"{record['label']}: {subject}; {when}; {sha}")
        if mobile:
            y = 117+i*111
            b += rect(28,y-10,8,8,LIME, LIME)
            b += txt(48,y,record['label'],18,BONE,700,mono=True)
            b += txt(w-28,y,f'{when} / {sha}',14,MUTED,mono=True,anchor='end')
            b += txt(28,y+31,short(subject,42),18,BONE)
            if len(subject)>42:
                b += txt(28,y+55,short(subject[41:].lstrip(),42),18,MUTED)
            b += line(28,y+76,w-28,y+76)
        else:
            y = 115+i*77
            b += txt(28,y,record['label'].upper(),15,BONE,700,mono=True,spacing=.8)
            b += f'<path d="M150 {y-5}H180L190 {y+5}H932" fill="none" stroke="{LINE}"/>'
            b += f'<circle cx="179" cy="{y-5}" r="4" fill="{LIME}"/>'
            b += txt(215,y-2,short(subject,76),16,BONE)
            b += txt(215,y+25,f"{record['repo']} / {record['branch']} / {sha}",11,MUTED,mono=True)
            b += txt(932,y+25,when,11,LIME,mono=True,anchor='end')
    b += txt(28,h-22,f'CHECKED {stamp}',10,MUTED,mono=True,spacing=.3)
    if not mobile:b += txt(932,h-22,'3 FEATURED REPOSITORIES',10,MUTED,mono=True,anchor='end',spacing=.3)
    return svg(w,h,'Build pulse — a dated snapshot of featured repository activity',b,'; '.join(desc)+'. Checked '+stamp)


def readme_block(data: dict) -> str:
    links = ' &nbsp; · &nbsp; '.join(
        f'<a href="{escape(r["url"],quote=True)}">{escape(r["label"])} <code>{r["sha"][:7]}</code> ↗</a>'
        for r in data['repositories'])
    return f'{START}\n<!-- Generated from public repository data; profile updates excluded. -->\n<sub>Inspect the commits: {links}</sub>\n{END}'


def publish(data: dict, root: Path = ROOT) -> None:
    validate(data)
    readme = root/'README.md'
    text = readme.read_text(encoding='utf-8')
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START)>text.index(END):
        raise ValueError('README must contain one correctly ordered activity marker pair.')
    begin, finish = text.index(START), text.index(END)+len(END)
    outputs = {
        root/'data/activity.json': json.dumps(data,ensure_ascii=False,indent=2)+'\n',
        root/'assets/activity.svg': draw(data),
        root/'assets/mobile/activity.svg': draw(data,True),
        readme: text[:begin]+readme_block(data)+text[finish:],
    }
    # Validate/render everything before replacing any file. Each file replacement
    # is atomic; GitHub Actions commits all changed files together afterward.
    for path, content in outputs.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-cache',action='store_true',help='Render the checked-in snapshot without network requests.')
    args=parser.parse_args()
    try:
        data = validate(json.loads((ROOT/'data/activity.json').read_text(encoding='utf-8'))) if args.from_cache else fetch_snapshot()
        publish(data)
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(f'Activity update failed: {exc}', file=sys.stderr)
        return 1
    print('Activity artwork and commit links updated from public repository data.')
    return 0

if __name__=='__main__':raise SystemExit(main())
