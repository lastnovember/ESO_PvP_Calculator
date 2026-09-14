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

| Item | Value used | Note |
| --- | --- | --- |
| Battle Spirit flat +5000 Max Health | Off by default (`flags.battleSpiritFlatHealth`) | Timeline in the notes: 2016-01-26 temporary "not modified by Health percentage increases", 2016-03-22 fixed (so it IS multiplied by percent bonuses), 2016-06-13 and 2019-08-26 pets get the same 5000. No note ever removes it, no note after 2019 mentions it for players, UESP does not list it. Only a PvP zone fixture can settle it. |
| Dual wield off hand contribution | 6% of off hand damage (Dual Wield Expert) | skills.csv tooltip. |
| Werewolf form stat changes beyond passives | none modelled | |

## Scribing

| Item | Status |
| --- | --- |
| Vault and Physical Damage | The UESP Scribing page (2026-09-14) shows no Vault icon on the Physical Damage focus row, while the esolog table (Update 44) still has Sundering Vault. The newer page wins, so the picker does not offer Physical Damage on Vault. If the game does, say so and the row gets a per script override. |
| Affix tiers on new pairs | The Major or Minor tier of an affix on a grimoire comes from the UESP Buffs and Debuffs pages, which predate the Scribing page. Pairs the Buffs pages do not list (Interrupt, Off Balance, and a few grimoire and affix pairs added since) show without a tier. Scripts change no sheet value in phase 1, so this is a label only. |

## Fixture 001 (Yeets-Swiftly, back bar, Eastern Elsweyr Gate, Battle Spirit on)

One geared reading in Cyrodiil. What it settled is in DECISIONS.md (crit damage and Battle Spirit sheet semantics, harm glyphs). What it left open, with the size of the gap after the fixes:

| Reading | Game | Engine | Gap and best reading of it |
| --- | --- | --- | --- |
| Max Magicka, Max Stamina | 21305, 18687 | 21483, 18865 | With base 12000 both are 178 high (168 before the 6% Undaunted Mettle); with the old 7958 both were 3874 short. One shared flat is off: the Prismatic Defense glyph total (2170 assumed), Lunar Blessings (915 from skills.csv) or the CP passives (520). |
| Max Health | 32701 | 29788 | 2913 short. Base 16000, 122 per point, Orzorga's Smoked Bear Haunch 3080 and the +5000 Battle Spirit health are all unverified, so the gap cannot be split yet. |
| Recoveries | 511, 1433, 1515 | 569, 1343, 1473 | Health: the game halves a value near 1022, the engine 1137. Magicka and Stamina need different flats to fit, so a percent source is off as well (Flourish 20%, Evocation 4%, Wind Walker 16%). |
| Critical Chance | 27.4% | 15.5% | Exactly 12% (2629 rating) above every known passive source: Major Savagery and Major Prophecy were active. Source not in the build (potion or group buff). |
| Critical Resistance | 2404 | 1084 | 1320 above Resilience (660) and Rallying Cry 3 piece (424). No known source; Rallying Cry 5 piece (1650) is a proc. |
| Resistances | 21689, 22415 | 20864, 21590 | Both 825 short. Armor piece ratings are unverified community values. |
| Penetration | 4879 | 4882 | 3 high. Lover 2744 with two Divines pieces; likely rounding per piece. |
| Costs | bash 655, block 996, break free 4921, roll 3248, sprint 428 | 1157, 930, 2698, 2306, 335 | Base costs are unverified; break free and roll dodge run far above the assumed bases even after reductions, so the bases are wrong, not the reductions. |
| Bash Damage | 685 | 120 | The sheet shows total bash damage, the engine only the bonus. Needs the base bash damage. |
| Sprint Speed | 154% | 184% | Base sprint speed assumed 160% + Athletics 12% + Hasty; the sheet suggests a lower base or a different stacking. |
| Healing Done | 22% | 2% | Combat Medic (+20% near a Keep) was active at the gate. Location dependent, correctly a proc. |
| Damage Done | 6% | 0% | The sheet folds Deadly Aim (single target, 6%) into every damage type; Physical and Shock read 11% with Energized. The engine keeps conditional damage out of Damage Done. |

A naked reading (no gear, no food, no Cyrodiil, both panels) settles base stats, per point values, base recoveries, base costs, base bash damage and sprint speed in one go; a second reading with only the seven Prismatic Defense pieces on then settles the glyph and armor values.

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
| (none yet) | | |
