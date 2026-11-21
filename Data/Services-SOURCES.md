# Standalone service-location dataset

`Services.lua` contains 47 inn spawns and 109 mailbox spawns. It is generated at build time; it performs no downloads and imports no other addon at runtime. Questie and QuestieDB are not data sources for this dataset.

## Spawn source

- Project: [Karrz1/TrinityCore, Forever branch](https://github.com/Karrz1/TrinityCore/tree/forever).
- Snapshot: [Forever TDB 2026-10-14](https://github.com/Karrz1/TrinityCore/releases/tag/forever-tdb-2026-10-14).
- Archive: `TDB_full_forever_2026_10_14.7z`.
- SHA-256: `373cdca7963927d4d67933032b4b858a811eae0af960d4de4ff19833a88d4f41`.
- Tables: `creature`, `creature_template`, `gameobject`, `gameobject_template`, `gameobject_template_addon`.
- Inn selection: effective NPC flags include INNKEEPER (65536).
- Mailbox selection: game-object type 19.
- World maps: 0, 1 and 2991 (Zephras Isle). Instances and other map IDs are excluded.
- Explicitly phased records are excluded. Duplicate identical template/world positions are collapsed.
- License/attribution: TrinityCore contributors; GPL version 2. See `Libs/Forever-Services-COPYING.txt`. Original source and the reproduction script are provided alongside the generated Lua data.

## Coordinate and faction validation

Spawn coordinates remain in game world north/east units. At runtime the embedded HereBeDragons library projects them through the selected Forever map's native geometry; there is no Classic-percentage-to-Forever-map shortcut.

Faction classification uses the local Forever **1.60.1.70959** `FactionTemplate` client table (FileDataID 1361579), extracted read-only from the existing workspace CASC snapshot and converted with DBC2CSV. Client tables are Blizzard game data. The build input is `tools/data/factiontemplate-70959.csv`.

- Original DB2 SHA-256: `41122e9c640d08a29bc39904d659fabbf3103287eb2bc5378b4e7705f4c4ecc4`.
- CSV SHA-256: `963a24a4a32acd76dea04ac337e037f45d72e2c6a403e3826dfcfc95e28b746d`.
- Inn access: 19 Alliance, 20 Horde, 8 shared.
- Mailbox access: 26 Alliance, 21 Horde, 62 shared.
- Unclassified access records: 0.

A regression check projects Innkeeper Trelayne through the local Forever Duskwood map bounds: **73.87, 44.41**. This agrees with the approximately 73.9, 44.4 position in the supplied in-game screenshot.

## Scope and updates

This is a public server-project snapshot, **not an authoritative export of the live Forever realm**. Archive integrity, schema, service types, faction classification and sample map projection have been checked; every spawn has not been visited in the client. The snapshot can omit new content or contain stale locations. Runtime discoveries supplement it and are retained across addon updates. Nearby same-category service pins are deduplicated.

Reproduce from the workspace root:

```powershell
python Mapperly/tools/build_services.py
```

The script verifies the pinned archive hash before reading it and uses `tar` for 7z extraction. It needs no SQL server, game writes or Questie installation. It emits a plain Lua dataset and a detailed local extraction report under `assets/services-source`. Release ZIPs include the small dataset, license, generator and faction input; the large source archive and SQL caches are excluded.
