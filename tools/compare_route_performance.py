"""Replay the frozen survey in a separate output directory and pair its results."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

import benchmark_route_matrix as bench

OUT = bench.ROOT / 'output' / 'route-improvements-2026-11-25'
BASE = bench.OUT / 'benchmark-results.json'


def key(row):
    return row['batch'], row['case'], row['profile'], row['temperature']


def source_hashes():
    return {name: hashlib.sha256((bench.ROOT / name).read_bytes()).hexdigest() for name in bench.FILES}


def replay(args, baseline):
    output = OUT / args.label
    output.mkdir(parents=True, exist_ok=True)
    results = output / 'after.jsonl'
    hashes = source_hashes()
    fingerprint = output / 'sources.json'
    if fingerprint.exists() and json.loads(fingerprint.read_text()) != hashes:
        raise SystemExit('Sources have changed. Choose a new --label for these measurements.')
    fingerprint.write_text(json.dumps(hashes, indent=2))
    seen = {key(json.loads(line)) for line in results.read_text().splitlines()} if results.exists() else set()
    with results.open('a', encoding='utf8') as dest:
        for b in baseline:
            if b['temperature'] != 'cold' or key(b) in seen:
                continue
            if args.cases and b['case'] not in args.cases.split(','):
                continue
            if args.batches and b['batch'] not in args.batches.split(','):
                continue
            cmd = [sys.executable, str(bench.ROOT / 'tools/benchmark_route_matrix.py'),
                   '--worker', b['case'], '--profile', b['profile']]
            for flag, field in [('--walking', 'walkingOnly'), ('--flights', 'flights'), ('--avoid', 'avoidSwimming')]:
                if b.get(field, False):
                    cmd.append(flag)
            if b['batch'] in ('trace-firm', 'user-route', 'user-route-light-moderate'):
                cmd.append('--trace')
            result = subprocess.run(cmd, cwd=bench.ROOT, capture_output=True, text=True, timeout=115, check=True)
            rows = json.loads(result.stdout)
            for row in rows:
                row['batch'] = b['batch']
                dest.write(json.dumps(row) + '\n')
            dest.flush()
            print(b['batch'], b['case'], b['profile'],
                  [(r['status'], r['hostSeconds'], r['progress'].get('cells', 0)) for r in rows], flush=True)
    if source_hashes() != hashes:
        raise SystemExit('Planner sources changed during measurement. Repeat with a new --label.')


def report(args, baseline):
    output = OUT / args.label
    after = [json.loads(s) for s in (output / 'after.jsonl').read_text().splitlines()]
    before = {key(row): row for row in baseline}
    matrix = json.loads(BASE.read_text())['matrix']
    definitions = {case['id']: case for case in matrix['cases']}
    zone_names = {anchor['point']['mapID']: anchor['zone']
                  for anchor in matrix['anchors'].values()}
    strengths = {'off': None, 'light': 1, 'moderate': 2, 'normal': 3, 'firm': 4, 'strong': 5}

    def sequence(values, names=False):
        if values is None:
            return ''
        return ' > '.join((zone_names.get(zone, str(zone)) + ' (' + str(zone) + ')')
                          if names else str(zone) for zone in values)

    def options(value, definition):
        profile = value['profile']
        return '; '.join([
            'faction=' + definition['faction'],
            'roads=' + profile,
            'swimming=' + ('dry first, then permitted' if value.get('avoidSwimming', False)
                           else 'permitted'),
            'recorded flights=' + ('yes' if value.get('flights', False) else 'no'),
            'walking only=' + ('yes' if value.get('walkingOnly', False) else 'no'),
        ])

    rows = []
    for a in after:
        b = before[key(a)]
        definition = definitions[a['case']]
        case = dict(zip(('batch', 'case', 'profile', 'temperature'), key(a)))
        case.update(start=definition['start']['name'], destination=definition['goal']['name'],
                    category=definition['category'], faction=definition['faction'],
                    minimumWalkingZoneCount=definition.get('minimumWalkingZoneCount'),
                    minimumWalkingChain=sequence(definition.get('minimumWalkingChain')))
        for label, anchor in [('start', definition['start']), ('destination', definition['goal'])]:
            point = anchor['point']
            case.update({label + 'MapID': point['mapID'], label + 'Zone': anchor['zone'],
                         label + 'X': point['x'], label + 'Y': point['y']})
        for tag, value in [('before', b), ('after', a)]:
            case.update({tag + field: value.get(field) for field in
                         ['status', 'hostSeconds', 'modeled60fpsSeconds', 'distanceYards', 'journeySeconds', 'slices', 'reason']})
            progress = value.get('progress', {})
            case[tag+'cells'] = progress.get('cells', 0)
            case[tag+'vehicles'] = ', '.join(v['kind'] for v in value.get('vehicles', []))
            case[tag+'options'] = options(value, definition)
            case[tag+'preferRoads'] = value['profile'] != 'off'
            case[tag+'roadPreferenceStrength'] = strengths[value['profile']]
            for field in ('flights', 'avoidSwimming', 'walkingOnly'):
                case[tag+field] = value.get(field, False)
            case.update({tag+field: value.get(field) for field in
                         ['maxStepMS', 'coverage', 'swimmingFallback', 'swimmingFallbackReason',
                          'drySearchBudget']})
            case[tag+'actualZones'] = sequence(value.get('actualZones'))
            case[tag+'itineraryZones'] = sequence(value.get('actualZones'), names=True)
            case[tag+'vehicleDetails'] = ' > '.join(
                v['kind'] + ': ' + v.get('name', '') + ' [' + str(v.get('id', '')) + ']'
                for v in value.get('vehicles', []))
            for field in ('invalidWalkingLegs', 'approximateGuidanceZones', 'pathReuseDelta', 'flightStats'):
                case[tag+field] = json.dumps(value.get(field), separators=(',', ':'))
            case[tag+'paths'] = progress.get('paths')
            case[tag+'progressStage'] = progress.get('stage')
            case[tag+'flightNote'] = progress.get('flightNote')
        flags = []
        if a['status'] != b['status']:
            flags.append('status changed: ' + b['status'] + ' -> ' + a['status'])
        if a.get('invalidWalkingLegs'):
            flags.append('invalid walking legs')
        if a.get('approximateGuidanceZones'):
            flags.append('approximate guidance')
        if a.get('swimmingFallback'):
            flags.append('swimming fallback: ' + (a.get('swimmingFallbackReason') or 'reason not recorded'))
        if a.get('actualZones') != b.get('actualZones'):
            flags.append('itinerary zones changed')
        if a.get('vehicles') != b.get('vehicles'):
            flags.append('transport itinerary changed')
        if any(a.get(field, False) != b.get(field, False)
               for field in ('flights', 'avoidSwimming', 'walkingOnly')):
            flags.append('requested options differ')
        old_distance, new_distance = b.get('distanceYards'), a.get('distanceYards')
        case['distanceChangePercent'] = ((new_distance / old_distance - 1) * 100
                                         if old_distance and new_distance is not None else None)
        case['flags'] = '; '.join(flags)
        rows.append(case)
    if not rows:
        print('No measurements to report.')
        return
    with (output / 'comparison.csv').open('w', newline='', encoding='utf8') as dest:
        writer = csv.DictWriter(dest, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    for temp in ('cold', 'warm'):
        selected = [r for r in rows if r['temperature']==temp]
        if not selected:
            continue
        for tag in ('before', 'after'):
            times = sorted(r[tag+'hostSeconds'] for r in selected
                           if isinstance(r[tag+'hostSeconds'], (int, float)))
            if not times:
                print(temp, tag, Counter(r[tag+'status'] for r in selected), 'no completed timing samples')
                continue
            print(temp, tag, Counter(r[tag+'status'] for r in selected), 'median/p95/max seconds',
                  statistics.median(times), times[(95*len(times)+99)//100-1], times[-1],
                  'total cells', sum(r[tag+'cells'] for r in selected))
    print('Rows', len(rows), 'distinct routes', len({r['case'] for r in rows}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--cases')
    parser.add_argument('--batches')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    baseline = json.loads(BASE.read_text())['measurements']
    if not args.report_only:
        replay(args, baseline)
    report(args, baseline)
