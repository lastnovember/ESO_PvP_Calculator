# Fixtures: real characters read from the game

A fixture is one JSON file: the build, plus the numbers the game shows.
The test runner computes the build and compares every number you filled in.
Blank numbers (`null`) are skipped, so a half filled fixture is still useful.

## Filling one in from your phone

1. Copy `TEMPLATE.fixture.json` to `my-character.fixture.json` (any name
   ending in `.fixture.json`).
2. Fill in `build` the same way the app does. Easiest: build the character
   in the app, tap Export, and paste the JSON into `build`.
3. Stand somewhere with **no** Battle Spirit (any overland zone, not Cyrodiil,
   Imperial City or Battlegrounds), out of combat, no potion, no group buffs,
   food active. Open the character sheet on bar 1 and copy the numbers into
   `readings.outOfPvpZone.bar1.main`. Open Advanced Stats and copy them into
   `readings.outOfPvpZone.bar1.advanced`. Swap to bar 2 and repeat for `bar2`.
4. Walk into Cyrodiil, Imperial City or a Battleground (Battle Spirit on),
   wait for the buff to show, and repeat step 3 into `readings.inPvpZone`.
5. Leave any value you cannot see as `null`. If the game shows a stat that is
   missing from the template, add it with the exact name from the game; the
   runner reports it as "not modelled" instead of failing.
6. Percentages: type the number only (`45.3`, not `"45.3%"`). Values shown as
   `12,345` are typed `12345`.

Read the numbers with the same food, mundus, CP and stage that the build says.
If a value in the game changes while you watch it (recovery ticking, a set
proc), wait until it settles or leave it `null`.

## What the runner does

`npm test` runs `engine/tests/fixtures.test.js`. For every fixture with at
least one number filled in it prints a table of expected vs computed values
and fails on any mismatch beyond the tolerance (`tolerance.flat` for whole
numbers, `tolerance.percent` for percentages). The order of operation
strategies can be switched per fixture in `build.flags.strategies` to find the
combination that matches.

## Key names

The keys in `main` and `advanced` are the labels the game uses as best known.
If your game shows a different label, rename the key; the runner maps common
spellings. Unknown keys are listed, never silently ignored.

## Record of readings

`REVISIONS.md` lists every reading taken so far, what it changed and what it left open.
Each fixture JSON also carries `captured`, `location`, `bar`, `attributes`, `photos` (downscaled
copies in `photos/`), `sheetExtras` (every number on the sheet the runner does not compare yet)
and `activeEffects` (the buff list on the character sheet at the time).
