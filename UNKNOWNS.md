# UNKNOWNS

Values the engine needs that could not be sourced from `data/reference`. Each
one is used with the best community-known value, is flagged `verified: false`
in `engine/data/constants.json`, and stays here until a fixture read from the
game settles it. When a fixture settles a value, move it to the "Settled"
table at the bottom with the fixture name.

## Missing inputs

| Item | Status |
| --- | --- |
| `data/patch-notes/html` | Not in the repository. Only `data/patch-notes/manifest.csv` (202 rows) is present. Every "newest patch note wins" check below is therefore pending. No outbound network in the build environment, so the notes could not be fetched. |
| UESP prose pages (Health, Magicka, Stamina, Combat, Attributes, Enchanting glyph tables, Armor values) | Archived as PDF only; PDFs are not in the repository. Only the wiki tables (`data/reference/tables`) are. |
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
| Critical Damage cap | 125% | | Class Mastery "Above and Beyond" raises it by 30 per skills.csv |
| Resistance per 1% mitigation | 660 | | |
| Resistance cap | 33000 (50%) | | |
| Block cost | 1730 | 2160 | |
| Block mitigation | 50% | | |
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
| Precise trait | 3.6% / 7.2% converted at 219 per percent | UESP gives a percent; the tooltip may give a rating. |
| Armor Infused trait | 25% | UESP Traits and Armor tables say 25% at gold, UESP Enchanting table says 20%. |

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
| Increase Bash Damage | 258 |
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
| Witchmother's Potent Brew | 2856 Health, 3161 Magicka, 315 Magicka Recovery | |
| Dubious Camoran Throne | 2856 Health, 3161 Stamina, 315 Stamina Recovery | |
| Jewels of Misrule | 3326 Health, 315 each recovery | |
| Lava Foot Soup-and-Saltrice, Ghastly Eye Bowl | 3080 max + 338 recovery | |
| Orzorga's Smoked Bear Haunch | 3080 Health, 338 each recovery | |
| Green recovery drinks | 565 (Magicka, Stamina), 621 (Health) | From Crown item descriptions that mention "Veteran Rank 10", so the era is old. |

## Systems

| Item | Value used | Note |
| --- | --- | --- |
| Champion Point cap | 3600 total, 1200 per constellation | Passive stars total 320 (Warfare), 342 (Fitness), 800 (Craft) points, so every passive can be maxed with four 50 point slottables to spare in each constellation. Craft has two 75 point slottables; still fits. |
| Battle Spirit flat +5000 Max Health | Off by default (`flags.battleSpiritFlatHealth`) | Referenced in 2016 to 2019 patch notes, not listed by UESP now. |
| Class Mastery passives (Update 50, patch 12.0.0) | Treated as ordinary passives of their class, all on by default | Activation rule (all five active, or one chosen) is unknown. |
| Dual wield off hand contribution | 6% of off hand damage (Dual Wield Expert) | skills.csv tooltip. |
| Werewolf form stat changes beyond passives | none modelled | |

## Settled by fixtures

| Constant | Settled value | Fixture |
| --- | --- | --- |
| (none yet) | | |
