# Online:Weapon Critical (effect)

Source: https://en.uesp.net/wiki/Online:Weapon_Critical_(effect)
License: CC BY-SA, UESP

ON:Weapon Critical
Weapon Critical is a value that represents your chance of performing a Critical Strike when attacking with a non-Staff weapon or ability with a Stamina cost. Your actual chance of performing such a strike also depends on your level - it is harder to strike critically the higher your level. The formula (all are identical - they are provided to aid ease of understanding) for determining the Maximum Critical Value (MCV) required to gain 100% Critical strike chance is:

MCV = (2 * Level * (100 + Level))))
MCV = (2*(100*Level + Level 2 ))))
MCV = (200*Level + 2*Level 2 ))))

You start with a baseline 10% critical value, so the amount of Weapon Critical needed from buffs to get 100% Critical Strike Chance is 0.9 * MCV. This means at level 50 you need 13,500 Spell Critical to have a 100% chance (an extra 90%). At CP160 (level 66) you need 19721 Spell Critical. Your Critical Strike Chance% is then computed from:

Critical Strike Chance% = min(100,10 + 100*(Critical Value / MCV))

You cannot have a worse than 10% chance (because 10% is your baseline) or better than 100% chance to critically strike. So if you are CP160 and have a Weapon Critical of 3000, your Critical Strike Chance% = 10 + 100 * (3000 / 21912) = 23.7%

There are a large number of skills and sets which increase your Weapon Critical rating. See those categories for a complete listing. In addition, there are a few other ways of increasing your Weapon Critical rating:
- Successfully attacking while in Stealth
- Using a potion of Weapon Critical
- Spending 20 Champion points in the warfare constellation point, Precision.
- The Thief Mundus Stone

The Critical Damage, or amount of increased damage or healing from Critical Strikes is normally 50% of the base strike. So at 50% chance, your strikes are 1.50x their defualt damage done, while at 100%, they are 2.0x and at 125% (which is maximum Critical Damage/Healing done) they are 2.25x. Factors which increase your Weapon Critical Damage include:
- The Aggressive Horn morph of War Horn
- Several sets contain critical damage effects, including 5 piece sets like Sul-Xan's Torment and mythics like Harpooner's Wading Kilt
- Activating any Synergy cast by a player using the Twilight Remedy set
- Spending Champion points on Fighting Finesse and Backstabber in the Warfare constellation
- The Shadow Mundus Stone

## References
