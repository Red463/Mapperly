# Mapperly 1.2.1: release checks

Install Mapperly-1.2.1.zip and run `/reload` before testing. This stable release consolidates the local diagnostic, compatibility, combat-control and branding builds since 1.2.0. Reload clears old diagnostic mouse handlers. No saved settings need resetting.

1. Open the map and make sure Lock map position is off. Drag the title bar once before capturing.
2. Run `/mapperly mapreport start` and drag the map again. Dragging must still work.
3. Change the theme or lock/unlock setting that previously reset the position. Run `/mapperly mapreport` immediately and copy the report with Ctrl+C.
4. Close the report, then verify the map still drags when unlocked. Repeat in the other theme if needed.

The report now identifies `Mapperly.trim` in focus chains and includes Title bar / Map trim geometry and `mouse` state. Trim should remain `mouse=false`; title-bar drag events should appear when dragging. Global mouse events, setter callers and layout state remain captured.

The supplied rc.8 trace confirmed that capture enabled trim mouse input: clicks reached trim.OnMouseDown/Up rather than bar.OnDragStart. EnhanceQoLMover also called map setters, but those entries alone do not prove it caused the original position reset. Capture a fresh reset after this hotfix before attributing it to another addon.

## Other release checks

- Confirm the new blue-and-gold addon-list icon and M portrait badges appear, with transparent backgrounds and unchanged placement. Check both themes.
- With EnhanceQoL's mover globally enabled and World Map ticked, open Mapperly and dismiss any update notice. The compatibility warning should appear once per session, with the setting path. Untick `/eqol` > Interface > Mover > World > World Map and reload; no warning should appear. No external settings are changed by detection.
- With Lock map position off, enter combat and drag the map. Release it, then close using X. Repeat with M while the map is visible. After combat, reopen it and confirm its saved position. Check both map sizes. Actual protected-frame restrictions and resizing deferral remain in place.
- If the map is reopened before combat ends, deferred cleanup must not close it. Locking must still prevent dragging.
