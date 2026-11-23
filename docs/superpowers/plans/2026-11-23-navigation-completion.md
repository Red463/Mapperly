# Remaining navigation features implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development for independent bounded modules; integrate and review in the existing feature checkout.

**Goal:** Complete remaining navigation implementation in one coordinated build and deliver a numbered live test guide.

**User authority:** Explicit instruction to implement all remaining checklist features in one pass and ask for confirmation through final testing instructions. Do not pause for feature-by-feature approval. No GitHub publication requested.

**Architecture:** Retain existing terrain/route/transport interfaces. Add source-backed swimming policy, safe character-specific resumable destination state and bounded route reports. Complete local transport support using native audited evidence where available and an explicit player-recorded ride workflow where exact pairing/floors cannot be proven offline. Preserve native floor, faction, flight discovery, cancellation, saved-data and direct-mode rules.

## Workstreams and ownership
1. Swimming: Water.lua / source-backed WaterData, builder, Terrain.lua and PathReuse.lua integration, dedicated tests. Default swimming allowed; disabled requires dry/known permissions. Preserve certified floor paths. Refresh bound source proofs/precomputed data if necessary; do not silently ship stale baked paths.
2. Reports and journey recovery: JourneySession.lua, RouteReport.lua, their UI and tests, PlanningJob.lua result observability. Save bounded validated target/profile per character, never blindly resume aboard vehicles or restore obsolete raw indices. Offer safe resume/replan after stable login; explicit Stop/arrival clear state. Export a bounded copyable report with routing context/errors/counters, excluding names/GUID/wallet/raw dumps.
3. Local transports: native tram/capital lift audit and supported connection data when proven; recorded ride model/UI and tests for remaining user-verified connections. Do not fabricate station pairing, floors or timings. Never enable source-only/unsupported services as verified. Report precisely what still needs live acceptance.
4. Root integration: Store defaults, Core lifecycle/commands, Navigation/Journey options and persistence hooks, Navigation settings layout and utility windows, TOC load order, final tests/reviews/docs/release-candidate packaging.

## Steps
- [x] Independent red tests and implementation of each workstream, with source/negative cases.
- [x] Integrate navigation controls into clean existing themed windows; preserve both themes and current actions.
- [x] Revalidate native lift proof and prepared walking path signatures after any terrain changes; rebuild or exclude incompatible paths rather than using stale results.
- [x] Run complete automated suite, representative performance checks and independent component/final reviews.
- [x] Update checklist truthfully: distinguish implemented, source-verified and live-confirmed. Document any data-dependent remaining limitation.
- [x] Package one local1.2.0 release candidate; supply numbered, reproducible in-game tests for every feature needing confirmation, plus report export instructions.

## Test focus
Water unknowns/bridges, cache policy isolation, updates while aboard, character/build isolation, corrupted/stale saved state, cancellation/newer-request ownership, same-XY lifts and zero nativeZ, loading during tram rides, report size/protected values, setting changes and both theme layouts.

## Rulings
Work continues in the existing dirty feature checkout because the earlier approved previews include necessary uncommitted data/modules. Generic recorded transport connections may be shipped as explicitly player-recorded/manual confirmation features; unproven native topology stays unbundled until evidence exists.

## Verification outcome

All 97 Python/Lua suites passed in the final combined run (output/rc1-tests.log). Independent component reviews checked recorded-ride policy/ownership, recovery/report isolation and native liquid coverage. Native lift exit proof retains all 2,223 accepted cells and all 3,367 prepared paths passed source/segment revalidation. RC ZIP contents and TOC modules were checked against the working sources. Live acceptance is pending as documented in docs/testing-1.2.0-rc1.md; automatic Deeprun/capital lift floor datasets remain unbundled.
