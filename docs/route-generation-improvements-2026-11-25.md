# Mapperly route generation study

25 November 2026 · WoW Forever · Mapperly 1.2.5 development build

**Mapperly returned a usable route on 258 of 262 attempts, up from 218.** It recovered 40 failures and retained every previously successful case. All 42 distinct trips succeeded with normal transport options. Across the 218 attempts where both builds returned a usable route, total calculation time fell from 630.16 to 50.07 seconds.

## Generation time and reliability

| Measurement across all configurations | Previous planner | 1.2.5 |
| --- | ---: | ---: |
| First attempts returning a route | 106 / 131 | 129 / 131 |
| First attempt, median | 2.388 s | 0.279 s |
| First attempt, 95th percentile | 24.228 s | 2.138 s |
| First attempt, slowest | 28.480 s | 5.081 s |
| Immediate repeats returning a route | 112 / 131 | 129 / 131 |
| Immediate repeat, median | 0.038 s | 0.053 s |
| Immediate repeat, 95th percentile | 23.195 s | 0.451 s |
| Immediate repeat, slowest | 26.143 s | 2.596 s |

Reported search expansions across the matrix fell from 145.14 million to 3.34 million. The new counter includes graph expansions and the final partial block of fine-grid work. The longest individual planning slice dropped from 283 ms to 68 ms. A single slice can still cause a noticeable hitch. Easy repeats cost an extra 15 ms at the median.

### First attempts by zone count

These are the 82 primary first attempts across 41 routes, combining Off and Firm road preferences. Ratchet to Shimmering Flats has its own six-setting test below. Each median includes every attempt in its row.

| Zones | Attempts | Usable before | Usable now | Previous median | New median | New slowest |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Within one zone | 4 | 4 | 4 | 0.437 s | 0.049 s | 0.107 s |
| 2 zones | 14 | 11 | 14 | 1.304 s | 0.189 s | 2.923 s |
| 3 zones | 8 | 7 | 8 | 1.055 s | 0.213 s | 0.937 s |
| 4 zones | 8 | 8 | 8 | 2.625 s | 0.235 s | 0.575 s |
| 5 zones | 8 | 8 | 8 | 3.877 s | 0.427 s | 1.238 s |
| 6 zones | 10 | 7 | 10 | 5.458 s | 0.602 s | 5.081 s |
| 7 zones | 8 | 7 | 8 | 4.827 s | 0.564 s | 3.617 s |
| 8 or more zones | 8 | 4 | 8 | 10.006 s | 0.964 s | 3.459 s |
| Cross-continent | 14 | 13 | 14 | 0.125 s | 0.151 s | 1.598 s |

The slowest new first attempt was Camp Mojache to Orgrimmar on Firm. It took 5.08 seconds and returned a route. The previous attempt failed after 24.23 seconds. On the cross-continent trips, the median rose by 26 ms. Eastern Ashenvale to Menethil on Firm, the previously failing trip, succeeded in 1.60 seconds.

### Ratchet to Shimmering Flats

With swimming allowed and no recorded flight offers, the new planner selected the Great Lift at every road setting. The host column measures offline elapsed calculation time. The final column estimates how long a player at 60 FPS would wait if the game resumes the planner once per frame.

| Road preference | Previous outcome and time | New host time | New 60 FPS estimate |
| --- | --- | ---: | ---: |
| Off | Route in 18.89 s | 0.76 s | 4.59 s |
| Light | Failed after 27.04 s | 0.96 s | 5.02 s |
| Moderate | Failed after 25.40 s | 1.13 s | 5.37 s |
| Balanced | Failed after 23.84 s | 1.10 s | 4.99 s |
| Firm | Failed after 25.74 s | 1.34 s | 5.60 s |
| Strong | Failed after 20.88 s | 2.24 s | 9.42 s |

## Why long routes stalled

Ratchet to Shimmering Flats reproduced the problem with swimming permitted. Six speculative searches in Dustwallow Marsh each spent 262,144 expansions. Together they consumed 1,572,864 of the 1,978,624 expansions in a successful roads-off run. The journey the player would actually follow went through the Barrens and Thousand Needles via the Great Lift. With Firm road preference the old planner exhausted its allowance before delivering a route.

In eastern Ashenvale, the old roads-off search found the walk towards Auberdine after 243,149 expansions. Firm exhausted its 262,144 allowance on the same connected ground. Enlarging the allowance would have made expensive alternatives even more costly. The base terrain, ground corrections, water masks, roads and crossings in this comparison have identical before-and-after file hashes.

## What changed

- Mapperly ships a connectivity graph for all 55 maps with supported terrain. The builder divides 39.3 million fine cells into 12-by-12-cell tiles and records actual walkable contacts between the separate connected areas inside each tile. It builds independent graphs for dry ground and swimming-permitted ground. At route time, Mapperly selects a series of contacts, then constructs and validates the walk with the original terrain, road and liquid rules. The detailed search is still available.
- The travel planner considers complete combinations of walking and transport before spending large amounts of work on individual connections. It tests promising walking legs cheaply, shares work across candidates, and retries an essential difficult leg with a larger allowance. A bounded search may return a feasible itinerary before establishing a global optimum. Character-specific eligibility, recorded flight offers, fares and boarding geometry still apply.
- Repeated budget failures are reusable only for compatible endpoints, direction, policy and allowance. A larger search can retry. A best-effort dry search has a 131,072-expansion ceiling, including smaller caller limits. Explicit dry-only requests keep their original policy. Dock walking and station guidance use separate cache entries.
- The planner counts the last partially completed block of expansions, yields during long cached-path checks and reports both active calculation time and total elapsed time in `/mapperly report`. These measurements help distinguish a difficult route from a low frame rate.

The graph contains 688,951 boundary contacts across the two water policies. The generated Lua source is about 3.34 MB and compresses to about 0.50 MiB. Five fresh Lua runtimes retained 3.33 MiB each after loading the asset. Parsing took 32–48 ms on this host. These are one-time loading costs.

The design draws on hierarchical grid search and lazy edge evaluation. Mapperly uses its own terrain policies, budget limits and transport estimates. The timings in this report come from Mapperly. [Hierarchical pathfinding paper](https://webdocs.cs.ualberta.ca/~jonathan/publications/ai_publications/jogd.pdf) · [Lazy edge evaluation paper](https://arxiv.org/pdf/1603.03490) · [Research notes](route-planning-research-2026-11-25.md)

## Method

The comparison uses 42 named routes and 131 configurations, each measured once in a fresh Lua runtime and once as an immediate repeat. The same Windows host ran the production Lua 5.1 planner serially with fixed start and destination coordinates. The test used both factions, road preference from Off through Strong, walking-only controls, optional swimming and synthetic discovered-flight offers. The primary comparison uses normal transport settings, no recorded flights, and both Off and Firm road preference. Setup and post-plan geometry checks are outside the timer.

Zone counts include both endpoints and describe the shortest chain in the walking crossing graph. A vehicle can change which zones the returned route actually traverses. The benchmark checks ordinary walking geometry at full map resolution. City guidance and native transport handoffs have separate tests. Results include time spent on failed plans. The 60 FPS estimate simulates one planning slice per frame. Both that estimate and host compute time require live-client confirmation on the player's hardware.

## Remaining coverage and journey quality

- **Travel time and road preference.** For the 218 matched successes, the median change in estimated journey duration was +0.04% and the 95th percentile was +1.45%. The largest increase was 48% on Goldshire to Darkshire with Avoid swimming enabled. The old planner fell back to a 3,019-yard swim-and-walk route. The new planner found a 4,469-yard dry route through Westfall. On four Firm routes sampled every two walking yards, the fraction on marked roads decreased by 2.4–5.0 percentage points. Walking distance on those four changed by at most 15 yards.
- **Eastvale to Refuge Pointe on foot.** The main Loch Modan ground region does not reach the northern pass used by crossing links 81–83. The western Dun Morogh route to the Wetlands also ends on a separate region. The sharper test includes verified structures as possible connections and skips its conclusion if the region evidence is incomplete. Walking to Thelsamar or to Loch Modan **19.16, 17.27** succeeds. With normal transport settings the full journey to Refuge Pointe succeeds. A through-walk needs verified pedestrian access through one of those gaps.
- **Booty Bay to Darkshire.** The 1.2.5 benchmark found a two-boat detour around the northern Stranglethorn chasm. The subsequent 1.2.6 preview adds the verified bridge deck and compares it when selecting a journey. The archived timings above refer to 1.2.5. [Native terrain findings](routing-terrain-findings-2026-11-25.md)
- **Goldshire to Astranaar.** The tested Stormwind harbour itinerary includes a tram trip to Ironforge and back before boarding the Auberdine boat. The city entrance is on ground region 52. The verified harbour descent and returning tram are on region 36. Closing that pedestrian gap in the city would remove the need for the planner's inefficient round trip. The test also confirmed the route uses the verified pier when boarding.

## Verification and raw results

All 131 addon test scripts passed. The data checks covered 3,367 precomputed walking paths, the terrain signatures for both water policies on all 55 supported maps, and the native samples behind the Great Lift. The benchmark checked every ordinary walking leg it returned. A route can pass these checks and still take a long detour around a gap in the terrain model.

The separate benchmark archive contains the frozen coordinates and settings, the old planner modules, both sets of raw results, a CSV pairing every attempt, the road samples and reproduction instructions. [Download benchmark evidence](../benchmarks/route-performance-2026-11-25.zip)

## In-game confirmation

1. Put the build's `Mapperly` folder in `Interface/AddOns` and reload the UI. Open Navigation settings, enable smart routing, select Firm roads, enable lifts and leave Avoid swimming off.
2. Start near Ratchet at **62.4, 37.8** in the Barrens. Alt-right-click **78.0, 75.0** on the Thousand Needles map. Record the time until the route steps appear and the selected transport. The reference character has no recorded flights, so an eligible flight on another character can change the result.
3. Repeat the request without reloading. If either run feels slow, use `/mapperly report` and copy the recent calculation and its counters. `elapsedMS` includes time between frames, `workMS` measures time inside planning slices, and `peakSliceMS` is the longest slice. Include the road setting and whether Avoid swimming was enabled.

## Dun Algaz follow-up, 26 November 2026

The Eastvale to Refuge Pointe gap recorded above was traced to Dun Algaz. Four native tunnel floor placements join three dry outdoor areas that the terrain cleanup had discarded. Each area has now been restored from the original terrain samples. The repaired route passes the R27 walking-only control with Firm roads, including full-resolution checks of every ordinary walking leg.

A player also reported a failed journey from Stranglethorn Vale (46.71, 15.97) to Eastern Plaguelands (82.57, 69.39). In preview.2 the client exhausted all 128 walking checks in 15.11 seconds. The preview.3 regression replays the exact coordinates in both directions with Firm roads, swimming allowed and boats and flights disabled. It requires all four tunnels, checks the endpoints and validates the walking legs. A separate follower test moves through each tunnel at five-yard intervals in both directions, including changing zones inside the tunnel.

The following timings use the offline Lua 5.1 harness, an Alliance character and the preview.3 walking data. A repeat uses the same runtime and starts from the same coordinates.

| Route | First calculation | Immediate repeat | Walking checks | Cells expanded on first calculation |
| --- | ---: | ---: | ---: | ---: |
| Stranglethorn Vale → Eastern Plaguelands | 1.75 s | 0.42 s | 30 | 24,509 |
| Eastern Plaguelands → Stranglethorn Vale | 1.63 s | 0.24 s | 30 | 24,452 |
| Same Stranglethorn start → Darkshire | 0.16 s | 0.05 s | 3 | 1,733 |

Neither long route expanded terrain cells on its immediate repeat. For comparison, the original offline replay exhausted 128 walking checks and failed on both attempts, including the repeat with zero expansions. Avoid swimming was off in the player's report. A separate run with it enabled succeeded but took about eight seconds while attempting a dry route before falling back.
