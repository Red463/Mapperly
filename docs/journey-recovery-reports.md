# Journey recovery and route reports

Remember journey is enabled by default. Mapperly saves one validated destination, its routing preference snapshot, paused intent, and a conservative transport/floor-crossing warning for the current character. It retains at most eight character entries. It saves no route point arrays, indices, raw flight/boat state, or floor progression. Addon version, client build, and interface version must match before a saved destination can be offered.

SavedVariables are written by WoW at its normal save points. Recovery supports reload, logout/login, and disconnects for which WoW actually saved the variables; a process crash cannot promise a new save.

After world entry, recovery waits for a readable character identity and actual map position. Taxi flight, vehicle use, and movement defer the offer. Resume always calculates a new route using current navigation preferences. A paused walking journey becomes paused after the replacement plan is installed. A saved transport or floor crossing additionally asks the player to confirm they have reached safe land; no boat arrival or previous floor is inferred. Stop, arrival, Discard, and forgetting the saved journey clear that character's recovery target. A pending or failed replacement request preserves the last installed target. A deliberate destination accepted while flying can replace the saved intent and is marked in transit.

The compact Resume/Discard window and the route report use the existing Minimal Charcoal and Default theme roles without a crest. The report offers selectable text for manual copying and never transmits anything. It is limited to 16,000 characters, six recent calculation results, and four rejected requests. It includes coordinates, options, route method/step, bounded errors, calculation counters and elapsed time, available source/cache metadata, water coverage, guarded native position and movement/vehicle flags. It excludes player name, realm, GUID, wallet, destination labels, and raw saved variables.

## Live acceptance

1. Enable Remember journey in Navigation settings. Start a supported terrain journey, pause it, and `/reload`. Wait on land for Resume/Discard. Resume must calculate from your current position, then retain Paused. Resume walking normally through the existing journey controls.
2. Start a journey, change position, reload, and resume. The route must begin at the actual new location. It must not jump to a saved bend, tunnel floor, boat, lift, or flight leg.
3. During an active journey, request an unsupported replacement and let it fail. Reload: recovery should still offer the previous installed destination. Repeat with a replacement cancelled during calculation.
4. Reload while aboard a taxi flight. No calculation should start aboard. After landing and stopping, recover through the explicit on-land confirmation. Repeat with a boat or lift: disembark onto a safe land approach before choosing **On land: Resume**.
5. While a saved offer is visible, intentionally choose another destination. The old offer must disappear and cannot later replace the newer journey or pause it.
6. Stop a journey, reload, and verify it is not offered again. Repeat after arrival and after Discard. Log in on a different character and verify no other character's target is offered. Changing the addon/client build should withhold incompatible recovery state.
7. Open `/mapperly report` with a route active. Copy using Ctrl+C. Trigger a failed replacement, reopen the report, and verify both the established destination and failed request are present. Cancel a long calculation and verify its cancellation and counters appear. Confirm your player name, realm, GUID and money are absent.
8. Repeat the two windows in both themes at compact UI scale. Verify every label, action and report scrollbar remains accessible; nothing should obscure the Resume/Discard text.

## Integration

`JourneySession.Normalize(db)` validates and bounds the store without resetting other fields. `Capture(target?)` records only the committed target, or an intentional deferred target; never `Navigation.pending`. `Installed(candidate)` runs after `Journey.Install` and before the first navigation tick so paused intent is applied before progression. `Intent()` invalidates restore ownership when a new manual request is accepted. `Clear()` clears the current character and restore ownership. `Open()` offers compatible recovery or returns a diagnostic. The module owns throttled world-entry and logout events.

`RouteReport.Open()` displays the copyable report; `Build()` returns its bounded plain text. `RecordRequest(candidate, reason, start?)` retains synchronous rejected requests, including those made while a previous route remains active. `PlanningJob.Recent()` returns bounded copies of result observability, recorded before the active job is cleared. Replaced jobs may be recorded as cancelled, but cannot publish a stale completion over a newer job.

Settings > Navigation > Recovery and reports contains Remember journey, Resume saved journey, Forget saved journey and Route problem report. `/mapperly resume` opens compatible recovery; `/mapperly report` opens the report. Transport recovery never restores a raw ride index or assumes an old arrival. Known tram/lift connections are bundled; player trip recording has been removed.
