Mapperly 1.2.2 fixes opening the map during combat.

- Open the closed map with **M** or **`/mapperly`** during combat, including the first opening after login.
- Preserve the prepared compact/enlarged layout and quest-pane choice instead of entering the combat-blocked native panel-opening path.
- Complete deferred layout after combat using the saved position, without closing a map reopened in the meantime.
- Retain native map-disable rules, actual protected-frame restrictions, and the movement/closing fixes from 1.2.1.

Install **Mapperly-1.2.2.zip** and run `/reload` or restart the game. Existing settings, notes and saved destinations are preserved.

Validation: **106 automated test suites passed**, including combat opening through both commands, first-show initialization, repeated toggles, both sizes/themes, quest-pane preferences and combat-end processing. The release ZIP is checked against current source and includes a SHA256 checksum.

For an in-game check, leave the map closed, enter combat, then open/close it with M and try `/mapperly`. See the [test guide](testing-1.2.2.md). Some game modes or addons can genuinely protect or disable the map; those restrictions remain respected.
