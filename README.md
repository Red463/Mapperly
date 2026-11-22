# Mapperly

![Mapperly logo](Media/Logo.png)

A cleaner world map for **WoW Forever**. Compact and enlarged views, painted location markers, custom notes and coordinate navigation, styled to fit the original game.

**Version: 1.1.1** | **Interface: 16001**

[Download the latest release](https://github.com/Red463/Mapperly/releases/latest) | [Report an issue](https://github.com/Red463/Mapperly/issues)

## Installation

1. Download **Mapperly-1.1.1.zip** from the release page.
2. Extract the `Mapperly` folder into your WoW Forever `Interface/AddOns` directory.
3. Restart the game or run `/reload` when updating an existing installation.
4. Open the world map with **M**.

Use the release ZIP for installation. GitHub's automatic source archives include development files and use a different outer folder name. Existing Mapperly preferences and notes are preserved when updating.

## Features

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
| Navigate | Open Coordinates, Saved and Recent destinations. Alt-right-click the map or a marker for a quick waypoint. |
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

The guide provides a **straight-line bearing**, not a terrain or transport route. It works across adjacent zones in the same world instance and waits when position/facing is unavailable or the destination requires another continent/instance. The arrow position is remembered; the active arrow target clears on reload, while Saved and Recent destinations remain available. Gatherly is not required and its navigation is not changed.

### Commands

- `/mapperly` opens the map or its filter menu.
- `/mapperly help` lists commands.
- `/way 10.23 52.65` starts navigation when no other addon owns `/way`. Add an optional name after the coordinates.
- `/mapperly way 10.23 52.65` always starts Mapperly navigation, including when another addon handles `/way`.
- `/mapperly note 1431 25 50 Meeting point` adds a permanent custom note.
- `/mapperly pin portal 1453 50 50 Destination name` adds a manually verified location.
- `/mapperly debug` prints build/map/pin diagnostics for bug reports.

Waypoint commands use the viewed map while it is open, otherwise your character's current zone. Coordinates are percentages from 0 to 100. Invalid input leaves the current destination unchanged. Mapperly respects existing and late-loaded `/way` handlers; it does not run a second navigation arrow alongside them.

## Coverage and compatibility

Mapperly includes **47 inn locations and 109 mailboxes** from a pinned public Forever server-database snapshot. It does not read Questie/QuestieDB. Interacting with services records additional discoveries; nearby duplicates are merged. The snapshot can have gaps or stale records. See [service data provenance](Data/Services-SOURCES.md).

Dungeon, flight and transport metadata is bundled from OpenMap. Recommended zone levels use valid client data first, then a cited recommendation table. They are guidance ranges, not quest or entry restrictions. Some zones have no client map links. Reveal metadata may not cover every area.

**Portals are manual locations only:** no verified portal-location dataset is bundled. Enabling the layer does not create portal pins automatically.

The map keeps native pin providers so Questie, Gatherly, RareScanner and other map addons can continue drawing their own markers. Mapperly filters affect its own pins. Other addons that resize or replace the map can conflict. Compatibility depends on the addon mix; please include it with bug reports.

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
python tests/services_builder.py
python tools/package.py
```

The package script reads the version from `Mapperly.toc` and writes an installable ZIP to `dist/`. It excludes Git metadata, dependencies, test files, generated-source artwork and database downloads. Source art and image-generation prompts are in `assets/`; large service-database downloads are cached locally and ignored by Git.

The tests use a bundled native-frame double and Lua 5.1 runtime. They cover syntax, saved preferences, map fitting, pin visibility and interactions, settings, opacity, navigation geometry/state and texture encoding. They do not replace in-game rendering and compatibility checks.

## License and credits

**Mapperly's original code and artwork are MIT licensed.** See [LICENSE](LICENSE).

Bundled third-party components retain their own licenses, including BSD-licensed HereBeDragons, MIT OpenMap metadata and GPL-2.0 service-location data. These components are not relicensed under MIT. See [NOTICE.md](NOTICE.md), [Data/SOURCES.md](Data/SOURCES.md) and the license files in `Libs/`.

[Changelog](CHANGELOG.md)
