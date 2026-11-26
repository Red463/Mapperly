# Mapperly route-generation survey — 25 November 2026

**42 distinct routes; 262 completed measurement records; 218 successes; 44 failures/timeouts/harness errors.** Counts include cold and immediate-repeat runs and all configurations; they are not distinct destinations.

Primary survey: 41 routes measured so far; 13 failing route/road-mode combinations across 9 distinct routes.

## Method and limits

- Production Lua 5.1 planner and all current terrain, water, roads, structures, docks, transports, trams and shipped walking paths. No routing algorithm or permission changes were made.
- Cold = fresh Lua runtime with shipped precomputed paths but no session history. Warm = immediate identical retry in that runtime. Setup and post-plan geometry validation are outside the route timer.
- Tables report measured host computation elapsed seconds. These are **not live in-game timings**. Benchmarks run sequentially, so separate route tests do not compete for CPU.
- `modeled60fpsSeconds` is a scheduling estimate only: one actual PlanningJob.Step per hypothetical 60fps frame, using a real monotonic host clock for the four-millisecond slice budget. It excludes game load, UI rendering and hardware differences. It is not a measurement or promise of game latency.
- Zone count includes start and destination: two zones means one border. Categories use the minimum supported walking-graph chain; the actual selected route can cross different/more zones or use a transport. Controlled walking-only rows exclude transports; primary rows retain normal transport choices.
- Primary characters have no recorded flight offers. Targeted flight runs use an explicitly synthetic recorded character with native same-faction segment chains between selected hubs. This does not test or assume the user’s own flight knowledge.
- Coordinates are retained in matrix.json. Named town anchors move at most 60 yards to permitted ground when needed; all movement is recorded. A permitted cell is not proof of physical reachability or safety from hostile NPCs.
- Avoid swimming is off unless flagged. Road keys: light=1, moderate=2, normal=Balanced (3), firm=4, strong=5; Off disables road preference. Other strengths and swimming comparisons are labelled separately.
- A 45-second per-plan host safety limit cancels the benchmark (timeout ≠ proven no route). Budget errors are the planner’s actual failures. Failed repeated attempts remain recorded. Native-floor guidance and Ironforge wayfinding are not live collision certificates.

## Reported route: Ratchet → Shimmering Flats

Swimming is permitted. Coordinates are inferred town-area points: Ratchet 62.4, 37.8; Thousand Needles 78.0, 75.0. No user flight-knowledge snapshot was supplied. These runs use the normal transport settings without recorded flight offers.

| Roads | Cold host s | Repeat host s | Cold 60fps model s | Cold result | Repeat result | Cold vehicle |
| --- | ---: | ---: | ---: | --- | --- | --- |
| off | 18.886 | 14.7653 | 56.936 | ok | ok | lift: The Great Lift |
| light | 27.041 | 26.1428 | 74.823 | failed | ok | — |
| moderate | 25.400 | 23.1949 | 71.630 | failed | ok | — |
| Balanced | 23.836 | 25.9874 | 68.745 | failed | failed | — |
| firm | 25.739 | 22.1015 | 71.951 | failed | failed | — |
| strong | 20.879 | 23.4623 | 66.107 | failed | failed | — |


## Primary cold timing by minimum walking zone count

| Zones | Road mode | Attempts | Success | Failed | Median host s | Worst host s |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | off | 2 | 2 | 0 | 0.327 | 0.642 |
| 1 | firm | 2 | 2 | 0 | 0.831 | 1.432 |
| 2 | off | 7 | 6 | 1 | 0.685 | 19.706 |
| 2 | firm | 7 | 5 | 2 | 1.810 | 21.892 |
| 3 | off | 4 | 4 | 0 | 0.879 | 15.746 |
| 3 | firm | 4 | 3 | 1 | 1.865 | 19.507 |
| 4 | off | 4 | 4 | 0 | 1.167 | 5.180 |
| 4 | firm | 4 | 4 | 0 | 4.043 | 14.548 |
| 5 | off | 4 | 4 | 0 | 2.521 | 6.932 |
| 5 | firm | 4 | 4 | 0 | 7.884 | 19.949 |
| 6 | off | 5 | 4 | 1 | 3.741 | 25.299 |
| 6 | firm | 5 | 3 | 2 | 6.102 | 24.228 |
| 7 | off | 4 | 4 | 0 | 3.610 | 16.099 |
| 7 | firm | 4 | 3 | 1 | 8.221 | 19.265 |
| 8+ | off | 4 | 2 | 2 | 9.352 | 20.040 |
| 8+ | firm | 4 | 2 | 2 | 10.092 | 22.142 |
| cross-continent | off | 7 | 7 | 0 | 0.079 | 7.978 |
| cross-continent | firm | 7 | 6 | 1 | 0.131 | 20.656 |

## Every primary route

Seconds below are measured host computation. `FAIL` and `TIMEOUT` retain elapsed time; a fast failure does not count as a fast usable route.

| ID | Zones | Route | Off cold / warm s | Firm cold / warm s |
| --- | --- | --- | --- | --- |
| R01 | 1 | Goldshire → Eastvale | 0.012 / 0.007 | 0.231 / 0.007 |
| R02 | 1 | Astranaar → Ashenvale east | 0.642 / 0.008 | 1.432 / 0.009 |
| R03 | 2 | Razor Hill → Orgrimmar | 0.044 / 0.018 | 0.079 / 0.019 |
| R04 | 2 | Goldshire → Darkshire | 0.685 / 0.027 | 1.810 / 0.029 |
| R05 | 6 | Darkshire → Kharanos | 3.288 / 0.078 | 4.813 / 0.078 |
| R06 | 2 | Ashenvale east → Azshara bank | 0.045 / 0.018 | 0.088 / 0.024 |
| R07 | 2 | Aerie Peak → Chillwind | 0.256 / 0.025 | 1.350 / 0.027 |
| R08 | 2 | Booty Bay → Darkshire | 19.706 FAILED / 18.965 FAILED | 21.892 FAILED / 21.060 FAILED |
| R09 | 2 | Ashenvale east → Auberdine | 7.988 / 0.040 | 17.266 FAILED / 21.470 FAILED |
| R10 | 2 | Astranaar → Azshara bank | 1.259 / 0.021 | 4.783 / 3.032 |
| R11 | 3 | Brill → Tarren Mill | 0.300 / 0.021 | 0.740 / 0.023 |
| R12 | 3 | Kharanos → Refuge Pointe | 1.371 / 0.035 | 2.990 / 0.039 |
| R13 | 3 | Bloodhoof → Camp Mojache | 15.746 / 4.487 | 19.507 FAILED / 19.499 FAILED |
| R14 | 3 | Cenarion Hold → Gadgetzan | 0.387 / 0.031 | 0.398 / 0.032 |
| R15 | 4 | Lakeshire → Thelsamar | 0.372 / 0.026 | 0.685 / 0.031 |
| R16 | 4 | Lights Hope → Southshore | 0.335 / 0.026 | 3.288 / 0.035 |
| R17 | 4 | Crossroads → Everlook | 5.180 / 0.098 | 14.548 / 0.124 |
| R18 | 4 | Emerald Sanctuary → Razor Hill | 1.962 / 0.038 | 4.798 / 0.050 |
| R19 | 5 | Chillwind → Menethil | 0.330 / 0.025 | 3.413 / 0.042 |
| R20 | 5 | Eastvale → Thelsamar | 0.702 / 0.029 | 2.861 / 0.048 |
| R21 | 5 | Marshals Refuge → Ratchet | 6.932 / 0.090 | 19.949 / 8.734 |
| R22 | 5 | Moonglade → Shadowprey | 4.340 / 0.075 | 12.355 / 0.078 |
| R23 | 6 | Goldshire → Kharanos | 0.065 / 0.022 | 0.145 / 0.020 |
| R24 | 6 | Darkshire → Menethil | 3.741 / 0.070 | 6.102 / 0.087 |
| R25 | 6 | Camp Mojache → Orgrimmar | 25.299 FAILED / 16.729 | 24.228 FAILED / 23.669 FAILED |
| R26 | 6 | Everlook → Feathermoon | 15.120 / 2.265 | 20.062 FAILED / 19.036 |
| R27 | 7 | Eastvale → Refuge Pointe | 4.831 / 3.764 | 11.619 / 2.798 |
| R28 | 7 | Kharanos → Sentinel Hill | 0.134 / 0.023 | 0.477 / 0.024 |
| R29 | 7 | Cenarion Hold → Sun Rock | 16.099 / 0.192 | 19.265 FAILED / 21.241 FAILED |
| R30 | 7 | Auberdine → Marshals Refuge | 2.388 / 0.302 | 4.823 / 0.152 |
| R31 | 8+ | Aerie Peak → Stormwind | 0.272 / 0.024 | 1.266 / 0.030 |
| R32 | 8+ | Booty Bay → Sepulcher | 0.300 / 0.026 | 1.608 / 0.024 |
| R33 | 8+ | Azshara bank → Cenarion Hold | 18.404 FAILED / 17.502 FAILED | 22.142 FAILED / 18.757 FAILED |
| R34 | 8+ | Marshals Refuge → Moonglade | 20.040 FAILED / 19.800 FAILED | 18.576 FAILED / 21.823 FAILED |
| R35 | cross-continent | Auberdine → Menethil | 0.042 / 0.017 | 0.112 / 0.020 |
| R36 | cross-continent | Menethil → Auberdine | 0.050 / 0.021 | 0.131 / 0.021 |
| R37 | cross-continent | Astranaar → Goldshire | 1.164 / 0.033 | 2.036 / 0.037 |
| R38 | cross-continent | Goldshire → Astranaar | 1.687 / 0.067 | 5.272 / 0.067 |
| R39 | cross-continent | Ratchet → Booty Bay | 0.079 / 0.019 | 0.119 / 0.019 |
| R40 | cross-continent | Orgrimmar → Brill | 0.051 / 0.017 | 0.086 / 0.018 |
| R41 | cross-continent | Ashenvale east → Menethil | 7.978 / 0.043 | 20.656 FAILED / 20.713 FAILED |

## Supplementary controlled tests

| Batch | ID | Route | Roads | Flights | Dry-first | Walking only | Cold/warm | Host s | 60fps model s | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| dry-first | R04 | Goldshire → Darkshire | firm | False | True | False | cold | 23.433 | 75.354 | ok |
| dry-first | R04 | Goldshire → Darkshire | firm | False | True | False | warm | 15.218 | 48.425 | ok |
| dry-first | R23 | Goldshire → Kharanos | firm | False | True | False | cold | 0.194 | 0.751 | ok |
| dry-first | R23 | Goldshire → Kharanos | firm | False | True | False | warm | 0.021 | 0.053 | ok |
| dry-first | R35 | Auberdine → Menethil | firm | False | True | False | cold | 24.644 | 72.076 | ok |
| dry-first | R35 | Auberdine → Menethil | firm | False | True | False | warm | 24.293 | 69.161 | ok |
| recorded-flights | R05 | Darkshire → Kharanos | off | True | False | False | cold | 0.048 | 0.201 | ok |
| recorded-flights | R05 | Darkshire → Kharanos | off | True | False | False | warm | 0.021 | 0.069 | ok |
| recorded-flights | R05 | Darkshire → Kharanos | firm | True | False | False | cold | 0.085 | 0.334 | ok |
| recorded-flights | R05 | Darkshire → Kharanos | firm | True | False | False | warm | 0.020 | 0.069 | ok |
| recorded-flights | R08 | Booty Bay → Darkshire | off | True | False | False | cold | 3.397 | 10.659 | ok |
| recorded-flights | R08 | Booty Bay → Darkshire | off | True | False | False | warm | 0.091 | 0.218 | ok |
| recorded-flights | R08 | Booty Bay → Darkshire | firm | True | False | False | cold | 19.933 | 62.557 | ok |
| recorded-flights | R08 | Booty Bay → Darkshire | firm | True | False | False | warm | 0.103 | 0.301 | ok |
| recorded-flights | R09 | Ashenvale east → Auberdine | off | True | False | False | cold | 0.658 | 2.302 | ok |
| recorded-flights | R09 | Ashenvale east → Auberdine | off | True | False | False | warm | 0.024 | 0.084 | ok |
| recorded-flights | R09 | Ashenvale east → Auberdine | firm | True | False | False | cold | 1.579 | 5.119 | ok |
| recorded-flights | R09 | Ashenvale east → Auberdine | firm | True | False | False | warm | 0.029 | 0.087 | ok |
| recorded-flights | R24 | Darkshire → Menethil | off | True | False | False | cold | 0.032 | 0.104 | ok |
| recorded-flights | R24 | Darkshire → Menethil | off | True | False | False | warm | 0.027 | 0.101 | ok |
| recorded-flights | R24 | Darkshire → Menethil | firm | True | False | False | cold | 0.039 | 0.136 | ok |
| recorded-flights | R24 | Darkshire → Menethil | firm | True | False | False | warm | 0.020 | 0.068 | ok |
| recorded-flights | R37 | Astranaar → Goldshire | off | True | False | False | cold | 0.182 | 0.669 | ok |
| recorded-flights | R37 | Astranaar → Goldshire | off | True | False | False | warm | 0.021 | 0.086 | ok |
| recorded-flights | R37 | Astranaar → Goldshire | firm | True | False | False | cold | 0.224 | 0.784 | ok |
| recorded-flights | R37 | Astranaar → Goldshire | firm | True | False | False | warm | 0.023 | 0.086 | ok |
| recorded-flights | R41 | Ashenvale east → Menethil | off | True | False | False | cold | 0.652 | 2.334 | ok |
| recorded-flights | R41 | Ashenvale east → Menethil | off | True | False | False | warm | 0.024 | 0.085 | ok |
| recorded-flights | R41 | Ashenvale east → Menethil | firm | True | False | False | cold | 1.604 | 5.218 | ok |
| recorded-flights | R41 | Ashenvale east → Menethil | firm | True | False | False | warm | 0.032 | 0.118 | ok |
| road-strength | R02 | Astranaar → Ashenvale east | normal | False | False | False | cold | 1.452 | 4.637 | ok |
| road-strength | R02 | Astranaar → Ashenvale east | normal | False | False | False | warm | 0.009 | 0.009 | ok |
| road-strength | R02 | Astranaar → Ashenvale east | strong | False | False | False | cold | 1.386 | 4.366 | ok |
| road-strength | R02 | Astranaar → Ashenvale east | strong | False | False | False | warm | 0.009 | 0.009 | ok |
| road-strength | R05 | Darkshire → Kharanos | normal | False | False | False | cold | 4.868 | 16.758 | ok |
| road-strength | R05 | Darkshire → Kharanos | normal | False | False | False | warm | 0.051 | 0.217 | ok |
| road-strength | R05 | Darkshire → Kharanos | strong | False | False | False | cold | 3.758 | 15.030 | ok |
| road-strength | R05 | Darkshire → Kharanos | strong | False | False | False | warm | 0.054 | 0.217 | ok |
| road-strength | R09 | Ashenvale east → Auberdine | normal | False | False | False | cold | 21.607 | 65.746 | failed |
| road-strength | R09 | Ashenvale east → Auberdine | normal | False | False | False | warm | 19.898 | 62.443 | failed |
| road-strength | R09 | Ashenvale east → Auberdine | strong | False | False | False | cold | 18.579 | 62.712 | ok |
| road-strength | R09 | Ashenvale east → Auberdine | strong | False | False | False | warm | 4.379 | 14.658 | ok |
| road-strength | R10 | Astranaar → Azshara bank | normal | False | False | False | cold | 4.926 | 15.543 | ok |
| road-strength | R10 | Astranaar → Azshara bank | normal | False | False | False | warm | 2.786 | 8.375 | ok |
| road-strength | R10 | Astranaar → Azshara bank | strong | False | False | False | cold | 4.260 | 13.743 | ok |
| road-strength | R10 | Astranaar → Azshara bank | strong | False | False | False | warm | 2.510 | 8.069 | ok |
| trace-firm | R09 | Ashenvale east → Auberdine | firm | False | False | False | cold | 20.766 | 63.939 | failed |
| trace-firm | R09 | Ashenvale east → Auberdine | firm | False | False | False | warm | 20.286 | 63.175 | failed |
| trace-firm | R10 | Astranaar → Azshara bank | firm | False | False | False | cold | 4.867 | 15.274 | ok |
| trace-firm | R10 | Astranaar → Azshara bank | firm | False | False | False | warm | 2.606 | 8.239 | ok |
| user-route-flights | R42 | Ratchet → Shimmering Flats | off | True | False | False | cold | 21.350 | 62.389 | ok |
| user-route-flights | R42 | Ratchet → Shimmering Flats | off | True | False | False | warm | 17.203 | 50.305 | ok |
| user-route-flights | R42 | Ratchet → Shimmering Flats | firm | True | False | False | cold | 28.480 | 76.799 | failed |
| user-route-flights | R42 | Ratchet → Shimmering Flats | firm | True | False | False | warm | 23.400 | 68.074 | failed |
| user-route-light-moderate | R42 | Ratchet → Shimmering Flats | light | False | False | False | cold | 27.041 | 74.823 | failed |
| user-route-light-moderate | R42 | Ratchet → Shimmering Flats | light | False | False | False | warm | 26.143 | 70.432 | ok |
| user-route-light-moderate | R42 | Ratchet → Shimmering Flats | moderate | False | False | False | cold | 25.400 | 71.630 | failed |
| user-route-light-moderate | R42 | Ratchet → Shimmering Flats | moderate | False | False | False | warm | 23.195 | 66.490 | ok |
| user-route | R42 | Ratchet → Shimmering Flats | off | False | False | False | cold | 18.886 | 56.936 | ok |
| user-route | R42 | Ratchet → Shimmering Flats | off | False | False | False | warm | 14.765 | 44.741 | ok |
| user-route | R42 | Ratchet → Shimmering Flats | normal | False | False | False | cold | 23.836 | 68.745 | failed |
| user-route | R42 | Ratchet → Shimmering Flats | normal | False | False | False | warm | 25.987 | 71.252 | failed |
| user-route | R42 | Ratchet → Shimmering Flats | firm | False | False | False | cold | 25.739 | 71.951 | failed |
| user-route | R42 | Ratchet → Shimmering Flats | firm | False | False | False | warm | 22.102 | 65.881 | failed |
| user-route | R42 | Ratchet → Shimmering Flats | strong | False | False | False | cold | 20.879 | 66.107 | failed |
| user-route | R42 | Ratchet → Shimmering Flats | strong | False | False | False | warm | 23.462 | 68.264 | failed |
| walking-controls | R01 | Goldshire → Eastvale | off | False | False | True | cold | 0.013 | 0.036 | ok |
| walking-controls | R01 | Goldshire → Eastvale | off | False | False | True | warm | 0.006 | 0.018 | ok |
| walking-controls | R01 | Goldshire → Eastvale | firm | False | False | True | cold | 0.240 | 0.787 | ok |
| walking-controls | R01 | Goldshire → Eastvale | firm | False | False | True | warm | 0.006 | 0.006 | ok |
| walking-controls | R04 | Goldshire → Darkshire | off | False | False | True | cold | 0.283 | 0.917 | ok |
| walking-controls | R04 | Goldshire → Darkshire | off | False | False | True | warm | 0.017 | 0.052 | ok |
| walking-controls | R04 | Goldshire → Darkshire | firm | False | False | True | cold | 0.620 | 2.135 | ok |
| walking-controls | R04 | Goldshire → Darkshire | firm | False | False | True | warm | 0.021 | 0.052 | ok |
| walking-controls | R11 | Brill → Tarren Mill | off | False | False | True | cold | 0.286 | 0.935 | ok |
| walking-controls | R11 | Brill → Tarren Mill | off | False | False | True | warm | 0.019 | 0.054 | ok |
| walking-controls | R11 | Brill → Tarren Mill | firm | False | False | True | cold | 0.740 | 2.451 | ok |
| walking-controls | R11 | Brill → Tarren Mill | firm | False | False | True | warm | 0.024 | 0.067 | ok |
| walking-controls | R15 | Lakeshire → Thelsamar | off | False | False | True | cold | 0.359 | 1.517 | ok |
| walking-controls | R15 | Lakeshire → Thelsamar | off | False | False | True | warm | 0.024 | 0.069 | ok |
| walking-controls | R15 | Lakeshire → Thelsamar | firm | False | False | True | cold | 0.712 | 2.650 | ok |
| walking-controls | R15 | Lakeshire → Thelsamar | firm | False | False | True | warm | 0.024 | 0.070 | ok |
| walking-controls | R19 | Chillwind → Menethil | off | False | False | True | cold | 0.751 | 2.718 | ok |
| walking-controls | R19 | Chillwind → Menethil | off | False | False | True | warm | 0.033 | 0.088 | ok |
| walking-controls | R19 | Chillwind → Menethil | firm | False | False | True | cold | 3.878 | 13.445 | ok |
| walking-controls | R19 | Chillwind → Menethil | firm | False | False | True | warm | 0.034 | 0.088 | ok |
| walking-controls | R23 | Goldshire → Kharanos | off | False | False | True | cold | 2.661 | 9.067 | ok |
| walking-controls | R23 | Goldshire → Kharanos | off | False | False | True | warm | 0.041 | 0.135 | ok |
| walking-controls | R23 | Goldshire → Kharanos | firm | False | False | True | cold | 4.473 | 15.951 | ok |
| walking-controls | R23 | Goldshire → Kharanos | firm | False | False | True | warm | 0.081 | 0.203 | ok |
| walking-controls | R27 | Eastvale → Refuge Pointe | off | False | False | True | cold | 11.744 | 38.713 | failed |
| walking-controls | R27 | Eastvale → Refuge Pointe | off | False | False | True | warm | 0.139 | 0.470 | failed |
| walking-controls | R27 | Eastvale → Refuge Pointe | firm | False | False | True | cold | 18.357 | 63.763 | failed |
| walking-controls | R27 | Eastvale → Refuge Pointe | firm | False | False | True | warm | 0.168 | 0.487 | failed |
| walking-controls | R33 | Azshara bank → Cenarion Hold | off | False | False | True | cold | 18.590 | 57.110 | failed |
| walking-controls | R33 | Azshara bank → Cenarion Hold | off | False | False | True | warm | 15.757 | 48.698 | ok |
| walking-controls | R33 | Azshara bank → Cenarion Hold | firm | False | False | True | cold | 21.630 | 66.778 | failed |
| walking-controls | R33 | Azshara bank → Cenarion Hold | firm | False | False | True | warm | 20.087 | 61.914 | ok |

## Cross-continent itineraries

| ID | Roads | Status | Host cold s | Zones actually walked | Vehicles selected |
| --- | --- | --- | ---: | --- | --- |
| R35 | off | ok | 0.042 | Darkshore → Wetlands | boat: Auberdine to Menethil Harbor |
| R35 | firm | ok | 0.112 | Darkshore → Wetlands | boat: Auberdine to Menethil Harbor |
| R36 | off | ok | 0.050 | Wetlands → Darkshore | boat: Menethil Harbor to Auberdine (stay aboard at Southshore) |
| R36 | firm | ok | 0.131 | Wetlands → Darkshore | boat: Menethil Harbor to Auberdine (stay aboard at Southshore) |
| R37 | off | ok | 1.164 | Ashenvale → Darkshore → Stormwind City → Elwynn Forest | boat: Auberdine to Stormwind |
| R37 | firm | ok | 2.036 | Ashenvale → Darkshore → Stormwind City → Elwynn Forest | boat: Auberdine to Stormwind |
| R38 | off | ok | 1.687 | Elwynn Forest → Stormwind City → 1455 → Stormwind City → Darkshore → Ashenvale | tram: Deeprun Tram; tram: Deeprun Tram; boat: Stormwind to Auberdine |
| R38 | firm | ok | 5.272 | Elwynn Forest → Stormwind City → 1455 → Stormwind City → Darkshore → Ashenvale | tram: Deeprun Tram; tram: Deeprun Tram; boat: Stormwind to Auberdine |
| R39 | off | ok | 0.079 | The Barrens → Stranglethorn Vale | boat: Ratchet to Booty Bay |
| R39 | firm | ok | 0.119 | The Barrens → Stranglethorn Vale | boat: Ratchet to Booty Bay |
| R40 | off | ok | 0.051 | Orgrimmar → Durotar → Tirisfal Glades | zeppelin: Orgrimmar to Undercity |
| R40 | firm | ok | 0.086 | Orgrimmar → Durotar → Tirisfal Glades | zeppelin: Orgrimmar to Undercity |
| R41 | off | ok | 7.978 | Ashenvale → Darkshore → Wetlands | boat: Auberdine to Menethil Harbor |
| R41 | firm | failed | 20.656 | — | — |

## Itinerary anomalies requiring review

These plans completed and passed their applicable terrain checks, but have a questionable travel sequence. This is separate from a generation failure and does not establish global travel-time optimality.

| ID | Route | Roads | Observed sequence |
| --- | --- | --- | --- |
| R24 | Darkshire → Menethil | off | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |
| R24 | Darkshire → Menethil | firm | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |
| R27 | Eastvale → Refuge Pointe | off | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |
| R27 | Eastvale → Refuge Pointe | firm | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |
| R38 | Goldshire → Astranaar | off | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |
| R38 | Goldshire → Astranaar | firm | Stormwind → Ironforge → Stormwind by tram, then onward. Investigate whether a direct city/harbour approach should avoid this return trip. |

## Primary failures by route

A budget failure is not proof that no physical route exists. It means this attempt did not find a complete usable itinerary within the planner’s work allowance.

| ID | Route | Failing cold road modes | Cold host s | Immediate retry |
| --- | --- | --- | --- | --- |
| R08 | Booty Bay → Darkshire | off, firm | 19.7062, 21.8915 | off: failed 18.9651s; firm: failed 21.0603s |
| R09 | Ashenvale east → Auberdine | firm | 17.2659 | firm: failed 21.4702s |
| R13 | Bloodhoof → Camp Mojache | firm | 19.5067 | firm: failed 19.4992s |
| R25 | Camp Mojache → Orgrimmar | off, firm | 25.2993, 24.2279 | off: ok 16.7292s; firm: failed 23.6685s |
| R26 | Everlook → Feathermoon | firm | 20.0622 | firm: ok 19.036s |
| R29 | Cenarion Hold → Sun Rock | firm | 19.265 | firm: failed 21.2415s |
| R33 | Azshara bank → Cenarion Hold | off, firm | 18.4037, 22.1415 | off: failed 17.5023s; firm: failed 18.7572s |
| R34 | Marshals Refuge → Moonglade | off, firm | 20.0399, 18.5759 | off: failed 19.8s; firm: failed 21.8231s |
| R41 | Ashenvale east → Menethil | firm | 20.6557 | firm: failed 20.713s |

## Failure inventory

| Batch | ID | Roads | Cold/warm | Host s | Paths | Cells | Result |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| primary | R08 | off | cold | 19.706 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R08 | off | warm | 18.965 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R08 | firm | cold | 21.892 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R08 | firm | warm | 21.060 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R09 | firm | cold | 17.266 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R09 | firm | warm | 21.470 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R13 | firm | cold | 19.507 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R13 | firm | warm | 19.499 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R25 | off | cold | 25.299 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R25 | firm | cold | 24.228 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R25 | firm | warm | 23.669 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R26 | firm | cold | 20.062 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R29 | firm | cold | 19.265 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R29 | firm | warm | 21.241 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R33 | off | cold | 18.404 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R33 | off | warm | 17.502 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R33 | firm | cold | 22.142 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R33 | firm | warm | 18.757 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R34 | off | cold | 20.040 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R34 | off | warm | 19.800 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R34 | firm | cold | 18.576 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R34 | firm | warm | 21.823 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R41 | firm | cold | 20.656 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| primary | R41 | firm | warm | 20.713 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| road-strength | R09 | normal | cold | 21.607 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| road-strength | R09 | normal | warm | 19.898 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| trace-firm | R09 | firm | cold | 20.766 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| trace-firm | R09 | firm | warm | 20.286 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route-flights | R42 | firm | cold | 28.480 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route-flights | R42 | firm | warm | 23.400 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route-light-moderate | R42 | light | cold | 27.041 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route-light-moderate | R42 | moderate | cold | 25.400 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | normal | cold | 23.836 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | normal | warm | 25.987 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | firm | cold | 25.739 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | firm | warm | 22.102 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | strong | cold | 20.879 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| user-route | R42 | strong | warm | 23.462 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R27 | off | cold | 11.744 | 128 | 1346560 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R27 | off | warm | 0.139 | 128 | 0 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R27 | firm | cold | 18.357 | 128 | 1986048 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R27 | firm | warm | 0.168 | 128 | 0 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R33 | off | cold | 18.590 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |
| walking-controls | R33 | firm | cold | 21.630 | 128 | 1999872 | failed: Some walking connections exceeded the search budget. Try an intermediate waypoint. |

## Slowest cold computations

| Batch | ID | Roads | Host s | 60fps model s | Paths | Cells | Max step ms | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| user-route-flights | R42 | firm | 28.480 | 76.799 | 128 | 1999872 | 102.6 | failed |
| user-route-light-moderate | R42 | light | 27.041 | 74.823 | 128 | 1999872 | 111.5 | failed |
| user-route | R42 | firm | 25.739 | 71.951 | 128 | 1999872 | 97.4 | failed |
| user-route-light-moderate | R42 | moderate | 25.400 | 71.630 | 128 | 1999872 | 90.5 | failed |
| primary | R25 | off | 25.299 | 67.187 | 128 | 1999872 | 283.4 | failed |
| dry-first | R35 | firm | 24.644 | 72.076 | 108 | 2007552 | 72.0 | ok |
| primary | R25 | firm | 24.228 | 71.894 | 128 | 1999872 | 77.2 | failed |
| user-route | R42 | normal | 23.836 | 68.745 | 128 | 1999872 | 78.5 | failed |
| dry-first | R04 | firm | 23.433 | 75.354 | 146 | 2166528 | 63.5 | ok |
| primary | R33 | firm | 22.142 | 67.130 | 128 | 1999872 | 66.5 | failed |
| primary | R08 | firm | 21.892 | 68.988 | 128 | 1999872 | 46.6 | failed |
| walking-controls | R33 | firm | 21.630 | 66.778 | 128 | 1999872 | 68.3 | failed |
| road-strength | R09 | normal | 21.607 | 65.746 | 128 | 1999872 | 91.3 | failed |
| user-route-flights | R42 | off | 21.350 | 62.389 | 23 | 1978624 | 89.4 | ok |
| user-route | R42 | strong | 20.879 | 66.107 | 128 | 1999872 | 68.2 | failed |

## Exact test anchors

| Place | Map | X | Y | Adjustment yd |
| --- | --- | ---: | ---: | ---: |
| Goldshire | Elwynn Forest (1429) | 42.3000 | 66.6000 | 0.00 |
| Eastvale | Elwynn Forest (1429) | 83.7000 | 69.4000 | 0.00 |
| Sentinel Hill | Westfall (1436) | 56.0000 | 47.0000 | 0.00 |
| Darkshire | Duskwood (1431) | 77.0000 | 44.0000 | 0.00 |
| Lakeshire | Redridge Mountains (1433) | 26.7241 | 44.3966 | 5.15 |
| Stormwind | Stormwind City (1453) | 62.4000 | 72.0000 | 0.00 |
| Kharanos | Dun Morogh (1426) | 46.0000 | 51.0000 | 0.00 |
| Thelsamar | Loch Modan (1432) | 34.9698 | 48.0769 | 8.57 |
| Menethil | Wetlands (1437) | 10.5237 | 60.8006 | 3.16 |
| Southshore | Hillsbrad Foothills (1424) | 50.5000 | 58.3000 | 0.00 |
| Refuge Pointe | Arathi Highlands (1417) | 45.9000 | 46.1000 | 0.00 |
| Aerie Peak | The Hinterlands (1425) | 11.7424 | 46.5097 | 12.26 |
| Chillwind | Western Plaguelands (1422) | 43.0000 | 85.0000 | 0.00 |
| Lights Hope | Eastern Plaguelands (1423) | 75.9439 | 54.0639 | 21.91 |
| Booty Bay | Stranglethorn Vale (1434) | 27.2000 | 76.9000 | 0.00 |
| Auberdine | Darkshore (1439) | 36.5000 | 45.6000 | 0.00 |
| Astranaar | Ashenvale (1440) | 34.0000 | 48.0000 | 0.00 |
| Ashenvale east | Ashenvale (1440) | 85.2000 | 44.6000 | 0.00 |
| Azshara bank | Azshara (1447) | 10.5700 | 75.0800 | 0.00 |
| Ratchet | The Barrens (1413) | 62.4000 | 37.8000 | 0.00 |
| Theramore | Dustwallow Marsh (1445) | 67.5000 | 51.2000 | 0.00 |
| Gadgetzan | Tanaris (1446) | 51.8000 | 28.5000 | 0.00 |
| Marshals Refuge | Un'Goro Crater (1449) | 45.0000 | 5.7000 | 0.00 |
| Cenarion Hold | Silithus (1451) | 51.2000 | 38.4000 | 0.00 |
| Emerald Sanctuary | Felwood (1448) | 51.1000 | 82.2000 | 0.00 |
| Everlook | Winterspring (1452) | 61.3000 | 38.8000 | 0.00 |
| Moonglade | Moonglade (1450) | 52.0000 | 59.0000 | 0.00 |
| Feathermoon | Feralas (1444) | 30.0000 | 43.0000 | 0.00 |
| Crossroads | The Barrens (1413) | 51.9000 | 30.3000 | 0.00 |
| Razor Hill | Durotar (1411) | 52.0000 | 43.5000 | 0.00 |
| Orgrimmar | Orgrimmar (1454) | 50.5000 | 65.4000 | 0.00 |
| Bloodhoof | Mulgore (1412) | 47.0000 | 61.0000 | 0.00 |
| Camp Mojache | Feralas (1444) | 75.9000 | 44.7000 | 0.00 |
| Sun Rock | Stonetalon Mountains (1442) | 45.0000 | 59.0000 | 0.00 |
| Shadowprey | Desolace (1443) | 22.8000 | 72.0000 | 0.00 |
| Brill | Tirisfal Glades (1420) | 61.0000 | 52.0000 | 0.00 |
| Sepulcher | Silverpine Forest (1421) | 45.0000 | 43.0000 | 0.00 |
| Tarren Mill | Hillsbrad Foothills (1424) | 62.0000 | 20.0000 | 0.00 |
| Shimmering Flats | Thousand Needles (1441) | 78.0000 | 75.0000 | 0.00 |

## Findings and follow-up priorities

Observed: zone count alone is a poor predictor. Several adjacent-zone plans exhaust their budget, while long journeys with a useful tram, flight or boat can be cheap. A failed budgeted search does not prove that a route is physically impossible.

Observed: successful route sections benefit strongly from session caching, but budget-limited subsearches can repeat on every request. In the traced Astranaar → Azshara Firm repeat, one failed 262,144-cell search dominates while successful sections cost almost nothing. The adjacent Ashenvale → Darkshore trace invokes 128 local searches across 18 map IDs before failing; attempted maps are not necessarily part of a final journey.

For the reported Ratchet → Shimmering Flats route, the repeat with roads off uses the Great Lift but still performs 6 budget-limited subsearches (1572864 cells). The expensive alternatives are in Dustwallow Marsh, although the returned walking legs use the Barrens and Thousand Needles. This directly reproduces the reported delay with swimming permitted.

Observed: known flight offers can avoid expensive walking sections, but the flight fixture is not a substitute for good walking performance. Dry-first swimming preference can also spend a full unsuccessful pass before retrying with swimming allowed; those results are kept outside the baseline.

Suggested implementation priorities, not changes made during this survey:

1. Reuse budget-limited failure results only under the same source signatures, endpoints, road/liquid policy and an equal or smaller search allowance. Do not cache a budget failure as permanent unreachability.
2. Bound or defer expensive alternative walking sections when a complete usable itinerary already exists. In particular, avoid repeatedly spending the full local allowance on low-value Dustwallow alternatives to the Great Lift.
3. Connect arbitrary first/last-mile locations to the prepared road/crossing network, rather than depending only on exact endpoint matches for prepared path reuse. Preserve terrain and native-floor validation.
4. Re-test these exact failure cases before increasing work budgets. A larger ceiling alone risks making failed requests take even longer. Review the tram-return itinerary separately from latency.


Reproduce: `python tools/benchmark_route_matrix.py --prepare`, then `--run`. Use `--cases R01,R05 --profiles off,firm --label example` for a subset; add `--walking`, `--flights` or `--avoid` for the labelled controls. Run this report with `python tools/report_route_matrix.py`. Raw JSONL and flattened CSV retain actual chosen zones, vehicles, source hashes, cache hits, search cells and precise coordinates.
