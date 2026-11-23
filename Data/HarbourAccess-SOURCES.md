# Stormwind harbour access

Native Forever build 70959 geometry, pinned in `tools/data/native-harbour-corridors-70959.json`, supplies two private walking corridors: the city-to-harbour descent and the Auberdine boarding pier. `tools/verify_harbour_corridors.py` independently checks the original ADT placements, WMO hashes, MPY2 collision flags and transformed floor triangles. The proofs cover 22 upward collision faces and 1,668 supported samples with no unsupported gap.

`tools/build_harbour_access.py` validates the proofs and existing permitted endpoint regions before compiling `Data/HarbourAccess.lua`. These corridors do not change terrain permissions or turn the water between shore and vessel into walking ground. The separate road supplement makes verified floor geometry a road preference.

The Stormwind boat handoff uses the real pier floor at native north/east/height `-8648.392483, 1332.613545, 5.508331`, 13.289 horizontal yards from vessel node 177218. `tools/build_transports.py` binds the override to the verified pier endpoint and proof hash. On zero-altitude clients, walking clear of the vessel along that corridor can confirm disembarkation; proximity to the vessel alone cannot.

Coverage remains bounded. The ordinary permitted-ground link between the two certified corridors is approximately 911 yards. A visually shorter harbour ramp connection remains unproven and is not promoted to a walking edge. Other ports' road-floor hints do not certify stairs, vessel boarding, or interior access. Live acceptance is still required.
