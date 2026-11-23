# Mapperly 1.2.3: combat map controls

Install Mapperly-1.2.3.zip and `/reload`. Keep EnhanceQoL's World Map mover disabled if installed.

1. Open the map, turn off Lock map position and enter combat. Drag its title bar and release it. The map should move and remember the released position.
2. Click X during combat: the map should close immediately. Repeat with M while the map is visible.
3. Leave combat and reopen the map. It should stay open normally and retain its position. If the map was reopened before combat ended, deferred cleanup must not close it.
4. Check compact/enlarged views and both themes. Enable Lock map position and confirm dragging remains disabled.
5. Map resizing and layout changes still wait until combat ends. If another addon makes WorldMapFrame protected, the game can restrict movement/hiding; `/mapperly mapreport` now includes `protected=` to diagnose this case.

The Forever native HideUIPanel helper rejects insecure addon calls in combat even for an unprotected frame. This build uses the frame's normal Hide/OnHide lifecycle during combat and completes native panel-manager cleanup after PLAYER_REGEN_ENABLED, without reopening or re-closing a map.

Reference: https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_UIParentPanelManager/Shared/UIParentPanelManager.lua
