# Coordinate Navigation Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. No subagents are needed for implementation.

**Goal:** Enter map coordinates and follow a standalone smooth bearing/distance arrow.

**Architecture:** Navigation.lua owns target validation, world-space geometry, HUD state and smoothing. NavigationUI.lua owns coordinate entry. Map.lua only adds the rail action; Pins.lua renders the navigation marker independently of layer filters. Store.lua validates the saved HUD position.

**Tech Stack:** WoW Forever Lua, native frames, bundled HereBeDragons, existing GuideArrow texture.

**Spec:** ../../navigation-design.md

## Global constraints
- No runtime dependency on Gatherly; no changes to other addons.
- Input X/Y are percentages 0–100; arrival radius 10 yards.
- Direct bearing only; no invented cross-instance routing.
- Keep current location filters, notes and settings intact.

## Review focus
- Do not replace a valid target when new coordinates are invalid.
- Guard protected/nonfinite API values before arithmetic or comparisons.
- Preserve captured destination map when navigating the world map behind the input window.
- Reset stale bearing after unavailable position/facing and instance changes.
- A navigation marker must not disappear when the Notes layer is hidden.

## Tasks
- [x] 1. Add failing navigation tests for input and geometry; implement Navigation.lua, saved HUD position validation and bundled arrow art. Verify bearings, smoothing, waiting states, arrival and cancellation.
- [x] 2. Add failing UI tests; implement NavigationUI.lua, new rail button and independent destination pin. Verify input errors, map capture, button action and pin visibility under disabled category filters.
- [x] 3. Run regression suites, inspect the diff, document controls/limits, increment development version and verify the packaged files.

## Execution ledger
- Design recorded before implementation. Existing Gatherly arrow source inspected; world bearing uses HBD horizontal/vertical coordinates and the same facing convention. Workspace is a shared non-git addon folder; no commit/worktree operations apply. Reuse user-owned GuideArrow media under the existing MIT license.

- Geometry and UI tests reproduced the missing navigation feature before implementation, then passed. Integration tests reproduced the missing rail action before wiring it. Destination rendering and right-click cancellation now pass with all permanent location filters off.
- Final read-only review identified precision loss on editing. Added a failing test for 42.56 / 51.24, fixed editable formatting to 15 significant digits and reran both suites. Reviewer confirmed the finding resolved and found no remaining concrete blocker.
- Ruling: reuse the user-owned GuideArrow for both the new rail action and HUD rather than generate another compass, preserving the requested Gatherly-like appearance and avoiding a runtime dependency.
- Validation: python Mapperly/tests/navigation.py and python Mapperly/tests/run.py; packaged TOC/media/source checks. Native-client visual and movement checks remain for the user.
