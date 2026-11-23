# Blocked quest endpoint fix

Screenshot: player Ashenvale85.2,44.6, quest The Missing Diplomat with Mikhail at Wetlands10.6,60.8. Reproduced from actual bundled quests1248/1249/1250: player cell is allowed, exact NPC point is prohibited, and Terrain.Approach finds permitted region1 ground3.2293yd away.

Add a quest-only routing target resolver after stale selection validation. Smart routing uses a permitted endpoint within30yd when the exact target is blocked, without drawing or authorizing the final segment. Copy/retain exact source coordinates, label the adjusted endpoint as an approach, and explain manual final access. Direct mode remains exact. No approach within the bound fails before altering navigation. Preview and Go share the resolver.

Regression drives actual snapshot source and full mixed journey, plus both UI actions. Terrain masks and global routing endpoint rules are unchanged. Review, full suite and package preview.35 before delivery.

Verified: actual Mikhail approach is3.2292876744yd from exact spawn and the full screenshot journey plans4legs in603 deterministic slices. UI regressions cover both Preview/Go and preview Start. Review found the preview Start stale-action bypass; fixed by re-resolving with explicit preview mode before Navigation.Start. Final review found no further defects. All70test suites pass. Final ZIP CRC and allTOC source entries match checkout. No Terrain.lua or mask changes, so existing native proof bindings remain unchanged.
