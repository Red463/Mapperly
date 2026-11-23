# Route Steps Visibility

User reports missing panel and requests default-on visibility. Default initialization was already true, but the old X action persisted showRouteSteps=false. No live SavedVariables or Lua-error capture was provided, so that failure path is confirmed in code, not asserted as the only live cause.

Restore enabled once for legacy profiles using a versioned visibility migration, as explicitly explained to the user; preserve all later explicit settings. X dismisses the current target reference only. Settings remains the sole persistent opt-out. Show a new target by default, layer the panel above the map, anchor/show the polling driver and refresh immediately when a destination activates.

- [x] RED test for close action vs preference and legacy default.
- [x] Separate temporary dismissal and persistent visibility, add overlay/driver guards.
- [x] Regression tests, independent review and preview.24 archive verification.

Live rendering remains pending; no route algorithms, masks, boats or flight data changed.
