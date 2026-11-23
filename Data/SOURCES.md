Places.lua and FlightData.lua: OpenMap (MIT), https://github.com/openmap-world/openmap/tree/273f9b672a7bfab568ebf161d07ee2380761c3a3/OpenMap/Data/Forever
Transports.lua: native Forever build 70959 directed passenger stops, approach proofs and explicit planning assumptions; see Transports-SOURCES.md.
Reveal.lua: see its pinned source header and Libs/OpenMap-Reveal-LICENSE.txt.
Services.lua: bundled standalone Forever service data; see Services-SOURCES.md and Libs/Forever-Services-COPYING.txt.
ZoneLevels.lua: pinned OpenMap recommended zone ranges with cited Warcraft Wiki provenance; see ZoneLevels-SOURCES.md.
# Flight journeys

Native build 70959 geometry and character-specific offered-route observation: see [Flights-SOURCES.md](Flights-SOURCES.md). Native geometry does not unlock undiscovered flights.

Native WMO street/dock preferences and private Stormwind harbour access: see [RoadsSupplement-SOURCES.md](RoadsSupplement-SOURCES.md) and [HarbourAccess-SOURCES.md](HarbourAccess-SOURCES.md). Supplements preserve original terrain permissions and are bound to their exact base data/proof hashes.

Active quest locations: native current quest pins and travel waypoints, supplemented by the independently bundled Forever SQL snapshot. See [QuestLocations-SOURCES.md](QuestLocations-SOURCES.md), `tools/build_quest_locations.py` and the GPL-2.0 notice in `NOTICE.md`. Quest names and acceptance/progress state come from the player's live log.

Unaccepted quest catalogue: English titles, snapshot requirements and verified starter spawns are bundled separately in `QuestCatalog.lua`. See [QuestCatalog-SOURCES.md](QuestCatalog-SOURCES.md). Runtime checks use this character's current log/completion/level/race/class state; unsupported conditions remain unconfirmed.



## Precomputed walking connections

See [WalkingPaths-SOURCES.md](WalkingPaths-SOURCES.md). The included offline builder uses the same bundled terrain/ground/road data and unchanged Lua terrain search; the source manifest fingerprints all inputs and generated output. Prepared paths accelerate exact walking sections without adding crossings or character travel unlocks.

## Liquid coverage and native local transports

See [Water-SOURCES.md](Water-SOURCES.md) for native liquid classifications, missing-cell handling, input hashes and builder provenance. Water masks add a dry-first preference without making roads evidence of bridges. Native tram portal pairing is audited in `tools/data/native-tram-portals-70959.json`; it does not certify platform or city-floor access. Native Subway spawns and exact city exit floors now support the fixed Deeprun connection without player recordings; see [Trams-SOURCES.md](Trams-SOURCES.md).
