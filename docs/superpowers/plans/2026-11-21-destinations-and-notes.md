# Destinations and Notes Implementation Plan

> Use superpowers:executing-plans inline, with one final fresh review.

Goal: Ctrl-click navigation, quick map waypoints, persistent saved/recent destinations and an editable note window matching Settings.
Architecture: Store validates persistent records; Destinations owns favorites/history; Navigation owns the active session target. Dialogs shares charcoal window/card controls. NotesUI and NavigationUI own their windows. MapInteractions registers native high-priority canvas/pin handlers without replacing other addons' scripts.
Spec: the user's four requested additions and accepted Ctrl-click preference.

## Constraints
- Preserve existing ordinary marker clicks, Alt-click notes and bare-map right-click navigation.
- Ctrl-left-click any map position places a waypoint immediately, with no dialog. Native pin handlers use the hovered marker's exact normalized coordinates when available.
- Saved destinations persist; history stores the latest 20 unique successful destinations. Explicit save/delete/clear actions; no external addon data dependency.
- Notes retain old records; edit name, description, icon and optional group. Right-click deletion and Shift-click sharing remain.
- Capture map IDs in all editors. Reject invalid input without replacing valid navigation or mutating an existing note.
- Reuse existing painted icons. Match Settings charcoal cards, gold headings and shared flat buttons; windows fit small screens.

## Tasks
- [x] 1. RED: data tests for records, migration, dedup/caps and note editing. Implement Destinations and note storage methods; connect successful navigation to history. Run navigation/data tests.
- [x] 2. RED: UI tests for Saved/Recent actions and notes validation/editing. Implement shared dialogs and both windows. Update obsolete popup regression checks and run UI tests.
- [x] 3. RED: click/pin tests. Implement Ctrl-click handlers before default map navigation, marker actions and note icon/tooltips. Run all suites, fresh review, document controls, build and verify local 1.1.0 ZIP.

Review focus: corrupt saved data, stale editor targets, coordinate precision, native pin click propagation, optional addon compatibility and bounded UI layouts. This is a local build; do not publish.

## Execution ledger
- Existing uncommitted 1.0.1-1.0.4 work preserved on feature/destinations-and-notes.
- Interfaces checked: persistent record normalized x/y; Navigation.Start consumes percentage x/y. Convert only at the boundary.

- Task 1 complete: destinations.py RED -> GREEN; navigation.py green. Invalid persisted records are discarded; note identity is retained.
- Task 2 complete: destination_ui.py RED -> GREEN; obsolete static-popup tests replaced with note editor behavior.
- Task 3 interactions complete: map_interactions.py RED -> GREEN, main regression suite green. Native pin events bypass the raw-button fallback to avoid rebuilding a clicked pin before its normal handler.

- Final fresh review: three Important findings plus sparse-array data loss corrected. Native pin overrides now have a deferred, deduplicated fallback; saved edits update by identity; malformed note fields/categories recover; sparse records survive loading.
- Final fixes: map_interactions.py and destination_ui.py RED -> GREEN; destinations.py reproduces malformed note categories and covers sparse arrays and stale updates. All six test commands pass after the fixes.
- Final minor (deferred): string length limits slice bytes, so unusually long multibyte note text can be cut mid-character. Standard English notes are unaffected; UTF-8-aware limits remain future polish.
- Local package: 1.1.0; TOC modules and ZIP bytes checked against the working source. No GitHub publication or push.
