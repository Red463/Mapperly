# Cross-zone walking plan

Implement the approved next milestone: connect verified zone exits, continue the arrow across boundaries, and render the complete journey.

- [x] Generate crossings from native MCNK area IDs, AreaTable ancestry and UiMapAssignment. Require road coverage and permitted connecting segments in both local maps; cluster nearby duplicates. Bundle map extents, canonical aliases, endpoints and provenance. Exclude underground capital interiors and unsupported terrain instances.
- [x] Add TravelNetwork: cooperative A* across crossing endpoints using actual local Terrain.Path geometry, finite graph budgets and road preference. Failure preserves the previous plan. No rectangle-overlap adjacency, synthetic straight-line gaps or transports.
- [x] Add multi-zone walking legs/flat display geometry to Journey. Follow local turns, aim across the verified boundary until the client reports the next zone, then advance. Preserve pause/skip/remaining-distance semantics. Never skip a boundary via ordinary near-waypoint arrival.
- [x] Adapt RouteRecovery to current-leg bounds and map ID. Make HUD/map/minimap use the same plan; preview lists zone legs and coverage limits.
- [x] Verify generated crossings, native Darkshire-to-Goldshire plans, synthetic multi-hop paths, transition lag, unexpected zones, cancellation and local-route regressions. Review, update checklist, package preview.8.

Data-backed means native area ownership plus the existing terrain heuristic, not collision certification. Missing links and underground cities fail clearly. All work stays on feature/journey-navigation; no public release.

Ruling: roads may be present on only one side of a native boundary when the other side lacks a road texture; the complete short connector must still pass both masks. This recovers bridge approaches without filling blocked terrain. Great Lift, Ironforge and Undercity interior entrances are deferred. Adjacent connections are tried before general graph search to avoid unrelated local searches; no global travel-time optimum is claimed.

Validation: 19 suites pass, including all 49 native connectors, 3-zone synthetic/reverse routing, Darkshire?Goldshire2,986yd/29 cooperative steps, real Navigation.Start/HUD handoff, overlap/lag, failure preservation and scrolling preview. Read-only fresh-context review found no important reproducible bugs. Live-client acceptance is still required.
