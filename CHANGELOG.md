# Changelog

## 1.2.0-preview.1 (local walking-navigation milestone)

- Bundle 55 terrain masks and local pathfinding independently of Gatherly, with explicit coverage/provenance.
- Plan walking routes in cancellable background jobs and follow their validated bends with the navigation arrow. Failures preserve the last successful destination and history.
- Add walking map lines, a themed preview with approximate distance/time and Start/Pause/Resume/Skip/Replan/Stop controls.
- Add Navigation settings with Walking route / Direct bearing and map-route visibility.
- Keep preview/map geometry synchronized after replanning; preserve pending replacement requests when the old target arrives.
- This first milestone is single-zone walking only. Transport, cross-zone, quest-search and road-preference features remain on docs/navigation-checklist.md.

## 1.1 - 2026-11-22

Release build **1.1.1**. This entry consolidates all changes since 1.0.0, including the initial 1.1 release and subsequent local development builds.

### Navigation and destinations

- Navigate directly to markers or place quick waypoints with **Alt-right-click**, preserving normal marker actions and the game's Ctrl-click ping system.
- Use **`/way X Y [name]`** to start navigation with decimal coordinates. Mapperly claims `/way` only when free and yields to other addons, including late-loaded handlers and cached registrations.
- Use **`/mapperly way X Y [name]`** whenever another addon owns `/way`. Commands use the viewed map while it is open, otherwise your character's current zone. Invalid input preserves the active destination.
- Save named destinations and revisit the latest **20 unique destinations** through Coordinates, Saved and Recent tabs. Favourites and history survive reloads.
- Preserve exact positions for supported Mapperly, native and addon markers; dragging does not place a waypoint.

### Custom notes

- Add and edit note names, descriptions, groups and icons in a dedicated window matching Settings.
- Browse and search notes across zones, navigate to them, share coordinates with Shift-click, or remove them with right-click.
- Choose from **twelve new painted symbols** with transparent, size-matched textures. The picker has no purpose labels, so each symbol can represent whatever the player chooses. Existing notes and older icon choices are preserved.

### Themes and map appearance

- Add the **Default** theme with warm Classic panels, Blizzard-style frames, native tabs and primary actions. Keep the previous look as **Minimal Charcoal** in Settings. Theme choices save immediately and switch without losing open drafts.
- Refine settings, note and destination windows, including button captions and inactive-tab spacing. Reset map position uses the native primary-button treatment, matching the red Blizzard Done button in Default.
- Fit the original Mapperly crest into its circular frame and use a standard Blizzard close button. Show Mapperly and the installed version in the title bar.
- Match the toolbar and footer to the brown header, keep frame borders consistent, and position toolbar controls below the header.
- Centre the zone name and level range in larger white outlined text; place native hover/POI labels on a separate row.
- Move Blizzard's Map Pin control to the upper-right of the map, clear of the crest and left-side addon controls.

### Position, sizing and usability

- Remember **independent compact and enlarged positions**, and allow dragging either unlocked view. Theme, lock and quest-pane changes preserve placement.
- Fit restored positions to the current display with room for the crest and borders, including ultrawide resolutions and UI-scale changes.
- Defer fitting/layout callbacks during dragging, save the released position first, then apply pending updates. Stop repeatedly invoking Blizzard's minimise/reposition routine on ordinary settings changes.
- Extend compact sizing down to **50%**, retaining readable text, marker sizes and native quest-pane width. Fit all toolbar actions on smaller screens.
- Keep player and cursor coordinates together at the left of the footer, separated by a pipe.
- Refresh hovered toolbar tooltips immediately after clicks and state changes.

Updating from 1.0.0 preserves existing settings, notes and preferences. No Gatherly or Questie dependency is added. Existing third-party licenses and notices are retained.

## 1.0.0

First public release for WoW Forever (Interface 16001).

- Remembered compact/enlarged map views, movable compact mode and stable movement opacity.
- Compact painted icon toolbar with dedicated settings, quest log and location controls.
- Standalone inn/mail data, dungeon entrances, flight masters and transport markers.
- Per-layer continent visibility and marker priority over standard gathering nodes.
- Custom notes, zone-level labels, optional unexplored-area reveal and coordinate readouts.
- Live marker-size previews and icon-labelled settings rows.
- Coordinate navigation with a movable direction/distance arrow and painted destination pin.
- Original Mapperly code released under MIT; third-party notices retained.

## Development builds

0.1.30 replaces the navigation destination?s plain map arrow with a hand-painted gold-and-ruby waypoint pin matching the map-marker family. It uses the current marker-size setting and 32/64/128px transparent texture variants. The gameplay HUD arrow and navigation behavior are unchanged. Source artwork and exact built-in image generation prompt are `assets/Destination.png` and `Destination-prompt.json`.

0.1.29 adds standalone coordinate navigation. The gold arrow button beneath My location opens X/Y entry for the viewed map (0?100, decimals supported). Start creates a destination pin and a movable direction/distance HUD that stays active after closing the map. Right-click the arrow or destination pin, or use Stop in the entry window, to cancel. Arrival within ten yards ends navigation automatically. The guide works across adjacent zones on the same world instance, waits when position/direction is unavailable or a different continent/instance is required, and provides a direct bearing rather than a terrain route. HUD position is remembered; destinations are session-only. Gatherly is not required and its route is not changed. See [navigation details](docs/navigation-design.md).

0.1.28 adjusts the dungeon swirl to a middle level of detail: defined painted ribbons, subtle brush texture and brighter edges, without the original dense fine streaks. Source and exact built-in image edit prompt are `assets/Dungeon-balanced.png` and `Dungeon-balanced-prompt.json`.

0.1.27 simplifies the blue dungeon portal swirl to a few broad, softly painted ribbons, reducing fine detail while retaining the stone frame and lighter blue palette. Source art and exact built-in image edit prompt are `assets/Dungeon-simple.png` and `Dungeon-simple-prompt.json`.

0.1.26 lightens the blue dungeon marker toward azure, retaining the doorway artwork. The lighter icon is shared by map pins, location-layer rows and live size previews. Source and exact built-in image edit prompt are `assets/Dungeon-light-blue.png` and `Dungeon-light-blue-prompt.json`.

0.1.25 replaces the dungeon marker with a blue variant of the purple portal artwork. Dungeon markers, location-layer rows and size previews share the new asset. Portal markers retain their original purple art. The source PNG and exact built-in image editing prompt are saved as `assets/Dungeon-blue.png` and `Dungeon-blue-prompt.json`.

0.1.24 refreshes the settings window with a branded charcoal header, highlighted page tabs, grouped display/size/opacity panels, and aligned location-layer rows. Every location name has its matching map-marker icon. The marker-size slider includes live inn, mailbox, dungeon and flight-master samples that use the selected dimensions and the same texture tier as actual map pins. Preview size restores on reopen; settings remain automatic and the window scales to fit smaller screens.

0.1.23 refines the compact icon directly from the expand artwork so its arrows share the same short, chunky proportions, broad heads and painted gold finish. Only the individual arrows? directions change. The source edit and prompt are `assets/toolbar/Compact-v2.png` and `Compact-v2-prompt.json`.

0.1.22 adds a generated inward-arrow icon for the Use compact map action. In compact mode the button shows outward arrows to enlarge; in enlarged mode it shows inward arrows to compact. The icon follows the saved map mode and updates immediately on layout changes. Source artwork and the exact built-in image_gen prompt are saved under `assets/toolbar/Compact.png` and `Compact-prompt.json`.

0.1.21 removes the icon-button borders and expands their solid face to the full 28-unit target. Artwork grows to 24 units with two units of padding; the rail narrows to 32 units. Filters uses a new generated stacked-map/checkmark icon instead of the funnel. The footer now contains separate Player and Cursor columns with explicit padding and width limits, plus clean placeholders when positions are unavailable. Its opaque background draws above legacy coordinate labels underneath it, avoiding competing text in the same strip.

0.1.20 replaces text actions with painted icons in a dedicated right-side rail. Buttons are 28?28 UI units with 20-unit icons, darker solid charcoal faces, complete borders, hover tooltips and active highlights. The rail reserves 36 units outside the map and quest content, preserving the map aspect ratio and native quest width. Nine new transparent icons match the existing marker style; the generated quest symbol is reused with its drawer arrow. The zone name and recommended level range remain in the header. Source art and exact built-in image-generation prompts are in `assets/toolbar`; `tools/build_toolbar.py` produces 128/64/32px RGBA TGA variants.

0.1.19 adds per-category **On continents** checkboxes under **Settings ? Location layers**. Dungeons are enabled on overview maps by default; every other category defaults to zone maps only. Overview includes continent, world and cosmic maps. The main Show/filter checkbox remains the master switch. Existing main filters and notes are preserved. Zone markers use the native layer immediately above AREA_POI resource nodes, below active quests and player/group arrows. Buttons now draw explicit pixel-snapped foreground borders, including the zone heading?s right edge.

0.1.18 keeps the native quest-list background fitted to the full list height. It restores the atlas coordinates after Blizzard?s fixed-height resize/crop and refits after quest updates, preserving both normal and empty-log artwork. This removes the exposed lower background band in taller Mapperly panels. The original background is stretched to the list bounds; quest rows, search, scrollbar and border remain native.

0.1.17 uses solid charcoal button faces with thin bronze borders, without gradients or bevels. Toolbar widths follow the actual font measurements to keep labels readable; the zone heading reserves space for those widths. The close button is labelled X. Custom notes consume right-click to remove the marker without navigating to the continent; other pins retain normal map navigation.

0.1.16 fixes the Add note dialog for Forever?s `GetEditBox()` API. Enter saves a named note; Escape cancels. Adding while viewing another map returns to your character?s zone, and saving enables the custom-notes layer so the marker is visible. Blank names keep the dialog open. Regression tests cover the button-to-marker flow.

0.1.15 implements the approved **Classic raised** charcoal button design: separate beveled controls with gold labels, a consistent rim, hover brightening, pressed depth and persistent active highlights. The quest drawer uses the same style. A taller header provides padding around the controls; map and quest layouts account for it. See [the approved design](docs/button-design.md).

0.1.14 simplifies dungeon entrance tooltips to names and level ranges only. Zone headings and continent-hover labels now show recommended questing levels when available: client map levels first, then a bundled cited recommendation table. Cities and unknown zones stay unlabelled. These are recommendations; Forever quests can extend outside them. See [zone-level sources and limitations](Data/ZoneLevels-SOURCES.md).

0.1.13 keeps the quest pane at its native width (at least 333 UI units) with separate gutters, rather than squeezing its fixed-width search bar, quest counts and rows into 300 units or less. The bottom-right quest toggle is a larger raised icon button with an opening/closing arrow, highlighted open state and pressed feedback. Layout regressions cover both quest states, both map modes and several screen sizes; real-client appearance still needs verification.

# Earlier development changes

0.1.11 — development build

![Mapperly logo](Media/Logo.png)

Native world map enhancements for WoW Forever (Interface 16001).

0.1.11 groups all text actions in the top bar, ordered My location, Add note, Filters, Reveal, Lock, Settings, then size and close. The quest icon remains over the bottom-right viewport. Text buttons use thin bronze edges, consistent padding, softer dark fills and distinct hover/pressed/active states; the footer contains coordinates only. My location fits the current zone and explicitly restarts the native two-second player-arrow ping on every click, including repeated clicks while already viewing that zone.

0.1.10 adds a generated gold quest-symbol icon matching the painted marker set. Markers up to 24px use dedicated 32px textures; larger markers use 64px textures, both resampled directly from source artwork. Pixel alignment is enabled when supported. This reduces reliance on the client shrinking a large texture to tiny marker sizes; actual small-size clarity still needs checking in the client. All three texture tiers retain transparent backgrounds.

0.1.9 replaces the native inn and flight-master markers with generated transparent hearthstone and winged-boot artwork matching the other painted map symbols. Source PNGs and generation prompts are in `assets`; the install ZIP contains the two 128?128 RGBA TGA textures. All ten marker textures pass transparency and encoding checks.

0.1.8 replaces square inventory-art markers with a generated transparent map-symbol set: sailing boat, zeppelin, airship, portal, dungeon entrance, mail, note and zone exit. Transport records retain their subtype so each route uses the right symbol. Inns and flight masters retain the native transparent hearthstone and winged boot. Textures are uncompressed 128×128 RGBA TGAs, drawn at the configured marker size (18px by default). Their alpha channels and encoding are checked by the test runner. Rebuild them with `python Mapperly/tools/build_markers.py`; the generated source atlas lives in `assets` and is excluded from the install ZIP.

0.1.7 changes the default marker size to 18px (saved sizes remain unchanged). Fixes movement-opacity flashing by removing the map from Blizzard's active and deferred movement-fade registries on each open; Mapperly alone applies its opacity preferences. Uses the client's movement-state API where available, with speed polling as a fallback. Settings sliders preview opacity immediately. Regression checks cover native-fader competition, repeated map opens, stop/start and enlarged mode.

0.1.6 uses the native transparent tracking artwork for inns (hearthstone) and flight masters (winged boot), replacing the square inventory icons. These client textures are also used by HandyNotes: https://github.com/Nevcairiel/HandyNotes/blob/master/HandyNotes_HandyNotes.lua .

0.1.5 uses a hearthstone icon for inns and boots for flight masters. Map text controls now have dark fills, gold-toned borders, larger Blizzard-font labels, padding, hover highlights and pressed feedback.

0.1.4 opens a dedicated draggable, Escape-closeable settings window from **Settings**. Map appearance groups coordinates, reveal, lock, quest visibility, compact size, marker size and stationary/moving opacity; size and opacity use sliders with explicit current values. Location layers provides the same category checkboxes as map filters. Changes save immediately; Reset map position and Done are available at the bottom. The quest-log action is a yellow quest-symbol overlay at the map viewport's bottom right, offset above existing fishing controls; its border highlights when open.

0.1.3 replaces raw canvas marker frames with registered MapCanvas POI pins. Native pin management now owns draw order, position and scaling. The filter count describes loaded locations, independently of its visibility checkbox; zero means no records for that category in the selected zone. `/mapperly debug` reports the loaded build, map ID and active pin positions/layers for troubleshooting.

The tiny item-picture controls are replaced with plain Blizzard-font labels: Quest log, Filters and Settings in the header; My location, Add note, Reveal and Lock in the footer. Size and close remain at the top right.

0.1.2 separates location filters from appearance settings and adds compact icon controls for quest log, locate, reveal, notes, position lock and settings. Red text buttons are removed. Filters contain only eight marker categories (with counts for the selected zone) and Show all/Hide all. Hover a control for its action; active quest/reveal/lock icons are highlighted.

Fixes world-coordinate axis order for bundled dungeon, transport and flight pins. Uses runtime-validated dungeon atlases with a spell-icon fallback instead of the previous unverified tracking texture. Reads inn and mailbox positions from an installed Questie database in small batches. Without Questie, inns and mailboxes still require recorded interactions or manual pins; there is no complete bundled database for them.

0.1.1 fixes the stale canvas zoom bounds after compact/enlarged switches. After the final viewport layout settles, Mapperly recalculates native canvas dimensions and resets to a centered full-zone view. This also applies when opening or closing the quest pane. Zoom and pan intentionally reset when changing layout.
