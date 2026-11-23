# Planning feedback

The approved change adds generation feedback for far destinations, especially Alt-right-click while the map obscures the low-strata navigation HUD.

- [x] Add identity-bound PlanningJob telemetry: stages, actual path count and terrain expansion activity. Never claim a completion percentage or ETA.
- [x] Add a themed nonmodal status panel above the map, also visible with the map closed. Include destination, live stage/elapsed/activity and Cancel. Show success briefly and failure persistently until dismissed.
- [x] Bind manual Navigation and walking previews; don't interrupt automatic-replan HUD guidance with panels. Reject stale callbacks. Cancel only the owned calculation, preserving the active route/destination. Invalid new clicks must not conceal an existing calculation.
- [x] Test real Alt-right-click pending/success/unsupported-route behavior and cancellation, plus stale callback identity and preview/UI regressions.
- [x] Run full suite/review, update docs and package local preview.9. No publication.

Validation: all 20 suites pass. Actual Alt-right-click tests cover immediate status, completion, unsupported far-zone failure and cancellation preserving a real active route. Fresh review finding about rejected manual clicks during silent automatic jobs reproduced RED and fixed. Installable preview.9 ZIP integrity and source/module bytes verified. Live-client visual acceptance remains needed.
