# Quest background sizing

The native QuestScrollFrame uses a fixed-size QuestLog-main-background atlas, anchored at the top left. QuestLogScrollFrameMixin:ResizeBackground caps the texture at its existing height and crops shorter views. Mapperly's taller quest pane exposes the underlying frame below that texture, creating a horizontal change in background.

Shell.lua refits only QuestLog.QuestsFrame.ScrollFrame.Background to the entire scroll frame. It restores the current atlas without its fixed size, then anchors all four edges to the list. A single post-hook on ResizeBackground reapplies this after native quest refreshes. Normal and empty-log atlases are retained. Details backgrounds, list contents, search controls, scrollbar and decorative frame are untouched.

Native source inspected on 2026-11-21:
- https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestMapFrame.xml
- https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/QuestMapFrame.lua

Tests reproduce the fixed-height crop, then verify full-frame anchoring, preserved atlas UVs, native resize callbacks, empty-log artwork and both map sizes across tested screen dimensions. The native artwork stretches vertically in taller panels; an in-game visual check is still required.
