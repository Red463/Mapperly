# Quest log Navigate to action

Extend Forever's native MENU_QUEST_MAP_LOG_TITLE through Menu.ModifyMenu; preserve Track, Share, Abandon and other addons' entries. Native source QuestMapFrame.lua2367 uses this tag with the quest button owner carrying questID. User waypoint menus reuse the tag, so only act on a validated active quest owner.

One known location: Navigate to starts existing quest navigation directly. Multiple locations: a scrollable submenu lets the player choose an objective/turn-in/travel waypoint. No known position: disabled Navigate to with an explanatory tooltip. Capture each selected quest/location rather than reading recycled row state at click time, and revalidate with RouteTarget before routing. Preserve nearby approaches, flight deferral and existing routes on failure. Install once when Menu API is present, retry at addon load/login for late native loading.

Add lifecycle/menu/action regressions, run review and all checks, package preview.37. No native function replacement, quest selection/header mutation or GitHub publication.

Verified result: native menu callback and scrollable element APIs checked against Forever Menu.lua. Targeted regression preserves existing entries, tests single/multiple/unavailable locations, recycled owner identity, stale quest clicks, nonquest/invalid owners and late registration exactly once. Independent review found no substantive defects. All74suites pass. Preview.37 ZIP CRC and allTOC source files plus updated documentation verified. Live acceptance guide: docs/testing-preview37.md.
