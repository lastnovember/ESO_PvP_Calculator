# Online:Bolt Escape

Source: https://en.uesp.net/wiki/Online:Bolt_Escape
License: CC BY-SA, UESP

Online Skill Summary
id=30205
line=Storm Calling
icon=Storm Calling-Bolt Escape
desc=Transform yourself into pure energy and flash forward, stunning enemies near your final location for [1 / 1.7 / 2.3 / 3] seconds. This effect cannot be blocked. Casting again within 4 seconds costs 33% more Magicka.
desc1=Target: Self. Transform yourself into pure energy and flash forward, dealing [3811 / 3852 / 3894 / 3936] Shock Damage to enemies in your wake and stunning them for 3 seconds. This effect cannot be blocked. Casting again within 4 seconds costs 33% more Magicka.
desc2=Transform yourself into pure energy and flash forward. After reaching your location, you become immune to snare and immobilize effects for 2 seconds. A ball of lightning is summoned at your end point, which intercepts up to 1 projectile attack made against you every 1 second for [2 / 2.3 / 2.7 / 3] seconds. Casting again within 4 seconds costs 33% more Magicka.
linerank=42
cost=3780 Magicka
attrib=Magicka
casttime=Instant
range=15 meters
radius=6 meters
target=Area
morph1name=Streak
morph1id=30215
morph1icon=Storm Calling-Streak
morph1desc=Now deals damage and stuns enemies between your beginning and final location.
morph2name=Ball of Lightning
morph2id=30224
morph2icon=Storm Calling-Ball of Lightning
morph2desc=Summons a ball of lightning that protects you from projectiles, but no longer stuns enemies. Grants brief snare and immobilization immunity after casting.
image=ON-skill-Bolt Escape.jpg
imgdesc=Bolt Escape and its morphs' visual

Bolt Escape causes you to teleport several meters forward, stunning all enemies at your final location. Streak will also damage and stun all enemies along the path of travel, while Ball of Lightning absorbs any projectiles while traveling and for a few seconds afterwards.

## Notes
- The direction of teleportation will be wherever the camera is pointing, not where your character is facing, so don't worry about trying to line up your character in the direction you want to go. Aim by rotating your view instead.
- This spell stuns enemies at your final position, not your starting location. Moreover, you will invariably end up facing away from the enemies that were around your starting position. These two facts make it somewhat tricky to use in combat. Following it up with a quick reverse roll-dodge can get you facing the right direction again. The Streak morph will also help in this regard, as enemies all along the path will be stunned. You can also aim your view towards a nearby wall or other obstacle so you don't teleport too far from the fight to take advantage of the stunning effect.
- Since you will teleport straight forward and keep the same elevation, this can be used to jump across small chasms to get to otherwise inaccessible places beyond the range of a simple jump. This is never required and rarely advantageous, but it can occasionally be used as a shortcut. Be careful, however. If the gap is a bit too wide, you may find yourself in midair with a long painful drop below.
- Ball of Lightning is a recommended morph for the Sorcerer Initiate build.

## Bugs
- The Ball from Ball of Lightning morph is flagged as a pet in the code and triggers some effects requiring an active pet.

## Gallery

File:ON-skill-Ball of Lightning ball.jpg|Ball of Lightning morph ball visual

## Patch Notes
* You can no longer use the ability Bolt Escape while carrying an Elder Scroll.
* After using Bolt Escape, the next use within 4 seconds costs 50% more.
* Streak will no longer affect more than six targets, which was resulting in a much larger amount of Ultimate gain than intended.
ESO Patch Note|1.6.5|* Crystal Fragments: Fixed an issue where this morph was applying multiple passives each time it was cast. We also fixed an additional issue where this ability's instant cast wasn't proccing when casting Bolt Escape.
- The disorient portion of Bolt Escape and its morphs has been changed. It now results in a 1.5 second stun and properly triggers crowd-control immunity for the target when the stun effect ends.
* Fixed an issue where the camera in third-person view could become detached briefly when using movement abilities, such as Bolt Escape.
* Fixed an issue where this ability and its morphs could fail to function in certain locations.
* Ball of Lightning: Fixed an issue where the ball summoned from this morph could intercept channeled beam attacks instead of only projectiles.
Shadow Image]], can no longer be cast before the Battleground match has started.
* Fixed an issue where Streak Fatigue could be avoided unintentionally.
ESO Patch Note|5.0.5|* Fixed an issue where this ability and its morphs could stun targets behind walls.
- Streak: This ability will now scale with your highest offensive stats, and increased the stun duration to 3 seconds from 1.8 seconds.
ESO Patch Note|5.1.5|* This ability and its morphs' stuns can no longer be blocked.
- Developer Comment: Previously, these abilities could be blocked without draining resources. While investigating this issue, we determined that the theme of charging into a group of enemies as a ball of pure energy would not be thwarted by a measly shield.
- Bolt Escape Fatigue (morph): Reduced the ramping cost increase from using Bolt Escape or its morphs to 33% per stack from 50% so it operates closer to Roll Dodge.
ESO Patch Note|5.2.5|* The fatigue from this ability and its morphs now apply only if you successfully teleport 1 meter or more, instead of whenever you activate the ability.
- This ability no longer stuns targets in a 4 meter radius from your origin location, but instead stuns targets in a 6 meter radius at your final location.
- Fixed an issue where you could become stuck in place after attempting to cast this ability or any of its morphs when a target was outside your line of sight.
- Ball of Lightning (morph):
- This morph now ranks up in duration of the summoned ball of lightning, which now lasts 3 seconds at Rank IV, up from 2.
- This morph also adds 2 seconds of snare and immobilization immunity after teleporting, but no longer stuns enemies at its end location.
- Fixed an issue where this morph was only absorbing spell-based projectiles, rather than any, as the tooltip indicates.
- Streak (morph):
- This ability now creates a cone behind you after casting that damage and stuns enemies inside of it, and enemies at your end location. The length is now 17 meters with a 40 degree arc, rather than being a 4 x 15 meter rectangle.
* Ball of Lightning (morph): Fixed an issue where the projectile absorption field could persist longer than intended under certain circumstances.
ESO Patch Note|6.1.5|* Ball of Lightning (morph): Fixed an issue where this ability's actual ball of lightning could count towards successful kills in some cases.
- Fixed an issue where the ball would leave a corpse for a brief moment.
* Ball of Lightning (morph): This ability's projectile absorption now operates more closely to Spell Wall or other abilities that deal with absorbing/deflecting ranged attacks. This should fix a few issues where it could absorb attacks it shouldn't have been able to.
ESO Patch Note|7.1.5|* Ball of Lightning (morph): The ball of lightning summoned from this ability now only intercepts projectiles from the caster of the ability, rather than any ally in the ball's vicinity. The ball now only absorbs up to 1 projectile per second, down from 100.
- Developer Comment: This ability is currently enabling far too much protection against ranged attackers, not only for the caster but their allies as well, meaning skilled sorcerers can deny any ranged threats when properly utilizing this skill for them and their group.
* Fixed an erroneous VO shout that would occur when using this ability and its morphs.
