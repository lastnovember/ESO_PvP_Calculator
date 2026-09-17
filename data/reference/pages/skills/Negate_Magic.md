# Online:Negate Magic

Source: https://en.uesp.net/wiki/Online:Negate_Magic
License: CC BY-SA, UESP

Online Skill Summary
id=29844
line=Dark Magic
type=Ultimate
icon=Dark Magic-Negate Magic
desc=Duration: [9 / 10 / 11 / 12] seconds. Create a globe of magic suppression for [9 / 10 / 11 / 12] seconds, removing and preventing all enemy area of effect abilities from occurring in the area. Enemies within the globe are stunned, while enemy players will be silenced rather than stunned.
desc1=Create a globe of magic suppression for 12 seconds, removing and preventing all enemy area of effect abilities from occurring in the area. Enemies within the globe are stunned, while enemy players will be silenced rather than stunned. The globe also damages enemies for [2747 / 2778 / 2807 / 2838] Magic Damage every 1 second.
desc2=Create a globe of magic suppression for 12 seconds, removing and preventing all enemy area of effect abilities from occurring in the area. Enemies within the globe are stunned, while enemy players will be silenced rather than stunned. The globe also heals you and your allies for [2747 / 2778 / 2807 / 2838] Health every 1 second.
linerank=12
cost=225 Ultimate
casttime=Instant
range=28 meters
radius=8 meters
duration=12 seconds
target=Ground
morph1name=Suppression Field
morph1id=29861
morph1icon=Dark Magic-Suppression Field
morph1desc=The globe also damages enemies standing inside it.
morph2name=Absorption Field
morph2id=29881
morph2icon=Dark Magic-Absorption Field
morph2desc=The globe also heals you and your allies standing inside it.
image=ON-skill-Negate Magic.jpg
imgdesc=A globe of magic suppression created by Negate Magic

Negate Magic dispels enemy magic effects and stuns all enemies within its radius. Enemy players will just be silenced, not stunned. The Suppression Field morph also deals damage to all affected enemies, while Absorption Field adds healing for you and your allies within the affected area.

## Notes
- This is the only instance of the Silence effect available to player characters. Silence prevents players from using any skill with a Magicka, Health, or Ultimate cost as long as they are in the affected area. Skills that have no resource cost are also affected. With the exception of Scribing, skills which cost Stamina can still be used, as can normal Light and Heavy Attacks.
- Absorption Field is a recommended morph for the Sorcerer Initiate and Eldritch Mender builds, while Suppression Field is recommended for War Mage.

## Gallery

File:ON-skill-Absorption Field.jpg|Absorption Field morph yellowy visual

## Patch Notes
* The abilities Hardened Ward and Negate Magic no longer share the same icon.
* Negate Magic cast by NPCs will now remove buffs that you cast upon them.
ESO Patch Note|1.6.5|* This Ultimate ability now removes enemy-placed effects when it is initially cast instead of constantly for the entire duration of the ability.
- Reduced the cost of this ability by 10%.
- Suppression Field: This ability has been redesigned, and now applies the Minor Protection buff to your allies inside the field.
- Absorption Field: This ability has been redesigned. Allies who pass through the field now gain the buffs Major Expedition, Major Intellect, Major Fortitude, and Major Endurance for 12 seconds.
- Several monster abilities that could not be previously dispelled by the Sorcerer ability Negate Magic can now be dispelled. This includes the following:
- Angof - Angof's Reach
- Battlemage - Ice Cage
- Flame Atronach - Lava Geyser
- Frost Atronach - Chilling Aura
- Gargoyle - Lava Geyser
- Lich - Defiled Ground, Soul Cage
- Nereid - Water Geyser
- Scamp - Rain of Fire
- Spider Daedra - Lightning Storm
- Thunder Bug - Thunderstrikes
- Titan - Soul Flame
- Wispmother - Rain of Wisps
* Fixed an issue where this ability and its morphs would not apply crowd control immunity to monsters at the end of their stun durations.
ESO Patch Note|2.4.5|* Absorption Field: Redesigned this morph so it now heals you and your allies standing within the area of effect, in addition to stunning or silencing enemies.
- Suppression Field: Redesigned this morph so it now damages enemies standing within the area of effect, in addition to stunning or silencing enemies. Also fixed an issue where the damage from this morph could not critically strike.
ESO Patch Note|2.6.4|* Monsters stunned by Negate Magic are now stunned for 3 seconds, up from 0.6 seconds.
- Negate Magic no longer affects objects outside the area indicated by its telegraph.
- Negate Magic now correctly removes dispellable area effects.
- Negate Magic now displays an area indicator, and requires a line of sight to cast.
- The silence from Negate Magic now displays a visual effect so you can tell you are silent.
* Silence no longer stops Watchers from attacking.
ESO Patch Note|4.0.5|* Increased the duration of this ability and its morphs to 12 seconds from 10 seconds.
- Developer Comments: This was done to make up for the fact that the Persistence passive was redesigned (details below) and no longer affects this iconic Ultimate ability. The net effect is the total duration will remain unchanged.
ESO Patch Note|5.0.5|* Fixed an issue where this ability would fail to continue suppressing Area of Effect abilities inside of the area.
- Updated the tooltip to better describe the function of this Ultimate.
ESO Patch Note|7.0.5|* The following abilities have received significant adjustments to how the server handles their behavior, reducing messages sent between the client and server and reducing the total amount of Area of Effect events occurring. This will largely have little to no effect on their gameplay other than improving their response time to entering or leaving the Area of Effect. In some rarer cases, it will reduce the interaction with sets that proc off application of buffs or debuffs, since you will no longer repeatedly apply these effects to targets inside the area every tick, but rather for the duration the target is inside the area. Their synergies (when applicable) have also been updated to be far more reliable to activate when in the area and they will no longer persist for a short duration after each tick, allowing you to activate them in cases where they could fail or were already used, going on cooldown with no effect, or gaining their effects despite already being used.
- Blood Altar and morphs
- In an instance where Blood Feast and Blood Funnel are both available, Blood Feast will now always take priority as it is stronger than Blood Funnel.
- Bone Totem and morphs
- Boneyard and morphs
- Cleansing Ritual and morphs
- Both morphs of Dragonknight Standard
- This will also fix an issue where the morphed version of this ability failed to properly fire its synergy, Shackle, when activated.
- Lightning Splash and morphs
- Necrotic Orbs and morphs
- Negate Magic and morphs
- Nova and morphs
- Rune Focus and morphs
- Spear Shards and morphs
- The morphs of this ability now tick every 1 second instead of 500ms.
- Increased the potency of their ticks by 103.3% to ensure their DPS/HPS remains almost the same, as well as fixing an issue where their values were missing rank up progression built into them.
- Scrolling Combat Text now properly displays successful silences with these abilities.
* Fixed an issue where this Ultimate and morphs' dispel failed to target most Area of Effects.
* Fixed an issue with this Ultimate and its morphs where they could not dispel another version of themselves. Previously, Negate Magic would only dispel Absorption Field or Suppression Field but fail to dispel an enemy Negate Magic, or any permutation where the Ultimates were of the same version. Now, any version of these Ultimates will actively dispel any version of the Ultimates they are placed on if they are sourced from enemies.
