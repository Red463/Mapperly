# Recommended zone levels

The heading and native continent-hover label show recommended player questing levels. These are guidance ranges, not entry restrictions or a claim that every quest falls within them.

1. Use the Forever client's `C_Map.GetMapLevels` when it returns a valid positive range for a zone. This is the API used by Blizzard's native area-label provider in the [Forever UI source](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_SharedMapDataProviders/AreaLabelDataProvider.lua).
2. Otherwise use the bundled, cited recommendation table from [OpenMap's Forever Levels.lua](https://github.com/openmap-world/openmap/blob/273f9b672a7bfab568ebf161d07ee2380761c3a3/OpenMap/Data/Forever/Levels.lua), pinned to commit `273f9b672a7bfab568ebf161d07ee2380761c3a3`. This is bundled metadata, not an installed-addon dependency. OpenMap is MIT licensed; see `Libs/OpenMap-Places-LICENSE.txt`.

The table cites the Warcraft Wiki's [original zone-level guide](https://warcraft.wiki.gg/wiki/Zones_by_level_(original)) for classic zones, plus its [Riverglades](https://warcraft.wiki.gg/wiki/Riverglades) and [Zephras Isle](https://warcraft.wiki.gg/wiki/Zephras_Isle) pages for those Forever-specific zones. The wiki pages were inaccessible to automated retrieval during this update; the ranges were adopted from the pinned OpenMap table, not independently reverified against those pages. Classic-zone recommendations may not cover all Forever-added quests.

Cities and non-zone maps have no questing range. Unknown zones without a client range stay unlabelled rather than receiving a guessed value. Hovering the map heading shows which source supplied its range. Corrections should identify the zone/map ID and cite a source.

The continent label uses the native area's map ID under the cursor. It updates only the zone-name label and does not overwrite higher-priority POI banners. It does not modify global map APIs or another addon's data.
