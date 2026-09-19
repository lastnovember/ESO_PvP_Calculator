# Online:Housing Editor

Source: https://en.uesp.net/wiki/Online:Housing_Editor
License: CC BY-SA, UESP

The Housing Editor is a feature which allows you to place and decorate furnishings and other items inside Player Houses, and purchase new furnishings from the Crown Store. Many items can also be crafted or purchased from Furnishers, and then placed in houses using the Editor.

## Controls
By default, the Housing Editor is accessed by pressing F5 while in your house or a friend's house where you have Decorator access. While in edit mode, most other menus will be inaccessible until you turn off edit mode (using the same key that activates it). Any item that can be moved will now have a white aura around it when you look at it, and you can select an item with the left mouse button. You can move the item simply by turning your view or walking around. The other options you have are:
- [R] Browse - opens up the item browser, see below (this option is only available in your own house, not other houses where you have Decorator access)
- [Z] Go to Entrance - instantly teleports you to the house's entrance, useful if you get yourself trapped in the house.

While you have an item selected, you will see a series of options on the bottom:
- [X] Cancel - puts the item back where you found it
- [LMB] Place - unselects the item and places it in its current location
- [R] Put Away - puts the item in your inventory so you can move it somewhere else, useful for moving an item to another house, or moving an item from one room to another, or for selling or trading the item to another player.
- [F] Cursor Mode - gives you more precise control over the item's rotation by allowing you to rotate it with the mouse button on the 3 rotation rings. (Cursor mode can be toggled off again with the F key, even though it does not display this option.)needs new Precision Edit options
- [T] Surface Drag Off - By default, items will be placed against whatever solid surface you are pointing at. By turning this off, you are able to place item in mid-air or embedded with other items, below the ground, etc. When this mode is turned off, you are given two additional options to push or pull the item using your mouse wheel.
- [RMB] Align - Attempts to align the item against the surface you're pointing at, useful for placing items against a wall or ceiling. If the item does not behave as you expect when doing this, try putting the item away and re-placing it to reset its rotation.
You can also rotate selected items using the 1-6 keys. The icons and the colored rings around the item will give you an indication of the direction of rotation. Be careful about rotating on the green and red axes as it is possible to get an item into gimbal lock when near 90 degrees off its default rotation (meaning it won't stay at certain rotations). If you're having trouble getting an item to stay in its set rotation, try rotating it 180 degrees around and approach it from the other direction.

## Item Browser
The Item Browser, accessed (by default) by pressing R while in edit mode, will display a House Information window, along with an inventory screen with 4 tabs.

### House Information
The name and zone are displayed at the top (note that renaming your house in the Collections menu is not reflected here, only the default name will be shown.) Below that are the counts for the various types of furnishings you have, as well as the maximums for the size of your house (which also depends on whether you have an ESO+ subscription).
- Traditional Furnishings - This includes most normal furnishings
- Special Furnishings - Includes visual effects furnishings, which are limited to improve performance. There are few available; examples include Fogs of the Hag Fen and Mists of the Hag Fen.
- Collectible Furnishings - Includes all static Collectibles, which mainly means Undaunted Trophies.
- Special Collectibles - Includes all animated Collectibles, such as Mounts, Non-Combat Pets, and Assistants.
Next is an indicator as to whether this is your Primary Residence, which can be changed in settings, and finally a Population counter, which tells you how many players (including yourself) are present in the house, and what the cap is for that as well.

### Housing Inventory
There are 4 tabs in this window:
- Place - lets you select an item from your inventory. You can browse the categories and sub-categories on the right, or type part of the item name in the "Filter By" field if you're looking for something specific.
- Purchase - lets you purchase new items from the Crown Store. There is a similar list of categories and sub-categories here. Before spending crowns, be aware that most of the items available here can also be acquired by other means.
- Retrieve - lets you pick up items that have already been placed. You again have the categories and sub-categories, but in addition, you will see that items here are sorted based on distance, so the closest items will be at the top, with an arrow indicating the direction. This can be very handy if you lose an item inside a wall or something.
- Settings - This screen lets you manage your permissions for visitors to your house. In the General section you can set the house to be your Primary Residence (necessary to allow other players to visit when you are not at home) and also set the default visitor access. "No Access" means other players cannot enter your home at all. "Visitor" allows them to enter the house but not move items (though they can still do things like turning lights on and off). "Decorator" allows other players to move items around in your house. They cannot remove or add items, though they may place them where they are difficult to find without the "Retrieve" menu, so you should only grant this access to people you generally trust. (It is highly advised to keep the default at "No Access" and only allow specific friends or guilds to have access.) The other sections let you add or ban specific players or entire guilds. Once you have these set up for one house, you can use "Load Permissions" to apply the same settings to your other houses.

### Character Pathing

Character Pathing is a Homestead feature introduced in Update 27. It allows you to create paths along which collectible assistants, pets, mounts, and houseguests will travel. This is achieved by placing down "Nodes" in your house, viewable only through the Housing Editor. The Nodes for each collectible are color-coded, and a maximum of 30 can be placed for each collectible. Pathing generally keeps the character adhered to the ground, although they will clip through objects and will even fly through the air if the Node is placed sufficiently high enough. The character will not move while their path is being edited.

Character Pathing has its own set of controls when interacting with Nodes:
- [Q] Create Path / Path Edit - places initial node beneath the character and opens Character Pathing editor for their path
- [LMB] Place Node - places a new Node for the selected path
- [RMB] Align Node - attempts to align the Node against the surface you're pointing at
- [RMB with Node highlighted] Add Node Before - allows you to place a new Node prior to the one you are looking at (default placement connects Nodes sequentially along the path)
- [U] Speed - toggles movement speed between Nodes (Walk, Jog, Run, Sprint); this is also indicated by the arrows between linked Nodes
- [I] Wait Time - toggles time spent waiting at the Node (0s, 3s, 10s, 30s, 1m, 3m)
- [R with Node selected] Finish Placement - deselects Node and returns to Character Pathing editor
- [R] Path Settings - opens Path Settings menu for the path currently being edited (Pathing On/Off toggle, Pathing Types Ping Pong/Loop/Random)
- [Q] Confirm - exits Character Pathing editor for current path
