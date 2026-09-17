# Online:Siphoning Strikes

Source: https://en.uesp.net/wiki/Online:Siphoning_Strikes
License: CC BY-SA, UESP

Online Skill Summary
id=37977
line=Siphoning
icon=Siphoning-Siphoning Strikes
desc=Channel a portion of your soul to convert Health to [1700 / 1800 / 1900 / 2000] Magicka and Stamina. While slotted on either bar, your soul yearns for the warmth of life. All damage you deal heals you for [950 / 1050 / 1150 / 1250] Health, up to once every 1 second.
desc1=Channel a portion of your soul to convert Health to 2000 Magicka and Stamina. While slotted on either bar, your soul yearns for the warmth of life. All damage you deal heals you for [1500 / 1600 / 1700 / 1800] Health and reduces the cost of your next Leeching Strikes by 10%, stacking up to 10 times. This effect can occur once every 1 second.
desc2=Channel a portion of your soul to convert Health to 2600 Magicka and Stamina. While slotted on either bar, your soul yearns for the warmth of life. All damage you deal heals you for 1250 Health and restores [170 / 180 / 190 / 200] Magicka and Stamina, up to once every 1 second.
linerank=30
cost=4000 Health
attrib=Magicka
casttime=Instant
target=Self
morph1name=Leeching Strikes
morph1id=38015
morph1icon=Siphoning-Leeching Strikes
morph1desc=Increases the healing done and grants ramping cost reduction for the next cast when the heal activates.
morph2name=Siphoning Attacks
morph2id=38050
morph2icon=Siphoning-Siphoning Attacks
morph2desc=Increases the Magicka and Stamina restored, and the heal now also restores Magicka and Stamina.
image=ON-skill-Siphoning Strikes.jpg
imgdesc=Siphoning Strikes and its morphs' cast visual

Siphoning Strikes passively restore Health when dealing damage once every second. The active immediately restores Magicka and Stamina. The Leeching Strikes morph heals more and reduces the cost of the next Leeching Strikes each time it heals, while Siphoning Attacks increases the Magicka and Stamina restored upfront and makes the heal restore some too.

## Notes
- As with all other "While slotted on either ability bar" skills, this doesn't work if you have Oakensoul Ring and have this skill in the disabled ability bar.
- Before Update 14, the base skill restored Magicka and Stamina on basic attacks, while the Siphoning Attacks morph allowed you to also gain Magicka and Stamina from other direct damage attacks in addition, and Leeching Strikes turned this ability into a toggle, reducing weapon and spell damage, but also restoring some Health with each attack.
- Before Update 7, this spell was a toggle, and would lower Weapon and Spell Damage while on.
- Siphoning Attacks is a recommended morph for the Nightblade Initiate, Blood Magus and Deathweaver builds, while Leeching Strikes is recommended for Umbral Assassin.

## Patch Notes
ESO Patch Note|1.2.3|* Siphoning Strikes: This ability now restores slightly less resources, and will no longer desync your resource bars upon use.
- Leeching Strikes: The tooltip for this ability now shows the correct percentage of health recovery.
* Reduced the damage penalty for having Siphoning Strikes active by 5%.
ESO Patch Note|2.3.5|* Fixed an issue where the weapon visual effects from abilities such as Grim Focus, Siphoning Strikes, and Expert Hunter could get visually detached from the weapon.
- Leeching Strikes: Increased the amount of Health restored from this morph to 3% of your maximum Health from 2%.
- Siphoning Attacks:
- Fixed an issue where this morph could proc its resource return on every tick from a damage over time effect.
- Increased the amount of resources provided by this ability and the Siphoning Attacks morph by roughly 10%.
ESO Patch Note|3.0.5|* This ability now causes your Light and Heavy Attacks to restore Health instead of Magicka or Stamina.
- Increased the duration of this ability and its morphs to 20 seconds from 15 seconds.
- Reduced the cost of this ability and its morphs by approximately 50%.
- Recasting this ability or its morphs early will now always trigger the ending resource restore. The value of this restore is based on the length of time the abilities were active, similar to Rally's heal.
- Each Light or Heavy Attack from this ability or its morphs will now restore less resources, but the final burst at the end will restore more resources. The total resources restored by this ability will remain roughly the same.
- Leeching Strikes: This morph now converts the ability into a Stamina ability and causes your Light and Heavy Attacks to restore Stamina based on your character level, and an additional burst of Stamina when the effect ends.
- Siphoning Attacks: This morph now causes your Light and Heavy Attacks to also restore Magicka based on your character level, and an additional burst of Magicka when the effect ends.
- Developer Comments: This is a significant reduction to the Magicka and Stamina restored by these abilities, but the addition of Health restore should give Nightblades more healing to improve their survivability. The changes also make the resource restore portion of these abilities better if you are not weaving Light Attacks perfectly, which is desirable for tanks and healers who spend time blocking or healing.
* Leeching Strikes: Fixed an issue where Rank III of this morph was not returning the correct amount of Stamina when the ability ended.
* Leeching Strikes: Fixed an issue where you could block the heal from this morph.
* Leeching Strikes: Fixed an issue where this morph was unable to be cast while you were silenced.
* Fully charged Heavy Attacks now restore twice the amount of Health and resources for this ability and its morphs.
ESO Patch Note|4.3.5|* The heal from Siphoning Strikes and Morphs will no longer be considered "proc" abilities, meaning it can proc other proc abilities such as item sets and enchants.
- Note: We will continue evaluating which abilities should and should not be considered procs in the future.
* Fixed an issue where this ability and its morphs had a cooldown on the heal. Since Light and Heavy Attacks already have their own unique cooldowns, this previous interaction meant if you had a set such as Blood Moon, you were not gaining the full efficiency of the bonus.
* Fixed an issue where this ability and its morphs could proc off Mend Wounds and its morphs. The soul-stealing power of this ability is now reserved for damaging Light and Heavy Attacks.
ESO Patch Note|9.3.5|* Reworked this ability and its morphs to be simpler to use, while making their resource recovery more engaging.
- When activated, the ability will instantly drain 4000 Health to restore 2000 Magicka and Stamina.
- When the ability is slotted on either bar, any damage you deal will heal you for 1250 Health, up to once every second.
- Leeching Strikes (morph): This morph now increases the passive healing done to 1800 Health. Whenever the heal activates, it reduces the cost of your next Leeching Strikes cast by 10%, stacking up to 10 times. The cost reduction lasts until consumed, your character dies, or you rezone.
- Siphoning Attacks (morph): This morph now increases the resources restored to 2600 Magicka and Stamina. Whenever the heal activates, it also restores 200 Magicka and Stamina.
- Developer Comment:The Nightblade class has long been limited in its overall performance by how well the player can utilize Light and Heavy Attacks between each ability, making it very difficult for many players and build types. In efforts to ease back some of this demand, we’re moving forward with a rework to their primary sustain tool to be more usable by any build or player. Rather than needing to constantly activate the ability to be eligible to heal when you properly weave, it now passively heals you anytime you deal damage, simply for having it slotted. The resource portion of the ability is now granted at the base level of the skill (rather than morphs) and no longer grants exclusive resources, but comes at a risky cost of Health - which we hope the passive healing helps lessen the risk of engaging with. Additionally, the morphs now focus on the different aspects of the skill, where Leeching Strikes focuses on raw healing and reducing the risk of activation, while Siphoning Attacks doubles down on resource recovery by adding a passive recovery option and increasing the rewards of its activation.
