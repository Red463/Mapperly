# Mapperly 1.2.0-rc.2: installation and acceptance tests

This is one local release candidate containing the navigation roadmap implementation. Automated checks cannot establish live platform/floor access or appearance on your client. Please test the six priority checks below and send a route report for any failure. You do not need to repeat every older preview test.

## Install

1. Close WoW, back up your current Mapperly folder and SavedVariables if desired, then replace the addon folder with the `Mapperly` folder from `Mapperly-1.2.0-rc.2.zip`. Do not nest the folders or leave a second copy enabled.
2. Log in and confirm **Mapperly 1.2.0-rc.2** in the map header. Existing notes, destinations and preferences should remain.
3. Open Settings > Navigation. Its three sections are **Routing**, **Travel methods**, and **Recovery and reports**. Smart routing defaults on; Avoid swimming if possible defaults off. Remember journey also defaults on. Existing saved display preferences remain yours.

## Priority 1: swimming preference

- In Routing, turn Prefer roads off temporarily to isolate water behavior. Preview a nearby destination across a pond or coastline with Avoid swimming if possible off, then on.
- A reproducible native-mask example is Elwynn Forest: start **53.001, 36.421**, destination **55.762, 36.421**. Use only if the starting bank is accessible on your client. Offline checks find approximately 100 yards with swimming and a 2,078-yard dry detour. Preview is enough; no need to walk the long detour. Another accessible pond is fine.
- Expected: off retains ordinary water-permitted planning; on prefers a dry detour. If no dry route is found, retry with swimming permitted and explain the retry in the preview. Also try a permitted destination inside water: navigation should still work. It must never silently draw a straight line through water after a planning failure. Previously installed navigation remains if the new request fails.
- Unknown liquid cells are unavailable during the dry attempt; failure retries under ordinary terrain permissions. Roads do not prove bridge floors, so unmodeled bridges may be rejected. Separately certified floor corridors remain usable.
- Restore your preferred road setting afterward. Also change Avoid swimming if possible during a boat/flight/recorded ride: it must not trigger unsafe mid-ride progression. Installed recorded rides retain their validated arrival policy; subsequent plans use the new preference.

## Priority 2: record and follow a tram

Open `/mapperly connections`, or Navigation > Travel methods > Recorded connections.

1. Choose Tram. At a safe, permitted city-side approach in Stormwind, before entering the station portal, choose **Record start**. Use a clear direction name.
2. Enter the station, ride to Ironforge, disembark and exit through the destination city portal. On safe city ground, choose **Capture end**.
3. Read the measured endpoints and observed duration, tick the verification statement and save. Waiting and walking are included in this estimate.
4. Use **Go to start** to return to the source approach. Within 18 yards, choose **Follow ride**. Follow the indicated ride manually.
5. At the destination, step off on the correct floor, open Active journey and choose **Continue on foot**. Loading/station interiors must retain the transport step. Arrival must not happen just because map coordinates overlap.
6. Record an actual reverse ride separately if wanted. Disable/remove the row or turn off Trams: new plans must not use it. Re-enable the preference afterward.

If either endpoint is rejected for missing terrain or native position disagreement, do not move the record onto an unrelated floor to bypass it. Export a report at the rejected spot. This identifies the floor/access data still needed.

**Data limit:** native Deeprun portal pairing is source-audited, but platform stopping positions and all city floor handoffs are not yet certified. No automatic native Deeprun or capital lift route is bundled from that incomplete evidence. Personal measured connections work only where both endpoints have permitted coverage.

## Priority 3: additional lifts and overlapping floors

- Repeat recording with Lift, standing off the vehicle at each safe landing. Record each direction separately; pending captures are not saved across reload.
- At the source use **Follow ride**, especially when both floors have the same map coordinates. Ordinary Go to coordinates cannot distinguish those floors.
- Expected: the ride stays active until explicit Continue on foot at the correct destination landing. Wrong instance, unavailable/mismatched native position, blocked ground, taxi/vehicle use, swimming, or being over 18 yards from the measured endpoint rejects confirmation.
- Try switching Smart routing off during the recorded ride: it should explain that you must finish or stop the ride first. It must not declare arrival at the starting floor.
- Existing Great Lift: test both lanes, viewed from the top, down and up. Its native arrival handling should remain unchanged.

## Priority 4: recover a journey after reload

1. Start a short walking journey and pause it. Run `/reload`, then stand still on safe land. Resume/Discard should appear with the destination and coordinates.
2. Resume: planning must start from your actual current position and retain Paused. Use normal journey controls to resume walking.
3. Repeat while moving to another location before reload. No saved bend/index/floor progression should be reused.
4. While aboard a flight, boat or lift, reload. Recovery must wait for a stable on-foot location and require explicit safe-land confirmation. For a recorded floor crossing, finish the ride manually and confirm at its measured destination floor.
5. Stop, arrive, or Discard, then reload: there should be no offer. Turn Remember journey off to disable future recovery. Another character must not receive this character's destination.
6. Cancel or fail a resumed plan and try `/mapperly resume` again. It should remain available. An accepted new manual destination should dismiss the old offer; a rejected request should not consume it.

Recovery is destination-only and character/build scoped. WoW must have saved its SavedVariables; an abrupt process crash cannot guarantee the latest state was written. Changing addon/client build withholds incompatible recovery entries.

## Priority 5: boat-to-walking connection

- Navigate **Auberdine to Menethil**, then a land destination beyond the dock. Disembark normally and walk along the pier/shore.
- Expected: confirmed arrival immediately plans onward walking from the actual landing position. No backwards arrow toward the static dock anchor and no spurious off-route loop. Loading or standing aboard must not falsely complete the ride.
- If convenient, also test the certified Stormwind boat pier. Unsupported floor shortcuts must not replace its established corridor.

## Priority 6: settings, reports and layouts

- Switch Default and Minimal Charcoal. Check all Navigation sections, recorder, recovery offer and report at your normal UI scale and compact map size. Text/actions should remain inside the frame; changes should preserve map placement.
- On ultrawide, drag compact and large maps, lock them, change theme and reload. Neither view should snap back or clip its header.
- Open `/mapperly report`, copy with Ctrl+C and paste into a text editor. Repeat after a failed route and after cancelling a long calculation. The report should show settings, coordinates, recent outcomes, counters and native position/movement flags, with unavailable values clearly marked.
- The report must exclude player name, realm, GUID and wallet. It is bounded and never sends automatically. `/mapperly resume` and `/mapperly connections` should open their respective tools.

## Optional regression checks

| Feature | Test | Expected |
| --- | --- | --- |
| Flights | Southshore to Goldshire with Stormwind flight offered/unlocked | Compare eligible flights; no replan aboard; onward walk after landing |
| Quest destinations | Active quest, catalogue pickup, native log Navigate to | Destination revalidated; nearby approach clearly labeled; flight/boat options considered |
| Cross-zone walking | Duskwood to Dun Morogh | Connected walking route or explicit current eligibility/coverage reason |
| Nearest service | Darkshire inn/mailbox/flight master | Shortest reachable walking result; hidden marker layer does not hide search results |
| Detour recovery | Leave a walking route and rejoin farther along | Stable advancement/replan without returning to an old bend |
| Route display | Winding route, minimap, world-view boat segment | Direction marks, completed fading, correct arrow turn and ocean connection |
| Prepared paths | Repeat same long route and road strength | Reuse where compatible; reports distinguish work; the dry attempt cannot reuse an incompatible water-crossing path |
| Existing data | Notes, favourites, history, markers, /way | Preserved; other addons' /way ownership respected |

## What to send back

For a failure, send the copied `/mapperly report` plus:

- Which numbered test failed and what you expected versus saw.
- Start/destination map and coordinates, direction of travel, and relevant setting changes.
- For a boat/lift/tram: before boarding, aboard, or after disembarking; which landing/lane; whether Continue on foot was clicked.
- A screenshot for clipping or appearance; screen resolution and UI scale for ultrawide problems.

Native tram/capital lift coverage and live UI/arrival acceptance remain explicit verification work. A recorded connection does not certify a whole city floor graph.
