# Stormwind Flight Handoff Bugfix

User report: Southshore to Goldshire selects Sentinel Hill instead of the closer Stormwind flight.

Reproduced with actual native flight geometry, walking regions and city exit data. With both offered itineraries, old data selects Sentinel Hill (1,957 yd walking / 762 estimated seconds). Stormwind alone fails the bounded search. Its landing handoff uses region 36; the existing Elwynn exit uses region 52. Local Terrain.Path confirms they are disconnected. Exact native pad XY already lies on region 52 and has a 281.45-yard permitted path to the exit. The initial extraction assumption that region 52 was a detached roof fragment was incorrect.

Fix only the pinned Stormwind runtime handoff to exact native pad XY/Z with manual platform access. Preserve all terrain permissions, native flight geometry, fares, offers and routing behavior. Add source connection proof, generator validation against the existing city exit and a complete native journey regression. Correct result: Stormwind, 842 yd walking / 530 estimated seconds; Sentinel Hill remains available if Stormwind was not observed.

- [x] Reproduce actual route choice and isolate failed local connectivity.
- [x] Correct pinned node 2 approach; regenerate native runtime data.
- [x] Add native comparison and build-time exit-component checks.
- [x] Run flight/walking regressions, independent review and package preview.18.
