# Mapperly 1.2.0 development history

Archived preview and release-candidate notes; the final 1.2.0 changelog describes shipped behavior. Earlier experiments may have been superseded.

## 1.2.0-rc.8 (local release candidate)

- Add `/mapperly mapreport` to open a themed, copyable map-position report in normal builds. Include current map, canvas and viewport geometry, UI scale, screen size, anchors, saved compact/enlarged positions, layout flags and loaded addon identifiers.
- Add opt-in `/mapperly mapreport start` capture for reproducing map snap-back or settings resets. Record setters and caller stacks, drag delivery, mouse focus, layout calls and observed geometry changes; exporting stops capture. `/mapperly mapreport stop` also stops recording.
- Keep diagnostic history bounded and session-only, guard unavailable API values and redact player identifiers. Reporting never saves, resets or changes map layout. This provides evidence for native-client position issues; it does not claim to fix the reported snap-back.

## 1.2.0-rc.7 (local release candidate)

- Add a brief Welcome to Mapperly window for first launch, covering map customization, useful locations, navigation and quick controls.
- Show concise What's new in Mapperly notes once for each new installed version. Announcement history is shared across characters; reloads and zoning do not repeat notices. Existing installations receive update notes rather than a new-user welcome.
- Match the selected addon theme, with native close/Escape and Got it controls. Defer announcements during loading, combat or other Mapperly dialogs.
- Generate packaged update notes from concise player-facing release highlights, with a matching-version check so future releases cannot accidentally ship stale notes.

## 1.2.0-rc.6 (local release candidate)

- Fix normal navigation rejecting all destinations from Ironforge positions marked blocked by the outdoor terrain mask. Valid city starts and destinations can use explicitly labeled city-direction guidance when an indoor path is unavailable.
- Keep existing terrain paths where they work; support normal journeys within Ironforge and city access legs entering/leaving through its native entrance. Terrain masks and outdoor permissions are unchanged.
- Keep city direction guidance active without obstructed-route messages or repeated off-route replans. Release inherited entrance-floor state only after leaving the protected gate volume. Pause/resume remains available; follow city walkways to the marker.
- Preserve strict walking-only nearest-service comparisons and certified floor/dock handling. Add native and actual navigation-entry regressions for masked starts, masked goals, city entrance directions and normal permitted routes.

## 1.2.0-rc.5 (local release candidate)

- Simplify tram guidance to: walk through the source city portal, ride and exit the destination city portal, then resume walking. Support both directions without recording, exact exit-radius, height or terrain-cell arrival checks.
- Keep the walk stage active until station entry is observed, including when the final outside position sample was missed. Loading and conflicting position sources cannot complete the transition.
- Use normal city walking paths where available; fall back to clearly labeled portal bearings for tram access/egress across indoor mask gaps. Keep ordinary routes, walking-only service searches and certified dock access separate.
- Continue city walking after arrival or replanning without aiming back at the portal or requesting another tram round trip.

## 1.2.0-rc.4 (local release candidate)

- Remove player-recorded tram/lift connections, their capture/verification window and settings entry. Existing saved recordings are no longer used.
- Bundle both fixed Deeprun Tram directions from native Subway spawns, paired server portals and source-verified native city exit floors. No trip recording or character setup is needed. Actual boarding/riding remains a player action.
- Recognise the station instance and paired city exit automatically, then advance to walking without a manual arrival acknowledgement. Reject loading, conflicting public position sources, wrong instance/floor and vehicle/swimming state; support public map/HBD positions when native coordinates are protected.
- Keep native Great Lift handling. Stormwind's broader station-to-city walking corridor remains unverified after clearance checks; the tram is used only where the existing walking network can reach its station approaches. No straight walking shortcut is invented.

## 1.2.0-rc.3 (local release candidate)

- Make M close an already-visible Mapperly map when character-specific native map/quest-log preferences disagree with Mapperly's layout. Keep native opening behavior, global keybindings/rule checks and panel close cleanup.
- Add regression coverage across native maximized/quest settings and Mapperly size/quest-pane combinations; retain position persistence and the header close button.

## 1.2.0-rc.2 (local release candidate)

- Replace Allow swimming with Avoid swimming if possible. Try a complete dry itinerary first; if the bounded dry search cannot find one, retry with swimming permitted. Ordinary terrain restrictions still apply.
- Migrate the former disabled-swimming setting to this preference. Temporary dry policies are isolated per search; live arrival checks still permit swimming. Explicit internal dry-only checks remain available.
- Explain swimming fallback in journey previews and include the preference in route reports and recovery snapshots. Revalidate all 3,367 prepared paths against the updated water module.

## 1.2.0-rc.1 (local release candidate)

- Add Allow swimming (on by default), backed by native liquid classifications across all 55 terrain maps. Disabled mode rejects water and unknown liquid coverage; certified floor corridors remain separate. Revalidate all 3,367 prepared walking paths and native lift exit proofs against the updated routing inputs.
- Add personal one-way Tram/Lift recording with measured endpoints, observed journey duration, character/build scope and explicit verification. Go to start and Follow ride support repeatable travel, including identical-coordinate lift floors. Arrivals require Continue on foot; unproven native tram/capital lift floor data stays unbundled.
- Remember validated destinations per character and offer safe Resume/Discard after reload or login. Replan from current position, retain paused intent and require land/floor confirmation after transport. Stop, arrival and Discard clear recovery.
- Add a bounded, copyable route problem report with recent successful/failed/cancelled calculations, settings, counters, native position and movement flags, excluding names, GUID and wallet.
- Group Navigation settings into Routing, Travel methods, and Recovery and reports; preserve both themes. Add /mapperly connections, /mapperly resume and /mapperly report.
- Preserve the actual-position boat/lift walking handoff and existing quest, service, flight, road, minimap and route-step features. See docs/testing-1.2.0-rc1.md for live acceptance tests and data limits.

## 1.2.0-preview.41 (local build)

- Fix the boat-to-walking handoff retaining a precomputed shore start instead of the actual confirmed disembark position. Extend the existing transactional lift-exit update to non-flight passenger arrivals so normal route recovery does not treat the transfer as a detour.
- Hide the stale walking arrow during the immediate onward update, retain the established journey until success, and keep manual/deferred destination changes ahead of automatic handoff work. Failure/cancellation preserve current navigation without a repeated handoff loop.
- Keep certified native dock floor continuations intact, including Stormwind's pier. Arrival confirmation, vessel/deck/floor checks, terrain masks and prepared walking data are unchanged.
- Add an actual Navigation.Start/Tick replay for Auberdine-to-Menethil at a permitted landing point beyond the static anchor, covering the replacement route origin, off-route suppression, history, cancellation/failure and pending/deferred ownership. Verify native Stormwind pier continuation and existing lift behavior.

## 1.2.0-preview.40 (local build)

- Add Services to Destinations with Inn, Mailbox, Flight master and Dungeon entrance categories, existing marker icons, source/exact coordinates, walking distance, Preview and Go. Fit all five tabs within the existing window and retain both themes.
- Find the nearest calculated reachable walking route under current road settings, including zone crossings. Use standalone bundled/native locations plus your observations, apply faction/class/access restrictions and include services whose marker layers are hidden.
- Keep the search cooperative and cancelable, with up to 12 route candidates and bounded terrain work. Distinguish a confirmed nearest result from Best found so far when lower-bound candidates remain budget-limited or unchecked. Search, failure and cancellation preserve current navigation/history.
- Revalidate service sources and access on actions, including preview Start; reject stale result actions while Smart routing is disabled. Replan from the current player location, preserve walking-only intent through request/recovery/preferences, and leave ordinary transport navigation available.
- Retain exact native flight-master positions and access flags. Source-only destinations are excluded; native handoffs or terrain approaches beyond 30 yards are not presented as service locations. Mark nearby approaches and manual final access explicitly.
- Native Darkshire checks find innkeeper Trelayne, the mailbox and flight master with one walking route calculation each (1,280-1,536 reported terrain cells). Existing precomputed paths and cross-zone cache remain in use.

## 1.2.0-preview.39 (local build)

- Ship 3,367 precomputed walking connections (51,926 polyline points) across 48 zones, covering road-off and all five road strengths where applicable. Use exact verified travel anchors; missing and failed offline pairs retain live terrain search.
- Keep bounded walking results across zone and road-mode changes for the current session. Limit retained runtime geometry to 512 entries / 16,384 points and 16 source contexts; return copies and preserve maximum-distance checks.
- Match generated paths to revisioned terrain/ground/road content signatures, validate every accepted baked polyline, and fall back for stale or malformed data. Source SHA256/output proofs and reproducible offline tooling are included.
- Clear the legacy inner path cache before fresh searches to prevent stale in-place ground/road changes from leaking into new contexts. Cooperatively hash cold inputs. Terrain permissions and the search algorithm remain unchanged; native lift mask audit is refreshed with exactly the same exit coverage.
- Native Firm benchmarks: the Mikhail flight/boat journey searches 165,376 cells instead of 252,928 (35% less); Duskwood-to-Dun-Morogh searches 578,304 instead of 1,053,952 (45% less). Immediate repeats use zero terrain-search cells in both cases. These are controlled tests, not guaranteed live timings.

## 1.2.0-preview.38 (local build)

- Prioritize promising complete flight/boat itineraries before calculating unrelated walking approaches. Queue inexpensive connection estimates, then validate terrain paths as needed within the existing search limits.
- Add a cached, goal-specific lower bound using eligible transport combinations. Keep recorded directional flight offers, cumulative fares, terrain restrictions and road strength unchanged.
- Show the eligible recorded flight count while planning and on failure, with guidance when flights are disabled or no eligible offers exist.
- Reproduce Ashenvale 85.2,44.6 to The Missing Diplomat/Mikhail with a recorded Astranaar-to-Auberdine flight: Balanced, Firm and Strong now complete using the flight plus boat in four to six local walking searches.

## 1.2.0-preview.37 (local build)

- Add Navigate to to the native quest-log right-click menu. A single known destination starts routing directly; multiple objective/turn-in/travel-waypoint locations appear in a scrollable submenu.
- Keep the existing quest actions and other menu extensions. Quests with no verified destination show a disabled action with an explanation; ordinary user-waypoint menus are unchanged.
- Revalidate captured destinations on click, preserving stale-quest rejection, nearby approaches, existing route failure handling and flight deferral. Support late loading of the native menu API without duplicate registration.

## 1.2.0-preview.36 (local build)

- Add Active / Find quests scopes inside the Quests tab. Search the standalone catalogue by name or ID, view known starter locations and Preview or Go using the existing routing and nearby-approach handling.
- Bundle 48,793 named snapshot quests; 3,702 have verified starter positions. Keep quests with missing/item-only starters searchable and explain unavailable locations without inventing coordinates.
- Distinguish possible pickups, known restrictions and unconfirmed availability. Check character completion, active quests, fixed level requirements, race/class and supported prerequisites; explicitly mark repeatable resets, skill/reputation/exclusive and other unevaluated conditions.
- Revalidate pickup actions, including preview Start, after acceptance/completion or changed requirements. Bound catalogue results to 100 and debounce typing; preserve the existing active-quest workflow and both themes.

## 1.2.0-preview.35 (local build)

- Fix quest routing to NPCs or objects whose exact coordinates fall in blocked terrain cells. Smart routing can use permitted ground within 30 yards, clearly labeled as an approach; the final approach remains manual.
- Preserve the exact quest coordinates in the location list and use them unchanged in direct mode. Both Preview and Go validate the latest quest state and nearby endpoint; an unavailable bounded approach keeps the current navigation intact.
- Revalidate quest destinations again when pressing Start inside a route preview, including previews opened before abandoning, failing or completing a quest.
- Reproduce the reported Missing Diplomat/Mikhail case: the exact Wetlands point is blocked, while the nearby approach is 3.23 yards away and supports the complete Ashenvale-to-Wetlands transport journey.

## 1.2.0-preview.34 (local build)

- Add a Quests tab to Destinations: search active quest names/IDs, choose a known objective or turn-in location, and Preview or Go using existing routing. Keep Coordinates, Saved and Recent available in the same themed window.
- Use current native quest pins and separately labeled travel waypoints. Bundle standalone, source-pinned Forever objective/turn-in locations for 5,415 quest IDs; no Questie dependency or runtime download.
- Show Game/Snapshot provenance, unavailable-location explanations and uncertain individual objective progress. Filter completed objectives where reliable IDs exist and turn-ins by faction; revalidate active quest and selected location before starting a route.
- Refresh visible quest results as the log changes without selecting quests, expanding headers or moving the native map. Searching and unavailable quest actions preserve current navigation.

## 1.2.0-preview.33 (local build)

- Avoid expensive neighboring-zone searches when no eligible transport combination can improve an already valid local walking route. Use an optimistic, inexpensive transport graph that retains useful combinations of flights and vehicles.
- Cache each grid cell's road cost during a search and reuse the current cell's cost across its neighbors. Preserve the selected road strength, smoothing costs, terrain restrictions and existing route geometry.
- Reproduce the reported Ashenvale route: Firm searches approximately 46% fewer cells and performs 93% fewer road lookups, with the same 4,326-yard route. Host benchmark CPU time falls from roughly 3.35 seconds to 1.61 seconds; live gains depend on route, machine and frame rate.
- Revalidate native lift exit masks against the updated terrain implementation; coverage remains unchanged.

## 1.2.0-preview.32 (local build)

- Add a saved Road preference strength slider in Navigation settings: Light, Moderate, Balanced, Firm and Strong. Balanced preserves the previous preference; stronger settings accept longer detours along known roads.
- Apply strength to local and cross-zone walking searches and route smoothing. Separate cached routes by strength; changing the setting replans the selected destination using the existing flight deferral rules.
- Disable the slider when smart routing or road preference is off, retaining its saved value. Strength changes do not alter terrain restrictions, certified dock access or areas without road data.

## 1.2.0-preview.31 (local build)

- Add native Stormwind WMO street paving and verified static dock floors to road preferences. Extend dock hints to Ratchet, Southshore, Booty Bay, Menethil, Rut'theran and the Feralas coast. Original terrain permissions remain unchanged; unverified ports and tilted dock placements remain outside this supplement.
- Replace Stormwind's city-level boat handoff with the actual Auberdine boarding pier. Add separately certified city-to-harbour and pier corridors; boat approaches/exits follow the pier instead of taking a terrain/swimming shortcut beneath it. Stepping clear of the vessel resumes onward guidance without pointing back to the boat.
- Prevent off-route recovery and flight database updates from replacing a journey at takeoff. Preserve manual destinations requested or completed during flight, including the first destination, until positive landing evidence is available.
- Resume walking on the first on-foot update at the destination flight master when Forever supplies constant zero altitude. Retain guards for loading, unknown taxi state, conflicting positions and readable wrong-floor heights.
- Reject stale or incomplete road/harbour proof combinations. The remaining ordinary-ground link through Stormwind harbour can still take a detour; no unproven shorter stair connection or universal dock coverage is claimed.

## 1.2.0-preview.30 (local build)

- Add interactive boat, zeppelin, airship and discovered flight connections on overview maps. Hover markers to highlight outgoing links; click to choose a destination with Preview or Navigate actions.
- Add faint background transport links and an Overview transport links toggle in Navigation settings. Existing location-layer and On continents filters remain in force; flights use this character's recorded, currently eligible offerings.
- Extend native transport markers to zeppelins/airships and retain flight-master identities. Revalidate selected connections before acting; preserve Ctrl-click pings, Alt-right-click waypoints and normal right-click map navigation.
- Keep world-overview connections schematic, native continent geometry/breaks intact and active/hover overlays prioritised within rendering caps. Destination planning chooses enabled methods rather than forcing the clicked service.

## 1.2.0-preview.29 (local build)

- Update onward walking immediately after leaving a lift, using the player's actual exit position. Avoid pointing back to the old arrival marker while waiting for ordinary detour recovery.
- Hide the outdated arrow during the short walking update. Preserve pending/deferred destinations, destination history and the current route if the replacement fails.
- Handle delayed native zone assignment at the upper exit by projecting the same player position onto the verified current walking map, with normal ground validation.
- Replay the recorded left-lift handoff through the real navigation HUD. The trace confirms lift detection completed before the previous 59-yard backward aim and delayed walking replan.

## 1.2.0-preview.28 (local build)

- Replace reliance on tiny lift exit circles with broad native-checked ground coverage around both Great Lift landings. Walking away in another direction can now resume the journey without crossing a particular marker.
- Cover 2,223 checked four-yard cells within 200 yards of the handoffs. Retain exclusions for tower/shaft projections, unsafe terrain, wrong-floor readings and conflicting positions.
- Add regressions across every included cell, alongside the recorded trip replay.

## 1.2.0-preview.27 (local build)

- Fix lift guidance using Forever's constant zero altitude as real height. Use neutral lift instructions when height cannot distinguish waiting from riding.
- Add native-checked dry exit areas clear of the Great Lift tower in both directions. Resume walking after reaching those areas, including the alternate walk-off in the captured report, without requiring the old arrival marker.
- Keep shaft/tower projections excluded and reject readable wrong-floor heights. Replay the actual zero-height failure with native data; retain explicit confirmation elsewhere when height is unavailable.

## 1.2.0-preview.26 (local build)

- Fix lift guidance staying on Board the lift when the client misses a readable source-floor sample. Recognise a ride already in progress and accept the verified destination floor without requiring recorded departure.
- Guide players towards the landing marker after reaching the destination floor, then resume walking at the handoff.
- Retain wrong-floor rejection, protected-height confirmation and loading preservation. Add missed-boarding regressions in both native Great Lift directions and full-data planning coverage.

## 1.2.0-preview.25 (local build)

- Add manual Great Lift navigation in both directions, using native dry approaches, static landing evidence and floor-aware arrival checks. The 120-second planning allowance is an estimate; boarding and landing access remain manual.
- Add an independent Lifts preference, enabled by default. Keep unverified Trams disabled with an explanatory tooltip; no unproven station connections are included.
- Preserve navigation through lift position/loading gaps, detect vertical departure and require explicit arrival confirmation when height is unavailable. Add concise lift/tram step labels and rearrange travel choices into two rows.
- Keep the tram milestone partially open: native station pairing and city floor access need verification. Other capital lifts remain outside bundled coverage.

## 1.2.0-preview.24 (local build)

- Restore on-screen route steps to enabled once for older saved profiles, where closing the panel could have saved the option as disabled. Subsequent explicit changes in Navigation settings remain remembered.
- Closing the panel now dismisses it for the current target without disabling the saved setting. A new route shows it again when enabled.
- Keep the panel above the world map, explicitly activate its refresh driver and refresh it immediately when navigation activates.

## 1.2.0-preview.23 (local build)

- Remove Drag to move and Journey steps text from the route panel. Minus now shrinks it to the current step only; plus restores the expanded list.
- Show schematic dashed connections across the ocean for boat legs on the Azeroth world overview, including journeys that cross continent/loading boundaries. Retain native sailing geometry on closer maps.
- Hover a boat marker on an overview map to preview its outgoing route and destination. Clear the preview on leave, pin recycling or map changes, without changing active navigation.
- Use native boat-stop markers with explicit service identities; keep continent-marker visibility configurable as before.

## 1.2.0-preview.22 (local build)

- Put bright route chevrons on an explicit draw sublevel above their dark outlines. Avoid relying on same-layer creation order, which could leave the dark outline covering the arrow on both maps.
- Preserve marker size, contrast, stroke gaps and route progress behavior.

## 1.2.0-preview.21 (local build)

- Give route steps consistent 20-pixel content insets, padded rows, clearer spacing and more bottom clearance.
- Add matching travel-method symbols for walking, flights, boats, zeppelins and airships. Keep completed icons muted and the current row highlighted.
- Use concise labels such as Fly to Stormwind and Boat to Menethil Harbor. Keep detailed current boarding/navigation instructions in row hover tooltips, and preserve dragging through the rows.

## 1.2.0-preview.20 (local build)

- Make route direction chevrons larger, brighter and thicker, with a dark outline on both maps.
- Leave a small gap in the route stroke behind each marker so the arrow remains distinct. Preserve gaps across dense bends without reconnecting transport splits or covering the minimap player arrow.
- Retain spaced, capped markers and faded completed sections.

## 1.2.0-preview.19 (local build)

- Use classic red buttons consistently for dialog actions across Settings, Destinations, Notes and Journey controls. Keep native tabs and quiet note-icon choices; mark the selected theme clearly.
- Replace flat grey settings groups with tiled native rock textures and opaque warm backing. Warm the main dialog backgrounds to match the Blizzard frame.
- Update button captions and disabled states immediately, without waiting for a hover. Preserve Minimal Charcoal styling and live theme switching.

## 1.2.0-preview.18 (local build)

- Fix Stormwind's flight handoff being assigned to a walking component disconnected from the city exit. Use the exact native flight-master position and pad height on the existing exit-connected component; platform access remains manual.
- Southshore to Goldshire now chooses the faster Stormwind flight-plus-walk journey when that flight is recorded and available. Add native regression coverage comparing both flight choices and build-time exit-connectivity validation. No terrain permissions or routing preferences changed.

## 1.2.0-preview.17 (local build)

- Fade completed route sections on the world map and minimap, using actual follower progress. Preview-only routes remain unfaded.
- Add subtle, spaced direction chevrons along remaining sections. Keep walking gold, transport blue, native route gaps intact and minimap player-arrow space clear.
- Show up to ten journey steps, including completed steps. Highlight the current step and mute completed ones; longer journeys keep the current step in a numbered ten-row window.

## 1.2.0-preview.16 (local build)

- Match small navigation windows to the main Mapperly frame family using the native no-portrait panel, without a Mapperly crest.
- Add an opaque brown base beneath the leather texture so the game cannot show through the panel. Preserve Minimal Charcoal theme switching.
- Use compact native plus/minus icons and fit controls and titles to the native header height.

## 1.2.0-preview.15 (local build)

- Restyle planning feedback and on-screen route steps with native Blizzard dialog textures, framed brown title bars and standard red buttons in the Default theme.
- Fit collapse/close controls inside the route panel heading, improve text alignment and add breathing room around dialog content. Keep Minimal Charcoal selectable.

## 1.2.0-preview.14 (local build)

- Add an on-screen route steps panel with the current instruction, destination and next three journey legs. Update it automatically as you travel, including flight, crossing, pause and replanning status.
- Drag the panel to move it, collapse it to reduce obstruction, or close it without stopping navigation. Position, visibility and collapsed state are remembered.
- Add On-screen route steps to Navigation settings. The panel follows the selected theme, fits smaller screens and hides when navigation ends.

## 1.2.0-preview.13 (local build)

- Add character-specific discovered flights to mixed journeys. Learn only routes actually offered by a visited flight master; retain directed itineraries, full quoted fares and faction/class restrictions without sharing discoveries between characters.
- Bundle native geometry for 65 flight masters and 286 directed segments. Raised and indoor masters use explicit manual access; Freewind Post permits live boarding outward but remains unavailable as a planned arrival pending a verified handoff.
- Add the saved Discovered flight paths preference and discovery/recorded-route counts. Journey previews show each flight fare and total, marking old quotes, estimates and unknown prices clearly.
- Hide the walking arrow during flight, retain guidance through loading screens, resume on a verified landing and make one safe route-update attempt after an early landing. Destination and preference changes in flight wait until landing and retain the latest target.
- Keep normal manual flight selection in Blizzard's flight window. Native flight time and historical prices remain estimates; in-game acceptance is required.

## 1.2.0-preview.12 (local build)

- Add 25 directed boat, zeppelin and airship links across 12 verified passenger services, including both Zephras airships. Respect faction routing recommendations and saved travel choices.
- Plan mixed walking/transport journeys with approximate total time and walking-only distance. Preserve circular sailing order and keep the player aboard through intermediate stops on one vessel.
- Guide to a dry land approach, show manual boarding/travel/disembarking instructions and retain the route through loading screens. Check native approach height before resuming ground guidance; protected-height cases can use Continue on foot at the destination.
- Add boat/zeppelin/airship controls to Navigation settings. Changes aboard replan the remaining journey after landing, retaining the latest requested destination through repeated changes.
- Draw native sailing geometry in blue on both maps; omit manual shore-to-vessel joins and teleport gaps. Times include stated assumptions and are not live timetables.

## 1.2.0-preview.11 (local build)

- Resolve the five previously listed walking gaps: all three Timbermaw branch pairs, Ironforge's main entrance and Undercity's static sewer. Coverage is now 121 links across 68 distinct zone pairs.
- Include short native stair risers regardless of face direction or group name when proving Timbermaw paths. Retain separate branch identities and sampled native floors; preserve existing terrain permissions.
- Use proven city floor anchors rather than assuming the overhead root terrain is the indoor floor. Undercity follows the dry static sewer route, avoiding its native liquid pool and elevators.
- Add forward/reverse passage tests and complete Bloodvenom Post â†’ Everlook (5,747 yd) and Astranaar â†’ Everlook (9,788 yd) planning regressions. Full indoor city navigation and live-client passage acceptance remain separate work.

## 1.2.0-preview.10 (local build)

- Audit native zone ownership boundaries; expand from 49 to 116 walking links across 63 distinct zone pairs. Add 61 dry-ground crossings in 28 formerly missing pairs without requiring a road texture.
- Add native-floor-supported Dun Morogh gate/approach tunnels, Talondeep and the winding Blackrock passage. Restore only the original dry Dun Morogh outpost ground connected by these tunnels; retain blocked/unknown terrain elsewhere.
- Use exact connected-ground labels to skip impossible local searches. Duskwood to Dun Morogh now plans successfully with road preference enabled.
- Follow winding tunnel floor paths across early/delayed map changes, tolerate ordinary movement past dense samples and recover safely after an outdoor deviation at a tunnel entrance.
- Publish a complete boundary coverage report with explicit unresolved Timbermaw, Hyjal and underground-city geometry. No guessed mountain or transport shortcuts.

## 1.2.0-preview.9 (local build)

- Show a planning panel above the map immediately after Alt-right-click or other manual walking requests. Display destination, current stage, elapsed time and real search activity without a misleading percentage.
- Show route completion briefly and keep failures readable until dismissed, including unsupported far-zone connections. Walking previews use the same feedback while calculating.
- Cancel only the pending calculation, retaining existing navigation. Bind feedback to job identity so stale results cannot replace newer status. Automatic detour updates retain their existing HUD feedback.

## 1.2.0-preview.8 (local build)

- Add multi-zone walking across 49 terrain-validated outdoor crossings connecting 32 zone pairs. Preserve road preference, background planning and transactional destination/history behavior.
- Continue guiding across a boundary until the client changes zones, then follow the next local leg. Handle overlapping map assignments without premature leg jumps or turning back while zone updates lag.
- Render complete mixed-map journeys on the world map/minimap, and list all zone legs in a scrolling preview. Scope detour recovery to the current leg.
- Missing connections and underground cities fail explicitly. Swimming remains permitted by the existing masks; transport transitions such as the Great Lift are deferred.

## 1.2.0-preview.7 (local build)

- Recognize sustained, walkable rejoins farther along the route and advance the navigation arrow without sending the player back to missed turns. Guard ambiguous crossings and overlapping legs.
- Automatically recalculate after a sustained detour, retaining the destination, road preference and previous guidance while planning. Throttle attempts and preserve the old route on failure.
- Keep automatic work separate from manual requests/previews. Cancel it on pause, stop, arrival, mode changes, a replacement destination or successful forward rejoin. Restricted player cells do not trigger replanning loops.

## 1.2.0-preview.6 (local build)

- Calculate walking HUD direction from the same local player position, route bend and map extents as the route follower, avoiding inconsistent separately sampled world coordinates.
- Show distance to the next route turn under the arrow and total route distance separately. Advance to the next leg at each bend; direct guidance retains destination distance.
- Cover winding routes with a destination in a different direction, automatic turn advancement and unavailable/inconsistent world-position feeds.

## 1.2.0-preview.5 (local build)

- Add optional **Prefer roads where possible** under Navigation settings. Smart routing favors native road/cobblestone terrain while respecting existing walkability masks. Direct guidance is unchanged.
- Preserve road bends during route smoothing and replan the current smart destination when the preference changes. The setting is saved and defaults off.
- Bundle independently generated road masks; missing road coverage falls back to ordinary terrain costs. Generic dirt is excluded, and paved town areas may count as roads.
- Generate a local overlay gallery and extraction inventory for every local map in the supplied terrain metadata; raw game artwork is excluded from the addon package.

## 1.2.0-preview.4 (local build)

- Draw navigation routes on the minimap, with movement/zoom/rotation updates, round/square clipping and a gap around the native player arrow.
- Add a Smart routing checkbox, enabled by default. Switching it off immediately converts the active or pending destination to straight-line guidance; switching on plans a walking route.
- Keep world-map and minimap line toggles separate. Direct guidance draws a live straight line on both maps and has a matching preview.
- Refresh the active direct-journey view as the player moves, and remove its geometry when navigation stops.

## 1.2.0-preview.3 (local build)

- Keep existing route guidance running when the player enters a restricted terrain-mask cell. Preserve the route geometry and current waypoint instead of hiding the arrow.
- Allow resume, manual skip and arrival advancement from restricted player cells. Restore normal segment checks when the player returns to permitted terrain; planned paths remain mask-constrained.
- Add follower and actual HUD regression tests for restricted-cell movement and recovery.

## 1.2.0-preview.2 (local build)

- Draw walking routes above native exploration/highlight map artwork, following Gatherly's route-layer ordering; account for stitched OpenMap artwork when present.
- Clear the pending preview message on success and report native display errors instead of leaving an apparent planning stall.
- Use an explicitly visible, noninteractive background worker frame and guarded profiling-clock fallbacks.
- Add regressions for the supplied Elwynn coordinates, real frame-callback completion, native map-art tiers and display/timer failures.

## 1.2.0-preview.1 (local walking-navigation milestone)

- Bundle 55 terrain masks and local pathfinding independently of Gatherly, with explicit coverage/provenance.
- Plan walking routes in cancellable background jobs and follow their validated bends with the navigation arrow. Failures preserve the last successful destination and history.
- Add walking map lines, a themed preview with approximate distance/time and Start/Pause/Resume/Skip/Replan/Stop controls.
- Add Navigation settings with Walking route / Direct bearing and map-route visibility.
- Keep preview/map geometry synchronized after replanning; preserve pending replacement requests when the old target arrives.
- This first milestone is single-zone walking only. Transport, cross-zone, quest-search and road-preference features remain on docs/navigation-checklist.md.

