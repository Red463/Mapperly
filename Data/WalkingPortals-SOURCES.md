# Walking portal topology

`WalkingPortals.lua` is generated deterministically by
`python tools/build_walking_portals.py`. It derives its permissions from the
shipped terrain, matching ground corrections, matching road supplements and
native dry masks, resolved through production `Terrain.Zone`, `Roads.Zone` and
`Water.Zone`. It never broadens those permissions. No external dataset or
additional native extraction is required.

Each supported map is split into 12 by 12 fine-cell tiles, including clipped
edge tiles. Four-neighbor connected components are numbered independently in
each tile, starting at 1. The first unlabelled permitted cell in row-major order
seeds each component. A full tile has component 1; a blocked tile has none.
Every pair of components sharing a cardinal tile boundary gets exactly one
portal. This preserves connectivity even when a tile contains narrow channels
or several disconnected permitted regions. Diagonal movement satisfying the
runtime's two-orthogonal-neighbor rule cannot join different four-neighbor
components, so cardinal portals preserve the fine grid's connectivity.

The selected contact is an actual adjacent pair of permitted fine cells. Among
contacts for the same component pair, prefer both cells on roads, then one cell
on a road, then ordinary ground. Choose the lower middle of the longest
contiguous span of contacts with the best road score; ties prefer lower offsets.
Road presence is a preference only. Dry topology intersects all permissions with
the matching native dry mask; absent or stale water data yields no dry portals.

## Runtime schema

`A.WalkingPortalData={version=1,stride=12,zones={...}}`. A zone contains:

- `w`, `h`: full fine-grid dimensions.
- `maskSha256`: original terrain mask identity.
- `signature`, `drySignature`: production `PathReuse.Signature` with
  `preferRoads=false` and explicit `allowSwimming=true` or `false`.
- `rows`, `dryRows`: variable-length packed strings, one per tile row.

Use the standard base64 alphabet
`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/` with values
0 through 63. Parse each row sequentially for `ceil(w/12)` tiles. A tile starts
with one base64 character. Its low five bits give portal count N (0 through 24);
bit 32 records whether any permitted fine cell in that tile is on a road under
the selected liquid policy. The following N records use four base64 characters
each, in big-endian order. Their integer value is:

```text
direction * 262144 + offset * 16384 + sourceComponent * 128 + targetComponent
```

Direction 0 means east and 1 means south. Offset is 0 through 11. Both component
IDs are 1 through 72. Only east and south records are stored; each is an
undirected connection. For zero-based tile coordinates `(tx,ty)`:

- East contact: `(tx*12+11,ty*12+offset)` to `(tx*12+12,ty*12+offset)`.
- South contact: `(tx*12+offset,ty*12+11)` to `(tx*12+offset,ty*12+12)`.

Coordinates above identify fine cells. Their actual point is the cell center.
Tile IDs are zero-based row-major, `ty*ceil(w/12)+tx`; a component node can use
`tileID*144+component` as its numeric key. A bounded local flood computes the
component of an arbitrary start/end cell. Isolated components without boundary
contacts have no portal records.

## Limits and checks

This data describes ordinary fine-grid ground connectivity, not a ready-made
physical route. Runtime must refine within permitted components and validate
all geometry. A matching complete source signature is necessary before treating
an exhausted abstract topology search as proof of ordinary-ground separation.
Search budgets and stale signatures are uncertainty and require fallback. Native
decks, city guidance, zone crossings and transport access remain separate planner
options even when ordinary ground is disconnected.

The builder holds only one map's fine labels at a time and ships compact strings,
not fine-cell labels or per-edge Lua tables. `compactness` verifies framing and
reports tile/portal counts, payload bytes, source bytes and deflated bytes.
`python tools/build_walking_portals.py --check` verifies the entire generated
output without writing. `--maps 1445,1413,1441 --output <path>` supports pilots.

`tests/walking_portals_builder.py` compares every abstract adjacency with an
independent component oracle on deterministic random and clipped grids, and
checks narrow channels, multi-component tiles, contact choice, road bits,
ground-correction doors, water guards, source signatures and compact rendering.
