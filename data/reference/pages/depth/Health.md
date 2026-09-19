# Online:Health

Source: https://en.uesp.net/wiki/Online:Health
License: CC BY-SA, UESP

Health is the amount of damage that any person or creature can take before dying. It is equivalent to hit points (HP) used in other games.

## Maximum Health
The amount of health you have depends on your character's level. Each time you level up, your maximum health attribute increases. You can additionally choose to increase your maximum health by allocating attribute points to it.

A level 1 character starts with 1300 health points and gains 300 points of health per level, resulting in 16000 health points at level 50. Additionally, every stat point allocated to health increases the stat by 122 points. A level 50 character with all 64 stat points allocated to health will have the maximum base health of 23808 points. This is without taking into account any of the numerous bonuses available.

Your health attribute can be increased using equipment with a Glyph of Health or Glyph of Prismatic Defense enchantment, with skills and items giving the Toughness buff, through jewelry with the healthy and triune traits, with certain set bonuses and with the Lord Mundus Stone. Characters over level 50 can further increase their health with the champion perks Boundless Vitality and Hero's Vigor. Food can be used to temporarily increase maximum health.

Argonians, Imperials, Nords, and Orcs can increase their maximum health with racial traits.

The formula for maximum health is:
Health = (300 * Level + 1000 + 122 * Attribute.Health + Item.Health + Set.Health + Food.Health + Skill2.Health + Mundus.Health)*(1 + Skill.Health + Buff.Health)

## Health Recovery
Health recovery refers to how quickly your health regenerates. This increases as your character levels. Increasing the health stat does not increase health recovery.

A level 1 character starts with a health regeneration of 35. Health recovery increases by approximately 5.59 points per level, rounded to the nearest integer. A level 50 character with no other bonuses will have a health recovery of 309 points.

Health recovery can be increased by using equipment with the invigorating effect, through bonuses from some item sets, with the Steed Mundus Stone, through skills or items offering the fortitude buff, from jewelry with a glyph of health recovery, and with many passive abilities from skill trees. Characters over level 50 can increase their health recovery with the champion perk Rejuvenation. Certain Drinks can increase health recovery for a duration of time. Characters afflicted with vampirism will suffer increasing penalties to their health recovery depending on their vampire stage.

Khajiit, Nords, and Orcs can increase their health recovery with racial traits.

The formula for health recovery is:
HealthRegen = (round(5.592 * Level + 29.4) + Item.HealthRegen + Set.HealthRegen + floor(Set.HealthRegenResistFactor * (PhysicalResist + SpellResist)) + Mundus.HealthRegen + (Food.HealthRegen)*(1/(1 + Skill2.HealthRegen)))*(1 + CP.HealthRegen + Skill.HealthRegen + Buff.HealthRegen)*(1 + Skill2.HealthRegen)*(1 + Vampire.HealthRegen)

## Restoring Health
You lose health when taking damage. The red bar in the bottom center of the screen shows you the current status of your health (although this bar will be invisible when health is full). There are many ways to restore health:
- Health slowly regenerates over time. You regenerate faster outside of combat than during combat. Most NPCs do not regenerate health during combat.
- Healing effects are available from:
- Health potions and crafted potions with the Restore Health effect
- Some skills healing yourself or others
- Your health regeneration rate can be increased by:
- Whenever your character levels up, your health is fully restored.
- In player houses, you can activate an Aetherial Well furnishing to restore all attributes.
