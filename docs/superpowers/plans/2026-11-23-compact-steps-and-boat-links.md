# Compact Steps and Boat Overview Links

User scope: remove Drag to move/Journey steps labels; minus collapses to only the current step. Show boat travel across the ocean on world overview; hovering a boat previews its route.

RouteSteps: retain movable header, icons and full expanded ten-step list. Hide destination/status in collapsed mode and render only the current leg. Keep pause/update status when expanded, remove static help and section labels.

BoatLinks: draw visual-only logical port-to-port dashed connections on Azeroth overview (947), projecting each endpoint through HBD even across continents. Retain native split sailing geometry elsewhere. Show hover previews on overview maps without changing active navigation or preferences. Native boat pins should identify their directed transport service; replace older boat inventory pins with native stop pins when data is available. Preserve optional continent marker filter and all other marker categories.

- [x] RED tests for compact current-only steps and no static headings.
- [x] RED tests for cross-continent overview links and hover lifecycle.
- [x] Implement shared boat overlay, native pin identities and release/leave cleanup.
- [x] Verify navigation/pin/line/UI regressions, independent review and preview.23.

No fabricated walking connections or transport availability. Ocean overview links are schematic, not exact sailing trajectories. Live visual acceptance remains pending.
