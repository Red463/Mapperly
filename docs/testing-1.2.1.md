# Mapperly 1.2.1: diagnostics must preserve map dragging

Install Mapperly-1.2.1.zip and run `/reload` before testing. Stopping the old capture does not remove its installed mouse handlers; reload is needed to clear them. No saved settings need resetting.

1. Open the map and make sure Lock map position is off. Drag the title bar once before capturing.
2. Run `/mapperly mapreport start` and drag the map again. Dragging must still work.
3. Change the theme or lock/unlock setting that previously reset the position. Run `/mapperly mapreport` immediately and copy the report with Ctrl+C.
4. Close the report, then verify the map still drags when unlocked. Repeat in the other theme if needed.

The report now identifies `Mapperly.trim` in focus chains and includes Title bar / Map trim geometry and `mouse` state. Trim should remain `mouse=false`; title-bar drag events should appear when dragging. Global mouse events, setter callers and layout state remain captured.

The supplied rc.8 trace confirmed that capture enabled trim mouse input: clicks reached trim.OnMouseDown/Up rather than bar.OnDragStart. EnhanceQoLMover also called map setters, but those entries alone do not prove it caused the original position reset. Capture a fresh reset after this hotfix before attributing it to another addon.
