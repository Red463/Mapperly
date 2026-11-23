# Preview.39: shipped walking connections and cross-zone reuse

Install preview.39 and reload. There is no new setting: the accelerator follows Smart routing and the existing road preference/strength. Flight and transport availability are still checked for your character.

1. Set road preference to Firm. From Ashenvale around 85.2,44.6, navigate to The Missing Diplomat / Mikhail with the Astranaar-to-Auberdine offer recorded. Confirm the flight, onward boat and permitted endpoint are unchanged. Compare first calculation with preview.38.
2. Stop and immediately request the same route from the same position. The current session can now reuse walking results even after multiple zone searches. Changing start coordinates still requires a new approach.
3. From Duskwood around 77,44, preview a journey to Dun Morogh around 46,51. Compare cold and immediate-repeat generation, and check city threshold passages remain normal.
4. Repeat a journey at Light, Balanced, Strong and road preference off. Each mode uses its own validated prepared connections; do not expect identical route geometry at different strengths.
5. Try an arbitrary same-zone destination and an unprepared connection. Both must continue to calculate through normal terrain rules. Disabling Smart routing must still provide direct guidance.
6. Disable flight paths or a boat method and retry a journey: cached walking geometry must not make an unavailable vehicle selectable.
7. Cancel a long calculation. Existing navigation must remain unchanged. Check both Great Lift directions and dock boarding paths as ordinary regression checks.

The dataset contains 3,367 successful walking paths / 51,926 points in 48 zones. The builder attempts up to 32 exact fixed-anchor pairs per zone in six road modes; 1,730 unavailable/budget-limited attempts are omitted and use live fallback. This is partial acceleration, not complete routing coverage. Zones without effective roads share road-off geometry.

Session cache bounds are 512 live entries, 16,384 points and 16 terrain/road contexts. Reload clears it. The generated dataset adds approximately 12.9 MiB of Lua 5.1 heap in the host test; client overhead can differ.

See routing-performance.md for measured native examples. Live timing depends on position, cache state, route settings, character travel knowledge, frame rate and hardware.
