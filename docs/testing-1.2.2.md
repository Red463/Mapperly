# Mapperly 1.2.2: EnhanceQoL mover warning

Install Mapperly-1.2.2.zip and `/reload`.

- With EnhanceQoL Mover and its World Map checkbox enabled, open the map. After welcome/update notices or other Mapperly dialogs close, the conflict warning should appear once. Dismiss it and reopen the map: it should not repeat this session.
- Follow `/eqol` > Interface > Mover > World and untick World Map, then `/reload`. Open Mapperly: no conflict warning should appear and dragging/settings changes should preserve position.
- With the entire EnhanceQoL mover disabled, or without EnhanceQoL installed, no warning should appear.
- In combat, the warning should wait until combat ends. It should use the selected Default or Minimal Charcoal appearance.
- No EnhanceQoL settings should change just from Mapperly detecting or dismissing the warning. The rest of EnhanceQoL's mover remains available.
- The prior map-report mouse-input fix is included. `/mapperly mapreport start` must still allow map dragging.

Detection uses the loaded `_G.EnhanceQoL.Mover.db` global enable flag, the WorldMapFrame per-frame flag and read-only registered entry defaults. It deliberately avoids IsFrameEnabled, which initializes external saved defaults in the inspected Forever implementation. Missing or unknown external configuration is not treated as a confirmed conflict.

Source reviewed: https://github.com/fiote/EnhanceQoLForever/blob/master/EnhanceQoLMover/Init.lua and EnhanceQoLMover.lua; English menu labels are Mover > World > World Map under Interface.
