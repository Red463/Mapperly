# Borderless map layout

User direction: follow the clean layout in the supplied Leatrix examples, with Blizzard-style typography, controls and map artwork. Remove the portrait, thick border, wood mat, duplicate coordinates and bottom action toolbar. Default to map-only; offer an optional quest pane. Keep two remembered screen-fitted sizes with game space around the large mode.

Shell.lua lays out the native ScrollContainer independently of its former portrait frame. The native map remains the pin-provider endpoint for Questie, Gatherly and RareScanner. Both native size entry points return to this same shell. Navigation, filters, locate, quests, size and close sit on one 26-unit top strip; coordinates appear once on a 20-unit footer. No crest appears over map content.

Forever API reference: Gethe/wow-ui-source, forever branch, Blizzard_WorldMap.lua, Blizzard_WorldMap.xml and QuestLogOwnerMixin.lua. The native QuestLog is attached directly to WorldMapFrame; BorderFrame can be hidden while retaining the map and quest contents.

Verification: Lua 5.1 compile and mocked regressions cover border/blackout suppression, default-hidden quest pane, native quest toggle synchronization, native maximize interception and screen bounds at 1024×768, 1280×720 and 2560×1080. Actual client appearance and interactions remain to be verified. The conversation preview is a layout concept, not an in-game screenshot.

## Canvas fitting correction (0.1.1)

The numbered in-game screenshots showed that the shell resized but artwork retained the old native minimum-window zoom bounds and pan. Native Minimize calls OnFrameSizeChanged before Mapperly sets its own viewport. Resizing the outer frame alone does not rebuild the MapCanvas zoom levels afterward.

Queue one fit after final anchors settle, call OnFrameSizeChanged to rebuild the native canvas extents, and ResetZoom(true) to center the zone without preserving a stale pan ratio. The ScrollContainer size hook covers late layout changes. Regression checks exercise initial open, six size toggles, coalesced delayed callbacks correcting stale geometry, and both quest-pane states. This is source-backed and mock-tested; the corrected in-game rendering still needs confirmation.
