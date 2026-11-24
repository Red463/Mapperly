# Clean overview travel connections

**Goal:** Replace the scraggly optional overview network with clean curves and make it default off, as requested.

**Design:** Use subtle blue schematic arcs with a narrow dark underlay, deduplicate reverse/duplicate connections and cap complete curves. Active journey lines and explicit marker previews remain separately controlled and retain their native geometry/gap handling. For a continent with only part of a cross-continent sailing path visible, curve each visible native piece separately; never join projection gaps. The new toggle is named Show travel connections and has an explanatory tooltip.

**Migration ruling:** The old network defaulted on, so switch it off once for existing installations too using a display-version marker. Subsequent deliberate on/off choices persist. Keep routing preferences and active journey settings unchanged.

**Implementation:** Store.lua initializes/migrates the toggle; BoatLinks.lua draws schematic background connections independently of active/hover lines; NavigationSettings.lua exposes the clearer setting. Continue in the current working checkout to retain preceding local fixes; no publish or client writes.

- [x] Add failing tests for new/legacy defaults, saved opt-in persistence, smooth complete arcs, reverse deduplication, native-piece gaps and toggle behavior. Observed RED: new installs defaulted on.
- [x] Implement scoped rendering/default/settings changes.
- [x] Verify connection, transport, UI, map, combat and prior-feature regressions; document schematic semantics and the one-time migration. All 15 focused suites pass. Independent focused review found no important actionable defects and reran the style/native-piece suites successfully.
- [x] Package and verify a local installable ZIP. CRC, runtime manifest, current travel/fishing/combat files, test guide and diagnostic exclusion verified. Post-generation announcement and release-note checks also pass.
