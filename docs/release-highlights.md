# Player-facing release highlights

Use short bullets of up to 180 characters. A release can use its consolidated CHANGELOG.md section as the source for the in-game window.

## 1.2.7

Source: CHANGELOG.md

## 1.2.6

Source: CHANGELOG.md

## 1.2.6-preview.12

- Change route colours, line width and direction markers for the world map and minimap in Navigation → Display → Route style. Preview changes or restore the default look.

## 1.2.6-preview.11

- Each world map panel now uses the Nearby Services width. Switch tools without resizing the map.
- Notes shows all twelve symbols together. Settings uses shorter pages, and long lists expand when you enlarge the map.

## 1.2.6-preview.10

- Fixed a Lua error when opening Destinations, Notes, Filters or Settings from the world map.

## 1.2.6-preview.9

- Open destinations, notes, filters and settings in the same right-hand space as quests and nearby services. Click the icon again to close its panel.
- Preview a route beside the map and choose Back to return to your destination.

## 1.2.6-preview.8

- Open the coin purse on the map and expand Gear repairs to see nearby repair NPCs by distance. Click a name to navigate.
- The separate Services tab has been removed from Destinations.

## 1.2.6-preview.7

- World-map walking routes now form a continuous teal line with rounded bends. The line and its direction arrows keep a consistent size as you zoom.
- The part you have already walked fades to a thinner slate line.

## 1.2.6-preview.6

- Open the coin purse to browse illustrated, collapsible lists of vendors, trainers and other nearby services.
- Find goods by item name or category, see who sells them and click to navigate to that merchant.

## 1.2.6-preview.5

- Open the coin purse beside the quest log button to find nearby vendors, trainers, innkeepers, flight masters and mailboxes.
- See distances from your character, filter by service and click a row to start navigation.

## 1.2.6-preview.4

- Follow a teal walking route on both maps. Travelled sections fade into slate dashes and transport legs appear as blue dots.
- Small ivory chevrons show the direction ahead, with a single cue on the minimap.

## 1.2.6-preview.3

- Follow the four Dun Algaz tunnels between Loch Modan and the Wetlands on journeys across the Eastern Kingdoms, including trips with boats and flights disabled.
- The arrow keeps pointing to the far tunnel exit when the zone changes underground.
- For long journeys, Mapperly checks which regions your enabled travel methods can reach before spending time on detailed walking paths.

## 1.2.6-preview.2

- If a route fails, choose Copy report in the error window to select the details for sharing in Mapperly's CurseForge comments.

## 1.2.6-preview.1

- Walk between Stranglethorn Vale and Duskwood via the northern chasm bridge, including journeys with boats and flights disabled.
- When a bridge is the only way across on foot, Mapperly considers it before sending you on a transport detour.

## 1.2.5

- Plan long journeys faster with bundled walking connections and earlier checks of complete routes involving lifts, boats and flights.
- Support 76 verified bridge placements, including Westfall-Duskwood, smaller-model and tilted bridges, with better nearby bridge routing.

- Hover a zone on a continent map to see readable minimum and recommended fishing skills beneath its quest levels in either theme.
- Check nearby approaches for all bundled crossings, testing alternatives and withholding unproven ground shortcuts. Keep boats, lifts and trams as transport steps.

## 1.2.4

- A clearer What's new window with a prominent version heading, inset highlights and a compact layout that fits its content.
- Defer Mapperly marker mouse-routing changes until combat ends to avoid blocked input calls while refreshing the map.
- Show minimum and recommended fishing skill beneath the zone heading, with source details and ranges for waters with different requirements.
- Optional travel connections now use clean curves, draw return trips once and default off. Enable them in Navigation > Routing > Show travel connections.

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
