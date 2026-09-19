# Online:Sun Shield

Source: https://en.uesp.net/wiki/Online:Sun_Shield
License: CC BY-SA, UESP

Online Skill Summary
id=27501
line=Aedric Spear
icon=Aedric Spear-Sun Shield
desc=Surround yourself with solar rays, dealing [4612 / 4662 / 4713 / 4764] Magic Damage to nearby enemies and applying Minor Maim to them for 10 seconds, reducing their damage done by 5%. The rays then protect you, granting a damage shield that absorbs up to 4800 damage for 6 seconds, increasing by 10% for each enemy hit, up to 60%. This portion of the ability scales off your Max Health.
desc1=Cost: 4320 Magicka. Surround yourself with solar rays, dealing 4764 Magic Damage to nearby enemies and applying Minor Maim to them for 10 seconds, reducing their damage done by 5%. The rays then protect you, granting a damage shield that absorbs up to [4800 / 4852 / 4905 / 4958] damage for 6 seconds, increasing by 20% for each enemy hit, up to 120%. This portion of the ability scales off your Max Health.
desc2=Radius: 8 meters. Surround yourself with solar rays, applying Minor Maim to nearby enemies for 10 seconds, reducing their damage done by 5%. You gain a damage shield that absorbs up to 4800 damage for 6 seconds, increasing by 10% for each enemy hit, up to 60%. This ability scales off your Max Health. When the shield expires it explodes, dealing [30 / 31 / 32 / 33]% of damage absorbed as Magic Damage to nearby enemies.
linerank=42
cost=4590 Magicka
attrib=Magicka
casttime=Instant
radius=5 meters
duration=6 seconds
target=Area
morph1name=Radiant Ward
morph1id=27514
morph1icon=Aedric Spear-Radiant Ward
morph1desc=Has reduced cost and the shield is strengthened further for each enemy hit.
morph2name=Blazing Shield
morph2id=27530
morph2icon=Aedric Spear-Blazing Shield
morph2desc=No longer deals damage to enemies on activation, instead deals damage when shield expires based on the amount it absorbed, and increases the radius.
image=ON-skill-Sun Shield.jpg
imgdesc=A character affected by Sun Shield

Sun Shield applies a Damage Shield to you. Enemies nearby take Magic Damage on cast, and increase the shield's magnitude. The Radiant Ward morph reduces the casting cost and further strengthens the shield based on the number of enemies affected, while the Blazing Shield deals damage to all enemies at the end of the effect based on how much damage it absorbed, rather than a fixed amount at the beginning.

## Notes
- Be careful when using the Blazing Shield morph that you don't re-cast it until the ending blast has occurred, otherwise you will cancel the original blast and the spell ends up doing basically nothing except for an expensive and fairly minor Damage Shield.
- By contrast, due to its reduced cost, the Radiant Ward morph can effectively be used several times in rapid succession to quickly take out some weaker mobs of enemies. The Damage Shield from the first cast still persists for the full duration, so even if there are fewer enemies on successive casts, your shield won't be reduced (except by the normal means of taking damage).
- Blazing Shield is a recommended morph for the Templar Initiate build.

## Gallery

File:ON-skill-Blazing_Shield.jpg|Blazing Shield

## Patch Notes
[Patch 1.1.2] * Radiant Ward: Fixed an issue where this ability wasn't properly progressing as it ranked up. This results in a slight increase to its damage.
[Patch 1.3.3] * This ability no longer stops your magicka regeneration.
ESO Patch Note|1.6.5|* Increased the cost of this ability by 10%.
- Radiant Ward: In addition to increased shield strength, this morph also has a reduced cost.
[Patch 2.3.5] * Radiant Ward: Increased the shield strength bonus from this morph's shield to 6% per enemy hit from 5%.
[Patch 2.3.6] * Blazing Shield: Fixed an issue where this morph was not working with the Spear Wall and Piercing Spear passive abilities.
ESO Patch Note|3.0.5|* Blazing Shield: Reduced the amount of damage done by this morph to 33/36/39/42% of the damage absorbed by the shield, down from 50/51/52/53%.
- Developer Comments: Blazing Shield builds have proven to be extremely effective due to being able to stack Health to improve both their survivability and damage done. We've reduced the effectiveness of this ability so that there is more of an opportunity cost to having so much Health.
[Patch 4.2.5] * Blazing Shield: Fixed an issue where casting this morph would aggro neutral monsters around you.
ESO Patch Note|5.0.5|* Updated the tooltip for this ability and its morphs to state the actual value, rather than an ambiguous value that required you to do super hard math.
- Increased the initial hit damage of this ability and the Radiant Ward morph by 150% to put it on par with our PBAoE standards. Blazing Shield's damage remains untouched since it is already above that standard, since it has an additional requirement in order to gain the damage.
- Radiant Ward (morph): This ability no longer gains additional cost reduction as it ranks up. Instead, the bonus shield size for enemies hit goes up to 9% per enemy hit at Rank IV.
ESO Patch Note|5.2.7|* Blazing Shield (morph):
- Fixed an issue where this ability could save damage taken from previous casts. Once the shield ends or is broken, it will attempt to deal damage and then wipe its memory clean of all the transgressions it experienced, if any. Be like Blazing Shield; forget and forgive.
[Patch 6.2.5] * Blazing Shield (morph): Fixed an issue where this ability's explosion visuals would multiply in intensity with the number of enemies hit, causing your screen to experience level 7 earthquakes and your eyes to be blinded with the brilliance of Meridia. The explosions will now always appear as well, regardless if you dealt damage.
[Patch 7.3.5] * Radiant Ward (morph): Increased the shield scaling per enemy hit to 20% at rank 4, up from 9%.
ESO Patch Note|8.0.5|* Blazing Shield (morph):
- Increased the radius of this morph to 8 meters, up from 6, to better match its visual effects.
- Fixed an issue where the damage could fail to activate in many cases.
ESO Patch Note|10.2.5|* Sun Shield: This ability and its morphs now apply Minor Maim to enemies in the area for 10 seconds. Increased the damage shield scaling per enemy hit to 10%, up from 4%. Increased the base cost to 4590, up from 4320, now that the Shield applies an additional affix and is stronger.
- Radiant Ward: This morph continues to increase the damage shield scaling to 20% per enemy hit. This morph now ranks up in damage shield size by 1.1% per rank, rather than increasing the enemy hit per scaling by 1% per rank. This results in a 3.3% shield size increase at rank IV. This morph also retains its cost reduction, reducing it to 4320, rather than 4050, due to its new base cost.
- Blazing Shield: This morph's damage now scales up to 33% of the damage the shield absorbed at rank IV, up from 30%. Reduced the variance in the power for rank progression to 30-33%, up from 21-30%.
- Developer Comment: In our ongoing crusade to improve the Templar Tank experience, we're making some number tweaks on their primary defensive ability to make it feel punchier when used in the thick of a fight. Minor Maim helps them potentially save a bar slot from another ability or source, while the increased base scaling reduces the variance in power on the morphs to make sure both feel potent enough that you can dive into the front lines and survive for a few moments longer. Now that these abilities have much more density to them, we're also increasing the cost to match the standard other defensive abilities like it have.
