# Flight itinerary search priority

## Reproduction
Ashenvale 85.2,44.6 to the verified Mikhail approach in Wetlands fails at Balanced/Firm/Strong despite a recorded Astranaar 28 to Auberdine 26 offer. Eager expansion evaluates every outgoing local walking connection, including unrelated Darkshore and Barrens approaches, before validating the final Wetlands walk. The shared two-million-cell budget is exhausted.

## Implementation
- Add a cached goal-specific relaxed transport bound. Same-instance straight walking and eligible vehicle times provide an optimistic estimate; the actual search retains terrain, road costs and cumulative fares.
- Queue connection and goal lower bounds before spending terrain work. Validate only when a task becomes the most promising frontier entry.
- Keep walking-only adjacent-zone handling, bounded cooperative jobs, path caching and validated dock access.
- Expose eligible flight count and unavailability explanations through the existing progress UI.

## Verification
Real-data regression at Balanced, Firm and Strong must select the recorded flight and onward boat with fewer than 16 walking searches and one million cells. Independently check lower-bound admissibility against an oracle, including multi-vehicle chains and shared flight-master positions. Run the full existing regression suite and independently review the lazy frontier and fare handling before packaging preview.38.
