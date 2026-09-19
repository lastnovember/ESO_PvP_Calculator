#!/usr/bin/env python3
"""Audit every citation in constants.json, DECISIONS.md and UNKNOWNS.md against the archive.

For constants.json: every entry that carries a source is classified (table, page, patch note,
fixture, forum, user supplied, esolog, definition, unverified) and each cited file, row, note or
fixture is checked to exist. For DECISIONS.md: every bullet must name a file, row, note, fixture
or table; bullets that rest on nothing are listed. For UNKNOWNS.md: every open entry must list
the searches that were tried.

Run:  python3 tools/audit_citations.py [--all]
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, 'data', 'reference')
TABLES = os.path.join(REF, 'tables')
PAGES = os.path.join(REF, 'pages')
FORUM = os.path.join(REF, 'forum')
FIXTURES = os.path.join(ROOT, 'engine', 'tests', 'fixtures')
MANIFEST = os.path.join(ROOT, 'data', 'patch-notes', 'manifest.csv')

with open(MANIFEST, encoding='utf-8') as f:
    NOTE_SEQS = {row[0].zfill(3) for row in csv.reader(f) if row and row[0].isdigit()}
FIXTURE_IDS = {n[:3] for n in os.listdir(FIXTURES) if n.endswith('.fixture.json') and n[:3].isdigit()}
FORUM_IDS = {n.split('_')[0] for n in os.listdir(FORUM)}

CITE_TOKENS = [
    (r'tables/([\w.\-]+\.csv)', 'table'), (r'pages/([\w./\-\']+\.md)', 'page'),
    (r'patch-notes/html (\d{3})', 'note'), (r'\bnotes? (\d{3})\b', 'note'), (r'\bfixtures? (\d{3})', 'fixture'),
    (r'\bforum (\d{5,6})', 'forum'), (r'\besolog\b', 'esolog'), (r'\bsets\.csv\b', 'csv'), (r'\bskills\.csv\b', 'csv'),
    (r'\btooltip', 'user'), (r'\buser\b', 'user'), (r'\bdefinition\b', 'definition'), (r'\bSTRATEGIES\b', 'strategy'),
    (r'\bUESP (?:\w+ )?(?:page|table)', 'page'), (r'\bOnline:[A-Z]', 'page'), (r'\bpatch note', 'note'), (r'\breading', 'fixture'),
]


def check_source(src):
    """Return (classes, problems) for one source string."""
    classes, problems = set(), []
    if src == 'UNVERIFIED':
        return {'unverified'}, problems
    for m in re.finditer(r'tables/([\w.\-]+\.csv)', src):
        classes.add('table')
        if not os.path.exists(os.path.join(TABLES, m.group(1))): problems.append(f'missing table {m.group(1)}')
    for m in re.finditer(r"tables/([\w.\-]+\.csv) rows? '([^']+)'", src):
        p = os.path.join(TABLES, m.group(1))
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f: text = f.read().lower()
            key = m.group(2).split(' / ')[0].lower()
            if key not in text: problems.append(f"row '{m.group(2)}' not in {m.group(1)}")
    for m in re.finditer(r"pages/([\w./\-']+\.md)", src):
        classes.add('page')
        if not os.path.exists(os.path.join(PAGES, m.group(1))): problems.append(f'missing page {m.group(1)}')
    for m in re.finditer(r'patch-notes/html (\d{3})', src):
        classes.add('note')
        if m.group(1) not in NOTE_SEQS: problems.append(f'no patch note {m.group(1)}')
    for m in re.finditer(r'\bfixtures? (\d{3})', src, re.I):
        classes.add('fixture')
        if m.group(1) not in FIXTURE_IDS: problems.append(f'no fixture {m.group(1)}')
    for m in re.finditer(r'\bforum (\d{5,6})', src):
        classes.add('forum')
        if m.group(1) not in FORUM_IDS: problems.append(f'no forum thread {m.group(1)}')
    if re.search(r'esolog', src): classes.add('esolog')
    if re.search(r'\buser\b|tooltip|image', src): classes.add('user')
    if re.search(r'^definition', src): classes.add('definition')
    if re.search(r'\bfit\b|fitted', src): classes.add('fit')
    if not classes: classes.add('uncited')
    return classes, problems


def walk(node, path, out):
    if isinstance(node, list):
        for i, v in enumerate(node): walk(v, f'{path}[{i}]', out)
    elif isinstance(node, dict):
        if isinstance(node.get('source'), str):
            out.append((path, node['source'], node.get('verified'), node.get('value', node.get('oneHand', node.get('byQuality', '')))))
        for k, v in node.items(): walk(v, f'{path}.{k}' if path else k, out)


def audit_constants():
    with open(os.path.join(ROOT, 'engine', 'data', 'constants.json'), encoding='utf-8') as f: C = json.load(f)
    entries = []; walk(C, '', entries)
    counts = {}; rows = []
    for path, src, verified, value in entries:
        classes, problems = check_source(src)
        for c in classes: counts[c] = counts.get(c, 0) + 1
        if problems or 'uncited' in classes or 'unverified' in classes or verified is False:
            rows.append((path, sorted(classes), problems, verified, value, src))
    return len(entries), counts, rows


def audit_decisions():
    out = []
    with open(os.path.join(ROOT, 'DECISIONS.md'), encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            if not line.startswith('- '): continue
            hits = {name for pat, name in CITE_TOKENS if re.search(pat, line, re.I)}
            # app behaviour and scope lines make no game claim and need no archive citation, but must say so
            if re.search(r'no game claim|task statement', line, re.I): continue
            if not hits: out.append((n, line.strip()[:160]))
    return out


def audit_unknowns():
    out = []; section = ''; searched_col = None
    with open(os.path.join(ROOT, 'UNKNOWNS.md'), encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            if line.startswith('## '): section = line[3:].strip(); searched_col = None; continue
            cells0 = [c.strip() for c in line.strip().strip('|').split('|')] if line.startswith('| ') else []
            if 'Searched' in cells0:
                searched_col = cells0.index('Searched'); continue
            if searched_col is not None and line.startswith('| '):
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if len(cells) > searched_col and cells[searched_col] and '---' not in cells[0]: continue
            if section.startswith('Settled') or section.startswith('Missing') or section.startswith('Open gaps'): continue
            if not line.startswith('| ') or line.startswith('| ---') or line.startswith('| Item |') or line.startswith('| Constant |') or line.startswith('| Glyph |') or line.startswith('| Gap |'): continue
            if not re.search(r'[Ss]earched|grep', line): out.append((n, section, line.split('|')[1].strip()[:80]))
    return out


if __name__ == '__main__':
    total, counts, rows = audit_constants()
    print(f'constants.json: {total} sourced entries; by class: ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
    print(f'  entries to look at ({len(rows)}): unverified, uncited, or a citation that does not resolve')
    for path, classes, problems, verified, value, src in rows:
        flag = '; '.join(problems) if problems else ('uncited' if 'uncited' in classes else 'unverified')
        print(f'  - {path} = {value!s:<12} {flag}')
        if '--all' in sys.argv: print(f'      {src[:200]}')
    dec = audit_decisions()
    print(f'\nDECISIONS.md: {len(dec)} bullets cite nothing')
    for n, line in dec: print(f'  - line {n}: {line}')
    unk = audit_unknowns()
    print(f'\nUNKNOWNS.md: {len(unk)} open entries list no searches')
    for n, section, item in unk: print(f'  - line {n} [{section}]: {item}')
