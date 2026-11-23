# Preview.31: streets, docks and flight transitions

Requested fixes: Stormwind missing road preferences; boat docks omitted from roads; Auberdine-to-Astranaar takeoff starts recalculation and landing is slow to resume.

- [x] Reproduce takeoff recovery ordering with the actual navigation lifecycle and native Auberdine/Astranaar offers.
- [x] Suppress walking recovery while positively airborne, keep flight metadata refreshes quiet, preserve pending/deferred manual destinations and resume after positive on-foot landing evidence even when native Z is constant zero.
- [x] Extract missing Stormwind native WMO street material and replay the original collision/placement proofs.
- [x] Add bounded native dock road hints in six additional zones, preserving all original road cells and walkability permissions.
- [x] Certify two Stormwind harbour/pier corridors and use the true pier floor for the boat handoff. Follow that floor for boarding and departure access; project a disembarked player onto the current pier step.
- [x] Reject incomplete/stale supplements and required dock access data; add regression coverage.
- [x] Final complete regression run (64 suites), independent review and preview.31 package verification.

Review reproduced a missing-corridor crash in mixed data; dependent services now require the actual merged, build-matched corridor. Fresh review found no remaining substantive defects. Native verification replayed all 3,861 road triangles and both harbour corridor proofs. ZIP CRC and every TOC source entry match the final checkout. Live acceptance is documented in `docs/testing-preview31.md`.

Limits: native snapshot is build 70959; live client acceptance remains required. The link between the Stormwind descent and boarding pier currently uses an approximately 911-yard ordinary-ground detour. A shorter apparent ramp is not certified. Other dock-floor hints do not certify vessel boarding, headroom or whole-port access. Tilted placements and ports lacking verified floor geometry are excluded.
