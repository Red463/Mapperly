# Preview.31 acceptance checks

Replace the existing Mapperly folder with the preview.31 folder and reload. The map title should say `Mapperly 1.2.0-preview.31`.

## Street and dock preferences

Enable **Settings > Navigation > Smart routing** and **Prefer roads where possible**. Plot a journey through Stormwind's streets. Compare with road preference disabled; the enabled route should favor the added native street paving where feasible. These are planning hints, not a visible road overlay.

Repeat a Stormwind–Auberdine boat journey in each direction. The Stormwind approach should reach the actual pier, follow its floor instead of cutting through the water underneath, and continue inland after stepping off and walking clear of the vessel. Boarding the boat remains manual. Walking on the ship deck alone should not advance the route.

Additional static dock hints cover Ratchet, Southshore, Booty Bay, Menethil, Rut'theran and the Feralas coast. Full vessel/stair access is not newly certified at those ports. Stormwind's middle-harbour ground connection still takes a detour; a shorter ramp is not verified.

## Flight transition

With the character's offered Auberdine–Astranaar flight recorded, start a journey that includes that flight and a final walk beyond Astranaar. Board the offered flight manually.

- At takeoff, the active journey should remain and the HUD should show flight guidance without a new planning popup.
- At Astranaar, walking guidance should resume on the first position update after the client reports the player on foot.
- During a flight, set a different destination. It should wait until landing, then plan from the landing position. The same applies when starting the first destination while already airborne.
- Loading or unavailable taxi state should preserve the journey and saved destination rather than invent a landing.

If a check fails, report the journey endpoints, character faction, road preference state, displayed route step, and whether the issue occurs at takeoff, aboard, or after walking clear of the destination.
