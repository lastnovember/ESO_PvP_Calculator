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


def pn(seq, date, text):
    """Cite a patch note by manifest sequence and date."""
    return f"data/patch-notes/html {seq} ({date}): {text}"


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
C['base'] = OrderedDict(
    maxHealth=sourced(16000, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 19305 = 16000 + 15 x 122 + Lunar Blessings 915 + Hero\'s Vigor 560.'),
    maxMagicka=sourced(12000, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 19251 = (12000 + 49 x 111 + 915 + 520) x 1.02 Magicka Controller.'),
    maxStamina=sourced(12000, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 13435 = 12000 + 915 + 520.'),
    healthRecovery=unverified(309, 'Naked level 50 Health Recovery. fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 540 = base + Capacitor 141 + Robustness 90, so 309 if both passives give Health Recovery the full amount. The split is the unverified part.', [484]),
    magickaRecovery=sourced(514, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 909 = (514 + 141 + 90) x 1.22 (Flourish 20%, Magicka Controller 2%).'),
    staminaRecovery=sourced(514, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 894 = (514 + 141 + 90) x 1.20 (Flourish).'),
    weaponDamage=unverified(1000, 'Sheet Weapon Damage with no weapon equipped and no bonuses.', [0]),
    spellDamage=unverified(1000, 'Sheet Spell Damage with no weapon equipped and no bonuses.', [0]),
    critChancePercent=unverified(10, 'Base Critical Chance for every character.'),
    critDamagePercent=unverified(50, 'Base Critical Damage.'),
    critDamageCapPercent=sourced(125, pn('111', '2021-11-15', 'Critical Damage and Healing now has a hard cap of 125%.'), 'Class Mastery Above and Beyond raises the cap by 30 (patch 12.0.0 note in skills.csv: 155%).'),
    critRatingPerPercent=unverified(219, 'Critical rating needed for 1% Critical Chance at level 50 CP160.'),
    resistancePerPercent=unverified(660, 'Physical or Spell Resistance rating per 1% of damage mitigation at level 50 CP160.'),
    resistanceCapRating=unverified(33000, 'Resistance cap, equals 50% mitigation at 660 per percent.'),
    resistanceCapPercent=unverified(50, 'Mitigation shown at the resistance cap.'),
    blockMitigationPercent=unverified(50, 'Base fraction of damage blocked.'),
    blockMitigationCapPercent=sourced(90, pn('076', '2019-08-26', 'Block mitigation now has a cap of 90%.')),
    blockCost=sourced(1750, 'fixtures 001 and 002 (Yeets-Swiftly): (1750 - 40 Tireless Guardian) x 0.91 (medium -12%, light +3%) = 1556 on the mace bar and x 0.64 more (Ice Staff) = 996 on the staff bar, both exact. The 2018 note (053, 2018-02-26) set 1730; no later note names the base, the sheet says 1750.', 'Flat reductions are subtracted from the base first, then percentage reductions (STRATEGIES.costOrder flatThenPercent); armor passives add up, a weapon passive multiplies separately (STRATEGIES.costWeaponPercent).'),
    rollDodgeCost=sourced(4040, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 3800 on the sheet with Tumbling 240 taken off first. Geared (fixture 002) reads 3248 where the additive passive model gives 3306; the percent stacking for Roll Dodge is still open.'),
    sprintCostPerSecond=sourced(500, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 460 = 500 - Sprinter 40; geared (500 - 40) x 0.93 = 428.'),
    breakFreeCost=sourced(5400, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 5180 = 5400 - Defiance 220; geared (5400 - 220) x 0.95 = 4921.'),
    bashCost=sourced(765, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points): 675 = 765 - Savage Defense 90; geared (765 - 90) x 0.97 = 655.'),
    movementSpeedPercent=sourced(100, src('uesp_Online_Movement_Speed_t00.csv', 'Walking'), 'Default walking speed 100%, maximum 200%.'),
    movementSpeedCapPercent=sourced(200, src('uesp_Online_Movement_Speed_t00.csv', 'Walking')),
    critResistance=sourced(1320, pn('087', '2020-06-09', 'All players will now have a baseline of 20% Critical Damage Reduction in the form of Critical Resistance, starting at level 10.'), '20% at 66 Critical Resistance per percent. Fixture 003 (naked) reads 1980 = 1320 + Resilience 660.'),
    sprintSpeedPercent=sourced(140, src('uesp_Online_Movement_Speed_t00.csv', 'Running'), 'Running (sprint) default 140%, maximum 200%.'),
    blockMoveSpeedPercent=unverified(42, 'Block Move Speed on the sheet. Fixtures 001 to 004 all read 42% (naked and geared, no shield); Battlefield Mobility changes it with a shield.'),
    sneakSpeedPercent=unverified(60, 'Sneak Speed on the sheet. Fixtures 003 and 004 (naked) read 60%; light armor reduces the 40 point penalty by 5% per piece (fixture 002 with one light piece reads 62%).'),
    sneakCost=unverified(118, 'Base Stamina cost of Sneak per tick. Fitted: fixtures 003 and 004 read 59 with Sustaining Shadows slotted (1% per stage, 50 stages, so half). The geared 34 (fixture 002) does not follow from the medium armor reductions yet.'),
    esoPlusBonusPercent=sourced(10, 'fixtures 001 to 004: Experience, Gold, Crafting Inspiration, Tel Var and Alliance Points all read 10% with ESO Plus Member in the active effects.'),
)

C['attributePoints'] = OrderedDict(
    total=sourced(64, 'task statement (level 50 characters have 64 attribute points)'),
    healthPerPoint=sourced(122, 'fixture 003 (Yeets-Swiftly naked, Elden Root, no food, 49 Magicka 15 Health points) with base 16000, and fixtures 001 and 002 seven points apart.'),
    magickaPerPoint=sourced(111, 'fixtures 001 and 002 (Yeets-Swiftly): 42 and 49 points with the same gear differ by 777 Max Magicka before percent bonuses, 7 x 111.'),
    staminaPerPoint=unverified(111, 'Max Stamina granted by one attribute point at level 50.'),
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
        **{'Health': OrderedDict(large=unverified(954, 'Glyph of Health, large piece'), small=unverified(385, 'Glyph of Health, small piece: 40.3% of the large piece, the ratio fixtures 002 and 003 give for Prismatic Defense (seven pieces total 2002 Magicka with 434 on the three large pieces)'), values=[OrderedDict(stat='maxHealth', kind='flat')]),
           'Magicka': OrderedDict(large=unverified(868, 'Glyph of Magicka, large piece'), small=unverified(350, 'Glyph of Magicka, small piece: 40.3% of the large piece, see Health'), values=[OrderedDict(stat='maxMagicka', kind='flat')]),
           'Stamina': OrderedDict(large=unverified(868, 'Glyph of Stamina, large piece'), small=unverified(350, 'Glyph of Stamina, small piece: 40.3% of the large piece, see Health'), values=[OrderedDict(stat='maxStamina', kind='flat')]),
           'Prismatic Defense': OrderedDict(
               large=unverified([477, 434, 434], 'Glyph of Prismatic Defense, large piece: Health, Magicka, Stamina'),
               small=unverified([192, 175, 175], 'Glyph of Prismatic Defense, small piece: Health, Magicka, Stamina. Fixtures 002 and 003: seven pieces (three large at 434) total 2002 Magicka and Stamina, so a small piece is 175, 40.3% of a large one; Health scaled the same way.'),
               values=[OrderedDict(stat='maxHealth', kind='flat'), OrderedDict(stat='maxMagicka', kind='flat'), OrderedDict(stat='maxStamina', kind='flat')])}
    ),
    jewelry=OrderedDict(
        **{'Weapon Damage': OrderedDict(magnitude=unverified(174, 'Glyph of Increase Physical Harm. Grants Weapon and Spell Damage since Update 37: data/patch-notes/html 135 (2023-03-28): Glyph of Physical Harm and Glyph of Spell Harm: These enchantments now grant Weapon and Spell Damage, rather than only Weapon or Spell Damage.'), values=[OrderedDict(stat='weaponDamage', kind='flat'), OrderedDict(stat='spellDamage', kind='flat')]),
           'Spell Damage': OrderedDict(magnitude=unverified(174, 'Glyph of Increase Magical Harm. Grants Weapon and Spell Damage since Update 37 (same note as Weapon Damage).'), values=[OrderedDict(stat='weaponDamage', kind='flat'), OrderedDict(stat='spellDamage', kind='flat')]),
           'Magicka Recovery': OrderedDict(magnitude=unverified(169, 'Glyph of Magicka Recovery'), values=[OrderedDict(stat='magickaRecovery', kind='flat')]),
           'Stamina Recovery': OrderedDict(magnitude=unverified(169, 'Glyph of Stamina Recovery'), values=[OrderedDict(stat='staminaRecovery', kind='flat')]),
           'Health Recovery': OrderedDict(magnitude=unverified(169, 'Glyph of Health Recovery'), values=[OrderedDict(stat='healthRecovery', kind='flat')]),
           'Prismatic Recovery': OrderedDict(magnitude=unverified(84, 'Glyph of Prismatic Recovery, each of the three recoveries'), values=[OrderedDict(stat='healthRecovery', kind='flat'), OrderedDict(stat='magickaRecovery', kind='flat'), OrderedDict(stat='staminaRecovery', kind='flat')]),
           'Reduce Spell Cost': OrderedDict(magnitude=unverified(203, 'Glyph of Reduce Spell Cost'), values=[OrderedDict(stat='magickaCostReduction', kind='flat')]),
           'Reduce Feat Cost': OrderedDict(magnitude=unverified(203, 'Glyph of Reduce Feat Cost'), values=[OrderedDict(stat='staminaCostReduction', kind='flat')]),
           'Reduce Block Cost': OrderedDict(magnitude=unverified(203, 'Glyph of Shielding'), values=[OrderedDict(stat='blockCost', kind='flat', negative=True)]),
           'Increase Bash Damage': OrderedDict(magnitude=sourced(500, pn('087', '2020-06-09', 'Glyph of Bashing: These enchantments now increase the damage of your Bash attacks by up to 500 per CP160 Gold quality enchantment.')), values=[OrderedDict(stat='bashDamage', kind='flat')]),
           'Potion Cooldown': OrderedDict(magnitude=unverified(5.2, 'Glyph of Potion Speed, seconds'), values=[OrderedDict(stat='potionCooldown', kind='flat', negative=True)]),
           'Potion Boost': OrderedDict(magnitude=unverified(8.2, 'Glyph of Potion Boost, seconds'), values=[OrderedDict(stat='potionDuration', kind='flat')]),
           'Flame Resist': OrderedDict(magnitude=unverified(2900, 'Glyph of Flame Resist'), values=[OrderedDict(stat='flameResistance', kind='flat')]),
           'Frost Resist': OrderedDict(magnitude=unverified(2900, 'Glyph of Frost Resist'), values=[OrderedDict(stat='frostResistance', kind='flat')]),
           'Shock Resist': OrderedDict(magnitude=unverified(2900, 'Glyph of Shock Resist'), values=[OrderedDict(stat='shockResistance', kind='flat')]),
           'Poison Resist': OrderedDict(magnitude=unverified(2900, 'Glyph of Poison Resist'), values=[OrderedDict(stat='poisonResistance', kind='flat')]),
           'Disease Resist': OrderedDict(magnitude=unverified(2900, 'Glyph of Disease Resist'), values=[OrderedDict(stat='diseaseResistance', kind='flat')]),
           'Decrease Physical Harm': OrderedDict(magnitude=unverified(None, 'Glyph of Decrease Physical Harm. Magnitude and stat unknown, no sheet effect until settled.'), values=[]),
           'Decrease Spell Harm': OrderedDict(magnitude=unverified(None, 'Glyph of Decrease Spell Harm. Magnitude and stat unknown, no sheet effect until settled.'), values=[])}
    ),
    weapon=OrderedDict(note='Every weapon glyph is a combat proc and has no character sheet effect. Kept for completeness.',
                       names=['Flame', 'Frost', 'Shock', 'Poison', 'Disease', 'Decrease Health', 'Absorb Health', 'Absorb Magicka', 'Absorb Stamina', 'Weapon Damage', 'Crushing', 'Weakening', 'Hardening', 'Prismatic Onslaught']),
)

# ---------------------------------------------------------------- armor and weapon item values
C['items'] = OrderedDict(
    note='Armor rating of a gold CP160 piece with no trait, and weapon damage of a gold CP160 weapon. Not in data/reference. UNVERIFIED. Slot factors relative to the chest are the community understanding: chest 1.0, head shoulders legs feet 0.879, hands waist 0.5.',
    qualityFactor=OrderedDict(
        gold=sourced(1.0, 'definition: ratings are stated for gold (Legendary) CP160 items'),
        purple=unverified(0.96, 'Armor and weapon rating of a purple (Epic) CP160 item relative to gold. Community steps of about 4% per quality; a purple piece reading settles it.', [0.95]),
        blue=unverified(0.92, 'Blue (Superior) relative to gold, see purple.', [0.90]),
        green=unverified(0.88, 'Green (Fine) relative to gold, see purple.'),
        white=unverified(0.84, 'White (Normal) relative to gold, see purple.'),
    ),
    armor=OrderedDict(
        heavy=OrderedDict(head=unverified(2437, 'heavy head'), shoulders=unverified(2437, 'heavy shoulders'), chest=unverified(2772, 'heavy chest'), hands=unverified(1386, 'heavy hands'), waist=unverified(1386, 'heavy waist'), legs=unverified(2437, 'heavy legs'), feet=unverified(2437, 'heavy feet')),
        medium=OrderedDict(head=unverified(1567, 'medium head'), shoulders=unverified(1567, 'medium shoulders'), chest=unverified(1782, 'medium chest'), hands=unverified(891, 'medium hands'), waist=unverified(891, 'medium waist'), legs=unverified(1567, 'medium legs'), feet=unverified(1567, 'medium feet')),
        light=OrderedDict(head=unverified(1015, 'light head'), shoulders=unverified(1015, 'light shoulders'), chest=unverified(1155, 'light chest'), hands=unverified(578, 'light hands'), waist=unverified(578, 'light waist'), legs=unverified(1015, 'light legs'), feet=unverified(1015, 'light feet')),
    ),
    shieldArmor=unverified(1880, 'Armor rating of a gold CP160 shield.'),
    weaponDamage=unverified(1335, 'Damage rating of any gold CP160 weapon. Applies to Weapon Damage and Spell Damage on the sheet.'),
    twoHandedTypes=['greatsword', 'battle axe', 'maul', 'bow', 'inferno staff', 'lightning staff', 'ice staff', 'restoration staff'],
    twoHandedSetPieces=sourced(2, 'sets.csv settype Weapon rows hold their bonus in bonus_2 (2 items) for a single two handed weapon; task statement', 'A two handed weapon counts as two set pieces.'),
)

# ---------------------------------------------------------------- foods
def food(id_, name, kind, note, verified=False, source='UNVERIFIED', **stats):
    d = OrderedDict(id=id_, name=name, kind=kind, stats=OrderedDict(stats), source=source, verified=verified, note=note)
    return d

foods = [
    food('green-health', 'Green single stat food (Max Health)', 'food', 'UESP scaling table last column read as CP160. Column alignment in that table is suspect.', True, src('uesp_Online_Food_t03.csv', 'Health, last column'), maxHealth=6277),
    food('green-magicka', 'Green single stat food (Max Magicka)', 'food', 'UESP scaling table last column read as CP160.', True, src('uesp_Online_Food_t02.csv', 'last column'), maxMagicka=5745),
    food('green-stamina', 'Green single stat food (Max Stamina)', 'food', 'UESP scaling table last column read as CP160.', True, src('uesp_Online_Food_t02.csv', 'last column'), maxStamina=5745),
    food('blue-health-magicka', 'Blue dual stat food (Health and Magicka)', 'food', 'UESP scaling table. Community tooltips are often quoted as 5395 and 4936; listed in UNKNOWNS.md.', True, src('uesp_Online_Food_t07.csv', 'last column'), maxHealth=5000, maxMagicka=4575),
    food('blue-health-stamina', 'Blue dual stat food (Health and Stamina)', 'food', 'UESP scaling table.', True, src('uesp_Online_Food_t08.csv', 'last column'), maxHealth=5000, maxStamina=4575),
    food('blue-magicka-stamina', 'Blue dual stat food (Magicka and Stamina)', 'food', 'UESP scaling table.', True, src('uesp_Online_Food_t09.csv', 'last column'), maxMagicka=4575, maxStamina=4575),
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
    food('blue-drink-health-stamina-recovery', 'Blue dual recovery drink (Health and Stamina Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t03.csv', 'last column'), healthRecovery=500, staminaRecovery=457),
    food('blue-drink-health-magicka-recovery', 'Blue dual recovery drink (Health and Magicka Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t04.csv', 'last column'), healthRecovery=500, magickaRecovery=457),
    food('blue-drink-magicka-stamina-recovery', 'Blue dual recovery drink (Magicka and Stamina Recovery)', 'drink', 'UESP scaling table.', True, src('uesp_Online_Drinks_t05.csv', 'last column'), magickaRecovery=457, staminaRecovery=457),
    food('purple-tri-recovery-drink', 'Purple tri recovery drink', 'drink', 'Crown Refreshing Drink description on UESP Drinks page.', True, src('uesp_Online_Drinks_t06.csv', 'Crown Refreshing Drink'), healthRecovery=446, magickaRecovery=410, staminaRecovery=410),
]
# Food buffs in the esolog coefficient table are listed at a lower level; the CP160 gold values are
# the table values times 1.1735 (Bewitched Sugar Skulls 3937/3622/393 in the table against the
# known 4620/4250/462; Smoked Bear Haunch 3675/346/315 against the fixture fit 4316/406/369).
FOOD_SCALE = 1.1735
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
            stats[k] = int(round(consts[n] * FOOD_SCALE))
    return food(id_, name, kind, f'esolog buff "{buff}" ({row[7].strip()}) x {FOOD_SCALE} for CP160 gold.', True, src('esolog_skill_coefficients_t00.csv', buff), **stats)
foods = [f for f in foods if f['id'] not in ESOLOG_FOODS] + [esolog_food(i) for i in ESOLOG_FOODS]
# Two geared readings of different characters (fixtures 002 and 005) both need 4316 Max Health from the Bear Haunch
# where the esolog value x 1.1735 gives 4313; the recoveries keep the scaled table values (406 fits fixture 002).
_bh = next(f for f in foods if f['id'] == 'orzorgas-smoked-bear-haunch')
_bh['stats']['maxHealth'] = 4316
_bh['note'] += ' Max Health 4316 from fixtures 002 (30001 = (16000 + 1600 ... ) geared minus naked) and 005 (36217, engine 36214 with 4313).'
C['foods'] = OrderedDict(note='Food and drink catalog. The app also accepts custom values typed from a tooltip. Racial food duration passives do not change magnitudes.', items=foods)

# ---------------------------------------------------------------- Battle Spirit
bs = table('uesp_Online_Campaigns_t05.csv')[1]
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
    legacyFlatMaxHealth=sourced(1600, 'fixtures 001 and 002 (Yeets-Swiftly): same gear, 22 Health points in Cyrodiil read 32701 and 15 points outside read 30001; 7 points are 7 x 122 x 1.10, the rest is 1600 x 1.10, so Battle Spirit adds 1600 Max Health before percent bonuses. Older notes said 5000: ' + pn('017', '2016-03-22', 'fixed: Battle Spirit Health bonus would not be modified by Health percentage increases.') + ' ' + pn('076', '2019-08-26', 'Pets will now properly gain the extra 5000 Health from Battle Spirit.') + ' No note carries the change to 1600.', 'Applied whenever Battle Spirit is on unless flags.battleSpiritFlatHealth is false.'),
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
        source=src('uesp_Online_Vampire_t01.csv', f'Stage {st}'), verified=True)
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
    slotsPerConstellation=sourced(4, 'task statement'),
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
    mythicMaxEquipped=sourced(1, 'task statement; sets.csv marks 35 sets Mythic'),
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
