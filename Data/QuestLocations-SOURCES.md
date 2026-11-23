# Standalone active quest location snapshot

`QuestLocations.lua` supplies **6,635 objective locations and 4,217 turn-in locations for 5,415 quest IDs**. It performs no runtime downloads or other-addon imports. Questie and QuestieDB are not sources. The player's native quest log supplies quest titles; this file does not bundle a quest-name database.

## Pinned source and integrity

- Project: [Karrz1/TrinityCore, Forever branch](https://github.com/Karrz1/TrinityCore/tree/forever).
- Release: [Forever TDB 2026-10-14](https://github.com/Karrz1/TrinityCore/releases/tag/forever-tdb-2026-10-14).
- Archive: `TDB_full_forever_2026_10_14.7z`, [download](https://github.com/Karrz1/TrinityCore/releases/download/forever-tdb-2026-10-14/TDB_full_forever_2026_10_14.7z).
- Archive SHA-256: `373cdca7963927d4d67933032b4b858a811eae0af960d4de4ff19833a88d4f41` (same pinned archive as the services builder).
- World SQL: `TDB_full_world_forever_2026_10_14.sql`.
- SQL SHA-256: `3357f62451dcdef27123243c83c76a1a2e3251cf730aea01abf2f7f3d776d341`.
- License: TrinityCore contributors, GPL version 2. See `Libs/Forever-Services-COPYING.txt`.

The generator verifies both archive and extracted SQL hashes before parsing. Only maps **0, 1, and 2991** are accepted; the last is Forever's Zephras Isle. This public project snapshot is not an authoritative export of the current live realm. Coordinates can be stale or incomplete; they have not all been visited in-game.

## Schema audit and selection

The actual snapshot contains 48,801 `quest_template` records, 62,272 `quest_objectives`, 135,751 `quest_poi`, 307,080 `quest_poi_points`, 4,261 `creature_questender` and 209 `gameobject_questender` relations. The builder reads each table's declared column names rather than assuming tuple offsets.

Objective locations prefer a single explicit POI point when its `QuestObjectiveID` identifies a visible objective of the same quest. POI/point joining uses `(QuestID, Idx1)`, matching the Forever server's [ObjectMgr::LoadQuestPOI implementation](https://github.com/Karrz1/TrinityCore/blob/forever/src/server/game/Globals/ObjectMgr.cpp). `BlobIndex` is not the point-table join key. Repeated POI join keys and POIs with player/navigation conditions or spawn-tracking requirements are omitted. Polygon vertices and invented polygon centroids are not exact targets, so multi-point area blobs are omitted. Missing, conditional or ambiguous POIs can fall back to explicit objective spawn relations.

The fallback joins `quest_objectives.ObjectID` to the exact `creature.id` or `gameobject.id` template. Supported objective types are monster (0), gameobject (2), and talk-to (3), as defined in Forever's [QuestDef.h](https://github.com/Karrz1/TrinityCore/blob/forever/src/server/game/Quests/QuestDef.h). Item objectives are included only if they have an explicit singleton objective POI; there is no inferred item-to-dropper lookup. Script-only kill credits without a matching spawn remain unavailable.

Turn-ins join `creature_questender` or `gameobject_questender` directly to exact spawns. They are never inferred from quest starters, POI negative indices, quest titles or descriptions. Labels use objective descriptions or NPC/gameobject names. Output provenance identifies the tables behind each record.

Spawns outside the three supported world maps, explicitly phased spawns (`PhaseId`, `PhaseGroup`, `phaseUseFlags`), terrain swaps, non-default spawn difficulties, and event/pool-dependent spawns are excluded. Event and pool membership is checked by spawn GUID, not template ID. The audited snapshot has no rows in the two event-spawn tables. Instance filtering excluded 19,996 spawns; conditional filtering excluded 51,639. This conservative filtering deliberately omits conditional content rather than pretending it is always accessible.

Turn-in records include `faction="A"`, `"H"`, or `"AH"`, using the same group rules and pinned local Forever 1.60.1.70959 `FactionTemplate` CSV as [Services-SOURCES.md](Services-SOURCES.md). CSV SHA-256: `963a24a4a32acd76dea04ac337e037f45d72e2c6a403e3826dfcfc95e28b746d`. Unknown or hostile-to-both faction relations are omitted; this snapshot required no such omissions. Enemy objective NPCs remain eligible because they can be legitimate kill targets.

## Runtime format and coordinates

`A.QuestLocationData={version=1,source="Forever TDB 2026-10-14",quests={[questID]={...}}}`.

Each record contains `kind` (`objective` or `turnin`), `label`, `worldX` (east), `worldY` (north), `instance` (world map ID), `source="snapshot"`, and `provenance`. Objective records contain the explicit database `objectiveID`; turn-ins contain `faction`. `objectiveIndex` is deliberately absent: SQL `ObjectiveIndex`, `Order`, and `StorageIndex` have not been verified as native `C_QuestLog.GetQuestObjectives` array indices. Consumers must not guess completion state by treating these fields as interchangeable.

SQL `position_x`/POI `X` are north coordinates; SQL `position_y`/POI `Y` are east coordinates. Output swaps these into HereBeDragons' east/north argument order. These are world units, not zone percentages. The tests check the axis swap and normalized map projection independently. No Classic-percent-to-Forever-map conversion is used.

Final objective provenance counts: 2,757 singleton POI points, 3,839 creature objective spawns, 39 gameobject objective spawns. Turn-in provenance counts: 4,045 creature and 172 gameobject spawns. No unsupported quest is invented; absent locations should be treated as unavailable and native live quest coordinates can supplement this snapshot.

## Bounds and reproduction

Identical records are collapsed. Each objective retains at most **8** actual locations, each quest at most **8** turn-ins, and each quest at most **64** records total. Oversized groups retain evenly spaced entries in deterministic map/east/north/name order; no new positions are calculated. The overall quest cap preserves turn-ins first, then distributes objective rows by objective ID before taking additional locations. This build truncated **7,622 candidate rows across 432 groups**; no quest reached the overall cap. Truncation means these are useful candidate locations, not an exhaustive list of every spawn. Rebuild statistics print to the console.

From the `Mapperly` directory, with the existing services source archive cached under `assets/services-source`:

```powershell
python tools/build_quest_locations.py
python tests/quest_locations_builder.py
```

The builder requires the pinned cache and does not implicitly download a different source. It can extract the world SQL with `tar` if needed. Release packages need only the generated data, source notes, generator and existing license/faction input; exclude the large source cache.
