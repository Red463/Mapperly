"""Reproduce the Southfury bridge proof from the read-only build 70959 CASC snapshot.

Run from any directory. Only writes tools/data/native-southfury-bridge-70959.json.
Native triangle collision rule matches the existing native corridor extractor.
"""
from pathlib import Path
import hashlib
import csv
import json
import math
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/roads'))
from local_casc import LocalCasc

T = 1600 / 3
ORIGIN = T * 32
S = T / 128


def chunks(raw, start=0, end=None):
    end = len(raw) if end is None else end
    while start < end:
        tag, size = struct.unpack_from('<4sI', raw, start)
        first, last = start + 8, start + 8 + size
        assert last <= end
        yield tag[::-1].decode('ascii'), first, last
        start = last


def bary(x, y, vertices):
    a, b, c = vertices
    den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
    if abs(den) < 1e-10:
        return None
    u = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1])) / den
    v = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1])) / den
    w = 1-u-v
    return u*a[2]+v*b[2]+w*c[2] if min(u, v, w) >= -1e-7 else None


class Native:
    def __init__(self, snapshot, placement=None, wdt_fdid=782779):
        self.casc = LocalCasc(snapshot)
        self.sources = {}
        self.cache = {}
        wdt = self.read(wdt_fdid)
        self.maid = next(wdt[a:z] for t, a, z in chunks(wdt) if t == 'MAID')
        obj = self.read(786406)
        modf = next(obj[a:z] for t, a, z in chunks(obj) if t == 'MODF')
        for at in range(0, len(modf), 64):
            fdid, uid = struct.unpack_from('<II', modf, at)
            if uid == 294532:
                self.placement = dict(fdid=fdid, uid=uid,
                    pos=list(struct.unpack_from('<3f', modf, at+8)),
                    rot=list(struct.unpack_from('<3f', modf, at+20)),
                    bounds=list(struct.unpack_from('<6f', modf, at+32)),
                    flags=struct.unpack_from('<H', modf, at+56)[0],
                    scale=struct.unpack_from('<H', modf, at+62)[0])
                break
        else:
            raise ValueError('Missing pinned MODF placement')
        if placement is not None:
            if any(abs(placement['rot'][i])>.0001 for i in (0,2)):
                raise ValueError('Tilted placements require a full rotation proof')
            # Bind supplied inventory coordinates to an actual native MODF
            # record, rather than trusting an editable inventory placement.
            tx,ty=int(placement['pos'][0]//T),int(placement['pos'][2]//T)
            matched=False
            for yy in range(max(0,ty-1),min(64,ty+2)):
                for xx in range(max(0,tx-1),min(64,tx+2)):
                    ids=struct.unpack_from('<8I',self.maid,(yy*64+xx)*32)
                    for fid in sorted(set(v for v in ids[:3] if v)):
                        data=self.read(fid)
                        for tag,a,b in chunks(data):
                            if tag!='MODF':continue
                            for at in range(a,b,64):
                                root,uid=struct.unpack_from('<II',data,at)
                                if uid!=placement['uid']:continue
                                if root!=placement['fdid'] or list(struct.unpack_from('<3f',data,at+8))!=placement['pos'] or list(struct.unpack_from('<3f',data,at+20))!=placement['rot'] or list(struct.unpack_from('<6f',data,at+32))!=placement['bounds'] or struct.unpack_from('<H',data,at+56)[0]!=placement['flags'] or struct.unpack_from('<H',data,at+62)[0]!=placement['scale']:
                                    raise ValueError('Inventory placement differs from native MODF')
                                matched=True
            if not matched:raise ValueError('Native placement witness unavailable near its origin')
            self.placement=placement
        raw = self.read(self.placement['fdid'])
        root = {t: raw[a:z] for t, a, z in chunks(raw)}
        count = struct.unpack_from('<I', root['MOHD'], 4)[0]
        self.faces = []
        self.vertices = []
        for fid in struct.unpack_from('<'+'I'*count, root['GFID']):
            raw = self.read(fid)
            a, z = next((a, z) for t, a, z in chunks(raw) if t == 'MOGP')
            group = {t: raw[s:e] for t, s, e in chunks(raw, a+68, z)}
            vertices = list(struct.iter_unpack('<3f', group['MOVT']))
            self.vertices.extend(vertices)
            for index, (ids, (flags, material)) in enumerate(zip(struct.iter_unpack('<3H', group['MOVI']), struct.iter_unpack('<BB', group['MOPY']))):
                if not (flags & 8 or flags & 32 and not flags & 4):
                    continue
                v = [vertices[k] for k in ids]
                p, q, r = v
                u, w = [[b-a for a, b in zip(p, vertex)] for vertex in (q, r)]
                n = [u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0]]
                slope = math.degrees(math.atan2(math.hypot(*n[:2]), abs(n[2])))
                self.faces.append(dict(v=v, up=n[2]>0, slope=slope, flags=flags, group=fid, triangle=index))

    def read(self, fid):
        raw = self.casc.read_fdid(fid)
        self.sources[fid] = hashlib.sha256(raw).hexdigest()
        return raw

    def world(self, x, y, z):
        p = self.placement
        ct, st = math.cos(math.radians(p['rot'][1])), math.sin(math.radians(p['rot'][1]))
        scale = p['scale']/1024 if p['flags'] & 4 else 1
        return [ORIGIN-p['pos'][2]-scale*(ct*x-st*y), ORIGIN-p['pos'][0]-scale*(st*x+ct*y), p['pos'][1]+scale*z]

    def floor(self, x, y):
        hits = [(z, i) for i, f in enumerate(self.faces) if (z := bary(x, y, f['v'])) is not None]
        floors = [(z, i) for z, i in hits if self.faces[i]['up'] and self.faces[i]['slope'] <= 50]
        if not floors:
            return None
        z, index = min(floors)
        ceiling = [h for h, i in hits if not self.faces[i]['up'] and h > z+.1]
        return z, index, min(ceiling)-z if ceiling else 999

    def terrain(self, north, east):
        tx, ty = int((ORIGIN-east)//T), int((ORIGIN-north)//T)
        key = tx, ty
        if key not in self.cache:
            fid = struct.unpack_from('<I', self.maid, (ty*64+tx)*32)[0]
            raw = self.read(fid)
            cells, liquid = {}, None
            for t, a, z in chunks(raw):
                if t == 'MCNK':
                    flags, cx, cy = struct.unpack_from('<3I', raw, a)
                    origin = struct.unpack_from('<3f', raw, a+104)
                    heights = next(struct.unpack_from('<145f', raw, s) for t, s, e in chunks(raw, a+128, z) if t == 'MCVT')
                    cells[cx, cy] = flags, origin, heights, int.from_bytes(raw[a+20:a+28], 'little'), struct.unpack_from('<H', raw, a+60)[0], struct.unpack_from('<I', raw, a+52)[0]
                if t == 'MH2O':
                    liquid = raw, a
            self.cache[key] = cells, liquid, fid
        cells, liquid, fid = self.cache[key]
        lx, ly = (ORIGIN-tx*T-east)/S, (ORIGIN-ty*T-north)/S
        ix, iy = int(lx), int(ly)
        cx, x = divmod(ix, 8)
        cy, y = divmod(iy, 8)
        flags, origin, h, hi, lo, area = cells[cx, cy]
        a, b, d, e, center = h[y*17+x], h[y*17+x+1], h[(y+1)*17+x], h[(y+1)*17+x+1], h[y*17+9+x]
        vertices = [(0, 0, a), (1, 0, b), (1, 1, e), (0, 1, d), (.5, .5, center)]
        z = next(z for i in range(4) if (z := bary(lx-ix, ly-iy, [vertices[i], vertices[(i+1)%4], vertices[4]])) is not None)+origin[2]
        gradients = [((b-a)/S, (2*center-a-b)/S), ((b+e-2*center)/S, (e-b)/S), ((e-d)/S, (d+e-2*center)/S), ((2*center-a-d)/S, (d-a)/S)]
        slope = math.degrees(math.atan(max(math.hypot(*g) for g in gradients)))
        hole = bool(hi & (1 << (y*8+x))) if flags & 0x10000 else bool(lo & (1 << ((y//2)*4+x//2)))
        wet = False;liquid_high=None
        if liquid:
            raw, base = liquid
            offset, layers, _ = struct.unpack_from('<3I', raw, base+(cy*16+cx)*12)
            for layer in range(layers):
                _, fmt, low, high, xo, yo, width, height, bitmap, verts = struct.unpack_from('<HHff4BII', raw, base+offset+layer*24)
                if xo <= x < xo+width and yo <= y < yo+height:
                    bit = (y-yo)*width+x-xo
                    covered=not bitmap or bool(raw[base+bitmap+bit//8] & (1 << (bit%8)))
                    if covered:wet=True;liquid_high=high if liquid_high is None else max(liquid_high,high)
        return dict(fdid=fid, height=z, hole=hole, slope=slope, liquid=wet, liquidHigh=liquid_high, area=area, permitted=not hole and not wet and slope<50)


def runtime():
    sys.path.insert(0, str(ROOT / '.test-deps'))
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT/'tests/wow.lua').read_text())
    lua.execute('fakeUI();A={}')
    for name in ['Store.lua', 'Data/Terrain.lua', 'Data/GroundCorrections.lua', 'Data/WalkingRegions.lua', 'Terrain.lua', 'WalkingRegions.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT/name).read_text())
    lua.execute('A.InitStore({})')
    return lua


def main():
    native = Native(ROOT.parent/'output/forever-datamine-70959')
    lua = runtime()
    zones = {z['id']: z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}

    def mapped(world, map_id):
        zone = zones[map_id]
        return dict(mapID=map_id, x=(zone['west']-world[1])/(zone['west']-zone['east']), y=(zone['north']-world[0])/(zone['north']-zone['south']))

    def contact(low, high):
        def delta(y):
            world = native.world(0, y, native.floor(0, y)[0])
            return world[2]-native.terrain(*world[:2])['height']
        assert delta(low)*delta(high) < 0
        for _ in range(45):
            mid = (low+high)/2
            if delta(low)*delta(mid) <= 0:
                high = mid
            else:
                low = mid
        return (low+high)/2

    start, end = contact(-30.75, -30.5), contact(29.25, 29.5)
    count = math.ceil((end-start)/.25)
    ys = [start+(end-start)*i/count for i in range(count+1)]
    samples, faces, used = [], [], set()
    points = []
    for y in ys:
        z, face, headroom = native.floor(0, y)
        used.add(face)
        points.append(native.world(0, y, z))
        samples.append(dict(point=points[-1], segment=min(len(points)-1, count-1), headroom=headroom))
    for index in sorted(used):
        face = native.faces[index]
        faces.append(dict(v=[native.world(*p) for p in face['v']], sourceGroup=face['group'], sourceTriangle=face['triangle'], sourceFlags=face['flags']))
    landings = []
    for map_id, y, p in zip((1440, 1447), (start, end), (points[0], points[-1])):
        terrain = native.terrain(*p[:2])
        point = mapped(p, map_id)
        allowed = bool(lua.eval('function(p) return A.Terrain.Segment(p,p) end')(lua.table_from(point)))
        region = lua.eval('function(p) return A.WalkingRegions.Get(p) end')(lua.table_from(point))
        assert allowed and region == 1 and terrain['permitted'] and abs(p[2]-terrain['height']) < .000001
        landings.append(dict(**terrain, localY=y, world=p, mapPoint=point, runtimeSegment=allowed, runtimeRegion=region, terrainDelta=p[2]-terrain['height']))
    width_rise = []
    for y in ys:
        center = native.floor(0, y)[0]
        for i in range(21):
            hit = native.floor(-2.5+i*.25, y)
            assert hit is not None and hit[2] >= 2.2
            width_rise.append(hit[0]-center)
    # MODF bounds conservatively enclose the transformed mesh, rather than
    # matching its extrema. Record that slack separately from roundtrip error.
    transformed = [native.world(*p) for p in native.vertices]
    actual = [ORIGIN-max(p[1] for p in transformed), min(p[2] for p in transformed), ORIGIN-max(p[0] for p in transformed), ORIGIN-min(p[1] for p in transformed), max(p[2] for p in transformed), ORIGIN-min(p[0] for p in transformed)]
    bounds = native.placement['bounds']
    slack = [actual[i]-bounds[i] if i<3 else bounds[i]-actual[i] for i in range(6)]
    assert min(slack) >= -.001
    theta = math.radians(native.placement['rot'][1])
    ct, st = math.cos(theta), math.sin(theta)
    transform_error = 0
    for x, y, z in native.vertices:
        p = native.world(x, y, z)
        a, b = ORIGIN-native.placement['pos'][2]-p[0], ORIGIN-native.placement['pos'][0]-p[1]
        local = [ct*a+st*b, -st*a+ct*b, p[2]-native.placement['pos'][1]]
        transform_error = max(transform_error, math.dist(local, (x, y, z)))
    db = ROOT.parent/'output/forever-datamine-70959/terrain-research/ashenvale/raw/dbfilesclient'
    areas = {int(r['ID']):r for r in csv.DictReader((db/'areatable.csv').open(encoding='utf-8-sig'))}
    assert int(areas[2457]['ParentAreaID']) == 331 and int(areas[878]['ParentAreaID']) == 16
    provenance = dict(fdidSha256={str(k):v for k, v in sorted(native.sources.items())},
        areaTableSha256=hashlib.sha256((db/'areatable.csv').read_bytes()).hexdigest(),
        runtimeSha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['Data/Terrain.lua', 'Data/GroundCorrections.lua', 'Data/WalkingRegions.lua', 'Terrain.lua', 'WalkingRegions.lua']})
    row = dict(name='Southfury stone bridge', corridorID=294532, placement=294532, wmo=113275,
        fromUiMap=1440, toUiMap=1447, build=70959,
        worldCenterline=points, samples=samples, faces=faces, landings=landings,
        transformError=transform_error, transformErrorMethod='World/local inverse roundtrip; independent MODF bounds containment below',
        nativePlacement=native.placement, transformedMeshBounds=actual, nativeBoundsSlack=slack,
        portalGap=max(abs(p['terrainDelta']) for p in landings),
        maximumStep=max(abs(a[2]-b[2]) for a, b in zip(points, points[1:])),
        minimumHeadroom=min(s['headroom'] for s in samples),
        widthProof=dict(radiusYards=2.5, lateralStepYards=.25, longitudinalStepYards=(end-start)/count, sampleCount=len(width_rise), minimumHeightDelta=min(width_rise), maximumHeightDelta=max(width_rise), method='Native upward collidable triangle support at transverse grid samples; 999 headroom denotes open sky'),
        nativeAreaOwnership=[dict(area=2457, parent=331, mapID=1440, name=areas[2457]['AreaName_lang']), dict(area=878, parent=16, mapID=1447, name=areas[878]['AreaName_lang'])],
        provenance=provenance,
        method='Native MODF UID294532 from ADTobj786406, WMO113275 GFID groups, MOVT/MOVI/MOPY collision triangles. Centerline x=0; handoffs are exact intersections with native MCNK triangle heights; MCNK holes and MH2O exclude invalid landings. No terrain permissions altered.')
    from build_structure_corridors import validate_curved
    length = validate_curved(row)
    destination = ROOT/'tools/data/native-southfury-bridge-70959.json'
    destination.write_text(json.dumps([row], separators=(',', ':'))+'\n')
    print(json.dumps(dict(output=str(destination), length=length, samples=len(samples), landings=landings, transformError=transform_error, boundsSlack=slack, width=row['widthProof']), indent=2))


if __name__ == '__main__':
    main()
