# Road preference strength

Add a five-step saved slider beside Prefer roads: Light, Moderate, Balanced, Firm, Strong. Balanced retains the current 1.35 off-road cost; the other costs are 1.10, 1.20, 1.75 and 2.50. Strength is a preference, not a promise to remain on roads or a hard maximum detour. Disabled smart routing or road preference disables the control while retaining the saved value. Keep the existing settings card dimensions and Blizzard slider style.

1. Add regression coverage for defaults/validation, meaningful route differences and strength-aware caching, local/cross-zone propagation, settings state and replanning.
2. Implement saved roadPreferenceStrength, strength normalization, per-request weighted routing/cache separation, and navigation setter with existing airborne deferral.
3. Add slider and clear help text, preserve both themes, run regressions, update documentation and package preview.32. No publication requested.

Implemented and independently reviewed. Native route regression confirms Strong takes a longer road detour than Light, strength changes invalidate cached geometry, saved values reach local/cross-zone requests, UI enablement/persistence work, and changes replan the pending destination once. Additional flight review confirms a queued manual destination remains deferred during flight.

The initial full run caught the lift audit's expected stale Terrain.lua digest. Replayed the original native exit audit: both masks are identical (1,312 upper and 911 lower cells). Refreshed the pinned runtime hash, retained the native revalidation proof, regenerated LocalTransports and reran all three affected lift suites successfully. Final complete rerun: all 65 suites pass. Preview.32 package CRC and all TOC entries verified against the final source.
