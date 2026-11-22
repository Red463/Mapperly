# Terrain routing provenance

Owned Gatherly terrain data and pathfinding, reused independently under Tom's MIT license. Generated from the read-only Forever 1.60.1 build 70959 snapshot by Gatherly/tools/build_terrain.py and tools/terrain. Original Gatherly source SHA256: `164266b0795a41fcbc77ffb223e5ff868bef905e0a8f156837a28bc46df58c3f`.

The packed dataset covers 55 local maps (43 complete indexed terrain, 12 partial); overview records reject routing. Cells are approximately 4.17 yards. Slopes at or above 50 degrees and terrain holes are restricted. Swimming is permitted in this binary mask. Unknown cells remain blocked.

This is a terrain heuristic, not collision/navmesh extraction. Fences, trees, buildings, caves, bridges, lifts and overlapping floors are not represented reliably. 'Complete' means indexed terrain coverage, not verified physical traversability. Client build changes require regeneration.

Generator and rules: ../Gatherly/tools/build_terrain.py, ../Gatherly/tools/terrain/rules.py in the shared workspace; public project https://github.com/Red463/Gatherly. Full method: Gatherly/docs/terrain-routing.md. No runtime Gatherly dependency.

Bundled data uses LF line endings; SHA256: `b52c3275f761a1f0c38f25f06ec2372a9a4c432a690ecaea9fca873f748a5acb`. Terrain rows and metadata are unchanged.
