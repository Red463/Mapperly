# Discovered Flight Journeys Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline, then obtain one fresh review. The existing journey design and instruction to proceed authorize this milestone.

**Goal:** Add character-specific, faction-appropriate flight journeys using positively observed client offerings, with native geometry, quoted fares and reliable landing guidance.

**Architecture:** `Flights.lua` owns character discovery, read-only taxi-window observation, eligible offered itineraries and flight guidance. `Data/Flights.lua` supplies native nodes/segments; `tools/build_flights.py` generates it from pinned build70959 evidence. The existing mixed planner consumes flight edges through Transports and follows the same typed transit legs. No taxi booking or protected click automation is performed.

**Spec:** `docs/journey-navigation-design.md`; roadmap9 and flight-cost portion of12. Existing boat/walking/diagnostic work stays on the current feature branch; no publication.

## Decisions

- Learn Current/Reachable nodes from `C_TaxiMap.GetAllTaxiNodes(GetTaxiMapID())`; IDs are nodeID, never slotIndex or CharacterBitNumber. Unreachable, absent, unknown and layer-transition rows cannot unlock destinations.
- Persist by validated player GUID. Missing/secret identity fails closed. Faction/class changes invalidate offered itineraries; no alt sharing.
- Use only observed offered directed itineraries. Source windows must be visited to record their offerings; native adjacency alone does not unlock routes. Capture full offered fare with TaxiNodeCost(slot), and match GetNumRoutes/TaxiGetNodeSlot hop slots to stable native IDs for geometry. Incomplete geometry is explicitly omitted rather than replaced with a straight air shortcut.
- Historical quotes are labelled last-quoted/estimated and revalidated when visiting the master. Known unaffordable quotes are excluded; free quotes are valid. Missing fares remain unknown, never free.
- Raised/indoor masters retain native pad height and explicit manual access. A live source-master interaction can prove the player is already at the boarding point even when root terrain does not model that floor; no walking permissions or fabricated connector are added.
- UnitOnTaxi true confirms departure; true-to-false plus valid destination proximity confirms landing. Missing/secret state and loading screens cannot end a flight. An interrupted flight waits for stable on-foot evidence before one transactional replan attempt.
- Preference changes before flight selection replan immediately. Changes during actual flight are deferred until landing, retaining the latest destination.
- Keep default-on useFlights, but unknown/unobserved flights remain unavailable. Display discovered/recorded counts and normal flight-window selection instructions in Navigation settings.

## Review focus

Alt switching and unavailable identity; transient/nonsequential slots; incomplete or cyclic hop records; free/missing/multi-hop fares; taxi UI closure without departure; protected/loading/early-landing positions; elevated/interior access; repeated deferred preference changes; existing route-budget regressions.

## Task checklist

### 1. Source data and discovery
- [x] Audit native TaxiNodes/TaxiPath/TaxiPathNode, faction/class rules and terrain/manual master access; preserve source IDs/provenance.
- [x] Write RED discovery tests, then implement `Flights.Opened/Closed/Collect/Character/Stats` and one next-frame retry only while the window is open.
- [x] Generate native lookup/segment data, verify exclusions and character isolation; integrate Core events without changing Blizzard UI.

### 2. Flight availability and planning
- [x] RED tests: no unknown or reverse route, faction/class filtering, source/destination offers, complete fares and money, missing geometry and per-character migration.
- [x] Implement `Flights.Edges(options)` for observed complete itineraries, source boarding override and typed flight metadata. Integrate with Transports/TravelNetwork without duplicating fares or waits.
- [x] Verify native mixed journeys from actual town/master locations, including raised/indoor source interactions; retain work bounds and existing walking routes.

### 3. Follower and UI
- [x] RED tests: flight selection instructions, UI close without departure, in-air suppression, loading, wrong/early landing, normal landing and deferred preferences.
- [x] Add flight-specific Guide/boarding/defer guards and one interruption replan; never call TakeTaxiNode.
- [x] Add saved Flights control and discovery status, show full route fares (or unknown/estimate) and total flight cost in preview. Existing themes and layout remain.

### 4. Verification and preview
- [x] Run all old/new suites; obtain fresh review and fix important findings.
- [x] Update design/checklist/changelog and package preview.13; verify TOC/archive. Live flight acceptance remains pending.
