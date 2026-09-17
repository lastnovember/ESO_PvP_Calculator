---
name: reading-log
description: Record every character sheet reading the user sends (front bar, back bar, the build JSON that goes with it, the photos) in the fixture database, keep the index current, and apply corrections to earlier readings safely. Use whenever the user sends sheet photos or a build export, corrects something they said earlier, or asks what data is on file.
---

# Reading log

The database is `engine/tests/fixtures/`. One reading is one file, `NNN-<who>-<bar>.fixture.json`,
with the photos beside it in `photos/NNN-*.jpg`. Nothing the user sends is kept only in the
conversation: if it is not in a fixture file, it is not saved.

## What every reading must carry

- `build`: the exact JSON export that goes with the photos (the user's paste, with only the
  fields they told you to change, such as a skill line they forgot to untick, and each such change
  listed under `corrections`).
- `readings`: every number on the main panel and every Advanced Stats page, under
  `inPvpZone` or `outOfPvpZone` and `bar1` or `bar2`, with the runner's labels.
- `sheetExtras`: the numbers the runner's main tables do not carry (sneak cost, block move speed,
  sneak speed, per type resistance and damage percents, critical healing, currency bonuses).
- `sheetState`: a number that is a state rather than a stat (Roll Dodge 0 with Expert Evasion
  primed, a percent that changed between two pages), never silently dropped.
- `activeEffects`: the Active Effects list as photographed, or `(not photographed)`.
- `photos`, `captured`, `location`, `bar`, `attributes`, `mundus`, `food`, `notes`.
- `status: "open"` until every number matches.

Front bar and back bar of the same state are two files sharing one build (copy the front file,
change `bar`, `readings`, `sheetExtras`, `photos`, `notes`). Never merge two bars into one file.

## After saving

1. `npm test` and read the fixture's block; record what matched and what did not.
2. Add the reading to `engine/tests/fixtures/REVISIONS.md` (state, what changed and the commit,
   what stayed open).
3. `npm run fixtures` rewrites `engine/tests/fixtures/INDEX.md`, the table of every reading on
   file with its match count. Commit the fixture, the photos, the log and the index together.

## Corrections

The user may later correct something they told you (a glyph, a passive, a location). The
original file is the record of what was said, so a correction never silently overwrites it:

1. Append to the fixture's `corrections` array:
   `{ "date", "field" (a JSON path such as build.gear.ring1.enchant), "from", "to", "reason" }`.
2. Then change the field itself to the corrected value, so the runner uses the truth. If the
   corrected value is not yet known, write `"to": "(pending ...)"` and leave the field alone.
3. Re-run `npm test`; if the correction changes matches, say so in REVISIONS.md under a dated
   line for that fixture, and refresh `UNKNOWNS.md` if a gap opened or closed.
4. Never delete a fixture, a photo or a reading value. A wrong reading gets a correction entry
   and the corrected value, and the runner compares the corrected one.

A correction that applies to every reading of a character (the same jewelry on all of them)
goes into every fixture of that character, one entry each.

## What not to do

- Do not ask for tooltips, naked readings or re reads; see the `fixture-calibration` skill.
- Do not keep readings in DECISIONS.md, UNKNOWNS.md or the chat only.
- Do not renumber fixtures; numbers are permanent identifiers used in constants sources.
