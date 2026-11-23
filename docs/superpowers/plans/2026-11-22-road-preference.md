# Road preference implementation plan

**Goal:** Expand the approved Duskwood extraction to all local zones and offer optional road-biased smart routing.

**Architecture:** Extract effective road/cobblestone texture weights from native texture ADTs. Bundle sparse binary masks aligned exactly with terrain grids. Penalize off-road walking by 35%, preserving terrain restrictions and cost-aware smoothing. No road data means ordinary smart routing. Direct guidance ignores this setting.

**Tech stack:** Python/Pillow extraction, standalone Lua 5.1 runtime, existing cooperative A* and settings UI.

**Decisions:** Off by default; changing it replans a current smart destination transactionally. No client writes, external addon requirement or public release. Texture classification is heuristic; generic dirt is excluded. Town paving can count as road. Missing texture tiles remain non-road, never prohibited.

- [x] Generator: test alpha decoding, layer occlusion, filename classification and aligned crop. Generate all local-zone masks, metadata, overlays and coverage index; record unavailable areas honestly.
- [x] Runtime: tests for road detour, smoothing preserving preference, blocked terrain, no-road fallback, toggling and cache separation. Add Roads.lua/Data/Roads.lua and integrate through Journey.Plan.
- [x] Settings: saved opt-in checkbox, clear description, live replan; UI regression tests.
- [x] Verify: all existing suites, representative map overlays and native route performance; bump local preview and package. Update roadmap and provenance.

Validation: 16 suites pass against the final dataset. All 55 grids match terrain coordinates and decoded cell counts. Duskwood and Elwynn native routes validate; measured searches about 0.77s/0.11s total in the test VM, divided into cooperative jobs in-game. Reviewed overlays: Duskwood, Mulgore, Arathi Highlands and Riverglades. ZIP integrity and all 55 overlay sets verified. In-game acceptance is still needed. Review finding fixed with RED/GREEN asynchronous-preview cancellation test. Public release unchanged.
