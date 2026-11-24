## Mapperly 1.2.4

### Fishing levels on your map

- See both **minimum and recommended fishing skill** beneath the zone's quest-level heading.
- Hover the fishing line for source details, lure-bonus guidance and exceptions for special waters.
- Fishing data is bundled with Mapperly, so no other fishing addon is needed. These are published reference values, not verified live server requirements; zones without reliable reference coverage stay blank.

### Cleaner travel connections

- Optional flight and transport connections now use smooth curves with a fine blue line and subtle dark outline.
- Return connections are drawn once to reduce clutter.
- Background connections are now **off by default**, including once after this update. Enable them under **Settings → Navigation → Routing → Show travel connections**.
- Your active journey and marker-hover previews remain available independently. Background curves show connections between stops, rather than exact travel paths.

### Interface and combat improvements

- Refreshed the **What's new** window with clearer release highlights, better spacing and a layout that fits its content.
- Improved combat handling for Mapperly markers by waiting until combat ends before applying restricted mouse-input changes.

**After updating:** run `/reload` or restart the game. Your saved map settings, notes and destinations are retained, apart from the one-time travel-connection default change described above.

Smart navigation remains a work in progress. Feedback and route reports are welcome; use `/mapperly report` when reporting a navigation problem.

Validation: **111 automated test suites passed**. The installable ZIP's integrity, runtime manifest and packaged source files were also verified. Native rendering checks are documented in the included testing guides.
