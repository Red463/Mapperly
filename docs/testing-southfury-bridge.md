# Southfury bridge acceptance checks

Install `dist/Mapperly-1.2.5.zip`, replacing the existing Mapperly folder, then reload the UI. Enable Smart routing. These checks concern the stone bridge between eastern Ashenvale and southwestern Azshara.

1. Stand on the Ashenvale bank near 94.7, 47.8. Alt-right-click a destination beyond the Azshara landing near 10.6, 75.1. The route should cross the stone bridge rather than fail or head north to an unrelated boundary.
2. Walk across. The navigation arrow and route steps should continue across the bridge, then resume ordinary terrain guidance. Repeat from Azshara back to Ashenvale.
3. Stand near the center of the bridge deck and plan to either bank. The route should follow the remaining deck and finish on land. Test a destination near the bridge center from each bank too.
4. Repeat with Prefer roads enabled and disabled, and Avoid swimming enabled. The bridge should remain available in all cases.

The width proof covers the central 2.5-yard strip, not the entire visible model. If planning still fails there, paste `/mapperly report` immediately after the failure, including exact player coordinates. The screenshot's rounded 10.3, 75.0 is insufficient to identify the player's native floor reliably.

Automated checks: `python tests/southfury_bridge.py` exercises both directions, nearby bank approaches, partial-deck endpoints and guidance, and rejection below the deck and in another world instance. `python tests/structure_corridors.py` validates other native structures. Rebuild with `python tools/build_southfury_bridge.py`, then `python tools/build_structure_corridors.py`, `python tools/build_crossings.py` and `python tools/report_walking_coverage.py`.
