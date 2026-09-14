#!/usr/bin/env python3
"""Extract the data tables of the UESP page Online:Scribing from a PDF print into UESP style CSVs.

Usage: python3 tools/extract_scribing_pdf.py <Online-Scribing.pdf> [data/reference/tables]
Needs pdfminer.six. Writes uesp_Online_Scribing_t00.csv (Grimoires), t01 (Focus Scripts),
t02 (Signature Scripts), t03 (Affix Scripts) and prints the tables_index.json entries.

The script tables show the compatible grimoires as icons, not text. Every icon is a 128 by 128
image and there are exactly twelve distinct ones. Rows are cut by the table's horizontal rules,
icons are assigned to the row they sit in, and the twelve icons are named by their order: inside a
row the wiki lists grimoires in its navbox order (Elemental Explosion, Mender's Bond, Shield Throw,
Smash, Traveling Knife, Vault, Wield Soul, Soul Burst, Torchbearer, Ulfsild's Contingency, Banner
Bearer, Trample). One row (Uncertainty) has two swapped, so icons are ranked by how often each
precedes the others. The naming was cross checked against the esolog ability IDs
(500 + focus script + grimoire number) for the nine grimoires that table covers.
"""
import collections, csv, hashlib, json, os, re, sys
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTImage, LTTextContainer, LTFigure, LTTextLine, LAParams, LTRect, LTLine, LTCurve

PAGE = 'Online:Scribing'
GRIMOIRE_ORDER = ['Elemental Explosion', "Mender's Bond", 'Shield Throw', 'Smash', 'Traveling Knife', 'Vault', 'Wield Soul', 'Soul Burst', 'Torchbearer', "Ulfsild's Contingency", 'Banner Bearer', 'Trample']
FOCUS = ['Bleed Damage', 'Damage Shield', 'Disease Damage', 'Dispel', 'Flame Damage', 'Frost Damage', 'Generate Ultimate', 'Healing', 'Immobilize', 'Knockback', 'Magic Damage', 'Mitigation', 'Multi-Target', 'Physical Damage', 'Poison Damage', 'Pull', 'Restore Resources', 'Shock Damage', 'Stun', 'Taunt', 'Trauma']
SIGNATURE = ["Anchorite's Cruelty", "Anchorite's Potency", "Assassin's Misery", "Cavalier's Charge", 'Class Flourish', "Crusader's Defiance", "Druid's Resurgence", "Fencer's Parry", "Gladiator's Tenacity", 'Growing Impact', "Hunter's Snare", 'Immobilizing Strike', "Knight's Valor", 'Leeching Thirst', 'Lingering Torment', "Sage's Remedy", "Thief's Swiftness", "Warmage's Defense", "Warrior's Opportunity", "Wayfarer's Mastery"]
AFFIX = ['Berserk', 'Breach', 'Brittle', 'Brutality and Sorcery', 'Courage', 'Cowardice', 'Defile', 'Empower', 'Enervation', 'Evasion', 'Expedition', 'Force', 'Heroism', 'Intellect and Endurance', 'Interrupt', 'Lifesteal', 'Magickasteal', 'Maim', 'Mangle', 'Off Balance', 'Protection', 'Resolve', 'Savagery and Prophecy', 'Uncertainty', 'Vitality', 'Vulnerability']
TABLES = [
    ('Grimoires', ['Grimoire', 'Price', 'Skill Line', 'Requirement'], GRIMOIRE_ORDER),
    ('Focus Scripts', ['Script', 'Price', 'Grimoires', 'Requirements'], FOCUS),
    ('Signature Scripts', ['Script', 'Effect', 'Price', 'Grimoires', 'Requirements'], SIGNATURE),
    ('Affix Scripts', ['Script', 'Price', 'Grimoires', 'Requirements'], AFFIX),
]
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
FOOTER = re.compile(r'^(https://en\.uesp\.net/|\d+/\d+/\d+, \d+:\d+|Page \d+ of \d+)')


def images(o):
    if isinstance(o, LTImage):
        yield o
    elif isinstance(o, LTFigure):
        for c in o:
            yield from images(c)


def bands(pdf):
    """Yield (page, top, bottom, lines, icons) for every band between two horizontal table rules."""
    for pno, page in enumerate(extract_pages(pdf, laparams=LAParams()), start=1):
        icons, lines, rules = [], [], []
        for el in page:
            for im in images(el):
                if im.srcsize == (128, 128):
                    icons.append((im.x0, im.y0, im.x1, im.y1, hashlib.md5(im.stream.get_rawdata()).hexdigest()[:6]))
            if isinstance(el, LTTextContainer):
                for ln in el:
                    if isinstance(ln, LTTextLine) and ln.get_text().strip():
                        lines.append((ln.x0, ln.y0, ln.x1, ln.y1, ln.get_text().strip()))
            if isinstance(el, (LTRect, LTLine, LTCurve)) and el.width > 200 and el.height < 3:
                rules.append(round(el.y0))
        merged = []
        for y in sorted(set(rules), reverse=True):
            if not merged or merged[-1] - y > 2:
                merged.append(y)
        for top, bot in zip(merged[:-1], merged[1:]):
            inside = lambda b: bot < (b[1] + b[3]) / 2 < top
            band_lines = sorted([l for l in lines if inside(l) and not FOOTER.match(l[4])], key=lambda l: (-round(l[3]), l[0]))
            # the last band on a page runs to the page's bottom rule: cut at the first large vertical gap
            kept = []
            for l in band_lines:
                if kept and kept[-1][3] - l[3] > 45:
                    break
                kept.append(l)
            yield pno, top, bot, kept, sorted([i for i in icons if inside(i)], key=lambda i: (-round(i[3] / 10), i[0]))


def column_bounds(all_bands, header_lines):
    """Column boundaries: cluster the x0 of every text line under this header (gap over 30pt starts a
    column); header text is centered so its own x0 would cut a wrapped cell in two."""
    ncols = len(header_lines)
    left = min(l[0] for l in header_lines) - 10
    xs = sorted(set(round(l[0]) for lines in all_bands for l in lines if l[0] >= left))
    clusters = [[xs[0]]] if xs else []
    for x in xs[1:]:
        if x - clusters[-1][-1] > 30:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    if len(clusters) != ncols:
        hx = sorted(l[0] for l in header_lines)
        return [(a + b) / 2 for a, b in zip(hx, hx[1:])]
    return [c[0] - 2 for c in clusters[1:]]


def read_tables(pdf):
    """Return {table name: [ {column: text, '_icons': [hashes]} ]} reading every band once."""
    tables = {t[0]: [] for t in TABLES}
    header = None  # (table name, [column x0 boundaries])
    last = None
    last_bot = 999  # bottom rule of the last row read; a row continues on the next page only when it ran to the page bottom
    all_bands = list(bands(pdf))
    for bi, (pno, top, bot, lines, icons) in enumerate(all_bands):
        texts = [l[4] for l in lines]
        if 'Price' in texts and ('Script' in texts or 'Grimoire' in texts):
            # data bands of this table: every following band up to the next header
            following = []
            left = min(l[0] for l in lines) - 10
            for b in all_bands[bi + 1:]:
                t2 = [l[4] for l in b[3]]
                if 'Price' in t2 and ('Script' in t2 or 'Grimoire' in t2):
                    break
                if b[3] and min(l[0] for l in b[3]) < left - 5:
                    break  # text left of the table: the table has ended
                if b[3] and abs(min(l[0] for l in b[3]) - (left + 10)) < 20:
                    following.append(b[3])  # a row of this table starts in its first column; other tables start elsewhere
            header = ('Grimoires' if 'Grimoire' in texts else 'scripts', column_bounds(following, lines))
            continue
        if not header or not lines and not icons:
            continue
        name_lines = [l[4] for l in lines if l[0] < header[1][0]]
        label = norm(' '.join(name_lines))
        table, name = None, None
        for tname, cols, names in TABLES:
            if header[0] == 'Grimoires' and tname != 'Grimoires':
                continue
            if header[0] != 'Grimoires' and tname == 'Grimoires':
                continue
            name = next((n for n in names if label.startswith(norm(n))), None)
            if name:
                table = tname
                break
        if not name:
            if last and top > 700 and last_bot < 60 and (lines or icons):
                table, name = last  # the rest of a row whose name is on the previous page
                last_bot = bot
                tables[table][-1]['_icons'].extend(i[4] for i in icons)
                for l in lines:
                    col = sum(1 for b in header[1] if l[0] >= b)
                    tables[table][-1].setdefault('_col%d' % col, []).append(l[4])
            continue
        row = {'_icons': [i[4] for i in icons], '_name': name}
        for l in lines:
            col = sum(1 for b in header[1] if l[0] >= b)
            row.setdefault('_col%d' % col, []).append(l[4])
        tables[table].append(row)
        last = (table, name)
        last_bot = bot
    return tables


def name_icons(tables):
    wins = collections.Counter()
    nodes = set()
    for rows in tables.values():
        for r in rows:
            hs = r['_icons']
            for i, a in enumerate(hs):
                for b in hs[i + 1:]:
                    wins[(a, b)] += 1
                    nodes.update([a, b])
    order = sorted(nodes, key=lambda h: -sum(wins[(h, o)] - wins[(o, h)] for o in nodes if o != h))
    if len(order) != 12:
        sys.exit(f'expected 12 distinct grimoire icons, found {len(order)}')
    against = [(r['_name'], a, b) for rows in tables.values() for r in rows for i, a in enumerate(r['_icons']) for b in r['_icons'][i + 1:] if order.index(a) > order.index(b)]
    print(f'{len(against)} icon pairs listed against the navbox order: {against}', file=sys.stderr)
    if len(against) > 3:
        sys.exit('too many rows disagree with the navbox order, check the icon naming by hand')
    return dict(zip(order, GRIMOIRE_ORDER))


def clean(parts):
    text = ' '.join(parts)
    text = re.sub(r'\s+', ' ', text).replace(' †', '†').strip()
    text = re.sub(r'(First:.*?)\s+(Later: ?)', r'\1; \2', text)
    return text


def main(pdf, outdir):
    tables = read_tables(pdf)
    for tname, cols, names in TABLES:
        got = [r['_name'] for r in tables[tname]]
        missing = [n for n in names if n not in got]
        if missing or len(got) != len(names):
            sys.exit(f'{tname}: expected {len(names)} rows, got {len(got)}, missing {missing}')
    name_of = name_icons(tables)
    print('icon hash to grimoire:', json.dumps(name_of), file=sys.stderr)
    index = []
    for ti, (tname, cols, names) in enumerate(TABLES):
        out = []
        for r in tables[tname]:
            name = r['_name']
            col0 = clean(r.get('_col0', []))
            rest = col0[len(name):].strip() if norm(col0).startswith(norm(name)) else col0
            # the name is wrapped over several lines; take the remainder after the name's words
            words = col0.split()
            k = 0
            acc = ''
            while k < len(words) and norm(acc) != norm(name):
                acc += words[k]
                k += 1
            rest = ' '.join(words[k:])
            if tname == 'Grimoires':
                out.append([name, clean(r.get('_col1', [])), clean(r.get('_col2', [])), clean(r.get('_col3', []))])
            elif tname == 'Signature Scripts':
                out.append([name, rest, clean(r.get('_col1', [])), ', '.join(name_of[h] for h in r['_icons']), clean(r.get('_col3', []))])
            else:
                out.append([name, clean(r.get('_col1', [])), ', '.join(name_of[h] for h in r['_icons']), clean(r.get('_col3', []))])
        fname = f'uesp_Online_Scribing_t{ti:02d}.csv'
        with open(os.path.join(outdir, fname), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(out)
        index.append({'source': 'uesp', 'page': PAGE, 'table': ti, 'rows': len(out), 'cols': len(cols), 'csv': fname, 'header': cols})
    json.dump(index, sys.stdout, indent=2)
    print()


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else 'data/reference/tables')
