# Mapperly 1.2.0-rc.8: map-position report

Replace the Mapperly folder with the folder in Mapperly-1.2.0-rc.8.zip and reload. This build adds diagnostics to the normal addon; it does not change map positioning.

## Capture the friend's map reset

1. Open the map with M.
2. Type `/mapperly mapreport start`.
3. Drag the map to the desired position and release it.
4. Open Mapperly Settings and change the theme, or tick Lock map position. If either causes a reset, leave the map in that state.
5. Immediately type `/mapperly mapreport`.
6. The report opens with all text selected. Press Ctrl+C and paste the full report back to Tom. Include which setting triggered it and whether it snapped during dragging or after release.

Capture one reproduction at a time. If both theme and lock trigger it, make a separate capture for each using the same commands. Capture is session-only: export before reloading or logging out.

## Commands

- `/mapperly mapreport` opens a current snapshot and any captured events, stops capture, and selects the text for copying. It also works without starting a capture.
- `/mapperly mapreport start` clears the previous trace and starts a new bounded capture. It does not reset the map or its saved position.
- `/mapperly mapreport stop` stops capture without opening the report. The captured events remain available until a new capture or reload.
- `/mapperly report` still opens the separate navigation/route report.

## Checks

- Confirm the report includes the correct physical resolution, UIParent dimensions, UI scale and saved compact/enlarged positions.
- Verify moving the map and changing theme or lock produces drag, layout and position-set events with caller stacks.
- Export in both Default and Minimal Charcoal themes; text is scrollable and copyable. Escape or Close dismisses the window.
- Opening a snapshot alone must not move the map, change settings or create a saved diagnostic log. A new login does not record automatically.
- Reports include addon identifiers and local file paths from Lua caller stacks so conflicts can be investigated. Nothing is sent automatically; player name, GUID and realm are redacted.
