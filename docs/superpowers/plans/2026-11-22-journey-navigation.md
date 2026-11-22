# Journey Navigation Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task. Track progress in docs/navigation-checklist.md.

**Goal:** Build the terrain-aware walking foundation, then expand it into verified multi-modal journeys and quest navigation.

**Architecture:** Standalone geometry, cooperative jobs and journey state behind existing navigation entry points. Render and follow the same immutable successful plan; validation or planning failure preserves the last destination.

**Tech stack:** Lua 5.1, native WoW Forever frames, bundled HereBeDragons, generated terrain masks, Python/lupa tests.

**Spec:** docs/journey-navigation-design.md; feature ledger: docs/navigation-checklist.md.

## Global constraints

No runtime Gatherly dependency. Missing terrain stays blocked. Keep direct bearing explicit. Preserve saved notes/themes, native pings and diagnostic work. No publication in this task.

## Review focus

Blocked/unknown endpoints; cancellation while another route is active; narrow mandatory bends; screen/map coordinate transforms; slow searches must yield without starving frames.

## Task 1: Walking geometry and planning jobs

Files: Data/Terrain.lua, Terrain.lua, PlanningJob.lua, Journey.lua, tests/journey.py, Mapperly.toc.
Interfaces: Journey.Plan(start,goal,options) returns plan or reason. PlanningJob.Start(work,done,failed) and Step() coordinate cancellable jobs.
- [x] Write and run failing tests for blocked geometry, budget yielding, unavailable masks and cancellation.
- [x] Adapt owned Gatherly terrain data/pathfinding and implement local walking plans/jobs.
- [x] Verify production masks and transactional planning; update feature ledger.

## Task 2: Arrow follows the walking plan

Files: Navigation.lua, Journey.lua, tests/journey.py, tests/navigation.py.
Interfaces: Journey.Request(candidate,done,failed), Journey.Current(), Pause(), Resume(), Skip(), Update(position).
- [x] Write failing tests for bends, arrival, safe resume/skip and failed replacement.
- [x] Connect existing navigation entry points and preserve direct mode.
- [x] Run navigation/history/slash regressions; update ledger.

## Task 3: Walking route preview and settings

Files: JourneyView.lua, NavigationSettings.lua, Settings.lua, NavigationUI.lua, Store.lua, tests/journey_ui.py.
- [x] Write failing tests for a third settings page and map-line projection/cleanup.
- [x] Add a themed preview with steps/distance/time and guidance controls; render validated route geometry.
- [x] Run the complete suite, review the milestone, package a local preview and update ledger.

## Later tasks

Tasks 4-7 implement checklist 6-18 in separate data-backed stages: TravelNetwork and discovery; transport map links/preview; QuestSearch; Roads and reporting. Their exact interfaces will be written after the first walking milestone proves the shared plan contract. Data gaps remain explicitly unchecked in the feature ledger.

Milestone ledger: tasks 1-3 implementation/tests complete. Final review, provenance/package checks and local preview are the remaining milestone gates. Later feature groups are intentionally tracked separately in docs/navigation-checklist.md.
