# Standalone quest catalog snapshot

`QuestCatalog.lua` contains **48,793 named quests**, including quests without a verified pickup location. **3,702 quests have 4,123 verified SQL starter-position records** after conservative filtering. It does not use Questie, another addon's globals, guessed drops, runtime downloads, or a live database. Titles are English `quest_template.LogTitle` values. Eight unnamed rows are omitted.

This is a public development snapshot, **not an authoritative export of the current live realm**. Its templates include older, newer, disabled and otherwise inaccessible content. A named result is not a promise that the quest can currently be accepted. Even a result that passes modeled player checks should be described as a possible pickup, because live realm configuration and script behavior can differ.

## Pinned inputs and license

- Project: [Karrz1/TrinityCore, Forever](https://github.com/Karrz1/TrinityCore/tree/forever).
- Release: [Forever TDB 2026-10-14](https://github.com/Karrz1/TrinityCore/releases/tag/forever-tdb-2026-10-14).
- Archive: [`TDB_full_forever_2026_10_14.7z`](https://github.com/Karrz1/TrinityCore/releases/download/forever-tdb-2026-10-14/TDB_full_forever_2026_10_14.7z).
- Archive SHA-256: `373cdca7963927d4d67933032b4b858a811eae0af960d4de4ff19833a88d4f41`.
- World SQL: `TDB_full_world_forever_2026_10_14.sql`; SHA-256 `3357f62451dcdef27123243c83c76a1a2e3251cf730aea01abf2f7f3d776d341`.
- Hotfix SQL: `TDB_full_hotfixes_forever_2026_10_14.sql`; SHA-256 `315e4b3bd2e2a0308f0fc5e746381e8733fe1d66b804b227b62f420681dcd36c`.
- Faction input: local Forever 1.60.1.70959 `tools/data/factiontemplate-70959.csv`; SHA-256 `963a24a4a32acd76dea04ac337e037f45d72e2c6a403e3826dfcfc95e28b746d`.
- SQL data copyright TrinityCore contributors, GPL version 2. Include the existing `Libs/Forever-Services-COPYING.txt` license when redistributing. These notes and the builder identify the source and modifications; keep them with the generated data.

All four hashes are verified before building. The builder uses the existing audited cache under `assets/services-source`; it does not download a replacement. Release packages should include the generated Lua, source notes, builder, tests and existing license/faction CSV, and exclude the large SQL/archive cache.

## Actual schema audit

The world snapshot has 48,801 `quest_template` rows, 16,294 `quest_template_addon` rows, 4,753 `quest_classic_level` rows, 4,757 `quest_template_classic_level` rows, 4,092 `creature_queststarter` relations, 266 `gameobject_queststarter` relations 20,962 `conditions` rows, 2,383 `spawn_group` memberships and 910 `spawn_group_template` rows. The builder joins by the actual declared column names, not fixed tuple positions.

There is **no `quest_chain` or `item_template` table** in this snapshot. `quest_template` has `ContentTuningID`, rather than legacy `QuestLevel`/`MinLevel` columns. The hotfix snapshot has 5,291 `item_sparse` records and only three `content_tuning` overrides. Those overrides do not constitute the client's entire content-tuning database. The two nonzero `item_sparse.StartQuestID` links identify one named quest in the catalog; they become `startItemIDs`, without any invented item drop, vendor or pickup position. Missing item links do not prove an item starter does not exist.

The audited server behavior is pinned for reference to [Forever commit 25be61f58f48b6e7bc8eda1146af8e1c73c82470](https://github.com/Karrz1/TrinityCore/tree/25be61f58f48b6e7bc8eda1146af8e1c73c82470), read on 2026-11-23. This source audit establishes field meanings; it does not establish that the public SQL and live realm run identical code/configuration.

## Availability field contract

The root is `A.QuestCatalogData={version=1,source="Forever TDB 2026-10-14",quests={...}}`. The top-level `searchOrder` array contains every named quest ID exactly once, sorted by `(title.lower(), ID)` during generation so the UI need not sort the full catalog on first search. It duplicates only IDs, not titles. Quests are keyed by numeric ID. Each quest always has `title` and `starters` (possibly empty). Zero-valued optional fields are omitted.

- `level`: positive `quest_template_classic_level.QuestLevel`, the fixed display level. This is not the acceptance threshold.
- `minLevel`: positive `quest_classic_level.MinLevel`. `Player::GetQuestMinLevel` explicitly prefers this fixed classic minimum. No minimum is invented from a missing or partial content-tuning record.
- `maxLevel`: `quest_template_addon.MaxLevel`, overridden by nonzero `quest_classic_level.MaxLevel`, matching `Quest::SetClassicLevelRange`. `Player::SatisfyQuestMaxLevel` rejects players above this value. It is an acceptance ceiling, not an inferred scaling cap.
- `raceIDs`: exact allowed native race IDs, decoded using the server's `RaceMask::GetRaceBit` mapping. In particular Skyborne race IDs 95/96 use bits 32/33; several other race IDs are remapped too. Python exact integers prevent uint64 mask precision loss in Lua. Zero and the full uint64 mask are unrestricted and omitted. Unknown/reserved bits do not create invented race IDs.
- `classIDs`: exact class IDs decoded from `quest_template_addon.AllowableClasses`, omitting unrestricted masks.
- `prevQuestID`: direct signed prerequisite. Positive means the predecessor must have been rewarded. Negative requires the predecessor to have **incomplete** status, not merely be present or have completed objectives.
- `nextQuestID`, `exclusiveGroup`, `breadcrumbForQuestId`: source metadata retained for auditing. The server also builds reverse dependency lists from `NextQuestID`. Positive exclusive groups prevent conflicting active/rewarded members; negative groups have all-members prerequisite semantics when used as dependencies. Chains, reverse links and breadcrumb interactions are conservatively marked unverified, rather than reduced to an incorrect single predecessor rule.
- `dependentBreadcrumbIDs`: sorted actual native quest IDs whose breadcrumb paths lead to this target, including transitive positive links, matching `ObjectMgr::LoadQuests`. Any listed breadcrumb in the current quest log (incomplete, complete, or failed) prevents taking the target, according to `Player::SatisfyQuestDependentBreadcrumbQuests`. Targets are marked unverified unless current native quest-log state can be checked reliably. Disabled source quests are skipped as on the server; zero/invalid links and cycles never create invented/self IDs. A signed direct target uses absolute value; a later negative link stops traversal conservatively because the server converts that later link to unsigned. The actual snapshot has 105 positive source links and no negative links; after server disabled-source filtering there are 79 reverse relationships across 61 named target quests.
- `requiredSkillID`, `requiredSkillPoints`, `requiredMinRepFaction`, `requiredMinRepValue`, `requiredMaxRepFaction`, `requiredMaxRepValue`: addon requirements. They must be checked through reliable native player state, or remain unverified.
- `flags`, `flagsEx`, `flagsEx2`, `flagsEx3`, `specialFlags`: exact source metadata. `repeatable=true` uses verified SpecialFlags bit 1 or daily/weekly Flags bits. Daily/weekly reset eligibility is not modeled by the catalog.
- `disabled=true`: explicit `disables` sourceType 1 quest entry. Such quests remain searchable for completeness but should not be offered as pickup routes.
- `startItemIDs`: exact item-start links from the limited hotfix overrides, without coordinates.
- `availabilityUnverified=true`: unsupported SQL quest-available conditions (source type 19), missing fixed minimum, scripts, reverse/explicit chain or breadcrumb constraints, skill/reputation/source-spell requirements, area/world-state constraints, special pickup/reset flags, or unmodeled extended flags. Ordinary sharable/remove-surplus flags do not alone trigger this marker. Starter templates/spawns with scripts also trigger it. The boolean is an uncertainty marker, never proof of availability or unavailability.

There are 45,989 unverified quests overall; 44,057 catalog quests have no fixed minimum. Of the 3,702 quests with starter positions, 1,518 are unverified and 2,184 pass the modeled snapshot fields; just 11 of those starter quests lack a fixed minimum. None of the starter quests are explicitly disabled. There are 1,515 explicitly disabled quests in the whole named catalog and 4,738 positive fixed display levels. The runtime must additionally use current native completed/active state and the player's level, race/class/faction. Completing a repeatable quest does not by itself prove it can or cannot be repeated now.

Field meanings were checked against [Player.cpp](https://github.com/Karrz1/TrinityCore/blob/25be61f58f48b6e7bc8eda1146af8e1c73c82470/src/server/game/Entities/Player/Player.cpp), [ObjectMgr.cpp](https://github.com/Karrz1/TrinityCore/blob/25be61f58f48b6e7bc8eda1146af8e1c73c82470/src/server/game/Globals/ObjectMgr.cpp), [QuestDef.h](https://github.com/Karrz1/TrinityCore/blob/25be61f58f48b6e7bc8eda1146af8e1c73c82470/src/server/game/Quests/QuestDef.h), [RaceMask.h](https://github.com/Karrz1/TrinityCore/blob/25be61f58f48b6e7bc8eda1146af8e1c73c82470/src/server/game/Miscellaneous/RaceMask.h), and [ConditionMgr.h](https://github.com/Karrz1/TrinityCore/blob/25be61f58f48b6e7bc8eda1146af8e1c73c82470/src/server/game/Conditions/ConditionMgr.h).

## Verified pickup records

Starters join only `creature_queststarter`/`gameobject_queststarter` to the exact native `creature.id`/`gameobject.id` spawn template, with creature/gameobject names as labels. Neither objective POIs nor turn-ins imply a starter. This schema has a single integer spawn template ID; no ambiguous multi-template positions are synthesized.

Each starter has `label`, `worldX` (east), `worldY` (north), `instance` (native world map ID), `faction` (`A`, `H`, `AH`), `source="snapshot"`, and relation-table `provenance`. SQL `position_x` is north and `position_y` east; the axes are intentionally swapped for HereBeDragons world coordinates.

Only maps 0, 1 and 2991 are accepted. Nonworld/instance maps exclude 19,996 spawns; phase/terrain/difficulty/event/pool conditions exclude 51,639. Phasing checks use `PhaseId`, `PhaseGroup`, `phaseUseFlags` and `terrainSwapMap`; spawn difficulty must be exactly default `0`. Event/pool membership is by spawn GUID, not template ID. Object-visibility conditions (source type 32) cause matching template entries to be omitted conservatively. Manual-spawn groups (flag 0x04), groups that despawn on condition failure (flag 0x20), and groups with source-type-33 conditions are excluded by their native spawn-type/GUID memberships. Ordinary dynamic spawn-rate groups are preserved. These conditions are not assumed evaluable on the client. Unknown or hostile-to-both starter faction templates are omitted using the same audited faction group rules as the bundled services builder. The runtime must still exclude starters hostile to the current player's faction.

A quest keeps at most **eight actual existing positions**, deduplicated and evenly sampled in deterministic map/east/north/label order. No new average, centroid or arbitrary coordinate is calculated. This build discards **108 excess positions across three quests**; starter records are useful candidate positions, not exhaustive spawn coverage. Scripted movement, live despawns and realm changes remain outside the snapshot guarantee.

## Rebuild and verification

From the Mapperly directory, with the existing cached archive:

```powershell
python tools/build_quest_catalog.py
python tests/quest_catalog_builder.py
```

The fourteen builder tests verify declared-column parsing, all-name retention, fixed levels, native starter relations, axes, exact/remapped race masks, class/availability extraction, missing tuning/item positions, conditional/instance/pool/event/spawn-group exclusions, faction filtering, reverse-chain uncertainty, reverse breadcrumb sorting/transitive links/signs/invalid targets/cycles/disabled sources, explicit disabled state, bounded actual-position sampling deterministic output and exact-once complete search-order coverage. The generated entire catalog is loaded with Lua 5.1 to verify syntax and its 48,793 quest / 4,123 starter counts. Rebuild statistics are printed to the console.
