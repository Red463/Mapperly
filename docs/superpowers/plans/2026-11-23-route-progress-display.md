# Route Progress Display Plan

User-requested scope: fade completed route geometry, add sparse unobtrusive direction chevrons, and display up to ten journey steps with the current one highlighted.

Use read-only authoritative Journey progress, never proximity to a later segment. Preview-only plans remain unfaded. Shared RouteStyle helpers apply identical completion colors on world/minimaps; split/native teleport gaps remain unjoined. Chevrons use pooled line pairs, fixed screen spacing and strict caps, skip completed segments and never overlap the minimap player-arrow gap. Refresh world-map progress only when follower indices change.

RouteSteps shows all legs for journeys of ten or fewer; longer journeys use a ten-row window containing the current leg, with absolute numbers. Completed rows are muted; only the current row is gold with a quiet background. Preserve collapse, position, themes, direct/planning state and small-screen fit.

- [x] Write RED progress/direction and ten-step tests.
- [x] Implement shared style and both map renderers, without changing routing/follower behavior.
- [x] Update step panel and existing assertions for changed requirements.
- [x] Verify tests, fresh review and package preview.17. Live visual acceptance remains pending.
