# Map visibility and marker layers

Requested behavior: dungeons enabled on every map scale by default, other categories restricted to zone maps by default, configurable continent visibility, and Mapperly zone markers above resource nodes.

Store.lua persists continentFilters independently from the existing category filters. Only missing or invalid values get defaults: dungeon true, all other categories false. A disabled main filter still hides a category everywhere. Settings ? Location layers displays the main Show checkbox and an On continents checkbox for each category. Show all / Hide all change the main filters and preserve continent preferences.

Pins.lua classifies overview maps using C_Map.GetMapInfo().mapType (Cosmic, World, Continent); zone, dungeon and micro maps use the zone behavior. Unknown map metadata retains normal zone rendering. Visibility is applied only to Mapperly's own pin template, leaving third-party providers untouched.

Zone markers use PIN_FRAME_LEVEL_GOSSIP, immediately above AREA_POI used by HereBeDragons/Gatherly resource nodes. Native quest and player/group layers remain above it. Overview markers retain AREA_POI. OnAcquired selects the tier on each acquisition so reused pins do not retain an old tier. No other addon's pin levels or strata are modified. Addons explicitly using higher custom tiers may still appear above Mapperly.

Native definitions inspected 2026-11-21:
https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_WorldMap/Blizzard_WorldMap.lua
https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_MapCanvas/MapCanvas_DataProviderBase.lua

Buttons.lua draws four explicit pixel-snapped BORDER-layer edges within the control bounds, instead of relying entirely on the thin BACKGROUND-layer rim. This reinforces the zone heading's right border when resizing at fractional UI scales.

Regression checks cover defaults, migration, saved choices, immediate settings updates, continent/world versus zone rendering, main-filter precedence, layer selection/reuse and the explicit right border. Real-client appearance and interaction with the installed addon mix still need in-game verification.
