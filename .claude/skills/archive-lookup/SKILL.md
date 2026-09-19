---
name: archive-lookup
description: Find a game constant, table, set bonus, skill value or
  mechanic in the local ESO archive before writing any number or
  modelling decision. Use before every constants.json entry, every
  DECISIONS.md entry and every UNKNOWNS.md entry.
---
# Archive lookup
Goal: a file and row citation, or a documented miss.
1. grep -i "<stat>" data/reference/tables_index.csv
   Matches name a CSV in data/reference/tables. Open it. Header row is
   the real header; a caption row may follow it.
2. grep -i "<topic>" data/reference/pages_index.csv
   Open the Markdown. Read the whole page; tables are listed at the
   end.
3. For a named set or skill: grep the page name in
   data/reference/entities.csv and data/reference/patch_history.csv.
4. For history: grep data/patch-notes/text. Later dates override.
5. Quality: five values in a cell are white / green / blue / purple /
   gold. Set bonus ranges like 6-300 run from level 1 white to CP160
   gold.
Record the citation as "<file>: <row or header>" next to the value.
If every step misses, write the UNKNOWNS entry with the grep terms
used, so nobody repeats the search.
