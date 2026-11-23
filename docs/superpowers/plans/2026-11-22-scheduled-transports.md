# Scheduled Transport Journeys Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task by task, with one fresh review at the end. The existing journey design and the user's instruction to proceed authorize this milestone.

**Goal:** Extend smart journeys with verified boats, zeppelins and airships, preserving all existing walking behavior and explicit direct mode.

**Architecture:** A transport adapter owns directed native stops, dry land approaches, availability and transit instructions. TravelNetwork combines those edges with existing walking crossings under one bounded search. Journey follows typed walking/transport legs; transport legs wait for an observed arrival and never tell the player to walk across the sea.

**Tech Stack:** WoW Lua 5.1, native build 70959 tables, existing MIT OpenMap metadata, Python generation and Lua regression harness.

**Spec:** `docs/journey-navigation-design.md`, roadmap features 8 and the related portions of 12/16. Selectable continent links and discovered flight paths remain following milestones.

## Constraints and rulings

- No other addon is required; no Shortest Path Forever implementation is copied.
- Keep the current isolated feature branch and all pending walking/diagnostic work. Do not publish.
- Native stop order defines directed edges, including circular multi-stop routes. Do not assume every route is bidirectional.
- A dry shore approach is a walking endpoint. The final pier/boarding action is explicitly manual where native floor geometry is not certified; do not erase terrain restrictions.
- Faction routing policy is conservative and distinguished from physical boarding restrictions. Unknown policy routes remain unavailable by default.
- Journey costs use walking time plus approximate transport time/wait. Never present a live countdown or exact schedule without observations.
- No automatic boat-control or invented onboard API. While waiting/travelling, retain instructions through missing/protected positions; advance only near the actual destination stop on the correct instance.
- Pause, stop, replacement, cancellation and preference changes retain existing transactional guarantees. Recovery cannot replan a sea crossing as walking.

## Review focus

- Cross-continent loading screens cannot clear the route or create a directional sea shortcut.
- A same-continent ferry must not complete while still at the departure dock.
- Reverse/circular sailing order, faction unknown and disabled travel modes cannot silently add a prohibited edge.
- Transport points must not be mistaken for contiguous walking geometry in the HUD, minimap or recovery.
- New transport searches must preserve short local walking routes and remain bounded on far requests.

## Task checklist

### 1. Native transport data and adapter
- [x] Audit TaxiPath/TaxiPathNode and native stops; record source IDs, directed order, map assignments, timing evidence, faction policy and unsupported approaches.
- [x] Write failing `tests/transports.py` for directed edges, source/build guards, safe approaches and preferences; implement `Transports.Edges(options)` and minimum estimated edge cost.
- [x] Generate `Data/Transports.lua` reproducibly with `tools/build_transports.py`; add provenance and TOC ordering. Retain unsupported links in the audit.

### 2. Mixed planner
- [x] Add RED synthetic cross-continent, same-continent ferry, disabled transport, wrong faction and cancellation tests.
- [x] Extend TravelNetwork graph edges and plan assembly to typed transport legs, approximate time cost and walking-only distance. Use an admissible capped heuristic for mixed graphs; preserve existing short/direct walking fast paths.
- [x] Verify real native route planning and walking regressions with the shared search bounds.

### 3. Boarding and arrival follower
- [x] Add RED tests for shore approach, boarding instructions, departure, missing position, wrong dock, same-map arrival, reverse travel, pause/resume and stop.
- [x] Add typed-leg state transitions to Journey and transport HUD instructions. Disable bend skipping/recovery inside transport legs and retain the route through loading screens.
- [x] Verify actual Navigation.Start/Tick behavior, not only pure follower methods.

### 4. Settings and preview
- [x] Add tested saved boat/zeppelin/airship preferences; changes replan the active smart destination transactionally and cancel stale previews.
- [x] Fit controls into Navigation settings using the existing theme. Explain transport estimates and manual boarding clearly.
- [x] Preview lists walking, boarding/travel and disembarking steps with approximate total time. Map/minimap lines distinguish native transport geometry and omit unsupported cross-instance joins.

### 5. Review and preview
- [x] Run all existing suites plus native transport/planner/follower/UI regressions; obtain a fresh code review and fix important findings.
- [x] Update roadmap/checklist/changelog and package preview.12; verify archive content against TOC. No GitHub push or public release.

## Verification ledger

- All 32 suites pass. Native plans include both Zephras services, a same-vessel through sailing, real Ratchet/Booty Bay and Stormwind/Auberdine town approaches, and the existing Duskwood/Dun Morogh walk.
- Fresh review found the deferred-destination race; reproduced RED and fixed both target selectors. Final targeted review passed.
- Town-region audit corrected Booty Bay, Dalaran and Stormwind handoffs; no walking permissions were added.
- Ruling: retain bounded short-zone-itinerary-first search, then unrestricted fallback; pure cost-first exhausted the existing budget on the legacy Duskwood/Dun Morogh case. Global fastest-route claims remain excluded.
- Preview.12 package CRC and all TOC file bytes verified; six walking datasets unchanged from preview.11. No publication. Live game acceptance remains pending.
