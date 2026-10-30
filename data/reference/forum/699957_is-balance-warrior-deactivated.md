# Is Balance Warrior deactivated?

Source: https://forums.elderscrollsonline.com/en/discussion/699957/is-balance-warrior-deactivated
Found by query: pasted by the user on 2026-10-30 (the forum returns 403 from the archive container; the thread's date and the poster's name were not included)
Posts: 1 (the testing post only, as pasted)

### (poster not recorded) (date not recorded; PC, live, after Update 50)

Here are some numbers from PC.

The weapon/spell damage added from the Armor appears to be working fine, while the additional weapon/spell damage added from Templar skills slotted works out to +2 weapon/spell damage added per skill instead of the 2-152 that appears to be intended for each one.

Scenario 1: no armor, only Silver Shards slotted. No gear, no slotted CP, no points in Piercing (and therefore no points in Mighty or Warmage), no passives that grant weapon or spell damage (no Balanced Warrior, no racial passives, no Fighters Guild passives):
Spell Damage and Weapon Damage: 1000 (base). Spell Pen and Physical Pen: 0. Spell Resistance and Physical Resistance: 0. Max stam (highest offensive resource): 21534. Tooltip for Silver Shards: 2978. Actual damage done with Shards: 2436.
The Precursor has 9100 armor, which mitigates 18.2% (9100/50000) of my damage. If 2436 is 81.8% of my raw damage, then the raw damage is 2978. That's the tooltip for Shards in this scenario.
When I add points to Balanced Warrior, nothing changes (0 armor, 0 skills slotted).

Scenario 2: heavy armor, only Silver Shards slotted. A complete set of white, untraited, unenchanted CP160 heavy armor; Undaunted Mettle removed. Armor 13005. Tooltip and damage done with Shards unchanged.
At rank 1 of Balanced Warrior the tooltip says "1% of Armor; 52 weapon and spell damage": Spell Damage and Weapon Damage 1052, Spell and Physical Resistance 13135, tooltip for Shards 3028, damage done 2477.
UESP's Skills page shows the formula of Shards as 0.092970 MaxStat + 0.97618 MaxDamage. At 1000 weapon/spell damage and 21534 max stam: 0.97618 x 1000 + 0.092970 x 21534 = 976 + 2002 = 2978. At 1052: 1027 + 2002 = 3029 (truncation makes it 3028; 1026.9).
At rank 2 of Balanced Warrior the passive adds 2% armor and 106 weapon/spell damage: Spell and Weapon Damage 1106, Spell and Physical Resistance 13265, tooltip 3081, damage done 2520. 103 raw x 81.8% = 84 actual.

Scenario 3: heavy armor, Silver Shards and Templar skills slotted. With five Templar skills slotted the tooltip for Balanced Warrior shows 12% armor and 566 Weapon and Spell Damage.
Slotting bonus for Templar skills: 0 skills 106; 1 skill 258 (+152); 2 skills 335 (+77); 3 skills 412 (+77); 4 skills 489 (+77); 5 skills 566 (+77); 6 skills 568 (+2).
At 5 skills the character sheet says: Spell Damage and Weapon Damage 1566, Spell and Physical Resistance 14566, tooltip on Silver Shards 3530, damage done 2528.
The tooltip takes the sheet's weapon/spell damage into account (3530 - 3081 = 449 = 0.97618 x 460). The actual damage takes the 106 into account but not the further 460 from slotting: an increase of only 8 damage done, about 10 raw, so about 2 flat weapon/spell damage per skill slotted.
0 skills: 106 total, 3081 tooltip, 2520 done. 1: 258, 3230, 2522. 2: 335, 3305, 2524. 3: 412, 3380, 2525. 4: 489, 3455, 2527. 5: 566, 3530, 2528. 6: 568, 3532, not testable.
Slotting Templar skills on the back bar has no effect.

tl;dr Only 2 flat weapon/spell damage is added per skill instead of the amount the tooltip shows.
