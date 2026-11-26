# All Bridges and Zone Crossings Implementation Plan

> **For agentic workers:** When the user explicitly activates this task, use superpowers:executing-plans to implement it task-by-task. Steps use checkbox syntax for tracking.

**Status:** Offline implementation and available-source audit completed on 25 November 2026, subject to the final verification recorded in the [execution ledger](../../bridges-and-crossings-progress.md). Live acceptance and entries lacking source/terrain coverage remain explicitly unresolved; this is not an exhaustive in-game certification. Publication still requires a separate request.

**Requested:** 25 November 2026.

**Goal:** Audit every bridge and zone crossing in WoW Forever and make supported walking routes work across them, including bridges entirely within one zone.

**Architecture:** Build a reproducible inventory from the available client snapshot, then validate individual placed structures and zone transitions against native floor geometry, terrain, area ownership and existing routing data. Extend the certified structure network where evidence supports it; retain explicit unresolved entries where evidence is incomplete. Same-zone bridge connections must participate in route planning rather than relying solely on zone-boundary edges.

**Tech Stack:** Python extraction/build tools, native client snapshot data, Lua 5.1 addon runtime, Lupa regression harness.

**Spec:** The user's request: “We need to address every bridge in the game including mid zone bridges. We also need to check every zone crossing in the game.” Plan and save this work now; execute only when requested.

## Global constraints

- Scope is the full WoW Forever world for the target client build, including custom zones, capitals and uncovered maps. The existing terrain-covered map list is a starting point, not the definition of completeness.
- Include bridges within zones and across zone boundaries, whether currently working, broken, or not yet represented in Mapperly.
- Include all potential zone crossings in the audit. Classify walking exits, tunnels, gates, bridges, portals, transports and non-traversable adjacencies separately.
- Do not infer a usable crossing from touching map rectangles, neighbouring area IDs, a bridge-like model name or a straight line between endpoints.
- Keep source installations read-only. Record build, asset identity, placement transforms and reproducible evidence.
- Keep Mapperly standalone; do not require another installed addon for routing data.
- Preserve swimming preferences, road preferences, optional straight-line guidance, existing transport handling and previous successful navigation on planning failure.
- Unknown geometry must remain explicit. A fully audited inventory can contain unresolved entries; it must not claim every crossing works until those entries are resolved and checked.
- No publishing, release or live installation is authorized by this deferred task.

## Review focus

1. A bridge and the riverbed below share map coordinates: certified deck access must not grant walking permission beneath it.
2. A bridge lies wholly within one map: routing must use its floor corridor even without a zone change.
3. The player starts, finishes or replans on a bridge: follow only the necessary deck section without bank detours or loss of guidance.
4. Native zone assignment changes before or after the physical crossing: preserve guidance across overlapping maps and both travel directions.
5. A placed bridge is incomplete, broken, unsupported, faction-restricted or actually a moving transport: classify it accurately instead of creating an unconditional walking shortcut.

## Starting references

- `docs/walking-coverage.md`: generated crossing inventory and known coverage limits.
- `docs/walking-geometry-gaps.md`: historical investigations; reconcile superseded findings with current data.
- `Data/Structures-SOURCES.md`: certified structure proof requirements and source provenance.
- `tools/build_southfury_bridge.py` and `tools/data/native-southfury-bridge-70959.json`: the current bridge-specific extraction example.
- `tools/build_structure_corridors.py`, `tools/build_crossings.py`, `tools/report_walking_coverage.py`: structure, crossing and coverage builders.
- `Structures.lua`, `TravelNetwork.lua`, `Journey.lua`, `RouteRecovery.lua`: floor access, network planning, guidance and recovery.
- `tests/southfury_bridge.py`, `tests/structure_corridors.py`, `tests/cross_zone.py`: current regression patterns.

Recheck these references and the client build when work resumes; this plan does not assume today's data is current indefinitely.

## Task 1: Establish the complete audit inventory

**Blocked by:** Explicit user request to begin.

**Deliverable:** A machine-readable inventory and readable checklist covering every discovered bridge placement and every potential zone crossing, including entries outside current terrain coverage.

**Files:** Create `tools/audit_bridges_and_crossings.py`, `tools/data/bridges-and-crossings-manifest.json`, `tests/bridge_crossing_inventory.py` and `docs/bridges-and-crossings-audit.md`.

- [x] Establish the target build and enumerate all maps, zone ownership boundaries and existing crossing/transport records. Record maps/assets unavailable in the snapshot.
- [x] Discover candidate bridges from placed WMO geometry, standalone and embedded model collision, road/water intersections and existing reports. Supplement name searches with geometry checks so differently named structures are included.
- [x] Assign stable placement/crossing identities. Record map ownership, coordinates, source assets, discovery method, current route support and evidence status.
- [x] Classify each entry as verified working, confirmed issue, unresolved, duplicate, non-traversable or transport/portal. Keep source verification and live acceptance as separate fields.
- [x] Add inventory regressions for duplicate placements, same-zone bridges, missing maps/assets and non-traversable boundaries. Generate per-zone counts and an unresolved list without silently dropping candidates.

## Task 2: Validate and integrate ordinary bridge crossings

**Blocked by:** Task 1.

**Deliverable:** Reproducible floor proofs and usable routes for supported fixed bridges, including same-zone bridges.

**Files:** Extend structure extraction/build tooling and proof data; modify `Structures.lua`, `TravelNetwork.lua` and `Journey.lua` only where the validated cases require it. Add `tests/bridge_routing.py` and update source documentation.

- [x] Select one same-zone bridge and one cross-zone bridge as failing end-to-end regressions before changing routing behavior.
- [x] Generalize the Southfury extraction approach to native placed floor geometry, correct transforms, continuous deck support, headroom, bounded steps, supported width and both bank connections. Reuse asset geometry while verifying each placement independently.
- [x] Integrate only validated corridors. Do not open large root-terrain cells or infer floor support across water/ravines.
- [x] Verify routes in both directions, nearby bank approaches, partial-deck starts/destinations, short deck-to-deck journeys, under-bridge rejection and instance isolation.
- [x] Verify world-map/minimap lines, arrow progression, route steps, rerouting and reload recovery use the actual deck path and retain guidance across native map handoffs.
- [x] Apply the validated method to every ordinary bridge candidate and update each inventory entry with evidence and test results.

## Task 3: Resolve exceptional bridge geometry

**Blocked by:** Tasks 1 and 2.

**Deliverable:** Individually tested support or a documented unresolved reason for each bridge that the ordinary method cannot certify.

- [x] Audit bridges built from multiple assets, standalone model floors, curved/long/suspended bridges, stairs and ramps, city/interior bridges and structures with overlapping floors or water.
- [x] Treat movable or conditional structures separately from fixed walking geometry; retain existing transport mechanisms where appropriate.
- [x] Add a failing regression for each newly supported geometry class, implement the narrowest evidence-backed handling, and verify the full route and guidance in both directions.
- [x] Identify cases where runtime position/height data cannot distinguish floors. Document the limitation and request specific live evidence rather than expanding permission speculatively.

## Task 4: Audit every zone crossing and fill confirmed gaps

**Blocked by:** Task 1; use Tasks 2 and 3 wherever a crossing depends on bridge geometry.

**Deliverable:** A disposition for every discovered crossing and corrected routing for confirmed usable exits.

**Files:** Extend `tools/build_crossings.py`, crossing/structure proof data, crossing regressions and generated `docs/walking-coverage.md`.

- [x] Check all existing links as well as missing candidates. Validate both directions, approach components, native area ownership and actual passage continuity.
- [x] Check roads, mountain passes, tunnels, city gates, cave passages, custom-zone connections, border bridges and map aliases. Audit portal/transport crossings without converting them into ordinary walking links.
- [x] Verify access from playable areas on both sides, not merely a route between two handoff coordinates.
- [x] Add confirmed missing links and correct misplaced links with reproducible evidence. Keep cliff/ocean/bounds-only adjacencies rejected and uncertain cases visible.
- [x] Add multi-zone regressions that cross several audited exits, including overlapping zone artwork, road settings, dry-first swimming fallback and supported travel-method combinations.

## Task 5: Complete acceptance and publish the coverage report

**Blocked by:** Tasks 2, 3 and 4.

**Deliverable:** A tested local candidate, explicit coverage accounting and an actionable live-test checklist. Publication still requires a separate user request.

- [x] Rebuild generated structure/crossing data and coverage reports. Revalidate retained precomputed walking paths or regenerate affected paths when their inputs change.
- [x] Run the full automated suite and measure representative short, long, same-zone and multi-zone route generation to catch regressions in search time or memory.
- [x] Produce per-zone live-test instructions with coordinates, destination, expected path, both directions, deck-start tests and `/mapperly report` collection for failures.
- [x] Track every inventory entry through source validation and live acceptance; report totals, unresolved cases and missing assets separately.
- [x] Build a local test ZIP and summarize completed coverage, outstanding limitations and any specific confirmations needed from players.

## Acceptance boundary

Checked task boxes record delivered source audits, implementation, automated regressions or the requested test instructions. They do not claim live client checks were performed. The inventory retains every unresolved candidate and missing-source map; four interior-floor approaches and all live acceptance require player confirmation. See `docs/testing-crossing-acceptance.md` and the ledger for exact totals and tests.

## Completion criteria

- Every map and discovered bridge/crossing candidate has an explicit audit disposition; missing source coverage is listed.
- Every confirmed supported bridge has reproducible geometry evidence and route/guidance checks, including mid-zone routing.
- Every confirmed supported zone crossing has correct handoffs and tested approaches in both directions, or an explicit directional restriction.
- Unresolved candidates remain visible and cannot silently become fabricated walking links.
- Automated results and live acceptance are reported separately; no claim of exhaustive live verification without recorded evidence.

## Resume instruction

When the user asks to start the all-bridges/all-crossings task, reread this plan, confirm the current repository/client state, and begin Task 1. Do not treat this document, the existing navigation checklist, or unrelated future requests as authorization to start it early.
