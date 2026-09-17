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
| Armor and weapon rating by quality | `items.qualityFactor` purple 0.96, blue 0.92, green 0.88, white 0.84 of gold are community steps. One reading with a single purple armor piece and one with a purple weapon settle them by differencing. Trait values by quality are verified (UESP trait tables). |
| Vault and Physical Damage | The UESP Scribing page (2026-09-14) shows no Vault icon on the Physical Damage focus row, while the esolog table (Update 44) still has Sundering Vault. The newer page wins, so the picker does not offer Physical Damage on Vault. If the game does, say so and the row gets a per script override. |
| Affix tiers on new pairs | The Major or Minor tier of an affix on a grimoire comes from the UESP Buffs and Debuffs pages, which predate the Scribing page. Pairs the Buffs pages do not list (Interrupt, Off Balance, and a few grimoire and affix pairs added since) show without a tier. Scripts change no sheet value in phase 1, so this is a label only. |

## Fixtures 001 to 003 (Yeets-Swiftly: 001 geared back bar in Cyrodiil, 002 geared front bar outside, 003 naked front bar outside)

The naked reading fixed the base values (DECISIONS.md and constants sources). Everything on the naked main sheet, and Max Magicka, Max Stamina, Critical Chance, Critical Damage, Critical Resistance, block, bash, break free and sprint costs and Sprint Speed on the geared sheets, now match. Still open:

| Reading | Game | Engine | Gap and best reading of it |
| --- | --- | --- | --- |
| Max Health, geared | 30001 (002), 32701 (001) | fitted | Base 16000 and 122 per point are settled; the geared gap was the food. Orzorga's Smoked Bear Haunch is now 4316 Health (fitted) with the Prismatic small piece at 192; the tooltip would confirm both. |
| Recoveries, geared | 1022, 1457, 1515 | 1022 with food 406; Magicka fits 411, Stamina 369 | Base 514/514/309 are settled by the naked sheet. The food's three recovery values do not fit one number with Evocation 4% and Wind Walker 16%, so either the food differs per stat or one of those passives is off. Tooltip wanted. |
| Weapon and Spell Damage, dual wield | 4362 | 4107 | Naked and staff bar are exact (base 1000). Dual wield is 236 short before the 8%: main hand 1335 x 1.15 Nirnhoned plus 6% of the off hand leaves 236. Mace traits and hands to confirm. |
| Resistances, geared | 18413 and 19139 | 17588 and 18314 | 825 short on every geared reading, naked is exact (Fortified 1730). Armor piece ratings (unverified) or Markyn's per set armor; an armor only reading splits it. |
| Penetration | 3444 naked, 9491 geared | 3444, 9494 | Naked exact (Lover 2744). Geared 3 high: the two Divines pieces round per piece. |
| Roll Dodge Cost | 3800 naked, 3248 geared | 3800, 3306 | Base 4040 settled. The geared reduction is 14.5%, not the 13% the passives add up to (Athletics 16, light 3, heavy +6); percent then flat with multiplicative groups gives 3250. Open. |
| Block Mitigation | 52 naked, 54 and 64 geared | 52, 53, 63 | 2% more from armor than heavy armor's 1% per piece gives. Open. |
| Bash Damage | 184 naked, 630 maces, 685 staff | 120 | The sheet shows total bash damage and it depends on the weapon; only the bonus is modelled. |
| Damage Done | 11% | 5% | The sheet folds Deadly Aim (single target) into every damage type. Intended difference. |
| Sneak Cost | 59 naked, 34 geared | not modelled | |
| Back bar naked (fixture 004): Max Health 21236, Resistances 6003 | 19305 x 1.10 and 1730 + 4272 | 19305, 1730 | With Bull Netch, Hurricane, Resolving Vigor, Streak, Wield Soul and Temporal Guard slotted and nothing equipped, the sheet shows 10% more Max Health and 4272 more resistance than the front bar. The archived skill texts (Update 44) and every note through 2026-08 have no "while slotted" health or resistance on these abilities; Resolving Vigor's Minor Resolve (2974) is "after casting". Tooltips of Resolving Vigor and Hurricane, and the rest of the Active Effects list below Major Prophecy, would settle it. The other 22 readings of that bar match. |

## Fixture 005 (Templar, Lastnovember: geared front bar, dual axes, Elden Root, vampire stage 3)

27 of 51 readings match, including Max Magicka and Stamina, penetration, crit chance, Critical Damage, Critical Resistance, bash, block and break free costs, Block Mitigation, Sprint Speed, Sneak Speed, Healing Done and Taken, Critical Healing and every damage type but two. Still open:

| Reading | Game | Engine | Gap and best reading of it |
| --- | --- | --- | --- |
| Weapon and Spell Damage, dual axes | 4471 | 3490 | 981 high in the game, 876 before the 12% (Agility 6 + Balanced Warrior 6). Main axe Sharpened 1335, off axe Nirnhoned 1535 x 6% (Dual Wield Expert) = 92, Expert Mage 108 (one Sorcerer ability), Mechanical Acuity 129, glyphs 174 + 278, base 1000. Fixture 002 (maces, Nirnhoned main) is 236 short with the same model, so the off hand and Nirnhoned rules are wrong in a way one reading cannot separate. A reading with only the two axes equipped, then only the main axe, would settle both. |
| Health Recovery | 415 | 848 | The engine applies Unnatural Resistance (stage 3: -25%). (309 + 141 Capacitor + 70 Roksa + 406 food) x 1.12 x 0.40 = 415 exactly if the stage 3 penalty is the plain -60% and the Prismatic Recovery ring glyph adds no Health Recovery; with the glyph's 84 it is 452. Two questions for the user: is Unnatural Resistance bought, and what does the glyph tooltip say. |
| Resistances | 16765 and 17491 (front), 20041 and 20767 (back) | 16220 and 16946, 19496 and 20222 | 545 short on both bars once Defending (3276) enters without the 6% (fixture 006 pinned that: the gap between the bars was exactly 6% of 3276). Spell = Physical + 726 (Spell Warding) is exact on both bars. Yeets reads 825 short on both bars with different armor, so the armor piece ratings (unverified community values) are the suspect; the tooltip armor value of each equipped piece (seven numbers) would replace them. Whether Resolve and Protective take the 6% is also unknown (they are multiplied now). |
| Magicka and Stamina Recovery | 1411 and 1785 | 1397 and 1804 | +11 and -15 before the percents (Evocation 4, Flourish 20, Magicka Controller 2; Flourish 20, Wind Walker 12). Yeets reads +41 Magicka on both bars and 0 Stamina. Bear Haunch tooltip and Prismatic Recovery tooltip wanted; both readings then reduce to the percents. |
| Sneak Cost | 55 | 40 | 118 x 0.79 (Improved Sneak, 3 medium) x 0.85 (Medium Armor Bonuses) x 0.5 (Sustaining Shadows) = 40; Yeets' 34 fits the same model with 4 medium. 55 = 59 x 0.93, as if the medium armor reductions were nearly absent. A naked Templar reading (59 expected) would show whether the vampire changes it. |
| Physical Damage 10%, Bleed Damage 5% (front bar only) | 10, 5 | 5, 0 | Energized gives 5% Physical and Shock, and the back bar (fixture 006) reads exactly that. The front bar's extra 5% Physical (and the Bleed 5% that read 0% on the next page) belongs to something on that bar: the two axes, Lacerate, Blood for Blood, Deep Fissure, Critical Surge, Ulfsild's Contingency (Bleed focus, Class Flourish) or Binding Javelin; no archived text gives a slotted Physical Damage bonus for any of them. Re-read at rest, and a reading with one of them unslotted would name it. |
| Roll Dodge Cost | 0 | 3572 | Expert Evasion slotted: the sheet shows 0 while the free roll is primed. The regular cost is not readable from this sheet. |
| Bash Damage | 556 axes, 608 staff | 120 | Total bash damage depends on the weapon (Yeets: 630 maces, 685 staff, 184 naked); the fixed bonus is all the engine has. Not modelled. |

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
| Critical Healing sources | Dexterity, Fighting Finesse, The Shadow (not Piercing Spear, Twin Blade and Blunt, Advanced Species, Hemorrhage, Feline Ambush counts) | 002, 003, 005 |
| Sneak Speed with Dark Stalker | 100 | 005 |
| Disease and Poison Resistance | physical rating plus Resist Affliction 2310, over 660 | 005 |
