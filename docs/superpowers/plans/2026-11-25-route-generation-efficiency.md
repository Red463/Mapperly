# Route generation performance

Use the frozen 42-route survey and the production Lua planner. The main reproduction goes from Ratchet (62.4, 37.8) to Shimmering Flats (78, 75) with swimming allowed and Firm road preference.

1. Reproduce the cold failure and record local search budgets, connectivity and the transport actually taken.
2. Test a coarser search for long walking connections. Use the original terrain, road costs, water policy and corner rules. Validate completed paths at full resolution. Keep the detailed search available for narrow passages.
3. Avoid repeating identical budget-limited searches in the same session. Keep retries available when direction, source data, policy, scope or work allowance changes.
4. Compare elapsed time, expanded cells, reliability, walking distance and selected transports. Run the primary matrix, flight, swimming and walking-only controls. Investigate any new failures or conspicuous detours.
5. Run the addon regression suite, verify the package and document the results and remaining limitations.

The timing baseline is in `output/route-matrix-2026-11-25`. Use a separate directory for all new measurements. Live frame rates and native transport handoffs require in-game confirmation.

## Outcome

The benchmark matched all 262 attempts and recovered 40 failures. Ratchet to Shimmering Flats now returns the Great Lift at all six road settings. The 131 addon test scripts passed. The remaining walking-only failure, estimated journey tradeoffs and live-client retest are documented in the [performance report](../../route-generation-improvements-2026-11-25.md).
