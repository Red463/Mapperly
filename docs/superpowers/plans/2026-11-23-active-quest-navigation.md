# Active quest navigation

Approved scope: add Quests to Destinations, search the active quest log by name, select objective/turn-in destinations, and preview or navigate through the existing routing system. Do not change the navigation arrow. Full-catalogue search remains separate.

Data model: read native active quests without changing selected quest, header collapse or map. Native current quest pins are quest-level destinations; native next waypoints are separately labeled travel waypoints. Add standalone verified snapshot objective/turn-in positions from the existing SHA-pinned Forever SQL source, excluding ambiguous conditions, phased spawns and invented centroids. Label snapshot provenance and unavailable locations explicitly. Revalidate active quest and selected coordinates immediately before any route action.

Implementation:
1. Audit native APIs (read-only agent) and independently build/source-test bundled quest locations (data agent).
2. Add QuestNavigation.lua with guarded enumeration, plain-text search, objective progress matching where reliable, coordinate validation/projection, provenance, unavailable reasons and stale-selection validation. Test before implementation.
3. Add QuestNavigationUI.lua as a themed fourth tab. Search active quests, choose Locations, then Preview or Go. Match existing red actions, spacing and scrollable cards; preserve coordinate/saved/history flows and both themes. Refresh on quest events while visible, never change current navigation merely by searching.
4. Wire load order, validate data and UI integration, run independent review, complete regressions, update checklist and package preview.34. Do not publish or commit unrelated dirty work.

Native sources: extracted local QuestMapFrame.lua plus Forever branch QuestDataProvider.lua and generated QuestInfoSharedDocumentation.lua. GetNextWaypoint is not an objective NPC or turn-in API. The standalone SQL snapshot is public project data, not a guaranteed live realm export; retain its provenance and license.

## Outcome

Implemented QuestNavigation and QuestNavigationUI, standalone quest location generation and four-tab destination integration. Native failed-quest handling is covered by IsFailed regression; current pin x/y use the queried UI map like the native provider. Modern collapsed-header enumeration stays read-only; native UI applies collapse as a display filter. Abandonment, failure, completion and changed-location checks reject stale actions. All 69 suites pass, including seven builder cases; source archive/SQL hashes and deterministic generated Lua rebuild verified. Independent final review found no further substantive defects. Preview.34 ZIP CRC, TOC payload, source documentation, generator and license checked. Live acceptance instructions are in docs/testing-preview34.md.
