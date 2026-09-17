Xbox One Patch Notes v1.10.1.0
Xbox One Patch Notes v1.10.1.0
Posted 2017-11-30 by ZOS_GinaBruno ·
forums.elderscrollsonline.com/en/discussion/383249 ·
archived 2026-09-12
The Elder Scrolls Online v1.10.1.0 is an incremental patch that includes a temporary fix for the long loading screens that many of you have experienced since the Clockwork City DLC game pack was released. In Update 16, we added in a new system that refined the character texture loading pipeline as part of our ongoing effort to increase performance and framerate in high-intensity situations (such as in Cyrodiil and densely-populated cities). Unfortunately, this new pipeline was causing some character textures to get lost, which was causing the load screen to never drop because there were still textures that need to be loaded.
While we continue to work on fixing this issue fully, this patch includes two changes. First, we’re reverting to the old pipeline which doesn’t have this issue, but this may affect how quickly you see other characters loading in (this will essentially be the same as it was before Clockwork City). Further, we’re introducing a new failsafe that will force your load screen to drop after two minutes if it is only waiting on textures.
In the future when we have a more permanent fix, we plan to re-enable the new pipeline because it makes for better game performance, but when we do that, we’ll be adding the equivalent of a switch on our side that we can turn off (to fall back to the old system) if we see these kinds of issues crop up again, rather than make you wait for another patch.
We’ve also included several fixes for Clockwork City content including quests and the Asylum Sanctorium Trial, player ability fixes such as using a charge ability that leads you into a loading screen, a fix for Scrolling Combat Text being off-center, and more. The size of this patch is approximately 800MB in size.
Fixes & Improvements
Morrowind
Clockwork City
Combat & Gameplay
Combat Fixes & Improvements
Itemization Fixes & Improvements
Base Game Patch
Art & Animation
Combat & Gameplay
Crown Store & Crown Crates
Dungeons & Group Content
Miscellaneous
Quests & Zones
UI
Battlegrounds
Fixed an issue where Mark of the Worm was not being removed from some players at the end of a Battleground match.
Fixed an issue where your game could occasionally crash while in a Battleground.
Quests
The second Omnivox alarm after you go over the bridge for the quest “Lost in the Gloam” is no longer a silent alarm.
Asylum Sanctorium Trial
Saint Felms will once again use the Shrapnel Storm ability when engaged on his upper platform.
Achievements
Removed the Clockwork Style Master achievement as the Clockwork Style Motif is not yet available.
Mementos
The spirit summoned by Nanwen’s Sword no longer has collision.
General
You will no longer become blocked if you collect all the Precursor components before attempting to do the quest "The Precursor".
Quests
Glitter and Gleam: You now only require 3 Ornate items to fulfill the conditions of this quest for the Blackfeather Court Dailies.
Where Shadows Lie: If you somehow end up at the Wayshrine after taking the portal out of the Cogitum Centralis, you will now be directed correctly to Sotha Sil.
General
Fixed an issue where you could move significantly faster than intended while on a mount.
Fixed an issue where the following abilities (and their associated morphs) could not be cast against an enemy player with the Shield Wall ability active:
Eclipse
Petrify
Rune Prison
Fixed an issue where it was possible to have two combat pets active at the same time.
Fixed an issue where using a charge ability from stealth would not correctly update your position or subsequent actions to enemy players.
Made improvements to the issue where you could use a charge ability, such as Critical Charge, straight into a loading screen.
Note: We’ve added some logging on the back end to identify other similar issues when using these types of abilities.
Nightblade
Shadow
Shadow Image (Summon Shade morph): Fixed an issue where attempting to teleport to your shade while you were out of range of it would cause you to lose some character functionality.
Veiled Strike: Fixed an issue where using this ability or its morphs from stealth wouldn’t cause the enemy to be stunned and go off-balance.
Champion System
Fixed an issue where some 10, 30, 75, or 120-point unlock abilities were still functioning in non-Champion Point PvP campaigns.
Item Sets
Concentrated Force: Fixed an issue where this item set (including the Perfect version) would not proc the Burning, Concussed, and Chilled effects on the enemy if you were using Force Shock at a long range.
General
Fixed an issue where reflections on the Xbox One X would only display the sky in some areas, rather than the full environment.
Monsters
All Spider Daedra have renounced their vows of non-violence and once again fight back against their enemies.
Collections
Fixed an issue where the Ebony Brassilisk pet was visible in your collections menu before you actually acquired it.
General
Fixed an issue that prevented you from queuing for some DLC-specific dungeons when using the Grouping Tool.
Trials
Adjusted the following Trial encounters to be more forgiving against player character pets:
The Warrior
Vashai and S'Kinrai
Zhaj'hassa the Forgotten
General
Fixed an issue where your game could crash when viewing artificially-created item links in chat.
Fixed an issue that would cause your game to freeze when resuming from a suspend.
General
You will once again be able to receive your own world boss daily quests in Wrothgar and Vvardenfell even if you had recently completed a different one shared by another player.
Fighters Guild
Guildmaster Sees-All-Colors will now respawn properly if your character dies in Mzeneldt.
The Dangerous Past: Sees-All-Colors will once again appear at the beginning of the quest if you were sent there by Bera Moorsmith.
General
Fixed an issue where the nameplates from group members could disappear after going through a door together.
Fixed an issue that was preventing the Lore Library from displaying all known book collections.
Fixed an issue that would cause some players to not display in the Recent Players UI.
Gameplay
Fixed an issue that was causing the scrolling combat text to appear in the wrong location on the Xbox One X.