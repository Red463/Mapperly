"""Replay intra-city journeys and inspect the native bridge and passage inventory."""
import argparse
import itertools
import json
import re
import struct
from functools import lru_cache
from pathlib import Path

from benchmark_route_matrix import ROOT, runtime
from compare_route_road_coverage import sampled_road_coverage

# Rounded in-city service positions, plus an Ironforge player report and destination.
POINTS = {
    1453: [(60.4, 75.3), (74.5, 55.4), (49.5, 44.6)],
    1454: [(54.1, 68.4), (62.3, 40.5), (79.6, 23.3)],
    1455: [(33.2, 65.3), (55.5, 47.8), (18.2, 51.4)],
    1456: [(45.8, 64.7), (29.7, 21.2), (46.6, 33.2)],
    1457: [(67.4, 15.6), (41.6, 41.8), (39.5, 81.2)],
    1458: [(67.7, 37.9), (71.4, 61.6), (56.0, 37.5)],
}


def replay():
    records = []
    for profile in ('off', 'strong'):
        lua = runtime(profile=profile)
        lua.execute("""
            for _, k in ipairs({'useTrams','useLifts','useFlights','useBoats','useAirships','useZeppelins'}) do
                A.db[k]=false
            end
        """)
        plan = lua.eval("""function(m,x,y,u,v)
            return A.Journey.Plan({mapID=m,x=x/100,y=y/100},{mapID=m,x=u/100,y=v/100},{liveStart=true})
        end""")
        for mid, points in POINTS.items():
            for start, end in itertools.permutations(points, 2):
                result = plan(mid, *start, *end)
                route, error = result if isinstance(result, tuple) else (result, None)
                record = dict(map=mid, profile=profile, start=start, end=end)
                if route is None:
                    record['error'] = error
                else:
                    metrics = sampled_road_coverage(lua, route)
                    record.update(points=len(route.points), coverage=route.coverage,
                                  roadFraction=metrics['roadFraction'], yards=metrics['walkingYards'])
                records.append(record)
    return records


def inspect_groups(casc, file_id):
    from bridge_geometry import chunks, collision_triangles, group_header
    raw = casc.read_fdid(file_id)
    root = {t: raw[a:b] for t, a, b in chunks(raw)}
    count = struct.unpack_from('<I', root['MOHD'], 4)[0]
    names = root.get('MOGN', b'')
    result = []
    for group_id in struct.unpack_from(f'<{count}I', root['GFID']):
        record = dict(file=group_id)
        try:
            blob = casc.read_fdid(group_id)
            start, end, name, area = group_header(blob, names)
            record.update(name=name, area=area)
            gc = {t: blob[s:e] for t, s, e in chunks(blob, start, end)}
            record['encoding'] = next((tag for tag in ('MPY2','MOPY') if tag in gc), None)
            record['collisionTriangles'] = sum(1 for _ in collision_triangles(gc))
        except (ValueError, KeyError, FileNotFoundError, StopIteration, struct.error) as error:
            record['error'] = f'{type(error).__name__}: {error}'
        result.append(record)
    return result


def native_inventory():
    from bridge_geometry import ORIGIN, LocalCasc, placed
    audit = ROOT.parent / 'output/bridges-and-crossings-70959'
    assets = json.loads((audit / 'assets.json').read_text())
    paths = json.loads((audit / 'asset-paths.json').read_text())
    zones = json.loads((ROOT / 'tools/roads/zones.json').read_text())['zones']
    casc = LocalCasc(ROOT.parent / 'output/forever-datamine-70959')
    groups = lru_cache(maxsize=None)(lambda fid: inspect_groups(casc, fid))
    # For standalone models, test their transformed collision bounding boxes.
    # World-model placement bounds already include the full building.
    terms = re.compile(r'bridge|viaduct|causeway|tunnel|sewer|passage', re.I)
    rows = {}
    for instance in (0, 1, 2940, 2959):
        file = audit / f'map-{instance}.json'
        if not file.exists():
            rows[str(instance)] = {'error': 'No placement inventory'}
            continue
        data = json.loads(file.read_text())
        regions = [z for z in zones if z['id'] in POINTS and z['terrainMap'] == instance]
        if instance == 2959:
            regions = [dict(id='instance-2959', east=-float('inf'), west=float('inf'),
                            south=-float('inf'), north=float('inf'))]
        for z in regions:
            rows[str(z['id'])] = {'placements': [], 'mapErrors': data['errors']}
        for p in data['placements']:
            asset = assets.get(f"{p['kind']}:{p['fdid']}", {})
            name = asset.get('name', '') + ' ' + paths.get(str(p['fdid']), '')
            labels = sorted(set(terms.findall(name.lower())))
            embedded = [fid for fid in asset.get('embeddedModels', []) if terms.search(
                assets.get(f'm2:{fid}', {}).get('name', '') + ' ' + paths.get(str(fid), ''))]
            if not labels and not embedded:
                continue
            if p['kind'] == 'wmo' and 'bounds' in p:
                b = p['bounds']
                ns = [ORIGIN-b[2], ORIGIN-b[5]]
                ew = [ORIGIN-b[0], ORIGIN-b[3]]
            elif asset.get('bounds'):
                b = asset['bounds']
                corners = [placed(v, p) for v in itertools.product(*zip(b[:3], b[3:]))]
                ns, ew, _ = zip(*corners)
            else:
                ns, ew = [ORIGIN-p['pos'][2]], [ORIGIN-p['pos'][0]]
            for z in regions:
                if min(ns)<=z['north'] and max(ns)>=z['south'] and min(ew)<=z['west'] and max(ew)>=z['east']:
                    record = dict(uid=p['uid'], asset=p['fdid'], path=paths.get(str(p['fdid']), ''),
                                  labels=labels, embeddedReferences=sorted(set(embedded)))
                    if p['kind'] == 'wmo':
                        try:
                            record['groups'] = groups(p['fdid'])
                        except (ValueError, KeyError, FileNotFoundError, struct.error) as error:
                            record['error'] = f'{type(error).__name__}: {error}'
                    rows[str(z['id'])]['placements'].append(record)
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output/city-navigation-audit.json')
    parser.add_argument('--routes-only', action='store_true', help='Replay routes using only bundled addon data')
    args = parser.parse_args()
    result = dict(routes=replay())
    if not args.routes_only:
        result['nativeBuild'] = 70959
        result['native'] = native_inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(args.output)
