# UNKNOWNS

Values the engine needs that could not be sourced from `data/reference`. Each
one is used with the best community-known value, is flagged `verified: false`
in `engine/data/constants.json`, and stays here until a fixture read from the
game settles it. When a fixture settles a value, move it to the "Settled"
table at the bottom with the fixture name.

## Missing inputs

| Item | Status |
| --- | --- |
| `data/patch-notes/html` | Present (202 notes, 2015-06-23 to 2026-08-10). Searched for every constant below; hits are cited in constants.json as "data/patch-notes/html NNN (date)". Base character numbers (naked stats, points, ratings per percent, Roll Dodge, Break Free, Sprint and Bash costs, glyph magnitudes other than Bashing, item armor and weapon ratings) never appear in a console patch note. |
| UESP prose pages (Health, Magicka, Stamina, Combat, Attributes, Enchanting glyph tables, Armor values) | Archived as PDF only; PDFs are not in the repository. Only the wiki tables (`data/reference/tables`) are. The Scribing page was added the same way on 2026-09-14 (tables t00 to t03, manifest seq 220). |
| esoapi.uesp.net data version | v101044 (Update 44, November 2024) per `tools/ARCHIVE_README.md`. Six updates behind live. |

## Base character values (level 50, CP160, naked, 0 attribute points)

| Constant | Value used | Alternatives seen | Note |
| --- | --- | --- | --- |
| Max Health | 16000 | 15000 | |
| Max Magicka | 7958 | 12000 | |
| Max Stamina | 7958 | 12000 | |
| Health Recovery | 484 | | per tick as displayed |
| Magicka Recovery | 514 | | |
| Stamina Recovery | 514 | | |
| Weapon Damage, no weapon | 1000 | 0 | The sheet may show only the weapon's damage rating. |
| Spell Damage, no weapon | 1000 | 0 | |
| Critical Chance base | 10% | | |
| Critical rating per 1% | 219 | | |
| Critical Damage base | 50% | | |
| Resistance per 1% mitigation | 660 | | |
| Resistance cap | 33000 (50%) | | |
| Block mitigation | 50% | | Cap of 90% is settled (2019-08-26). |
| Roll Dodge cost | 2891 | 3060 | |
| Sprint cost | 400 per second | | |
| Break Free cost | 3060 | | |
| Bash cost | 1283 | | |
| Health per attribute point | 122 | 111 | |
| Magicka per attribute point | 111 | | |
| Stamina per attribute point | 111 | | |

## Items

| Constant | Value used | Note |
| --- | --- | --- |
| Gold CP160 weapon damage rating | 1335 | Any weapon type. Dual wield off hand counts through the Dual Wield Expert passive only (6% of off hand damage per skills.csv). |
| Gold CP160 armor rating, heavy | chest 2772, head/shoulders/legs/feet 2437, hands/waist 1386 | |
| Gold CP160 armor rating, medium | chest 1782, head/shoulders/legs/feet 1567, hands/waist 891 | |
| Gold CP160 armor rating, light | chest 1155, head/shoulders/legs/feet 1015, hands/waist 578 | |
| Gold CP160 shield armor rating | 1880 | |
| Precise trait conversion | 3.6% / 7.2% converted at 219 per percent | The percent is settled (2020-09-15). Whether the sheet applies it as a rating or as a percent is not, see STRATEGIES.preciseTrait. |

## Glyphs (Truly Superb, gold)

| Glyph | Value used |
| --- | --- |
| Health | 954 large piece, 477 small piece |
| Magicka, Stamina | 868 large, 434 small |
| Prismatic Defense | 477 / 434 / 434 large, 239 / 217 / 217 small |
| Weapon Damage, Spell Damage (jewelry) | 174 |
| Health, Magicka, Stamina Recovery (jewelry) | 169 |
| Prismatic Recovery | 84 each |
| Reduce Spell Cost, Reduce Feat Cost | 203 |
| Reduce Block Cost (Shielding) | 203 |
| Potion Cooldown | 5.2 s |
| Potion Boost | 8.2 s |
| Elemental resist glyphs | 2900 |
| Decrease Physical Harm, Decrease Spell Harm | unknown, no sheet effect applied |

Large pieces: head, chest, legs, shield. Small: shoulders, hands, waist, feet.

## Food and drink

The UESP Food and Drinks scaling tables in `data/reference/tables` have their
per level columns collapsed, so only the last (CP160) column was trusted.
Named items are community tooltip values.

| Item | Value used | Note |
| --- | --- | --- |
| Blue dual stat food | 5000 Health + 4575 secondary (UESP) | Community tooltips often quote 5395 / 4936. |
| Green single stat food | 6277 Health, 5745 Magicka or Stamina (UESP) | |
| Purple tri stat food | 4620 / 4250 / 4250 | UESP level 50 columns show 4625 / 4233. |
| Bewitched Sugar Skulls | tri stat + 406 Health Recovery | |
| Artaeum Takeaway Broth, Clockwork Citrus Filet | 3724 Health, 3458 resource, 406 and 406 recovery | A 2019-06-03 note cut their max values by about 15%, so they are not equal to tri stat food. |
| Witchmother's Potent Brew | 2856 Health, 3161 Magicka, 315 Magicka Recovery | |
| Dubious Camoran Throne | 2856 Health, 3161 Stamina, 315 Stamina Recovery | |
| Jewels of Misrule | 3326 Health, 315 each recovery | |
| Lava Foot Soup-and-Saltrice, Ghastly Eye Bowl | 3080 max + 338 recovery | |
| Orzorga's Smoked Bear Haunch | 3080 Health, 338 each recovery | |
| Green recovery drinks | 565 (Magicka, Stamina), 621 (Health) | From Crown item descriptions that mention "Veteran Rank 10", so the era is old. |

## Systems

- Mora's Whispers (crit by books collected) and Thrassian Stranglers (Weapon Damage by kill stacks) depend on character state the build cannot express yet.

- Cyrodiil scroll and keep bonuses: values from the UESP campaign table (2% and 5% damage or resistance, 1% crit per enemy keep, 900 to 1750 Max Health by home keeps under Emperorship); whether the percents multiply the sheet total or add to the other percents is unverified, no reading carries one yet.

| Item | Value used | Note |
| --- | --- | --- |
| Battle Spirit flat +5000 Max Health | Off by default (`flags.battleSpiritFlatHealth`) | Timeline in the notes: 2016-01-26 temporary "not modified by Health percentage increases", 2016-03-22 fixed (so it IS multiplied by percent bonuses), 2016-06-13 and 2019-08-26 pets get the same 5000. No note ever removes it, no note after 2019 mentions it for players, UESP does not list it. Only a PvP zone fixture can settle it. |
| Dual wield off hand contribution | 6% of off hand damage (Dual Wield Expert) | skills.csv tooltip. |
| Werewolf form stat changes beyond passives | none modelled | |

## Scribing

| Item | Status |
| --- | --- |
| Armor and weapon rating by quality | `items.qualityFactor` purple 0.96, blue 0.92, green 0.88, white 0.84 of gold are community steps. One reading with a single purple armor piece and one with a purple weapon settle them by differencing. Trait values by quality are verified (UESP trait tables). |
| Vault and Physical Damage | The UESP Scribing page (2026-09-14) shows no Vault icon on the Physical Damage focus row, while the esolog table (Update 44) still has Sundering Vault. The newer page wins, so the picker does not offer Physical Damage on Vault. If the game does, say so and the row gets a per script override. |
| Affix tiers on new pairs | The Major or Minor tier of an affix on a grimoire comes from the UESP Buffs and Debuffs pages, which predate the Scribing page. Pairs the Buffs pages do not list (Interrupt, Off Balance, and a few grimoire and affix pairs added since) show without a tier. Scripts change no sheet value in phase 1, so this is a label only. |

## Open gaps across the ten readings (2026-09-17, after the dual wield, vampire and armor fits)

Every reading now matches 43 to 55 of its numbers (`engine/tests/fixtures/INDEX.md`). What is left, in every case the same on both bars of a character:

| Gap | Readings | Game vs engine | Best reading of it |
| --- | --- | --- | --- |
| Magicka Recovery | all four characters | +14 (Templar), +34 and +37 (Necro), +45 (DK), +50 and +52 (Yeets) after percents; +11, +29, +42, +41 before | Not race (Argonian and Khajiit read the same 41), not food (the DK eats Sugar Skulls), not glyphs, not Max Magicka. It grows with Magicka attribute points (0, 17, 49, 52 points give 11, 29, 41, 42) and flattens above 40, but the UESP Magicka page says outright that the attribute does not raise recovery and gives base 514 at level 50 with no attribute term, and none of the nine archived forum threads on recovery names a scaling source. Its formula puts one skill group in a separate multiplier with food divided out; tried against the readings it does not fit either. Open. |
| Resistances | all geared readings | within 14 to 73 after the armor fit (was 514 to 859) | The slot factors (big 0.879, small 0.5 of the chest) are still community values. The archived UESP Armor page (2026-09-12) has no rating table and the Nirnhoned page gives only the Nirnhoned armor value, so the fit stands. |
| Roll Dodge Cost | Yeets 3248 (engine 3306), DK 3315 (3344), Necro 3420 (exact) | | No order (flat first or percent first, additive or multiplicative) with any per piece values from 0 to 6% fits all three within 1; the closest is flat first, additive, medium 4, heavy 2, light 2.5 (total error 10). Tumbling is at both stages everywhere (user). The archived armor line pages list the passives by name only. |
| Health Recovery, vampire | Templar 415 (engine 452) | | The 60% stage penalty is right (Unnatural Resistance is gone); the remaining 37 is exactly the Prismatic Recovery ring's 84 through Constitution and the penalty, so that glyph's Health Recovery share is the suspect. |
| Weapon and Spell Critical | Necro 19.4 and 16.4 (engine 18.5 and 15.5) | | One percent (about 206 rating) on both bars from no archived source. |
| Stamina Recovery | Templar 1785 (engine 1804) | | 15 before percents, the only stamina miss on file. |
| Physical and Bleed Damage | Templar front bar 10 and 5 (engine 5 and 0) | | A buff running out during the photos (the same reading carries Major Brutality and Sorcery in its first photo). |
| Yeets back bar naked (004) | Max Health 21236 (19305), resistances 6003 (1730) | | 10% Max Health and 4272 resistance from something slotted on that bar; no archived "while slotted" text on Bull Netch, Hurricane, Resolving Vigor, Streak, Wield Soul or Temporal Guard gives it. |
| Bash Damage | all | not modelled | Weapon dependent total; the sheet's number is not the bonus. |
| Penetration | Yeets 9491 and 4879 (engine 9494 and 4882) | | Two Divines pieces round per piece. |

## Settled by data supplied later

| Item | Settled by |
| --- | --- |
| Scribing script catalog (21 focus, 20 signature, 26 affix, and which grimoires take each) | UESP Online:Scribing page printed 2026-09-14, archived as `data/reference/tables/uesp_Online_Scribing_t00..t03.csv` by `tools/extract_scribing_pdf.py` (manifest seq 220). Class Mastery is Class Flourish now (patch note), Passive Master reads Wayfarer's Mastery and Healing Absorption reads Trauma on the page; old build files are mapped on load. |
| Rakkhat's Voidmantle, Stormweaver's Cavort slots and text | In game tooltips supplied by the user (medium shoulders, light legs, plus the missing 300 Magicka Recovery line). |

## Settled by patch notes

| Constant | Settled value | Note |
| --- | --- | --- |
| Battle Spirit damage taken | -50% | 108, 2021-09-07 (up from 44%) |
| Battle Spirit healing received | -55% | 108, 2021-09-07. History: 50% (2015-09-14), 60%, 55% (2020-11-09), 50%, 55% |
| Battle Spirit Health Recovery | -50% | 103, 2021-06-08 (new penalty) |
| Battle Spirit damage shield strength | -50% | 007, 2015-09-14, no later change |
| Block base cost | 1730 | 053, 2018-02-26 (down from 2160); flat reductions apply before percent reductions |
| Block mitigation cap | 90% | 076, 2019-08-26 |
| Critical Damage cap | 125% | 111, 2021-11-15; Above and Beyond raises it to 155% (12.0.0 note) |
| Champion Point cap | 3600 | 100, 2021-03-15. Passive stars total 320 (Warfare), 342 (Fitness), 800 (Craft), so every passive can be maxed with four slottables to spare |
| Precise trait | 3.6% one hand, 7.2% two hand | 093, 2020-09-15 |
| Armor Infused | 25% | 092, 2020-09-01 |
| Weapon Infused | 30% | 048, 2017-08-28 |
| Weapon Nirnhoned | 15% | 048, 2017-08-28 |
| Armor Nirnhoned | 253 | 092, 2020-09-01 |
| Glyph of Bashing | up to 500 Bash damage | 087, 2020-06-09 |
| Mundus stones | UESP table values | 092 (2020-09-01), 140 (Thief 1212, 2023-07-25), 066 (Steed 10%), 048 (238 stones) |
| Major and Minor Resolve, Courage | 5948, 2974, 430, 215 | 096, 2020-11-09 |
| Racial passives | skills.csv values | 2019-03-11 rework, 2021-03-15 adjustments, 2022-11-14 Robustness 90 |
| Class Mastery | 5 passives per class, 2 points, hidden while subclassing | 194, 2026-06-08 |

## Settled by fixtures

| Constant | Settled value | Fixture |
| --- | --- | --- |
| Orzorga's Smoked Bear Haunch Max Health | 4316 (esolog x 1.1735 gives 4313) | 002 and 005 |
| Block Mitigation heavy armor | one point per piece added after the Champion Point percent | 002, 003, 005 |
| Spell Warding under an armor percent | not multiplied (Spell = Physical + 726) | 005, 006 |
| Defending trait under an armor percent | not multiplied (3276 flat, the bar to bar gap difference was 6% of it) | 005, 006 |
| Ice staff block (Ancient Knowledge) | Block Cost 1029 and Block Mitigation 65 with the settled cost and mitigation rules | 006 |
| Battle Spirit flat Max Health | none (the flag keeps the earlier 1600 reading available) | 007 |
| Sneak Cost | 118 x Sustaining Shadows stages bought x the medium armor reductions (34, 55, 94) | 002, 005, 007 |
| Shield armor | 1720 gold (1995 Reinforced) | 008 |
| Curative Curse under Battle Spirit | applies (Healing Done +12 on both bars) | 007, 008 |
| Deadly Bash order | halves the base before the flat and the armor percent (257) | 008 |
| Block Move Speed with a shield | 54 (fit, one reading) | 008 |
| Combat Medic near a keep | 20% on the sheet under Battle Spirit (`flags.cyrodiil.nearKeep`) | 001, 009 |
| Dual wield off hand | 23.67% of the off hand rating, trait included (Dual Wield Expert inside it) | 002, 005, 009 |
| Vampire stage penalty | full stage value; Unnatural Resistance removed in Greymoor (note 087) | 005, 006 |
| Medium and light armor | chest 1995 and 1354 (fit, residuals 14 to 73) | 002, 005, 007, 009 |
| Damage Done line | folds the single target star | 001 to 004 |
| Two handed melee weapon damage | 1571 (UESP Nirnhoned page CP160 row, forum 348673); staves, bows and one handed 1335 | pages, 002 to 010 for the 1335 |
| Emperor passives | Domination, Monarch, Emperor by home keeps (UESP Emperor page) | pages |
| Gaze of Sithis, Velothi | full texts parse from the rebuilt sets.csv (3276 Health, 1025 Health Recovery, 4000 Armor, block 0; 1650 penetration, Minor Force) | sets.csv 2026-09-17 |
| Food health scale | 1.17442 for Max Health and Health Recovery, 1.1735 for Magicka and Stamina (Sugar Skulls 4624/4250, Bear Haunch 4316) | 002, 005, 009 |
| Critical Healing sources | Dexterity, Fighting Finesse, The Shadow (not Piercing Spear, Twin Blade and Blunt, Advanced Species, Hemorrhage, Feline Ambush counts) | 002, 003, 005 |
| Sneak Speed with Dark Stalker | 100 | 005 |
| Disease and Poison Resistance | physical rating plus Resist Affliction 2310, over 660 | 005 |
