# DECISIONS

Short record of modelling choices. One line each, newest at the bottom.

## Scope

- Phase 1 computes the character sheet only. No combat, no targets.
- Fixed: level 50, CP160 gear, gold quality, set ranges resolve to the maximum ("6-300" is 300). Quality per item is reserved in the schema (`quality: "gold"`) for a later revision, as is a proper set bonus scaling formula.
- Out of scope this phase because they need a target or combat state (listed so they are not forgotten): damage done vs a specific target, penetration vs target resistance, Bloodthirsty trait, execute bonuses, Off Balance, status effect chance, Enemy Keep and Scroll bonuses, Emperorship, Empower, all 5 piece and 1 piece proc effects, weapon glyph procs, Major or Minor buffs from casting abilities, potions, Vengeance campaign stat standardisation, scribing signature scripts, companion skills.

## Data

- Patch notes (`data/patch-notes/html`) were searched for every constant. Where they hold a value, the newest note wins and constants.json cites it by manifest number and date. Where UESP and a note disagree (armor Infused 20% vs 25%) the note wins. Base character numbers never appear in console notes and stay unverified.
- UESP tables are treated as the truth for anything they hold. Community values fill the gaps and are flagged `verified: false`.
- Set piece count comes from the bonus column index in sets.csv: `bonus_N` is the N piece bonus. Monster sets are `bonus_1` and `bonus_2`, mythics `bonus_1`, arena weapons `bonus_2`, 12 piece sets up to `bonus_12`.
- Perfected sets are separate set names in sets.csv ("Perfected Saxhleel Champion"), so the build references the perfected name instead of carrying a flag.

## Build inputs

- Attribute points must sum to 64. The engine reports an error otherwise but still computes.
- Champion Points on: every non slottable star at max rank, four slottable stars per constellation at max rank. Off: nothing at all. Slottable stars are the "Active Perks" and "Base Active Perks" rows of the UESP Champion tables.
- All passives the character has access to are assumed purchased at max rank (`passives.mode: "all"`), with an exclusion list. Access: the three class lines (subclassing supported via `classSkillLines`), racial line, all three armor lines, all six weapon lines, Fighters Guild, Mages Guild, Psijic Order, Undaunted, Assault, Support, Soul Magic, Vampire (stage above 0), Werewolf (flag). Legerdemain, Dark Brotherhood, Thieves Guild, Scrying, Excavation and crafting lines have no sheet effects and are ignored.
- Class Mastery (Update 50, note 194): each class has five passives, two Class Mastery Points exist, and the line is hidden while subclassing. The build lists up to two purchased passives in `classMastery`; the engine ignores them when `classSkillLines` are not the native lines.
- Effects that state a lower value "against targets with Battle Spirit" (Above and Beyond, Feral Cruelty) keep both values. The sheet shows the unreduced value (STRATEGIES.battleSpiritTargetValues = sheet); pvpTarget applies the reduced value when Battle Spirit is on.
- Weapon line passives that say "with X equipped" apply per bar based on that bar's weapons. Armor passives count pieces across the seven armor slots; the shield does not count as armor for piece counts.
- A two handed weapon counts as two pieces of its set and only on the bar it is equipped on. One handed weapons and shields count as one piece on their bar.
- At most one mythic item. Monster sets only on head and shoulders. Arena weapon sets only on weapons.
- Vampire stage effects (Health Recovery, ability costs) come from the UESP Vampire table; Unnatural Resistance softens the recovery penalty.
- Werewolf passives marked "while in werewolf form" only apply when `werewolfForm` is true. The sheet in human form does not show them.
- Battle Spirit: the confirmed UESP effects. The flat +5000 Max Health is behind a flag, off by default, until a PvP zone fixture settles it. Effects that state a different value against Battle Spirit targets are stored as conditional effects and only the sheet-facing value is applied.
- Food: catalog ids in constants.json, or a custom object typed straight from the tooltip, because food magnitudes are the least verifiable constants.

## Engine

- Order of operations is documented in `engine/src/engine.js` (header comment) and every uncertain point is a named strategy in `STRATEGIES` so it can be switched during validation.

## App

- One page, vanilla JavaScript, no framework, no runtime requests. The build script converts the ES module engine into a plain script and inlines a slimmed effects.json (per effect raw text dropped, bonus and passive text kept) so the page stays near 1 MB.
- Skill pickers list final nodes only (unmorphed base, or a morph) grouped by line, own class first. Passives are never picked one by one: class, racial, armor and weapon passives follow the build automatically (weapon passives follow each bar's weapons through their conditions), Vampire and Werewolf follow their toggles, and guild plus Alliance War lines are on or off as whole lines (`skillLines`). Lines with no sheet effect (crafting, Legerdemain and the like) are not shown.
- A set is offered on a slot only where it can be worn: monster sets on head and shoulders, arena weapon sets on weapons, mythics on their slot, three piece jewelry sets on jewelry and weapons. Weapon type restrictions of arena weapon sets are not enforced yet.
- Results show both bars side by side and a per source breakdown per stat, plus the list of conditional effects the sheet did not apply.
- The last edited build is restored on reload; named builds live in localStorage under one key.
- Scribing: the twelve grimoires are slottable abilities of their skill line (Torchbearer counts as a Fighters Guild ability for Slayer, and so on) with focus, signature and affix pickers. Scripts act on cast and change no sheet value this phase, so the pickers only record the choice. Focus names come from the esolog coefficient table, affix scripts from the UESP Buffs page; the catalog is partial (UNKNOWNS.md).
- Attribute points default to 0. Unspent points are not flagged at all (the page shows "N of 64" next to the heading); a total above 64 is an error.
- A monster set picked on head or shoulders fills the other slot only when it is empty; afterwards either can be changed on its own.
- Poisons: one per bar, a combat proc with no sheet effect. A poison overrides the weapon enchant while it has charges, so the page dims the enchant fields on that bar but keeps their values.
- Sets that only drop in one weight (settype Light, Medium or Heavy Armor in sets.csv) lock the weight of their armor pieces. Monster sets and "All Weights" sets stay free.
- Guild and Alliance War lines default on and are whole line toggles; Soul Magic is one of them so its abilities can be slotted.
- Champion Point pickers group slottable stars by theme (Warfare: Damage, Healing, Damage reduction, Resources. Fitness: Health and resources, Defense and shields, Utility and CC. Craft: Movement, Stealth and crime, Gathering and fishing). The grouping is a UI convenience agreed with the user and lives in the app template, not in the engine data.
- Two mythics have no slot word in their name and sets.csv gives none, so the parser carries the slot from the in game tooltip supplied by the user: Rakkhat's Voidmantle is medium shoulders, Stormweaver's Cavort is light legs. sets.csv also dropped the leading "Adds 300 Magicka Recovery" line of Stormweaver's Cavort, so the parser overrides that bonus text with the full tooltip.
- "For each X ability slotted" counts every ability on that bar whose skill line (or class, for "each Sorcerer ability") matches, ultimate slot included, morphs by their base line, scribed grimoires by their grimoire's line. Parser prose line names are mapped onto real line names ("Animal Companion" to "Animal Companions").
