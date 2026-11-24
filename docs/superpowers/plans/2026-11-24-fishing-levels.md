# Fishing levels implementation plan

**Goal:** Show both fishing minimum and recommended skill beneath the quest-level heading, as requested and confirmed by the user.

**Design:** Bundle published Forever reference facts by map ID, independent of other addons. Label the source and uncertainty on hover. Include ranges for documented special waters. Unknown zones and overview maps have no fishing row. Keep both themes readable and move the native subzone caption down when needed. The label does not query auras, tracking settings or server requirements.

**Architecture:** Data/FishingLevels.lua stores facts and provenance; FishingLevels.lua handles formatting, the small mouse-motion-only tooltip surface and placement. Shell refreshes it alongside the existing heading, Theme repositions it, and ZoneLevels reserves space for it.

**Scope ruling:** Continue in the existing working checkout so the preceding local 1.2.4 fixes and announcement work are preserved in the installable build. No push, release or client-directory writes.

- [x] Add failing tests for both values, mixed waters, cities, unknown/overview maps, themes, tooltip and subzone spacing. Observed RED: missing FishingRange.
- [x] Implement the bundled reference table and fishing label; integrate existing refresh paths.
- [x] Verify focused map/theme/combat and announcement tests; record source limitations and testing instructions. All 11 focused suites pass; underlying run.py also compiles all Lua and verifies assets.
- [x] Build and verify the local ZIP, retaining the preceding fixes. CRC, TOC entries, packaged fishing data/UI, prior fixes and diagnostic exclusion verified.

**Ruling:** Determine native caption spacing from the current map ID rather than the fishing frame's previous visibility, so an overview transition cannot reserve a stale extra row.
