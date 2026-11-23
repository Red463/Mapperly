# Mapperly

![Mapperly logo](Media/Logo.png)

A cleaner world map for **WoW Forever**. Compact and enlarged views, painted location markers, custom notes and coordinate navigation, styled to fit the original game.

**Version: 1.2.4** | **Interface: 16001**

[Download the latest release](https://github.com/Red463/Mapperly/releases/latest) | [Report an issue](https://github.com/Red463/Mapperly/issues)

Version 1.2.0 adds smart journey navigation, quest and service search, road/swimming preferences, supported travel methods, route recovery and copyable diagnostics. See the [release notes](docs/release-1.2.0.md) and [in-game test guide](docs/testing-1.2.0.md) for features and coverage limits.

Version 1.2.4 adds updated branding, combat map controls, an EnhanceQoL mover warning and map-diagnostic fixes. See the [latest release notes](docs/release-1.2.4.md).

## Installation

1. Download **Mapperly-1.2.4.zip** from the release page.
2. Extract the `Mapperly` folder into your WoW Forever `Interface/AddOns` directory.
3. Restart the game or run `/reload` when updating an existing installation.
4. Open the world map with **M**.

Use the release ZIP for installation. GitHub's automatic source archives include development files and use a different outer folder name. Existing Mapperly preferences and notes are preserved when updating.

## Smart journey navigation

Mapperly **1.2.0** adds terrain-estimated walking routes within and between supported zones, using bundled Gatherly terrain data without requiring Gatherly. It includes background planning, a map route, distance/time preview, bend-following guidance and Pause/Resume/Skip/Replan controls. Settings now has a **Navigation** tab with **Smart routing** enabled by default and separate world-map/minimap route toggles. Turning Smart routing off immediately converts the current destination to straight-line guidance. Both modes draw their route on the map and minimap; minimap lines follow movement, zoom and rotation.

Open Destinations from the arrow toolbar button, enter coordinates and choose **Preview route** or **Start**. **Active journey** opens the guidance controls. Alt-right-click and `/way` use the chosen route mode. Previews follow the chosen routing mode; changing modes closes a stale preview. A planning panel appears above the map immediately for manual requests, including Alt-right-click. It shows the current stage, elapsed time and search activity. It also shows the number of eligible recorded flight offers and explains when none are available. Cancel stops that calculation while keeping your existing navigation; failures remain readable until dismissed.

Mapperly ships validated walking connections between fixed travel points in 48 zones and retains a bounded session cache across zone changes. Prepared paths match the chosen road mode and current terrain data; arbitrary player/destination approaches and missing pairs still use live terrain searches. Flight unlocks, faction and fares remain character-specific runtime checks.

The journey preview lists walking and supported transport legs. Boats, zeppelins, airships, the verified Great Lift, bundled Deeprun Tram and this character's recorded flight offerings can form part of a journey. Boarding and choosing a flight remain manual. The tram needs no player trip recording: walk through the source city portal, ride and exit the destination portal, then continue walking. City access uses normal walking paths where available and a labeled portal bearing across indoor mask gaps. Ironforge also uses labeled city-direction guidance for normal destinations when indoor terrain data cannot provide a path.

Open **Destinations > Quests** to search your active quest log by name or ID. Choose **Locations**, then **Preview** or **Go** beside a known objective, turn-in or travel waypoint. **Game** identifies live native quest data; **Snapshot** identifies the bundled Forever database, which may be incomplete or outdated. Some completed sub-objectives cannot be identified individually and are labeled accordingly. Quests without verified locations explain why no destination is offered. Searching does not change quest selection, map view or current navigation. Questie is not required.

Open **Destinations > Services**, choose Inn, Mailbox, Flight master or Dungeon entrance, then **Find nearest**. Mapperly compares verified walking routes under your road settings, including nearby zones. Preview or Go recalculates from your current position. Smart routing must be enabled. Searches exclude vehicles and keep current navigation unchanged. **Best found so far** means search limits prevent confirming the nearest; a labeled approach leaves final building/platform access manual. Hidden marker layers are still searched.

You can also right-click a quest in the native log and choose **Navigate to**. One known location routes directly; several locations appear in a submenu. With no verified location, the action is disabled and its tooltip explains why.

If an exact quest point is blocked, smart routing can stop at permitted ground within 30 yards. The route is labeled **approach**, with final access left to you. The list retains the exact quest coordinates; direct guidance uses those exact coordinates. Without a bounded walkable approach, the existing route is preserved.

Choose **Find quests** in that tab to search quests you have not accepted by English name or ID. Results distinguish **Possible pickup**, **Unavailable**, and **Availability unconfirmed**, using known snapshot requirements and this character's live status. Choose **Locations** to see recorded starters. Known restrictions disable pickup routing; unconfirmed results can navigate to a recorded starter with a clear reminder to check requirements in-game. The catalogue includes unused or inaccessible snapshot content, and many quests have no verified starter. It does not guarantee live availability or infer item drops. Already active quests remain in **Active**.

Planning into unknown/blocked terrain fails explicitly and preserves the previous destination. Once following a route, stepping into a restricted player cell keeps the arrow, route and current waypoint active. Swimming is allowed by default. Enable **Avoid swimming if possible** in Navigation > Routing to try a dry itinerary first and retry with swimming permitted if none is found. Unknown liquid coverage and unmodeled bridges may require that retry. These masks do not guarantee collision-free travel through buildings, bridges, caves or fences. Coverage and remaining live checks are on the [implementation checklist](docs/navigation-checklist.md).

The walking navigation arrow points toward the next route turn. Its primary distance is to that turn; total route distance is shown separately underneath. Rejoining safely farther along advances guidance after sustained proximity. A sustained detour triggers a throttled background replan, keeping your destination and previous route until a replacement succeeds. Pausing or switching to direct guidance disables this recovery.

Enable **Settings > Navigation > Prefer roads where possible** to favor known roads during smart routing. Adjust **Strength** from Light to Strong to choose how readily routing accepts a longer road detour. Balanced retains the original preference. Both choices are saved; changing them replans your current smart destination. Strength is a preference, not a roads-only restriction or a guaranteed maximum detour. Missing road data uses normal terrain routing. Native road textures are hints: small dirt paths may be missing, and town paving may count as road.

Road hints also include native Stormwind street paving and verified static dock floors at seven covered zone maps. Stormwind's boat handoff follows a certified pier corridor; its middle-harbour ground link still takes a detour. Other dock hints are preferences rather than full harbour access guarantees. See [road supplement coverage](Data/RoadsSupplement-SOURCES.md) and [harbour access limits](Data/HarbourAccess-SOURCES.md).

Cross-zone walking currently uses **121 links across 68 zone pairs**, including dry native boundaries without road textures and native-floor-supported Dun Morogh gate, Talondeep, Blackrock and all three Timbermaw branch passages. Ironforge's main entrance and Undercity's static sewer connect to proven interior floor anchors. Exact ground-region labels avoid wasting search work on disconnected terrain islands. Duskwood to Dun Morogh and Bloodvenom Post/Astranaar to Everlook have automated full-route regressions. Whole-city indoor corridors, unsupported transport transitions and unknown custom areas remain outside complete coverage; see the [walking coverage audit](docs/walking-coverage.md). Live testing is still required.

## Features

- **Welcome and update notes:** a brief introduction on first launch and concise changes after updates, shown once across your characters.

- **Two remembered map sizes:** a substantial compact view and an enlarged view with game space around the edges. Drag the title bar in either view to move it; each view remembers its own position. Use Lock to keep it in place. Theme and settings changes preserve placement, and screen bounds include the crest and frame trim.
- **Location markers:** inns, mailboxes, dungeon entrances with level ranges, flight masters, boats/zeppelins, zone exits where supported, and custom notes.
- **Simple layer controls:** toggle individual categories in Filters. In Settings, choose which also appear on continent/world maps. Dungeons are enabled there by default; the other layers default to zone maps.
- **Switchable themes:** the Default theme uses warm Classic panels, native window trim and red primary actions. Choose **Minimal Charcoal** in **Settings > Appearance theme** for the previous charcoal look. The choice is remembered and applies immediately to open windows without losing drafts; Gatherly is not required.
- **Dedicated settings window:** grouped display, sizing and opacity controls; matching icons beside location names; a live marker-size preview.
- **Optional quest pane:** the quest icon opens or closes the native quest list and remembers your choice.
- **Useful map details:** player/cursor coordinates, recommended zone levels when reliable data is available, optional unexplored-area reveal and a repeatable player-location ping.
- **Navigation and destinations:** enter coordinates or Alt-right-click a map location/marker for an immediate waypoint. Follow a movable direction/distance arrow; save named favourites and revisit the latest 20 unique destinations.
- **Custom notes:** choose from twelve purpose-made symbols (enemy, chest/loot, POI, scenic spot, building, danger, camp, meeting point, resources, fishing, cave and travel); edit names, descriptions, groups and painted icons in a window matching Settings. Browse and search notes across all zones.

## Map controls

Use the standard Blizzard close button at the top right of the header to close the map. Hover any icon in the right-hand toolbar for its description. From top to bottom:

| Control | Action |
| --- | --- |
| Resize arrows | Switch compact/enlarged view. Arrows indicate the next action. |
| Parent map | Zoom out to the parent zone, continent or world map. |
| My location | Return to your current zone and ping the player arrow. |
| Navigate | Open Coordinates, Saved, Recent, Quests and Services destinations. Alt-right-click the map or a marker for a quick waypoint. |
| Add note | Open the note editor at your character. Alt-click the map to place one elsewhere. The My notes tab browses existing notes. |
| Filters | Toggle Mapperly location categories. |
| Quest symbol | Show or hide the quest log. |
| Reveal | Show unexplored map artwork. This does not grant exploration credit. |
| Lock | Lock or unlock the map position. |
| Settings | Open Mapperly's options window. |

Click a custom note to edit its name, description, group or icon. Notes stay in the Custom notes layer regardless of their chosen icon. The My notes tab searches names, groups, descriptions and zones. Right-click a custom note to remove it. Shift-click inserts its name and coordinates into an active chat edit box; nothing is sent automatically.

### Navigation

**Alt-right-click** any map position or marker to start navigation immediately. Mapperly and standard native pins use the exact marker position; raw addon buttons inside native/HBD wrappers are also supported. Markers that entirely bypass these map systems may need an Alt-right-click beside the icon. Ordinary marker clicks and Alt-click note placement keep their existing actions. Dragging does not place a waypoint.

Use **Save** in Coordinates to keep a named favourite without starting navigation. **Saved** offers Edit, Go and Remove; **Recent** keeps the last 20 unique successful destinations and offers Edit, Go, Save and Clear history. Saved and recent records survive reloads. Visiting the same point moves it to the top of history.

Open the destination map, click Navigate, enter X and Y from **0 to 100** (decimals supported), then press **Start**. Close the map to follow the arrow. Drag the arrow to move it, left-click it to edit, or right-click it to stop. Right-clicking the destination pin or using Stop in the entry window also cancels navigation. Arrival within ten yards clears the destination.

With **Smart routing** enabled, the guide follows the planned walking and supported transport legs. Turn it off for a straight-line bearing. If position/facing is unavailable, guidance waits. The arrow position is remembered; validated destinations can be resumed after reload through the resume offer. Saved and Recent destinations remain available. Gatherly is not required and its navigation is not changed.

### Commands

- `/mapperly` opens the map or its filter menu.
- `/mapperly help` lists commands.
- `/way 10.23 52.65` starts navigation when no other addon owns `/way`. Add an optional name after the coordinates.
- `/mapperly way 10.23 52.65` always starts Mapperly navigation, including when another addon handles `/way`.
- `/mapperly note 1431 25 50 Meeting point` adds a permanent custom note.
- `/mapperly pin portal 1453 50 50 Destination name` adds a manually verified location.
- `/mapperly resume` opens the saved-journey resume offer.
- `/mapperly report` opens copyable route diagnostics.
- `/mapperly debug` prints build/map/pin diagnostics for bug reports.
- `/mapperly mapreport` opens a copyable map-position report. To capture a reset, use `/mapperly mapreport start`, reproduce it, then `/mapperly mapreport`. Capture is opt-in and lasts only for this session; `/mapperly mapreport stop` stops it without opening the report.

Waypoint commands use the viewed map while it is open, otherwise your character's current zone. Coordinates are percentages from 0 to 100. Invalid input leaves the current destination unchanged. Mapperly respects existing and late-loaded `/way` handlers; it does not run a second navigation arrow alongside them.

## Coverage and compatibility

Mapperly includes **47 inn locations and 109 mailboxes** from a pinned public Forever server-database snapshot. It does not read Questie/QuestieDB. Interacting with services records additional discoveries; nearby duplicates are merged. The snapshot can have gaps or stale records. See [service data provenance](Data/Services-SOURCES.md).

Dungeon, flight and transport metadata is bundled from OpenMap. Recommended zone levels use valid client data first, then a cited recommendation table. They are guidance ranges, not quest or entry restrictions. Some zones have no client map links. Reveal metadata may not cover every area.

**Portals are manual locations only:** no verified portal-location dataset is bundled. Enabling the layer does not create portal pins automatically.

The map keeps native pin providers so Questie, Gatherly, RareScanner and other map addons can continue drawing their own markers. Mapperly filters affect its own pins. Other addons that resize or replace the map can conflict. Compatibility depends on the addon mix; please include it with bug reports.

Mapperly warns if EnhanceQoL's mover is enabled for World Map. To prevent position resets, open `/eqol` > Interface > Mover > World, untick **World Map**, then `/reload`. Other mover features can remain enabled. Mapperly reads the active configuration without changing it; the warning appears once per session on map open and waits during combat or other dialogs.

Scheduled journeys now include **25 directed boat, zeppelin and airship links across 12 services**, with faction-appropriate choices in Navigation settings. Follow the walking route to the land approach, board manually and follow the travel/disembarking instructions. Through sailings keep you aboard at intermediate stops. Travel choices changed aboard take effect after landing. Blue map/minimap lines show native sailing pieces; total times include planning assumptions, not live timetables. See [transport sources and limits](Data/Transports-SOURCES.md).

**Interactive travel connections:** enable the desired transport/flight layers and their **On continents** options in Location layers. On world/continent maps, hover a marker to highlight available outgoing connections; click it to choose a destination, then **Preview** or **Navigate**. The chooser uses current method preferences, faction policy, this character's recorded flights and known fare affordability. It plans to the chosen destination using enabled travel methods; it does not force the clicked boat or flight. Boarding remains manual. **Navigation â†’ Overview transport links** controls faint background connections independently of hover previews. World-overview lines are schematic; continent views retain native geometry when available. Rendering is capped to keep busy maps manageable.

**The Great Lift** connects the Barrens and Thousand Needles in either direction, with its own default-on Lifts setting. Access and boarding are manual; navigation checks the destination floor or checked clear exit ground before resuming walking. Clear exit areas also support clients that return no usable altitude. Its 120-second planning allowance is an estimate. The bundled Deeprun Tram supports both city directions through its separate Trams setting; other capital lifts are not included. See [local transport coverage](Data/LocalTransports-SOURCES.md).

**Discovered flights** are enabled in Navigation settings. Open flight masters to record this character's offered routes and quoted fares; only those directed itineraries can be planned. Select flights manually in the normal flight window. The navigation arrow waits while flying, resumes on a verified landing and can update after an early landing. Journey previews show historical quoted/estimated fares and flight totals. Native geometry covers 65 masters/286 directed segments; Freewind Post currently supports proven boarding outward but has no verified arrival handoff. Platform/building access is manual. See [flight sources and limits](Data/Flights-SOURCES.md).

**On-screen route steps** show up to ten journey legs while playing, with completed steps muted and the current step highlighted. Longer journeys keep the current step inside the visible ten-step window. Drag the panel to move it; minus shows only the current step and plus restores the full list. Closing the panel keeps navigation running. Restore it with **Settings â†’ Navigation â†’ On-screen route steps**. Its position, visibility and collapsed state are saved, and it hides automatically when navigation ends. Completed route sections fade on both maps; sparse chevrons indicate the direction of remaining travel.

Boat legs include dashed port-to-port links across the ocean on the Azeroth overview. These are schematic travel connections, rather than exact sailing paths through loading transitions. Hover a visible boat marker on a world/continent overview to preview its outgoing service without changing navigation. Enable boat markers on overview maps through the location-layer settings; the existing visibility preference is preserved.

## Development

Python development dependencies are separate from the addon and are not needed in game.

```sh
python -m pip install -r requirements-dev.txt
python tests/run.py
python tests/navigation.py
python tests/themes.py
python tests/destinations.py
python tests/destination_ui.py
python tests/map_interactions.py
python tests/map_position.py
python tests/way_command.py
python tests/journey.py
python tests/journey_navigation.py
python tests/journey_ui.py
python tests/minimap_route.py
python tests/services_builder.py
python tools/package.py
```

The package script reads the version from `Mapperly.toc` and writes an installable ZIP to `dist/`. It excludes Git metadata, dependencies, test files, generated-source artwork and database downloads. Source art and image-generation prompts are in `assets/`; large service-database downloads are cached locally and ignored by Git.

The tests use a bundled native-frame double and Lua 5.1 runtime. They cover syntax, saved preferences, map fitting, pin visibility and interactions, settings, opacity, navigation geometry/state and texture encoding. They do not replace in-game rendering and compatibility checks.

## License and credits

**Mapperly's original code and artwork are MIT licensed.** See [LICENSE](LICENSE).

Bundled third-party components retain their own licenses, including BSD-licensed HereBeDragons, MIT OpenMap metadata and GPL-2.0 service-location data. These components are not relicensed under MIT. See [NOTICE.md](NOTICE.md), [Data/SOURCES.md](Data/SOURCES.md) and the license files in `Libs/`.

[Changelog](CHANGELOG.md)
