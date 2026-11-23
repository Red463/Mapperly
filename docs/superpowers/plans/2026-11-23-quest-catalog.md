# Quest search beyond the active log

User approved extending quest search to quests not accepted yet, with quest names, starting locations and availability checks (level, faction, prerequisites and completed history).

Keep Active as the default scope within the existing Quests tab; add Find quests as a separate choice. Search the pinned Forever catalogue by plain name or ID, limit broad result lists and explain missing starter locations. Catalogue titles and locations come from the independent snapshot; never import Questie data or promise live realm availability.

Availability is three-state: known restrictions, possible pickup (known checks pass), or unconfirmed (required live data/additional conditions cannot be evaluated). Read character completion/active status, level, race/class and verified prerequisite/exclusive rules; never infer unknown conditions are satisfied. Completed nonrepeatable and currently active quests cannot start catalogue pickup routing. Repeatable, unsupported skill/reputation/condition checks remain explicitly unconfirmed unless reliable live evidence exists.

Tasks:
1. Independently audit/build full named quest metadata and conservative exact starter spawns from the existing SHA-pinned Forever SQL (data agent; owned new files).
2. Add QuestCatalog.lua with bounded search, three-state availability, source-backed starter projection and stale selection checks. Reuse quest approach routing, normal Preview/Go and preview Start validation. Test before implementation.
3. Add Active / Find quests scope choices and status explanations in the current themed page; preserve all active quest behavior and existing destination tabs. Throttle catalogue typing and bound result rendering.
4. Review, regenerate/verify data, run complete regressions, update checklist/docs and package preview.36. No GitHub publication requested.

## Verified result

Implemented catalogue model, Active/Find quests choices, source-backed pickup projection and reused stale/approach routing guards. Generated48,793names,4,123starters for3,702quests, exact raceID mapping and sorted searchOrder. Independent review reproduced reverse breadcrumb false-possible state1840?1844; added source-backed transitive IDs plus runtime active-state blocking and explicit uncertainty. Missing character IDs stay unknown. First-search index work fell from262ms to73ms on host, subsequent samples under7ms. All73suites pass, including14builder tests; archive/world/hotfix/faction hashes and deterministic generated-data SHA verified. Final review found no further substantive findings. Preview.36 CRC, allTOC entries, generated source/generator/tests/license and updated docs verified. Live test instructions: docs/testing-preview36.md.
