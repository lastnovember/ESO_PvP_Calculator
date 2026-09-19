# Fixture revisions

One entry per stat sheet reading, newest last. Each says what the sheet showed, what changed
in the engine or constants because of it (with the commit), and what it left open. The photos are
in `photos/` (downscaled copies of the originals), the transcribed numbers in the fixture JSON
(`readings` for what the runner compares, `sheetExtras` and `activeEffects` for the rest).

All four readings are the same character: Yeets-Swiftly, Khajiit Warden with Animal Companions,
Assassination and Storm Calling, Xbox, Update 50 era, September 2026.

## 001, 2026-09-14, geared, back bar, Eastern Elsweyr Gate (Cyrodiil)

Attributes 42 Magicka, 22 Health. Battle Spirit on (Health Recovery 511 is half of the 1022 read
outside later). Healing Done 22% includes Combat Medic near a Keep.

Changed (commit ac0dd22):
- Jewelry harm glyphs give Weapon and Spell Damage (Update 37 note); Spell Damage matched.
- The sheet shows Critical Damage as the bonus above the 50% base.
- Healing Taken, Damage Taken and Shield Strength on the sheet leave Battle Spirit out; the adjusted
  values moved to `advanced.battleSpirit`.
- Ancient Knowledge (Ice Staff block cost and block amount) parsed.
- Base Magicka and Stamina moved from 7958 to 12000 (fitted).

Left open then: Max Health, recoveries, crit chance (+12%), crit resistance (+1320), resistances
(+825), costs, block mitigation, sprint speed.

## 002, 2026-09-16, geared, front bar, Elden Root Wayshrine

Same gear and food, attributes 49 Magicka, 15 Health. Outside Cyrodiil.

Changed (commit 340c828):
- "Slotted on either bar" buffs (Merciless Resolve) apply from the other bar; plain "while
  slotted" (Bird of Prey) does not. Crit chance matched on both bars.
- Costs: flat first, armor passives additive, weapon passive multiplicative. Block base 1750 and
  sprint base 500 matched both bars.
- Battle Spirit adds 1600 Max Health before percent bonuses (seven attribute points apart with
  122 per point). On by default.
- 111 Magicka per attribute point verified (777 apart before percents).

Left open then: Max Health constant gap, recoveries, dual wield Weapon Damage (236 short),
resistances, crit resistance, bash, break free, roll dodge, block mitigation 2%.

## 003, 2026-09-16, naked, front bar, Elden Root Wayshrine

No armor, jewelry, weapons or food. The Lover kept. Active effects: Minor Berserk, Gallop,
The Lover, Major Savagery, Major Prophecy, an experience scroll.

Changed (commit 9958697):
- Base values settled: Max Health 16000, Magicka and Stamina 12000, recoveries 514/514/309,
  block 1750, sprint 500, bash 765, break free 5400, roll dodge 4040, sprint speed base 140%
  without movement speed bonuses.
- Baseline Critical Resistance 1320 (Update 26 note: 20% critical damage reduction for all).
- Small armor pieces carry 40.3% of a large piece's glyph value (seven Prismatic pieces total
  2002 Magicka against fixture 002).
- Orzorga's Smoked Bear Haunch fitted to 4316 Health and 406 recovery; Max Health and Health
  Recovery matched on all three readings.

25 of 27 readings match; the two left are sheet semantics (total bash damage, Deadly Aim folded
into every damage type).

## 004, 2026-09-16, naked, back bar, Elden Root Wayshrine

Same state as 003 with the back bar active. Active effects: Minor Protection (Temporal Guard),
Gallop, The Lover, Major Savagery, Major Prophecy; the list may continue below the photo.

No change (commit b036c71). 22 of 27 match. Open: Max Health is 003's value x 1.10 and
resistances are 4272 above Fortified with Bull Netch, Hurricane, Resolving Vigor, Streak, Wield
Soul and Temporal Guard slotted; no archived text or note gives a slotted health or resistance
bonus on any of them.

## 005, 2026-09-17, geared, front bar (dual axes), Elden Root Wayshrine

Different character: Wood Elf Templar "Lastnovember", subclassed Storm Calling and Animal
Companions, vampire stage 3, 64 Health, Roksa the Warped, Mechanical Acuity, Rallying Cry,
Trainee, Monomyth Reforged, The Shadow, Smoked Bear Haunch. Active effects: ESO Plus, Increased
Experience scroll, Smoked Bear Haunch, Gallop, Boon: The Shadow, Vampire Stage 3.

Changes (this commit): Block Mitigation adds one point per heavy piece after the Champion Point
percent (55 = 52 + 3; Yeets' 54 = 52 + 2 now matches too); a flat added to Spell Resistance
alone is not multiplied by Balanced Warrior (Spell = Physical + 726, exact); Disease and Poison
Resistance include Resist Affliction (28.9 = (16765 + 2310) / 660); The Shadow counts for
Critical Healing (25 = 6 + 8 + 11); Dark Stalker caps the sneak penalty (Sneak Speed 100);
`championPoints.notTaken` for passive stars a character skipped (Sprint Cost 470 = 500 x 0.94,
no Sprinter); Bear Haunch Max Health 4316 (second reading agrees). Expert Evasion explains the
sheet's Roll Dodge Cost 0 (free roll primed), recorded in `sheetState`, engine shows the regular
cost with a note.

27 of 51 match. Open: Weapon Damage 4471 (engine 3490, dual axes with Nirnhoned off hand),
Health Recovery 415 (fits -60% without the glyph's 84, engine applies Unnatural Resistance),
resistances 514 short before the 6% (armor ratings), recoveries +14 and -19, Sneak Cost 55
(engine 40), Physical 10% and Bleed 5% (a buff was expiring during the photos), Bash Damage.

## 006, 2026-09-17, geared, back bar (ice staff, Defending), Elden Root Wayshrine

Same state as 005 with the back bar active. Active effects as 005.

Change (this commit): the Defending trait's 3276 is not multiplied by Balanced Warrior (the
game's excess over the engine was 545 on the front bar and 348 on the back bar, a difference of
exactly 6% of 3276); the engine flags weapon trait resistance rows unscaled. Block Cost 1029,
Block Mitigation 65, Weapon Damage 3387 (Rallying Cry 4 pieces with the staff, Expert Mage from
Hurricane), Max Magicka 17485 (no Magicka Controller on this bar), penetration 2589 and Critical
Damage 42 (no axes) all match at once, which confirms the cost and mitigation rules and the
positional weapon passives.

37 of 51 match. Open: the same 545 resistance gap as the front bar, Health Recovery 415,
recoveries +14 and -19, Sneak Cost 55, Bash Damage 608. Physical Damage reads 5% here against 10%
on the front bar, so the front bar's extra 5% is something slotted or wielded there.

## 007, 2026-09-17, geared, front bar (restoration staff), Western Elsweyr Gate (Cyrodiil)

Third character: Breton Necromancer healer "Z antilles", subclassed Restoring Light and Green
Balance, Earthgore, Trainee, Robes of Transmutation, Spell Power Cure, Markyn, The Lady, Smoked
Bear Haunch, 47 Health and 17 Magicka. Active effects: ESO Plus, Battle Spirit, Smoked Bear
Haunch, Gallop, Boon: The Lady.

Changes (this commit): Battle Spirit adds no flat Max Health (33289 is exact without the 1600;
flag default off, Yeets fixtures keep it on); `championPoints.points` holds the stages bought in
a star, and Sneak Cost 94 here, 55 on the Templar and 34 on Yeets are Sustaining Shadows at 10,
31 and 50 of 50 stages with the medium armor reductions unchanged. The app has a stages box next
to each slotted star.

40 of 55 match. Open: Magicka Recovery +34, crit +0.9, resistances 721 short (Markyn counted at
two sets), Healing Done 31 against 19 (Curative Curse 12, or Mending 6 plus Restoration Master 6),
Bash Damage.

## 008, 2026-09-17, geared, back bar (dagger and shield), Western Elsweyr Gate (Cyrodiil)

Same state as 007 with the back bar active (Spell Power Cure dagger, Powered, and a Reinforced
shield). Active effects as 007.

Changes (this commit): Healing Done is 12 above every other source on both bars, so Curative
Curse counts Battle Spirit as a negative effect (the engine applies it under Battle Spirit);
Deadly Bash parses (500 bash damage, 50% less cost) and its percent changes the bash base before
the Savage Defense flat and the armor percent (257 = (765 x 0.5 - 90) x 0.88); a gold shield is
1720 armor (the bar to bar difference 1995 = 1720 x 1.16); Battlefield Mobility reads Block Move
Speed 54 (fit). Block Cost 1193 and Block Mitigation 64 with the shield matched at once.

42 of 55 match. Open, identical on both bars: Magicka Recovery about +30 before percents, crit
about +1, resistances 721 short, Bash Damage.

## 009, 2026-09-17, geared, front bar (dual maces), Western Elsweyr Gate (Cyrodiil)

Fourth character: Argonian Dragonknight "Yuggah Yuggah" (native class, Class Mastery Inexorable
Descent and Wildfire Embers), Bloodspawn, Trainee, Rallying Cry, Essence Thief, Markyn (Swift),
The Mage, Bewitched Sugar Skulls, 52 Magicka and 12 Health. Four photos, no Active Effects page.
The user said the Undaunted line is not unlocked on this character (skillLines.Undaunted false).

Changes (this commit): Combat Medic's 20% goes on the sheet near a Keep (`flags.nearKeep`; this
reading and Yeets' 001 at the other gate both carry it, the Necromancer at the same gate did not,
which needs an answer on whether that character has the Support passive); food health values
scale by 1.17442 and Magicka and Stamina values by 1.1735 (Sugar Skulls 4624 and 4250 both exact,
the Bear Haunch 4316 falls out of the same scale).

41 of 55 match. Open: Magicka Recovery +41.6 before the percent (same as Yeets, and this
character has no recovery food, so the food is cleared), Weapon Damage 236 flat short (same as
Yeets, same weapons), resistances 859 short, Roll Dodge Cost 29 short, Bash Damage.

## 010, 2026-09-17, geared, back bar (ice staff, Defending), Western Elsweyr Gate (Cyrodiil)

Same state as 009 with the back bar active. Four photos, no Active Effects page.

No change (this commit). 43 of 55 match on the first run: Weapon and Spell Damage 3598 (Rallying
Cry at four pieces with the staff), Block Cost 1062 and Block Mitigation 69 (Ancient Knowledge on
top of two heavy pieces), penetration 2578, crit, Healing Done 28 near the gate. The four misses
are the same numbers as the front bar: Magicka Recovery +45, resistances 859 short on both bars
(so Defending's 3276 is confirmed again), Roll Dodge 3315 against 3344, Bash Damage.

## 2026-09-17, calibration pass over all ten readings

Changes (this commit): dual wield off hand share 23.67% of the off hand rating (fixtures 002, 005
and 009 agree to 0.05% once fixture 005 is read with Major Brutality and Sorcery up, recorded as
a correction with `activeBuffs`); Unnatural Resistance dropped (removed in Greymoor, note 087),
so the Templar's Health Recovery reads 452 against 415 instead of 848; medium and light armor
chests fitted to 1995 and 1354 over the four geared characters (resistances within 14 to 73
instead of 514 to 859); the sheet's Damage Done line folds the single target star; `activeBuffs`
in the build; the `reading-log` skill, `corrections` entries and `npm run fixtures` (INDEX.md).

Match counts after the pass: 001 49/56, 002 49/56, 003 55/56, 004 52/56, 005 43/51, 006 45/51,
007 49/55, 008 49/55, 009 50/55, 010 50/55.

## 2026-09-17, archive pass with the UESP pages and forum threads

The user added data/reference/pages (89 UESP system pages) and data/reference/forum (40 threads)
and rebuilt sets.csv. Settled from them: the dual wield share is 17.67% inherent plus Dual Wield
Expert's 6% (forum 348673 by the UESP build editor's author agrees with the three readings); two
handed melee weapons are 1571 (Nirnhoned page); the vampire stage table and the Update 26 removal
of Unnatural Resistance are on the Vampire page; the Emperor passives are on the Emperor page and
now apply; Gaze of Sithis and Velothi parse in full. Match counts unchanged (no reading carries
a two handed melee weapon or an Emperor). Magicka Recovery, roll dodge and the armor slot factors
stay open: the pages hold no rating table and no recovery source the engine lacks.

## 2026-09-17, full crawl pass (1550 UESP pages, 41 forum threads, 150 ZOS articles, 205 patch notes as text)

- Patch note 135 (2023-03-28, Update 37): Physical Harm glyphs add 10 Stamina Recovery and Spell
  Harm glyphs 10 Magicka Recovery at all qualities. Scaled by Infused (16), this is the Magicka
  Recovery gap on every character: Yeets 42, DK 42, Necro 30, Templar 26. Fixtures 001 and 002
  corrected to Spell Damage glyphs (user: "I chose Weapon Damage glyphs instead of Spell Damage ones
  on the jewelry"); the correction entries carry the old value.
- The same pair (001 back bar 1433, 002 front bar 1457, Magicka Controller only on the front bar)
  pins the pre-percent recovery at 1156, so Bear Haunch's 369.65 is truncated to 369: Magicka and
  Stamina food values truncate, Health values round.
- Templar (005, 006): Health 415, Magicka 1411 and 1389, Stamina 1785 are exact with Roksa the
  Warped's 70 per recovery (note 194 and the set page) and nothing from the ring exported as
  Prismatic Recovery. That glyph is set to 0 until its tooltip is known.
- Roll dodge: the Light, Medium and Heavy Armor Bonuses pages confirm 3, 4 and 3 percent per
  piece; the order that fits Yeets and the DK within 1 is still not found.
- No armor rating table anywhere in the crawl (Armor, the armor line pages, Nirnhoned, the ZOS
  articles): the fitted medium 1995 and light 1354 chest values stand. The Templar reads 70 above
  and the DK 70 below the engine, one quality step (4%) of a medium head, shoulder, leg or foot piece.
- Match counts: 001 50, 002 50, 003 55, 004 52, 005 46, 006 48, 007 50, 008 50, 009 51, 010 51.

## 2026-09-19, DK gear tooltips (typed by the user, recorded in fixture 009 `tooltips`)

- Armor: heavy Reinforced head 2813 and chest 3215 give 2425 and 2772 at 16%; medium big
  pieces 1823 (Reinforced 2114, truncated); light big 1221, hands 698, waist 523. So the slot
  factors are 0.875, 0.5 and 0.375 of the chest, the waist a size below the hands. Resistances
  are now exact on the DK and the Necro, 3 over on Yeets (derived medium waist) and 72 over on
  the Templar (4% of one medium big piece: a purple shoulders or feet).
- Glyphs: Prismatic Defense 477 / 434 / 434 and 193 / 175 / 175, Max Magicka small 351, Health
  984 (typed) and 386. The sheet sums truncated small pieces (192, 350, 385) and 954 for the
  large Health glyph; 984 does not fit the DK's Max Health (94 over) nor the 386 small piece.
- Weapons: Nirnhoned mace 1535 and maul 1806 confirm 1335 and 1571 with 15% truncated.
- Sets: Essence Thief 1096 / 1096 / 129 and Markyn 100 and 1157 per set read as parsed.
- Feet: Reinforced now (2114); the user re-traited the boots after the export, so the readings
  on file (Impenetrable, 1823) stand and the sheet total agrees with them.
- Match counts: 001 50, 002 50, 003 55, 004 52, 005 46, 006 48, 007 52, 008 52, 009 53, 010 53.

## Open questions for the next reading

- Answered 2026-09-17: the Necromancer has every Support passive (so Combat Medic at that gate was
  a matter of position), every character has Tumbling at both stages, the Templar has every
  vampire passive (Unnatural Resistance bought, so its Health Recovery 415 is unexplained by the
  archive's rule). Naked, single weapon and tooltip readings are not asked for; the remaining
  gaps (dual wield 236 and 876, resistances 514 to 859, Magicka Recovery +11 to +42, roll dodge)
  are worked from the archive and from differencing the readings on file.

- Answered by the DK tooltips (2026-09-19): armor values per slot; the Templar's open items are one purple medium piece and the ring glyph.
- Answered by the crawl (2026-09-17): the Magicka Recovery offsets were the harm glyphs' 10 recovery (note 135); Bear Haunch's tooltip is no longer needed.
- A reading of the necromancer outside Cyrodiil: Healing Done should drop by 12 if Curative Curse
  is the Battle Spirit reading, and the crit and Magicka Recovery offsets should stay.

- Templar: the glyph on the Protective ring (exported as Prismatic Recovery, reads as nothing on the sheet) and the quality of the two Roksa pieces (resistances 70 high in the engine, one purple medium piece's worth); Physical and Bleed Damage percents re-read at rest.
- Templar naked front bar (no gear, no food, mundus may stay), then with only the two axes, then
  only the main axe: settles the vampire Health Recovery, the sneak cost, and the dual wield and
  Nirnhoned Weapon Damage rules.
- Yeets-Swiftly (still open):
- Tooltips of Resolving Vigor and Hurricane as they read now, and the rest of the back bar's
  Active Effects list.
- Trait on each mace and which one is main hand (dual wield Weapon Damage 236 short).
- An armor only reading to split armor ratings from Markyn's per set armor (resistances 825 short
  on every geared reading).
