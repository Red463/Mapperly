# Route recovery plan

Implement the approved detour/rejoin behavior, preserving the destination and previous guidance until replacement succeeds.

- [x] Add deterministic tracker tests: forward segment projection, sustained proximity, ambiguous crossings, blocked connectors, invalid/restricted positions and pause handling.
- [x] Add RouteRecovery.lua after Journey.lua: evaluate every 0.5 seconds; rejoin a unique later segment within 12 yards for 2 seconds only when over 18 yards from current segment. Require walkable player-to-projection and player-to-next-turn connections. Reset streaks on ambiguity. Never go backwards.
- [x] Request replanning after 3 seconds over 30 yards off all remaining route segments; throttle attempts to 10 seconds. Missing/blocked player cells do not trigger replans or halt guidance. Use existing cooperative jobs and saved road preference.
- [x] Integrate automatic job ownership: never interrupt manual requests/previews; cancel automatic work on pause, stop, new destination or successful forward rejoin. Failed requests preserve current journey; arrival cancels automatic same-goal requests.
- [x] Verify integration tests for success/failure/cancellation, rerun all suites, update checklist/docs and package preview.7. No GitHub publication.

Route recovery does not introduce new user-facing settings; it is part of Smart routing. Direct mode remains unchanged. Map/remaining-line rendering already follows Journey.index.

Validation: 17 suites pass. ZIP integrity and module/TOC bytes verified. Review reproduced an adjacent hairpin ambiguity; regression added and fixed. Additional RED/GREEN cases cover current-leg return cancelling work and continuous proximity around a turn. Preview.7 is local and requires in-game acceptance.
