# Mapperly 1.2.0: release checks

Install Mapperly-1.2.0.zip, reload, then open the map with M. Existing preferences, notes and destinations should remain available.

- Check compact/enlarged map sizes, both themes, quest pane and moving/locking the map. Press M again to close it.
- In Navigation settings, switch Smart routing off/on and compare direct guidance with terrain routes. Try Prefer roads at different strengths and Avoid swimming if possible.
- Alt-right-click a nearby destination, then a destination in another zone. Check planning progress, world-map/minimap lines, turn-following arrow and route steps. Collapse/expand the step window.
- Take a detour and rejoin later in the route. Check pause/resume/replan and cancellation while planning.
- Plan a journey using known flights and a boat. Check step changes on takeoff, landing and disembarkation. Hover a boat on the continent/world map to preview its outgoing connections.
- Where available, check both directions of the Deeprun Tram and the Great Lift. Boarding remains manual. Tram guidance should advance after exiting into the destination city.
- Search Active and Find quests in Destinations, inspect known locations and try Preview/Go. Right-click a supported native quest-log entry for Navigate to.
- Find a nearby service under Destinations > Services. Confirm the service and route match your faction and current road preferences.
- Start a journey, reload and test the resume offer. Stop it and confirm it is not offered again.
- Confirm the welcome/update notice appears once, and respects open dialogs/combat. Existing installations should see What's new rather than a new-user welcome.

## Report a problem

- Route calculation or guidance: run `/mapperly report`, copy the text and include the starting point, destination and what happened.
- Map snapping back or resetting after settings: open the map, run `/mapperly mapreport start`, reproduce it, then immediately run `/mapperly mapreport` and copy the selected text. Capture before reloading. See [detailed map report instructions](testing-1.2.0-rc8.md).

The automated release suite covers the implemented paths. Native appearance, transport timing and character-specific addon interactions still benefit from live checks; terrain estimates do not guarantee indoor or collision-perfect access.
