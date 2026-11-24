# Clean travel connections — local 1.2.4

Install the updated ZIP and `/reload`. The previous background network is switched off once after this update. Your active journey, transport preferences and marker filters are retained.

1. Open a continent/world overview: the background network should be absent. In Settings > Navigation > Routing, **Show travel connections** should be unticked.
2. Enable Show and On continents for the relevant flight-master/boat layers in Location layers. Enable **Show travel connections**. Available connections should appear as smooth schematic arcs with a fine blue centre and subtle dark underlay. Reverse journeys between the same stops should share one arc. The layer is bounded to keep dense maps manageable; it is not a complete taxi-route atlas.
3. Hover a visible transport/flight marker. Its explicit preview should appear above the background. Click to browse destinations as before. Curved background links indicate connectivity; actual routes/continent hover previews retain native geometry where available.
4. Disable Show travel connections: all background curves should clear immediately. Hovering a marker should still preview its destinations. An active journey should retain its route and continue navigating.
5. Enable the setting, `/reload`, and confirm it stays enabled. Repeat with it disabled. The one-time migration must not repeat.
6. Check both themes, compact/enlarged sizes, map movement, zone-to-continent/world switching and quest pane resizing. Curves should remain anchored to their stops, clear off zone maps and have no black strokes covering their blue centres.
7. On a cross-continent boat route, inspect each continent and the world overview. Continent background arcs may summarise the visible native sailing piece; they must not connect separate loading/projection pieces. Your world-overview active boat leg should still span the ocean with its existing route display.

Automated checks cover defaults/migration/persistence, curve geometry and endpoint alignment, underlay ordering, reverse deduplication, drawing bounds/pool reuse, immediate toggle, native piece gaps, hover/active independence and marker eligibility. Native rendering/line joins at real UI scales still require the checks above.
