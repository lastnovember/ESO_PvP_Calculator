# ESO PvP Calculator, phase 1: character sheet

Computes both in game stat panels (main character sheet and Advanced Stats)
for a fully specified Elder Scrolls Online build, per weapon bar, at level 50
with CP160 gold gear. Combat simulation comes in a later phase; nothing here
models damage against a target.

```
app/index.html            the calculator, one self contained file, open it in any browser
app/src/template.html     source of the page (tools/build_app inlines engine and data into it)
engine/src/engine.js      pure ES module: build in, both panels for both bars out
engine/data/constants.json  every base value and conversion rate, each with a source
engine/data/effects.json    set bonuses, passives, slotted effects, Champion stars, buffs, parsed
engine/schema/            build JSON schema and an example build
engine/tests/             unit tests, fixture runner, fixtures/ with the template
tools/build_constants.py  regenerates constants.json from data/reference tables
tools/parse_effects/      regenerates effects.json from the CSVs (prints coverage)
tools/build_app/          regenerates app/index.html
data/reference            UESP tables, sets.csv, skills.csv (input, never edited by hand)
data/patch-notes          the console patch note archive used to verify constants
DECISIONS.md              modelling choices, one line each
UNKNOWNS.md               constants that no data source settles, with the value in use
```

## Run the tests

Node 20 or newer, no npm packages needed.

```
npm test
```

This runs the constants checks, the parser grammar tests, the engine tests
(against a hand written effects stub) and every fixture in
`engine/tests/fixtures/*.fixture.json` that has at least one reading filled in.

## Rebuild the data and the app

Run in this order whenever `data/reference` changes:

```
python3 tools/build_constants.py          # engine/data/constants.json
node tools/parse_effects/index.js          # engine/data/effects.json, prints parse coverage
node tools/build_app/index.js              # app/index.html
npm test
```

`node tools/parse_effects/index.js --report` also lists every set bonus,
passive, star or buff the grammar did not fully understand.

## Scribing script catalog

The UESP page Online:Scribing is archived like the other UESP pages: its four
data tables are `data/reference/tables/uesp_Online_Scribing_t00.csv`
(Grimoires), `t01` (Focus Scripts), `t02` (Signature Scripts) and `t03`
(Affix Scripts), listed in `tables_index.json` and `manifest.csv` (seq 220).
The page shows compatible grimoires as icons, so the tables are produced from a
PDF print of the page by `tools/extract_scribing_pdf.py` (needs `pdfminer.six`;
the PDF itself is not in the repository):

```
python3 tools/extract_scribing_pdf.py Online-Scribing.pdf data/reference/tables
```

It rewrites the four CSVs, prints the `tables_index.json` entries, and refuses
to run if a row or an icon cannot be placed. Then run `npm run effects`.

## Fill in a fixture from the game

Fixtures are the ground truth. Each one holds a build and the numbers the game
shows for it: both panels, both bars, once outside and once inside a PvP zone.

1. Build the character in `app/index.html`, open "Export and import" and tap
   "Fixture template". The JSON box now holds the build wrapped in a fixture
   with every reading blank. Copy it.
   (Or copy `engine/tests/fixtures/TEMPLATE.fixture.json` by hand and paste
   the plain Export JSON into its `build` field.)
2. Save it as `engine/tests/fixtures/<name>.fixture.json`.
3. Read the numbers from the game into `readings`, following
   `engine/tests/fixtures/README.md` (phone friendly, one number per line,
   leave what you cannot see as `null`). One bar outside a PvP zone is
   enough to start; the rest can be filled in later.
4. Run `npm test`. The runner prints game vs engine for every filled number and
   fails on differences beyond the tolerance. Values the engine cannot name are
   reported as "not modelled" so the panel list can grow.
5. When a number settles an entry of UNKNOWNS.md, update the constant in
   `tools/build_constants.py`, regenerate, and move the row to the settled table.

Order of operation strategies (`STRATEGIES` in `engine/src/engine.js`) can be
switched per fixture through `build.flags.strategies` to find the combination
that matches the game.

## Using the app

Everything is on one page: character, buffs, gear, bars, results. Set, trait,
enchant, food, skill and Champion star fields are type to search boxes. Bulk
tools fill a set or apply a trait, weight or enchant to several slots at once.
Picking a monster set on head or shoulders offers the matching piece. Builds
save to the browser's local storage and export or import as JSON. Tap a result
row to see every source that contributed to it.

The page makes no network requests. Rebuild it with `node tools/build_app/index.js`
after any engine or data change.
