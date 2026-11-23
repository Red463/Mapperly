# Player-facing release highlights

Keep each release to at most four short, plain-language bullets (180 characters each). Packaging requires a section matching the TOC version and regenerates Data/ReleaseNotes.lua.

## 1.2.3

- Fix the map-drag error when native display changes clear the frame's movable flag, including deferred combat opening.
- Check movement readiness before starting and clean up safely if movement is rejected, without leaving the map stuck in dragging mode.

## 1.2.2

- Fix opening the closed map with M or /mapperly during combat, including the first opening after login.
- Keep your map size and quest-pane settings; finish deferred layout after combat. Native map-disable rules and protected-frame restrictions still apply.

## 1.2.1

- New blue-and-gold Mapperly branding, with a clearer small icon and M badges for the map and addon windows.
- Move the unlocked map and close it with X or M during combat when the game permits the frame operations.
- Warn when EnhanceQoL's World Map mover is enabled, with the setting to disable. Other EnhanceQoL preferences are left unchanged.
- Fix map-report capture blocking dragging, and include more useful frame and mouse-input details in diagnostic reports.

## 1.2.0

- Smart navigation plans routes through supported zones using terrain, roads and available travel methods, with guidance on the map and minimap.
- Search active quests, find quest pickups and navigate to nearby services. Follow route steps, recover from detours and resume saved journeys.
- Choose road-preference strength and avoid swimming where possible. Bundled tram and Great Lift guidance needs no trip recording.
- Welcome and update notices explain new features. Copy route diagnostics with /mapperly report or map-position diagnostics with /mapperly mapreport.

## 1.2.0-rc.8

- Use /mapperly mapreport to copy display, UI scale and map-position details when reporting a problem.
- Use /mapperly mapreport start before reproducing a map reset, then /mapperly mapreport to copy the captured events.

## 1.2.0-rc.7

- A brief welcome introduces Mapperly the first time you launch it.
- New update windows highlight changes once per version, shared across your characters.
- Both windows match your selected theme and wait until you are out of combat.
