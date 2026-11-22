# Journey navigation design

Build a standalone journey engine behind the existing coordinate, marker and slash-command interfaces. The first milestone plans local walking paths from bundled Forever terrain masks; later milestones connect validated local paths through a directed network of zone crossings and transport edges.

A plan is a sequence of typed legs with geometry, approximate time/distance, source/coverage and availability information. The HUD follows the current leg instead of always pointing directly at the destination. Map lines and the preview window render the same plan. Pause/resume/skip/replan operate on this shared state.

Routing runs as cancellable coroutine jobs with frame work budgets. A successful request atomically installs its destination and history; failures preserve the old active destination. Terrain failures are reported instead of silently creating straight-line walking routes. Direct-bearing navigation remains an explicit user choice.

Use separate modules: Terrain (validated local geometry), PlanningJob (cooperative work), Journey (plan and follower), JourneyView (map lines/preview), NavigationSettings (preferences), TravelNetwork (directed transports/zone crossings), QuestSearch (quest-to-destination adapter), Roads (verified road metadata), JourneyReport (export). Reuse owned Gatherly terrain code/data with provenance. Do not copy Shortest Path Forever code.

The Navigation settings tab will contain route mode, guidance visibility, recalculation and road/swimming/transport preferences as their backing features become available. Do not show functional-looking toggles for unsupported data.

Quest scope begins with active quests. A later bundled catalogue must identify source, objective/turn-in ambiguity and coverage. Transport times are approximate without observed schedules; unknown flights are excluded until discovered or explicitly confirmed.

Player movement may leave the terrain mask without stopping an installed journey. Restricted player cells preserve the current route/waypoint and permit manual resume, skip and normal arrival advancement. This does not make restricted cells valid planning endpoints or rewrite any planned segment. Missing/protected positions and another zone still pause directional guidance.
