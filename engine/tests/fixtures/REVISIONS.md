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

## Open questions for the next reading

- Tooltips of Resolving Vigor and Hurricane as they read now, and the rest of the back bar's
  Active Effects list.
- Trait on each mace and which one is main hand (dual wield Weapon Damage 236 short).
- Exact tooltip of Orzorga's Smoked Bear Haunch (recovery fits 411 Magicka, 369 Stamina, 406 Health).
- An armor only reading to split armor ratings from Markyn's per set armor (resistances 825 short
  on every geared reading).
