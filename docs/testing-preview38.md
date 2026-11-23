# Preview.38: flight itinerary search priority

Install preview.38 and reload. Keep Flight paths and boats enabled in Navigation settings.

1. On the original character, start around Ashenvale 85.2,44.6. Select The Missing Diplomat / Mikhail using Quests or the quest-log Navigate to action.
2. Try Balanced, Firm and Strong road preference. The planning panel now shows how many recorded flight routes are eligible, alongside path and terrain counters.
3. With an observed Astranaar-to-Auberdine offer, expect a flight to Auberdine, the boat to Menethil and a walk to Mikhail's nearby approach. Routes may vary with this character's other recorded flights.
4. If zero flight routes are considered, open the departure flight master's window to record its offered destinations. Merely knowing both masters, or recording only the reverse flight, does not establish an outbound offer.
5. Check a normal same-zone walking route, an adjacent-zone walk and a boat journey. Cancel a calculation and confirm existing navigation remains unchanged.
6. Check the failure panel with flights disabled or unavailable: it should explain flight eligibility without hiding the original failure reason.

Automated reproduction uses actual bundled terrain and transport data with exactly one recorded flight offer, and cold terrain caches at each road strength. It checks that both the flight and boat are selected without raising the search budget. Live flight availability and client timing still need confirmation.
