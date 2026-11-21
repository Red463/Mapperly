# Coordinate navigation

Add a standalone Mapperly destination guide similar to Gatherly's arrow. A new right-rail arrow button opens a small coordinate window for the currently viewed map, displaying its name and requiring X/Y percentages from 0 through 100. Decimal values are supported. Start validates input and map geometry before replacing an active destination; errors remain visible in the window. Stop navigation is available there and through right-clicking the HUD arrow.

The guide uses Mapperly's bundled HereBeDragons library for world positions, allowing direction and yard distance across adjacent zones on the same world instance. It samples position at 10 Hz and smooths rotation against current player facing every frame. Unavailable or protected positions and different world instances show an explanatory waiting state, never an invented direction. It is a straight-line bearing, not terrain/boat/portal routing. Arrival within ten yards clears the target.

The movable HUD is independent of the world map and remains visible after closing it. Use the existing user-owned Gatherly GuideArrow artwork, bundled into Mapperly; no runtime dependency or control over Gatherly's routes/arrow. Initial HUD placement is slightly right of center so both addons can be used together. Save only its position; destination is session-only and clears on reload. The active destination has a dedicated native map pin, independent of location filters and custom notes.

Use the existing charcoal/gold style and hover hints. Coordinate entry targets the map captured when opening the window, even if the map changes behind it. Continent/zone maps with valid world geometry are supported; disconnected world overview maps are rejected if projection is unavailable. The input window has X, Y, Start, Stop and Close, with Enter to start and Escape to dismiss. Settings and permanent note data remain unchanged.

Validation: malformed/out-of-range/empty coordinates, exact boundaries, preserved target on invalid replacement, map capture, cardinal bearings, angular wrap/smoothing, cross-zone versus cross-instance, missing/protected coordinates, arrival/cancel, HUD dragging, map pin filtering independence, map close, and ZIP integrity. Native visual behavior remains subject to in-game verification.

Version 0.1.30: the destination map pin now uses the generated painted Destination marker (gold rim, ruby-red center) via the shared size-tier texture path. The HUD and rail navigation arrow retain GuideArrow. Both pin interactions and filter-independent visibility remain unchanged. Source artwork/prompt: assets/Destination.png and assets/Destination-prompt.json.


## Destination library and richer notes (1.1.0)

The coordinate window now matches Settings with themed cards and controls. Coordinates, Saved and Recent tabs share the same captured-map navigation engine. Save stores a copied normalized record without starting guidance; a successful start remembers a copied record at the front of a deduplicated 20-item history. Favourites and history persist, while the active arrow remains session-only.

Alt-right-click places a waypoint immediately. High-priority native canvas/pin handlers consume modifier clicks before default zone navigation. The marker's exact normalized position is preferred over the cursor. A global mouse observer handles raw addon buttons inside native/HBD wrappers without replacing their scripts; it checks map ownership, matching down/up focus, and drag distance. The fallback waits until the next frame and skips clicks already handled by Mapperly/native handlers. This avoids releasing/reacquiring a pin before its own click completes while still supporting addons that override native OnClick directly. Alt-click continues placing notes; ordinary clicks retain their actions.

Custom notes have names, descriptions (up to 1,000 characters), optional groups and twelve new painted symbols (with older icon choices retained). Their category stays Custom notes. Click to edit; Alt-right-click to navigate; Shift-click to share into an edit box; right-click to delete. The draggable note window uses the same styling as Settings and offers a searchable My notes browser sorted by group/name. Empty names and stale note references cannot overwrite saved records. Saved data migration keeps existing note objects and validates new optional fields.

Validation also covers persistence, malformed saved records, coordinate precision, cross-map list actions, history dedup/capping, note creation/editing/deletion, search and icon selection, modifier-click consumption and small-screen window fitting. In-game rendering and the user's particular addon mix still need client verification.
