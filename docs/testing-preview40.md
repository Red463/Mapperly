# Preview.40: nearest walking service

Install preview.40 and reload. Enable Smart routing. Open the map, click Destinations (the navigation arrow), then choose **Services**.

## Basic use

1. Around Darkshire / Duskwood 82.6,57.5, choose **Inn**, then **Find nearest**. Expect Innkeeper Trelayne, with a labeled nearby approach if the exact NPC cell is blocked. The list shows exact service coordinates; the route stops only on permitted terrain within30yd. Final building/platform access is manual.
2. Choose **Mailbox**, then **Flight master** and repeat. Native tests find each Darkshire location with one route calculation (1,280-1,536 reported terrain cells), but live timing and positions can vary.
3. Use **Preview** to review a route, then **Start**. Use **Go** to navigate directly. Walking-only routing excludes flights, boats and other vehicle legs, even if normal navigation allows them.
4. Choose **Dungeon entrance** to find a recorded entrance by calculated walking distance. Dungeon/raid wings sharing an entrance remain grouped. No questing/instance level restriction is inferred.

## Safety and interaction checks

- Search while following another route: guidance/history should remain intact. **Cancel search** cancels only that service calculation. Switching categories/tabs or closing Destinations cancels its own active search, without canceling an unrelated newer job. The main Stop button still explicitly stops navigation.
- Try near a zone boundary. A service across the border remains eligible. Overlapping map artwork may represent the same physical position; the current map is preferred when it contains the exact world point.
- Change road strength and search again. Calculations follow the current road setting. Search results describe distance from the search position; Preview/Go/preview Start calculate from the player's current position.
- Hide inn/mail/flight markers in Filters, then search again. Display toggles do not remove service locations.
- Change road settings while following a service route, use Replan, and toggle Smart routing off/on. The walking-only profile should survive. Ordinary waypoints still support enabled vehicles.
- Turn Smart routing off with an old result visible: Find nearest, Preview, Go and old preview Start must not silently turn a walking search result into a new direct-guidance action. An already active route can still follow your deliberate global direct-mode toggle.
- Check both Default and Minimal Charcoal themes and all five Destinations tabs for clipping.

## Coverage and limits

The finder uses bundled inn/mailbox spawns, native flight-master records, bundled dungeon entrances and same-faction observed interactions. Unknown access and explicit source-only flight destinations are excluded. Discovery of a flight is not required to walk to its master; this does not unlock flights. Snapshot data may be incomplete/outdated.

It checks up to12 viable route candidates and approximately350,000 reported terrain cells, using per-candidate limits. Candidates are ordered/pruned by an optimistic same-instance distance bound, adjusted for possible nearby approaches. A lower-bound candidate that hits a work limit prevents a proven-nearest claim. **Best found so far** remains a usable verified route, but another service could be closer. If no verified result is found, move closer or try another location; current navigation remains unchanged.

The finder compares calculated walking route lengths, including road-preferred detours. It does not claim collision-perfect shortest paths or access through unverified building floors. In-flight/active-ride searches wait until the ride ends; an unpermitted player starting cell must move to known walkable ground before searching.

Automated checks: `python tests/nearest_services.py`, `python tests/nearest_services_native.py`, `python tests/nearest_services_routing.py`, `python tests/nearest_services_ui.py`, `python tests/nearest_services_lifecycle.py`.
