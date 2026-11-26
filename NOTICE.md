# Third-party content

Mapperly's original code is MIT licensed; see `LICENSE`.

The generated service dataset `Data/Services.lua` contains data derived from the TrinityCore Forever database snapshot. That component is provided under GPL version 2 with attribution to TrinityCore contributors. Its license is bundled in `Libs/Forever-Services-COPYING.txt`; provenance and original source locations are in `Data/Services-SOURCES.md`. The generator and its faction-classification input are included in the release ZIP for reproducibility.

`Data/ServiceDirectory.lua` contains vendor and trainer locations from the same snapshot under the same GPL version 2 license. `Data/ServiceDirectory-SOURCES.md` documents the selection rules and the bundled generator.

`Data/VendorGoods.lua` includes merchant stock relationships from the same GPL version 2 Forever snapshot and item metadata from the WoW Forever client. Item icons are references to client-owned artwork. See `Data/VendorGoods-SOURCES.md` for inputs and reproduction.

`Data/QuestLocations.lua` also derives from the pinned TrinityCore Forever database snapshot and is provided under GPL version 2 with the same bundled license. Source selection, omissions, hashes and reproduction instructions are in `Data/QuestLocations-SOURCES.md`; its generator is included in release ZIPs. Native quest log data is read from the game and is not imported from Questie or another addon.

`Data/QuestCatalog.lua` extends that GPL version 2 dataset with English quest titles, snapshot requirements and exact starter positions. Its pinned world/hotfix source hashes, server field semantics and reproduction instructions are in `Data/QuestCatalog-SOURCES.md`; the builder and its helper scripts are included.

Other bundled map metadata and libraries retain the licenses identified in `Data/SOURCES.md` and `Libs`.

`Media/GuideArrow.tga` reuses the user-owned Gatherly arrow artwork from this workspace (Copyright 2026 Tom, MIT). It is bundled locally; Mapperly does not load or control Gatherly navigation.

`Data/Trams.lua` includes fixed service/portal facts derived from the same pinned TrinityCore Forever database snapshot, with native animation and WMO floor witnesses. The database-derived component is provided under GPL version 2 with the bundled Forever services license. See `Data/Trams-SOURCES.md`; generator and compact source proofs are included. No implementation or transport dataset was imported from Shortest Path Forever.
