# Walking coverage audit

User request: check and fill all missing walking connections. Preserve native terrain restrictions and never invent an unsupported shortcut.

- [x] Audit every supported native MCNK ownership boundary and unassigned-area bridge candidate; retain an inventory of rejected pairs.
- [x] Remove the road-texture prerequisite for independently dry, permitted boundary connectors. Add 61 links across 28 missing pairs; rank main ground regions before edge islands.
- [x] Extract and validate native gate floor profiles; recover the two original dry Dun Morogh outpost components linked by those tunnels.
- [x] Add winding, floor-supported Talondeep and Blackrock corridors, retaining their native world-coordinate polylines.
- [x] Label exact ground components for all 55 masks to reject disconnected local endpoint pairs cheaply, with source-hash guards.
- [x] Verify complete native Duskwood → Dun Morogh planning with road preference: 7 legs, about 9,364 yards, 294 cooperative steps.
- [x] Review runtime following; reproduce and fix missed dense floor samples and an off-corridor recovery coordinate error. Test coarse movement in both directions and nearby parallel hairpins.
- [x] Investigate Timbermaw's three branches, Hyjal cave, Ironforge and Undercity; record concrete proof blockers instead of certifying them from area names or asset availability.
- [x] Resolve Timbermaw native stair/portal connectivity and verify all three branch paths, reverse following and service-to-service journeys in automated tests.
- [x] Prove Ironforge/Undercity entrance floors and native interior anchors; retain existing ground permission.
- [ ] Validate these passages in the live client. Full indoor city navigation remains a separate future feature.
- [x] Publish coverage inventory and local preview.10. No GitHub publication requested.

Current data: 121 links, 68 distinct non-self zone pairs in preview.11. The five previously listed gaps are resolved with native-floor proofs. The audit covers supported maps; complete coverage of unknown custom areas, indoor city geometry and transports is **not** claimed.

Research artifacts are under `../output/walking-structure-audit`; generated ownership inventories and ground corrections are under `../output/zone-crossings-70959`. Source snapshot stays read-only. See `Data/Structures-SOURCES.md` and `docs/walking-coverage.md` for evidence and limitations.
