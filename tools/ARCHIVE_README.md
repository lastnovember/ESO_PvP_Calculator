# ESO Xbox patch note archive

Builds a searchable PDF archive of every Elder Scrolls Online patch note that
applied to Xbox, pulled from the official **Patch Notes & Hotfixes** forum
category.

You get both packagings: one PDF per patch in `pdf\`, plus a single merged
`ESO_Xbox_Patch_Notes_Complete.pdf` with a bookmark per patch.

## Why you have to run this yourself

Two things ruled out running it for you:

1. The ESO forums sit behind Cloudflare bot verification. Headless scrapers get
   a "Just a moment..." wall. A real browser window, with you present to click
   the check if it appears, goes straight through.
2. The Linux workspace on your PC will not start right now (a Windows update
   from September 8 broke it), and my cloud sandbox has no outbound network.

So the script drives a visible Chrome window on your machine. You click the
verification box once, it stores the cookie in a local profile folder, and
later runs skip it.

## Easiest way to run it

Open `eso_patch_archive.py` in VS Code and hit **Run File**, or double click
`run_full_archive.bat`. You get a menu:

```
  1  Test run      3 threads only, so you can check the output first
  2  Full archive  harvest everything, render PDFs, merge
  3  Render only   rebuild PDFs from already harvested pages, no network
  4  Merge only    rebuild the single combined PDF
  5  Inspect       print parser diagnostics
```

Start with 1. It checks for the packages it needs, offers to install them for
you, then archives three threads so you can look at a PDF before committing to
the full crawl. Then run it again and choose 2.

## About those Pylance warnings

"Import could not be resolved" just means the packages are not installed in the
interpreter VS Code is pointed at. Option 1 above installs them into whichever
interpreter is running the script. If the squiggles stay after that, VS Code is
using a different Python: press Ctrl+Shift+P, pick **Python: Select
Interpreter**, and choose the same one.

To install by hand instead:

```
pip install playwright beautifulsoup4 pypdf lxml
playwright install chromium
```

## Command line, if you prefer it

```
python eso_patch_archive.py harvest --limit 3
python eso_patch_archive.py render
python eso_patch_archive.py all
```

Expect the full harvest to take 45 to 90 minutes. It pauses 2.5 seconds
between page loads on purpose, to stay polite to the forum. It is fully
resumable: rerun the same command and it skips anything already saved.

## What gets collected

The category holds 712 threads. The filter was tuned against all of them and
selects 202, in three tiers, tagged in the `applies_to` column of
`manifest.csv`:

| Tier | Count | What it is |
| --- | --- | --- |
| `xbox` | 132 | Threads naming Xbox, from `Xbox One Patch Notes v1.0.0.5` at console launch in June 2015 through Update 48 |
| `all-platform` | 32 | `Update NN Live Patch Notes: All Platforms`, how ZOS has published since Update 49, plus console-server and all-megaserver hotfixes |
| `unlabeled` | 38 | Console-era hotfixes that name no platform, for example `Hotfix 8-6-15`. ZOS normally says so when a fix is PC-only, so these most likely applied to Xbox too |

Dropped: anything naming PC, Mac, PTS, PlayStation, Stadia, the launcher or
the patcher, and every unlabeled thread from before the Xbox launch, since
those predate consoles entirely. Run with `--strict` to skip the `unlabeled`
tier and keep only the first two.

Long patch notes are split across several consecutive posts by the ZOS author
because of forum post length limits. The script stitches those back into one
document and stops at the first reply from a regular player.

## Layout

```
ESO Patch Notes Archive\
  raw\                  saved HTML, the network work, never repeated
  clean_html\           one tidy HTML file per patch
  pdf\                  one PDF per patch, numbered chronologically
  manifest.csv          date, title, word count, source URL for each
  ESO_Xbox_Patch_Notes_Complete.pdf
  _browser_profile\     Cloudflare clearance cookie, leave it alone
```

Because `raw\` is kept, you can re-render the whole archive with different
settings (for example `render --no-images`) without hitting the forums again.

## Useful flags

| Flag | Effect |
| --- | --- |
| `--limit N` | only the N most recent matching threads |
| `--include-all` | harvest every thread in the category, no filter |
| `--refresh` | re-download pages already saved |
| `--no-images` | strip images, smaller and faster PDFs |
| `--out PATH` | write the archive somewhere else |

## If parsing looks wrong

The forum's HTML class names are the one thing I could not verify directly,
since the bot check blocked me from reading the live markup. The parser tries
several selector patterns and falls back sensibly, but if a PDF comes out empty
or truncated, run:

```
python eso_patch_archive.py inspect
```

and send me that output. It prints which selectors matched and how many posts
were found, which is enough to pin the extractor exactly.

## Fair use note

This is a personal archive of publicly posted patch notes. The rate limit is
deliberate. Do not republish the collected text.

---

# Part two: the reference archive

`eso_reference_archive.py` is one script covering the two sources that
actually hold mechanics detail. The patch note archive above is unchanged
and still runs from its own script.

| Source | What it gets | How |
| --- | --- | --- |
| **UESP systems** | Combat (blocking, dodging, break free, CC immunity), attributes, buffs, champion points, traits, mundus, armor, weapons, classes, races, damage types and their status effects, consumables, Alliance War, Campaigns (Battle Spirit and battle leveling) | MediaWiki API, one page at a time |
| **UESP families** | Every item set and every ability, morph and passive, each with its own page | Category enumeration, then 50 pages per request |
| **ZOS** | Developer Deep Dives, official guides, New Player Guide, combat and PvP news | Real browser, the site is age gated |
| **esolog** | UESP's skill coefficient table, built from game client data | Same browser session, it blocks plain HTTP |

Five titles I originally guessed do not exist on UESP. Battle Spirit has no
page of its own and lives in `Online:Campaigns`; blocking, dodging, breaking
free and crowd control immunity are all inside `Online:Combat`; status
effects are documented on the damage type pages. The seed list reflects
that now, and any title that goes missing later is reported and skipped
rather than failing the run.

## Run it

Open it in VS Code and hit Run File, or run `python eso_reference_archive.py`.

```
  1  Test run        a few pages from each source
  2  Full archive    everything, then data and PDFs
  3  UESP only       no browser needed
  4  ZOS only        browser, asks your age once
  5  Rebuild offline re-extract data and PDFs from what is saved
  6  Inspect         what is harvested, and the biggest data tables
```

Start with 1.

## Output: data first, then PDFs

```
ESO Reference Archive\
  data\
    sets.csv             every set, one row each, bonuses as columns
    skills.csv           every ability, morph and passive
    tables\              every wiki table as its own CSV
    reference.sqlite     pages, table cells, and every template value
    tables_index.json    which CSV came from which page
  pdf\                   one readable PDF per page
  clean_html\            the tidied HTML behind each PDF
  raw\                   untouched API responses and HTML
  manifest.csv
  ESO_Reference_Complete.pdf
```

The SQLite file is the point. Every table cell is stored with its page,
column header and value, so you can ask questions across sources:

```sql
-- every set bonus mentioning penetration
SELECT page, value FROM entities
WHERE family='sets' AND value LIKE '%Penetration%';

-- what a given ability costs
SELECT param, value FROM entities WHERE page='Online:Veiled Strike';
```

Sets and skills are parsed from the wiki's own templates rather than from
rendered tables, so a set's five piece bonus arrives as a labelled field,
not as text to be picked apart.

## The age gate

The ESO site redirects to `/en-us/agegate` and asks for a date of birth.
The script detects it, stops, and waits for you to type it in the browser
window. It does not answer that on your behalf. The answer is stored in
this archive's profile folder, so it asks once. If you skip it, the run
keeps whatever UESP already downloaded and carries on rather than failing,
which is what went wrong the first time.

## Two things to expect

The newest data export on esoapi.uesp.net is v101044 from November 2024,
which is Update 44 era and six updates behind live. Coefficients from
there need reconciling against your patch notes, which is exactly what the
patch archive is for.

UESP text is CC BY-SA. This is a personal reference copy. Attribute UESP
if any of it gets republished.

`eso_official_archive.py` is superseded by this script and can be deleted.
