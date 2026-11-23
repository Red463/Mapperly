# Player-facing release highlights

Keep each release to at most four short, plain-language bullets (180 characters each). Packaging requires a section matching the TOC version and regenerates Data/ReleaseNotes.lua.

## 1.2.4

- New blue-and-gold Mapperly branding, with a clearer small icon and M badges for the map and addon windows.
- Move the unlocked map and close it with X or M during combat when the game permits the frame operations.
- Warn when EnhanceQoL's World Map mover is enabled, with the setting to disable. Other EnhanceQoL preferences are left unchanged.
- Fix map-report capture blocking dragging, and include more useful frame and mouse-input details in diagnostic reports.

## 1.2.3

- Move the unlocked world map and close it with X or M during combat when the game permits the frame operations.
- Keep native panel cleanup until after combat, without closing a map you have reopened. Resizing and protected-frame restrictions remain in place.

## 1.2.2

- Warn when EnhanceQoL's World Map mover is enabled, with instructions to prevent map-position conflicts. No EnhanceQoL settings are changed.
- Show the warning once per session when opening the map, deferring it during combat or other Mapperly dialogs.

## 1.2.1

- Fix map diagnostics preventing map dragging by keeping decorative trim transparent to mouse input.
- Map-position reports now identify the trim and include title-bar and trim mouse-input states. Reload after installing before capturing again.

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
