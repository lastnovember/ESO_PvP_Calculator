#!/usr/bin/env python3
"""Generate engine/data/constants.json from data/reference tables.

Every entry carries a "source" naming the CSV and row it came from, or
"UNVERIFIED" with the community value that was used. UNVERIFIED entries are
also listed in UNKNOWNS.md (that file is maintained by hand; this script
prints the list so the two can be kept in step).

Run:  python3 tools/build_constants.py
"""
import re
import csv, json, os, re, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(ROOT, 'data', 'reference', 'tables')
OUT = os.path.join(ROOT, 'engine', 'data', 'constants.json')


def table(name):
    with open(os.path.join(TABLES, name), encoding='utf-8') as f:
        return list(csv.reader(f))


def src(name, row):
    return f"tables/{name} row '{row}'"


def unverified(value, note, alternatives=None):
    d = OrderedDict(value=value, source='UNVERIFIED', verified=False, note=note)
    if alternatives:
        d['alternatives'] = alternatives
    return d


def sourced(value, source, note=None):
    d = OrderedDict(value=value, source=source, verified=True)
    if note:
        d['note'] = note
    return d


def page(name, what):
    """Cite a UESP system page archived as Markdown in data/reference/pages (pages_index.csv)."""
    return f"pages/{name} ({what})"


def forum(thread, who, date, text):
    """Cite an archived forum post (data/reference/forum, forum_index.csv). Community level unless the poster maintains the data."""
    return f"forum/{thread} {who} ({date}): {text}"


def pn(seq, date, text):
    """Cite a patch note by manifest sequence and date."""
    return f"data/patch-notes/html {seq} ({date}): {text}"


PAGES = os.path.join(ROOT, 'data', 'reference', 'pages')
QUALITIES = ['white', 'green', 'blue', 'purple', 'gold']


def glyph_by_quality(page_name, gold):
    """Read the five quality rows under the Truly Superb (CP160) line of an archived UESP glyph page.

    The page tables list one value per quality, white to gold (Glyph of Prismatic Defense lists
    'Health | Magicka/ Stamina' pairs). The gold row must equal the value the engine already uses,
    so a stale page (Glyph of Bashing) cannot slip in.
    """
    path = os.path.join(PAGES, 'glyphs', page_name)
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('Truly Superb Glyph of'))
    rows = [l.strip() for l in lines[start + 1:start + 6]]
    def nums(l):
        vals = [float(x) if '.' in x else int(x) for x in re.findall(r'[0-9]+(?:\.[0-9]+)?', l)]
        return vals[0] if len(vals) == 1 else vals
    by = OrderedDict((q, nums(r)) for q, r in zip(QUALITIES, rows))
    if by['gold'] != gold:
        raise SystemExit(f'{page_name}: gold row {by["gold"]} does not match the engine value {gold}')
    return by


def nirn_rows(name):
    """CP160 row of an Online:Nirnhoned weapon table: five base damage values then five Nirnhoned values, white to gold."""
    rows = table(name)
    r = next(r for r in rows if r[0] == '160')
    return [int(x) for x in r[1:6]], [int(x) for x in r[6:11]]


def num(s):
    s = s.replace(',', '').replace('%', '').strip()
    return float(s) if '.' in s else int(s)


C = OrderedDict()
C['_meta'] = OrderedDict(
    generatedBy='tools/build_constants.py',
    level=50, championGearLevel=160, quality='gold',
    note='Values marked verified:false could not be sourced from data/reference (tables or patch notes) and are community values. See UNKNOWNS.md. The first fixture read from the game settles them. Patch note citations name the manifest sequence number and date; the newest note wins.',
    classMastery=OrderedDict(points=2, note=pn('194', '2026-06-08', 'Class Mastery: five passives per class, each costs 1 Class Mastery Point, you are limited to 2 points for the time being. Requires level 50 in all three native class lines and not actively subclassing.')),
)

# ---------------------------------------------------------------- base stats
F3 = 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points)'

C['base'] = OrderedDict(
    maxHealth=sourced(16000, page('Health.md', 'line 12: 1300 at level 1 plus 300 per level, 16000 health points at level 50; line 19 formula') + '; ' + F3 + ': 19305 = 16000 + 15 x 122 + Lunar Blessings 915 + Hero\'s Vigor 560.'),
    maxMagicka=sourced(12000, page('Magicka.md', 'line 12: 1220 at level 1 plus 220 per level, 12 000 maximum magicka at level 50; line 19 formula') + '; ' + F3 + ': 19251 = (12000 + 49 x 111 + 915 + 520) x 1.02 Magicka Controller.'),
    maxStamina=sourced(12000, page('Stamina.md', 'line 12: 1220 at level 1 plus 220 per level, 12000 points of stamina at level 50; line 19 formula') + '; ' + F3 + ': 13435 = 12000 + 915 + 520.'),
    healthRecovery=sourced(309, page('Health.md', 'line 24: a level 50 character with no other bonuses will have a health recovery of 309') + '; ' + F3 + ': 540 = 309 + Capacitor 141 + Robustness 90.', 'The 484 seen in community sources is not in the archive.'),
    magickaRecovery=sourced(514, page('Magicka.md', 'line 24: a level 50 character will have a base magicka recovery of 514 points') + '; ' + F3 + ': 909 = (514 + 141 + 90) x 1.22 (Flourish 20%, Magicka Controller 2%).'),
    staminaRecovery=sourced(514, page('Stamina.md', 'line 24: at level 50 a character will have 514 points of stamina recovery') + '; ' + F3 + ': 894 = (514 + 141 + 90) x 1.20 (Flourish).'),
    weaponDamage=sourced(1000, F3 + ', no weapon: the sheet reads Weapon Damage 1000 with no Weapon Damage source in the build.', 'Searched: tables_index.csv header "Weapon Damage" (none), pages/Weapon_Damage.md and depth/Weapon_Damage.md (no base value), data/patch-notes/text "base weapon damage", "unarmed" (none). The reading is the only source.'),
    spellDamage=sourced(1000, F3 + ', no weapon: the sheet reads Spell Damage 1000 with no Spell Damage source in the build.', 'Searched as for weaponDamage (pages/Spell_Damage.md has no base value).'),
    critChancePercent=sourced(10, page('depth/Weapon_Critical_effect.md', 'You start with a baseline 10% critical value; Critical Strike Chance% = min(100, 10 + 100 x (Critical Value / MCV))') + '; ' + page('depth/Spell_Critical_effect.md', 'same formula')),
    critDamagePercent=sourced(50, page('Critical_Damage.md', 'Critical Damage starts with a base damage increase of 50%, and is capped at 125%') + '; ' + page('depth/Weapon_Critical_effect.md', 'normally 50% of the base strike') + '; fixture 003 (naked) reads Critical Damage 40 above the base with Backstabber and medium passives off'),
    critDamageCapPercent=sourced(125, pn('111', '2021-11-15', 'Critical Damage and Healing now has a hard cap of 125%.') + '; ' + page('Critical_Damage.md', 'capped at 125%'), 'Class Mastery Above and Beyond raises the cap by 30 (patch 12.0.0 note in skills.csv: 155%).'),
    critRatingPerPercent=sourced(219, page('depth/Weapon_Critical_effect.md', 'Critical Strike Chance% = 10 + 100 x (Critical Value / MCV), MCV 21912 at CP160 (level 66): 219.12 rating per percent; 3000 rating reads 23.7%') + '; ' + pn('100', '2021-03-15', 'Critical Rating granted per set bonus to 657 (3%), down from 833 (3.8%): 219 per percent'), 'Fixtures 001 to 010 read their Weapon and Spell Critical percents with 219.'),
    resistancePerPercent=sourced(660, page('depth/Physical_Resistance.md', 'caps at 33,000 for players, which reduces all forms of martial damage taken by 50%: 33000 / 50 = 660 per percent') + '; ' + page('depth/Spell_Resistance.md', 'the same cap and percent') + '; fixtures 001 to 010 read every resistance percent on the advanced panel with 660'),
    resistanceCapRating=sourced(33000, page('depth/Physical_Resistance.md', 'It caps at 33,000 for players and 25,000 for NPCs') + '; ' + page('depth/Spell_Resistance.md', 'the same')),
    resistanceCapPercent=sourced(50, page('depth/Physical_Resistance.md', 'reduces all forms of martial damage taken by 50%') + '; ' + page('depth/Spell_Resistance.md', 'the same')),
    blockMitigationPercent=sourced(50, 'fixtures 002, 003 and 005: Block Mitigation reads 50 x (1 + Champion percent) plus one per heavy piece (52 naked, 54 with two heavy pieces, 55 with three)', 'Searched: tables_index.csv "Block" (none), pages/Combat.md Blocking section (no percent), data/patch-notes/text "block mitigation", "blocked damage" (only the 90% cap note 076). The readings are the only source.'),
    blockMitigationCapPercent=sourced(90, pn('076', '2019-08-26', 'Block mitigation now has a cap of 90%.')),
    blockCost=sourced(1750, 'fixtures 001 and 002 (Yeets-Swiftly): (1750 - 40 Tireless Guardian) x 0.91 (medium -12%, light +3%) = 1556 on the mace bar and x 0.64 more (Ice Staff) = 996 on the staff bar, both exact. The 2018 note (053, 2018-02-26) set 1730; no later note names the base, the sheet says 1750.', 'Flat reductions are subtracted from the base first, then percentage reductions (STRATEGIES.costOrder flatThenPercent); armor passives add up, a weapon passive multiplies separately (STRATEGIES.costWeaponPercent).'),
    rollDodgeCost=sourced(4040, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 3800 on the sheet with Tumbling 240 taken off first. Geared (fixture 002) reads 3248 where the additive passive model gives 3306; the percent stacking for Roll Dodge is still open.'),
    sprintCostPerSecond=sourced(500, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 460 = 500 - Sprinter 40; geared (500 - 40) x 0.93 = 428.'),
    breakFreeCost=sourced(5400, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 5180 = 5400 - Defiance 220; geared (5400 - 220) x 0.95 = 4921.'),
    bashDamageResistanceCoefficient=sourced(0.02252, 'fixtures 001, 002, 006 to 010: (sheet Bash Damage / damage percents - 120 Bashing Brutality) / average resistance reads 0.02249 to 0.02254 on all seven (003 at 0.0230 sits on a 1731 rating where rounding dominates); ' + src('esolog_skill_coefficients_t00.csv', 'Bash') + ' gives the form: <<1>> = 0.0224424 MaxResist + 0.356649 (Max Resistance, SingleTarget, Direct, R2 = 0.999978)', 'The sheet\'s Bash Damage is (flat bash bonuses + this x the average of Physical and Spell Resistance) x (1 + Physical damage done + direct damage done). The average is what fits the Breton healer (spell resistance 5214 above physical): physical alone reads 48 low, spell alone 57 high, the average within 2. With the esolog 0.0224424 every geared reading sits 2 low. Light Armor Penalties\' bash reduction does not show in the sheet number. Whether Deadly Bash and the Glyph of Bashing sit inside the damage percents is untested (the only Deadly Bash reading has 0%).'),
    bashCost=sourced(765, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 675 = 765 - Savage Defense 90; geared (765 - 90) x 0.97 = 655.'),
    movementSpeedPercent=sourced(100, src('uesp_Online_Movement_Speed_t00.csv', 'Walking'), 'Default walking speed 100%, maximum 200%.'),
    movementSpeedCapPercent=sourced(200, src('uesp_Online_Movement_Speed_t00.csv', 'Walking')),
    critResistance=sourced(1320, pn('087', '2020-06-09', 'All players will now have a baseline of 20% Critical Damage Reduction in the form of Critical Resistance, starting at level 10.'), '20% at 66 Critical Resistance per percent. Fixture 003 (naked) reads 1980 = 1320 + Resilience 660.'),
    sprintSpeedPercent=sourced(140, src('uesp_Online_Movement_Speed_t00.csv', 'Running'), 'Running (sprint) default 140%, maximum 200%.'),
    blockMoveSpeedShieldBonus=unverified(12, 'Fixture 008: Block Move Speed 54 with a shield and Battlefield Mobility against 42 without. One reading, kept as a fit. Searched: pages/Movement_Speed.md row "One Hand and Shield: Reduces the blocking speed penalty to 48/36%" (would give 64, not 54); tables_index.csv "Block" (none); data/patch-notes/text "Battlefield Mobility" (no number that fits).'),
    blockMoveSpeedPercent=sourced(42, 'fixtures 001 to 004: Block Move Speed reads 42% naked and geared without a shield', 'Searched: pages/Movement_Speed.md (blocking reduces speed, no base percent), pages/Combat.md (none), data/patch-notes/text "block" with "speed" (none). The readings are the only source.'),
    sneakSpeedPercent=sourced(60, 'fixtures 003 and 004 (naked): Sneak Speed 60%; fixture 002 with one light piece reads 62%, fixture 005 with Dark Stalker 100', 'Searched: pages/Stealth.md (penalty reductions only, no base), pages/Movement_Speed.md (Dark Stalker row only), data/patch-notes/text "sneak" with "speed" (none).'),
    sneakCost=sourced(118, 'fixtures 003 and 004 (naked, Sustaining Shadows at 50 of 50 stages): 59 = 118 x 0.5; fixtures 002, 005 and 007 (34, 55, 94) with the medium armor reductions and the stages bought', 'Searched: pages/Stealth.md and pages/Combat.md (cost reductions only, no base), tables_index.csv "Sneak" (none), data/patch-notes/text "cost of sneak", "sneak cost" (none).'),
    esoPlusBonusPercent=sourced(10, 'fixtures 001 to 004: Experience, Gold, Crafting Inspiration, Tel Var and Alliance Points all read 10% with ESO Plus Member in the active effects.'),
)

C['attributePoints'] = OrderedDict(
    total=sourced(64, page('Health.md', 'line 12: a level 50 character with all 64 stat points allocated to health will have the maximum base health of 23808') + '; task statement'),
    healthPerPoint=sourced(122, page('Health.md', 'line 12: every stat point allocated to health increases the stat by 122 points') + '; ' + page('Attributes.md', '111 points (122 points for Health)') + '; ' + F3 + ' with base 16000, and fixtures 001 and 002 seven points apart.'),
    magickaPerPoint=sourced(111, page('Magicka.md', 'line 12: every point placed into the magicka attribute will increase it by 111 points') + '; fixtures 001 and 002 (Yeets-Swiftly): 42 and 49 points with the same gear differ by 777 Max Magicka before percent bonuses, 7 x 111.'),
    staminaPerPoint=sourced(111, page('Stamina.md', 'line 12: stamina can additionally be increased by 111 points for every stat point allocated to stamina') + '; ' + page('Attributes.md', 'increase one attribute by 111 points (122 points for Health)')),
)

# ---------------------------------------------------------------- mundus
mund = table('uesp_Online_Mundus_Stones_t00.csv')
hdr = mund[0]
mundus = OrderedDict()
for row in mund[1:]:
    r = dict(zip(hdr, row))
    name = r['Stone']
    eff = r['Effect']; val = r['Value']; full = r['Full Divines armor value']
    entry = OrderedDict(effect=eff, source=src('uesp_Online_Mundus_Stones_t00.csv', name), verified=True)
    if name == 'The Steed':
        a, b = [x.strip() for x in val.split('/')]
        entry['values'] = [OrderedDict(stat='healthRecovery', value=num(a), kind='flat'),
                           OrderedDict(stat='movementSpeed', value=num(b), kind='percent')]
        entry['fullDivines'] = full
    elif val.endswith('%'):
        stat = {'The Ritual': 'healingDone', 'The Shadow': 'critDamageAndHealing'}[name]  # fixture 005: Critical Healing 25 = Dexterity 6 + Fighting Finesse 8 + The Shadow 11
        entry['values'] = [OrderedDict(stat=stat, value=num(val), kind='percent')]
        entry['fullDivines'] = full
    else:
        statmap = {
            'The Apprentice': ['spellDamage'], 'The Atronach': ['magickaRecovery'],
            'The Lady': ['physicalResistance', 'spellResistance'], 'The Lord': ['maxHealth'],
            'The Lover': ['physicalPenetration', 'spellPenetration'], 'The Mage': ['maxMagicka'],
            'The Serpent': ['staminaRecovery'], 'The Thief': ['critRating'],
            'The Tower': ['maxStamina'], 'The Warrior': ['weaponDamage'],
        }[name]
        entry['values'] = [OrderedDict(stat=s, value=num(val), kind='flat') for s in statmap]
        entry['fullDivines'] = num(full)
    mundus[name] = entry
MUNDUS_NOTES = {
    'The Apprentice': pn('048', '2017-08-28', 'The Apprentice: Increased Spell Damage to 238 from 167.'),
    'The Warrior': pn('048', '2017-08-28', 'The Warrior: Increased Weapon Damage to 238 from 167.'),
    'The Steed': pn('048', '2017-08-28', 'The Steed: Increased Health Recovery to 238 from 167.') + ' ' + pn('066', '2018-11-05', 'Increased the movement speed bonus from the Steed Mundus Stone to 10% from 5%.'),
    'The Atronach': pn('092', '2020-09-01', 'The Atronach and The Serpent: Increased the recovery bonus granted to 310, up from 238.'),
    'The Serpent': pn('092', '2020-09-01', 'The Atronach and The Serpent: Increased the recovery bonus granted to 310, up from 238.'),
    'The Lady': pn('092', '2020-09-01', 'The Lady and The Lover: Decreased the Armor and Armor Penetration granted to 2744, down from 2752.'),
    'The Lover': pn('092', '2020-09-01', 'The Lady and The Lover: Decreased the Armor and Armor Penetration granted to 2744, down from 2752.'),
    'The Lord': pn('092', '2020-09-01', 'The Lord: Decreased the Max Health granted to 2225, down from 2230.'),
    'The Mage': pn('092', '2020-09-01', 'The Mage and The Tower: Decreased the maximum resource granted to 2023, down from 2028.'),
    'The Tower': pn('092', '2020-09-01', 'The Mage and The Tower: Decreased the maximum resource granted to 2023, down from 2028.'),
    'The Ritual': pn('092', '2020-09-01', 'The Ritual: Decreased the Healing Done granted to 8%, down from 10%.'),
    'The Shadow': pn('092', '2020-09-01', 'The Shadow: Now grants 11% Critical Damage and Healing, rather than 13% Critical Damage.'),
    'The Thief': pn('140', '2023-07-25', 'Reduced the Critical Chance rating granted from The Thief Mundus Stone to 1212, down from 1333.'),
}
for k, e in mundus.items():
    e['patchNote'] = MUNDUS_NOTES[k]
C['mundus'] = OrderedDict(
    note='Values are level 50 CP160, UESP table cross checked against the newest patch note for each stone. fullDivines is the UESP figure with 7 gold Divines pieces (63.7%) and is kept as a cross check of the rounding rule. The Thief value is a critical rating.',
    divinesGoldPercent=sourced(9.1, src('uesp_Online_Mundus_Stones_t01.csv', 'Legendary')),
    stones=mundus,
)

# ---------------------------------------------------------------- traits
def gold(cells):
    return num(cells[-1])


QUALITY_KEYS = ['white', 'green', 'blue', 'purple', 'gold']  # Normal, Fine, Superior, Epic, Legendary columns


def by_quality(cells):
    return OrderedDict((k, num(c)) for k, c in zip(QUALITY_KEYS, cells[-5:]))

armor_traits = OrderedDict()
for row in table('uesp_Online_Traits_t01.csv'):
    if len(row) >= 8 and row[0] not in ('Trait', 'Normal'):
        name = row[0]; desc = row[2]; vals = row[3:8]
        v = gold(vals)
        kind = 'percent' if vals[-1].endswith('%') else 'flat'
        stat = {
            'Sturdy': 'blockCost', 'Impenetrable': 'critResistance', 'Reinforced': 'itemArmor',
            'Well-fitted': 'sprintAndRollDodgeCost', 'Training': 'experience', 'Infused': 'armorEnchantEffect',
            'Invigorating': 'allRecovery', 'Divines': 'mundusEffect', 'Nirnhoned': 'physicalAndSpellResistance',
        }[name]
        armor_traits[name] = OrderedDict(stat=stat, value=v, kind=kind, byQuality=by_quality(vals), description=desc,
                                        source=src('uesp_Online_Traits_t01.csv', name), verified=True)
# Enchanting page lists Infused armor at 20% gold, Traits page at 25%. Newer patch notes should settle it.
armor_traits['Infused']['note'] = 'tables/uesp_Online_Enchanting_t04.csv says 20% at gold; ' + pn('092', '2020-09-01', 'Infused: Increased the enchantment potency bonus to 25%, up from 20%.') + ' Newest note wins: 25%.'

weapon_traits = OrderedDict()
rows = table('uesp_Online_Traits_t00.csv')
i = 0
while i < len(rows):
    row = rows[i]
    if row and row[0] not in ('Trait', 'Normal') and len(row) >= 4:
        name = row[0]; desc = row[2]
        if row[3] == '1H':
            one = row[4:9]; two = rows[i + 1][1:6]
            i += 1
            v1, v2 = gold(one), gold(two)
            kind = 'percent' if one[-1].endswith('%') else 'flat'
            weapon_traits[name] = OrderedDict(description=desc, kind=kind, oneHand=v1, twoHand=v2,
                                             oneHandByQuality=by_quality(one), twoHandByQuality=by_quality(two),
                                             source=src('uesp_Online_Traits_t00.csv', name), verified=True)
        else:
            vals = row[3:8]
            kind = 'percent' if vals[-1].endswith('%') else 'flat'
            weapon_traits[name] = OrderedDict(description=desc, kind=kind, oneHand=gold(vals), twoHand=gold(vals),
                                             oneHandByQuality=by_quality(vals), twoHandByQuality=by_quality(vals),
                                             source=src('uesp_Online_Traits_t00.csv', name), verified=True)
    i += 1
statmap_w = {'Powered': 'healingDone', 'Charged': 'statusEffectChance', 'Precise': 'critChance',
             'Infused': 'weaponEnchantEffect', 'Defending': 'physicalAndSpellResistance', 'Training': 'experience',
             'Sharpened': 'physicalAndSpellPenetration', 'Decisive': 'ultimateChance', 'Nirnhoned': 'weaponDamageOfItem'}
for k, v in weapon_traits.items():
    v['stat'] = statmap_w[k]
weapon_traits['Precise']['note'] = pn('093', '2020-09-15', 'Precise: Reduced the Critical Chance granted to 7.2%, down from 8.6%.') + ' Two hand 7.2%, one hand 3.6%. The engine converts the percent to a rating at critRatingPerPercent (STRATEGIES.preciseTrait); the conversion factor itself is unverified.'
weapon_traits['Infused']['note'] = pn('048', '2017-08-28', 'Infused: Increased the bonus value granted to the applied enchantment to 30% from 20%, and increased the cooldown reduction to 50% from 40%.')
weapon_traits['Nirnhoned']['note'] = pn('048', '2017-08-28', 'Nirnhoned: Increased the bonus to the weapon damage to 15% from 11%.')
armor_traits['Nirnhoned']['note'] = pn('092', '2020-09-01', 'Nirnhoned: Decreased the Armor granted to 253, down from 301.')

jewelry_traits = OrderedDict()
rows = table('uesp_Online_Traits_t02.csv')
for idx, row in enumerate(rows):
    if row and row[0] not in ('Trait', 'Normal') and len(row) >= 9:
        name = row[0]; desc = row[3]; vals = row[4:9]
        entry = OrderedDict(description=desc, source=src('uesp_Online_Traits_t02.csv', name), verified=True)
        if name == 'Triune':
            second = rows[idx + 1][0:5]
            entry['values'] = [OrderedDict(stat='maxHealth', value=gold(vals), kind='flat', byQuality=by_quality(vals)),
                               OrderedDict(stat='maxMagicka', value=gold(second), kind='flat', byQuality=by_quality(second)),
                               OrderedDict(stat='maxStamina', value=gold(second), kind='flat', byQuality=by_quality(second))]
        else:
            stat = {'Healthy': 'maxHealth', 'Arcane': 'maxMagicka', 'Robust': 'maxStamina',
                    'Bloodthirsty': 'weaponAndSpellDamageVsUnder90', 'Harmony': 'synergyRestore',
                    'Infused': 'jewelryEnchantEffect', 'Protective': 'physicalAndSpellResistance',
                    'Swift': 'movementSpeed'}[name]
            kind = 'percent' if name in ('Infused', 'Swift') else 'flat'
            entry['values'] = [OrderedDict(stat=stat, value=gold(vals), kind=kind, byQuality=by_quality(vals))]
        jewelry_traits[name] = entry
jewelry_traits['Bloodthirsty']['note'] = 'Conditional on target health. Not applied to the sheet in phase 1 (target dependent).'
jewelry_traits['Harmony']['note'] = 'Combat proc. Not applied to the sheet.'

C['traits'] = OrderedDict(
    note='value, oneHand and twoHand are the gold (Legendary) column of the UESP trait tables; byQuality carries all five columns (white, green, blue, purple, gold) for the item quality toggle. Shields use armor traits.',
    armor=armor_traits, weapon=weapon_traits, jewelry=jewelry_traits,
)

# ---------------------------------------------------------------- enchants (glyphs)
C['enchants'] = OrderedDict(
    note='Truly Superb (CP160) gold glyph magnitudes. None of these are in data/reference; all are UNVERIFIED community values. Armor glyphs have a large value on head, chest, legs and shield, and a small value elsewhere.',
    armorLargeSlots=['head', 'chest', 'legs', 'shield'],
    armor=OrderedDict(
        **{'Health': OrderedDict(large=sourced(954, 'glyph table image supplied by the user, 2026-09-19 (engine/tests/fixtures/photos/table-truly-superb-glyph-of-health-by-quality.jpg): Truly Superb Glyph of Health, Repora, CP160: 734 white, 774 green, 839 blue, 882 purple, 954 gold; fixtures 009 and 010 (Dragonknight, seven Glyphs of Health): Max Health 30684 exact with 954 and 385', 'The 984 first typed from the DK tooltips (2026-09-19) was a misread; the user confirmed 954 with the table. Quality steps in enchants.glyphQualityFactor.'), byQuality=glyph_by_quality('Glyph_of_Health.md', 954), small=sourced(385, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: every other piece reads 386; the sheet sums 385 (fixture 009 exact with 385, 4 over with 386). Small glyph values truncate on the sheet and round on the tooltip: 954 x 0.4043 = 385.7.'), values=[OrderedDict(stat='maxHealth', kind='flat')]),
           'Magicka': OrderedDict(large=sourced(868, page('glyphs/Glyph_of_Magicka.md', 'Truly Superb row, CP160: 668 / 704 / 763 / 802 / 868 white to gold') + '; fixture 009 (the Prismatic Defense 434 is half of it)'), byQuality=glyph_by_quality('Glyph_of_Magicka.md', 868), small=sourced(350, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Roksa epaulets Max Magicka glyph reads 351; the sheet sums the truncated 350 (868 x 0.4043 = 350.9), as the Health and Prismatic Defense small pieces show.'), values=[OrderedDict(stat='maxMagicka', kind='flat')]),
           'Stamina': OrderedDict(large=sourced(868, page('glyphs/Glyph_of_Stamina.md', 'Truly Superb row, CP160: 668 / 704 / 763 / 802 / 868 white to gold')), byQuality=glyph_by_quality('Glyph_of_Stamina.md', 868), small=sourced(350, 'as the Magicka small piece (tooltip 351, sheet 350; the glyph pages say small pieces get 40%, the sheet shows 40.4% truncated)'), values=[OrderedDict(stat='maxStamina', kind='flat')]),
           'Prismatic Defense': OrderedDict(
               large=sourced([477, 434, 434], 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Roksa and Balorgh visages, Prismatic Defense 477 Health, 434 Magicka, 434 Stamina; pages/glyphs/Glyph_of_Prismatic_Defense.md Truly Superb row agrees'),
               byQuality=OrderedDict((q, [h, m, m]) for q, (h, m) in glyph_by_quality('Glyph_of_Prismatic_Defense.md', [477, 434]).items()),
               small=sourced([192, 175, 175], 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Balorgh epaulets, Prismatic Defense reads 193 Health, 175 Magicka, 175 Stamina; the sheet sums 192 Health (fixtures 001, 002, 005, 007 exact with 192, 4 to 5 over with 193: 477 x 0.4043 = 192.9 truncated) and 175 (fixtures 002 and 003).'),
               values=[OrderedDict(stat='maxHealth', kind='flat'), OrderedDict(stat='maxMagicka', kind='flat'), OrderedDict(stat='maxStamina', kind='flat')])}
    ),
    jewelry=OrderedDict(
        **{'Weapon Damage': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Increase_Physical_Harm.md', 174), magnitude=sourced(174, page('glyphs/Glyph_of_Increase_Physical_Harm.md', 'Truly Superb row, CP160: 134 / 141 / 153 / 160 / 174 white to gold') + '; fixtures 002, 005, 009', 'Glyph of Increase Physical Harm. Grants Weapon and Spell Damage since Update 37: data/patch-notes/html 135 (2023-03-28): Glyph of Physical Harm and Glyph of Spell Harm: These enchantments now grant Weapon and Spell Damage, rather than only Weapon or Spell Damage.'), values=[OrderedDict(stat='weaponDamage', kind='flat'), OrderedDict(stat='spellDamage', kind='flat'), OrderedDict(stat='staminaRecovery', kind='flat', magnitude=sourced(10, pn('135', '2023-03-28', 'Physical Harm glyphs now add 10 Stamina Recovery at all qualities, while Spell Harm glyphs now add 10 Magicka Recovery at all qualities.'), 'Scaled by the Infused jewelry trait like the damage part (16 on a gold Infused piece).'))]),
           'Spell Damage': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Increase_Magical_Harm.md', 174), magnitude=sourced(174, page('glyphs/Glyph_of_Increase_Magical_Harm.md', 'Truly Superb row, CP160: 134 / 141 / 153 / 160 / 174 white to gold'), 'Glyph of Increase Magical Harm. Grants Weapon and Spell Damage since Update 37 (same note as Weapon Damage).'), values=[OrderedDict(stat='weaponDamage', kind='flat'), OrderedDict(stat='spellDamage', kind='flat'), OrderedDict(stat='magickaRecovery', kind='flat', magnitude=sourced(10, pn('135', '2023-03-28', 'Physical Harm glyphs now add 10 Stamina Recovery at all qualities, while Spell Harm glyphs now add 10 Magicka Recovery at all qualities.'), 'Scaled by the Infused jewelry trait like the damage part (16 on a gold Infused piece). Fits fixtures 002 (Yeets, plain plus two Infused: 42), 007/008 (Necro, three plain: 30), 009/010 (DK, plain plus two Infused: 42) and 005/006 (Templar, plain plus one Infused: 26) to within rounding.'))]),
           'Magicka Recovery': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Magicka_Recovery.md', 169), magnitude=sourced(169, page('glyphs/Glyph_of_Magicka_Recovery.md', 'Truly Superb row, CP160: 121 / 133 / 145 / 157 / 169 white to gold')), values=[OrderedDict(stat='magickaRecovery', kind='flat')]),
           'Stamina Recovery': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Stamina_Recovery.md', 169), magnitude=sourced(169, page('glyphs/Glyph_of_Stamina_Recovery.md', 'Truly Superb row, CP160: 121 / 133 / 145 / 157 / 169 white to gold')), values=[OrderedDict(stat='staminaRecovery', kind='flat')]),
           'Health Recovery': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Health_Recovery.md', 169), magnitude=sourced(169, page('glyphs/Glyph_of_Health_Recovery.md', 'Truly Superb row, CP160: 121 / 133 / 145 / 157 / 169 white to gold')), values=[OrderedDict(stat='healthRecovery', kind='flat')]),
           'Prismatic Recovery': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Prismatic_Recovery.md', 84), magnitude=sourced(84, 'tooltip image supplied by the user, 2026-09-19 (engine/tests/fixtures/photos/tooltip-prismatic-recovery-and-reduce-skill-cost-glyphs.jpg): Truly Superb Glyph of Prismatic Recovery, minimum level CP160, Adds 84 Magicka Recovery, Adds 84 Health Recovery, Adds 84 Stamina Recovery', 'The only sheet reading with this glyph exported (Templar, fixtures 005 and 006) shows no share from the ring: its three recoveries are exact with nothing from it and 84 would read 1517, 1785 and 446 against 1411, 1785 and 415. That ring most likely carries another glyph (the same image shows Reduce Skill Cost, which has no main sheet stat); pending the user, see UNKNOWNS.md.'), values=[OrderedDict(stat='healthRecovery', kind='flat'), OrderedDict(stat='magickaRecovery', kind='flat'), OrderedDict(stat='staminaRecovery', kind='flat')]),
           'Reduce Skill Cost': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Reduce_Skill_Cost.md', 133), magnitude=sourced(133, 'tooltip image supplied by the user, 2026-09-19 (same file): Truly Superb Glyph of Reduce Skill Cost, Reduce Prismatic Cost Enchantment, Reduce Health, Magicka, and Stamina cost of abilities by 133, minimum level CP160', 'Health cost has no sheet line; the Magicka and Stamina cost reductions show in the advanced panel.'), values=[OrderedDict(stat='magickaCostReduction', kind='flat'), OrderedDict(stat='staminaCostReduction', kind='flat')]),
           'Reduce Spell Cost': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Reduce_Spell_Cost.md', 203), magnitude=sourced(203, page('glyphs/Glyph_of_Reduce_Spell_Cost.md', 'Truly Superb row, CP160: 154 / 167 / 179 / 191 / 203 white to gold')), values=[OrderedDict(stat='magickaCostReduction', kind='flat')]),
           'Reduce Feat Cost': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Reduce_Feat_Cost.md', 203), magnitude=sourced(203, page('glyphs/Glyph_of_Reduce_Feat_Cost.md', 'Truly Superb row, CP160: 154 / 167 / 179 / 191 / 203 white to gold')), values=[OrderedDict(stat='staminaCostReduction', kind='flat')]),
           'Reduce Block Cost': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Bracing.md', 203), magnitude=sourced(203, page('glyphs/Glyph_of_Bracing.md', 'Truly Superb row, CP160: 154 / 167 / 179 / 191 / 203 white to gold'), 'Glyph of Bracing (UESP), also known as Shielding.'), values=[OrderedDict(stat='blockCost', kind='flat', negative=True)]),
           'Increase Bash Damage': OrderedDict(magnitude=sourced(500, pn('087', '2020-06-09', 'Glyph of Bashing: These enchantments now increase the damage of your Bash attacks by up to 500 per CP160 Gold quality enchantment, rather than increasing the Weapon and Spell Damage of your Bash attacks by 348.'), 'pages/glyphs/Glyph_of_Bashing.md still lists the pre Greymoor 348 Weapon and Spell Damage; the patch note is newer and wins.'), values=[OrderedDict(stat='bashDamage', kind='flat')]),
           'Potion Cooldown': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Potion_Speed.md', 5), magnitude=sourced(5, page('glyphs/Glyph_of_Potion_Speed.md', 'Truly Superb row, CP160: 1 / 2 / 3 / 4 / 5 seconds; the Aspect rune alone sets it white to gold'), 'Seconds off the potion cooldown.'), values=[OrderedDict(stat='potionCooldown', kind='flat', negative=True)]),
           'Potion Boost': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Potion_Boost.md', 3.6), magnitude=sourced(3.6, page('glyphs/Glyph_of_Potion_Boost.md', 'Truly Superb row, CP160: 3.1 / 3.2 / 3.3 / 3.5 / 3.6 seconds white to gold'), 'Seconds added to potion durations.'), values=[OrderedDict(stat='potionDuration', kind='flat')]),
           'Flame Resist': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Flame_Resist.md', 3520), magnitude=sourced(3520, page('glyphs/Glyph_of_Flame_Resist.md', 'Truly Superb row, CP160: 2708 / 2857 / 3095 / 3250 / 3520 white to gold')), values=[OrderedDict(stat='flameResistance', kind='flat')]),
           'Frost Resist': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Frost_Resist.md', 3520), magnitude=sourced(3520, page('glyphs/Glyph_of_Frost_Resist.md', 'Truly Superb row, CP160: 2708 / 2857 / 3095 / 3250 / 3520 white to gold')), values=[OrderedDict(stat='frostResistance', kind='flat')]),
           'Shock Resist': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Shock_Resist.md', 3520), magnitude=sourced(3520, page('glyphs/Glyph_of_Shock_Resist.md', 'Truly Superb row, CP160: 2708 / 2857 / 3095 / 3250 / 3520 white to gold')), values=[OrderedDict(stat='shockResistance', kind='flat')]),
           'Poison Resist': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Poison_Resist.md', 3520), magnitude=sourced(3520, page('glyphs/Glyph_of_Poison_Resist.md', 'Truly Superb row, CP160: 2708 / 2857 / 3095 / 3250 / 3520 white to gold')), values=[OrderedDict(stat='poisonResistance', kind='flat')]),
           'Disease Resist': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Disease_Resist.md', 3520), magnitude=sourced(3520, page('glyphs/Glyph_of_Disease_Resist.md', 'Truly Superb row, CP160: 2708 / 2857 / 3095 / 3250 / 3520 white to gold')), values=[OrderedDict(stat='diseaseResistance', kind='flat')]),
           'Decrease Physical Harm': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Decrease_Physical_Harm.md', 927), magnitude=sourced(927, page('glyphs/Glyph_of_Decrease_Physical_Harm.md', 'Truly Superb row, CP160: 713 / 744 / 805 / 856 / 927 white to gold'), 'Adds Physical Resistance (page text).'), values=[OrderedDict(stat='physicalResistance', kind='flat')]),
           'Decrease Spell Harm': OrderedDict(byQuality=glyph_by_quality('Glyph_of_Decrease_Spell_Harm.md', 927), magnitude=sourced(927, page('glyphs/Glyph_of_Decrease_Spell_Harm.md', 'Truly Superb row, CP160: 713 / 744 / 805 / 856 / 927 white to gold'), 'Adds Spell Resistance (page text).'), values=[OrderedDict(stat='spellResistance', kind='flat')])}
    ),
    glyphQualityFactor=OrderedDict(note='Glyph value at each quality relative to gold, from the Truly Superb Glyph of Health row (734 / 774 / 839 / 882 / 954; pages/glyphs/Glyph_of_Health.md and the user\'s table image). Fallback only: every glyph that has a UESP page carries its own byQuality row read from that page; the factor covers Increase Bash Damage, whose page is stale. Read when flags.itemQuality is on and an item carries enchantQuality.', source='glyph table image supplied by the user, 2026-09-19 (engine/tests/fixtures/photos/table-truly-superb-glyph-of-health-by-quality.jpg): Truly Superb Glyph of Health, Repora, CP160: 734 white, 774 green, 839 blue, 882 purple, 954 gold', white=round(734/954, 4), green=round(774/954, 4), blue=round(839/954, 4), purple=round(882/954, 4), gold=1.0),
    glyphSmallRatio=sourced(0.4043, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010): small pieces truncate 0.4043 of the large value (954 to 385, 868 to 350, 477 to 192, 434 to 175); the glyph pages say 40%', 'Share of the large piece value a shoulders, hands, waist or feet glyph gets, truncated. Used to derive the small value at qualities below gold, which no reading has confirmed yet.'),
    weapon=OrderedDict(note='Every weapon glyph is a combat proc and has no character sheet effect. Kept for completeness.',
                       names=['Flame', 'Frost', 'Shock', 'Poison', 'Disease', 'Decrease Health', 'Absorb Health', 'Absorb Magicka', 'Absorb Stamina', 'Weapon Damage', 'Crushing', 'Weakening', 'Hardening', 'Prismatic Onslaught']),
)

# ---------------------------------------------------------------- armor and weapon item values
C['items'] = OrderedDict(
    note='Armor rating of a gold CP160 piece with no trait, and weapon damage of a gold CP160 weapon. Armor from the user\'s tooltips (2026-09-19): slot factors chest 1.0, head shoulders legs feet 0.875, hands 0.5, waist 0.375. Medium and light chests and the small heavy and medium pieces are derived from those factors.',
    qualityFactor=OrderedDict(
        gold=sourced(1.0, 'definition: ratings are stated for gold (Legendary) CP160 items'),
        purple=unverified(0.96, 'Armor rating of a purple (Epic) CP160 piece relative to gold. Community steps of about 4% per quality; a purple armor piece reading settles it. Weapons no longer use this: items.weaponDamageByQuality holds the Nirnhoned page rows. Searched: tables_index.csv "Armor" (uesp_Online_Armor_t01 is the trait table), pages/Armor.md (no ratings), pages/depth/Rubedite_Ore.md and Rubedo_Leather.md and Ancestor_Silk.md tables (ingot counts, not ratings), data/patch-notes/text "armor rating" (none by quality).', [0.95]),
        blue=unverified(0.92, 'Blue (Superior) relative to gold, see purple.', [0.90]),
        green=unverified(0.88, 'Green (Fine) relative to gold, see purple.'),
        white=unverified(0.84, 'White (Normal) relative to gold, see purple.'),
    ),
    # Slot factors from the tooltips: big pieces (head, shoulders, legs, feet) 0.875 of the chest, hands 0.5, waist 0.375
    # (light 1221 / 698 / 523 all sit on a 1395.4 chest). Tooltips truncate: a Reinforced medium big piece reads 2114 =
    # 1823 x 1.16 (2114.68) and the Reinforced heavy chest 3215 = 2772 x 1.16 (3215.5).
    armor=OrderedDict(
        heavy=OrderedDict(
            head=sourced(2425, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Bloodspawn, Roksa and Balorgh visages, Reinforced, all 2813 = 2425 x 1.16'),
            shoulders=sourced(2425, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010): the heavy big pieces read 2425 (Reinforced 2813 = 2425 x 1.16); slot factor 0.875 of the chest like the head'),
            chest=sourced(2772, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Cuirass of the Trainee, Reinforced, 3215 = 2772 x 1.16 (3215.5 truncated)'),
            hands=unverified(1386, 'heavy hands, 0.5 of the chest like the light hands (698 of 1395.4)'),
            waist=unverified(1039, 'heavy waist, 0.375 of the chest like the light waist (523 of 1396.3), truncated: 1039.6'),
            legs=sourced(2425, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010): heavy big pieces 2425, see head'), feet=sourced(2425, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010): heavy big pieces 2425, see head')),
        medium=OrderedDict(
            head=sourced(1823, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Bloodspawn Mask, Reinforced, 2114 = 1823 x 1.16 truncated; Bloodspawn epaulets (Impenetrable) 1823'),
            shoulders=sourced(1823, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Bloodspawn shoulders, medium, Impenetrable: 1823'),
            chest=unverified(2084, 'medium chest: the big pieces read 1823 = trunc(0.875 x chest), so the chest is 2083.4 to 2084.6; the weights step by 688 (light 1396.3, medium 2084.3, heavy 2772.3) so 2084. No medium chest read yet.'),
            hands=unverified(1042, 'medium hands, trunc(0.5 x 2084.3)'),
            waist=unverified(781, 'medium waist, trunc(0.375 x 2084.3)'),
            legs=sourced(1823, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Guards of Essence Thief, Reinforced, 2114 = 1823 x 1.16 truncated'),
            feet=sourced(1823, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Boots of Essence Thief, Reinforced, 2114 = 1823 x 1.16 truncated')),
        light=OrderedDict(
            head=sourced(1221, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010): light big pieces 1221, same slot factor as the shoulders'),
            shoulders=sourced(1221, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Balorgh and Roksa epaulets, light, Impenetrable: 1221'),
            chest=unverified(1396, 'light chest: 1221 = trunc(0.875 x chest), 698 = trunc(0.5 x chest) and 523 = trunc(0.375 x chest) together put the chest in 1396.0 to 1396.6. No light chest read yet.'),
            hands=sourced(698, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Gloves of Rallying Cry, light, Divines: 698'),
            waist=sourced(523, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Belt of Rallying Cry, light, Divines: 523'),
            legs=sourced(1221, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Breeches of Rallying Cry, light, Impenetrable: 1221'),
            feet=sourced(1221, 'user, 2026-09-19, gold CP160 tooltips on the Dragonknight (fixtures 009 and 010) and its inventory: Shoes of Vicious Death, light, Impenetrable: 1221')),
    ),
    shieldArmor=sourced(1720, 'fixture 008 (Z antilles): back bar with a Reinforced shield reads 24166 against 22171 on the staff bar, 1995 = 1720 x 1.16.'),
    weaponDamage=sourced(1335, page('Nirnhoned.md', 'One-Handed and Ranged table, CP160 row: 1335 base, 1535 Nirnhoned') + '; fixtures 002, 005, 006, 009, 010 (staves and one handed weapons read exactly with it)', 'Damage rating of a gold CP160 one handed weapon, bow or staff. Applies to Weapon Damage and Spell Damage on the sheet.'),
    twoHandedMeleeWeaponDamage=sourced(1571, page('Nirnhoned.md', 'Two-Handed table, CP160 row: 1571 base, 1806 Nirnhoned') + '; ' + forum('348673', 'Reorx_Holybeard', '2017-05-31', '2H = 1571'), 'Greatsword, battle axe and maul. No reading on file carries one yet.'),
    dualWieldOffHandInherentPercent=sourced(17.67, forum('348673', 'Reorx_Holybeard', '2017-05-31', 'DW = 1335 + 1335*0.177 = 1571, DW + Dual Wield Expert 2 = 1571 + 1335*0.06 = 1651') + '; fixtures 002, 005 and 009 (17.67 + 6 = 23.67 lands all three within 1, the forum 17.7 misses two by 1)', 'Share of the off hand weapon rating (trait included) the sheet adds while dual wielding before Dual Wield Expert. With the passive the off hand reaches 23.67%, and two maces equal a two handed weapon (1571) before the passive.'),
    twoHandedTypes=['greatsword', 'battle axe', 'maul', 'bow', 'inferno staff', 'lightning staff', 'ice staff', 'restoration staff'],
    weaponDamageByQuality=OrderedDict(
        note='Damage rating of a CP160 weapon at each quality, white to gold, base and Nirnhoned, from the Online:Nirnhoned page tables (CP160 row). One handed covers axes, maces, swords, daggers, bows and staves (the page\'s One-Handed and Ranged table); two handed covers greatswords, battle axes and mauls. Read when flags.itemQuality is on; gold agrees with items.weaponDamage and items.twoHandedMeleeWeaponDamage.',
        oneHanded=OrderedDict(source=src('uesp_Online_Nirnhoned_t01.csv', '160') + ' (columns Normal Fine Superior Epic Legendary, Base Damage then Nirnhoned Damage)', verified=True,
                              base=OrderedDict(zip(['white', 'green', 'blue', 'purple', 'gold'], nirn_rows('uesp_Online_Nirnhoned_t01.csv')[0])),
                              nirnhoned=OrderedDict(zip(['white', 'green', 'blue', 'purple', 'gold'], nirn_rows('uesp_Online_Nirnhoned_t01.csv')[1]))),
        twoHanded=OrderedDict(source=src('uesp_Online_Nirnhoned_t02.csv', '160') + ' (columns Normal Fine Superior Epic Legendary, Base Damage then Nirnhoned Damage)', verified=True,
                              base=OrderedDict(zip(['white', 'green', 'blue', 'purple', 'gold'], nirn_rows('uesp_Online_Nirnhoned_t02.csv')[0])),
                              nirnhoned=OrderedDict(zip(['white', 'green', 'blue', 'purple', 'gold'], nirn_rows('uesp_Online_Nirnhoned_t02.csv')[1]))),
    ),
    twoHandedSetPieces=sourced(2, page('Weapon_Sets.md', 'most of these sets consist only of a single two-handed weapon, so only one item is needed to receive the full bonus') + '; sets.csv settype Weapon rows hold their bonus in bonus_2 (2 items); task statement', 'A two handed weapon counts as two set pieces.'),
)

# ---------------------------------------------------------------- foods
def food(id_, name, kind, note, verified=False, source='UNVERIFIED', **stats):
    d = OrderedDict(id=id_, name=name, kind=kind, stats=OrderedDict(stats), source=source, verified=verified, note=note)
    return d

foods = [
    food('green-health', 'Green single stat food (Max Health)', 'food', 'UESP scaling table last column read as CP160. Column alignment in that table is suspect.', True, src('uesp_Online_Food_t03.csv', 'Health') + ', last level column', maxHealth=6277),
    food('green-magicka', 'Green single stat food (Max Magicka)', 'food', 'UESP scaling table last column read as CP160.', True, src('uesp_Online_Food_t02.csv', 'Health') + ', last level column (Max Magicka)', maxMagicka=5745),
    food('green-stamina', 'Green single stat food (Max Stamina)', 'food', 'UESP scaling table last column read as CP160.', True, src('uesp_Online_Food_t02.csv', 'Health') + ', last level column (Max Stamina, the same single stat table)', maxStamina=5745),
    food('blue-health-magicka', 'Blue dual stat food (Health and Magicka)', 'food', 'UESP scaling table. Community tooltips are often quoted as 5395 and 4936; listed in UNKNOWNS.md.', True, src('uesp_Online_Food_t07.csv', 'Health') + ', last level column', maxHealth=5000, maxMagicka=4575),
    food('blue-health-stamina', 'Blue dual stat food (Health and Stamina)', 'food', 'UESP scaling table.', True, src('uesp_Online_Food_t08.csv', 'Health') + ', last level column', maxHealth=5000, maxStamina=4575),
    food('blue-magicka-stamina', 'Blue dual stat food (Magicka and Stamina)', 'food', 'UESP scaling table.', True, src('uesp_Online_Food_t09.csv', 'Magicka') + ', last level column', maxMagicka=4575, maxStamina=4575),
    food('purple-tristat', 'Purple tri stat food (Longfin Pasty, Braised Rabbit, Sugar Skulls without recovery)', 'food', 'Community tooltip value.', maxHealth=4620, maxMagicka=4250, maxStamina=4250),
    food('bewitched-sugar-skulls', 'Bewitched Sugar Skulls', 'food', 'Community tooltip value.', maxHealth=4620, maxMagicka=4250, maxStamina=4250, healthRecovery=406),
    food('artaeum-takeaway-broth', 'Artaeum Takeaway Broth', 'food', 'Community tooltip value. ' + pn('073', '2019-06-03', 'Reduced the Max Health and Max Resource granted by these foods by approximately 15%, recovery slightly increased.'), maxHealth=3724, maxStamina=3458, healthRecovery=406, staminaRecovery=406),
    food('clockwork-citrus-filet', 'Clockwork Citrus Filet', 'food', 'Community tooltip value. ' + pn('073', '2019-06-03', 'Reduced the Max Health and Max Resource granted by these foods by approximately 15%, recovery slightly increased.'), maxHealth=3724, maxMagicka=3458, healthRecovery=406, magickaRecovery=406),
    food('candied-jesters-coins', "Candied Jester's Coins", 'food', 'Community tooltip value. Same as blue Health and Stamina food.', maxHealth=5000, maxStamina=4575),
    food('witchmothers-potent-brew', "Witchmother's Potent Brew", 'drink', 'Community tooltip value.', maxHealth=2856, maxMagicka=3161, magickaRecovery=315),
    food('dubious-camoran-throne', 'Dubious Camoran Throne', 'drink', 'Community tooltip value.', maxHealth=2856, maxStamina=3161, staminaRecovery=315),
    food('jewels-of-misrule', 'Jewels of Misrule', 'drink', 'Community tooltip value.', maxHealth=3326, healthRecovery=315, magickaRecovery=315, staminaRecovery=315),
    food('lava-foot-soup-and-saltrice', 'Lava Foot Soup-and-Saltrice', 'drink', 'Community tooltip value.', maxStamina=3080, staminaRecovery=338),
    food('orzorgas-smoked-bear-haunch', "Orzorga's Smoked Bear Haunch", 'drink', 'Fitted from fixtures 002 and 003 (geared minus naked, same character): Max Health 4316 with Prismatic small pieces at 192, Health Recovery 406 (1022 = (309 + 141 + 90 + 406) x 1.08). Magicka and Stamina Recovery fit 411 and 369 with the assumed Evocation and Wind Walker percents, so 406 is used for all three and the in game tooltip is wanted.', maxHealth=4316, healthRecovery=406, magickaRecovery=406, staminaRecovery=406),
    food('ghastly-eye-bowl', 'Ghastly Eye Bowl', 'drink', 'Community tooltip value.', maxMagicka=3080, magickaRecovery=338),
    food('green-drink-magicka-recovery', 'Green single recovery drink (Magicka Recovery)', 'drink', 'Crown Star-Magic Tea description on UESP Drinks page, era of the text unknown.', True, src('uesp_Online_Drinks_t06.csv', 'Crown Star-Magic Tea'), magickaRecovery=565),
    food('green-drink-stamina-recovery', 'Green single recovery drink (Stamina Recovery)', 'drink', 'Crown Endurance Tonic description on UESP Drinks page.', True, src('uesp_Online_Drinks_t06.csv', 'Crown Endurance Tonic'), staminaRecovery=565),
    food('green-drink-health-recovery', 'Green single recovery drink (Health Recovery)', 'drink', 'Crown Health Vigor Liquor description on UESP Drinks page.', True, src('uesp_Online_Drinks_t06.csv', 'Crown Health Vigor Liquor'), healthRecovery=621),
    food('blue-drink-health-stamina-recovery', 'Blue dual recovery drink (Health and Stamina Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t03.csv', 'Health') + ', last level column', healthRecovery=500, staminaRecovery=457),
    food('blue-drink-health-magicka-recovery', 'Blue dual recovery drink (Health and Magicka Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t04.csv', 'Health') + ', last level column', healthRecovery=500, magickaRecovery=457),
    food('blue-drink-magicka-stamina-recovery', 'Blue dual recovery drink (Magicka and Stamina Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t05.csv', 'Magicka') + ', last level column', magickaRecovery=457, staminaRecovery=457),
    food('purple-tri-recovery-drink', 'Purple tri recovery drink', 'drink', 'Crown Refreshing Drink description on UESP Drinks page.', True, src('uesp_Online_Drinks_t06.csv', 'Crown Refreshing Drink'), healthRecovery=446, magickaRecovery=410, staminaRecovery=410),
]
# Food buffs in the esolog coefficient table are listed at a lower level; the CP160 gold values are
# the table values times 1.1735 (Bewitched Sugar Skulls 3937/3622/393 in the table against the
# known 4620/4250/462; Smoked Bear Haunch 3675/346/315 against the fixture fit 4316/406/369).
# Magicka and Stamina values are truncated, not rounded: Bear Haunch recovery is 369 (315 x 1.1735 = 369.65).
# Fixtures 001 and 002 (Yeets, same jewelry, Magicka Controller only on the front bar) read 1433 = 1156 x 1.24
# and 1457 = 1156 x 1.26, which pins the pre-percent total at 1156 = 514 + 141 + 90 + 42 + 369; with 370 the
# back bar would read 1434. Health values keep rounding (4316, 4624, 406 and 462 all need it).
FOOD_SCALE = 1.1735
# Health values scale a touch higher than Magicka and Stamina ones: Bear Haunch Max Health 4316 (fixtures 002 and 005)
# over the esolog 3675 is 1.17442, and Sugar Skulls Max Health 4624 (fixture 009: 30684) is 3937 x 1.17442, while
# Sugar Skulls Max Magicka and Stamina read 4250 = 3622 x 1.1735 (fixture 009 exact). Health Recovery lands on the
# same number either way (406, 462).
FOOD_SCALE_HEALTH = 4316 / 3675
ESOLOG_FOODS = {
    'orzorgas-smoked-bear-haunch': ("Orzorga's Smoked Bear Haunch", 'drink', 'Smoked Bear Haunch', {1: ['maxHealth'], 2: ['healthRecovery'], 3: ['magickaRecovery', 'staminaRecovery']}),
    'bewitched-sugar-skulls': ('Bewitched Sugar Skulls', 'food', 'Bewitched Sugar Skulls', {1: ['maxHealth'], 2: ['maxStamina', 'maxMagicka'], 3: ['healthRecovery']}),
    'artaeum-takeaway-broth': ('Artaeum Takeaway Broth', 'food', 'Artaeum Takeaway Broth', {1: ['maxHealth'], 2: ['healthRecovery'], 3: ['maxStamina'], 4: ['staminaRecovery']}),
    'clockwork-citrus-filet': ('Clockwork Citrus Filet', 'food', 'Clockwork Citrus Filet', {1: ['maxHealth'], 2: ['healthRecovery'], 3: ['maxMagicka'], 4: ['magickaRecovery']}),
    'dubious-camoran-throne': ('Dubious Camoran Throne', 'drink', 'Dubious Camoran Throne', {1: ['staminaRecovery'], 2: ['maxStamina'], 3: ['maxHealth']}),
    'witchmothers-potent-brew': ("Witchmother's Potent Brew", 'drink', "Witchmother's Potent Brew", {1: ['magickaRecovery'], 2: ['maxMagicka'], 3: ['maxHealth']}),
    'jewels-of-misrule': ('Jewels of Misrule', 'drink', 'Jewels of Misrule', {1: ['staminaRecovery', 'magickaRecovery'], 2: ['maxHealth']}),
    'lava-foot-soup-and-saltrice': ('Lava Foot Soup-and-Saltrice', 'drink', 'Lava Foot Soup & Saltrice', {1: ['maxStamina'], 2: ['staminaRecovery']}),
    'mud-ball': ('Mud Ball', 'food', 'Mud Ball', {1: ['maxMagicka', 'maxStamina']}),
    'candied-jesters-coins': ("Candied Jester's Coins", 'food', "Candied Jester's Coins", {1: ['maxStamina'], 2: ['magickaRecovery']}),
    'ghastly-eye-bowl': ('Ghastly Eye Bowl', 'drink', 'Witchfest Food: Max M, Reg M,', {1: ['maxMagicka'], 2: ['magickaRecovery']}),
    'purple-tristat': ('Purple tri stat food (Longfin Pasty, Braised Rabbit, Sugar Skulls without recovery)', 'food', 'Bewitched Sugar Skulls', {1: ['maxHealth'], 2: ['maxStamina', 'maxMagicka']}),
    'witchmothers-party-punch': ("Witchmother's Party Punch", 'drink', "Witchmother's Party Punch", {1: ['magickaRecovery', 'staminaRecovery'], 2: ['healthRecovery']}),
}
def esolog_food(id_):
    name, kind, buff, slots = ESOLOG_FOODS[id_]
    rows = [r for r in table('esolog_skill_coefficients_t00.csv') if r and r[0].strip() == buff]
    row = rows[0]
    consts = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r'<<(\d+)>> = ([\d.]+) \(Constant\)', row[8])}
    stats = OrderedDict()
    for n, keys in slots.items():
        for k in keys:
            stats[k] = int(round(consts[n] * FOOD_SCALE_HEALTH)) if k in ('maxHealth', 'healthRecovery') else int(consts[n] * FOOD_SCALE)
    return food(id_, name, kind, f'esolog buff "{buff}" ({row[7].strip()}) x {FOOD_SCALE} for CP160 gold.', True, src('esolog_skill_coefficients_t00.csv', buff), **stats)
foods = [f for f in foods if f['id'] not in ESOLOG_FOODS] + [esolog_food(i) for i in ESOLOG_FOODS]
C['foods'] = OrderedDict(note='Food and drink catalog. The app also accepts custom values typed from a tooltip. Racial food duration passives do not change magnitudes.', items=foods)

# ---------------------------------------------------------------- Battle Spirit
bs = table('uesp_Online_Campaigns_t05.csv')[1]
# ---------------------------------------------------------------- set bonuses by quality
def craftable_quality_row(table_name, caption):
    """CP160 row of an Online:Craftable Sets quality table: Normal, Fine, Superior, Epic, Legendary."""
    rows = table(table_name)
    assert rows[1][0] == caption, (table_name, rows[1])
    r = next(r for r in rows if r[0] == '160')
    return OrderedDict(zip(['white', 'green', 'blue', 'purple', 'gold'], [int(x) for x in r[1:6]]))


def set_bonus_type(key, table_name, caption, stats):
    by = craftable_quality_row(table_name, caption)
    return OrderedDict(
        stats=stats,
        source=f"tables/{table_name} row '160' (caption '{caption}', columns Normal Fine Superior Epic Legendary; page Online:Craftable Sets: bonus ranges depend on item level and quality)",
        verified=True,
        byQuality=by,
        multiplier=OrderedDict((q, round(v / by['gold'], 4)) for q, v in by.items()),
    )


C['sets'] = OrderedDict(
    note='Flat set bonus magnitudes at CP160 by item quality, from the six Online:Craftable Sets quality tables. A range like "6-300" runs from level 1 white to CP160 gold, so sets.csv resolves to the gold value; below gold the engine multiplies a ranged flat bonus by multiplier[quality] of its type. Types with no table (Offensive Penetration, Critical Resistance) are not scaled, see UNKNOWNS.md. Which piece sets the quality of a mixed set is STRATEGIES.setBonusQuality (unverified).',
    bonusByQuality=OrderedDict([
        ('recovery', set_bonus_type('recovery', 'uesp_Online_Craftable_Sets_t03.csv', 'Health / Magicka / Stamina Recovery', ['healthRecovery', 'magickaRecovery', 'staminaRecovery', 'allRecovery'])),
        ('maxMagickaOrStamina', set_bonus_type('maxMagickaOrStamina', 'uesp_Online_Craftable_Sets_t04.csv', 'Max Magicka / Stamina', ['maxMagicka', 'maxStamina'])),
        ('maxHealth', set_bonus_type('maxHealth', 'uesp_Online_Craftable_Sets_t05.csv', 'Max Health', ['maxHealth'])),
        ('weaponAndSpellDamage', set_bonus_type('weaponAndSpellDamage', 'uesp_Online_Craftable_Sets_t06.csv', 'Spell / Weapon Damage', ['weaponDamage', 'spellDamage', 'weaponAndSpellDamage'])),
        ('critRating', set_bonus_type('critRating', 'uesp_Online_Craftable_Sets_t07.csv', 'Spell / Weapon Critical', ['critRating', 'weaponCritRating', 'spellCritRating'])),
        ('resistance', set_bonus_type('resistance', 'uesp_Online_Craftable_Sets_t08.csv', 'Spell / Physical Resistance', ['armor', 'physicalResistance', 'spellResistance', 'physicalAndSpellResistance'])),
    ]),
)

C['battleSpirit'] = OrderedDict(
    source=src('uesp_Online_Campaigns_t05.csv', 'Battle Spirit'),
    rawText=bs[2],
    effects=[
        OrderedDict(stat='damageTaken', value=-50, kind='percent', verified=True, source=pn('108', '2021-09-07', 'Increased the damage taken reduction from the Battle Spirit passive to 50%, up from 44%.')),
        OrderedDict(stat='damageShieldStrength', value=-50, kind='percent', verified=True, source=pn('007', '2015-09-14', '50% less damage shield strength.') + ' No later change found.'),
        OrderedDict(stat='healingReceived', value=-55, kind='percent', verified=True, source=pn('108', '2021-09-07', 'Increased the healing received penalty to 55%, up from 50%.') + ' Timeline: 50% (007, 2015-09-14), 60%, 55% (096, 2020-11-09), 50%, 55% (108).'),
        OrderedDict(stat='healthRecovery', value=-50, kind='percent', verified=True, source=pn('103', '2021-06-08', 'The Battle Spirit passive now also reduces your Health Recovery by 50%.')),
        OrderedDict(stat='abilityRangeOver28m', value=8, kind='flat', verified=True, source=src('uesp_Online_Campaigns_t05.csv', 'Battle Spirit') + '; ' + pn('103', '2021-06-08', 'known issue: abilities with a range of 28m or more are not receiving the Battle Spirit range increase buff')),
    ],
    legacyFlatMaxHealth=sourced(1600, 'Not applied unless flags.battleSpiritFlatHealth is true: fixture 007 (Cyrodiil) reads 33289, exactly the engine without it. Earlier reading: fixtures 001 and 002 (Yeets-Swiftly): same gear, 22 Health points in Cyrodiil read 32701 and 15 points outside read 30001; 7 points are 7 x 122 x 1.10, the rest is 1600 x 1.10, so Battle Spirit adds 1600 Max Health before percent bonuses. Older notes said 5000: ' + pn('017', '2016-03-22', 'fixed: Battle Spirit Health bonus would not be modified by Health percentage increases.') + ' ' + pn('076', '2019-08-26', 'Pets will now properly gain the extra 5000 Health from Battle Spirit.') + ' No note carries the change to 1600.', 'Applied whenever Battle Spirit is on unless flags.battleSpiritFlatHealth is false.'),
)

# ---------------------------------------------------------------- Cyrodiil campaign bonuses (Battle Spirit on)
def _bonus_rows(fname):
    return [(r[1].strip(), r[2].strip()) for r in table(fname)[1:] if len(r) > 2 and r[1].strip()]
_keep = _bonus_rows('uesp_Online_Campaigns_t06.csv')
_scroll = _bonus_rows('uesp_Online_Campaigns_t07.csv')
_emp = _bonus_rows('uesp_Online_Campaigns_t08.csv')
def _pct(text, pat):
    m = re.search(pat, text)
    return float(m.group(1)) if m else None
C['cyrodiil'] = OrderedDict(
    note='Campaign bonuses shown on the sheet under Battle Spirit (flags.cyrodiil). Values from the UESP Campaigns page; how the flats and percents combine with the rest of the sheet is unverified until a reading carries one.',
    enemyKeepCritPercent=OrderedDict(
        source=src('uesp_Online_Campaigns_t06.csv', 'Enemy Keep Bonus I') + " to 'Enemy Keep Bonus IX'", verified=True,
        values=[_pct(e, r'Critical by (\d+)%') for n, e in _keep if n.startswith('Enemy Keep Bonus')]),
    offensiveScrollDamagePercent=OrderedDict(
        source=src('uesp_Online_Campaigns_t07.csv', 'Offensive Scroll Bonus I') + " and 'Offensive Scroll Bonus II'", verified=True,
        values=[_pct(e, r'by (\d+)%') for n, e in _scroll if n.startswith('Offensive')]),
    defensiveScrollResistancePercent=OrderedDict(
        source=src('uesp_Online_Campaigns_t07.csv', 'Defensive Scroll Bonus I') + " and 'Defensive Scroll Bonus II'", verified=True,
        values=[_pct(e, r'by (\d+)%') for n, e in _scroll if n.startswith('Defensive')]),
    emperorshipAllianceMaxHealth=OrderedDict(
        source=src('uesp_Online_Campaigns_t08.csv', 'Emperorship Alliance Bonus I') + " to 'Emperorship Alliance Bonus VI'" + '; ' + pn('128', '2022-11-14', 'The Health bonus for having an Emperor crowned for your Alliance will now scale depending on how many home Keeps you have controlled by your alliance.'),
        verified=True, note='Index is the number of home Keeps the alliance owns (1 to 6).',
        values=[_pct(e, r'by (\d+)') for n, e in _emp if n.startswith('Emperorship')]),
    emperorPassives=OrderedDict(
        source=page('Emperor.md', 'Innate Abilities: Domination, Authority, Monarch, Tactician, Emperor, each by Home Keeps owned, 1 or less to 6'), verified=True,
        note='Index is the number of home Keeps the alliance owns (1 or less, 2, 3, 4, 5, 6). Authority (Ultimate generation) and Tactician (siege damage) have no sheet stat.',
        dominationRecoveryPercent=[50, 60, 70, 80, 90, 100],
        monarchHealingTakenPercent=[25, 30, 35, 40, 45, 50],
        emperorMaxStatsPercent=[38, 45, 53, 60, 68, 75]),
)

# ---------------------------------------------------------------- Vampire stages
vt = table('uesp_Online_Vampire_t01.csv')
stages = OrderedDict()
for row in vt[1:]:
    st = int(row[0])
    stages[str(st)] = OrderedDict(
        healthRecovery=OrderedDict(value=num(row[1]), kind='percent'),
        flameDamageTaken=OrderedDict(value=num(row[2]), kind='percent'),
        vampireAbilityCost=OrderedDict(value=num(row[3]), kind='percent'),
        regularAbilityCost=OrderedDict(value=num(row[4]), kind='percent'),
        source=src('uesp_Online_Vampire_t01.csv', f'{st}') + ' (Stage column)' + '; ' + page('Vampire.md', 'Vampire Stages table (fetched 2026-09-17): stage 3 -60% Health Recovery; Update 26 removed Unnatural Resistance'), verified=True)
C['vampireStages'] = OrderedDict(
    note='Unnatural Resistance (skills.csv) changes the Health Recovery penalty: stage 2 none, stage 3 25%, stage 4 50%. Applied by the engine when that passive is active.',
    stages=stages,
)

# ---------------------------------------------------------------- Champion Points
CONSTELLATION = {}
for t in range(0, 4): CONSTELLATION[t] = 'craft'
for t in range(4, 13): CONSTELLATION[t] = 'warfare'
for t in range(13, 23): CONSTELLATION[t] = 'fitness'
stars = []
for t in range(0, 23):
    fn = f'uesp_Online_Champion_t{t:02d}.csv'
    rows = table(fn)
    head = rows[0][0]
    slottable = 'Active' in head
    for row in rows[1:]:
        if len(row) < 5: continue
        _, name, effect, cost, nstages = row[:5]
        stars.append(OrderedDict(name=name, constellation=CONSTELLATION[t], slottable=slottable,
                                 costPerStage=int(cost), stages=int(nstages), maxPoints=int(cost) * int(nstages),
                                 effect=effect, source=src(fn, name)))
C['championPoints'] = OrderedDict(
    note='Stars from the UESP Champion page tables. Tables t00 to t03 are Craft, t04 to t12 Warfare, t13 to t22 Fitness. "Active" rows are slottable. Per stage effect text is parsed by tools/parse_effects; the engine applies max stages.',
    totalCap=sourced(3600, pn('100', '2021-03-15', 'The CP cap per update has been lifted, and you can now spend up to the 3600 CP cap.')),
    perConstellationCap=sourced(1200, pn('100', '2021-03-15', 'Update 29 Champion Point System Update: points are earned equally across the three constellations.'), 'One third of 3600.'),
    slotsPerConstellation=sourced(4, page('Champion.md', 'line 88: the most expensive four active perks per constellation; line 9: the cap is 3600, 1200 per constellation') + '; task statement'),
    stars=stars,
)

# ---------------------------------------------------------------- named buffs (Major / Minor)
buffs = OrderedDict()
rows = table('uesp_Online_Buffs_t00.csv')
current = None
for row in rows[1:]:
    if not row or len(row) < 3: continue
    if row[0].strip() in ('Major', 'Minor'):
        tier = row[0].strip(); desc = row[1].strip()
    elif row[0].strip():
        current = re.sub(r'\s*\[ edit \]', '', row[0]).strip()
        tier = row[1].strip(); desc = row[2].strip()
    else:
        continue
    if current and tier in ('Major', 'Minor') and desc:
        buffs[f'{tier} {current}'] = OrderedDict(description=desc, source=src('uesp_Online_Buffs_t00.csv', f'{current} / {tier}'), verified=True)
BUFF_NOTES = {
    'Major Resolve': pn('096', '2020-11-09', 'Major Resolve: Increased to 5948, up from 5280.'),
    'Minor Resolve': pn('096', '2020-11-09', 'Minor Resolve: Increased to 2974, up from 1320.'),
    'Major Courage': pn('096', '2020-11-09', 'Major Courage: Increased to 430, up from 258.'),
    'Minor Courage': pn('096', '2020-11-09', 'Minor Courage: Increased to 215, up from 129.'),
}
for k, n in BUFF_NOTES.items():
    buffs[k]['patchNote'] = n
C['namedBuffs'] = OrderedDict(note='Major and Minor buff magnitudes. Set bonuses and passives that grant a named buff resolve through this table in the parser.', buffs=buffs)

# ---------------------------------------------------------------- misc
C['slots'] = OrderedDict(
    armor=['head', 'shoulders', 'chest', 'hands', 'waist', 'legs', 'feet'],
    jewelry=['necklace', 'ring1', 'ring2'],
    weapon=['mainHand', 'offHand'],
    monsterSetSlots=['head', 'shoulders'],
    mythicMaxEquipped=sourced(1, page('Sets.md', 'Mythic Items: Only one mythic item can be worn at a time') + '; sets.csv marks 35 sets Mythic; task statement'),
)

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(C, f, indent=2, ensure_ascii=False)
    f.write('\n')

# report
def walk(o, path=''):
    if isinstance(o, dict):
        if o.get('source') == 'UNVERIFIED' or o.get('verified') is False:
            yield path, o.get('value', o.get('oneHand', '')), o.get('note', '')
        for k, v in o.items():
            yield from walk(v, f'{path}.{k}' if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f'{path}[{i}]')
unv = list(walk(C))
print(f'wrote {OUT}: {len(stars)} CP stars, {len(buffs)} named buffs, {len(foods)} foods, {len(unv)} unverified entries')
if '--list' in sys.argv:
    for p, v, n in unv:
        print(f'  {p} = {v}  ({n})')
