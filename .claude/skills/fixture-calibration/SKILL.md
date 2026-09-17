---
name: fixture-calibration
description: Turn photos of the in game character sheet into a fixture, compare them with the engine, and settle constants from the differences. Use whenever the user sends stat sheet screenshots or asks why the app's numbers differ from the game.
---

# Fixture calibration

A fixture is one reading of one bar of one character: the build, every number on both panels of
the sheet, the active effects, and the photos. The runner (`engine/tests/fixtures.test.js`)
compares every number with the engine. Four readings of Yeets-Swiftly settled the base game
values this way (see `engine/tests/fixtures/REVISIONS.md`); follow the same steps.

## 1. Capture

Ask for, per reading: the main Attributes panel, every Advanced Stats page (they scroll), and the
Active Effects list, plus the build exported from the app (Export, or Fixture template). Record
what was on: mundus, food, location, which bar, attribute split, and anything in Active Effects.

The most useful sequence for a new character is naked (no armor, jewelry, weapons, food; mundus
may stay) on each bar, then armor only, then the full build in and out of Cyrodiil. Naked settles
base values and passives; armor only splits glyphs from armor ratings; full readings settle sets.

## 2. Transcribe

1. Copy the photos into `engine/tests/fixtures/photos/NNN-<panel>.jpg`, downscaled to 1400 px
   (Pillow in a venv: `pip install pillow`, `Image.thumbnail((1400, 1400))`, JPEG quality 72,
   apply `ImageOps.exif_transpose` first).
2. Create `engine/tests/fixtures/NNN-<who>-<state>.fixture.json` from
   `TEMPLATE.fixture.json`: `name`, `status: "open"`, `captured`, `location`, `bar`,
   `attributes`, `mundus`, `food`, `photos`, `notes` (which bar and why, what was active),
   `build` (the export; set `gear` slots to `null` when naked, a slot object with a weight counts
   as an armor piece), `readings` under `outOfPvpZone` or `inPvpZone` and `bar1` or `bar2`
   (`main` and `advanced` with the runner's labels), `sheetState` (a number the sheet shows that
   is a state, not a stat: Roll Dodge Cost 0 with Expert Evasion primed, a percent that changed
   between two pages), `sheetExtras` (every other number:
   sneak cost, block move speed, sneak speed, per type resistance and damage percents, critical
   healing, currency bonuses) and `activeEffects`.
3. Read digits twice. Percent values as numbers (27.4), currency bonuses as numbers.

## 3. Compare

```
npm test 2>&1 | sed -n '/^# NNN-/,/status open/p'
```

Every line is `ok` or `MISS game X vs engine Y`. `status: "open"` keeps the suite green while
the fixture is being worked; remove it once every reading matches.

Champion Point passive stars are per character: a cost that reads as the plain base (Sprint 470
= 500 x 0.94 with no Sprinter flat) means the star was never bought, so list it in
`championPoints.notTaken` rather than fitting a constant.

Identify the bar and the zone from the numbers before trusting the label: Weapon Damage and
Penetration differ per bar; a Cyrodiil location means Battle Spirit (Health Recovery halves,
Healing Done gains Combat Medic near a keep). Buffs in Active Effects explain crit and damage
percents (Major Savagery and Prophecy, Minor Berserk, Minor Protection).

## 4. Settle differences, in this order

1. **Sheet semantics first.** A miss on a stat the engine computes from others is usually a
   presentation rule (bonus above base, Battle Spirit excluded, single target star folded in).
   Check the settled list in the `archive-check` skill before touching a constant.
2. **Difference two readings of the same character.** Same gear and different attributes gives
   the per point value and any flat that differs between zones (Battle Spirit health). Naked
   versus geared gives glyph and set totals. Front versus back bar gives slotted effects. Only
   the changed thing can explain the difference, so one equation has one unknown.
3. **Fit only when one unknown is left**, and write the fit into the source string with the
   arithmetic (`(1750 - 40) x 0.91 = 1556`). A fit from one reading stays `unverified`; a second
   reading that lands on it promotes it to `sourced`.
4. **Do not fit two unknowns from one reading.** Put the gap in `UNKNOWNS.md` with its size and
   the candidates, and ask for the reading that separates them.
5. **Check the passive texts before inventing a source.** Every slotted, per piece and per
   ability rule lives in `engine/data/effects.json`; a missing effect is usually a grammar gap
   (`tools/parse_effects/grammar.js`), not a new mechanic. Unparsed text shows in the runner's
   dropped list with reason `proc` or `unparsed`.
6. **Patch notes beat the fit** when they name the value; run the `archive-check` skill on every
   number before writing it (block cost 1730 in a 2018 note lost to two exact readings of 1750
   only because no later note named a value; the fixtures are the newer data).

## 5. Record

- Constants: `tools/build_constants.py`, `sourced(value, 'fixture NNN (...): arithmetic')`.
  Regenerate with `npm run constants`.
- Engine rules: comment the fixture in `engine/src/engine.js`; a unit test in
  `engine/tests/engine.test.js` for the rule (naked stub data), and the real data test when it
  depends on effects.json.
- `engine/tests/fixtures/REVISIONS.md`: one entry per reading (state, what changed with the
  commit hash, what stayed open), and refresh the open questions list at the end.
- `UNKNOWNS.md` fixture section: the table of remaining gaps with game, engine, and the best
  reading of the gap. `DECISIONS.md`: one line per rule of interpretation.
- `npm run build`, `npm test`, commit, republish the hosted app when the sheet changes.
