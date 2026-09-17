---
name: archive-check
description: Verify an ESO value or mechanic against this repository's archive (patch notes, esolog table, UESP tables, sets and skills CSVs, fixtures) and record the result with a citation. Use before changing any constant, parser rule or engine formula, and whenever a number's source is "UNVERIFIED" or "community".
---

# Archive check

The archive is the only authority. Never use memory of the game for a number. The order of
authority, newest wins inside each source:

1. **Patch notes** (`data/patch-notes/html`, 205 notes 2015-06-23 to 2026-08-10). A later note
   overrides an earlier one and overrides every table below, because the tables are snapshots.
2. **In game readings** (`engine/tests/fixtures/*.fixture.json`, photos in `fixtures/photos`).
   These are the newest data of all (2026-09) and beat every table for anything the character
   sheet shows. Use the `fixture-calibration` skill to add or fit one.
3. **esolog coefficient table** (`data/reference/tables/esolog_skill_coefficients_t00.csv`,
   Update 44, November 2024): exact numbers for ability tooltips, food buffs, scribing.
4. **UESP tables** (`data/reference/tables/uesp_Online_*.csv`, indexed in
   `data/reference/tables_index.json`; `data/reference/sets.csv`; `data/reference/skills.csv`).
5. Community values. Allowed only as a placeholder marked `UNVERIFIED` with the alternatives
   listed, and only when 1 to 4 say nothing.

A value is "verified" only when a source above says the number, or a fixture pair pins it.
A fit from a single reading is `UNVERIFIED` with the fit written out (see the constants for
examples). "Data beats community values, the newest patch note wins."

## 1. Patch notes

Build the searchable text once per session (git ignored, rebuilt only when the html changes):

```
python3 tools/patch_notes_text.py
```

Then search whole sentences. The three digit prefix of the file name is the manifest sequence
number (`data/reference/manifest.csv`) and the date follows it:

```
grep -h -o "[^.]*Critical Resistance[^.]*\." .cache/patch-notes-text/* | sort -u
grep -l "baseline of 20% Critical Damage Reduction" .cache/patch-notes-text/* | sed 's|.*/||'
```

Rules that came from being wrong before:

- Search several phrasings. ZOS names things differently over time: "Glyph of Physical Harm"
  is the Weapon Damage jewelry glyph; "Class Mastery" scripts became "Class Flourish";
  "Healing Absorption" became "Trauma".
- Always look for a later note on the same thing before citing. List hits with the file prefix
  and take the highest number: `grep -l "cost of Block" .cache/patch-notes-text/* | sort | tail`.
- A note that names a value settles it (block cost 1730 in note 053). A note that does not name
  the current value settles nothing, however strongly worded (the Battle Spirit 5000 Health notes
  were about pets; the player value is 1600 by fixture).
- Read the sentence in context when the hit is short; `grep -B3 -A3` on the file.

Cite as: `data/patch-notes/html NNN (YYYY-MM-DD): <the sentence>`.

## 2. esolog table

One row per ability rank or buff: `Skill Name, ID, Mechanic, Class, Skill Line, Set Name, #,
Description, Equations`. Placeholders `<<n>>` in the description are defined in the equations
column as `a MaxStat + b MaxPower + c` or `N (Constant)`.

```
grep -i "^Smoked Bear Haunch," data/reference/tables/esolog_skill_coefficients_t00.csv | cut -c1-300
```

- Food and drink buffs are listed at a lower level: multiply the constants by **1.1735** for
  CP160 gold (`FOOD_SCALE` in `tools/build_constants.py`; checked against Bewitched Sugar Skulls
  4620/4250/462 and a fixture fit of Smoked Bear Haunch).
- Scribing rows carry the script in the ID: `500` + focus script number (2 digits) + grimoire
  number (3 digits).
- Tooltip numbers scale with the sheet: MaxStat is the relevant max resource, MaxPower the
  weapon or spell damage. Phase 1 does not compute them; phase 2 will.

Cite as: `tables/esolog_skill_coefficients_t00.csv row '<Skill Name>'`.

## 3. UESP tables, sets, skills

- Find the table: `grep -n '"page": "Online:Traits"' -A 12 data/reference/tables_index.json`
  gives the csv file and header. Pages that settle sheet mechanics: Traits (t00 to t04: armor,
  weapon, jewelry traits by quality), Mundus Stones, Champion (per star: text, cost, stages),
  Buffs and Debuffs (Major and Minor values, and the Scribing affix tiers), Movement Speed,
  Campaigns (Battle Spirit text), Armor and Weapons (traits only, no ratings), Enchanting (no
  glyph magnitudes), Food and Drinks (scaling tables for plain recipes), Scribing (t00 to t03,
  grimoires and the three script tables).
- `sets.csv`: `bonus_N` is the N piece bonus. A range like `9-424` runs from level 1 to CP160
  gold; the top of the range is the value. Monster sets use bonus_1 and bonus_2, mythics bonus_1,
  arena weapons bonus_2. `ESO Quality Color.2 == Mythic` marks mythics; `settype` gives the weight
  lock. sets.csv sometimes drops a leading sentence of a tooltip (Stormweaver's Cavort); the
  parser carries an override with the in game text.
- `skills.csv`: one row per base skill; the morphs are in `morph1name`/`desc1` and
  `morph2name`/`desc2`, passives in `desc`/`desc2`/`desc3` (the newest non empty one wins). Rank
  brackets `[a / b / c / d]` are ranks I to IV; the last is the value.
- Champion stars say "per stage"; the parser multiplies by the star's stage count from the
  Champion table. Slottable stars apply only when slotted; passives are always maxed.

Cite as: `tables/<file>.csv row '<row name>'`.

## 4. What the sheet means (settled by fixtures, do not relitigate)

- Critical Damage and Critical Healing show the bonus above the 50% base.
- Healing Taken, Damage Taken and Shield Strength leave Battle Spirit out; Health Recovery
  includes its halving; Battle Spirit adds 1600 Max Health before percent bonuses.
- Damage type percents are damage done + the single target Champion star + the type's own bonus.
- Elemental resistance percents are spell mitigation (rating / 660), Disease, Poison and Bleed
  physical mitigation. Critical Resistance starts at 1320 for everyone.
- Sprint Speed is 140 plus sprint bonuses only; Block Move Speed 42; Sneak Speed 60 plus armor.
- Costs: flat reductions first, armor passives add up, a weapon passive multiplies (block);
  sneak cost multiplies per source. Bases: block 1750, sprint 500, bash 765, break free 5400,
  roll dodge 4040 (roll dodge stacking still open).
- "While slotted" applies on the active bar; "when slotted on either bar" on both.
- Small armor pieces carry 40.3% of a large piece's glyph value.
- Jewelry harm glyphs give Weapon and Spell Damage.

## 5. Record the result

1. Constants: edit `tools/build_constants.py` (never `engine/data/constants.json` by hand) and use
   `sourced(value, source, note)` or `unverified(value, note, [alternatives])`; run
   `npm run constants`. Every entry needs a `source`.
2. Effects: edit `tools/parse_effects/grammar.js` or an override in `tools/parse_effects/index.js`
   with a comment naming the source; run `npm run effects` and check the coverage line did not drop.
3. Engine formulas: comment the fixture or note that settled them; add or update a test in
   `engine/tests/engine.test.js` (naked stub data) or the real data tests.
4. `UNKNOWNS.md`: move the row to the settled table or add a row with the gap. `DECISIONS.md`:
   one line for any rule of interpretation.
5. `npm run build`, `npm test`. Commit with the source in the message.
