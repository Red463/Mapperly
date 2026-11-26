"""Exact tile-component portal graph retains narrow-channel connectivity."""
from collections import deque
from pathlib import Path
import importlib.util
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / '.test-deps'))
assert importlib.util.find_spec('build_walking_portals'), 'Walking portal builder is missing'
from build_walking_portals import portal_rows, build, render, compactness, decode_rows
from lupa.lua51 import LuaRuntime

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
assert decode_rows({1: 'g', 2: ''}, 8, 2).tobytes() == bytes([255] + [0] * 15)
assert decode_rows({1: '?'}, 8, 2).tobytes() == bytes(16), 'Unknown packed bytes and absent rows stay blocked'


def packed(cells, width, height):
    return [''.join(ALPHABET[sum(1 << (5 - bit) for bit in range(6)
                                if (x + bit, y) in cells and x + bit < width)]
                    for x in range(0, width, 6)) for y in range(height)]


def local_components(cells, width, height):
    """Independent set-based oracle, with the documented row-major seed IDs."""
    result = {}
    for ty in range((height + 11) // 12):
        for tx in range((width + 11) // 12):
            left = {(x, y) for x, y in cells if x // 12 == tx and y // 12 == ty}
            component = 0
            while left:
                seed = min(left, key=lambda p: (p[1], p[0]))
                component += 1
                todo = deque([seed])
                left.remove(seed)
                while todo:
                    x, y = todo.popleft()
                    result[x, y] = ((ty * ((width + 11) // 12) + tx), component)
                    for q in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        if q in left:
                            left.remove(q)
                            todo.append(q)
    return result


def decode(rows, width, height):
    contacts, edges = [], set()
    columns = (width + 11) // 12
    for ty, row in enumerate(rows):
        at = 0
        for tx in range(columns):
            count = ALPHABET.index(row[at]) % 32
            at += 1
            for _ in range(count):
                value = 0
                for char in row[at:at + 4]:
                    value = value * 64 + ALPHABET.index(char)
                at += 4
                direction, offset = value // 262144, (value // 16384) % 16
                ca, cb = (value // 128) % 128, value % 128
                assert direction in (0, 1) and offset < 12 and 1 <= ca <= 72 and 1 <= cb <= 72
                if direction == 0:
                    a, b = (tx * 12 + 11, ty * 12 + offset), (tx * 12 + 12, ty * 12 + offset)
                    target = ty * columns + tx + 1
                else:
                    a, b = (tx * 12 + offset, ty * 12 + 11), (tx * 12 + offset, ty * 12 + 12)
                    target = (ty + 1) * columns + tx
                first, last = (ty * columns + tx, ca), (target, cb)
                edges.add((first, last))
                contacts.append((first, last, a, b))
        assert at == len(row), 'No unparsed tile data or omitted columns'
    return contacts, edges


def verify(cells, width, height, roads=None):
    mask = decode_rows(packed(cells, width, height), width, height)
    road_mask = decode_rows(packed(roads, width, height), width, height) if roads is not None else None
    rows = portal_rows(mask, road_mask)
    labels = local_components(cells, width, height)
    expected = set()
    for x, y in cells:
        for q in ((x + 1, y), (x, y + 1)):
            if q in cells and labels[x, y][0] != labels[q][0]:
                expected.add((labels[x, y], labels[q]))
    contacts, actual = decode(rows, width, height)
    assert actual == expected, 'Every and only adjacent tile-component pair must be represented'
    assert len(contacts) == len(actual), 'Only one selected contact per adjacent component pair'
    for first, last, a, b in contacts:
        assert a in cells and b in cells and labels[a] == first and labels[b] == last
    return rows, contacts


# Fixed tile centers are blocked along this narrow connected path.
channel = {(x, 2) for x in range(25)} | {(23, y) for y in range(2, 13)} | {(x, 12) for x in range(5, 24)}
rows, contacts = verify(channel, 25, 13)
assert len(contacts) == 4, 'Narrow turns and clipped tile contacts must survive'

# A complete wall separates components within tiles; disconnected islands must
# never be merged just because each tile contains permitted cells.
wall = {(x, y) for y in range(25) for x in range(25) if x != 6 and y != 17}
verify(wall, 25, 25)

# Prefer a fully road-supported contact even outside the longest ground span.
full = {(x, y) for y in range(12) for x in range(24)}
_, contacts = verify(full, 24, 12, {(11, 10), (12, 10)})
assert contacts[0][2:] == ((11, 10), (12, 10))
road_rows = portal_rows(decode_rows(packed(full, 24, 12), 24, 12),
                        decode_rows(packed({(11, 10), (12, 10)}, 24, 12), 24, 12))
assert ALPHABET.index(road_rows[0][0]) == 33 and ALPHABET.index(road_rows[0][5]) == 32
assert portal_rows(decode_rows(packed({(0, 0)}, 24, 12), 24, 12),
                   decode_rows(packed({(23, 11)}, 24, 12), 24, 12)) == ['AA'], 'Blocked roads cannot set the hint bit'
_, contacts = verify(full, 24, 12)
assert contacts[0][2:] == ((11, 5), (12, 5)), 'Middle of longest span, lower tie wins'

rng = random.Random(70959)
for width, height in ((13, 13), (25, 25), (25, 13), (13, 25), (1, 25), (25, 1)):
    for _ in range(8):
        cells = {(x, y) for y in range(height) for x in range(width) if rng.random() > .43}
        verify(cells, width, height)

# Integration uses production terrain, ground, road and water source guards.
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={}')
for name in ('Terrain.lua', 'Roads.lua', 'Water.lua', 'PathReuse.lua'):
    lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
shape = dict(w=24, h=12, widthYards=240, heightYards=120)
for name, value in dict(
    TerrainData=dict(version=1, zones={1: dict(shape, status='complete', maskSha256='base', rows=packed(full, 24, 12))}),
    GroundCorrectionData=dict(version=1, zones={}),
    RoadData=dict(version=1, build=1, zones={}),
    RoadSupplementData=dict(version=1, build=1, zones={}),
    WaterData=dict(version=1, zones={1: dict(w=24, h=12, baseSha256='base', rows=packed(full - {(12, y) for y in range(12)}, 24, 12))}),
).items():
    lua.globals().A[name] = lua.table_from(value, recursive=True)
data = build(lua)
assert compactness(data)['payloadBytes'] == 8
assert data['zones'][1]['signature'] == lua.globals().A.PathReuse.Signature(
    1, lua.table_from(dict(preferRoads=False, allowSwimming=True)))[0]
assert data['zones'][1]['drySignature'] == lua.globals().A.PathReuse.Signature(
    1, lua.table_from(dict(preferRoads=False, allowSwimming=False)))[0]
assert len(decode(data['zones'][1]['rows'], 24, 12)[1]) == 1
assert not decode(data['zones'][1]['dryRows'], 24, 12)[1], 'Dry wall cannot have a portal'
lua.globals().A.WaterData.zones[1].baseSha256 = 'stale'
assert build(lua)['zones'][1]['dryRows'] == ['AA'], 'Unknown water cannot certify dry portals'
lua.globals().A.WaterData.zones[1].baseSha256 = 'base'
lua.globals().A.RoadData.zones[1] = lua.table_from(dict(
    shape, roadCells=2, rows=packed({(11, 10), (12, 10)}, 24, 12)), recursive=True)
with_roads = build(lua)['zones'][1]
assert ALPHABET.index(with_roads['rows'][0][0]) == 33
assert ALPHABET.index(with_roads['dryRows'][0][0]) == 32
assert ALPHABET.index(with_roads['dryRows'][0][1]) == 0
lua.globals().A.TerrainData.zones[1].rows = lua.table_from(packed(full - {(11, y) for y in range(12)}, 24, 12))
assert not decode(build(lua)['zones'][1]['rows'], 24, 12)[1]
patch = dict(w=24, h=12, baseSha256='base', maskSha256='door', cells=1,
             rows=packed({(11, 5)}, 24, 12))
lua.globals().A.GroundCorrectionData.zones[1] = lua.table_from(patch, recursive=True)
corrected = build(lua)['zones'][1]
assert len(decode(corrected['rows'], 24, 12)[1]) == 1, 'Matching ground correction restores the narrow portal'
assert corrected['signature'] != data['zones'][1]['signature']
lua.globals().A.GroundCorrectionData.zones[1].baseSha256 = 'stale'
assert not decode(build(lua)['zones'][1]['rows'], 24, 12)[1], 'Stale correction cannot invent a portal'

# A road supplement is resolved by production source guards, including the
# exact base rows. Neither stale supplements nor prohibited roads set bit 32.
lua.globals().A.TerrainData.zones[1].rows = lua.table_from(packed(full, 24, 12))
base_rows = packed(set(), 24, 12)
lua.globals().A.RoadData.zones[1] = lua.table_from(dict(shape, roadCells=0, rows=base_rows), recursive=True)
supplement = dict(shape, baseRoadCells=0, terrainMaskSha256='base',
                  baseRows=base_rows, roadCells=2, rows=packed({(11, 10), (12, 10)}, 24, 12))
lua.globals().A.RoadSupplementData.zones[1] = lua.table_from(supplement, recursive=True)
assert ALPHABET.index(build(lua)['zones'][1]['rows'][0][0]) == 33
lua.globals().A.RoadSupplementData.zones[1].terrainMaskSha256 = 'stale'
assert ALPHABET.index(build(lua)['zones'][1]['rows'][0][0]) == 1
lua.globals().A.RoadSupplementData.zones[1].terrainMaskSha256 = 'base'
lua.globals().A.RoadSupplementData.zones[1].baseRows[1] = 'changed'
assert ALPHABET.index(build(lua)['zones'][1]['rows'][0][0]) == 1
text = render(data)
assert text == render(data)
lua.execute('assert(loadstring(...))("Mapperly",A)', text)
assert lua.globals().A.WalkingPortalData.stride == 12
assert lua.globals().A.WalkingPortalData.zones[1].rows[1] == data['zones'][1]['rows'][0]
assert compactness(data)['sourceBytes'] < 2000 and compactness(data)['deflatedBytes'] < 1000
print('PASS: topology-complete cardinal portals, narrow channels, component IDs, contact selection and source policy')
