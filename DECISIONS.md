# DECISIONS

Short record of modelling choices. One line each, newest at the bottom.

## Scope

- Phase 1 computes the character sheet only. No combat, no targets.
- Fixed: level 50, CP160 gear, gold quality, set ranges resolve to the maximum ("6-300" is 300). Quality per item is reserved in the schema (`quality: "gold"`) for a later revision, as is a proper set bonus scaling formula.
- Out of scope this phase because they need a target or combat state (listed so they are not forgotten): damage done vs a specific target, penetration vs target resistance, Bloodthirsty trait, execute bonuses, Off Balance, status effect chance, Enemy Keep and Scroll bonuses, Emperorship, Empower, all 5 piece and 1 piece proc effects, weapon glyph procs, Major or Minor buffs from casting abilities, potions, Vengeance campaign stat standardisation, scribing signature scripts, companion skills.

## Data

- `data/patch-notes/html` is missing from the repository (only the manifest is present) and the build environment has no network. Patch notes could not be consulted. Wherever a patch note would have decided a value, UNKNOWNS.md says so.
- UESP tables are treated as the truth for anything they hold. Community values fill the gaps and are flagged `verified: false`.
- Set piece count comes from the bonus column index in sets.csv: `bonus_N` is the N piece bonus. Monster sets are `bonus_1` and `bonus_2`, mythics `bonus_1`, arena weapons `bonus_2`, 12 piece sets up to `bonus_12`.
- Perfected sets are separate set names in sets.csv ("Perfected Saxhleel Champion"), so the build references the perfected name instead of carrying a flag.

## Build inputs

- Attribute points must sum to 64. The engine reports an error otherwise but still computes.
- Champion Points on: every non slottable star at max rank, four slottable stars per constellation at max rank. Off: nothing at all. Slottable stars are the "Active Perks" and "Base Active Perks" rows of the UESP Champion tables.
- All passives the character has access to are assumed purchased at max rank (`passives.mode: "all"`), with an exclusion list. Access: the three class lines (subclassing supported via `classSkillLines`), racial line, all three armor lines, all six weapon lines, Fighters Guild, Mages Guild, Psijic Order, Undaunted, Assault, Support, Soul Magic, Vampire (stage above 0), Werewolf (flag). Legerdemain, Dark Brotherhood, Thieves Guild, Scrying, Excavation and crafting lines have no sheet effects and are ignored.
- Class Mastery passives (Update 50) are attached to their class and default on. See UNKNOWNS.md.
- Weapon line passives that say "with X equipped" apply per bar based on that bar's weapons. Armor passives count pieces across the seven armor slots; the shield does not count as armor for piece counts.
- A two handed weapon counts as two pieces of its set and only on the bar it is equipped on. One handed weapons and shields count as one piece on their bar.
- At most one mythic item. Monster sets only on head and shoulders. Arena weapon sets only on weapons.
- Vampire stage effects (Health Recovery, ability costs) come from the UESP Vampire table; Unnatural Resistance softens the recovery penalty.
- Werewolf passives marked "while in werewolf form" only apply when `werewolfForm` is true. The sheet in human form does not show them.
- Battle Spirit: the confirmed UESP effects. The flat +5000 Max Health is behind a flag, off by default, until a PvP zone fixture settles it. Effects that state a different value against Battle Spirit targets are stored as conditional effects and only the sheet-facing value is applied.
- Food: catalog ids in constants.json, or a custom object typed straight from the tooltip, because food magnitudes are the least verifiable constants.

## Engine

- Order of operations is documented in `engine/src/engine.js` (header comment) and every uncertain point is a named strategy in `STRATEGIES` so it can be switched during validation.
