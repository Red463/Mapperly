# Nearest services implementation plan

> **For agentic workers:** Use superpowers:executing-plans for inline work; request one final independent review.

**Goal:** Add a themed Services tab to Destinations for finding a nearest verified reachable inn, mailbox, flight master or dungeon entrance, with Preview and Go.

**Approved scope:** User said proceed after the nearest-service recommendation. Ruling: shortest walking distance under current road settings is the default, rather than transport time; the user explicitly confirmed shortest walking route in the asynchronous reply. No new map assets or third-party data dependency.

**Architecture:** NearestServices.lua projects bundled and observed services through verified world-map geometry, filters faction access, deduplicates positions and finds nearby permitted approaches. A bounded cooperative search sorts candidates by same-instance Euclidean lower bound, evaluates walking-only journeys and stops when remaining lower bounds cannot beat the best calculated route. Budget-limited candidates and search caps must yield an explicitly partial result. NearestServicesUI.lua adds an existing-style tab with category buttons, progress, result details, Preview and Go. Activation revalidates source/access; previews replan from current position on Start. Walking-only intent persists through recovery and routing setting changes.

**Constraints:** No invented services or flight unlocks; hidden marker layers do not hide services from search. Unknown faction access is excluded. No current destination/history change during search, preview, cancellation or failure. Existing coordinate/saved/recent/quest actions and both themes remain intact. Same algorithms, masks, road strengths and bounded caches as preview.39; do not change Terrain.lua.

## Tasks
- [x] Add failing model tests for world projection, access, deduplication, longer-but-reachable candidates, cross-zone bounds, search budget uncertainty, approaches and cancellation.
- [x] Implement candidate projection and bounded asynchronous nearest-walking search with result provenance and source revalidation.
- [x] Thread walking-only intent through Journey/Navigation/preview lifecycle; test that methods remain available for ordinary navigation.
- [x] Add Services tab using existing dialogs and marker icons. Show exact service coordinates, actual route distance, nearby approach/manual-access notice and complete/partial status. Preserve all existing tabs within the window width.
- [x] Add actual native data regression and UI tests; run all suites, independent review, document preview.40, package and verify ZIP.

## Verification focus
Faction changes and removed observations invalidate stale result actions. Changed player position invalidates old route reuse on Go. Background search is cancelable and cannot overwrite newer jobs. Failed/capped candidates cannot be called proven nearest. Source blocked cells can use only a marked permitted approach within30yd. Same-instance world distance is the lower bound on walking routes; disconnected instances are excluded.


## Execution ledger
- Added four categories to a fifth Destinations tab with reused theme components/marker art; no new assets or external data.
- Native Darkshire uses1route per inn/mailbox/flight result, 1,280-1,536 reported cells. Prefer the current map's representation of exact world positions to avoid overlapping Deadwind artwork assigning Darkshire a gratuitous crossing.
- Independent review found stale service actions could follow direct mode and native flight handoffs could be mislabeled exact NPCs. Resolve now rejects old actions in direct mode; exact node.world/eligibility/manual handoffs are retained, and approaches beyond30yd rejected. Actual AeriePeak52.62yd and source-only FreewindPost regressions pass.
- Walking-only intent is tested through actual ToPin/Start/Request, manual replan, Smart/road transitions and preview Start. Ordinary destinations retain transport support.

- Final verification:84 suites pass; native/source/model/routing/UI/lifecycle regressions pass, independent review has no remaining findings. A cleared preview Start is harmless. Preview.40 package payload and integrity verified.
