# Verified tram and lift navigation

Implement checklist item 10 using build 70959 native evidence. Preserve existing walking, scheduled passenger and discovered-flight behavior.

1. Audit Deeprun Tram and Great Lift independently. Record native identities, floor heights, instance transitions and reachable access points. Do not publish an invented connector through unsupported indoor geometry.
2. Add separate saved tram/lift preferences, enabled by default, and clear typed journey labels and icons.
3. Add floor-aware manual boarding/arrival handling. A lift's identical horizontal coordinates must not immediately complete its leg; protected or missing position must preserve guidance and allow explicit confirmation only at a supported exit.
4. Bundle only connections with verified access in both directions. Document excluded services and exact blockers.
5. Run transport, journey, settings and existing regression suites; independently review the milestone and package preview.25 after verification.

Acceptance: turning either method off excludes it from plans; loading and vertical motion retain the active journey; the HUD describes the current method; settings remain within their existing window bounds. Native data validation and an installable preview accompany the completed scope. Live-client boarding remains an explicit acceptance check.

## Outcome

Great Lift manual access is implemented in both directions with a native-proof builder and floor-aware follower. Separate method preferences and typed labels are present; unverified trams are visibly disabled with an explanation. All 50 automated suites pass, including three new suites. Independent review found no important reproducible defects and planned both directions between native approach anchors (about 489.55 yards walking).

Tram enablement remains blocked on verified station pairing and floor/access evidence; the native audit is in `output/tram-audit`. Other capital elevators remain outside this preview. Roadmap item 10 stays partially open. Live-client acceptance of Great Lift boarding, vertical motion, disembarking and protected-height confirmation is still required.
