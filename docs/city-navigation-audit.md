# Capital city walking routes

The six routable capital city maps were tested using the production journey planner. The tests used three points per city, all six directions between them, with transport disabled. Each trip was planned twice, with road preference off and at Strong. Road coverage is the percentage of walking distance on the addon's road overlay, sampled every two yards. These are offline planner checks. They do not establish that a character can physically walk a generated line.

| Capital | Routes generated per setting | Road coverage, off | Road coverage, Strong | Bridge and passage findings from native build 70959 |
| --- | ---: | ---: | ---: | --- |
| Stormwind | 2/6 | 17% | 42% | The city model contains canal geometry and a gnome tunnel. Many district groups have abbreviated names. The harbour has separately validated access. Interior canal bridges still need connections from deck to street. Four trips involving 49.5, 44.6 failed the terrain endpoint check. |
| Ironforge | 6/6 | 0% | 0% | The entrance crossing has a validated floor in both directions. The model contains entrance halls, gnome tunnels and gryphon tunnels. Four trips used the two-point city fallback, including 33.2, 65.3 to 55.5, 47.8. The two terrain-routed trips also missed the marked roads. |
| Orgrimmar | 6/6 | 0% | 0% | The city model contains ten gateway groups and two warlock tunnel groups. None of the six journeys followed marked roads to a measurable extent. Passage connectivity remains unverified. |
| Thunder Bluff | 2/6 | 13% | 83% | Six mesa placements have named bridge geometry. The existing outdoor validator could not establish two ground landings for these elevated spans. A separate footbridge within the rectangular map bounds belongs to Mulgore. |
| Darnassus | 6/6 | 5–14% | 17–45% | Three bridge groups were identified by their own file headers (bridge31, bridge32 and bridge100). The outdoor validator could not establish both landings. |
| Undercity | 2/6 | 0% | 0% | The static sewer entrance has bidirectional routing coverage. The city model includes additional sewers, approaches and canals. Four trips failed the terrain endpoint check. |

City of Dalaran's native instance (2959) contains bridge, tunnel and sewer placements, but lacks a dedicated city map in the tested routing dataset. There was no placement inventory for the phased Stormwind instance (2940). Neither is included in the six-city success figures.

## What the geometry checks established

The bridge extractor previously skipped modern MPY2 collision records. Stormwind, Ironforge, Orgrimmar and Undercity all use this format throughout their main city models. It could also associate a bridge name with the wrong group file. For example, in Darnassus it selected 113387 for a temple section where the actual bridge group was 113385. The reader now uses each group's own header for its name and checks that the collision record count matches its triangle list.

The inventory checks candidate placements whose bounds intersect a city, then reads every base-detail group in those world models. A placement's bounds or name alone do not identify its playable floor or owning zone. Rerunning the corridor validator on ten unresolved placements identified the correct bridge geometry in Thunder Bluff and Darnassus, but admitted no new corridors.

## What needs to change in the addon

Road priority can only choose among routes the walking planner already considers walkable. Stormwind needs its streets linked across the actual canal decks and through district entrances. Ironforge needs connected indoor floors for its ring and passages. The next routing check is to trace continuous floors through those connections, retaining elevation where two floors share a map position, then rerun these same service trips in both directions. Elevated Thunder Bluff landings need the same floor-to-floor check.

## Reproduce

Run `python tools/audit_city_navigation.py --routes-only` from the addon repository for the 72 routes. Run without the switch to also inspect placements from the local build 70959 snapshot and the existing bridges-and-crossings inventory. The JSON output at `output/city-navigation-audit.json` includes coordinates, individual failures, fallback types and measured road fractions. The native inventory also includes placement IDs, group names and collision counts.
