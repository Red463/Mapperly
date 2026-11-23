Mapperly 1.2.0 brings smart journey navigation to WoW Forever, together with all updates and fixes developed since 1.1.1.

## Smart journey navigation

- Plan terrain-aware walking routes within and between supported zones. Smart routing is enabled by default; switch it off for straight-line guidance.
- Follow the route on the world map and minimap, with direction chevrons, faded completed sections, a bend-following navigation arrow and an on-screen steps window. Collapse the window to show only the current step.
- Prefer known roads with five strength levels, and optionally avoid swimming where possible while allowing it when a dry route cannot be found.
- Include eligible discovered flight paths, boats, zeppelins, airships, the Deeprun Tram and the Great Lift. Transport boarding and flight selection remain manual; no tram trip recording is needed.
- View and hover transport connections on continent/world maps, including ocean crossings, and inspect available destinations.
- See planning progress, cancel calculations, preview journey steps and use Pause, Resume, Skip or Replan. Detours and later route rejoins update guidance, while failed calculations preserve the previous route.

## Find destinations

- Search active quests for known objectives and turn-in locations, or search the bundled quest catalogue for recorded pickups. Availability and missing-data messages explain snapshot limitations. Questie is not required.
- Right-click supported native quest-log entries to choose Navigate to.
- Find nearby inns, mailboxes, flight masters and dungeon entrances by reachable walking route, with preview and navigation actions.
- Keep coordinate entry, quick Alt-right-click waypoints, saved destinations and recent history. Remember a destination across reloads and offer to resume it safely.

## Performance, appearance and fixes

- Ship validated precomputed travel-point walking paths and bounded session caches to reduce repeated searches. Prioritize promising flight/transport itineraries and avoid redundant terrain work.
- Refine Blizzard-style navigation windows, red action buttons, route labels, spacing and the collapsible steps panel; retain the Minimal Charcoal theme.
- Improve road and dock access, boat-to-walking handoffs, flight takeoff/landing transitions, both Great Lift exits, tram progression and Ironforge city guidance.
- Fix M failing to close the map with some character-specific native map preferences.
- Add a brief first-launch welcome and once-per-version update notices, shared across characters.
- Add copyable route reports with `/mapperly report`. For a map-position reset, run `/mapperly mapreport start`, reproduce it, then `/mapperly mapreport` and copy the report.

## Installation

Download **Mapperly-1.2.0.zip**, extract its `Mapperly` folder into `Interface/AddOns`, then restart or reload the game. Existing settings, notes and saved destinations are preserved. Use the attached addon ZIP rather than GitHub's automatic source archives.

## Coverage

Routes are estimates based on bundled data, not live collision detection. Some interiors, custom zones and transport approaches have incomplete coverage; labeled city bearings or nearby quest approaches may require manual final access. Flight availability depends on this character's observed flight-master offerings. Quest availability comes from a database snapshot and live checks where available. Strong road preferences and long multi-zone routes can still take longer to calculate.

The reported ultrawide map snap-back is still under investigation; this release includes opt-in diagnostics to capture it.

Validation: 102 automated test suites, plus release ZIP integrity and source checks. See [the release test guide](testing-1.2.0.md) for in-game checks.
