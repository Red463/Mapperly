# Mapperly 1.2.2: combat opening and compatibility

Install Mapperly-1.2.2.zip and `/reload`.

## Open during combat

1. Leave the map closed, enter combat, then press M. It should open. Press M again to close, then reopen it using `/mapperly`.
2. Repeat immediately after login/reload without first opening the map out of combat. The map should open and draw normally; deferred sizing finishes when combat ends.
3. Check both compact/enlarged sizes, both themes and the quest-pane toggle. Opening in combat must not overwrite those choices. Dragging and X closing should remain available when unlocked and unprotected.
4. Leave the map open as combat ends. It should stay open and restore its saved layout/position. Close it before combat ends in another attempt: it should stay closed.

World-map-disabled game rules and genuinely protected frames retain native restrictions. The game client is needed for final in-game appearance confirmation; the automated harness models the native blocked panel helpers and first-show transition from the Forever UI source.

## EnhanceQoL compatibility (included from 1.2.1)

- With EnhanceQoL Mover and its World Map checkbox enabled, open the map. After welcome/update notices or other Mapperly dialogs close, the conflict warning should appear once. Dismiss it and reopen the map: it should not repeat this session.
- Follow `/eqol` > Interface > Mover > World and untick World Map, then `/reload`. Open Mapperly: no conflict warning should appear and dragging/settings changes should preserve position.
- With the entire EnhanceQoL mover disabled, or without EnhanceQoL installed, no warning should appear.
- In combat, the warning should wait until combat ends. It should use the selected Default or Minimal Charcoal appearance.
- No EnhanceQoL settings should change just from Mapperly detecting or dismissing the warning. The rest of EnhanceQoL's mover remains available.
- The prior map-report mouse-input fix is included. `/mapperly mapreport start` must still allow map dragging.

Detection uses the loaded `_G.EnhanceQoL.Mover.db` global enable flag, the WorldMapFrame per-frame flag and read-only registered entry defaults. It deliberately avoids IsFrameEnabled, which initializes external saved defaults in the inspected Forever implementation. Missing or unknown external configuration is not treated as a confirmed conflict.

Source reviewed: https://github.com/fiote/EnhanceQoLForever/blob/master/EnhanceQoLMover/Init.lua and EnhanceQoLMover.lua; English menu labels are Mover > World > World Map under Interface.
