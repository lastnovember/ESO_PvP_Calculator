# UNKNOWNS

Values the engine needs that no archive source settles. Each one is used with
the best value on hand, is flagged `verified: false` in
`engine/data/constants.json`, lists the searches that were tried (the
archive-lookup skill: tables_index.csv, pages_index.csv, entities.csv and
patch_history.csv, data/patch-notes/text), and stays here until a source or a
fixture read from the game settles it. When something settles a value, move it
to a "Settled" table at the bottom with the citation.

## Missing inputs

| Item | Status |
| --- | --- |
| `data/patch-notes/html` | Present (202 notes, 2015-06-23 to 2026-08-10, `data/patch-notes/manifest.csv`; searchable text in `data/patch-notes/text`). Base character numbers (naked stats, points, ratings per percent, Roll Dodge, Break Free, Sprint and Bash costs, item armor and weapon ratings) never appear in a console patch note; the UESP pages carry most of them. |
| UESP system pages | Archived as Markdown in `data/reference/pages` (`pages_index.csv`, fetched 2026-09-12 to 2026-09-19), tables in `data/reference/tables` (`tables_index.csv`). Pages whose wiki template values did not render (pages/depth/Rubedite_Weapons.md, Ruby_Ash_Weapons.md: empty damage cells) are listed where they matter below. |
| esoapi.uesp.net data version | v101044 (Update 44, November 2024) per `tools/ARCHIVE_README.md`. Six updates behind live. |

## Open constants

| Constant | Value used | Why it is open | Searched |
| --- | --- | --- | --- |
| Block Move Speed with a shield (`base.blockMoveSpeedShieldBonus`) | 12 (54 on the sheet) | One reading (fixture 008) with Battlefield Mobility; the passive text (penalty 36%) would give 64. Kept as a fit. | pages/Movement_Speed.md row "One Hand and Shield: Reduces the blocking speed penalty to 48/36%"; `grep -i block data/reference/tables_index.csv` (none); data/patch-notes/text "Battlefield Mobility" (no number that fits). A second shield reading settles it. |
| Armor rating below gold (`items.qualityFactor`) | purple 0.96, blue 0.92, green 0.88, white 0.84 of gold | Community steps; no archived armor rating by quality. Weapons no longer use this (Nirnhoned tables). | `grep -i armor data/reference/tables_index.csv` (uesp_Online_Armor_t01 is the trait table); pages/Armor.md (no ratings); pages/depth/Rubedite_Ore.md, Rubedo_Leather.md, Ancestor_Silk.md tables (ingot counts, not ratings); data/patch-notes/text "armor rating" (none by quality). One reading with a single purple armor piece settles it by differencing. |
| Derived armor slot values (`items.armor`: medium and light chest, heavy and medium hands and waist) | chest 2084 / 1396, hands 1386 / 1042, waist 1039 / 781 | Not read from a tooltip; derived from the DK's read pieces with the slot factors 0.875 / 0.5 / 0.375 (truncated) and the 688 step between weights. | Same searches as the row above; the six read slots are in constants.json with the tooltips. A tooltip of any derived piece settles it. |
| Precise trait on the sheet (`STRATEGIES.preciseTrait`) | rating (3.6% x 219) | Whether the sheet applies Precise as rating or as a percent is not stated. | tables/uesp_Online_Weapons_t01.csv row 'Precise' (percent only); data/patch-notes/html 093 (2020-09-15, the percent); no reading on file carries a Precise weapon. |

## Systems

| Item | Value used | Why it is open | Searched |
| --- | --- | --- | --- |
| Mora's Whispers, Thrassian Stranglers | not modelled | Crit by books collected and Weapon Damage by kill stacks are character state the build cannot express. | sets.csv bonus_1 texts (the rule is in the text; the state is not a build field). |
| Cyrodiil scroll and keep bonus stacking | percents from tables/uesp_Online_Campaigns_t06..t08.csv | Whether the scroll and keep percents multiply the sheet total or add to the other percents is not stated; no reading carries one. | pages/Campaigns.md and pages/depth/Elder_Scrolls.md (effects only); data/patch-notes/text "scroll bonus", "keep bonus" (values, no stacking rule). |
| Werewolf form stat changes beyond passives | none modelled | The sheet in werewolf form is not read. | `grep -ic 'werewolf form' data/reference/skills.csv` (10 passive rows, all modelled); pages/Werewolf.md (no sheet values); no fixture in werewolf form. |
| Roll Dodge Cost stacking | flat first, then additive percents | No stacking order fits all three geared readings (see Open gaps). | pages/Combat.md (cost depends on level, no formula); skills.csv Athletics, Light and Heavy Armor passive texts; data/patch-notes/text "Roll Dodge" with "cost" (none). |

## Item quality

| Item | Status |
| --- | --- |
| Glyph values below gold | Searched: pages/glyphs/*.md Truly Superb rows, tables_index.csv "Glyph" (no small piece rows). Large armor pieces and jewelry read the per quality rows of the UESP glyph pages (verified). Small armor pieces at white to purple are derived as 0.4043 of the large value truncated, the rule the gold readings follow (`enchants.glyphSmallRatio`); a reading with one non gold small glyph settles whether the game truncates the same way there. Increase Bash Damage below gold uses `enchants.glyphQualityFactor` because its page is stale (pre Greymoor 348 Weapon and Spell Damage). |
| Set bonus types with no quality table | Offensive Penetration ("34-1487", 69 bonuses) and Critical Resistance (27 bonuses) ranges have no CP160 by quality row: Online:Craftable Sets tables t03 to t08 cover recovery, Max Magicka or Stamina, Max Health, damage, critical and resistance only. Searched: `grep -i penetration data/reference/tables_index.csv` (0 hits), `grep -i 'penetration\|critical resistance' data/reference/pages_index.csv` (Online:Penetration and Online:Critical Resistance, prose only, no ranges), `grep -i 'set bonus' data/patch-notes/text` (no quality values). Below gold these bonuses keep the gold value and the engine adds a note. |
| Which piece sets a mixed quality set's bonus | `STRATEGIES.setBonusQuality`, default lowest piece on the bar, alternative highest piece. Searched: `grep -rhi 'lowest\|highest' data/reference/pages/Sets.md data/reference/pages/Craftable_Sets.md` (nothing), `grep -rhi 'set bonus' data/patch-notes/text | grep -i 'qualit\|lowest\|highest'` (nothing), `grep -rhi 'mixed qualit\|different qualit' data/patch-notes/text data/reference/pages` (nothing), forum threads with "set bonus" (three, none on quality). A reading with one purple piece in an otherwise gold five piece set settles it. |

## Scribing

| Item | Status |
| --- | --- |
| Vault and Physical Damage | The UESP Scribing page (2026-09-14) shows no Vault icon on the Physical Damage focus row, while the esolog table (Update 44) still has Sundering Vault. The newer page wins, so the picker does not offer Physical Damage on Vault. If the game does, say so and the row gets a per script override. Searched: tables/uesp_Online_Scribing_t01.csv row 'Physical Damage'; tables/esolog_skill_coefficients_t00.csv rows 'Sundering Vault'; data/patch-notes/text "Vault" (no script list). |
| Affix tiers on new pairs | The Major or Minor tier of an affix on a grimoire comes from the UESP Buffs and Debuffs pages, which predate the Scribing page. Pairs the Buffs pages do not list (Interrupt, Off Balance, and a few grimoire and affix pairs added since) show without a tier. Scripts change no sheet value in phase 1, so this is a label only. Searched: tables/uesp_Online_Buffs tables and tables/uesp_Online_Scribing_t03.csv (no tier column). |

## Open gaps across the ten readings (2026-09-19, after the glyph pages and the bash formula)

Every reading now matches 43 to 56 of its numbers (`engine/tests/fixtures/INDEX.md`). What is left, in every case the same on both bars of a character:

| Gap | Readings | Game vs engine | Best reading of it |
| --- | --- | --- | --- |
| Templar ring1 glyph | Templar 005 and 006 | engine 106, 0 and 31 high on the three recoveries | The Prismatic Recovery glyph is 84 per recovery (tooltip image, 2026-09-19), and this sheet is exact with nothing from ring1 (Health 415, Magicka 1411 and 1389, Stamina 1785 with Roksa the Warped's 70 counted). So ring1 carries a glyph with no main sheet stat; the same image shows Reduce Skill Cost (133 prismatic cost). Pending the user's word on which glyph the ring has; the build keeps the exported value until then. |
| Resistances | Yeets 21689 (engine 21692), Templar 16765 (16837) | 3 and 72 | The DK's tooltips (2026-09-19) settle the slot values and the DK and Necro read exact. The Templar's 72 is 4% of one medium big piece, a purple shoulders or feet. Yeets' 3 sits on the derived medium waist (781). Medium and light chests and the small heavy and medium pieces are derived from the 0.875 / 0.5 / 0.375 factors, not read. |
| Roll Dodge Cost | Yeets 3248 (engine 3306), DK 3315 (3344), Necro 3420 (exact), naked 3800 (exact) | | Base 4040 is fixture sourced: the naked reading 003 shows 3800 with Tumbling's 240 (Champion table: 120 per stage, two stages) taken off, and UESP documents no base. Per piece: Athletics 4% medium (pages/skills/Athletics.md rank 2), Heavy Armor Penalties +3%, Light Armor Bonuses -3% (passive texts). No stacking order fits all three geared readings: flat first then additive percents gives the Necro exactly and the DK 29 high; percents first then the flat gives the DK exactly and the Necro 24 low; Yeets (four medium) fits neither, and a grid over per piece values 3 to 5 / 0 to 4 / 0 to 4 with additive or multiplicative groups leaves a total error of 7 at best with unnatural values. A fourth geared reading with a different medium count (the Templar with Expert Evasion unslotted: 3 heavy, 3 medium, 1 light) would separate the models. |
| Weapon and Spell Critical | Necro 19.4 and 16.4 (engine 18.5 and 15.5) | | One percent (about 206 rating) on both bars from no archived source. |
| Physical and Bleed Damage | Templar front bar 10 and 5 (engine 5 and 0) | | A buff running out during the photos (the same reading carries Major Brutality and Sorcery in its first photo). |
| Yeets back bar naked (004) | Max Health 21236 (19305), resistances 6003 (1730) | | 10% Max Health and 4272 resistance from something slotted on that bar; no archived "while slotted" text on Bull Netch, Hurricane, Resolving Vigor, Streak, Wield Soul or Temporal Guard gives it. |
| Penetration | Yeets 9491 and 4879 (engine 9494 and 4882) | | Two Divines pieces round per piece. |

## Settled by data supplied later

| Item | Settled by |
| --- | --- |
| Every glyph magnitude (Magicka and Stamina 868, recoveries 169, costs 203 and 133, resists 3520, Decrease Physical and Spell Harm 927 resistance, Potion Speed 5 s, Potion Boost 3.6 s, harm glyphs 174) | pages/glyphs, the per glyph UESP pages in the 2026-09-19 archive (Truly Superb row). |
| Bash Damage formula | esolog Bash row (0.0224424 x MaxResist) plus fixtures 001 to 010: flat bonuses + 0.02252 x average resistance, times the physical and direct damage percents. |
| Glyph of Health 954 and the glyph quality steps (white 734, green 774, blue 839, purple 882) | Glyph table image supplied by the user, 2026-09-19, saved with the fixture photos. The 984 typed earlier was a misread. |
| Prismatic Recovery 84 each, Reduce Skill Cost 133 | Glyph tooltip image supplied by the user, 2026-09-19, saved with the fixture photos. |
| Armor ratings by weight and slot, Reinforced 16%, glyph large and small values, Markyn 1157 per set, Essence Thief, two handed 1571 | The DK's gear tooltips typed by the user, 2026-09-19 (fixture 009 `tooltips`). Slot factors 0.875 / 0.5 / 0.375 of the chest; heavy chest 2772, medium big 1823, light big 1221, light hands 698, light waist 523 read; chests and small heavy and medium pieces derived. |
| Scribing script catalog (21 focus, 20 signature, 26 affix, and which grimoires take each) | UESP Online:Scribing page printed 2026-09-14, archived as `data/reference/tables/uesp_Online_Scribing_t00..t03.csv` by `tools/extract_scribing_pdf.py` (manifest seq 220). Class Mastery is Class Flourish now (patch note), Passive Master reads Wayfarer's Mastery and Healing Absorption reads Trauma on the page; old build files are mapped on load. |
| Rakkhat's Voidmantle, Stormweaver's Cavort slots and text | In game tooltips supplied by the user (medium shoulders, light legs, plus the missing 300 Magicka Recovery line). |

## Settled by patch notes

| Constant | Settled value | Note |
| --- | --- | --- |
| Harm glyph recovery | Spell Harm (Spell Damage) 10 Magicka Recovery, Physical Harm (Weapon Damage) 10 Stamina Recovery at every quality, scaled by Infused (16) | 135, 2023-03-28 (Update 37). Closes the Magicka Recovery gap on all four characters: Yeets and DK 42 (plain plus two Infused), Necro 30, Templar 26. |
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
| Food Magicka and Stamina values | truncated, not rounded (Bear Haunch recovery 369 = 315 x 1.1735 = 369.65 cut) | 001 and 002: the same jewelry reads 1433 = 1156 x 1.24 on the back bar and 1457 = 1156 x 1.26 on the front bar, which pins the pre-percent sum at 1156; 370 would read 1434 |
| Roksa the Warped 1 item | 70 Health, Magicka and Stamina Recovery, counted | 005 and 006 (with the Prismatic Recovery ring at 0) |
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
| Medium and light armor | replaced by the DK's tooltips, 2026-09-19 | 009 |
| Damage Done line | folds the single target star | 001 to 004 |
| Two handed melee weapon damage | 1571 (UESP Nirnhoned page CP160 row, forum 348673); staves, bows and one handed 1335 | pages, 002 to 010 for the 1335 |
| Emperor passives | Domination, Monarch, Emperor by home keeps (UESP Emperor page) | pages |
| Gaze of Sithis, Velothi | full texts parse from the rebuilt sets.csv (3276 Health, 1025 Health Recovery, 4000 Armor, block 0; 1650 penetration, Minor Force) | sets.csv 2026-09-17 |
| Food health scale | 1.17442 for Max Health and Health Recovery, 1.1735 for Magicka and Stamina (Sugar Skulls 4624/4250, Bear Haunch 4316) | 002, 005, 009 |
| Critical Healing sources | Dexterity, Fighting Finesse, The Shadow (not Piercing Spear, Twin Blade and Blunt, Advanced Species, Hemorrhage, Feline Ambush counts) | 002, 003, 005 |
| Sneak Speed with Dark Stalker | 100 | 005 |
| Disease and Poison Resistance | physical rating plus Resist Affliction 2310, over 660 | 005 |

## Settled by the archive pages (audit of 2026-09-19)

| Constant | Settled value | Source |
| --- | --- | --- |
| Max Health, Magicka, Stamina at level 50 | 16000, 12000, 12000 | pages/Health.md line 12, Magicka.md line 12, Stamina.md line 12 (and the formulas on line 19); fixture 003 |
| Attribute points, per point values | 64 points; 122 Health, 111 Magicka and Stamina | pages/Health.md line 12, Attributes.md line 24, Magicka.md and Stamina.md line 12 |
| Base recoveries | Health 309, Magicka 514, Stamina 514 | pages/Health.md, Magicka.md, Stamina.md line 24; fixture 003 (the 484 seen in community sources is nowhere in the archive) |
| Critical Chance base and rating | 10%; 219 per percent (MCV 21912 at CP160) | pages/depth/Weapon_Critical_effect.md and Spell_Critical_effect.md; data/patch-notes/html 100 (2021-03-15): 657 rating = 3% |
| Critical Damage base and cap | 50%, cap 125% | pages/Critical_Damage.md; data/patch-notes/html 111 |
| Resistance cap and per percent | 33000 = 50%, 660 per percent | pages/depth/Physical_Resistance.md and Spell_Resistance.md; every fixture's mitigation percents |
| Weapon damage by quality | one handed 1037 / 1072 / 1108 / 1132 / 1335, two handed 1220 / 1262 / 1304 / 1332 / 1571, Nirnhoned 1151 to 1535 and 1354 to 1806 | tables/uesp_Online_Nirnhoned_t01.csv and t02.csv row '160' |
| Set bonuses by quality | six types, tables t03 to t08 | tables/uesp_Online_Craftable_Sets_t03..t08.csv row '160'; pages/Craftable_Sets.md line 511 |
| Weapon and Spell Damage with no weapon | 1000 | fixture 003 (naked): no page or note states it |
| Block Mitigation base | 50 | fixtures 002, 003, 005 (52, 54, 55 with the Champion percent and heavy pieces); no page or note states it |
| Block Move Speed, Sneak Speed, Sneak Cost | 42, 60, 118 | fixtures 001 to 004 (naked and geared), 002, 005, 007; no page or note states them |
| Slottable stars per constellation, Champion cap | 4, 3600 | pages/Champion.md lines 88 and 9; data/patch-notes/html 100 |
| One mythic, monster set slots, two handed weapon as two pieces | 1; head and shoulders; 2 | pages/Sets.md; pages/Weapon_Sets.md line 7 |
| Poison overrides the weapon enchant | yes, until depleted | pages/Poisons.md |

