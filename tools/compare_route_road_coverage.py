"""Compare sampled road coverage of saved routes or selected matrix cases.

Inputs are JSON route objects with `points`, or `legs` containing `kind` and
`points`. Vehicle legs are excluded. Import sampled_road_coverage(lua, route)
to measure an existing production Lua route directly. Fractions are estimates,
not terrain proofs. Optional --cases plans only the requested cold cases;
it does not run the timing matrix or record flights.

Example:
  python tools/compare_route_road_coverage.py before.json after.json \
    --before-modules output/route-improvements-2026-11-25/baseline-modules
  python tools/compare_route_road_coverage.py --cases R02,R42 --profile off \
    --before-modules output/route-improvements-2026-11-25/baseline-modules
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('Data/Terrain.lua', 'Data/GroundCorrections.lua', 'Data/Roads.lua',
           'Data/RoadsSupplement.lua', 'Roads.lua', 'Terrain.lua')
OPTIONAL_MODULES = {'Data/WalkingPortals.lua', 'TerrainPortals.lua'}


def field(value, name, default=None):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(name, default)
    result = value[name]
    return default if result is None else result


def array(value):
    if value is None:
        return []
    if isinstance(value, (tuple, list)):
        return value
    return [value[i] for i in range(1, len(value) + 1)]


def walking_lines(route):
    """Use explicit legs first so a route's overview cannot count boats twice."""
    legs = field(route, 'legs')
    if legs is not None:
        for leg in array(legs):
            yield field(leg, 'kind') == 'walk', array(field(leg, 'points'))
    else:
        yield True, array(field(route, 'points'))


def sampled_road_coverage(lua, route, sample_yards=2):
    """Distance-weight midpoint samples on same-map walking segments.

    roadFraction uses all measured walking yards as its denominator; missing
    or mismatched road grids contribute unknownRoadYards and cannot inflate
    that fraction. knownRoadFraction excludes unknown data. An explicitly
    empty, aligned road grid is known off-road ground.
    """
    if not isinstance(sample_yards, (int, float)) or not math.isfinite(sample_yards) or sample_yards <= 0:
        raise ValueError('sample_yards must be a finite positive number')
    addon = lua.globals().A
    totals = dict(walkingYards=0., roadYards=0., knownRoadYards=0.,
                  unknownRoadYards=0., samples=0, skippedNonWalkingLegs=0,
                  skippedMapChanges=0, missingTerrainSegments=0)
    grids = {}

    def grid(map_id):
        if map_id not in grids:
            zone = addon.Terrain.Zone(map_id)
            if isinstance(zone, tuple):
                zone = zone[0]
            roads = addon.Roads.Zone(map_id, zone) if zone is not None else None
            data = field(addon, 'RoadData')
            source = field(data, 'zones')
            source = source[map_id] if source is not None else None
            empty = (field(data, 'version') == 1 and zone is not None and source is not None and
                     all(field(source, k) == field(zone, k)
                         for k in ('w', 'h', 'widthYards', 'heightYards')) and
                     field(source, 'roadCells') == 0 and field(source, 'rows') is not None)
            grids[map_id] = zone, roads, roads is not None or empty
        return grids[map_id]

    for walking, points in walking_lines(route):
        if not walking:
            totals['skippedNonWalkingLegs'] += 1
            continue
        for first, last in zip(points, points[1:]):
            map_id = field(first, 'mapID')
            if map_id != field(last, 'mapID'):
                totals['skippedMapChanges'] += 1
                continue
            zone, roads, known = grid(map_id)
            if zone is None:
                totals['missingTerrainSegments'] += 1
                continue
            ax, ay = field(first, 'x'), field(first, 'y')
            bx, by = field(last, 'x'), field(last, 'y')
            if not all(isinstance(n, (float, int)) and math.isfinite(n) and 0 <= n <= 1
                       for n in (ax, ay, bx, by)):
                raise ValueError('Route points must have finite normalized x and y coordinates')
            distance = math.hypot((bx - ax) * zone.widthYards,
                                  (by - ay) * zone.heightYards)
            if not distance:
                continue
            totals['walkingYards'] += distance
            if not known:
                totals['unknownRoadYards'] += distance
                continue
            totals['knownRoadYards'] += distance
            count = math.ceil(distance / sample_yards)
            weight = distance / count
            totals['samples'] += count
            if roads is None:  # Aligned source with zero road cells.
                continue
            for i in range(count):
                fraction = (i + .5) / count
                x = min(int(zone.w) - 1, math.floor((ax + (bx - ax) * fraction) * zone.w))
                y = min(int(zone.h) - 1, math.floor((ay + (by - ay) * fraction) * zone.h))
                if addon.Roads.Cell(roads, x, y):
                    totals['roadYards'] += weight
    # Repeated fractional segment samples can accumulate a few ulps above
    # the measured length on an entirely on-road route.
    totals['roadYards'] = min(totals['knownRoadYards'], max(0., totals['roadYards']))
    totals['offRoadYards'] = totals['knownRoadYards'] - totals['roadYards']
    totals['roadFraction'] = (totals['roadYards'] / totals['walkingYards']
                              if totals['walkingYards'] else None)
    totals['knownRoadFraction'] = (totals['roadYards'] / totals['knownRoadYards']
                                   if totals['knownRoadYards'] else None)
    return totals


def load_runtime(module_root):
    sys.path.insert(0, str(ROOT / '.test-deps'))
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('A={}')
    fingerprints = {}
    for name in MODULES:
        path = module_root / name
        blob = path.read_bytes()
        fingerprints[name] = hashlib.sha256(blob).hexdigest()
        lua.execute('assert(loadstring(...))("Mapperly",A)', blob.decode('utf-8-sig'))
    return lua, fingerprints


def plan_case(module_root, case, profile, timeout, sample_yards):
    """Plan one selected case in fresh Lua state; no latency claim is emitted."""
    from benchmark_route_matrix import FILES
    sys.path.insert(0, str(ROOT / '.test-deps'))
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow.lua').read_text())
    lua.execute('fakeUI();A={}')
    fingerprints = {}
    for name in FILES:
        path = module_root / name
        if name in OPTIONAL_MODULES and not path.exists():
            continue
        blob = path.read_bytes()
        fingerprints[name] = hashlib.sha256(blob).hexdigest()
        lua.execute('assert(loadstring(...))("Mapperly",A)', blob.decode('utf-8-sig'))
    values = lua.globals()
    values.coverageClock = lambda: time.perf_counter() * 1000
    values.coverageFaction = case['faction']
    values.coverageRoads = profile != 'off'
    values.coverageStrength = {'off': 3, 'light': 1, 'moderate': 2,
                               'normal': 3, 'firm': 4, 'strong': 5}[profile]
    values.coverageStart = lua.table_from(case['start']['point'])
    values.coverageGoal = lua.table_from(case['goal']['point'])
    lua.execute('''
        debugprofilestop=coverageClock
        GetTimePreciseSec=function() return coverageClock()/1000 end
        UnitClass=function() return 'Warrior','WARRIOR',1 end
        UnitFactionGroup=function() return coverageFaction end
        UnitGUID=function() return 'Player-1-RoadCoverage' end
        UnitOnTaxi=function() return false end
        UnitInVehicle=function() return false end
        GetMoney=function() return 100000000 end
        A.InitStore({preferRoads=coverageRoads,roadPreferenceStrength=coverageStrength})
        A.PlanningJob.Start(function()
            return A.Journey.Plan(coverageStart,coverageGoal,
                                  {faction=coverageFaction,liveStart=true})
        end,function(route) coverageRoute=route end,
            function(reason) coverageReason=reason end)
    ''')
    began = time.perf_counter()
    addon = values.A
    while addon.PlanningJob.IsRunning():
        addon.PlanningJob.Step()
        if time.perf_counter() - began > timeout:
            addon.PlanningJob.Cancel()
            return dict(status='timeout', reason='Selected case exceeded its planning timeout',
                        sourceHashes=fingerprints, modules=str(module_root))
    result = dict(status='ok' if values.coverageRoute is not None else 'failed',
                  sourceHashes=fingerprints, modules=str(module_root))
    if values.coverageRoute is None:
        result['reason'] = values.coverageReason
    else:
        result.update(sampled_road_coverage(lua, values.coverageRoute, sample_yards))
    return result


def comparison(before, after):
    return {name: after[name] - before[name]
            if before.get(name) is not None and after.get(name) is not None else None
            for name in ('walkingYards', 'roadYards', 'roadFraction', 'unknownRoadYards')}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('before', type=Path, nargs='?')
    parser.add_argument('after', type=Path, nargs='?')
    parser.add_argument('--before-modules', type=Path, default=ROOT)
    parser.add_argument('--after-modules', type=Path, default=ROOT)
    parser.add_argument('--sample-yards', type=float, default=2)
    parser.add_argument('--cases', help='Optional comma-separated matrix case IDs; plans each once per module root')
    parser.add_argument('--matrix', type=Path, default=ROOT / 'output/route-matrix-2026-11-25/matrix.json')
    parser.add_argument('--profile', choices=('off', 'light', 'moderate', 'normal', 'firm', 'strong'), default='firm')
    parser.add_argument('--timeout', type=float, default=90, help='Planning seconds per selected case and root')
    parser.add_argument('--output', type=Path, help='Optional JSON report; default is stdout only')
    args = parser.parse_args()
    if not math.isfinite(args.sample_yards) or args.sample_yards <= 0:
        parser.error('--sample-yards must be finite and positive')
    if args.cases and (args.before or args.after):
        parser.error('Choose saved route files or --cases')
    if not args.cases and (args.before is None or args.after is None):
        parser.error('Pass both saved route files or --cases')
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    result = dict(method='Distance-weighted midpoint road samples; vehicle legs excluded',
                  sampleYards=args.sample_yards)
    if args.cases:
        requested = args.cases.split(',')
        cases = {case['id']: case for case in json.loads(args.matrix.read_text(encoding='utf-8-sig'))['cases']}
        missing = [case for case in requested if case not in cases]
        if missing:
            parser.error('Unknown matrix cases: ' + ','.join(missing))
        result.update(profile=args.profile, recordedFlights=False, cases=[])
        for case_id in requested:
            row = dict(case=case_id)
            for label in ('before', 'after'):
                row[label] = plan_case(getattr(args, label + '_modules').resolve(),
                                       cases[case_id], args.profile, args.timeout, args.sample_yards)
            row['change'] = comparison(row['before'], row['after'])
            result['cases'].append(row)
    else:
        for label in ('before', 'after'):
            module_root = getattr(args, label + '_modules').resolve()
            lua, fingerprints = load_runtime(module_root)
            route = json.loads(getattr(args, label).read_text(encoding='utf-8-sig'))
            result[label] = dict(modules=str(module_root), sourceHashes=fingerprints,
                                 **sampled_road_coverage(lua, route, args.sample_yards))
        result['change'] = comparison(result['before'], result['after'])
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf8')
    print(text, end='')


if __name__ == '__main__':
    main()
