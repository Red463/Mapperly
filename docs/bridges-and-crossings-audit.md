# Bridge and zone crossing audit

**Status: available-source audit complete; unresolved source coverage and live acceptance remain explicit. Discovery is not floor certification.**

Snapshot build 70959. Reported live client build 71091. Native maps: 73. Placements: 616311. Candidate placements: 8228.

## Limits

- Live verification is pending on reported client build 71091. The source snapshot is build 70959.
- Geometric/name candidates are a discovery superset, not certified bridges.
- Native ownership/ground approaches cover 55 UI terrain maps. All 73 native maps were scanned for placements; instances without UI terrain masks cannot receive ground permissions.
- Active embedded-model transforms and selected bridge groups were tested. Unsupported component contacts and missing floor coverage remain explicit per candidate.
- Missing or legacy assets are counted, never classified as safe.

## Native map coverage

| Map | Tiles | Errors | UI terrain maps | Ground audit |
| --- | ---: | ---: | --- | --- |
| 0 Eastern Kingdoms | 736 | 0 | 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1453, 1455, 1458, 2548 | terrain-supported |
| 1 Kalimdor | 988 | 0 | 1411, 1412, 1413, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450, 1451, 1452, 1454, 1456, 1457, 2482, 2652 | terrain-supported |
| 13 Test Dungeon | 0 | 1 | none | source-unavailable-and-no-UI-terrain-mask |
| 25 Scott Test | 0 | 0 | none | no-UI-terrain-mask |
| 29 CashTest | 0 | 0 | none | no-UI-terrain-mask |
| 30 Alterac Valley | 35 | 0 | 1459 | terrain-supported |
| 33 Shadowfang Keep | 25 | 0 | none | no-UI-terrain-mask |
| 34 Stormwind Stockade | 0 | 0 | none | no-UI-terrain-mask |
| 35 <unused>StormwindPrison | 0 | 0 | none | no-UI-terrain-mask |
| 36 Deadmines | 36 | 0 | none | no-UI-terrain-mask |
| 37 Azshara Crater | 30 | 0 | none | no-UI-terrain-mask |
| 42 Collin's Test | 0 | 0 | none | no-UI-terrain-mask |
| 43 Wailing Caverns | 0 | 0 | none | no-UI-terrain-mask |
| 44 <unused> Monastery | 0 | 0 | none | no-UI-terrain-mask |
| 47 Razorfen Kraul | 6 | 0 | none | no-UI-terrain-mask |
| 48 Blackfathom Deeps | 0 | 0 | none | no-UI-terrain-mask |
| 70 Uldaman | 0 | 0 | none | no-UI-terrain-mask |
| 90 Gnomeregan | 0 | 0 | none | no-UI-terrain-mask |
| 109 Sunken Temple | 0 | 0 | none | no-UI-terrain-mask |
| 129 Razorfen Downs | 24 | 0 | none | no-UI-terrain-mask |
| 169 Emerald Dream | 256 | 0 | none | no-UI-terrain-mask |
| 189 Scarlet Monastery | 36 | 0 | none | no-UI-terrain-mask |
| 209 Zul'Farrak | 21 | 0 | none | no-UI-terrain-mask |
| 229 Blackrock Spire | 0 | 0 | none | no-UI-terrain-mask |
| 230 Blackrock Depths | 0 | 0 | none | no-UI-terrain-mask |
| 249 Onyxia's Lair | 0 | 0 | none | no-UI-terrain-mask |
| 269 Caverns of Time | 39 | 0 | none | no-UI-terrain-mask |
| 289 Scholomance | 16 | 0 | none | no-UI-terrain-mask |
| 309 Zul'Gurub | 25 | 0 | none | no-UI-terrain-mask |
| 329 Stratholme | 20 | 0 | none | no-UI-terrain-mask |
| 349 Maraudon | 0 | 0 | none | no-UI-terrain-mask |
| 369 Deeprun Tram | 0 | 0 | none | no-UI-terrain-mask |
| 389 Ragefire Chasm | 0 | 0 | none | no-UI-terrain-mask |
| 409 Molten Core | 0 | 0 | none | no-UI-terrain-mask |
| 429 Dire Maul | 0 | 0 | none | no-UI-terrain-mask |
| 449 Alliance PVP Barracks | 0 | 0 | none | no-UI-terrain-mask |
| 450 Horde PVP Barracks | 0 | 0 | none | no-UI-terrain-mask |
| 469 Blackwing Lair | 16 | 0 | none | no-UI-terrain-mask |
| 489 Warsong Gulch | 16 | 0 | 1460 | terrain-supported |
| 509 Ruins of Ahn'Qiraj | 40 | 0 | none | no-UI-terrain-mask |
| 529 Arathi Basin | 16 | 0 | 1461 | terrain-supported |
| 531 Ahn'Qiraj Temple | 25 | 0 | none | no-UI-terrain-mask |
| 533 Naxxramas | 24 | 0 | none | no-UI-terrain-mask |
| 2720 The Searing Basin | 12 | 0 | none | no-UI-terrain-mask |
| 2784 Demon Fall Canyon | 9 | 0 | none | no-UI-terrain-mask |
| 2789 The Tainted Scar | 9 | 0 | none | no-UI-terrain-mask |
| 2791 Storm Cliffs | 20 | 0 | none | no-UI-terrain-mask |
| 2804 The Crystal Vale | 9 | 0 | none | no-UI-terrain-mask |
| 2806 Shadow Hold | 9 | 0 | none | no-UI-terrain-mask |
| 2807 Burning of Andorhal | 25 | 0 | none | no-UI-terrain-mask |
| 2817 Starfall Barrow Den | 9 | 0 | none | no-UI-terrain-mask |
| 2832 Nightmare Grove | 36 | 0 | none | no-UI-terrain-mask |
| 2853 Deadwind Pass | 12 | 0 | none | no-UI-terrain-mask |
| 2856 Scarlet Enclave | 42 | 0 | none | no-UI-terrain-mask |
| 2868 Eastern Plaguelands (Scarlet Raid Phase) | 12 | 0 | none | no-UI-terrain-mask |
| 2875 Karazhan Crypts | 12 | 0 | none | no-UI-terrain-mask |
| 2902 The Scarab Dais | 25 | 0 | none | no-UI-terrain-mask |
| 2921 Naxxramas | 24 | 0 | none | no-UI-terrain-mask |
| 2959 City of Dalaran | 25 | 0 | none | no-UI-terrain-mask |
| 2980 Dalaran City | 16 | 0 | none | no-UI-terrain-mask |
| 2991 Zephras Isle | 72 | 0 | 2521, 2665 | terrain-supported |
| 2995 Hyjal Crater | 35 | 0 | none | no-UI-terrain-mask |
| 2996 Warsong Gulch (Winter) | 9 | 0 | none | no-UI-terrain-mask |
| 2997 Darkspear Islands | 25 | 0 | 2524 | terrain-supported |
| 2998 Excavation Site: Wetlands | 39 | 0 | none | no-UI-terrain-mask |
| 2999 Ruins of Lordaeron | 9 | 0 | none | no-UI-terrain-mask |
| 3005 Battle for Gilneas | 16 | 0 | none | no-UI-terrain-mask |
| 3021 Eastern Kingdoms Preserved | 60 | 0 | none | no-UI-terrain-mask |
| 3065 The Hall of Thanes | 81 | 0 | none | no-UI-terrain-mask |
| 3104 nothing to see here | 240 | 0 | none | no-UI-terrain-mask |
| 3109 Manor Mistmantle | 0 | 1 | none | source-unavailable-and-no-UI-terrain-mask |
| 3217 Dalaran Skycuter | 0 | 1 | none | source-unavailable-and-no-UI-terrain-mask |
| 3218 Mulgore Skycuter | 0 | 1 | none | source-unavailable-and-no-UI-terrain-mask |

## Bridge candidates

Full identities, coordinates, placement transforms, source hashes and individual validation results are in `tools/data/bridges-and-crossings-manifest.json`. A certified corridor covers its proven path, not an entire compound asset. All live acceptance remains pending.

| Native map | Candidates | Certified corridors |
| --- | ---: | ---: |
| 0 | 2192 | 43 |
| 1 | 3060 | 39 |
| 30 | 36 | 1 |
| 33 | 90 | 0 |
| 36 | 6 | 0 |
| 37 | 43 | 0 |
| 43 | 1 | 0 |
| 47 | 30 | 0 |
| 70 | 1 | 0 |
| 90 | 1 | 0 |
| 109 | 1 | 0 |
| 169 | 20 | 0 |
| 189 | 1 | 0 |
| 209 | 27 | 0 |
| 229 | 1 | 0 |
| 230 | 1 | 0 |
| 249 | 1 | 0 |
| 269 | 123 | 0 |
| 289 | 24 | 0 |
| 309 | 135 | 0 |
| 329 | 1 | 0 |
| 369 | 1 | 0 |
| 389 | 1 | 0 |
| 429 | 1 | 0 |
| 469 | 25 | 0 |
| 489 | 47 | 0 |
| 509 | 30 | 0 |
| 529 | 15 | 4 |
| 531 | 11 | 0 |
| 533 | 31 | 0 |
| 2720 | 10 | 0 |
| 2784 | 92 | 0 |
| 2789 | 142 | 0 |
| 2791 | 105 | 0 |
| 2804 | 43 | 0 |
| 2806 | 101 | 0 |
| 2807 | 158 | 0 |
| 2817 | 14 | 0 |
| 2832 | 219 | 0 |
| 2853 | 166 | 0 |
| 2856 | 110 | 0 |
| 2868 | 66 | 0 |
| 2875 | 170 | 0 |
| 2902 | 52 | 0 |
| 2921 | 31 | 0 |
| 2959 | 149 | 0 |
| 2980 | 92 | 0 |
| 2991 | 113 | 0 |
| 2995 | 178 | 0 |
| 2996 | 39 | 0 |
| 2997 | 56 | 0 |
| 2998 | 29 | 0 |
| 2999 | 26 | 0 |
| 3005 | 15 | 0 |
| 3021 | 94 | 0 |
| 3065 | 1 | 0 |

## Zone boundary accounting

97 audited ownership pairs; 64 have bundled links. A link's presence is not proof that every passage on that border has been checked.

Approaches: 325 verified-ground-approach, 47 verified-with-swimming-fallback, 15 short-verified-ground-approach, 4 interior-floor-approach-required, 1 verified-ground-approach-via-zone-crossing.
18 exact ground handoffs were withheld after the approach audit. Nearby replacement candidates were re-evaluated before spacing/pair selection. Their evidence remains in `tools/data/crossing-handoff-review.json`; no whole zone pair is banned.
See `crossing-approaches-audit.md` and `testing-crossing-acceptance.md` for approach and live-test details.

## Known transport and portal crossings

Each directed native record is accounted for separately. They retain the existing transport/portal mechanisms; none grants ordinary walking permission. All live acceptance is pending. Source hashes and full endpoints remain in the inventory.

| ID | Kind | Name | Source |
| --- | --- | --- | --- |
| transport:241:11:29 | boat | Ratchet - Booty Bay | native-transports-70959.json |
| transport:241:29:11 | boat | Ratchet - Booty Bay | native-transports-70959.json |
| transport:285:4:20 | zeppelin | Grom'gol - Orgrimmar | native-transports-70959.json |
| transport:285:20:4 | zeppelin | Grom'gol - Orgrimmar | native-transports-70959.json |
| transport:292:8:21 | boat | Menethil Harbor - Theramore | native-transports-70959.json |
| transport:292:21:8 | boat | Menethil Harbor - Theramore | native-transports-70959.json |
| transport:293:5:17 | boat | Rut'theran - Auberdine | native-transports-70959.json |
| transport:293:17:5 | boat | Rut'theran - Auberdine | native-transports-70959.json |
| transport:301:5:21 | zeppelin | Grom'gol - Undercity | native-transports-70959.json |
| transport:301:21:5 | zeppelin | Grom'gol - Undercity | native-transports-70959.json |
| transport:302:7:28 | zeppelin | Orgrimmar - Undercity | native-transports-70959.json |
| transport:302:28:7 | zeppelin | Orgrimmar - Undercity | native-transports-70959.json |
| transport:303:1:6 | boat | Feathermoon Stronghold - Feralas coast | native-transports-70959.json |
| transport:303:6:20 | boat | Feathermoon Stronghold - Feralas coast | native-transports-70959.json |
| transport:11167:7:20 | boat | Menethil Harbor - Southshore - Auberdine | native-transports-70959.json |
| transport:11167:20:34 | boat | Menethil Harbor - Southshore - Auberdine | native-transports-70959.json |
| transport:11167:34:7 | boat | Menethil Harbor - Southshore - Auberdine | native-transports-70959.json |
| transport:11391:5:23 | boat | Steamwheedle Port - Powderfuse Port | native-transports-70959.json |
| transport:11391:23:5 | boat | Steamwheedle Port - Powderfuse Port | native-transports-70959.json |
| transport:11398:13:31 | airship | Alterac Mountains - Zephras Isle | native-transports-70959.json |
| transport:11398:31:13 | airship | Alterac Mountains - Zephras Isle | native-transports-70959.json |
| transport:11457:5:17 | airship | Mulgore - Zephras Isle | native-transports-70959.json |
| transport:11457:17:5 | airship | Mulgore - Zephras Isle | native-transports-70959.json |
| transport:11616:6:18 | boat | Auberdine - Stormwind | native-transports-70959.json |
| transport:11616:18:6 | boat | Auberdine - Stormwind | native-transports-70959.json |
| lift:great-lift:1413:1441 | lift | The Great Lift | native-local-transports-70959.json |
| lift:great-lift:1441:1413 | lift | The Great Lift | native-local-transports-70959.json |
| tram:deeprun:1453:1455 | tram | Deeprun Tram | native-tram-service-70959.json |
| tram:deeprun:1455:1453 | tram | Deeprun Tram | native-tram-service-70959.json |
| portal:tram:2166 | portal | Deeprun Tram Ironforge - Exit | native-tram-portals-70959.json |
| portal:tram:2171 | portal | Deeprun Tram Stormwind - Exit | native-tram-portals-70959.json |
| portal:tram:2173 | portal | Deeprun Tram Stormwind - Entrance | native-tram-portals-70959.json |
| portal:tram:2175 | portal | Deeprun Tram Ironforge - Exit | native-tram-portals-70959.json |
