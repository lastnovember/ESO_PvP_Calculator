# ROADMAP

What comes after the character sheet, in the order the evidence supports. Each phase is
verifiable against something you can photograph in the game before the next one starts.

## 0. Archive refresh (blocks everything below)

The newest patch note on file is 2026-08-10 and skills.csv was crawled in September 2026. Forum
thread 699957 (data/reference/forum) shows Balanced Warrior reworked since then, so the live game
has moved. The crawlers in `tools/` must run from your PC (`tools/ARCHIVE_README.md`): the forums
sit behind Cloudflare and this container cannot reach the forums, UESP, ESO Hub, esologs or
esoapi at all (403 or no answer). After the refresh: `python3 tools/build_constants.py`,
`node tools/parse_effects/index.js`, `npm test`, and re-read the Templar fixtures.

## 1. Tooltip panel (phase 1.5)

For every ability slotted on a bar, compute the number its tooltip shows from the sheet the
engine already produces: tables/esolog_skill_coefficients_t00.csv holds 2507 equations of the
form `a x MaxStat + b x MaxPower` (plus constants), where MaxStat is the higher of Max Magicka
and Max Stamina and MaxPower the higher of Weapon and Spell Damage; thread 699957 shows the game
truncates the result. Validation is a photo of the skill tooltip, the same way the sheet was
validated. Deliverables: `engine/src/tooltips.js`, a Tooltips card in the app per bar, fixtures
that carry tooltip readings next to the sheet readings. Battle Spirit applies to tooltips too
(damage done and healing done lines) and is read from the same flag.

## 2. Import and export with the other tools

Do not rebuild what UESP, ESO Hub and Battle Scrolls already do; read their outputs.
- UESP build editor: its data comes from esoapi.uesp.net (the esolog source this archive already
  uses); find the build export format and map it onto `engine/schema/build.schema.json`.
- ESO Hub build links: find the shared build format and map it.
- Battle Scrolls (console companion): find what its build sheets and logs export.
None of these sites are reachable from this container, so the format research runs from your PC
or from a browser; the mapping itself is a `tools/import_*` script plus a test per format. The
app's Export and import card gets one more button per format.

## 3. Combat (the simulator)

Only after 1 and 2. First target: damage done to a dummy or a player from the tooltip, which
needs the target's mitigation (`constants.targets`: players 660 per percent to 33,000, NPCs 500
per percent to 25,000), penetration, Battle Spirit, critical chance and critical damage against
the target's critical resistance. Thread 699957 is the model for the evidence: tooltip, damage
done, and the target's armor read together. Keep a known bugs list for effects the sheet carries
and the damage does not (Balanced Warrior's per slotted skill damage, 2026-10-30).

## Readings still wanted for the sheet (phase 1)

See UNKNOWNS.md: a Sorcerer, Nightblade and Arcanist reading; a purple armor piece tooltip; the
Templar with Expert Evasion unslotted; a fresh export of Yeets-Swiftly.
