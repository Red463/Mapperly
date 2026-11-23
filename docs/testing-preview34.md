# Preview.34: active quest navigation

Install the preview.34 Mapperly folder and reload. Open **Destinations** from the map's navigation-arrow button, then select **Quests**.

1. Search the name or ID of an accepted quest. Choose **Locations**, then **Preview** for a listed objective. Check the destination zone and coordinates before choosing **Go**. Existing road and transport preferences apply.
2. Check a quest ready for turn-in. Its locations should identify turn-ins rather than unfinished objectives. Game travel waypoints are labeled separately.
3. Check the source on a location row: **Game** comes from current quest pins; **Snapshot** comes from the pinned Forever database. Hover a row for the full title and source explanation. Snapshot objective progress may be unknown when the native log does not expose a matching objective ID.
4. Select a quest, then complete, fail or abandon it. Results should refresh. A stale location action must not start the old objective. Quest acceptance/progress events may refresh the list, but searching or refreshing must never replace current navigation by itself.
5. Collapse headers in the native quest log, then search again. Mapperly must leave those header states unchanged. Modern Forever enumeration should still include the quests; report any discrepancy with the live client.
6. Try a custom quest with no location data. It should explain that no verified location is available, rather than inventing a coordinate. Existing navigation should remain active.
7. Return to Coordinates, Saved and Recent to confirm existing actions remain available. Test both Default and Minimal Charcoal themes if used.

Coverage is deliberately partial. The public Forever database snapshot is not an authoritative export of the live realm. Item-drop guesses, polygon centroids, conditional/phased spawns and unsupported instance destinations are omitted. Some objectives offer multiple sampled spawn locations rather than every spawn. A known location can still fail terrain routing inside unsupported buildings or geometry; normal route failure preserves the previous journey.
