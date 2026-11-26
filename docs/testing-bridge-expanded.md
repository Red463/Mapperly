# Expanded bridge acceptance tests

The local 1.2.5 candidate explicitly supports the 76 bridge placements below. Asset names are native file/model labels, not necessarily official location names. Automated validation is not a live-client collision guarantee.

## How to test

1. Enable Smart routing and start on a bank. Alt-right-click a point just beyond the other end. Test both directions.
2. Check that the world-map/minimap line and navigation arrow follow the deck, then resume ground walking.
3. Repeat with Avoid swimming and Prefer roads enabled. Try starting five yards farther back from each listed handoff to check normal approaches.
4. Pause/resume and rejoin after a short detour. Put a destination pin on the deck and test a partial crossing.
5. If a new start from the deck reports that elevation cannot be confirmed, move onto a bank. This client can report zero/unknown player height; Mapperly does not treat that as proof of being on a deck. An established route retains XY guidance.
6. Paste `/mapperly report` immediately after a failure, including the exact starting position and intended destination.

Priority checks: Westfall-Duskwood, Westfall-Elwynn, Duskwood-Redridge, and Western/Eastern Plaguelands crossings; a narrow rope bridge; one tilted bridge; and a normal same-zone bank approach.

| Native bridge label | First bank | Second bank | Verified strip radius |
| --- | --- | --- | ---: |
| Southfury stone bridge (294532) | Ashenvale 94.75, 47.76 | Azshara 10.57, 75.08 | 2.50 yd |
| elwynnlionbridge (21672) | Duskwood 93.84, 11.24 | Redridge Mountains 1.88, 89.67 | 2.50 yd |
| Native stone bridge 281972 (281972) | The Barrens 62.68, 19.22 | Durotar 34.60, 42.30 | 2.50 yd |
| plaguelandsbridge (290679) | Western Plaguelands 69.83, 50.28 | Eastern Plaguelands 8.83, 61.64 | 2.50 yd |
| duskwoodcoveredbridge (35875) | Westfall 67.39, 62.83 | Duskwood 8.77, 63.77 | 2.50 yd |
| elwynnlionbridge (170818) | Westfall 61.72, 18.06 | Elwynn Forest 20.70, 79.82 | 2.50 yd |
| ironfootbridge (586276) | Alterac Valley 49.25, 86.81 | Alterac Valley 49.49, 87.52 | 2.50 yd |
| arathistonebridge02 (599003) | Arathi Basin 36.04, 31.57 | Arathi Basin 36.04, 34.59 | 1.50 yd |
| arathistonebridge02 (599007) | Arathi Basin 61.51, 51.94 | Arathi Basin 61.61, 54.80 | 2.50 yd |
| arathistonebridge03 (604139) | Arathi Basin 49.16, 52.09 | Arathi Basin 49.61, 54.86 | 1.50 yd |
| arathistonebridge03 (604140) | Arathi Basin 48.82, 34.25 | Arathi Basin 48.90, 31.34 | 2.50 yd |
| arathistonebridge02 (199411) | Arathi Highlands 44.00, 82.98 | Arathi Highlands 44.03, 81.61 | 2.50 yd |
| kalidarbridge01 (237080) | Ashenvale 63.37, 69.96 | Ashenvale 63.80, 70.21 | 1.50 yd |
| kalidarbridge01 (237613) | Ashenvale 37.26, 53.08 | Ashenvale 37.46, 53.74 | 2.50 yd |
| kalidarbridge01 (237614) | Ashenvale 33.77, 47.99 | Ashenvale 34.12, 48.46 | 2.50 yd |
| Native stone bridge 573962 (573962) | Ashenvale 84.36, 66.22 | Ashenvale 85.09, 65.09 | 2.50 yd |
| Native stone bridge 574021 (574021) | Ashenvale 78.86, 68.09 | Ashenvale 79.84, 68.38 | 2.50 yd |
| lavabridge (9990) | Burning Steppes 80.13, 36.35 | Burning Steppes 81.61, 36.89 | 1.50 yd |
| lavabridge (57975) | Burning Steppes 65.08, 26.68 | Burning Steppes 65.44, 24.48 | 1.50 yd |
| lavabridge (69515299) | Burning Steppes 78.24, 76.07 | Burning Steppes 78.04, 74.63 | 0.75 yd |
| lavabridge (70047366) | Burning Steppes 15.18, 32.41 | Burning Steppes 15.21, 31.05 | 0.75 yd |
| darkshorebridge01 (140667) | Darkshore 41.26, 74.81 | Darkshore 41.39, 75.37 | 2.50 yd |
| darkshorebridge03 (165743) | Darkshore 38.34, 42.08 | Darkshore 38.55, 42.63 | 2.50 yd |
| darkshorebridge03 (165924) | Darkshore 38.06, 43.52 | Darkshore 38.43, 43.38 | 2.50 yd |
| darkshorebridge01 (165925) | Darkshore 37.55, 42.46 | Darkshore 37.53, 43.10 | 2.50 yd |
| deadwindrockbridge (559817) | Deadwind Pass 43.67, 34.29 | Deadwind Pass 41.86, 34.63 | 2.50 yd |
| deadwindrockbridge (561328) | Deadwind Pass 48.06, 61.65 | Deadwind Pass 45.96, 62.90 | 2.50 yd |
| ironforgeropebridge01 (66628) | Dun Morogh 39.89, 37.93 | Dun Morogh 39.66, 39.82 | 2.50 yd |
| ironfootbridge (76674) | Dun Morogh 46.92, 43.29 | Dun Morogh 47.04, 44.00 | 2.50 yd |
| elwynnlionbridge (71546) | Dustwallow Marsh 63.65, 44.45 | Dustwallow Marsh 64.29, 45.62 | 2.50 yd |
| dustwallowfootbridge (82011) | Dustwallow Marsh 36.38, 40.86 | Dustwallow Marsh 36.14, 41.47 | 2.50 yd |
| swampbridge01 (92581) | Dustwallow Marsh 39.16, 37.12 | Dustwallow Marsh 39.34, 36.42 | 1.50 yd |
| swampbridge01 (92582) | Dustwallow Marsh 39.43, 34.95 | Dustwallow Marsh 39.42, 35.72 | 1.50 yd |
| swampbridge01 (92583) | Dustwallow Marsh 39.40, 33.82 | Dustwallow Marsh 39.40, 33.08 | 1.50 yd |
| swampbridge01 (95934) | Dustwallow Marsh 41.13, 67.73 | Dustwallow Marsh 41.60, 67.40 | 1.50 yd |
| dustwallowfootbridge (104982) | Dustwallow Marsh 43.38, 26.24 | Dustwallow Marsh 43.25, 26.91 | 0.50 yd |
| dustwallowfootbridge (106337) | Dustwallow Marsh 54.54, 28.80 | Dustwallow Marsh 54.65, 29.52 | 1.50 yd |
| elwynnwidebridge (10463) | Elwynn Forest 52.56, 44.91 | Elwynn Forest 53.07, 45.69 | 1.50 yd |
| elwynnwidebridge (17365) | Elwynn Forest 28.33, 77.87 | Elwynn Forest 29.02, 77.95 | 2.50 yd |
| elwynnwidebridge (19975) | Elwynn Forest 74.92, 72.49 | Elwynn Forest 74.25, 72.62 | 1.50 yd |
| Native stone bridge 256839 (256839) | Felwood 40.98, 47.91 | Felwood 41.00, 48.70 | 2.50 yd |
| Native stone bridge 258296 (258296) | Felwood 43.43, 74.75 | Felwood 43.77, 75.33 | 2.50 yd |
| elwynnfootbridge (240196) | Feralas 75.90, 43.55 | Feralas 75.58, 43.66 | 2.50 yd |
| feralasstonebridge01 (255475) | Feralas 63.74, 51.16 | Feralas 63.41, 52.43 | 2.50 yd |
| Native stone bridge 261342 (261342) | Feralas 48.86, 45.58 | Feralas 49.05, 46.85 | 2.50 yd |
| darkshorebridge03 (380436) | Feralas 39.73, 11.60 | Feralas 39.51, 12.03 | 1.50 yd |
| wetlandsfootbridge01 (179476) | Hillsbrad Foothills 62.48, 41.46 | Hillsbrad Foothills 63.15, 41.72 | 2.50 yd |
| moongladebridge (301662) | Moonglade 43.72, 60.90 | Moonglade 44.67, 61.36 | 2.50 yd |
| moongladebridge (301663) | Moonglade 46.48, 62.16 | Moonglade 47.54, 62.85 | 2.50 yd |
| moongladebridge (305309) | Moonglade 49.58, 40.06 | Moonglade 50.81, 39.88 | 1.50 yd |
| moongladebridge (305310) | Moonglade 49.51, 37.92 | Moonglade 50.77, 37.73 | 1.50 yd |
| moongladebridge (333964) | Moonglade 49.34, 33.73 | Moonglade 50.45, 33.51 | 2.50 yd |
| darkshorebridge03 (337633) | Mount Hyjal 60.02, 83.45 | Mount Hyjal 59.46, 84.33 | 1.50 yd |
| darkshorebridge03 (346146) | Mount Hyjal 77.92, 45.50 | Mount Hyjal 78.73, 45.45 | 2.50 yd |
| darkshorebridge03 (65736246) | Mount Hyjal 41.05, 44.56 | Mount Hyjal 41.62, 45.40 | 1.50 yd |
| elwynnfootbridge (598652) | Mulgore 38.86, 41.17 | Mulgore 39.13, 41.61 | 2.50 yd |
| wetlandsfootbridge01 (66784906) | Riverglades 22.26, 67.18 | Riverglades 21.82, 67.25 | 2.50 yd |
| Native stone bridge 66785036 (66785036) | Riverglades 66.16, 36.29 | Riverglades 66.45, 34.44 | 2.50 yd |
| keepbridge01 (70157344) | Riverglades 43.21, 46.31 | Riverglades 43.88, 46.92 | 0.50 yd |
| wetlandsfootbridge01 (71629778) | Riverglades 75.07, 31.39 | Riverglades 74.54, 32.17 | 2.50 yd |
| lavabridge (73015) | Searing Gorge 37.65, 73.79 | Searing Gorge 38.75, 73.72 | 0.75 yd |
| duskwoodchasmbridge (98521) | Silverpine Forest 49.75, 30.06 | Silverpine Forest 49.74, 28.84 | 2.50 yd |
| Native stone bridge 67155284 (67155284) | Silverpine Forest 45.31, 79.93 | Silverpine Forest 45.31, 76.66 | 2.50 yd |
| stranglechasmbridge (114437) | Stranglethorn Vale 28.36, 58.37 | Stranglethorn Vale 28.69, 58.19 | 2.50 yd |
| stranglechasmbridge (119071) | Stranglethorn Vale 27.21, 58.90 | Stranglethorn Vale 27.62, 58.53 | 2.50 yd |
| swampbridge01 (599481) | Stranglethorn Vale 14.42, 13.68 | Stranglethorn Vale 14.76, 13.97 | 0.75 yd |
| bridgestranglethorn (31960) | Swamp of Sorrows 23.31, 47.80 | Swamp of Sorrows 22.23, 48.83 | 2.50 yd |
| kalidarbridge01 (146213) | Teldrassil 44.50, 50.40 | Teldrassil 44.17, 50.92 | 1.50 yd |
| Native stone bridge 334573 (334573) | The Barrens 50.81, 48.24 | The Barrens 51.06, 48.94 | 2.50 yd |
| duskwoodcoveredbridge (127329) | Tirisfal Glades 52.59, 54.37 | Tirisfal Glades 53.53, 53.34 | 2.50 yd |
| lavabridge (317114) | Un'Goro Crater 53.03, 43.21 | Un'Goro Crater 52.88, 44.60 | 1.50 yd |
| plaguelandsbridge (392611) | Western Plaguelands 67.84, 84.26 | Western Plaguelands 68.07, 82.52 | 2.50 yd |
| elwynnlionbridge (588171) | Western Plaguelands 48.43, 71.77 | Western Plaguelands 49.22, 73.11 | 2.50 yd |
| Native stone bridge 84525 (84525) | Wetlands 12.30, 50.51 | Wetlands 11.02, 54.30 | 2.50 yd |
| elwynnwidebridge (188812) | Wetlands 49.67, 36.72 | Wetlands 49.85, 37.54 | 2.50 yd |
| winterspringrockbridge (344256) | Winterspring 62.39, 67.63 | Winterspring 61.93, 70.48 | 1.50 yd |

## Remaining coverage

Uncertified candidates and per-placement reasons are recorded in `tools/data/bridges-and-crossings-manifest.json`. Some entries are props/components rather than complete bridges. Native maps without shipped terrain, unverified bank contacts, broken/stepped floor geometry and submerged decks remain withheld. The separate full zone-crossing approach audit is still open.
