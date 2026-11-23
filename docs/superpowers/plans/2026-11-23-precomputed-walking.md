# Precomputed walking connections implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship reusable terrain-validated walking sections and retain bounded live path results across zone changes.

**Architecture:** Add PathReuse.lua as a narrow wrapper around Terrain.Path, leaving the terrain algorithm and native lift coverage unchanged. Cache exact endpoint pairs under actual terrain/ground/road content signatures and normalized road strength. An offline Lua 5.1 builder generates fixed travel-point pairs using the original terrain search; missing, stale or invalid entries fall back to that same live search. Transport eligibility and dock floor constraints remain outside this layer.

**Tech stack:** Existing Lua 5.1 runtime, Python/lupa offline tooling, root Lua TOC modules.

**Approved scope:** User approved precomputed travel-point connections plus a cross-zone bounded cache. No saved-variable route cache, invented roads, change to available flights, or full road-network redesign.

## Constraints and review focus
- Maintain terrain algorithm, road strengths, maxDistance semantics and source-backed dock/lift handling.
- Bind baked results to terrain, ground corrections, roads and algorithm revision; stale entries cannot be used.
- Bound contexts, cached entry count and retained points, and return copies.
- Generate all six road modes; incomplete/failed offline pairs use live fallback.
- No GitHub publication; package local preview.39.

## Tasks
- [x] Add red tests for reuse across zones/modes, mutable source invalidation, range failures, reverse/copy safety and bounded retention.
- [x] Implement PathReuse wrapper and TOC integration without editing Terrain.lua.
- [x] Add red tests for valid/stale/invalid generated entries and offline reproducibility.
- [x] Implement fixed-anchor collection, offline generation and a source manifest; ship validated connections for all supported anchor zones/modes where searches succeed.
- [x] Benchmark native long journeys cold and repeated, verify all generated geometry and source signatures, run full regression suite and independent review.
- [x] Document measured gains and limits, bump preview.39, package and verify ZIP.

## Execution ledger
- Work in the existing feature/journey-navigation checkout: the approved preview work includes many uncommitted/untracked dependencies and must stay together.
- Use original Terrain.Path in the builder; generated failures are coverage gaps, never cached navigation failures.

- Review found the legacy cache could survive in-place ground/road mutations. Ruling: add only Terrain.ClearPathCache(), with no search algorithm changes, and invoke it before wrapper misses. Reran native exit-mask audit: masks/links exactly unchanged (1,312 upper and 911 lower accepted cells), refreshed bound source proof and rebuilt local transports.
- Cold signature hashing now cooperates with background jobs by byte budget; malformed generated arrays fail into ordinary live searches.

- Final verification: all 79 suites pass. All 3,367 generated paths validate source inputs, geometry, length, road modes and fallback guards. Independent review resolved all findings and exactly reproduced representative zone1455. Cold benchmark terrain work falls 34.6% / 45.1%; warm tests search zero cells. Local preview.39 packaged after final source verification.
