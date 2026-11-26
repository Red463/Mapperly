# Manual local transport access — build 70959

`LocalTransports.lua` contains two directed Great Lift connections between the Barrens and Thousand Needles. Rebuild with `python tools/build_local_transports.py` from `tools/data/native-local-transports-70959.json`. The generated data pins its source SHA256 independently of scheduled vessel data.

The native WMO root 112647, placement 283429, has `elevator` and `bottom` groups 112648/112649. Placement scale 1024 means scale 1. Native area 485 identifies The Great Lift; the nearby sign 19844 corroborates the southern approach. Pinned records include transformed collidable static floor triangles/file hashes, exact native MCVT dry ground heights, and runtime walking paths from a native road cell/named sign approach. Upper dry handoff height 85.333926 is 5.26 yards from static walkway height 85.639081. Lower handoff height -50.887676 is 12.64 yards from static floor height -44.178241. Both approaches belong to their playable walking components. The upper tower roof near113–115yards is excluded as boarding evidence.

These are **manual access legs**, not collision-certified moving-platform paths. Walk to the ground marker, access the nearby landing, board the lift and leave it yourself. No automatic walking connector between dry ground and platform is claimed. No moving-platform spawn ID, animation ID, route polyline, timetable or exact boarding center is asserted. Animation 11898/11899 remains unjoined candidate evidence and is not used. Both directions use an assumed 120-second total planning allowance, including waiting, riding and manual access. No physical faction restriction is established; the manual link is available to both factions.

Arrival requires the destination ground marker and readable compatible floor height, even if departure was not observed. A readable height away from the source floor within the two-floor span recognises an already-started ride. Near the destination floor, guidance points towards the dry landing marker. Protected heights require explicit **Continue on foot** confirmation at that marker. Loading gaps retain the leg and suppress invented bearings. The lift setting independently excludes these edges from future plans; settings changed during an active transport leg retain the existing deferred-replan behavior.

### Live zero-altitude correction (preview.27)

The Forever 71037 capture returned UnitPosition Z=0 in all 110 samples across approach, waiting, riding and walking away. Zero cannot establish a floor when both native landing heights are far from zero. Lift guidance treats that reading as unavailable, without inferring departure; a genuine sea-level landing remains supported when its expected height is near zero.

`tools/data/native-lift-exits-70959.json` adds checked dry exit disks, with a separate generated source hash. Each disk is at least 8 yards clear of every projected static collision triangle of the Great Lift WMO. Its complete bounding-square grid and corners pass exact native dry/root-slope tests and runtime mask/region checks, and its center connects directly to the existing handoff. Upper and broad lower disks have radius 8 yards; the captured lower walk-off also has a radius 1-yard disk. Radius 2 at that particular point would include a native cell over the slope limit, so it is excluded. The tower/shaft and overlapping upper-floor projections cannot use these exemptions.

An active lift leg may finish on checked destination exit ground without a recorded departure or readable altitude. If height is readable it must match that exit area's native height range. Inside the old landing-marker area, the existing readable-height or explicit-confirmation rule remains; other arbitrary nearby ground cannot finish the leg. Runtime validates disk distance, connected region and the segment to its center. This recognises destination ground, not vehicle membership. Native moving-platform identity and geometry remain unresolved.

### Broad exit coverage (preview.28)

The small circles missed players taking another exit path. `tools/data/native-lift-exit-masks-70959.json` replaces reliance on those circles with bounded four-yard ground cells: 1,312 upper and 911 lower cells within 200 yards of the respective handoff. Each entire cell is at least 8 yards clear of every projected static collision triangle. Its 25 one-yard grid samples (including all corners) pass exact native dryness, slope, hole/liquid and destination-height-band tests, plus current runtime ground/connected-region checks. All 55,575 accepted native samples are retained in the hashed audit proof in `output/lift-audit`.

The generated grid stores maximum north/east origins; rows run south and columns decrease world east. Runtime checks instance, cell membership, current ground/region and any readable height. Readable conflicting coordinates still block arrival. The source pins terrain and region input hashes, and the builder rechecks centers/corners of every accepted cell. These are local arrival permissions only: no base terrain mask changes or arbitrary ground exemptions are introduced. Small disks remain as supplementary checked areas, but normal exit detection no longer depends on crossing them.

The source snapshot is the existing read-only Forever 70959 extraction. Audit scripts/artifacts are retained in `output/lift-audit`; pinned JSON contains the compact proofs needed for rebuild validation. Runtime depends on no other addon or client installation files.

## Tram and other lifts

Deeprun Tram is now bundled separately in Data/Trams.lua. Native SQL identifies the six Subway objects, pairs station portals, and original WMO collision triangles prove both exact city exit floors. See [Trams-SOURCES.md](Trams-SOURCES.md). No player recording is required. The Stormwind portal component36 still lacks a certified walking corridor to the main city component52: bounded native stair candidates failed clearance checks. As requested for rc.5, unavailable indoor walking paths now use explicitly labeled city portal bearings for tram access/egress. This is high-level wayfinding, not a newly certified floor corridor or a change to the terrain masks.

Thunder Bluff and Undercity lifts remain unbundled until their own floor/access audits are complete. Great Lift support is unchanged; automatic Deeprun arrival uses paired-instance transitions rather than inferring floors from map XY alone.

Preview.32 replays the original native exit audit after the road-strength routing change. Both masks remain identical (1,312 upper and 911 lower cells). The pinned runtime Terrain.lua hash is refreshed, with the revalidation proof retained in native-lift-exit-masks-70959.json provenance. No native coverage or terrain permissions changed.

Preview.33 repeats the native exit audit after road-cost memoization. Coverage remains identical; the provenance routingPerformanceRevalidation field records the new proof and runtime hash binding.

The 25 November 2026 route-planning revalidation repeats the original native
exit-mask audit against the updated terrain implementation. All 55,575 accepted
native samples, 591 additional retained disk/anchor samples and six retained
walking paths pass fresh native and runtime checks. Coverage remains exactly
1,312 upper and 911 lower cells. Native identities, coordinates, heights, masks,
links and compiled lift edge fields remain unchanged; generated source hashes
are rebuilt after validation. `routePlanningRevalidation` in the pinned mask
provenance records the frozen runtime hash and the revalidator/proof hashes.
The retained replay is `output/lift-audit/revalidate_route_planner.py`; canonical
proof bytes omit elapsed timings so repeated validation is deterministic.
