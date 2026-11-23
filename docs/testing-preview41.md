# Preview.41: boat arrival joins onward walking

Install preview.41 and reload. Recreate the reported Auberdine-to-Menethil journey with an onward walking destination beyond the harbour.

1. Board normally and sail to Menethil. Disembark and follow the dock onto land. Arrival still requires the existing destination/ground evidence; merely standing on a ship does not force a walking transition.
2. Once the transport leg finishes, expect a brief **Updating walking route...** state where the stale arrow is hidden. Mapperly recalculates the remaining journey from the confirmed landing position, keeping the existing destination.
3. When it completes, the walking line starts from that sampled landing position. You should not be sent backward to the old handoff point or get an off-route replan just because the original walking start was offset.
4. Repeat another boat connection, ideally Menethil/Theramore or Ratchet/Booty Bay. The same non-flight arrival handling covers passenger methods; flights keep their existing landing behavior.
5. Check Auberdine-to-Stormwind: the certified pier already joins its native floor, so that protected route should continue without replacing it with a general terrain shortcut. Existing native lift exit behavior should remain intact.
6. During the update, cancel, change destination or disable Smart routing. Cancellation/failure must keep the old established journey; a manual/deferred destination takes priority. Destination history should not gain duplicate entries.

This fix handles the transition after arrival is confirmed. If guidance stays on **Disembark** after you are on land, report the current map/coordinates and which dock you used; that is a separate arrival-recognition issue. Recalculation uses a sampled position, so continuing to move substantially during a long calculation can still require ordinary route recovery.

Automated reproduction: `python tests/passenger_handoff.py`. The native Auberdine-to-Menethil replay uses a permitted, confirmed landing point12yd beyond the static walking anchor. It failed before the fix, and now verifies that replacement geometry begins at the actual point while recovery stays quiet. Existing lift, flight, transport and harbour regressions also remain required.
