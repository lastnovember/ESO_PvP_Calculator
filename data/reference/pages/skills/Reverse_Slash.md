# Online:Reverse Slash

Source: https://en.uesp.net/wiki/Online:Reverse_Slash
License: CC BY-SA, UESP

Online Skill Summary
id=39928
line=Two Handed
icon=Two Handed-Reverse Slash
desc=Shift your grip and strike an enemy down, dealing [3074 / 3107 / 3141 / 3175] Physical Damage. Deals up to 300% more damage to enemies with less than 50% Health.
desc1=Area: 5 meters. Shift your grip and unleash a devastating slice, dealing [3175 / 3209 / 3244 / 3279] Physical Damage to your foe and all nearby enemies. Deals up to 300% more damage to enemies with less than 50% Health.
desc2=Cost: 2160 Stamina. Shift your grip and cut deep, dealing 3175 Bleed Damage to your foe. Deals up to [385 / 390 / 395 / 400]% more damage to enemies with less than 50% Health.
linerank=20
cost=2430 Stamina
attrib=Stamina
casttime=Instant
range=7 meters
target=Enemy
morph1name=Reverse Slice
morph1id=39942
morph1icon=Two Handed-Reverse Slice
morph1desc=Now deals its damage in an area around the initial target.
morph2name=Executioner
morph2id=39957
morph2icon=Two Handed-Executioner
morph2desc=Converts to Bleed Damage and reduces the cost. Increases the amount of bonus damage dealt to low health targets.
image=ON-skill-Reverse_Slash.jpg
imgdesc=Reverse Slash

Reverse Slash deals physical damage, additional damage is applied to enemies below 50% Health. The Reverse Slice morph also damages other nearby enemies, while Executioner reduces the cost, deals bleed damage instead and is even more effective against low-Health targets.

## Damage scaling
Testing of the skill without morphs on a dummy reveals that the "up to 300% more" damage scaling works in a constant, linear fashion. Every 1% of missing health under 50% grants a damage bonus of approximately 6% to the initial damage of the skill. For example, at 45% enemy health, the damage bonus is 30%; at 40% enemy health, the damage bonus is 60%; and so on until the bonus approaches 300% as the enemy's health approaches 0%.

## Notes
- As seen in the patch note of update 8.0.5, Reverse Slice no longer deals the exact damage done on the initial target to the nearby targets. Now it calculates the execute bonus for each target hit.
- The Disciplined Slash set from Asylum Sanctorium will cause you to gain Ultimate when using this ability against low-health targets.
- Contrary to most damaging abilities, you cannot use Reverse Slash and its morphs on passive creatures such as Goats and Cockroaches.
- Before Update 10, Executioner gave a passive bonus for all Two-Handed abilities against low-Health targets when slotted.

## Gallery

File:ON-skill-Reverse Slice AoE.jpg|Reverse Slice morph AoE visual

## Patch Notes
* Executioner: The tooltip for this ability now reports the correct damage when you don't have a target.
* Reverse Slice: Increased the area damage of this ability by approximately 100%, and it can now hit up to 6 targets.
ESO Patch Note|2.4.5|* Executioner: Redesigned this morph so it no longer passively increases the damage of all Two Handed abilities while slotted; instead, it increases the scaling bonus damage to low health targets to a maximum of 335/340/345/350% more damage at Ranks I/II/III/IV, increased from 300%.
- Reverse Slice: Increased the splash damage percentage from this morph to 59/61/63/65% at Ranks I/II/III/IV from 41/42/43/44%.
ESO Patch Note|2.7.5|* Adjusted the order of the Active Abilities in this skill line. They now unlock in the following order:
- Uppercut
- Critical Charge
- Cleave
- Reverse Slash
- Momentum
- Developer Comment: This change is aimed at newer players. Our intention for this weapon line and the ones below is getting players into the habit of using their primary damage ability as soon as possible.
* Reduced the cost of this ability and its morphs by approximately 27%.
ESO Patch Note|3.1.5|* The bonus damage dealt by execute abilities, such as Assassin's Blade or Reverse Slash, now works more intuitively with global damage done bonuses, such as Mighty or Minor/Major Berserk. Execute bonus damage is now multiplicative with global damage bonuses instead of additive.
- Fixed an issue where this ability and its morphs would grant slightly less than a 300% damage bonus against a target at 1% Health.
* Executioner: Increased the execute multiplier of this ability to 400% from 350%.
ESO Patch Note|5.2.5|* Reverse Slice (morph):
- Fixed an issue where the AoE damage of this ability could critically strike. Since the initial hit can already critically strike, this was effectively allowing the attack to double crit, contributing to a tremendous power spike.
* Reverse Slice (morph): Fixed an issue where the splash damage of this ability was double hit by Battle Spirit.
* Reverse Slice (morph): Fixed an issue where the Area of Effect component of this ability was not considered a Two Handed ability or Weapon ability.
ESO Patch Note|7.3.5|* Reverse Slice: Increased the cost of this ability and its morphs to 2430, up from 2160.
- Executioner (morph): This morph no longer ranks up in 1.1% damage done per rank and instead reduces the cost per rank.
- Reverse Slash (morph): This morph's splash damage now ranks up to 100% of the original hit, up from 78% at rank 4.
ESO Patch Note|8.0.5|* Reverse Slice (morph): This morph no longer deals damage based on its initial hit and instead deals damage to all targets around the initial.
- Developer Comment: This will allow the Area of Effect damage to be increased and decreased by bonuses, and to be calculated separately per target. It will also fix the issue where the damage continuously became weaker as it cascaded outwards, being diminished by each target's defenses.
* Executioner (morph): This morph now deals Bleed Damage, rather than Physical Damage. This was done to help additional sources of the damage type enter the game, to help balance out ways to apply status effects.
