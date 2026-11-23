"""Reproduce conservative standalone quest locations from the pinned Forever SQL.

No SQL server, Questie, client changes, or runtime download is involved.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import build_services as services

ROOT = Path(__file__).resolve().parents[1]
SQL_SHA256 = '3357f62451dcdef27123243c83c76a1a2e3251cf730aea01abf2f7f3d776d341'
MAX_PER_OBJECTIVE = 8
MAX_TURNINS = 8
MAX_PER_QUEST = 64
TABLES = {'quest_template', 'quest_objectives', 'quest_poi', 'quest_poi_points',
          'creature_questender', 'gameobject_questender', 'creature', 'gameobject',
          'creature_template', 'gameobject_template', 'game_event_creature',
          'game_event_gameobject', 'pool_members', 'gameobject_template_addon'}


def integer(row, key, default=0):
    return int(row.get(key) or default)


def coordinates(row, north='position_x', east='position_y'):
    """HBD uses east/north; SQL position_x/X is north, position_y/Y east."""
    x, y = float(row[east]), float(row[north])
    if not all(math.isfinite(v) and abs(v) < 17067 for v in (x, y)):
        return None
    if x == 0 and y == 0:
        return None
    return round(x, 3), round(y, 3)


def bounded(records, limit, stats):
    """Keep actual positions, evenly sampled in stable coordinate order."""
    unique = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in records}
    values = sorted(unique.values(), key=lambda r: (r['instance'], r['worldX'], r['worldY'], r['label']))
    if len(values) > limit:
        stats['truncatedRecords'] += len(values) - limit
        stats['truncatedGroups'] += 1
        return [values[i * (len(values) - 1) // (limit - 1)] for i in range(limit)]
    return values


def faction_access(faction, factions):
    """Same Forever FactionTemplate group rules as the bundled services builder."""
    f = factions.get(faction)
    if not f:
        return 'AH' if faction == 0 else None
    group, friends, enemies = (int(f[k]) for k in ('FactionGroup', 'FriendGroup', 'EnemyGroup'))
    if (group | friends) & 2 and not (group | friends) & 4 and enemies & 4:
        return 'A'
    if (group | friends) & 4 and not (group | friends) & 2 and enemies & 2:
        return 'H'
    if enemies & 6 == 0:
        return 'AH'
    if enemies & 2 and not enemies & 4:
        return 'H'
    if enemies & 4 and not enemies & 2:
        return 'A'
    return None


def extract(input_rows, factions=None):
    factions = factions or {}
    data = defaultdict(list)
    stats = Counter()
    for table, row in input_rows:
        data[table].append(row)
        stats['input:' + table] += 1
    quests = {integer(r, 'ID') for r in data['quest_template']}
    objectives = {integer(r, 'ID'): r for r in data['quest_objectives'] if integer(r, 'QuestID') in quests}
    names, template_factions = {}, {}
    for kind in ('creature', 'gameobject'):
        for r in data[kind + '_template']:
            names[kind, integer(r, 'entry')] = r.get('name') or kind
            template_factions[kind, integer(r, 'entry')] = integer(r, 'faction')
    for r in data['gameobject_template_addon']:
        template_factions['gameobject', integer(r, 'entry')] = integer(r, 'faction')
    excluded = set()
    for kind in ('creature', 'gameobject'):
        excluded.update((kind, integer(r, 'guid')) for r in data['game_event_' + kind])
    for r in data['pool_members']:
        if integer(r, 'type') in (0, 1):
            excluded.add(('creature' if integer(r, 'type') == 0 else 'gameobject', integer(r, 'spawnId')))
    spawns = defaultdict(list)
    for kind in ('creature', 'gameobject'):
        for r in data[kind]:
            if integer(r, 'map') not in services.MAPS:
                stats['excludedNonWorldSpawns'] += 1
                continue
            if (any(integer(r, k) for k in ('PhaseId', 'PhaseGroup', 'phaseUseFlags'))
                    or integer(r, 'terrainSwapMap', -1) != -1
                    or (kind, integer(r, 'guid')) in excluded
                    or (r.get('spawnDifficulties') or '0') != '0'):
                stats['excludedConditionalSpawns'] += 1
                continue
            point = coordinates(r)
            if point:
                spawns[kind, integer(r, 'id')].append((integer(r, 'map'), point))
    groups = defaultdict(list)

    def record(qid, kind, label, instance, point, provenance, objective=None, faction=None):
        r = dict(kind=kind, label=label, worldX=point[0], worldY=point[1],
                 instance=instance, source='snapshot', provenance=provenance)
        if objective:
            r['objectiveID'] = integer(objective, 'ID')
        if faction:
            r['faction'] = faction
        groups[qid, kind, integer(objective or {}, 'ID')].append(r)

    points = defaultdict(list)
    poi_keys = Counter((integer(r, 'QuestID'), integer(r, 'Idx1')) for r in data['quest_poi'])
    for r in data['quest_poi_points']:
        points[integer(r, 'QuestID'), integer(r, 'Idx1')].append(r)
    covered = set()
    for r in data['quest_poi']:
        qid, oid = integer(r, 'QuestID'), integer(r, 'QuestObjectiveID')
        key = qid, integer(r, 'Idx1')
        obj = objectives.get(oid)
        if (not obj or integer(obj, 'QuestID') != qid or not integer(obj, 'Visible')
                or integer(r, 'MapID') not in services.MAPS
                or integer(r, 'ObjectiveIndex') < 0
                or any(integer(r, k) for k in ('PlayerConditionID', 'NavigationPlayerConditionID', 'SpawnTrackingID'))
                or poi_keys[key] != 1):
            stats['excludedAmbiguousPOI'] += 1
            continue
        if len(points[key]) != 1:
            stats['excludedAreaOrMissingPOI'] += 1
            continue
        point = coordinates(points[key][0], 'X', 'Y')
        if point:
            label = obj.get('Description') or 'Objective location'
            record(qid, 'objective', label, integer(r, 'MapID'), point, 'quest_poi/quest_poi_points', obj)
            covered.add(oid)
    for oid, obj in sorted(objectives.items()):
        if oid in covered or not integer(obj, 'Visible'):
            continue
        kind = {0: 'creature', 2: 'gameobject', 3: 'creature'}.get(integer(obj, 'Type'))
        if not kind:
            continue  # In particular, never infer item drop locations.
        entry = integer(obj, 'ObjectID')
        label = obj.get('Description') or names.get((kind, entry), 'Objective location')
        for instance, point in spawns[kind, entry]:
            record(integer(obj, 'QuestID'), 'objective', label, instance, point, 'quest_objectives/' + kind, obj)
    for kind in ('creature', 'gameobject'):
        for r in data[kind + '_questender']:
            qid, entry = integer(r, 'quest'), integer(r, 'id')
            if qid not in quests:
                continue
            faction = faction_access(template_factions.get((kind, entry), -1), factions)
            if not faction:
                stats['excludedUnknownOrHostileTurninRelations'] += 1
                continue
            for instance, point in spawns[kind, entry]:
                record(qid, 'turnin', names.get((kind, entry), 'Quest turn-in'), instance, point, kind + '_questender/' + kind, faction=faction)
    result = defaultdict(list)
    for (qid, kind, oid), records in sorted(groups.items()):
        result[qid].extend(bounded(records, MAX_PER_OBJECTIVE if kind == 'objective' else MAX_TURNINS, stats))
    for qid, records in result.items():
        # Preserve turn-ins and objective coverage when a quest has many objectives.
        turnins = [r for r in records if r['kind'] == 'turnin']
        objective_groups = defaultdict(list)
        for r in records:
            if r['kind'] == 'objective':
                objective_groups[r['objectiveID']].append(r)
        ordered = [r for depth in range(MAX_PER_OBJECTIVE) for oid in sorted(objective_groups)
                   for r in objective_groups[oid][depth:depth + 1]]
        combined = turnins + ordered
        if len(combined) > MAX_PER_QUEST:
            stats['truncatedRecords'] += len(combined) - MAX_PER_QUEST
            stats['truncatedQuests'] += 1
        result[qid] = combined[:MAX_PER_QUEST]
    stats['quests'] = len(result)
    for records in result.values():
        for r in records:
            stats[r['kind'] + 'Records'] += 1
            stats['provenance:' + r['provenance']] += 1
    return dict(sorted(result.items())), dict(sorted(stats.items()))


def render(quests):
    output = ['-- Generated by tools/build_quest_locations.py; do not hand-edit.',
              '-- Forever TDB 2026-10-14; GPL-2.0. See QuestLocations-SOURCES.md.',
              'local _,A=...', 'A.QuestLocationData={version=1,source="Forever TDB 2026-10-14",quests={']
    for qid, records in sorted(quests.items()):
        output.append(' [' + str(qid) + ']={')
        for r in records:
            output.append('  {' + ','.join(k + '=' + json.dumps(v, ensure_ascii=False) for k, v in r.items()) + '},')
        output.append(' },')
    output.append('}}')
    return '\n'.join(output) + '\n'


def verify(path, expected):
    with path.open('rb') as f:
        actual = hashlib.file_digest(f, 'sha256').hexdigest()
    if actual != expected:
        raise ValueError(f'Source integrity failed: {path.name}: {actual}')


def build():
    # Deliberately require the existing audited source cache, avoiding implicit downloads.
    archive = services.CACHE / services.ARCHIVE
    verify(archive, services.SHA256)
    sql = services.CACHE / services.WORLD
    if not sql.exists():
        subprocess.run(['tar', '-xf', str(archive), '-C', str(services.CACHE), services.WORLD], check=True)
    verify(sql, SQL_SHA256)
    faction_csv = ROOT / 'tools/data/factiontemplate-70959.csv'
    verify(faction_csv, '963a24a4a32acd76dea04ac337e037f45d72e2c6a403e3826dfcfc95e28b746d')
    with faction_csv.open(encoding='utf-8-sig', newline='') as f:
        factions = {int(r['ID']): r for r in csv.DictReader(f)}
    quests, stats = extract(services.rows(sql, TABLES), factions)
    (ROOT / 'Data/QuestLocations.lua').write_text(render(quests), encoding='utf-8', newline='\n')
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    build()
