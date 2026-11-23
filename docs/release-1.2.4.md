Mapperly 1.2.4 includes all updates since 1.2.0.

## Changes

- **New branding:** replace the old logo with the supplied blue-and-gold artwork. Use a clear small icon in the addon list, the M badge in map/window portraits and the full wordmark for project presentation. Transparency and original artwork are preserved.
- **Combat map controls:** move the unlocked map and close it with X or M during combat when the world map is unprotected. Native panel bookkeeping completes after combat without closing a map reopened in the meantime. Locking, resizing and actual protected-frame restrictions remain respected.
- **EnhanceQoL compatibility warning:** detect when EnhanceQoL Mover and its World Map entry are enabled. Show a themed warning once per session when opening the map, with instructions to untick World Map under `/eqol` > Interface > Mover > World, then reload. No EnhanceQoL settings are changed. Warnings wait during combat or other Mapperly dialogs.
- **Map diagnostic fix:** `/mapperly mapreport start` no longer enables mouse input on decorative trim and blocks title-bar dragging. Keep mouse-focus, layout, drag and setter tracing, and add title-bar/trim input state and protected-frame details to reports.

## Installation

Download **Mapperly-1.2.4.zip**, extract the `Mapperly` folder into `Interface/AddOns` and run `/reload` or restart the game. Reloading clears any diagnostic mouse handlers left by older builds. Existing settings, notes and saved destinations are preserved.

## Navigation feedback

Smart navigation remains a work in progress. Please report awkward paths, missing connections or transport handoff issues with the starting point, destination and copied `/mapperly report` output. For a map reset, run `/mapperly mapreport start`, reproduce it, then `/mapperly mapreport` and copy the report.

Validation: 105 automated test suites, branding pixel/alpha checks and installable ZIP/source verification.
