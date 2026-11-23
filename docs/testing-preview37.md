# Preview.37: quest-log Navigate to

Install preview.37 and reload. Open the native quest log/world-map quest panel, then right-click an accepted quest title.

- Existing Track/Untrack, Share and Abandon entries should remain. **Navigate to** should appear alongside them.
- With one known objective or turn-in location, click Navigate to to start normal Mapperly navigation.
- With several locations, hover Navigate to and choose the desired objective, turn-in or travel waypoint. The submenu should scroll when long.
- With no verified location, Navigate to should be disabled; hover for the reason.
- Open a menu, then abandon, fail or complete the quest before activating an old objective. The stale action should be rejected without replacing navigation.
- An indoor/blocked exact location such as Mikhail should retain the previously implemented nearby-approach behavior. A destination selected during flight should keep normal landing deferral.
- Right-click a native user waypoint: no quest-navigation entry should be added to that nonquest menu, despite the shared native tag.

The hook uses the native Menu.ModifyMenu extension, not replacement of the native quest menu function. If the entry is missing, report which quest-log addon/frame is being right-clicked; third-party logs may use a different menu rather than the native one.
