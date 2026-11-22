# Mapperly journey navigation checklist

Status: implementation started, 22 November 2026. Branch: `feature/journey-navigation`.

## Feature checklist

- [x] 1. Bundle standalone terrain masks and validated walking pathfinding.
- [x] 2. Plan in bounded background jobs; handle unavailable/partial terrain explicitly.
- [x] 3. Draw route previews on zone/continent maps and the minimap.
- [x] 4. Follow terrain bends with the arrow; pause, resume and skip safely.
- [x] 5. Add a dedicated Navigation settings tab with Smart routing (default on) and display toggles.
- [ ] 6. Recalculate after meaningful deviations, with throttling and cancellation.
- [ ] 7. Connect walking routes across verified zone exits.
- [ ] 8. Route using boats, zeppelins and airships.
- [ ] 9. Route using faction-appropriate discovered flight paths.
- [ ] 10. Add verified tram and lift connections.
- [ ] 11. Show selectable transport links and destinations on continent maps.
- [ ] 12. Preview journey steps, approximate times, distance and flight costs.
- [ ] 13. Search active quests and select objective/turn-in destinations.
- [ ] 14. Research/bundle reliable locations for quests not currently accepted.
- [ ] 15. Add road-preference routing backed by actual road data.
- [ ] 16. Add swimming and per-transport preferences with availability explanations.
- [ ] 17. Navigate to nearest reachable bundled services.
- [ ] 18. Export route-problem reports and retain resumable journey state.
- [ ] 19. Final integration: verify all features, performance and package a release candidate.

## Milestones

1. Walking foundation: 1-5 and the walking portion of 12. First playable preview.
2. Connected journeys: 6-12, transport preferences and discovery tracking.
3. Destinations: 13-18, using verified datasets rather than invented coordinates.
4. Integration: 19 and live-client acceptance of terrain/transport transitions.

## Decisions and limits

- Quest search begins with the player's active quest log. Full-catalogue search is a separate data-backed feature.
- Reuse our Gatherly terrain algorithm/data independently; neither addon becomes required by the other.
- Unknown terrain stays blocked. A terrain-estimated path is not a collision guarantee.
- No fabricated road tags, discovered flights, timetable precision or transport links.
- Retain explicit direct-bearing mode. Never silently substitute it for a failed walking route.
- Planning failure keeps the previous successful destination/history intact.
- Preserve the pending ultrawide diagnostic tools and existing public 1.1 behavior.
- No GitHub publication until requested.

## Progress ledger

- 2026-11-22: Inspected Gatherly's masks/pathfinder, Mapperly navigation/settings and bundled transport data. Created feature branch and this checklist. Next: terrain routing and cooperative planning tests.

- 2026-11-22: Completed features 1-2. Bundled 55 terrain masks with provenance; added validated local walking plans and cancellable frame-budgeted jobs. `python tests/journey.py` verifies ridge detours, every segment, blocked endpoints, missing coverage, cancellation and mask inventory. Next: arrow following and safe pause/resume/skip.

- 2026-11-22: Arrow/follower core completed and verified through actual Navigation.Start/Tick entry points. Planning commits history only after success; mandatory bends are followed, pause/resume/skip are validated, cancellation drops stale work and explicit direct mode remains. Controls will be exposed in the next preview UI task. Next: map lines, preview window and Navigation settings tab.

- 2026-11-22: Completed map-line previews and dedicated Navigation settings. Walking preview includes approximate distance/time, Start/Pause/Resume/Skip/Replan/Stop. Root UI regression now loads the actual production TOC order. Thirteen automated suites pass; fresh-context walking milestone review is running. Features 6-18 remain unchecked.

- 2026-11-22: Fresh review found three important state bugs (arrival cancelling replacement; walking preview obeying direct-mode preference; stale active preview after Replan). Reproduced each RED and fixed together. All regressions now pass. Walking preview version: 1.2.0-preview.1. Remaining next milestone: features 6-12, cross-zone and transport journeys.

- 2026-11-22: First walking milestone packaged and verified as an installable local preview. Thirteen suites pass, with real TOC load order and all 55 mask records checked. Fresh review findings fixed; live-client acceptance remains required. No public release or GitHub push.

- 2026-11-22: Screenshot follow-up, preview.2: reproduced the Elwynn coordinates (about 1,397 yd; one local planning step). Corrected route art-layer ordering and stale pending status. Added actual OnUpdate completion tests, guarded clocks and visible display-error reporting. Core roadmap remains unchanged; cross-zone/transport work is next.

- 2026-11-22: Preview.3 live-client follow-up: restricted player cells no longer suspend existing guidance. Route and waypoint remain intact, with resume/skip/arrival available; return to permitted terrain restores segment checks. RED/GREEN follower and actual HUD tests cover the behavior. Automatic recalculation must preserve this rule in the next milestone.

- 2026-11-22: Preview.4 completes minimap route display and live Smart routing switching. Minimap checks cover HBD axes, rotation/ignored rotation, zoom, clipping and the native arrow gap. Direct mode now renders straight lines on both maps, previews without terrain work and preserves the destination through mode changes. Fresh review found and fixed a frozen active-direct view; regression added. Cross-zone/transport/quest/road work remains next.
