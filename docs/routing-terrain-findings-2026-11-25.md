# Routing terrain findings — 25 November 2026

## Outcome

The investigated failures do not justify changing the terrain masks. The three cases have different causes:

| Case | Evidence | Action supported by the evidence |
| --- | --- | --- |
| R42 Ratchet → Shimmering Flats | Six speculative searches across Dustwallow consume 1,572,864 expansions, then the successful roads-off plan uses the Great Lift instead. The Dustwallow endpoints are connected only when wet cells are permitted in the base mask. | Prioritize usable alternatives and share search work between nearby crossing anchors. Do not open terrain cells to shorten the swamp detour. |
| R08 Booty Bay → Darkshire | The Stranglethorn side of crossing 37 is stranded in a small ground component. A native Duskwood chasm bridge spans the separation, but its full floor/landing proof does not satisfy the existing standards. | Keep the missing bridge explicit and investigate its deck and landings. Do not certify it from a nearby road pixel or lower the geometry gates. |
| R09 Ashenvale east → Auberdine | The same local query succeeds with roads off at 243,149 expansions and exhausts 262,144 with firm road preference. Both endpoints are in the same component before and after terrain cleanup. | Improve the search for road-weighted costs; a terrain permission change would address the wrong cause. |

No runtime, mask, corridor proof, or manifest was changed by this investigation. The only delivered change is this report. Physical traversal on the live client remains unverified.

## Sources and method

The captured failures are in `output/route-matrix-2026-11-25/benchmark-results.json`; exact town points and source hashes are in `matrix.json`. Native sources are the read-only Forever build 70959 snapshot at `../output/forever-datamine-70959`. Terrain and road PNGs are at `../output/terrain-overlays-70959` and `../output/road-overlays-70959`.

Checks used the actual Lua 5.1 terrain search through `.test-deps/lupa`, `tools/bridge_geometry.py`, and native MCVT/MCNK/MH2O samples. Raw masks were reconstructed in memory from cached native root tiles using the generator's exact EXTENT crop and nearest-neighbor transform. Four-neighbor connectivity is sufficient: a safe diagonal requires both orthogonal neighbors and therefore cannot join separate four-neighbor components. BFS paths below are diagnostic cardinal paths, not recommended player routes or minimum-swimming paths.

Baseline `Terrain.lua` was obtained with `git show HEAD:Terrain.lua` and its SHA256 was checked against `matrix.json` before the paired Ashenvale experiment. This matters because other agents were concurrently changing the search. The expansion counter was instrumented only in the in-memory Lua source; no timing comparisons were made against concurrent work.

## R42: costly speculative Dustwallow branches

The tested start is `(1413, 0.624, 0.378)` and goal `(1441, 0.78, 0.75)`. Both are dry permitted terrain, walking region 1, and off-road at their exact cells.

The three Barrens → Dustwallow crossings have road-supported Dustwallow entries:

| Crossing | Dustwallow point `(x, y)` | Cell `(column, row)` |
| --- | --- | --- |
| 13 | `(0.29007937319274385, 0.4708333832142901)` | `(365, 395)` |
| 14 | `(0.29484127790022635, 0.4744048120918411)` | `(371, 398)` |
| 12 | `(0.29880953182312914, 0.48035719355442585)` | `(376, 403)` |

The investigated exits toward Thousand Needles are dry but off-road:

| Crossing | Dustwallow point `(x, y)` | Cell |
| --- | --- | --- |
| 90 | `(0.4242063557868481, 0.9136905640306199)` | `(534, 767)` |
| 91 | `(0.44246032383219963, 0.9136905640306199)` | `(557, 767)` |
| 92 | `(0.6797619084217686, 0.7136905468877612)` | `(857, 599)` |

All six points are in runtime region 1. The four sampled native entry/exit cell centers are dry, have no terrain holes, and have slopes of approximately 5.06–22.99°. The source ADTs are 785805, 786260, and 786695. Thus none of these anchors is simply a prohibited or unknown cell.

The first entry and all three exits belong to the same four-neighbor component in both raw native-derived terrain (723,931 cells) and the cleaned shipped mask (724,666 cells). Cleanup did not disconnect them. In contrast, an exhaustive dry-only BFS from `(365,395)` visits 177,446 cells and reaches none of the three exits. This is a base-ground-mask result; independently certified structure floors can provide additional links.

With wet cells allowed, example shortest-cardinal paths from that entry are:

| Exit cell | Cardinal steps | Wet cells on the example path | Bounds reached by the path |
| --- | --- | --- | --- |
| `(557,767)` | 1,254 | 304 | columns 365–857, rows 395–800 |
| `(534,767)` | 1,277 | 304 | columns 365–857, rows 395–800 |
| `(857,599)` | 716 | 304 | columns 365–857, rows 395–599 |

The southern anchors are physically close in map coordinates but the permitted base-mask path bends far east. A connected-region test correctly permits the search; it cannot establish that a cheap local connection exists.

An exact roads-off Lua reproduction of entry 13 → exit 91 with `maxExpansions=262144` returns `nil, 'budget'` after 262,144 expansions. The captured roads-off cold R42 trace contains all six combinations of the three western entries and two southern exits, each consuming 262,144 cells. Those six searches account for 1,572,864 of 1,978,624 total cells, approximately 79.5%. The cold baseline reports 18.8862 host seconds, and the immediate warm repeat still spends 1,572,864 cells.

The successful plan uses the Great Lift, visits `[1413,1441]`, and measures 7,006.52 yards. It does not route through Dustwallow. Its status is `ok` with partial coverage because of the lift. The walking graph's nominal minimum chain `[1413,1445,1441]` consequently describes neither the selected journey nor the actual difficulty of its local legs.

With normal or firm road preference, Barrens entry searches additionally cost hundreds of thousands of cells. The complete journey then reaches 1,999,872 reported cells, after which later queries often return budget with zero additional expansions. Those zero-cell trace entries are not evidence of additional bad masks; the journey allowance is already exhausted.

## R08: a stranded handoff and an unresolved native bridge

Booty Bay is `(1434,0.272,0.769)`, cell `(416,785)`, walking region 1. It is permitted only when swimming is allowed and has no road support at that cell. Native ADT 777882 reports terrain height approximately −14.1524 yards and liquid at height 0. This point is a wet benchmark anchor; it is not a certified town floor. Darkshire `(1431,0.77,0.44)` is dry, region 1.

Crossing 37 connects Duskwood `(0.4483024733939184,0.8530096296296303)` to Stranglethorn `(0.4071172128903858,0.031341826654938704)`. The Stranglethorn side is cell `(623,32)`, region 21, dry and off-road. Region 21 has a bounding box of columns 612–737, rows 0–41. It contains 1,687 raw cells and 1,692 cleaned cells; Booty Bay remains in the separate large component. This disconnection exists before cleanup.

The existing local approach audit for crossing 37 succeeds within the stranded region. Its Stranglethorn approach is `(0.4179757385883371,0.024595202891930564)`, approximately 81.63 yards from the handoff. That local proof does not establish a route to the rest of Stranglethorn.

The nearest cardinal separation from region 21 to region 1 includes column 638, rows 27–34. Native samples in the blocked cells report steep slopes, including 66.22°, 67.96°, 80.44°, and 59.61°. ADT 778052 has no liquid or terrain holes at those sampled cells. Opening them as ordinary ground would admit a steep gorge; the native height source supports their restriction.

The relevant placed object is `0:m2:44103`, asset `DuskwoodChasmBridge`, model FileDataID **189411**, native UID **44103**. Its native placement is:

```text
position = [17442.794921875, 55.681732177734375, 28391.67578125]
rotation = [0, 288.5, 0]
scale = 1024; flags = 64
world center north ≈ -11325.009114583332
world center east  ≈ -376.1282552083321
```

The native collision model has 219 faces and a longitudinal span of 38.3342075348 yards. Its floor sits about 19.26 yards above the gorge at the sampled midspan. The central axis ends over region 21 and region 1 respectively:

| Side | Map point | Native deck minus terrain |
| --- | --- | --- |
| North | `(1434,0.40600248291600355,0.03246003151449403)` | approximately +0.370 yards |
| South | `(1434,0.4079086334243864,0.04100535762749127)` | approximately +0.399 yards |

Both exceed the existing 0.3-yard landing-contact gate. The inventory already records this bridge as unresolved with `No independently dry contacts on opposite ends`.

The standard extractor tries lateral offsets 0, ±1, and ±2 yards. Additional in-memory probes found contacts within the existing landing threshold five yards off center: north `(1434,0.406745537713205,0.0320870974818246)`, delta +0.1715, and south `(1434,0.40865168822158787,0.04063242359482185)`, delta +0.2902. These individual contacts are insufficient. Running the existing full extractor in memory, changing only its candidate offset, gives:

| Offset | Full validation result |
| --- | --- |
| +5 / +5.5 yards | `Winding floor lacks one-yard central strip` |
| +6 yards | `Centerline floor/clearance gap` |
| +6.5 yards | `No supported central strip at least one yard wide` |

No bridge fix was admitted. A follow-up should inspect the actual deck width and the bank-to-deck transition in the native collision mesh, retaining the existing headroom, interval, step, and width standards. The evidence identifies the missing native connection but does not certify a complete traversable corridor. Merely expanding the offset list is not a sufficient fix.

The baseline R08 fails with roads off and firm at 1,999,872 reported journey cells. Recorded flights allow it to succeed. A replacement Booty Bay benchmark anchor should be selected from independently supported dry town ground before using this case to evaluate dry walking; moving the anchor alone does not reconnect the northern bridge.

### Follow-up on 25 November 2026

The two banks meet different sides of the collision deck. Sampling them independently identified a continuous 39.17-yard lane on model 189411, placement 44103. From the northern bank, the lane begins three yards to one side of the model axis and ends five yards to the other side at the southern bank. The first and last quarter-yard run parallel to the axis. This keeps the entire one-yard lane on the deck at each landing and clear of the central bridge rails.

The native re-probe verified 167 centerline positions, 835 lateral samples, zero unsupported centerline interval, and at least 5.46 yards of centerline headroom. Across five positions on each landing, the largest deck-to-dry-ground height difference was 0.29849 yard. Corridor 479338901316938 now joins region 21 to region 1 between Stranglethorn (40.56, 3.27) and (40.87, 4.06). The existing terrain mask and floor thresholds apply. The original Booty Bay benchmark begins in water, and live-client traversal remains unverified. Reproduction commands and source details are in [the native structure notes](../Data/Structures-SOURCES.md).

## R09: search pressure from road costs

The start is `(1440,0.852,0.446)`, cell `(1179,411)`: dry, region 1, off-road. The Ashenvale endpoints of the two Darkshore handoffs are:

| Crossing | Ashenvale point | Cell | Road support |
| --- | --- | --- | --- |
| 42 | `(0.291546238915433,0.14742543472976746)` | `(403,136)` | yes |
| 43 | `(0.20628611936583233,0.1604335651494912)` | `(285,148)` | yes |

These three cells belong to the same raw component (504,575 cells) and cleaned component (505,935 cells). Native samples at their centers are dry, without holes, and have slopes of approximately 13.08°, 4.23°, and 11.58°. Their source ADTs are 786185 and 784600. None requires a terrain correction to become permitted.

The paired actual Lua search uses the exact same endpoints, same baseline terrain source, and same 262,144-expansion allowance. The sole policy difference is `preferRoads=true, roadPreferenceStrength=4`:

| Query: start → crossing 42 | Result | Expansions | Returned distance |
| --- | --- | --- | --- |
| Roads off | success, 38 points | 243,149 | 4,972.5562 yards |
| Firm | `budget` | 262,144 | none |

Firm applies a 1.75 factor to off-road edge costs. The baseline heuristic remains an admissible geometric grid distance, so road costs can broaden the searched area considerably. This is A* with road-weighted edge costs, not a demonstrated loss of terrain connectivity.

The captured full R09 roads-off plan succeeds with 910,080 total cells, visits `[1440,1439]`, and measures 7,293.93 yards. Its cold host time is 7.9876 seconds; warm time is 0.0396 seconds. Firm fails at 1,999,872 cells, including repeated 262,144-cell attempts between multiple Ashenvale starts and the same western handoffs. Those repeated attempts amplify the difficult local query.

## Reproduction and source fingerprints

The exact local calls used the existing harness to load actual data and Lua modules. For the initial Dustwallow repro, `A.Terrain.Path(a,b,{maxExpansions=262144,yield=counter})` returned `nil,'budget'` with the counter at 262144. For the paired Ashenvale check, the in-memory baseline source was instrumented at `work=work+1;closed[id]=true` to record the final exact expansion count. `git show HEAD:Terrain.lua` matched the matrix hash before that instrumentation. No on-disk source was instrumented.

Selected verified native blob SHA256s:

| FileDataID | Role | SHA256 |
| --- | --- | --- |
| 775971 | Azeroth WDT | `160452dec4c2b0ae4cbe7468ce52fee91ac7ec521d2cb0f28e955def0d087137` |
| 782779 | Kalimdor WDT | `1120509b2ac42a94310bf05f915b5e67ed233be854089a3545829e064b614b44` |
| 778052 | Stranglethorn gorge ADT | `d682069e6153f3460e459e07f1f1f70e07eaf4778c5b8cfe0de0c76612638dc5` |
| 189411 | Duskwood chasm bridge collision model | `312e2ce6f8ee6791aeee896ecf9c7900af2ca77e4ea907ce109d0a15a087dff8` |
| 777882 | Booty Bay anchor ADT | `c6f558de02759087344b64c89f7cd69255221c9ce4e6bb5a412e8d973db85f18` |
| 785805 | Dustwallow western entry ADT | `445b034bdda091e9ea628db5d67745a311eed2e079f25b305dc1999f8a5bf9b4` |
| 786260 | Dustwallow southern exits ADT | `b445e5ea0d41e608478535fbbd09e75ec02bb7e8957a8a4564e44848d8d4fa67` |
| 786695 | Dustwallow eastern exit ADT | `04b07a33834520c925e1feea734465072c27f22e7d00c5c8d5a1fb0d89a9cf75` |
| 786185 | Ashenvale eastern start ADT | `c0aeb8ce20c466746bf65ffdfbd651b0e18e021c6ca80072090e9c7c8a0b4b76` |
| 784600 | Ashenvale western handoff ADT | `7f58b6570b75f66a1726f9c66bbd93d7fc8dcc564270cd3b7fbc33ec53b61a08` |

The terrain generator intentionally uses a conservative whole-cell fan slope threshold. This report does not convert a single low-slope triangle, visual road, dry endpoint, or locally reachable approach into permission for the whole cell or a complete bridge corridor.
