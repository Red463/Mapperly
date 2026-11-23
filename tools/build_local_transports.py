"""Compile audited manual lift access without inventing moving-platform geometry."""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.test-deps'))
from lupa.lua51 import LuaRuntime


def compile_data(source):
    audit=json.loads(source.read_text(encoding='utf-8-sig'))
    exit_source=ROOT/'tools/data/native-lift-exits-70959.json'
    exit_audit=json.loads(exit_source.read_text(encoding='utf8'))
    mask_source=ROOT/'tools/data/native-lift-exit-masks-70959.json'
    mask_audit=json.loads(mask_source.read_text(encoding='utf8'))
    assert mask_audit['version']==1 and mask_audit['build']==audit['build']
    assert mask_audit['provenance']['nativeStaticWmo']['rootSha256']==audit['provenance']['nativeIdentity']['rootSha256']
    for filename,digest in mask_audit['provenance']['runtimeMaskInputSha256'].items():
        assert hashlib.sha256((ROOT/filename.replace('\\','/')).read_bytes()).hexdigest()==digest,'stale exit mask input: '+filename
    assert exit_audit['version']==1 and exit_audit['build']==audit['build']
    assert exit_audit['provenance']['nativeWmoRootSha256']==audit['provenance']['nativeIdentity']['rootSha256']
    assert exit_audit['provenance']['nativeWmoGroupSha256']==audit['provenance']['groupSha256']
    assert audit['version']==1 and audit['build']==70959 and audit['method']=='manualLift'
    native=audit['provenance']['nativeIdentity']
    assert native['rootFileDataID']==112647 and native['placementUID']==283429
    assert native['groupNames']==['elevator','bottom']
    zones={z['id']:z for z in json.loads((ROOT/'tools/roads/zones.json').read_text())['zones']}
    lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
    for name in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Terrain.lua','WalkingRegions.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)',(ROOT/name).read_text(encoding='utf8'))

    def point(p):
        assert p['mapID'] in (1413,1441) and p['continent']==1
        n,e,z=p['worldPosition'];zone=zones[p['mapID']]
        assert all(math.isfinite(v) for v in (n,e,z))
        assert abs(p['x']-(zone['west']-e)/(zone['west']-zone['east']))<1e-9
        assert abs(p['y']-(zone['north']-n)/(zone['north']-zone['south']))<1e-9
        proof=p['groundHeightProof']
        assert proof['permitted'] and not proof['hole'] and not proof['liquid'] and proof['slope']<=50
        assert abs(proof['height']-z)<1e-6 and abs(p['groundHeight']-z)<1e-6
        assert p['manualAccess']
        q={k:p[k] for k in ('mapID','x','y')};lq=lua.table_from(q)
        assert lua.globals().A.Terrain.Segment(lq,lq)
        assert lua.globals().A.WalkingRegions.Get(lq)==p['walkingRegion']
        floor=p['nativeCollidableFloor'];vertices=floor['vertices']
        assert floor['groupFileDataID'] in native['groupFileDataIDs'] and len(vertices)==3
        center=[sum(v[i] for v in vertices)/3 for i in range(3)]
        assert math.dist(center,floor['position'])<1e-6 and math.dist(center,(n,e,z))<=30
        u=[vertices[1][i]-vertices[0][i] for i in range(3)]
        v=[vertices[2][i]-vertices[0][i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        assert math.hypot(*normal)>0 and abs(normal[2])/math.hypot(*normal)>=math.cos(math.radians(50))
        anchor=p['connectedAnchor'];points=anchor['points']
        assert len(points)>=2 and points[-1]==q
        for a,b in zip(points,points[1:]):
            assert a['mapID']==q['mapID']==b['mapID']
            assert lua.globals().A.Terrain.Segment(lua.table_from(a),lua.table_from(b))
        return q

    edges=[]
    for row in audit['links']:
        assert row['kind']=='lift' and row['method']=='manualLift' and row['manualBoarding'] and row['manualDisembark']
        assert row['timingIsAssumption'] and row['estimatedSeconds']==row['waitSeconds']+row['travelSeconds']
        assert 0<row['estimatedSeconds']<=7200 and row['sourceObjectID'] is None and row['pathID'] is None
        a,b=point(row['a']),point(row['b'])
        assert a['mapID']!=b['mapID'] and abs(row['boardingGroundHeight']-row['arrivalGroundHeight'])>16
        assert row['boardingGroundHeight']==row['a']['groundHeight'] and row['arrivalGroundHeight']==row['b']['groundHeight']
        def world(key,endpoint):
            n,e,z=row[key]
            assert row[key]==row[endpoint]['nativeCollidableFloor']['position']
            return dict(worldX=e,worldY=n,instance=1)
        exit_rows=next(r['arrivalExits'] for r in exit_audit['links'] if r['id']==row['id'])
        exits=[]
        for zone in exit_rows:
            assert zone['mapID']==b['mapID'] and 0<zone['radius']<=12 and zone['continent']==1
            assert zone['minimumProjectionClearanceWithinDiskYards']>=8
            assert zone['nativeStaticProjectionClearanceYards']-zone['radius']>=8
            proof=zone['nativeDryProof'];assert proof['allNativePermitted'] and proof['allMaskDry'] and proof['allRegion1']
            assert proof['maximumRootCellSlope']<=50 and proof['boundingSquareHalfExtentYards']>=zone['radius']
            assert len(proof['corners'])==4 and proof['sampleCount']>=9
            q={k:zone[k] for k in ('mapID','x','y')};lq=lua.table_from(q)
            assert lua.globals().A.WalkingRegions.Get(lq)==zone['region']
            assert lua.globals().A.Terrain.Segment(lq,lua.table_from(b))
            n,e,z=zone['worldPosition'];extent=zones[zone['mapID']]
            assert abs(q['x']-(extent['west']-e)/(extent['west']-extent['east']))<1e-9
            assert abs(q['y']-(extent['north']-n)/(extent['north']-extent['south']))<1e-9
            assert math.dist((n,e),row['b']['worldPosition'][:2])<=150
            for corner in proof['corners']:
                p=corner['ground'];assert p['permitted'] and not p['hole'] and not p['liquid'] and p['slope']<=50
                cn,ce,_=corner['world'];cq=lua.table_from(dict(mapID=q['mapID'],x=(extent['west']-ce)/(extent['west']-extent['east']),y=(extent['north']-cn)/(extent['north']-extent['south'])))
                assert lua.globals().A.WalkingRegions.Get(cq)==zone['region'] and lua.globals().A.Terrain.Segment(lq,cq)
            exits.append(dict(q,radius=zone['radius'],region=zone['region'],minHeight=proof['minimumGroundHeight'],maxHeight=proof['maximumGroundHeight']))
        mask_map=next(r['arrivalExitMaskMapID'] for r in mask_audit['links'] if r['id']==row['id'])
        mask=next(m for m in mask_audit['masks'] if m['mapID']==mask_map)
        assert mask_map==b['mapID'] and mask['cellSize']==4 and 0<mask['width']<=128 and 0<mask['height']<=128
        assert len(mask['rows'])==mask['height'] and mask['maxDistanceFromHandoffYards']<=200
        assert mask['minHeight']<=row['arrivalGroundHeight']<=mask['maxHeight']
        assert mask['proof']['nativeSamplesPerCell']==25 and mask['proof']['guaranteedCellProjectionClearanceYards']>=8
        assert mask['proof']['nativeRootTerrainNoHoleNoLiquid'] and mask['proof']['nativeRootCellSlopeMaximumDegrees']<=50
        count=0;extent=zones[mask_map]
        for line,bits in enumerate(mask['rows']):
            assert len(bits)==mask['width'] and set(bits)<=set('.1')
            for column,bit in enumerate(bits):
                if bit!='1':continue
                count+=1
                for dn,de in ((0,0),(-2,-2),(-2,2),(2,-2),(2,2)):
                    n=mask['originNorth']-(line+.5)*4+dn;e=mask['originEast']-(column+.5)*4+de
                    assert math.dist((n,e),row['b']['worldPosition'][:2])<=200.001
                    p=lua.table_from(dict(mapID=mask_map,x=(extent['west']-e)/(extent['west']-extent['east']),y=(extent['north']-n)/(extent['north']-extent['south'])))
                    assert lua.globals().A.WalkingRegions.Get(p)==mask['region'] and lua.globals().A.Terrain.Segment(p,p)
        assert count==mask['allowedCellCount'] and count>=900
        grid={k:mask[k] for k in ('mapID','region','originNorth','originEast','cellSize','width','height','rows','minHeight','maxHeight')}
        grid.update(version=1,instance=mask['continent'])
        edges.append(dict(id=row['id'],kind='lift',name=row['name'],faction='Neutral',a=a,b=b,
            board=world('boardingPosition','a'),arrival=world('arrivalPosition','b'),
            boardingGroundHeight=row['boardingGroundHeight'],arrivalGroundHeight=row['arrivalGroundHeight'],
            fromName=zones[a['mapID']]['name'],toName=zones[b['mapID']]['name'],
            boardingAccess='the nearby lift landing',arrivalAccess='the nearby lift landing',
            planningSeconds=row['estimatedSeconds'],waitAssumptionSeconds=row['waitSeconds'],
            rideEstimateSeconds=row['travelSeconds'],timingIsAssumption=True,arrivalExits=exits,arrivalExitMask=grid,path=[]))
    assert len(edges)==2 and edges[0]['a']==edges[1]['b'] and edges[0]['b']==edges[1]['a']
    return dict(version=1,build=audit['build'],sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),exitSourceSha256=hashlib.sha256(exit_source.read_bytes()).hexdigest(),exitMaskSourceSha256=hashlib.sha256(mask_source.read_bytes()).hexdigest(),edges=edges)


def literal(v):
    if isinstance(v,dict):return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in v.items())+'}'
    if isinstance(v,list):return '{'+','.join(literal(x) for x in v)+'}'
    if isinstance(v,bool):return str(v).lower()
    return json.dumps(v)


if __name__=='__main__':
    data=compile_data(ROOT/'tools/data/native-local-transports-70959.json')
    (ROOT/'Data/LocalTransports.lua').write_text('-- Native manual lift handoffs; see LocalTransports-SOURCES.md.\nlocal _,A=...\nA.LocalTransportData='+literal(data)+'\n',encoding='utf8')
    print('Manual lifts:',len(data['edges']),'directed links; tram withheld pending station verification')
