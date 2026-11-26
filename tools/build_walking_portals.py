"""Compile exact within-tile ground components and cardinal boundary portals.

No fine-grid permissions are invented: a portal records one pair of adjacent
permitted cells for every pair of tile components sharing a boundary. Runtime
must refine the tile component itinerary using current fine-grid geometry.
"""
from pathlib import Path
import argparse
import json
import sys
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from PIL import ImageChops
from PIL import Image
from lupa.lua51 import LuaRuntime

STRIDE = 12
INPUTS = ('Data/Terrain.lua', 'Data/GroundCorrections.lua', 'Data/Roads.lua',
          'Data/RoadsSupplement.lua', 'Data/Water.lua', 'Roads.lua', 'Water.lua',
          'Terrain.lua', 'PathReuse.lua')
ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
CHARS = ALPHABET.decode('ascii')
EXPANDED = [bytes(6) for _ in range(256)]
for value, char in enumerate(ALPHABET):
    EXPANDED[char] = bytes(255 if value & (32 >> bit) else 0 for bit in range(6))


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('A={}')
    for name in INPUTS:
        lua.execute('assert(loadstring(...))("Mapperly",A)',
                    (ROOT / name).read_text(encoding='utf8'))
    return lua


def decode_rows(rows, width, height):
    """Decode production six-bit rows; absent and unknown cells stay blocked."""
    empty = bytes(width)
    decoded = []
    for y in range(height):
        if isinstance(rows, (list, tuple)):
            row = rows[y] if y < len(rows) else None
        elif isinstance(rows, dict):
            row = rows.get(y + 1)
        else:
            row = rows[y + 1] if rows is not None else None
        if not isinstance(row, str):
            decoded.append(empty)
            continue
        packed = row[:(width + 5) // 6].encode('ascii', errors='replace')
        line = b''.join(EXPANDED[char] for char in packed)[:width]
        decoded.append(line + bytes(width - len(line)))
    return Image.frombytes('L', (width, height), b''.join(decoded))


def label_tiles(permitted):
    """Local IDs start at one, in row-major component-seed order per tile."""
    width, height = permitted.size
    labels = bytearray(width * height)
    for y in range(0, height, STRIDE):
        for x in range(0, width, STRIDE):
            tw, th = min(STRIDE, width - x), min(STRIDE, height - y)
            raw = permitted.crop((x, y, x + tw, y + th)).tobytes()
            count = raw.count(255)
            if not count:
                continue
            if count == tw * th:
                row = bytes([1]) * tw
                for dy in range(th):
                    at = (y + dy) * width + x
                    labels[at:at + tw] = row
                continue
            local = bytearray(tw * th)
            component = 0
            for seed, value in enumerate(raw):
                if not value or local[seed]:
                    continue
                component += 1
                todo = [seed]
                local[seed] = component
                for at in todo:
                    lx = at % tw
                    for target in ((at - 1 if lx else -1),
                                   (at + 1 if lx + 1 < tw else -1),
                                   (at - tw if at >= tw else -1),
                                   (at + tw if at + tw < len(raw) else -1)):
                        if target >= 0 and raw[target] and not local[target]:
                            local[target] = component
                            todo.append(target)
            assert component <= 72, 'A 12x12 four-neighbor tile has at most 72 components'
            for dy in range(th):
                at = (y + dy) * width + x
                labels[at:at + tw] = local[dy * tw:(dy + 1) * tw]
    return labels


def contact_offset(candidates):
    """Prefer both-road, then either-road; middle of longest span, lower tie."""
    score = max(value for _, value in candidates)
    offsets = [offset for offset, value in candidates if value == score]
    start = previous = offsets[0]
    best_start, best_length = start, 1
    for offset in offsets[1:] + [STRIDE + 1]:
        if offset != previous + 1:
            length = previous - start + 1
            if length > best_length:
                best_start, best_length = start, length
            start = offset
        previous = offset
    return best_start + (best_length - 1) // 2


def portal_rows(permitted, roads=None):
    width, height = permitted.size
    labels = label_tiles(permitted)
    road_raw = roads.tobytes() if roads is not None else None
    permitted_roads = ImageChops.multiply(permitted, roads) if roads is not None else None
    result = []
    for y in range(0, height, STRIDE):
        row = []
        for x in range(0, width, STRIDE):
            records = []
            # Keep each component-pair adjacency once, regardless of the number
            # of disjoint spans along that shared face.
            for direction in (0, 1):
                if direction == 0 and x + STRIDE >= width or direction == 1 and y + STRIDE >= height:
                    continue
                contacts = {}
                length = min(STRIDE, height - y) if direction == 0 else min(STRIDE, width - x)
                for offset in range(length):
                    at = ((y + offset) * width + x + STRIDE - 1 if direction == 0
                          else (y + STRIDE - 1) * width + x + offset)
                    other = at + (1 if direction == 0 else width)
                    first, last = labels[at], labels[other]
                    if first and last:
                        road_score = int(bool(road_raw and road_raw[at])) + int(bool(road_raw and road_raw[other]))
                        contacts.setdefault((first, last), []).append((offset, road_score))
                for (first, last), candidates in sorted(contacts.items()):
                    offset = contact_offset(candidates)
                    value = direction * 262144 + offset * 16384 + first * 128 + last
                    records.append(''.join(CHARS[(value >> shift) & 63] for shift in (18, 12, 6, 0)))
            assert len(records) <= 24
            has_road = (permitted_roads is not None and permitted_roads.crop(
                (x, y, min(width, x + STRIDE), min(height, y + STRIDE))).getbbox() is not None)
            row.append(CHARS[len(records) + (32 if has_road else 0)])
            row.extend(records)
        result.append(''.join(row))
    return result


def build(lua, maps=None):
    addon = lua.globals().A
    zones = {}
    for map_id, source in sorted(addon.TerrainData.zones.items()):
        if source.status not in ('complete', 'partial') or maps is not None and int(map_id) not in maps:
            continue
        zone = addon.Terrain.Zone(map_id)
        if isinstance(zone, tuple):
            zone = zone[0]
        if zone is None:
            continue
        width, height = int(zone.w), int(zone.h)
        permitted = decode_rows(zone.rows, width, height)
        if zone.groundRows is not None:
            permitted = ImageChops.lighter(permitted, decode_rows(zone.groundRows, width, height))
        roads = addon.Roads.Zone(map_id, zone)
        road_mask = decode_rows(roads.rows, width, height) if roads is not None else None
        water = addon.Water.Zone(map_id, zone)
        dry_mask = decode_rows(water.rows, width, height) if water is not None else None
        options = lua.table_from(dict(preferRoads=False, allowSwimming=True))
        signature = addon.PathReuse.Signature(map_id, options)[0]
        options.allowSwimming = False
        dry_signature = addon.PathReuse.Signature(map_id, options)[0]
        rows = portal_rows(permitted, road_mask)
        dry_rows = (portal_rows(ImageChops.multiply(permitted, dry_mask), road_mask)
                    if dry_mask is not None else ['A' * ((width + 11) // 12)] * ((height + 11) // 12))
        zones[int(map_id)] = dict(w=width, h=height, maskSha256=zone.maskSha256,
                                  signature=signature, drySignature=dry_signature,
                                  rows=rows, dryRows=dry_rows)
    return dict(version=1, stride=STRIDE, zones=zones)


def render(data):
    lines = ['-- Generated by tools/build_walking_portals.py; exact ground-component topology.',
             '-- Header base64 value: portal count (low 5 bits), permitted road present (bit 32).',
             '-- Each portal is 4 big-endian base64 chars: direction*262144+offset*16384+sourceComponent*128+targetComponent.',
             '-- Direction 0=E, 1=S; offset 0..11; component IDs 1-based in row-major seed order.',
             '-- Tile IDs are zero-based row-major; nodeKey=tileID*144+component. Runtime must refine and validate geometry.',
             'local _,A=...', 'A.WalkingPortalData={version=1,stride=12,zones={}}',
             'local Z=A.WalkingPortalData.zones']
    for map_id, zone in sorted(data['zones'].items()):
        fields = ','.join(name + '=' + json.dumps(zone[name]) for name in
                          ('w', 'h', 'maskSha256', 'signature', 'drySignature'))
        lines.append(f'Z[{map_id}]={{' + fields + ',rows={')
        lines.extend(json.dumps(row) + ',' for row in zone['rows'])
        lines.append('},dryRows={')
        lines.extend(json.dumps(row) + ',' for row in zone['dryRows'])
        lines.append('}}')
    return '\n'.join(lines) + '\n'


def compactness(data):
    """Verify packed framing and report sizes without materializing Lua edges."""
    tiles = portals = payload = 0
    for zone in data['zones'].values():
        columns, height = (zone['w'] + 11) // 12, (zone['h'] + 11) // 12
        tiles += columns * height
        for policy in ('rows', 'dryRows'):
            assert len(zone[policy]) == height
            for row in zone[policy]:
                at = 0
                for _ in range(columns):
                    count = CHARS.index(row[at]) % 32
                    assert count <= 24
                    at += 1 + count * 4
                    portals += count
                assert at == len(row) and all(char in CHARS for char in row)
                payload += len(row)
    assert payload == tiles * 2 + portals * 4
    assert payload <= tiles * 2 * 97
    source = render(data).encode('utf8')
    return dict(maps=len(data['zones']), tiles=tiles, portals=portals,
                payloadBytes=payload, sourceBytes=len(source),
                deflatedBytes=len(zlib.compress(source, 9)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', help='comma-separated pilot map IDs; default all supported maps')
    parser.add_argument('--output', type=Path, default=ROOT / 'Data/WalkingPortals.lua')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    maps = set(map(int, args.maps.split(','))) if args.maps else None
    began = time.perf_counter()
    data = build(runtime(), maps)
    content = render(data)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding='utf8') != content:
            raise SystemExit('Walking portal data is stale; rebuild it with the same map selection')
    else:
        args.output.write_text(content, encoding='utf8', newline='\n')
    print(json.dumps(compactness(data), sort_keys=True))
    print(('Verified' if args.check else 'Generated') + f' in {time.perf_counter() - began:.2f}s')


if __name__ == '__main__':
    main()
