# Combat pin input and aura taint investigation — 24 November 2026

## Evidence

StutterAlert's 15:57 report on Forever 1.60.1 build 71037 lists 98 blocked
`Button:SetPassThroughButtons()` calls attributed to Mapperly, plus an aura
access warning surfaced through `secureexecuterange` in Blizzard Edit Mode.
The player was questing normally. The report abbreviates the warning stack;
it does not establish where the aura taint originated. Historical hitch totals
cover multiple versions and cannot establish a current performance regression.

The Forever UI source calls `pin:CheckMouseButtonPassthrough("RightButton")`
after **every** `OnAcquired`, including reused pins. The base implementation
clears and reapplies `SetPassThroughButtons`. Mapperly inherited it unchanged,
and refreshes its own pins from addon callbacks. There was no combat guard.

References:

- [AcquirePin](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_MapCanvas/Blizzard_MapCanvas.lua)
- [MapCanvasPinMixin mouse routing](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_MapCanvas/MapCanvas_DataProviderBase.lua)
- [Edit Mode secure iteration](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_EditMode/Shared/EditModeManager.lua)

## Scoped correction

Mapperly's own pin mixin now defers that callback during combat. Pending work
coalesces per pin and runs after combat using the latest pin data. Released or
hidden pins are discarded. Neither Blizzard's shared mixins nor other addons'
pins or protected setters are replaced. Last-applied mouse passthrough remains
in effect during combat; a newly created or repurposed pin can therefore have
different right-click propagation until combat ends. Existing navigation continues.

`python tests/combat_pin_input.py` reproduced the blocked setter before the fix
and passes afterward. This is a replay of the native acquisition contract with
a combat-restricted setter; it is not a reproduction of the engine's taint graph.
It does **not** prove that all 98 calls were Mapperly's own pins, nor that the
separate aura warning is fixed. Native quest/provider pins can have a similar path.

## Diagnostic build and testing

Build with `python tools/package_taint_diagnostic.py`. This includes the scoped
pin correction and the existing local 1.2.4 announcement changes. The diagnostic
module is excluded from the public TOC and normal build. No release is published.

1. Install the diagnostic ZIP's Mapperly folder and `/reload`.
2. Quest normally. Open/close the map with M before and during combat. Check that
   service/note/destination pins remain visible. When combat ends, check ordinary
   pin right-click zoom-out and note/destination right-click actions again.
3. After combat, run `/mapperly taintreport` and copy the report with Ctrl+C,
   whether or not the warning has appeared. Capture starts automatically.
4. If a warning appears, collect another report before reloading. If already
   reloaded, `/mapperly taintreport previous` reads the report saved at logout.
5. Test one session with Mapperly alone if the warning persists, then add other
   addons back. This distinguishes an independent failure from an interaction.

The diagnostic observes Mapperly blocked-action events, records bounded
delivery-time stacks and reads existing native error messages/stacks and selected
native-variable taint owners. It does not inspect auras, collect error locals,
hook native execution, replace the error handler, change CVars or send data.
Player name, GUID and realm are redacted. Current ownership and event stacks
are evidence for tracing; they do not necessarily identify the first taint source.

Automated coverage: `python tests/taint_diagnostics.py` checks bounded capture,
native full-stack inclusion, taint ownership, redaction, unavailable APIs and
ordinary slash-command forwarding. Final combat and aura behavior needs the
real client test above.
