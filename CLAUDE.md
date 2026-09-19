# Working rules for this repo

Every constant, formula and mechanic claim must be searched for in the
archive before it is written down anywhere. The archive is
data/reference and data/patch-notes. Search order:
  1. data/reference/tables_index.csv, grep the header column for the
     stat name, then open the CSV.
  2. data/reference/pages_index.csv, grep the title, then read the
     Markdown. Every page's Markdown ends with the list of tables
     extracted from it.
  3. data/reference/entities.csv and patch_history.csv for a specific
     set or skill.
  4. data/patch-notes/text for when a value changed. Newest wins.
Only after all four come up empty may a value go to UNKNOWNS.md, and
the entry must list the searches that were tried. A decision in
DECISIONS.md must cite the file and row it rests on. If it rests on
nothing, it is an UNKNOWN, not a decision.
Never ask for pages to be pasted. If a UESP page is not in
pages_index.csv, it does not exist under that title.
No em dashes anywhere.
