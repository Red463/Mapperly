# Route-planning research and implementation priorities - 25 November 2026

## Recommendation

Keep the current terrain, liquid and certified-floor predicates as the authority. Improve the amount of search requested before changing the grid representation. The best immediate combination for this Lua 5.1 addon is:

1. Cache directional, allowance-scoped budget failures in `PathReuse`, with the same resolved source/policy checks used for successful geometry.
2. Retain a fully validated itinerary as an incumbent and limit optional improvement work. Use admissible bounds to reject connections that cannot improve it, and distinguish a usable budget-limited result from proven optimality.
3. Try prepared walking geometry through nearby anchors as a validated candidate for arbitrary endpoints. Keep ordinary terrain search as the fallback when connector selection is incomplete.
4. If cold failures remain substantial, add an offline hierarchy over the unchanged fine grid. This is the strongest structural improvement, but has a larger implementation and generated-data cost.

A complete-itinerary lazy planner is a credible subsequent replacement for the current network scheduler. Full ARA*, JPS/JPSW and changing terrain resolution should follow evidence from the smaller interventions. These rankings are engineering judgments based on the inspected implementation and existing survey, not measured speedup claims.

This investigation edits this report only. No runtime, generated mask, bridge, crossing or fishing changes were made, and no timed benchmarks were run concurrently with other work.

## Evidence in the present code

Sources inspected: `tools/benchmark_route_matrix.py`, `docs/route-generation-survey-2026-11-25.md`, `TravelNetwork.lua`, `Terrain.lua`, `PathReuse.lua`, `TravelBounds.lua`, `Roads.lua`, `Water.lua`, `WalkingRegions.lua`, `PlanningJob.lua`, `Journey.lua`, `tools/build_walking_paths.py`, `tools/build_walking_regions.py`, and the walking-path manifest. Observations below describe that working-tree snapshot; other agents may change it after this report.

### The expensive operation is an entire local search

`Terrain.Path` performs A* on an eight-neighbor grid. It uses physical rectangular-cell distances, a binary heap, cached row expansion, and a rectangular-grid octile heuristic. Diagonal movement requires both adjacent orthogonal cells. Returned geometry is smoothed with a supercover segment test. With roads enabled, neighbor cost is physical move length multiplied by the average endpoint road factors. The factors are 1 on roads and 1.10, 1.20, 1.35, 1.75 or 2.50 away from roads.

`TravelNetwork.Plan` already queues cheap lower-bound connection attempts instead of immediately searching every outgoing edge. However, resolving one attempt can still invoke a 262,144-cell local search. The plan shares a default two-million-cell ceiling and a 128-call ceiling. It has a restricted first phase and an unrestricted fallback, per-plan path memoization, fare labels, and an incumbent `bestGoal` when available. Therefore simply adding another per-edge deferral is unlikely to address the whole bottleneck.

The existing survey provides direct evidence:

- Ratchet to Shimmering Flats with roads off returns a Great Lift itinerary, but its warm attempt still spends six full local allowances, 1,572,864 cells, on alternatives in Dustwallow Marsh. The returned walking legs use the Barrens and Thousand Needles.
- Astranaar to the Azshara bank on Firm repeats one failed 262,144-cell search while successful portions become cheap.
- Ashenvale east to Auberdine on Firm reaches 128 local searches across 18 map IDs before failing. Those maps are attempted alternatives, not necessarily intended journey legs.
- Recorded flights can make several routes cheap; this does not repair walking planning or establish the user's own flight knowledge.

These are host measurements and traces from [the existing survey](route-generation-survey-2026-11-25.md), not live WoW latency. Increasing the per-plan budget alone risks lengthening the same failures.

### Prepared paths have a narrow lookup surface

`PathReuse` uses exact endpoint coordinates and resolved terrain, ground, road and water policy identities. It revalidates segments even on a hit. Shipped geometry is indexed by that exact pair, and only successful live geometry is retained. On a miss it clears the legacy inner terrain cache before invoking the original search; budget exhaustion returns without a persistent negative entry.

The manifest records 3,367 paths and 51,926 retained points across 48 zones. The compiler defaults to 32 selected fixed-anchor pairs per zone and six road modes. It deliberately leaves missing pairs and bounded offline failures for runtime. This is valuable acceleration for exact travel anchors, but does not directly connect an arbitrary player position to a prepared route or establish every pair's reachability.

The cross-zone cache keeps at most 16 source contexts. An 18-map failed plan can consequently evict earlier contexts. This is a plausible contributor to repeated misses, requiring measurement before changing the limits. The main problem is still expensive searches, rather than evidence that raising a cache cap alone will solve it.

### There are two cost quantities

Local A* minimizes a road-weighted grid score, then returns physical smoothed length. `TravelNetwork` adds physical walking lengths and transport seconds converted to equivalent walking yards. The local weighted score is not returned as the network objective.

Consequences for any replacement:

- Preserve separate physical length, road-weighted score and estimated seconds fields when introducing new bounds or caches.
- An existing prepared path is a feasible upper bound, not generally a lower bound on an unknown connection.
- Do not claim a global shortest-time or road-cost guarantee from the present two-level objectives. Adjacent-zone walking searches explicitly favor a feasible direct crossing, and other search limits also affect completeness.
- A road-aware local shortcut must still preserve the selected road preference. The existing smoother already guards against replacing a road bend with a higher-cost chord.

## Established techniques and their fit

### Hierarchical pathfinding

HPA* partitions a grid into clusters, precomputes connectivity and crossing costs between entrances, inserts the start and goal using local connections, searches the abstract graph, and refines its selected path. Restricting entrance transitions trades exactness for speed; the original paper's favorable path-quality and speed results are experimental, not universal guarantees. [Botea, Mueller and Schaeffer, *Near Optimal Hierarchical Path-Finding*, 2004, original paper](https://webdocs.cs.ualberta.ca/~jonathan/PREVIOUS/Grad/Papers/jogd.pdf).

**Mapperly application, inferred from the code:** zones already form one hierarchy, but a local edge can span a very large zone. Add a second hierarchy inside zones, starting with a small offline experiment using approximately 32-64 fine cells per cluster side. Cluster size is a tuning candidate, not a paper-derived optimum for this dataset. Retain multiple entrances where obstacles or road changes require them; bridge and transport landing endpoints must be inserted explicitly.

Store compact numeric node/edge arrays, source signatures, component labels, and either fine-cell portal paths or enough information for small bounded refinements. Match the actual rectangular dimensions, corner rule, ground corrections, road factor and liquid policy. A hierarchy can share topology across road strengths while retaining appropriate costs; a dry hierarchy needs dry connectivity, since removing liquid can split components.

A sampled entrance graph must not be used to prove that the underlying terrain is disconnected. An exact fine-grid fallback remains necessary unless all required connectivity is represented. Restricting refinement to an abstract corridor should widen or fall back if blocked. Fine-grid validation still decides whether a returned path is allowed.

**Assessment:** high potential for cold-query speed and predictable local work; medium/high engineering cost and substantial offline-data evaluation. A focused Barrens/Dustwallow/Thousand Needles prototype is more informative than a whole-world build first.

### LazySP and complete-itinerary evaluation

LazySP repeatedly finds a cheapest complete path using cheap estimated weights on unevaluated edges, evaluates selected edges on that path, and repeats. With admissible estimates and complete evaluation of its returned path, it has an optimality result under the paper's assumptions; edge-selection strategy affects efficiency. [Dellin and Srinivasa, *A Unifying Formalism for Shortest Path Problems with Expensive Edge Evaluations*, 2016, algorithm 1 and theorems 1-2](https://arxiv.org/pdf/1603.03490).

**Mapperly application, inferred from the code:** a small graph of crossing sides, certified structure endpoints, transport departures/arrivals, and query endpoints could represent same-zone walking connections as initially optimistic edges. Resolve only connections on the current complete candidate itinerary. Re-run the cheap graph search when a resolved edge is longer or blocked. Favor existing valid prepared paths and cheap connectors when selecting the next connection to resolve.

This differs from the present frontier, where several attractive partial journeys can trigger expensive alternatives before any complete usable journey is retained. It is particularly relevant to the Dustwallow/Great Lift case. It still cannot guarantee avoiding every expensive wrong candidate: optimistic geometry can favor a blocked shortcut. Failure caching, connectivity labels and a prepared hierarchy remain complementary.

Budget exhaustion is **unknown**, not an infinite true edge cost. Temporarily defer that edge for the present allowance; permit escalation or a fallback attempt later. Label a returned incumbent as budget limited when unresolved competitors remain. Preserve money as a search resource, directed flight offers, faction availability, boarding context, dock corridors, structure access and city/tram guidance. The existing planner's fare labels cannot be replaced by a scalar shortest path without equivalent state.

**Assessment:** medium/high potential and medium/high complexity. Worth implementing when traces show that full-itinerary ordering materially reduces expensive calls; larger than a cache fix.

### Admissible lower bounds and incumbent limits

A useful admissible estimate relaxes constraints rather than adding penalties: ignore obstacles, use the cheapest walking factor, and allow all eligible transport combinations in the bound. Mapperly already does much of this through `TravelBounds.Build`, which uses reverse shortest paths among transport positions with straight-line walking. Keep this transport-aware bound; direct distance to the goal alone can overestimate a journey that uses a fast vehicle.

For a known complete incumbent cost `U`, current accumulated cost `g`, fixed transition cost `c`, and admissible remaining bound `h`, a connection cannot improve the incumbent when:

```text
g + connectionLowerBound + c + h >= U
```

If geometry is searched only for improvement, the available physical walking allowance is:

```text
L = U - g - c - h
```

These expressions are deductions for this implementation, requiring consistent equivalent-yard units. Existing `Terrain.Path(maxDistance=L)` already restricts exploration to a padded ellipse and returns a scoped `too long` result. The network currently omits that option.

**Cautions:** with road preference, the local solver optimizes weighted cost while `L` bounds physical length. A returned road detour longer than `L` does not prove that no shorter physical route exists. Treat this as an improvement attempt, preserve the incumbent, and retain an appropriate fallback before any completeness or optimality claim. Include certified dock prefix/suffix lengths when bounding their middle ground connection. A bound on the raw grid route and a bound on the smoothed route are also different; padding must account for endpoint-to-cell-center representation.

Never multiply the entire heuristic by the off-road factor and call it admissible: a cheap road corridor can make that estimate too large. Avoid summing two separate lower bounds for the same remaining journey; use their maximum unless the sum represents disjoint required costs. These correctness conditions are consistent with the heuristic requirements discussed in [Likhachev, Gordon and Thrun, 2003, section 2.1](https://papers.neurips.cc/paper_files/paper/2003/file/ee8fe9093fbbb687bef15a38facc44d2-Paper.pdf).

**Assessment:** high value once an incumbent exists; low/medium implementation cost. Does not solve the first route or disconnected terrain by itself.

### Weighted A* and anytime planning

Weighted A* inflates the heuristic to favor goalward progress. ARA* starts with a bounded-suboptimal result and improves it by reducing inflation while reusing OPEN/INCONS search state. Its guarantees assume the stated cost and heuristic conditions; inflating a heuristic is a route-quality tradeoff, not automatically an equivalent optimization. [Likhachev, Gordon and Thrun, *ARA*: Anytime A* with Provable Bounds on Sub-Optimality*, 2003, sections 2.1-2.2](https://papers.neurips.cc/paper_files/paper/2003/file/ee8fe9093fbbb687bef15a38facc44d2-Paper.pdf).

**Mapperly application, inferred from the code:** an optional bounded weighted pass could generate a first candidate, then exact A* can remain the fallback when that pass fails. Such a pass can cut exploration for reachable destinations but need not help true dead ends. Keep heuristic inflation separate from road preference strength: changing search direction must not silently change which terrain is cheap.

If this mode affects cached geometry, include solver policy in its identity or explicitly treat its result as a candidate. Existing baked paths and session successes should not silently be presented as exact results under a different solver. Full ARA* adds persistent frontier and inconsistency state, cancellation handling, and a clear policy for when an improved itinerary replaces the displayed one. Those costs are unlikely to be the first priority when the survey shows unused alternative searches dominating.

**Assessment:** a small, explicit first-candidate experiment is feasible; a universal weighted-search replacement or full anytime UI needs more evidence and validation. Do not promise an end-to-end epsilon bound while local smoothing, network objectives and incomplete graph passes differ.

### JPS and weighted JPS

Original JPS removes symmetric alternatives on undirected uniform-cost grids. Its published movement model has unit horizontal/vertical moves and diagonal cost square root of two. [Harabor and Grastien, *Online Graph Pruning for Pathfinding on Grid Maps*, 2011, notation and pruning rules](https://users.cecs.anu.edu.au/~dharabor/data/papers/harabor-grastien-aaai11.pdf).

Road-enabled Mapperly grids violate uniform terrain cost; arbitrary JPS pruning there can discard the preferred route. Roads-off mode is closer, but rectangular physical cells and Mapperly's strict corner predicate still require a matching proof and implementation. Hard dry/liquid blocking does not itself introduce weighted terrain: roads-off dry mode remains uniform over permitted cells. Future swimming speed penalties would introduce additional costs.

JPSW addresses weighted-grid symmetries with revised pruning and jump caching; the authors warn that naive weighted extensions can repeatedly scan large areas. Their paper discusses alternate edge-cost models as possible adaptations, rather than supplying a direct Lua implementation for Mapperly. [Carlson et al., *Optimal Pathfinding on Weighted Grid Maps*, AAAI 2023, problem model and overscanning sections](https://ojs.aaai.org/index.php/AAAI/article/download/26458/26230).

**Assessment:** potentially useful local solver work, but higher correctness and porting risk than eliminating redundant local calls. Published C++ results do not establish a Lua 5.1 speedup. Keep JPS/JPSW behind differential tests on small grids with road boundaries, rectangular cells, narrow passages and every corner configuration before considering production use.

## Ranked changes for this addon

| Rank | Change | Expected benefit | Effort / principal risk |
| --- | --- | --- | --- |
| 1 | Context-aware directional budget-failure reuse | Removes repeated identical expensive failures on warm plans | Low/medium; must preserve uncertainty and larger-budget retries |
| 2 | Preserve a validated incumbent; bound optional alternatives | Targets Great Lift versus expensive Dustwallow alternatives | Medium; explicit quality/completeness limits and consistent units |
| 3 | Bounded first/last-mile connectors to prepared anchor geometry | Expands value of 3,367 existing paths to arbitrary positions | Medium; nearest anchor alone can miss a better or reachable option |
| 4 | Complete-itinerary lazy scheduling | Reduces evaluations of attractive partial journeys | Medium/high; retain all transport and fare state and budget uncertainty |
| 5 | Offline within-zone hierarchy over original masks | Reduces cold local-search size and worst-case refinement work | High; graph size, dry connectivity, signatures, portal coverage |
| 6 | Explicit weighted first-candidate experiment | May accelerate reachable local legs | Medium; route quality and solver-policy cache identity |
| 7 | JPS/JPSW or full ARA* | Potential local-search gains after scheduler work | High; movement/cost assumptions and Lua memory/constant factors |

The hierarchy is the strongest longer-term structural option; its rank reflects implementation cost and the current evidence of avoidable work before a useful route appears.

## Concrete safe cache design

Use separate successful, proven-unreachable, range-limited, and exhausted-budget states. A negative entry should carry resolved map/context identity, ordered exact endpoints, road factor/mode, effective swimming policy, algorithm revision/options, optional distance scope, and actual exhausted allowance. Bound negative entry count independently of retained geometry.

- Successful geometry can use the existing reversible pair key because movement costs and geometry are symmetric under the same policy.
- Budget failure must remain **directional**. A* from B to A can explore a different amount from A to B even on the same undirected terrain. Canonicalizing endpoint order for these failures is unsafe.
- Reuse an exhaustion only for the same deterministic search policy and an equal or smaller requested allowance. A larger allowance must be allowed to try again. If solver order, heuristic weighting or fallback strategy changes, its identity changes.
- A `too long` result only applies to its bound/search scope. The present road-weighted/local-physical mismatch means it should not be promoted to a permanent no-route fact.
- Exhaustive component separation is stronger than an exhausted search. Base ground region labels can establish separation under a stricter dry policy too, but equal base labels do not establish dry connectivity. Certified structure/portal paths can still connect otherwise separate local ground regions at the network level.
- Return cache hits through normal planning progress reporting, without charging fictitious expanded cells. Include negative hits and reasons in benchmark diagnostics so an apparent speedup can be audited.

Mutation tests should invalidate a cached exhaustion when terrain, ground corrections, roads, dimensions or liquid policy changes. Direction, smaller/equal/larger allowances, and cross-context eviction deserve explicit tests; positive geometry validation remains unchanged.

## Prepared connectors without a new mask format

Index the existing fixed endpoints spatially per map and base component. Query a few candidates in increasing physical-distance order, then run bounded terrain connectors rather than unvalidated straight chords. Combine a connector, one or more already validated prepared paths, and a destination connector into a full candidate. Validate the resulting geometry and exact endpoints again. A prepared path to a distant anchor can be more useful than a nearest anchor across a river; candidate selection should consider connectivity and the complete estimated itinerary.

Cap candidate connector work and preserve the ordinary terrain/network fallback. Missing prepared geometry means unknown, not forbidden. Keep certified bridge decks, landing access and dock tails as distinct graph edges so an apparent terrain chord cannot bypass their floor evidence. Avoid materializing all anchor pairs and all query connectors: the existing source is already approximately 3.9 MB before Lua table allocation.

## Terrain and runtime constraints

Do not downsample the authoritative terrain mask to obtain speed. An any-permitted-cell coarse tile can create false passages; an all-permitted-cell tile can erase narrow valid passages. A coarse optimistic graph can guide search or form lower bounds only with a demonstrated relaxation relation, followed by original-grid validation. A conservative coarse graph can provide candidate routes but must not prove fine-grid unreachability. Build bridge/ground corrections remain necessary for actual geometry omissions, independently of search performance.

The current decoder already moves packed-row expansion into `gsub` and caps its decoded storage. The local search uses a heap; replacing the network's linear frontier scan with a heap may help at scale, but existing traces indicate full local A* calls dominate. Avoid building giant per-cell Lua table hierarchies during login. Prefer generated compact arrays and lazy per-zone structures; measure loaded memory as well as file size.

`PlanningJob` slices work at four milliseconds or eight checkpoints. A lower total computation cost and fewer checkpoints can reduce modeled latency, but checkpoint removal alone can worsen frame responsiveness. Preserve coroutine cancellation and checkpoint coverage during cache signatures, graph construction, refinement, smoothing and validation. Host timing and the benchmark's 60fps model remain distinct from in-game measurements.

## Verification and decision gates

Run comparisons serially using the existing benchmark harness, retaining cold and immediate repeat results, host seconds, modeled scheduling seconds, cells, call counts, negative hits and geometry validation. Preserve each source hash set so a bridge-data change cannot be mistaken for an algorithm speedup.

First inspect R42, R09 and R10 with roads off and Firm; then R08, R13, R25, R26, R29, R33, R34 and R41. Include known fast routes R01, R03, R23, R35 and R39 to catch setup regressions. Run a small targeted subset before the full matrix. Dry-first, explicit swimming prohibition, recorded flight fixtures and walking-only controls are separate policies and should be reported separately.

Accept an optimization only when it improves usable results or computation without invalidating geometry or transport rules. Report changed distance, estimated seconds, selected transports, actual zones and road-weighted cost if added. An earlier failure is not a routing success. A returned incumbent with unresolved alternatives is useful but should have honest quality metadata. Require certified bridge/crossing tests, dock approach tests, money/flight eligibility tests, swimming policy checks and small-grid differential checks appropriate to the changed algorithm.

If negative caching fixes warm repeats but cold R42 remains slow, pursue prepared connectors and complete-itinerary ordering. If the dominant time then becomes a necessary long local leg rather than unused alternatives, prioritize the within-zone hierarchy. That distinction should decide the next substantial investment.

## Source availability and limits

Primary papers were consulted through web search and, where accessible, their complete PDFs. The [LazySP arXiv PDF](https://arxiv.org/pdf/1603.03490), [JPS author-hosted PDF](https://users.cecs.anu.edu.au/~dharabor/data/papers/harabor-grastien-aaai11.pdf), and [ARA* proceedings PDF](https://papers.neurips.cc/paper_files/paper/2003/file/ee8fe9093fbbb687bef15a38facc44d2-Paper.pdf) were directly readable during this investigation.

HPA*'s author-hosted paper remains indexed with primary text, including its cluster, start/goal insertion and refinement descriptions; direct fetching redirected to an unavailable university directory. JPSW's AAAI paper and author copy were indexed with primary text, including the edge-cost and overscanning sections; direct fetching encountered publisher bot protection and university resource protection. These access limits prevent claiming that every page of those two PDFs was directly fetched. The report uses their indexed original paper text, not third-party summaries, and does not transfer their experimental speedups to this addon.
