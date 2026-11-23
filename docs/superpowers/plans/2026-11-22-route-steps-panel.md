# On-screen Route Steps Implementation Plan

> Execute inline with superpowers:executing-plans. Existing feature branch and user request authorize this focused addition.

**Goal:** Show the current route instruction and the next three journey legs while playing, without opening the map.

**Design:** A compact movable panel follows the selected Mapperly theme, highlights the current step, shows live transport/paused/replanning status, and lists upcoming leg names. The destination stays visible. A collapse button reduces obstruction; close hides the panel via a saved Navigation setting. Save its position and collapsed state. Show only during active/pending navigation; direct mode explicitly shows direct guidance. Read existing journey state without advancing progress or requesting routes.

**Architecture:** New RouteSteps.lua owns read-only presentation and a throttled refresh driver. Store.lua supplies preferences and validated anchor migration. NavigationSettings.lua exposes visibility. TOC loads after Dialogs. Use the current plan's legIndex, with a local-plan fallback, never infer completed steps from map position.

- [x] RED tests for current/upcoming legs, progress, pause/transport/replanning, direct mode, stop, close/toggle, collapse and saved placement.
- [x] Implement panel, settings and persistence; preserve existing navigation behavior.
- [x] Run focused and existing navigation/theme tests; request fresh review.
- [x] Document and package preview.14; verify archive and TOC. Live rendering remains pending.
