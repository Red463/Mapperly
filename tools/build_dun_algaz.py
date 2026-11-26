"""Extract the four Dun Algaz passages from build 70959's placed collision and terrain."""
import json
import math
from pathlib import Path

from bridge_geometry import Reader, placed, unplaced
from build_structure_corridors import validate

ROOT = Path(__file__).resolve().parents[1]
TUNNELS = (73025, 126354, 68441769, 68443158)
# The same medium-tunnel model and centre lane as the existing North Gate Pass proof.
LANE_X = .08
DOORS = (1.7, 192.0)
AREA_MAP = {836: 1437, 837: 1432}  # ADT areas named Dun Algaz, owned by Wetlands / Loch Modan


def check_riser(asset, local_y, low, high):
    """The exposed part of the first/last stair must have a collidable vertical face."""
    if low >= high:
        return
    intervals = []
    for face in asset['faces']:
        section = []
        vertices = face['v']
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            if min(a[0], b[0]) <= LANE_X <= max(a[0], b[0]) and a[0] != b[0]:
                t = (LANE_X - a[0]) / (b[0] - a[0])
                section.append([a[i] + t * (b[i] - a[i]) for i in (1, 2)])
        if len(section) == 2 and all(abs(y-local_y) < .025 for y, z in section):
            intervals.append(sorted(z for y, z in section))
    covered = low
    for a, b in sorted(intervals):
        if a <= covered + .005:
            covered = max(covered, b)
    if covered < high - .005:
        raise ValueError('The exposed landing step is missing collision')


def extract(reader, sampler, placement):
    if placement['fdid'] != 110707 or placement['rot'][0] or placement['rot'][2]:
        raise ValueError('Unexpected Dun Algaz tunnel model or rotation')
    reader.used.clear()
    mesh, asset, _ = reader.mesh(placement, sampler)

    def floor(y):
        n, e, _ = placed([LANE_X, y, 0], placement)
        hit = mesh.floor(n, e)
        return ([n, e, hit[0]], hit[2]) if hit else (None, None)

    mouths, landings = [], []
    for outside, inside in zip(DOORS, (2.25, 191.5)):
        lo, hi = outside, inside
        if floor(lo)[0] or not floor(hi)[0]:
            raise ValueError('Unexpected collision at the tunnel entrance')
        for _ in range(24):
            mid = (lo + hi) / 2
            if floor(mid)[0]:
                hi = mid
            else:
                lo = mid
        mouths.append(hi)
        lip, _ = floor(hi)
        terrain = reader.terrain(sampler, *lip[:2])
        rise = lip[2] - terrain['height']
        if not 0 <= rise <= .55:
            raise ValueError('Outdoor terrain exceeds the gate landing step limit')
        low = unplaced([*lip[:2], terrain['height']], placement)[2]
        check_riser(asset, hi, low, unplaced(lip, placement)[2])
        # Check the entire short section outside the WMO, including the lip.
        heights = []
        for j in range(17):
            y = outside + (hi-outside)*j/16
            n, e, _ = placed([LANE_X, y, 0], placement)
            ground = reader.terrain(sampler, n, e)
            if not ground['permitted'] or ground['area'] not in AREA_MAP:
                raise ValueError('No owned dry walking approach to the tunnel entrance')
            heights.append(ground['height'])
            if j == 0:
                landings.append(dict(world=[n, e, ground['height']], terrain=ground, exposedRiser=rise))
        if max(abs(a-b) for a,b in zip(heights, heights[1:])) > .3:
            raise ValueError('Unsupported ground approach')

    count = math.ceil((mouths[1] - mouths[0]) / .1)
    interior = []
    clearance = math.inf
    gap = 0
    for i in range(count+1):
        y = mouths[0] + (mouths[1]-mouths[0])*i/count
        if i == count:
            y = mouths[1]
        point, headroom = floor(y)
        if not point or headroom < 2.2:
            raise ValueError('Unsupported tunnel floor or insufficient headroom')
        if interior:
            gap = max(gap, mesh.gap(interior[-1], point))
        interior.append(point)
        clearance = min(clearance, headroom)
    if gap > .02:
        raise ValueError('Gap in the tunnel floor')
    changes = [b[2]-a[2] for a,b in zip(interior,interior[1:])]
    first, last = landings
    row = dict(wmoRootFDID=placement['fdid'], placementUID=placement['uid'],
               fromUiMap=AREA_MAP[first['terrain']['area']], toUiMap=AREA_MAP[last['terrain']['area']],
               nativeFloorSupported=True, unsupportedInteriorSamples=[], minimumCenterlineHeadroom=clearance,
               maxAdjacentFloorRise=max(changes), maxAdjacentFloorDrop=min(changes), maximumFloorGap=gap,
               terrainLandings=landings, worldCenterline=[first['world'], *interior, last['world']],
               build=70959, sourceHashes=dict(reader.used))
    validate(row)
    return row


def main():
    out = ROOT.parent/'output'
    placements = json.loads((out/'bridges-and-crossings-70959/map-0.json').read_text())['placements']
    selected = {p['uid']:p for p in placements if p['kind']=='wmo' and p['uid'] in TUNNELS}
    reader = Reader(out/'forever-datamine-70959')
    sampler = reader.sampler(0, 775971)
    rows = [extract(reader, sampler, selected[uid]) for uid in TUNNELS]
    for row in rows:
        row['sourceHashes'][775971] = reader.hashes[775971]
        print(row['placementUID'], row['fromUiMap'], row['toUiMap'], len(row['worldCenterline']),
              'floor gap', row['maximumFloorGap'], 'headroom', row['minimumCenterlineHeadroom'])
    (ROOT/'tools/data/native-dun-algaz-70959.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')


if __name__ == '__main__':
    main()
