# Bridge and crossing execution ledger

Started 25 November 2026 at the user's request. Work is active; no release publication authorized.

## Historical first-batch status

- Inventory scan completed across all 73 native Map table entries: 616,311 placed objects, 7,516 inspected assets including embedded model references, 8,176 discovery candidates (including 173 road/water overlap hints). Candidates include false positives and are not claimed as usable bridges.
- Four maps have explicit source limitations: 13 and 3109 have unavailable WDT data; 3217 and 3218 provide no WDT FileDataID. No placed asset referenced by the successfully scanned maps was unreadable.
- All 132 bundled crossings, including the new bridge batch, pass endpoint-to-endpoint planning in both directions (264 route checks). This does not certify nearby approaches or every possible passage on those borders.
- Existing ownership audit covers 97 pairs in the terrain-supported world. Broader native map discovery is complete; ownership/approach auditing beyond this coverage remains open.
- The first ordinary bridge batch evaluated 118 additional named WMO placements: 10 certified corridors integrated (nine same-zone, one Barrens/Durotar), 108 unresolved with recorded reasons. Cross-zone Southfury remains separately certified. Tilted, compound and unsupported-contact cases receive no guessed links.

## Decisions

- Preserve the existing uncommitted fishing/Southfury changes and work in place. The audit adds reproducible development tools and evidence without publishing or installing a build.
- Snapshot build 70959 is the available native source; reported client build is 71037. Source certification and live-client acceptance remain separate.
- An 8,176-candidate discovery superset cannot be presented as 8,176 bridges. Names, elongated bounds and embedded bridge-model references are discovery hints only.
- First ordinary batch uses straight, yaw-only WMO floors. Unsupported rotations and missing contact proofs require further extraction work; rejection here is not a claim that the bridge cannot be walked in game.

## Next work

1. Complete ordinary bridge floor/contact validation and integrate only certified results, with same-zone and partial-deck regressions.
2. Resolve tilted, compound, M2 and embedded-model bridge cases and expand geometry-based discovery beyond bounding-box hints.
3. Audit all crossing approaches and remaining ownership candidates, including maps outside current terrain coverage.
4. Run full regressions, refresh generated path provenance, and prepare a local test build and per-zone live acceptance guide.

## Verification and corrections

- Native bank contacts now also pass the shipped dry-only liquid policy; a fine dry point is not enough if its coarse routing cell remains wet. No liquid mask was relaxed.
- Bridge and Southfury regressions cover both directions and floor following. Added same-zone entries exposed a zero-length access leg that could stall; those redundant edges are now omitted.
- Added bridge choices initially regressed quest/transport search budgets. Optional same-zone bridge detours now enter the fallback graph phase unless tied to a deck endpoint. Recorded-flight quest routing and Duskwood-to-Dun Morogh transport regressions pass again.
- Independent review found no important issues in the initial batch; source wording and ownership/runtime provenance were strengthened afterward. Full final regression result is recorded below when available.

- Strict dry-only revalidation withheld placement 237080: native contacts exist but the coarse water grid does not provide both dry routing landings. The final batch contains ten added corridors; this unresolved case is not bypassed.

## First candidate verification

- Final full automated run: **115 suites passed, 0 failed** (109.1 seconds).
- All 132 bundled crossing links pass both endpoint directions: **264 route checks**. This remains distinct from exhaustive approach and live acceptance.
- The 3,367 retained precomputed walking paths were revalidated against unchanged geometry signatures and every segment; their input provenance was refreshed.
- Local package: `dist/Mapperly-1.2.5.zip`. Per-bridge coordinates and live checks: `docs/testing-bridge-audit-batch1.md`.
- The overall plan is **not complete**. The inventory/discovery foundation and first ten-corridor implementation are ready for testing; exceptional geometry, additional ordinary candidates, full crossing approaches and live acceptance remain open.

## Expanded bridge pass, 25 November 2026

- Native file paths now supplement model/group names. This recognizes abbreviated rope-bridge assets and distinguishes bridge components from unrelated elongated props. The inventory contains 8,228 discovery candidates; every candidate has a recorded disposition or an existing certified source.
- Full native ZYX placement rotation, M2 collision arrays, active WMO doodad sets and selected bridge groups are supported by the read-only extractor. Layered floor tracking avoids dropping to a lower overlapping floor. A bounded native floor search handles winding paths; triangle-interval checks reject unsupported chords.
- Of 81 expanded floor proofs, independent floor/width/clearance and native liquid re-probes accepted 80 and withheld one submerged/unproven deck. Sixty-five accepted proofs are classified bridge placements; fifteen other floor candidates are not added as bridge permissions.
- Together with the prior eleven bridges, **76 bridge placements** have explicit deck support. The network contains **197 links / 87 native structure corridors**, including previous tunnels/gates. Offline source proof is separate from live-client acceptance.
- Fifty clusters of touching native bridge pieces were also tested. No extra cluster met all floor, clearance and dry-contact requirements; no composite shortcut was added.
- All named/path-recognized candidates and all other discovered placement candidates have been examined at the available coverage level. Remaining source limits include unsupported native maps/instances, components that do not independently form a passage, absent dry handoffs, floor/step gaps, and an unproven liquid clearance. The audit does not call these in-game bridges impassable merely because certification failed.

### Review fixes and rulings

- Fixed an observed same-zone bank-to-bank detour by comparing bridge shortcuts against the actual ground-route geometry. Replaced the loose endpoint-distance trigger that caused unrelated searches; the existing Firm Ashenvale route retains one search and its original geometry.
- Fixed rectangular-strip access: projections beyond certified endpoint planes no longer get semicircular permission caps. Narrow rows retain their individually proven radius.
- New live bridge starts use explicit elevation context. Missing/zero height cannot establish a new deck start; a remote destination pin can still name that deck. Existing established routes retain approximate XY guidance when height is unavailable, preserving the user's requirement that restricted terrain does not stop guidance. This cannot establish which vertical floor the player occupies without live elevation.
- Ruling: retain the existing dirty workspace and previous fishing/Southfury edits; no release publication or live installation is authorized by bridge implementation alone.
- Ruling: use the available build 70959 source and label live build 71037 acceptance separately. Missing terrain/geometry evidence never grants a guessed crossing.
- Deferred minor from review: expanded proofs retain the constant transform-error field for the documented native transform convention. WMO bounds, native placements, collision floors and contacts are independently checked; recording a measured numeric rotation roundtrip remains a provenance follow-up.

The full zone-crossing approach audit and live acceptance remain open. See `testing-bridge-expanded.md` for the bridge test locations and remaining-bridge status report.

### Expanded candidate verification

- Final full run after the review fixes: **117 test suites passed, 0 failed** (85.5 seconds). The additional explicit live-height admission regression also passes.
- All **197 bundled links pass both endpoint directions: 394 route checks**. The bridge suite additionally follows every certified bridge in both directions; this is still separate from live-client acceptance.
- The normal bank-approach regression selects the nearby Darkshore bridge instead of its former 226-yard ground detour. The established Firm Ashenvale case remains 4,326.394 yards with **one search / 185,600 cells**.
- Native re-probes cover all 65 expanded bridge proofs plus the prior ten-corridor batch and Southfury. No submerged deck is admitted. Fifty compound clusters were examined without manufacturing a missing connection.
- Local installable candidate remains `dist/Mapperly-1.2.5.zip`; it includes the preserved fishing work, bridge data and expanded test guide. No GitHub publication performed.

## Crossing approaches and final offline pass, 25 November 2026

- Completed the remaining work sequentially: owned-ground approach audit, review of missing boundary candidates, exact unsupported handoff quarantine, provenance follow-up, regenerated coverage and live-test instructions. Automated final verification and package evidence are recorded below when completed.
- Added a reproducible native ownership/dry-ground audit for every retained endpoint. It checks both routing directions to probes at least 75 yards beyond the handoff, with explicitly labelled 30-yard approaches and swimming fallback. Normal radial probes are 75–150 yards; a bounded 450-yard / 6,000-cell connected-ground search supplements them so narrow paths are not rejected merely because they miss a spoke. Labels describe a successful sampled approach, not swimming necessity or the maximum reachable distance.
- Eighteen ordinary handoff candidates had no supported nearby approach within that audit. Their exact world-coordinate identities and all rejection evidence remain in `tools/data/crossing-handoff-review.json`. The builder filters them before spacing and per-pair selection; nearby replacements are re-evaluated until supported or exhausted. This recovered usable alternatives, including a Dun Morogh/Wetlands candidate, rather than suppressing a whole pair.
- Ruling: withhold these unproven shortcuts rather than continue advertising useful walking access based only on two handoff cells. A legitimate obscure passage may need a new evidenced landing; this is not a claim that the location is physically impassable.
- Current network: **191 links, 66 inter-zone pairs, 87 native structure corridors, 76 bridge placements**. All **382 retained sides** have explicit outcomes: **316 normal dry approaches, 47 swimming-fallback approaches, 15 short dry approaches, four floor-specific anchors**. No retained side is silently labelled verified from a failed approach probe. Ironforge/Undercity and the two shared Timbermaw Winterspring anchors remain separately dependent on floor evidence and live acceptance.
- The 97 native ownership pairs now retain bundled-link/approach results or an unresolved no-certified-exit disposition; 33 have no bundled walking link. Zero safe samples is not proof of an in-game wall. Alternative source-supported handoffs were evaluated without adding guessed connections.
- Broader discovery remains 73 native Map entries and 8,228 candidate placements. Terrain routing covers 55 UI maps; these denominators do not imply eighteen missing normal outdoor zones. Unsupported native maps/instances and the four WDT source limitations remain explicit.
- Active embedded-model, tilted and compound candidates have source dispositions. Fifty touching-piece clusters still yield no additional certified passage. Missing masks, absent dry contacts and unsupported collision intervals cannot be resolved by granting broad terrain permission.
- Resolved the earlier deferred transform-field provenance item: expanded proofs now record measured forward/inverse placement roundtrip error rather than a constant zero. The maximum measured error is below 1e-12 yards; this tests numerical consistency, not the native transform convention itself. Native placement witnesses, bounds and floor re-probes remain independent checks.
- Twelve representative ground-approach journeys cover road/border, tunnel, bridge, custom-zone and Timbermaw cases in both directions. Transport/lift/tram paths retain their existing mechanisms and regression suites; no transport became a ground shortcut.
- The inventory individually accounts for 33 directed non-walking records: 25 static transport links, two Great Lift directions, two tram service directions and four tram portal destinations. Historical excluded records remain explicit, including the superseded old tram exclusion. No walking permission is inferred from them.
- `docs/testing-crossing-acceptance.md` contains every retained link's approach coordinates and exact handoffs plus the 18 withheld historical handoffs. An approach journey may choose another valid exit; the guide requires separately confirming the listed passage. Live tests, live screenshots, runtime elevation availability and unavailable source extraction remain external acceptance work; no exhaustive live verification is claimed.

### Final review fixes

- Fixed quarantine ordering so an unsupported candidate cannot suppress nearby road or dry-ground alternatives before they are audited. The new spacing/alternative regression failed before the fix and passed afterward. Four replacement rounds converged with 18 exact withheld candidates and 191 retained links.
- Fixed the 75-yard floating-point classification boundary; corrected the connected-grid probe range description. Swimming-fallback/short labels report observed successful probes rather than a proof that no better probe exists.
- Bound approach evidence to full inventory/CrossingData hashes; stale ordinal IDs now cause reports to fail clearly instead of attaching another crossing's evidence. The hash mismatch regression was observed RED then GREEN.
- Extended endpoint validation to load Water and isolate each target edge, checking its exact handoff or native floor in both directions. Normal journey success alone no longer stands in for checking the target link.
- Added individually enumerated transport/portal inventory records. The missing-record regression failed before implementation and passed after generation. The previously deferred transform-provenance minor is resolved; no new minor is deferred from this review.

### Final local verification

- Fresh full run after all review corrections: **120 suites passed, zero failures**, 90.8 seconds. Full machine results are retained locally under `../output/bridges-and-crossings-70959/full-tests-final.json`.
- All **191 retained links pass both directions: 382 exact-connector checks**. The checks load water data and verify the target native floor or ground handoff with other graph links isolated, in addition to ordinary journey planning.
- All **3,367 retained precomputed walking paths** revalidate against their signatures and every segment after the final crossing rebuild. Expanded native re-probes verify all 80 emitted floor proofs, of which 65 are classified bridge placements; earlier ten-bridge and Southfury checks remain recorded separately.
- The representative Firm Ashenvale regression retains its 4,326.394-yard route, one path search and 185,600 cells. Twelve representative approach journeys pass, and Duskwood-to-Dun Morogh, transport selection, cold/warm path reuse, bridge following and recovery regressions remain green.
- Inventory, approach and shipped-data hashes match; generated reports reject stale evidence. ZIP integrity and inclusion of the full test guide are checked. `git diff --check` passes, with only repository line-ending notices.
- Local candidate: `dist/Mapperly-1.2.5.zip`. No commit, push, public release or live installation performed. Available-source implementation/audits are complete; unresolved native coverage and live acceptance remain explicit in the inventory and test guide.
## Dun Algaz, 26 November 2026

The Loch Modan–Wetlands road now includes four native tunnel passages, links 193–196. The full crossing rebuild preserved all 192 previous link records and their IDs. The approach audit verified dry ground on both sides of all four tunnels, and the runtime audit passed all 392 directional checks across the 196 bundled links. In-game confirmation on client build 71091 is pending. [Per-link test coordinates](testing-crossing-acceptance.md)
