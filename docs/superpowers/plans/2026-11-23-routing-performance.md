# Routing performance

Reproduced the screenshot's Ashenvale route (72.9,68.3 to 28.6813,20.3167) with all native data. Firm performs approximately 344,064 cell expansions over three local path calls, including redundant neighboring-zone exploration after already finding the 4,326-yard valid route. CPU baseline approximately 3.35 seconds / 709 four-millisecond work slices on this host. Strong and ordinary routing exhibit similar redundant transport exploration.

Implement an optimistic transport-only lower-bound graph using straight-line permitted-continent distances and eligible scheduled flight/vehicle costs. If no transport combination can improve the existing route, retain the local route without opening the full walking network. Treat absent/invalid data conservatively. Preserve multi-leg transports, all terrain rules and existing road strengths; no approximate heuristic inflation.

Memoize road costs per search cell, and evaluate the current cell once per expansion. Keep memory bounded by existing expansion limits. Measure reported route and existing benchmarks, add correctness/performance regressions, refresh native lift proof bindings if Terrain.lua changes, review and package preview.33 after full regressions. No GitHub publication requested.

## Verified outcome

Firm keeps exactly the same 4,326.3938899295-yard route. Search cells fall from 344,064 to 185,600 and road lookups from 2,723,848 to 188,275. Representative host CPU falls from 3.35 to 1.61 seconds. An 80-case randomized relaxed-graph oracle agrees with the pruning helper. Existing short ferry, flights, native cross-zone, harbour and lift regressions pass. Replayed native lift audit yields identical 1,312/911-cell masks and refreshed hash binding. Independent review found no substantive defects. All 66 suites pass. Preview.33 ZIP CRC and all TOC source entries verified.

Prevention: retain the full-data screenshot regression and characterize performance at each preference strength, including transport availability, rather than testing the local terrain search alone.
