# Data inventory

Generated 2026-09-19 by eso_reference_archive.py export.
Everything the scrapers hold is in this folder. If a page is not
listed in reference/pages_index.csv, it does not exist on UESP
under that title. Do not ask for pastes; ask for a new scrape.

| Path | What it is |
| --- | --- |
| reference/sets.csv | one row per set, bonus_N columns, lines joined with ; |
| reference/skills.csv | one row per ability, morph, passive; desc columns are tooltips |
| reference/entities.csv | every template parameter from every set and skill page |
| reference/patch_history.csv | UESP's per page change log: family, page, version, note |
| skills.csv kind column | player, companion or artifact; the engine wants player only |
| quality values | five values a / b / c / d / e are white / green / blue / purple / gold |
| morphs | live on the base skill page as morph1desc and morph2desc, not on their own pages |
| reference/tables/ | every wiki table as CSV; tables_index.csv lists each with its page and header, and each page's Markdown ends with the list of its tables |
| reference/pages/*.md | UESP system pages as text (Combat, Armor, Vampire, Campaigns...) |
| reference/pages/sets/*.md | every set page as text |
| reference/pages/skills/*.md | every ability and passive page as text, both ranks |
| reference/pages_index.csv | title, file, words, url for every page above |
| reference/raw_wikitext/ | the untouched wikitext behind the Markdown |
| reference/forum/*.md | forum threads found by search, replies included |
| reference/zos/*.md | ZOS deep dives, guides, new player guide, combat news |
| reference/zos_index.csv | tier, date, title, file for each ZOS document |
| patch-notes/html/ | 202 patch notes 2015 to 2026 as HTML |
| patch-notes/text/ | the same as plain text |
| patch-notes/manifest.csv | date, title, applies_to, url per patch note |

## Counts

- patch-notes/html: 205
- patch-notes/text: 205
- reference/entities.csv rows: 149155
- reference/forum: 41
- reference/pages: 3998
- reference/raw_wikitext: 121
- reference/tables: 2122
- reference/zos: 150
