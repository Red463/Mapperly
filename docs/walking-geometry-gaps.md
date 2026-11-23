# Walking geometry investigation and resolutions

## Current result: preview.11

All five previously listed entrance/branch gaps now have bundled, sampled native-floor proofs: the three Timbermaw branches, Ironforge main entrance and Undercity static sewer. Forward/reverse following and complete Bloodvenom Post/Astranaar-to-Everlook journeys pass automated tests. Terrain permissions are unchanged.

The Timbermaw graph omitted short native stair risers that face downward or occur outside `steps_*` groups. Including only bounded, collidable native risers connects the branches; the actual maximum rise is approximately 0.312012 yard. The Winterspring dry landing differs from its floor by 0.305200 yard, narrowly outside the initial 0.30-yard contact threshold. Every emitted sample has supporting native geometry; no empty-space bridge was inserted. Native service anchors establish that the existing entrance components connect the playable zones even though they are not the largest white regions in their map rectangles.

Ironforge's exact-overlap floor graph connects facade, entrance and halls. Its anchor is a proven interior floor beneath overhead terrain. Undercity's outer static sewer connects through adjoining FFR groups to a genuine outdoor terrain intersection; the dry route avoids the native liquid pool. Neither entrance proof certifies all indoor city walls or vertical layers, and Undercity elevators remain transport work.

Current proof inputs are `tools/data/native-curved-corridors-70959.json`; city entrance and Timbermaw service-anchor evidence is under `../output/walking-city-audit`. See [coverage](walking-coverage.md) and [structure sources](../Data/Structures-SOURCES.md). Live-client acceptance remains pending. The Hyjal candidate below is still rejected because it has no outdoor Hyjal exit.

## Historical preview.10 findings, superseded where noted above

No new corridors from this investigation are ready for integration. The authoritative machine-readable result is timbermaw-hyjal-final-audit.json. It contains unique candidate corridor IDs per WMO placement/branch pair, dry landing witnesses and bounds, search outcomes, and the remaining gap inventory.

Timbermaw root111596 / UID372018: all35WMOgroups and17nonzero embedded M2models are available. Native exterior triangle edges/interiors were sampled on a barycentric lattice with maximum spacing0.25yd. Actual dry/nohole contacts with absolute floor/terrain difference at most0.30yd exist on21Felwood faces,19Moonglade faces and13Winterspring faces. Each accepted contact-to-face-center segment has native floor support and was checked for ceiling clearance.

These improved landings still do not produce a continuous verified corridor. Exact native edges/projected triangle-overlap portals were tested with the original slope floor, bounded native step-riser triangles, and a diagnostic retaining EVERY upward triangle in all named steps groups. Even a geometry-only union ignoring headroom has no shared connected component between any branch pair. Its16635faces form196components: Felwood contacts reach a6003-face component, Moonglade contacts reach a6886-face component, and the valid Winterspring contacts remain in separate small exterior components. This is an extraction/path-proof limitation; it does not establish that in-game travel is impossible.

Embedded M2collision was extracted with native MODD quaternion/scale/translation. Five model types contribute24colliding placements: furniture/tents/totems/bones/a wooden door. None has a collision AABB overlapping steps_A01, so an omitted embedded stair/platform does not explain that branch. No unsupported free-space bridge has been invented.

Sources: timbermaw-dense-landing-paths-111596.json, timbermaw-bounded-riser-paths-111596.json, timbermaw-all-stair-diagnostic-111596.json, timbermaw-geometry-only-connectivity.json, timbermaw-m2-placement-proof.json. Source scripts sit alongside these artifacts.

Hyjal cave root7960309 / UID70062766 is not a demonstrated walking exit. It genuinely has a native ground contact in Winterspring Area2252, The Ruins of Kel'Theril, with floor/terrain difference0.006545yd. Its floor underneath native Hyjal Area616 is far below the outdoor terrain: the closest checked vertex/centroid is196.25yd below terrain; the closest checked dry witness is305.15yd below. Dense native floor sampling found no Hyjal dry landing within0.30yd. Bounding overlap with Hyjal ADTs therefore supplies no through-exit proof. The other Timbermaw-derived roots in the Hyjal inventory are located inside Hyjal or Darkwhisper, and have not been established as cross-zone walking exits.

Sources: hyjal-boundary-assets.json, hyjal-cave-ground-contact-probe.json, hyjal-cave-ground-paths-7960309.json.

Remaining known walking proofs are Timbermaw's three branch pairs, the Dun Morogh-to-Ironforge ground threshold, and the Tirisfal-to-Undercity static sewer path. City assets are available, but no whole interior routing readiness is claimed. Felwood/Winterspring-to-Hyjal are unproven adjacencies rather than established missing walking exits. Cliff, ocean and transport adjacencies must not be converted into invented walking links.

Earlier successful gate, Talondeep and exact Blackrock proofs remain valid and separate. No runtime/data files or snapshot files were modified.
