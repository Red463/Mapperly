# Bridge and zone-crossing live acceptance

Geometry comes from source build 70959. In-game verification is pending on WoW Forever client build 71091.

## Test setup

Install the Mapperly preview into Interface/AddOns and reload the UI. Enable Smart routing and the on-screen route steps. Set a destination by Alt-right-clicking its map location, or enter its X/Y values in Destinations after selecting that zone map.

For each row, stand at approach A and navigate to approach B, then repeat B to A. Confirm the route actually visits the listed handoff or bridge. The planner can choose a different valid crossing between those ground probes; arriving at B does not test the listed crossing in that case. Test approach A → handoff A, the specific handoff A → B passage, then handoff B → approach B separately, including the reverse direction. A floor-anchor row needs a live reachable starting point inside that city or cave; the handoff alone is not an approach certificate.

Verify that the line, arrow and current route step progress through the passage and across the native zone change without an off-route loop. Repeat priority cases with Prefer roads off, then Firm, and with Avoid swimming enabled. That setting may fall back to swimming; rows marked swimming-fallback are not dry-only guarantees.

On a bridge, also test a destination halfway along the deck, a fresh start on the deck, a small detour/rejoin, pause/resume and a reload. If fresh planning cannot establish your elevation, retry from a bank. An established route should continue providing guidance. Do not use a point beneath the deck as a deck-start test.

If planning fails, click **Copy report** in the error window and press Ctrl+C (Cmd+C on Mac). For a problem while following a route, use `/mapperly report`. Include the link number and direction when sharing the report.

## Priority circuit

- Follow the Dun Algaz road from northern Loch Modan through the tunnels to the Wetlands, then return. Check that the arrow follows each tunnel bend and resumes road guidance outside.
- Walk the northern Stranglethorn road across the chasm bridge into Duskwood, then return south. Check that the arrow follows the deck and continues along the road through the zone change in both directions.
- Westfall ↔ Duskwood covered bridge, Ashenvale ↔ Azshara Southfury bridge, and Duskwood ↔ Redridge bridge.
- Wetlands ↔ Arathi Highlands, Dun Morogh ↔ Loch Modan tunnel, and all three Timbermaw branch pairs.
- Ironforge main entrance and Undercity sewer entrance, starting well inside each capital as well as outdoors.
- One small same-zone bridge in Darkshore, a tilted bridge, a narrow rope bridge, and a custom-zone border such as Redridge ↔ Riverglades.
- A journey through several audited exits; a boat/flight journey with walking at both ends; both Great Lift platforms and both tram directions. Transports must remain transport steps, not walking shortcuts.

## All retained link tests

| Link | Approach A | Approach B | Exact handoff A → B | Approach evidence A / B |
| --- | --- | --- | --- | --- |
| 15 | Alterac Mountains 80.88, 42.08 | Western Plaguelands 44.14, 81.18 | Alterac Mountains 80.88, 34.04 → Western Plaguelands 44.14, 86.41 | verified-ground-approach / verified-ground-approach |
| 16 | Alterac Mountains 50.85, 62.11 | Hillsbrad Foothills 55.14, 18.85 | Alterac Mountains 52.90, 69.53 → Hillsbrad Foothills 55.14, 11.82 | verified-ground-approach / verified-ground-approach |
| 17 | Alterac Mountains 51.71, 81.14 | Hillsbrad Foothills 55.66, 19.43 | Alterac Mountains 51.71, 89.17 → Hillsbrad Foothills 55.66, 26.46 | verified-ground-approach / verified-ground-approach |
| 18 | Alterac Mountains 49.66, 75.05 | Hillsbrad Foothills 55.66, 13.57 | Alterac Mountains 51.71, 82.48 → Hillsbrad Foothills 55.66, 20.61 | verified-ground-approach / verified-ground-approach |
| 19 | Alterac Mountains 25.52, 81.14 | Hillsbrad Foothills 26.85, 31.30 | Alterac Mountains 25.52, 89.17 → Hillsbrad Foothills 31.18, 28.61 | verified-ground-approach / verified-ground-approach |
| 20 | Alterac Mountains 21.95, 82.92 | Hillsbrad Foothills 25.14, 33.00 | Alterac Mountains 21.95, 90.96 → Hillsbrad Foothills 28.45, 28.03 | verified-ground-approach / verified-ground-approach |
| 57 | Alterac Mountains 27.43, 3.68 | Tirisfal Glades 67.45, 74.76 | Alterac Mountains 28.50, 3.68 → Tirisfal Glades 67.45, 79.74 | short-verified-ground-approach / verified-ground-approach |
| 58 | Alterac Mountains 13.43, 84.10 | Silverpine Forest 68.46, 53.28 | Alterac Mountains 11.38, 76.67 → Silverpine Forest 70.98, 57.07 | verified-ground-approach / verified-ground-approach |
| 59 | Alterac Mountains 10.38, 74.83 | Silverpine Forest 69.25, 56.85 | Alterac Mountains 12.43, 82.25 → Silverpine Forest 71.78, 60.64 | verified-ground-approach / verified-ground-approach |
| 60 | Alterac Mountains 8.28, 67.60 | Silverpine Forest 68.33, 48.70 | Alterac Mountains 9.30, 71.32 → Silverpine Forest 69.69, 53.65 | verified-ground-approach / verified-ground-approach |
| 187 | Alterac Valley 49.25, 81.50 | Alterac Valley 52.76, 85.48 | Alterac Valley 49.25, 86.81 → Alterac Valley 49.49, 87.52 | verified-ground-approach / verified-ground-approach |
| 188 | Arathi Basin 36.04, 18.76 | Arathi Basin 32.77, 46.43 | Arathi Basin 36.04, 31.57 → Arathi Basin 36.04, 34.59 | verified-ground-approach / verified-ground-approach |
| 189 | Arathi Basin 58.24, 40.10 | Arathi Basin 53.72, 59.71 | Arathi Basin 61.51, 51.94 → Arathi Basin 61.61, 54.80 | verified-ground-approach / verified-ground-approach |
| 190 | Arathi Basin 49.16, 39.28 | Arathi Basin 41.72, 59.77 | Arathi Basin 49.16, 52.09 → Arathi Basin 49.61, 54.86 | verified-ground-approach / verified-ground-approach |
| 191 | Arathi Basin 45.55, 46.09 | Arathi Basin 42.86, 22.28 | Arathi Basin 48.82, 34.25 → Arathi Basin 48.90, 31.34 | verified-ground-approach / verified-ground-approach |
| 21 | Arathi Highlands 17.94, 34.89 | Hillsbrad Foothills 83.92, 49.12 | Arathi Highlands 20.89, 30.47 → Hillsbrad Foothills 83.92, 56.15 | verified-ground-approach / verified-ground-approach |
| 61 | Arathi Highlands 51.25, 89.37 | Wetlands 58.16, 6.80 | Arathi Highlands 52.72, 91.58 → Wetlands 57.43, 6.80 | verified-ground-approach / short-verified-ground-approach |
| 143 | Arathi Highlands 44.00, 89.23 | Arathi Highlands 44.03, 75.36 | Arathi Highlands 44.00, 82.98 → Arathi Highlands 44.03, 81.61 | verified-ground-approach / verified-ground-approach |
| 44 | Ashenvale 53.98, 31.59 | Felwood 54.96, 89.08 | Ashenvale 55.82, 28.83 → Felwood 54.96, 92.99 | verified-ground-approach / verified-ground-approach |
| 88 | Ashenvale 99.75, 38.41 | Azshara 15.65, 62.75 | Ashenvale 99.39, 40.33 → Azshara 14.95, 65.62 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 89 | Ashenvale 98.81, 33.32 | Azshara 13.27, 51.54 | Ashenvale 97.65, 23.63 → Azshara 12.98, 46.64 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 109 | Ashenvale 42.29, 67.30 | Stonetalon Mountains 75.28, 42.81 | Ashenvale 42.29, 71.20 → Stonetalon Mountains 78.35, 42.81 | verified-ground-approach / verified-ground-approach |
| 116 | Ashenvale 92.91, 45.00 | Azshara 12.66, 78.21 | Ashenvale 94.75, 47.76 → Azshara 10.57, 75.08 | verified-ground-approach / verified-ground-approach |
| 125 | Ashenvale 81.95, 64.72 | Ashenvale 85.09, 61.19 | Ashenvale 84.36, 66.22 → Ashenvale 85.09, 65.09 | verified-ground-approach / verified-ground-approach |
| 126 | Ashenvale 77.87, 64.48 | Ashenvale 81.68, 71.13 | Ashenvale 78.86, 68.09 → Ashenvale 79.84, 68.38 | verified-ground-approach / verified-ground-approach |
| 165 | Ashenvale 63.37, 66.06 | Ashenvale 63.80, 74.11 | Ashenvale 63.37, 69.96 → Ashenvale 63.80, 70.21 | verified-ground-approach / verified-ground-approach |
| 166 | Ashenvale 37.26, 49.17 | Ashenvale 35.62, 56.50 | Ashenvale 37.26, 53.08 → Ashenvale 37.46, 53.74 | verified-ground-approach / verified-ground-approach |
| 167 | Ashenvale 33.77, 44.09 | Ashenvale 35.96, 51.22 | Ashenvale 33.77, 47.99 → Ashenvale 34.12, 48.46 | verified-ground-approach / verified-ground-approach |
| 62 | Badlands 15.91, 28.26 | Searing Gorge 85.29, 6.37 | Badlands 11.64, 21.86 → Searing Gorge 91.50, 10.22 | verified-ground-approach / verified-ground-approach |
| 63 | Badlands 14.99, 26.63 | Searing Gorge 85.94, 6.23 | Badlands 8.96, 26.63 → Searing Gorge 88.52, 15.55 | verified-ground-approach / verified-ground-approach |
| 64 | Badlands 0.01, 37.30 | Searing Gorge 83.47, 9.94 | Badlands 4.27, 30.90 → Searing Gorge 83.47, 20.03 | verified-ground-approach / verified-ground-approach |
| 65 | Badlands 50.97, 15.14 | Loch Modan 46.98, 73.95 | Badlands 48.66, 6.78 → Loch Modan 46.98, 82.11 | verified-ground-approach / verified-ground-approach |
| 66 | Badlands 11.10, 24.32 | Loch Modan 23.56, 94.79 | Badlands 16.67, 20.85 → Loch Modan 18.13, 94.79 | verified-ground-approach / verified-ground-approach |
| 67 | Badlands 15.62, 24.32 | Loch Modan 16.77, 94.79 | Badlands 21.19, 20.85 → Loch Modan 22.21, 94.79 | verified-ground-approach / verified-ground-approach |
| 68 | Badlands 56.20, 83.92 | Riverglades 30.50, 33.24 | Badlands 56.20, 92.96 → Riverglades 32.69, 29.96 | verified-ground-approach / verified-ground-approach |
| 69 | Badlands 93.22, 39.45 | Riverglades 51.76, 4.70 | Badlands 93.22, 48.49 → Riverglades 51.76, 7.02 | verified-ground-approach / verified-ground-approach |
| 70 | Badlands 90.91, 50.82 | Riverglades 51.76, 6.25 | Badlands 93.22, 42.46 → Riverglades 51.76, 3.93 | verified-ground-approach / verified-ground-approach |
| 22 | Blasted Lands 52.30, 11.29 | Swamp of Sorrows 33.61, 56.81 | Blasted Lands 52.30, 4.57 → Swamp of Sorrows 33.61, 66.62 | verified-ground-approach / verified-ground-approach |
| 28 | Burning Steppes 78.24, 78.24 | Redridge Mountains 38.91, 11.01 | Burning Steppes 81.86, 83.67 → Redridge Mountains 45.30, 7.05 | verified-ground-approach / verified-ground-approach |
| 29 | Burning Steppes 78.73, 73.64 | Redridge Mountains 41.07, 16.83 | Burning Steppes 78.73, 81.32 → Redridge Mountains 41.07, 6.47 | verified-ground-approach / verified-ground-approach |
| 30 | Burning Steppes 78.24, 78.24 | Riverglades 16.19, 72.62 | Burning Steppes 81.86, 83.67 → Riverglades 16.19, 67.98 | verified-ground-approach / verified-ground-approach |
| 110 | Burning Steppes 25.70, 45.68 | Searing Gorge 34.99, 73.91 | Burning Steppes 30.43, 48.62 → Searing Gorge 34.99, 83.99 | verified-ground-approach / verified-ground-approach |
| 132 | Burning Steppes 60.35, 29.62 | Burning Steppes 65.05, 23.06 | Burning Steppes 65.08, 26.68 → Burning Steppes 65.44, 24.48 | verified-ground-approach / short-verified-ground-approach |
| 133 | Burning Steppes 78.24, 79.91 | Burning Steppes 78.04, 66.95 | Burning Steppes 78.24, 76.07 → Burning Steppes 78.04, 74.63 | verified-ground-approach / verified-ground-approach |
| 134 | Burning Steppes 13.22, 39.51 | Burning Steppes 17.17, 23.95 | Burning Steppes 15.18, 32.41 → Burning Steppes 15.21, 31.05 | verified-ground-approach / verified-with-swimming-fallback |
| 136 | Burning Steppes 80.13, 28.66 | Burning Steppes 86.34, 39.83 | Burning Steppes 80.13, 36.35 → Burning Steppes 81.61, 36.89 | verified-ground-approach / verified-ground-approach |
| 42 | Darkshore 44.62, 91.94 | Ashenvale 26.55, 14.74 | Darkshore 44.62, 95.37 → Ashenvale 29.15, 14.74 | verified-ground-approach / verified-ground-approach |
| 43 | Darkshore 37.31, 94.51 | Ashenvale 18.23, 17.54 | Darkshore 37.31, 97.95 → Ashenvale 20.63, 16.04 | verified-ground-approach / verified-ground-approach |
| 87 | Darkshore 48.44, 73.02 | Felwood 32.64, 51.88 | Darkshore 48.44, 73.71 → Felwood 32.64, 52.66 | short-verified-ground-approach / short-verified-ground-approach |
| 160 | Darkshore 41.26, 71.37 | Darkshore 39.27, 76.69 | Darkshore 41.26, 74.81 → Darkshore 41.39, 75.37 | verified-with-swimming-fallback / verified-ground-approach |
| 162 | Darkshore 38.34, 38.64 | Darkshore 36.93, 45.06 | Darkshore 38.34, 42.08 → Darkshore 38.55, 42.63 | verified-with-swimming-fallback / verified-ground-approach |
| 163 | Darkshore 36.44, 45.95 | Darkshore 38.43, 39.95 | Darkshore 38.06, 43.52 → Darkshore 38.43, 43.38 | verified-ground-approach / verified-ground-approach |
| 164 | Darkshore 39.84, 42.46 | Darkshore 35.91, 45.53 | Darkshore 37.55, 42.46 → Darkshore 37.53, 43.10 | verified-with-swimming-fallback / verified-ground-approach |
| 74 | Deadwind Pass 37.63, 32.93 | Duskwood 89.15, 34.31 | Deadwind Pass 32.08, 36.38 → Duskwood 91.28, 42.01 | verified-ground-approach / verified-ground-approach |
| 75 | Deadwind Pass 29.42, 65.63 | Duskwood 84.88, 66.66 | Deadwind Pass 29.42, 56.63 → Duskwood 88.81, 60.76 | verified-ground-approach / verified-ground-approach |
| 76 | Deadwind Pass 30.75, 59.63 | Duskwood 87.92, 64.18 | Deadwind Pass 30.75, 68.63 → Duskwood 90.05, 71.88 | verified-ground-approach / verified-ground-approach |
| 77 | Deadwind Pass 35.92, 81.38 | Stranglethorn Vale 59.58, 3.13 | Deadwind Pass 35.92, 85.88 → Stranglethorn Vale 61.93, 3.13 | verified-ground-approach / verified-ground-approach |
| 78 | Deadwind Pass 59.92, 40.52 | Swamp of Sorrows 7.41, 63.15 | Deadwind Pass 59.92, 34.88 → Swamp of Sorrows 4.90, 54.09 | verified-ground-approach / verified-ground-approach |
| 79 | Deadwind Pass 54.37, 44.32 | Swamp of Sorrows 10.95, 64.38 | Deadwind Pass 59.92, 40.88 → Swamp of Sorrows 4.90, 60.63 | verified-ground-approach / verified-ground-approach |
| 80 | Deadwind Pass 52.58, 24.63 | Swamp of Sorrows 9.49, 46.67 | Deadwind Pass 58.58, 24.63 → Swamp of Sorrows 3.45, 42.92 | verified-ground-approach / verified-ground-approach |
| 130 | Deadwind Pass 43.67, 25.29 | Deadwind Pass 37.61, 41.00 | Deadwind Pass 43.67, 34.29 → Deadwind Pass 41.86, 34.63 | verified-ground-approach / verified-ground-approach |
| 131 | Deadwind Pass 54.06, 61.65 | Deadwind Pass 45.11, 61.63 | Deadwind Pass 48.06, 61.65 → Deadwind Pass 45.96, 62.90 | verified-ground-approach / short-verified-ground-approach |
| 46 | Desolace 41.40, 92.67 | Feralas 44.99, 5.53 | Desolace 42.68, 97.29 → Feralas 44.99, 2.29 | verified-ground-approach / verified-ground-approach |
| 47 | Desolace 30.35, 92.29 | Feralas 37.02, 6.16 | Desolace 30.35, 97.29 → Feralas 37.02, 2.92 | verified-ground-approach / verified-ground-approach |
| 97 | Desolace 66.03, 79.50 | Shen'dralas 30.13, 9.06 | Desolace 66.03, 84.50 → Shen'dralas 36.89, 13.26 | verified-ground-approach / verified-ground-approach |
| 98 | Desolace 58.53, 86.45 | Shen'dralas 20.83, 23.02 | Desolace 58.53, 91.45 → Shen'dralas 20.83, 28.51 | verified-ground-approach / verified-ground-approach |
| 99 | Desolace 63.18, 75.99 | Shen'dralas 33.64, 16.01 | Desolace 64.46, 80.61 → Shen'dralas 33.64, 5.03 | verified-ground-approach / verified-ground-approach |
| 72 | Dun Morogh 68.97, 10.63 | Wetlands 27.61, 73.17 | Dun Morogh 66.16, 8.88 → Wetlands 25.79, 73.17 | verified-ground-approach / verified-ground-approach |
| 106 | Dun Morogh 82.99, 35.75 | Dun Morogh 78.37, 44.47 | Dun Morogh 82.99, 40.32 → Dun Morogh 81.18, 42.73 | verified-ground-approach / verified-ground-approach |
| 108 | Dun Morogh 87.04, 49.56 | Dun Morogh 80.11, 50.21 | Dun Morogh 84.23, 51.30 → Dun Morogh 82.27, 53.44 | verified-ground-approach / verified-ground-approach |
| 111 | Dun Morogh 51.27, 38.02 | Ironforge 21.12, 57.89 | Dun Morogh 53.42, 34.79 → Ironforge 21.12, 57.89 | verified-ground-approach / interior-floor-approach-required |
| 151 | Dun Morogh 38.72, 33.71 | Dun Morogh 36.62, 39.82 | Dun Morogh 39.89, 37.93 → Dun Morogh 39.66, 39.82 | verified-ground-approach / verified-ground-approach |
| 155 | Dun Morogh 46.92, 38.72 | Dun Morogh 44.23, 45.74 | Dun Morogh 46.92, 43.29 → Dun Morogh 47.04, 44.00 | verified-ground-approach / verified-ground-approach |
| 1 | Durotar 36.70, 23.38 | The Barrens 63.78, 5.20 | Durotar 37.79, 19.44 → The Barrens 64.35, 7.25 | verified-ground-approach / verified-with-swimming-fallback |
| 2 | Durotar 35.97, 34.69 | The Barrens 62.80, 10.93 | Durotar 35.97, 30.44 → The Barrens 63.36, 12.98 | verified-ground-approach / verified-with-swimming-fallback |
| 3 | Durotar 35.26, 38.48 | The Barrens 62.47, 17.34 | Durotar 35.26, 42.73 → The Barrens 63.03, 19.40 | verified-ground-approach / verified-with-swimming-fallback |
| 4 | Durotar 35.88, 28.10 | The Barrens 62.75, 7.49 | Durotar 34.79, 24.17 → The Barrens 62.75, 9.71 | verified-with-swimming-fallback / verified-ground-approach |
| 5 | Durotar 43.03, 15.01 | Orgrimmar 47.28, 77.16 | Durotar 45.04, 12.00 → Orgrimmar 47.28, 93.20 | verified-ground-approach / verified-ground-approach |
| 36 | Duskwood 89.85, 13.49 | Redridge Mountains 7.19, 96.68 | Duskwood 94.98, 10.30 → Redridge Mountains 2.30, 89.35 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 37 | Duskwood 44.83, 76.97 | Stranglethorn Vale 41.80, 2.46 | Duskwood 44.83, 85.30 → Stranglethorn Vale 40.71, 3.13 | verified-ground-approach / verified-ground-approach |
| 38 | Duskwood 11.41, 70.13 | Westfall 67.20, 56.70 | Duskwood 7.48, 64.24 → Westfall 67.20, 63.13 | verified-with-swimming-fallback / verified-ground-approach |
| 145 | Duskwood 88.70, 14.43 | Redridge Mountains 8.26, 93.63 | Duskwood 93.84, 11.24 → Redridge Mountains 1.88, 89.67 | verified-ground-approach / verified-with-swimming-fallback |
| 158 | Dustwallow Marsh 43.38, 21.95 | Dustwallow Marsh 40.61, 28.55 | Dustwallow Marsh 43.38, 26.24 → Dustwallow Marsh 43.25, 26.91 | verified-ground-approach / verified-with-swimming-fallback |
| 159 | Dustwallow Marsh 54.54, 24.51 | Dustwallow Marsh 52.01, 31.16 | Dustwallow Marsh 54.54, 28.80 → Dustwallow Marsh 54.65, 29.52 | verified-with-swimming-fallback / verified-ground-approach |
| 181 | Dustwallow Marsh 63.65, 40.16 | Dustwallow Marsh 63.20, 49.58 | Dustwallow Marsh 63.65, 44.45 → Dustwallow Marsh 64.29, 45.62 | verified-ground-approach / verified-ground-approach |
| 182 | Dustwallow Marsh 36.38, 36.57 | Dustwallow Marsh 33.50, 39.83 | Dustwallow Marsh 36.38, 40.86 → Dustwallow Marsh 36.14, 41.47 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 183 | Dustwallow Marsh 36.52, 38.76 | Dustwallow Marsh 39.34, 32.13 | Dustwallow Marsh 39.16, 37.12 → Dustwallow Marsh 39.34, 36.42 | verified-ground-approach / verified-with-swimming-fallback |
| 184 | Dustwallow Marsh 39.43, 30.66 | Dustwallow Marsh 36.56, 35.72 | Dustwallow Marsh 39.43, 34.95 → Dustwallow Marsh 39.42, 35.72 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 185 | Dustwallow Marsh 36.55, 33.82 | Dustwallow Marsh 39.40, 28.80 | Dustwallow Marsh 39.40, 33.82 → Dustwallow Marsh 39.40, 33.08 | verified-with-swimming-fallback / verified-ground-approach |
| 186 | Dustwallow Marsh 39.11, 64.70 | Dustwallow Marsh 40.50, 63.44 | Dustwallow Marsh 41.13, 67.73 → Dustwallow Marsh 41.60, 67.40 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 31 | Elwynn Forest 91.50, 78.62 | Duskwood 88.62, 14.42 | Elwynn Forest 93.16, 84.61 → Duskwood 93.75, 11.23 | verified-with-swimming-fallback / verified-ground-approach |
| 32 | Elwynn Forest 90.12, 69.89 | Redridge Mountains 5.14, 81.37 | Elwynn Forest 94.12, 72.37 → Redridge Mountains 2.50, 71.80 | verified-ground-approach / verified-ground-approach |
| 33 | Elwynn Forest 91.50, 77.90 | Redridge Mountains 8.11, 94.18 | Elwynn Forest 93.16, 83.89 → Redridge Mountains 1.73, 90.22 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 34 | Elwynn Forest 21.13, 72.55 | Westfall 59.73, 9.86 | Elwynn Forest 21.13, 79.03 → Westfall 61.37, 15.80 | verified-ground-approach / verified-with-swimming-fallback |
| 35 | Elwynn Forest 31.00, 56.21 | Stormwind City 76.02, 85.79 | Elwynn Forest 32.65, 50.23 → Stormwind City 76.02, 92.27 | verified-ground-approach / verified-ground-approach |
| 137 | Elwynn Forest 52.56, 38.43 | Elwynn Forest 51.42, 51.68 | Elwynn Forest 52.56, 44.91 → Elwynn Forest 53.07, 45.69 | verified-ground-approach / verified-ground-approach |
| 140 | Elwynn Forest 28.33, 71.39 | Elwynn Forest 30.67, 83.94 | Elwynn Forest 28.33, 77.87 → Elwynn Forest 29.02, 77.95 | verified-ground-approach / verified-ground-approach |
| 144 | Elwynn Forest 74.92, 66.01 | Elwynn Forest 72.59, 66.63 | Elwynn Forest 74.92, 72.49 → Elwynn Forest 74.25, 72.62 | verified-with-swimming-fallback / verified-ground-approach |
| 113 | Felwood 63.21, 11.00 | Moonglade 35.66, 62.74 | Felwood 65.05, 8.24 → Moonglade 35.66, 72.48 | verified-ground-approach / verified-ground-approach |
| 114 | Felwood 63.21, 11.00 | Winterspring 27.89, 34.43 | Felwood 65.05, 8.24 → Winterspring 27.89, 34.43 | verified-ground-approach / interior-floor-approach-required |
| 120 | Felwood 40.98, 44.00 | Felwood 38.59, 50.19 | Felwood 40.98, 47.91 → Felwood 41.00, 48.70 | verified-ground-approach / verified-ground-approach |
| 121 | Felwood 43.43, 70.84 | Felwood 41.93, 78.10 | Felwood 43.43, 74.75 → Felwood 43.77, 75.33 | verified-ground-approach / verified-ground-approach |
| 100 | Feralas 54.96, 10.45 | Shen'dralas 25.05, 69.58 | Feralas 55.73, 9.31 → Shen'dralas 22.46, 65.70 | verified-ground-approach / verified-ground-approach |
| 122 | Feralas 48.86, 42.34 | Feralas 50.58, 49.14 | Feralas 48.86, 45.58 → Feralas 49.05, 46.85 | verified-ground-approach / verified-ground-approach |
| 168 | Feralas 75.90, 40.32 | Feralas 74.75, 40.67 | Feralas 75.90, 43.55 → Feralas 75.58, 43.66 | verified-ground-approach / verified-ground-approach |
| 169 | Feralas 64.50, 50.01 | Feralas 61.25, 52.43 | Feralas 63.74, 51.16 → Feralas 63.41, 52.43 | verified-ground-approach / verified-ground-approach |
| 178 | Feralas 39.73, 8.36 | Feralas 37.52, 10.79 | Feralas 39.73, 11.60 → Feralas 39.51, 12.03 | verified-ground-approach / verified-ground-approach |
| 27 | Hillsbrad Foothills 87.25, 30.07 | The Hinterlands 9.41, 56.18 | Hillsbrad Foothills 90.56, 25.10 → The Hinterlands 6.66, 60.31 | verified-ground-approach / verified-ground-approach |
| 141 | Hillsbrad Foothills 62.48, 34.42 | Hillsbrad Foothills 63.15, 48.75 | Hillsbrad Foothills 62.48, 41.46 → Hillsbrad Foothills 63.15, 41.72 | verified-ground-approach / verified-ground-approach |
| 81 | Loch Modan 16.77, 4.42 | Wetlands 49.97, 87.68 | Loch Modan 22.21, 4.42 → Wetlands 53.60, 87.68 | verified-ground-approach / verified-ground-approach |
| 82 | Loch Modan 15.86, 4.42 | Wetlands 49.37, 87.68 | Loch Modan 18.58, 4.42 → Wetlands 51.18, 87.68 | verified-ground-approach / verified-ground-approach |
| 83 | Loch Modan 19.98, 7.54 | Wetlands 46.20, 83.83 | Loch Modan 14.95, 4.42 → Wetlands 48.77, 87.68 | verified-ground-approach / verified-ground-approach |
| 105 | Loch Modan 24.18, 20.39 | Dun Morogh 82.25, 34.26 | Loch Modan 19.16, 17.27 → Dun Morogh 84.41, 31.03 | verified-ground-approach / verified-ground-approach |
| 107 | Loch Modan 21.51, 65.64 | Dun Morogh 86.24, 46.75 | Loch Modan 19.59, 62.75 → Dun Morogh 86.24, 51.32 | verified-ground-approach / verified-ground-approach |
| 115 | Moonglade 35.66, 62.74 | Winterspring 27.89, 34.43 | Moonglade 35.66, 72.48 → Winterspring 27.89, 34.43 | verified-ground-approach / interior-floor-approach-required |
| 170 | Moonglade 39.12, 54.01 | Moonglade 44.67, 71.11 | Moonglade 43.72, 60.90 → Moonglade 44.67, 61.36 | verified-ground-approach / verified-with-swimming-fallback |
| 171 | Moonglade 41.88, 55.27 | Moonglade 45.06, 71.85 | Moonglade 46.48, 62.16 → Moonglade 47.54, 62.85 | verified-with-swimming-fallback / verified-ground-approach |
| 172 | Moonglade 44.98, 33.17 | Moonglade 56.82, 36.15 | Moonglade 49.58, 40.06 → Moonglade 50.81, 39.88 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 173 | Moonglade 43.51, 34.19 | Moonglade 57.27, 37.73 | Moonglade 49.51, 37.92 → Moonglade 50.77, 37.73 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 174 | Moonglade 42.84, 33.73 | Moonglade 52.93, 42.51 | Moonglade 49.34, 33.73 → Moonglade 50.45, 33.51 | verified-with-swimming-fallback / verified-with-swimming-fallback |
| 175 | Mount Hyjal 64.34, 83.45 | Mount Hyjal 55.14, 84.33 | Mount Hyjal 60.02, 83.45 → Mount Hyjal 59.46, 84.33 | verified-ground-approach / verified-ground-approach |
| 177 | Mount Hyjal 76.27, 39.52 | Mount Hyjal 81.79, 40.87 | Mount Hyjal 77.92, 45.50 → Mount Hyjal 78.73, 45.45 | verified-ground-approach / verified-ground-approach |
| 180 | Mount Hyjal 40.26, 44.07 | Mount Hyjal 41.62, 51.88 | Mount Hyjal 41.05, 44.56 → Mount Hyjal 41.62, 45.40 | short-verified-ground-approach / verified-ground-approach |
| 6 | Mulgore 63.44, 61.15 | The Barrens 41.04, 56.40 | Mulgore 65.17, 63.74 → The Barrens 41.04, 58.62 | verified-ground-approach / verified-ground-approach |
| 7 | Mulgore 35.95, 11.48 | Stonetalon Mountains 62.10, 96.07 | Mulgore 37.68, 14.07 → Stonetalon Mountains 63.18, 97.70 | verified-ground-approach / verified-ground-approach |
| 8 | Mulgore 38.59, 41.24 | Thunder Bluff 47.39, 77.99 | Mulgore 40.32, 43.83 → Thunder Bluff 52.89, 97.90 | verified-ground-approach / verified-ground-approach |
| 9 | Mulgore 36.87, 41.80 | Thunder Bluff 30.44, 70.49 | Mulgore 39.30, 41.80 → Thunder Bluff 43.71, 78.74 | verified-ground-approach / verified-ground-approach |
| 10 | Mulgore 35.56, 39.28 | Thunder Bluff 29.43, 55.83 | Mulgore 37.81, 40.68 → Thunder Bluff 34.93, 75.75 | verified-ground-approach / verified-ground-approach |
| 48 | Mulgore 33.70, 24.91 | Desolace 79.71, 34.96 | Mulgore 31.45, 23.51 → Desolace 82.07, 38.50 | verified-ground-approach / verified-ground-approach |
| 49 | Mulgore 31.65, 11.43 | Desolace 82.25, 25.82 | Mulgore 31.65, 15.08 → Desolace 82.25, 26.82 | verified-ground-approach / short-verified-ground-approach |
| 50 | Mulgore 32.58, 15.62 | Desolace 82.25, 20.43 | Mulgore 31.65, 12.24 → Desolace 82.25, 22.93 | verified-ground-approach / verified-ground-approach |
| 51 | Mulgore 34.16, 59.87 | Shen'dralas 71.85, 22.71 | Mulgore 33.82, 60.39 → Shen'dralas 79.17, 22.71 | short-verified-ground-approach / verified-ground-approach |
| 52 | Mulgore 33.82, 83.04 | Shen'dralas 75.51, 85.21 | Mulgore 33.82, 81.21 → Shen'dralas 79.17, 85.21 | verified-ground-approach / verified-ground-approach |
| 53 | Mulgore 33.82, 81.82 | Shen'dralas 79.17, 87.04 | Mulgore 33.82, 83.65 → Shen'dralas 79.17, 92.53 | verified-ground-approach / verified-ground-approach |
| 179 | Mulgore 36.42, 41.17 | Mulgore 37.41, 44.20 | Mulgore 38.86, 41.17 → Mulgore 39.13, 41.61 | verified-ground-approach / verified-ground-approach |
| 39 | Redridge Mountains 64.53, 29.57 | Riverglades 25.73, 68.49 | Redridge Mountains 67.18, 20.00 → Riverglades 25.73, 73.13 | verified-ground-approach / verified-ground-approach |
| 40 | Redridge Mountains 38.91, 12.74 | Riverglades 18.88, 70.91 | Redridge Mountains 45.30, 8.78 → Riverglades 16.02, 69.14 | verified-ground-approach / verified-ground-approach |
| 84 | Redridge Mountains 45.31, 91.24 | Swamp of Sorrows 29.93, 27.45 | Redridge Mountains 53.93, 91.37 → Swamp of Sorrows 27.43, 18.39 | verified-ground-approach / verified-ground-approach |
| 85 | Redridge Mountains 53.35, 91.24 | Swamp of Sorrows 18.69, 19.78 | Redridge Mountains 45.68, 91.37 → Swamp of Sorrows 19.62, 18.39 | verified-ground-approach / short-verified-ground-approach |
| 117 | Riverglades 63.07, 36.29 | Riverglades 69.31, 32.67 | Riverglades 66.16, 36.29 → Riverglades 66.45, 34.44 | verified-with-swimming-fallback / verified-ground-approach |
| 152 | Riverglades 23.45, 71.47 | Riverglades 18.73, 67.25 | Riverglades 22.26, 67.18 → Riverglades 21.82, 67.25 | verified-with-swimming-fallback / verified-ground-approach |
| 153 | Riverglades 40.35, 44.54 | Riverglades 43.88, 51.56 | Riverglades 43.21, 46.31 → Riverglades 43.88, 46.92 | verified-ground-approach / verified-ground-approach |
| 154 | Riverglades 77.92, 33.16 | Riverglades 72.36, 28.89 | Riverglades 75.07, 31.39 → Riverglades 74.54, 32.17 | verified-ground-approach / verified-ground-approach |
| 73 | Searing Gorge 85.29, 4.68 | Loch Modan 19.03, 94.56 | Searing Gorge 91.50, 8.54 → Loch Modan 13.60, 94.56 | verified-ground-approach / verified-ground-approach |
| 135 | Searing Gorge 35.08, 64.48 | Searing Gorge 44.96, 69.86 | Searing Gorge 37.65, 73.79 → Searing Gorge 38.75, 73.72 | verified-ground-approach / verified-ground-approach |
| 25 | Silverpine Forest 65.28, 75.90 | Hillsbrad Foothills 18.85, 48.88 | Silverpine Forest 67.81, 79.69 → Hillsbrad Foothills 14.52, 46.19 | verified-ground-approach / verified-ground-approach |
| 118 | Silverpine Forest 41.74, 79.93 | Silverpine Forest 45.31, 71.30 | Silverpine Forest 45.31, 79.93 → Silverpine Forest 45.31, 76.66 | verified-ground-approach / verified-ground-approach |
| 156 | Silverpine Forest 46.45, 32.11 | Silverpine Forest 49.74, 23.48 | Silverpine Forest 49.75, 30.06 → Silverpine Forest 49.74, 28.84 | verified-ground-approach / verified-ground-approach |
| 96 | Stonetalon Mountains 29.82, 73.64 | Desolace 52.00, 6.46 | Stonetalon Mountains 29.82, 78.25 → Desolace 54.36, 2.92 | verified-ground-approach / verified-ground-approach |
| 86 | Stranglethorn Vale 29.42, 2.35 | Westfall 72.59, 73.97 | Stranglethorn Vale 28.24, 2.35 → Westfall 74.23, 79.91 | verified-ground-approach / verified-ground-approach |
| 127 | Stranglethorn Vale 26.19, 59.72 | Stranglethorn Vale 30.87, 59.54 | Stranglethorn Vale 28.36, 58.37 → Stranglethorn Vale 28.69, 58.19 | verified-with-swimming-fallback / verified-ground-approach |
| 128 | Stranglethorn Vale 24.86, 58.90 | Stranglethorn Vale 27.62, 55.00 | Stranglethorn Vale 27.21, 58.90 → Stranglethorn Vale 27.62, 58.53 | verified-ground-approach / verified-with-swimming-fallback |
| 150 | Stranglethorn Vale 14.87, 12.05 | Stranglethorn Vale 14.76, 17.50 | Stranglethorn Vale 14.42, 13.68 → Stranglethorn Vale 14.76, 13.97 | verified-with-swimming-fallback / verified-ground-approach |
| 192 | Duskwood 44.83, 76.97 | Stranglethorn Vale 39.20, 6.56 | Stranglethorn Vale 40.56, 3.27 → Stranglethorn Vale 40.87, 4.06 | dry via link 37 / verified-ground-approach |
| 147 | Swamp of Sorrows 23.31, 37.99 | Swamp of Sorrows 17.60, 41.90 | Swamp of Sorrows 23.31, 47.80 → Swamp of Sorrows 22.23, 48.83 | verified-with-swimming-fallback / verified-ground-approach |
| 101 | Tanaris 27.80, 50.84 | Un'Goro Crater 71.37, 84.84 | Tanaris 28.20, 50.59 → Un'Goro Crater 72.92, 90.46 | short-verified-ground-approach / verified-ground-approach |
| 102 | Tanaris 25.27, 53.62 | Un'Goro Crater 70.33, 88.77 | Tanaris 26.81, 51.31 → Un'Goro Crater 70.33, 91.81 | verified-ground-approach / verified-ground-approach |
| 103 | Tanaris 34.06, 28.76 | Un'Goro Crater 83.73, 49.92 | Tanaris 34.06, 32.02 → Un'Goro Crater 83.73, 56.00 | verified-ground-approach / verified-ground-approach |
| 41 | Teldrassil 38.66, 57.27 | Darnassus 83.04, 15.02 | Teldrassil 36.58, 54.14 → Darnassus 88.47, 34.65 | verified-ground-approach / verified-ground-approach |
| 161 | Teldrassil 43.37, 46.31 | Teldrassil 41.45, 49.23 | Teldrassil 44.50, 50.40 → Teldrassil 44.17, 50.92 | verified-ground-approach / verified-ground-approach |
| 11 | The Barrens 46.82, 5.01 | Ashenvale 68.68, 82.93 | The Barrens 48.19, 4.16 → Ashenvale 68.68, 86.83 | verified-ground-approach / verified-ground-approach |
| 12 | The Barrens 50.42, 77.60 | Dustwallow Marsh 29.88, 43.75 | The Barrens 50.99, 79.65 → Dustwallow Marsh 29.88, 48.04 | verified-ground-approach / verified-ground-approach |
| 13 | The Barrens 50.53, 75.39 | Dustwallow Marsh 31.87, 47.08 | The Barrens 50.53, 77.61 → Dustwallow Marsh 29.01, 47.08 | verified-ground-approach / verified-ground-approach |
| 14 | The Barrens 49.71, 76.32 | Dustwallow Marsh 29.48, 43.15 | The Barrens 49.71, 78.54 → Dustwallow Marsh 29.48, 47.44 | verified-ground-approach / verified-ground-approach |
| 54 | The Barrens 35.02, 29.34 | Stonetalon Mountains 81.10, 96.67 | The Barrens 34.46, 27.29 → Stonetalon Mountains 84.17, 96.67 | verified-ground-approach / verified-ground-approach |
| 55 | The Barrens 35.28, 28.40 | Stonetalon Mountains 80.64, 95.72 | The Barrens 33.80, 28.40 → Stonetalon Mountains 82.81, 98.98 | verified-ground-approach / verified-ground-approach |
| 56 | The Barrens 35.86, 17.10 | Stonetalon Mountains 88.27, 78.86 | The Barrens 36.43, 19.15 → Stonetalon Mountains 88.27, 79.78 | verified-ground-approach / short-verified-ground-approach |
| 123 | The Barrens 62.68, 17.00 | Durotar 34.60, 46.55 | The Barrens 62.68, 19.22 → Durotar 34.60, 42.30 | verified-ground-approach / verified-ground-approach |
| 124 | The Barrens 50.81, 46.02 | The Barrens 50.01, 50.51 | The Barrens 50.81, 48.24 → The Barrens 51.06, 48.94 | verified-ground-approach / verified-ground-approach |
| 45 | Thousand Needles 9.12, 15.45 | Feralas 88.65, 37.97 | Thousand Needles 7.81, 10.72 → Feralas 89.48, 40.96 | verified-ground-approach / verified-ground-approach |
| 90 | Thousand Needles 60.42, 46.73 | Dustwallow Marsh 45.28, 91.37 | Thousand Needles 62.83, 43.11 → Dustwallow Marsh 42.42, 91.37 | verified-ground-approach / verified-ground-approach |
| 91 | Thousand Needles 61.95, 45.21 | Dustwallow Marsh 42.82, 91.37 | Thousand Needles 65.10, 43.25 → Dustwallow Marsh 44.25, 91.37 | verified-ground-approach / verified-ground-approach |
| 92 | Thousand Needles 93.42, 24.50 | Dustwallow Marsh 67.76, 70.58 | Thousand Needles 93.42, 19.39 → Dustwallow Marsh 67.98, 71.37 | verified-ground-approach / short-verified-ground-approach |
| 93 | Thousand Needles 75.71, 92.54 | Tanaris 52.22, 23.89 | Thousand Needles 75.71, 97.66 → Tanaris 51.39, 20.88 | verified-ground-approach / verified-ground-approach |
| 94 | Thousand Needles 91.83, 61.97 | Tanaris 62.56, 4.30 | Thousand Needles 93.13, 66.69 → Tanaris 62.56, 1.04 | verified-ground-approach / verified-ground-approach |
| 95 | Thousand Needles 91.83, 65.66 | Tanaris 63.39, 6.41 | Thousand Needles 93.13, 70.38 → Tanaris 62.56, 3.40 | verified-ground-approach / verified-ground-approach |
| 23 | Tirisfal Glades 54.63, 69.64 | Silverpine Forest 65.13, 4.84 | Tirisfal Glades 54.63, 74.62 → Silverpine Forest 68.70, 4.84 | verified-ground-approach / verified-ground-approach |
| 24 | Tirisfal Glades 84.79, 65.35 | Western Plaguelands 30.81, 61.19 | Tirisfal Glades 84.79, 70.33 → Western Plaguelands 28.34, 57.49 | verified-ground-approach / verified-ground-approach |
| 112 | Tirisfal Glades 51.14, 66.72 | Undercity 45.33, 39.77 | Tirisfal Glades 51.14, 71.70 → Undercity 45.33, 39.77 | verified-ground-approach / interior-floor-approach-required |
| 138 | Tirisfal Glades 49.27, 54.37 | Tirisfal Glades 53.53, 48.36 | Tirisfal Glades 52.59, 54.37 → Tirisfal Glades 53.53, 53.34 | verified-ground-approach / verified-ground-approach |
| 104 | Un'Goro Crater 29.95, 15.03 | Silithus 82.21, 14.22 | Un'Goro Crater 27.08, 10.73 → Silithus 86.18, 11.75 | verified-ground-approach / verified-ground-approach |
| 157 | Un'Goro Crater 53.03, 37.13 | Un'Goro Crater 52.30, 45.46 | Un'Goro Crater 53.03, 43.21 → Un'Goro Crater 52.88, 44.60 | verified-with-swimming-fallback / short-verified-ground-approach |
| 26 | Western Plaguelands 68.58, 45.53 | Eastern Plaguelands 8.91, 56.47 | Western Plaguelands 69.91, 50.36 → Eastern Plaguelands 8.91, 61.70 | verified-with-swimming-fallback / verified-ground-approach |
| 71 | Western Plaguelands 64.41, 84.63 | The Hinterlands 22.00, 27.14 | Western Plaguelands 65.75, 89.46 → The Hinterlands 21.70, 26.06 | verified-ground-approach / short-verified-ground-approach |
| 146 | Western Plaguelands 68.50, 45.44 | Eastern Plaguelands 8.83, 56.41 | Western Plaguelands 69.83, 50.28 → Eastern Plaguelands 8.83, 61.64 | verified-ground-approach / verified-ground-approach |
| 148 | Western Plaguelands 64.35, 84.26 | Western Plaguelands 68.07, 77.29 | Western Plaguelands 67.84, 84.26 → Western Plaguelands 68.07, 82.52 | verified-ground-approach / verified-ground-approach |
| 149 | Western Plaguelands 48.43, 66.53 | Western Plaguelands 47.89, 77.95 | Western Plaguelands 48.43, 71.77 → Western Plaguelands 49.22, 73.11 | verified-ground-approach / verified-ground-approach |
| 129 | Westfall 67.39, 56.40 | Duskwood 12.70, 69.66 | Westfall 67.39, 62.83 → Duskwood 8.77, 63.77 | verified-ground-approach / verified-ground-approach |
| 139 | Westfall 60.08, 12.12 | Elwynn Forest 20.70, 73.34 | Westfall 61.72, 18.06 → Elwynn Forest 20.70, 79.82 | verified-ground-approach / verified-ground-approach |
| 119 | Wetlands 15.65, 48.43 | Wetlands 7.39, 54.30 | Wetlands 12.30, 50.51 → Wetlands 11.02, 54.30 | verified-ground-approach / verified-ground-approach |
| 142 | Wetlands 49.67, 31.28 | Wetlands 46.50, 39.63 | Wetlands 49.67, 36.72 → Wetlands 49.85, 37.54 | verified-ground-approach / verified-ground-approach |
| 193 | Wetlands 54.95, 82.36 | Loch Modan 21.73, 16.09 | Wetlands 55.65, 84.88 → Loch Modan 25.57, 10.33 | verified-ground-approach / verified-ground-approach |
| 194 | Wetlands 50.61, 77.13 | Wetlands 56.98, 83.54 | Wetlands 50.61, 82.58 → Wetlands 55.17, 83.54 | verified-ground-approach / verified-ground-approach |
| 195 | Wetlands 50.13, 68.80 | Wetlands 49.48, 80.94 | Wetlands 50.13, 71.52 → Wetlands 50.17, 78.42 | verified-ground-approach / verified-ground-approach |
| 196 | Wetlands 53.89, 64.89 | Wetlands 48.59, 68.06 | Wetlands 53.89, 70.33 → Wetlands 49.29, 70.57 | verified-ground-approach / verified-ground-approach |
| 176 | Winterspring 62.39, 64.46 | Winterspring 59.82, 70.48 | Winterspring 62.39, 67.63 → Winterspring 61.93, 70.48 | verified-ground-approach / verified-ground-approach |

## Withheld shortcuts needing specific evidence

These exact old handoffs failed the bounded nearby-ground approach audit. They are withheld, not declared physically impassable. A live route showing how to approach them can justify a new source-backed handoff. These numbers are historical IDs, not current link IDs.

| Previous link | Zones | Previous handoffs |
| --- | --- | --- |
| 28 | Dun Morogh / Wetlands | Dun Morogh 65.06, 8.88 → Wetlands 24.48, 73.17 |
| 40 | Redridge Mountains / Riverglades | Redridge Mountains 85.22, 30.36 → Riverglades 34.58, 78.80 |
| 50 | Durotar / Ashenvale | Durotar 27.86, 9.40 → Ashenvale 88.98, 83.14 |
| 64 | Alterac Mountains / The Hinterlands | Alterac Mountains 91.00, 50.33 → The Hinterlands 5.03, 35.31 |
| 76 | Western Plaguelands / The Hinterlands | Western Plaguelands 50.82, 97.60 → The Hinterlands 5.03, 35.15 |
| 84 | Deadwind Pass / Swamp of Sorrows | Deadwind Pass 62.58, 48.13 → Swamp of Sorrows 7.63, 68.26 |
| 94 | Ashenvale / Azshara | Ashenvale 98.23, 30.79 → Azshara 13.64, 54.78 |
| 106 | Feralas / Shen'dralas | Feralas 55.73, 12.10 → Shen'dralas 22.46, 75.15 |
| 28 | Dun Morogh / Wetlands | Dun Morogh 64.97, 8.88 → Wetlands 24.38, 73.17 |
| 62 | Alterac Mountains / The Hinterlands | Alterac Mountains 91.00, 50.11 → The Hinterlands 5.03, 35.15 |
| 74 | Western Plaguelands / The Hinterlands | Western Plaguelands 51.50, 96.58 → The Hinterlands 5.90, 33.85 |
| 82 | Deadwind Pass / Swamp of Sorrows | Deadwind Pass 62.58, 48.13 → Swamp of Sorrows 7.81, 68.53 |
| 28 | Dun Morogh / Wetlands | Dun Morogh 64.89, 8.88 → Wetlands 24.28, 72.71 |
| 73 | Western Plaguelands / The Hinterlands | Western Plaguelands 51.89, 96.44 → The Hinterlands 6.22, 33.85 |
| 72 | Western Plaguelands / The Hinterlands | Western Plaguelands 52.28, 96.44 → The Hinterlands 6.66, 33.85 |
| 73 | Dun Morogh / Wetlands | Dun Morogh 65.14, 8.88 → Wetlands 24.58, 73.17 |
| 72 | Western Plaguelands / The Hinterlands | Western Plaguelands 52.18, 96.44 → The Hinterlands 6.55, 33.85 |
| 73 | Dun Morogh / Wetlands | Dun Morogh 64.89, 8.88 → Wetlands 24.28, 73.17 |

## Remaining source limits

The 73-map discovery inventory includes instances, test maps and continents; terrain routing covers 55 UI zone/capital/battleground maps. These counts do not imply eighteen missing ordinary zones. Four native-map WDT limitations and every unsupported candidate remain in `bridges-and-crossings-audit.md` and its machine-readable manifest.

Ownership borders with no certified exit remain unresolved; ocean, cliff and overlapping-artwork adjacencies never become walking permission by inference. Missing terrain masks require a new source/extraction task before they can be certified. Live acceptance can establish gameplay behaviour but does not substitute for missing collision provenance.
