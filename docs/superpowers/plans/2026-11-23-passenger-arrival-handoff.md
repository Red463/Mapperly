# Passenger arrival handoff correction

## Report and reproduction
User reports Auberdine-to-Menethil walking route not connecting to the disembark location and triggering off-route handling. Native data separates boat stops from land handoffs; walking polylines begin at the static land point. Navigation.Tick previously rebased only lift exits. A real native Navigation.Start/Tick replay confirms the boat transitions to walking without the transactional actual-position replacement; its stale arrow still targets the old start. `python tests/passenger_handoff.py` failed the continuation-origin assertion before the fix.

## Fix
Extend the existing lift handoff branch to confirmed non-flight passenger arrivals. Preserve certified arrivalCorridor floor joins (Stormwind), normal arrival evidence and all pending/deferred guards. While replacement planning runs, the existing handoffPending state hides stale direction and skips normal recovery; only a successful plan replaces the established journey.

## Verification
Native Auberdine-Menethil replay covers replacement origin, quiet recovery during the update, arrow state, destination history, failure/cancellation and manual/deferred ownership. Native Stormwind pier replay retains its already joined protected floor without a replan. Existing lift regression passes unchanged. Independent review found no actionable defect. All85 suites pass. Local preview.41 package verified against every TOC payload and updated documentation.

## Prevention
Include a native boat-to-walking lifecycle regression alongside the lift exit test. Checking planned transport geometry alone does not exercise actual arrival position and route recovery ownership together.
