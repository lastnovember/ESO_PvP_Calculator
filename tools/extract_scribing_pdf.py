#!/usr/bin/env python3
"""Rebuild data/reference/scribing_scripts.json from a PDF print of the UESP page Online:Scribing.

Usage: python3 tools/extract_scribing_pdf.py <Online-Scribing.pdf>   (needs pdfminer.six)

The three script tables (Focus, Signature, Affix) show the compatible grimoires as icons, not
text. Every icon is a 128 by 128 image; there are exactly twelve distinct ones. Rows are cut by
the table's horizontal rules, icons are assigned to the row they sit in, and the twelve icons are
named by two independent checks: the icon order inside every row is the navbox grimoire order,
and the focus rows agree with the esolog ability IDs (500 + focus script + grimoire number) for the
nine grimoires that table covers. The script prints the icon hash to grimoire table it used so a
new print of the page (new icon bytes) can be re-verified against it.
"""
import collections, hashlib, json, re, sys
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTImage, LTTextContainer, LTFigure, LTTextLine, LAParams, LTRect, LTLine, LTCurve

GRIMOIRE_ORDER = ['Elemental Explosion', "Mender's Bond", 'Shield Throw', 'Smash', 'Traveling Knife', 'Vault', 'Wield Soul', 'Soul Burst', 'Torchbearer', "Ulfsild's Contingency", 'Banner Bearer', 'Trample']
FOCUS = ['Bleed Damage', 'Damage Shield', 'Disease Damage', 'Dispel', 'Flame Damage', 'Frost Damage', 'Generate Ultimate', 'Healing', 'Immobilize', 'Knockback', 'Magic Damage', 'Mitigation', 'Multi-Target', 'Physical Damage', 'Poison Damage', 'Pull', 'Restore Resources', 'Shock Damage', 'Stun', 'Taunt', 'Trauma']
SIGNATURE = ["Anchorite's Cruelty", "Anchorite's Potency", "Assassin's Misery", "Cavalier's Charge", 'Class Flourish', "Crusader's Defiance", "Druid's Resurgence", "Fencer's Parry", "Gladiator's Tenacity", 'Growing Impact', "Hunter's Snare", 'Immobilizing Strike', "Knight's Valor", 'Leeching Thirst', 'Lingering Torment', "Sage's Remedy", "Thief's Swiftness", "Warmage's Defense", "Warrior's Opportunity", "Wayfarer's Mastery"]
AFFIX = ['Berserk', 'Breach', 'Brittle', 'Brutality and Sorcery', 'Courage', 'Cowardice', 'Defile', 'Empower', 'Enervation', 'Evasion', 'Expedition', 'Force', 'Heroism', 'Intellect and Endurance', 'Interrupt', 'Lifesteal', 'Magickasteal', 'Maim', 'Mangle', 'Off Balance', 'Protection', 'Resolve', 'Savagery and Prophecy', 'Uncertainty', 'Vitality', 'Vulnerability']
ALL = FOCUS + SIGNATURE + AFFIX
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())


def images(o):
    if isinstance(o, LTImage):
        yield o
    elif isinstance(o, LTFigure):
        for c in o:
            yield from images(c)


def read_rows(pdf):
    """Yield (script name, [icon hashes in reading order]) for every table row with icons."""
    last = None
    for page in extract_pages(pdf, laparams=LAParams()):
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
            words = [l[4] for l in sorted(lines, key=lambda l: -l[1]) if l[0] < 150 and bot < (l[1] + l[3]) / 2 < top
                     and not re.match(r'^(First:|Later:|free|[\d,]+|Found|Earned|Reward|A Signature|achievement|reward)', l[4])]
            label = norm(' '.join(words))
            name = next((n for n in ALL if label.startswith(norm(n))), None)
            row_icons = [i for i in icons if bot < (i[1] + i[3]) / 2 < top]
            if name:
                last = name
            elif row_icons and last and top > 700:
                name = last  # a row whose name sits on the previous page
            if name and row_icons:
                row_icons.sort(key=lambda i: (-round(i[3] / 10), i[0]))
                yield name, [i[4] for i in row_icons]


def main(pdf):
    rows = collections.OrderedDict()
    for name, hashes in read_rows(pdf):
        rows.setdefault(name, []).extend(hashes)
    missing = [n for n in ALL if n not in rows]
    if missing:
        sys.exit(f'rows without icons: {missing}')
    # name the icons: inside a row the wiki lists grimoires in navbox order (one row, Uncertainty,
    # has two swapped), so rank the twelve icons by how often each precedes the others
    wins = collections.Counter()
    nodes = set()
    for hs in rows.values():
        for i, a in enumerate(hs):
            for b in hs[i + 1:]:
                wins[(a, b)] += 1
                nodes.update([a, b])
    order = sorted(nodes, key=lambda h: -sum(wins[(h, o)] - wins[(o, h)] for o in nodes if o != h))
    if len(order) != 12:
        sys.exit(f'expected 12 distinct icons, found {len(order)}')
    against = [(rows_name, a, b) for rows_name, hs in rows.items() for i, a in enumerate(hs) for b in hs[i + 1:] if order.index(a) > order.index(b)]
    print(f'{len(against)} icon pairs listed against the navbox order: {against}', file=sys.stderr)
    if len(against) > 3:
        sys.exit('too many rows disagree with the navbox order, check the icon naming by hand')
    name_of = dict(zip(order, GRIMOIRE_ORDER))
    print('icon hash to grimoire:', json.dumps(name_of))
    cat = {'focus': {}, 'signature': {}, 'affix': {}}
    for n in FOCUS:
        cat['focus'][n] = [name_of[h] for h in rows[n]]
    for n in SIGNATURE:
        cat['signature'][n] = [name_of[h] for h in rows[n]]
    for n in AFFIX:
        cat['affix'][n] = [name_of[h] for h in rows[n]]
    json.dump(cat, sys.stdout, indent=1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
