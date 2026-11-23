# Preview.33 routing performance

The reported Ashenvale example was reproduced using player coordinates approximately 72.9, 68.3 and destination 28.6813, 20.3167. Source coordinates were inferred from the screenshot. The resulting Firm route is 4,326.39 yards long.

| Firm benchmark | Before | After |
|---|---:|---:|
| Search cells reported | 344,064 | 185,600 |
| Road-cost lookups | 2,723,848 | 188,275 |
| Deterministic work slices, no wall clock | 208 | 112 |
| Approximate host CPU time | 3.35 s | 1.61 s |
| Final walking distance | 4,326.39 yd | 4,326.39 yd |

These are local Lua 5.1 benchmark measurements, not promised in-game timings. The planner still spreads work over frames to keep the game responsive. Ordinary routing and other test routes also benefit, with varying gains. Long or constrained routes still require more work than nearby open-ground destinations.

The main waste was exploring potential transport alternatives through a neighboring zone after finding a usable local route. A relaxed graph now estimates the best possible cost of eligible transport combinations using straight-line walking distances. It can admit a route that later fails, but cannot reject a genuinely faster transport combination under those costs. Unknown inputs conservatively keep the full search. Multiple transports, cross-continent legs and character-specific flight eligibility remain supported.

Road factors are memoized during each grid search instead of repeatedly decoding the same cells for every neighbor. Search costs and heuristic remain unchanged; stronger road preference is not weakened, and terrain and private dock access remain enforced.

To test, repeat the screenshot route at Firm and Strong, then compare road preference off. Also try a flight or boat journey that saves time; the planner must still select it.


# Preview.39: precomputed connections and session reuse

The offline builder attempts fixed travel-point pairs using the unchanged original Terrain.Path algorithm, with the runtime maximum of 262,144 expansions per attempt. It ships only successful geometry, source-bound to resolved terrain, ground corrections and effective road rows. It never adds a walking crossing or unlocks a vehicle. The manifest records 887 selected anchor pairs, 3,367 successful mode-specific paths and 1,730 omitted attempts across six effective road modes. Forty-eight zones have at least one prepared connection. Bounded live fallback remains necessary.

| Native Firm case | Preview.38 cells | Preview.39 cold cells | Immediate repeat cells | Cold work reduction |
|---|---:|---:|---:|---:|
| Ashenvale 85.2,44.6 to Mikhail approach, recorded Astranaar flight plus boat | 252,928 | 165,376 | 0 | 34.6% |
| Duskwood 77,44 to Dun Morogh 46,51 | 1,053,952 | 578,304 | 0 | 45.1% |

Deterministic cooperative slices were 165 -> 126 -> 3 and 965 -> 555 -> 12 respectively. Slice counts use the synthetic host clock, not promised in-game frames. Recorded host elapsed examples were about 2.18 -> 1.48 -> 0.02 seconds and 9.42 -> 4.99 -> 0.06 seconds; these vary with CPU contention and are not live-client timing guarantees. Terrain-work reduction is the reproducible performance assertion.

Mikhail retains exactly the same walking distance and both vehicle legs. Duskwood's prepared reverse section changes a grid tie choice by about 4.9 yards (9,581.67 -> 9,576.78, approximately 0.05%); all sections remain terrain-validated under the same road factor. The old terrain cache already reuses reversed sections; no road penalty or collision permission is weakened.

The generated Lua file is approximately 3.93 MB uncompressed and uses approximately 12.9 MiB of Lua 5.1 heap in a standalone host test. Session cache geometry is separately capped at 512 entries / 16,384 points with 16 source contexts. Cache lifetime is the current session; changing road modes or zones does not by itself clear earlier contexts, but bounded eviction can remove them. New arbitrary approaches still need live searches.

Reproduce with `python tests/path_reuse_journeys.py`; inspect source/geometry proofs with `python tests/walking_path_data.py`. Rebuild using `python tools/build_walking_paths.py --workers 4`. Missing prepared paths are normal fallback cases, not evidence that a destination is unreachable.
