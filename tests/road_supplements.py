"""Pinned native WMO supplement is reproducible and rejects stale base bindings."""
from pathlib import Path
import copy,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'.test-deps'))
from build_road_supplements import build,decode,lua
source=ROOT/'tools/data/native-road-supplements-70959.json';proof=json.loads(source.read_text());zones=build(proof);z=zones[1453];sw=next(i for i,p in enumerate(proof['zones'])if p['mapID']==1453)
assert (z['baseRoadCells'],z['addedCells'],z['roadCells'],z['nativeTriangles'])==(2028,3586,5614,2360)
assert z['nativeStreetTriangles']==2349 and z['nativeDockTriangles']==11
assert set(zones)=={1413,1424,1434,1437,1438,1444,1453}
for mid,other in zones.items():
 assert all(b>=a for a,b in zip(decode({**other,'rows':other['baseRows']}),decode(other)))
 assert other['roadCells']-other['baseRoadCells']==other['addedCells']
 assert hashlib.sha256(decode(other)).hexdigest()==other['maskSha256']
assert hashlib.sha256(decode(z)).hexdigest()==z['maskSha256']
base=decode({**z,'rows':z['baseRows']});merged=decode(z)
assert all(b>=a for a,b in zip(base,merged)), 'supplement must preserve every original road cell'
for field in('baseMaskSha256','terrainMaskSha256'):
 bad=copy.deepcopy(proof);bad['zones'][0][field]='0'*64
 try:build(bad)
 except ValueError:pass
 else:raise AssertionError('stale binding accepted: '+field)
bad=copy.deepcopy(proof);bad['zones'][sw]['triangles'][0]['flags']=4
try:build(bad)
except ValueError:pass
else:raise AssertionError('noncollidable triangle accepted')
bad=copy.deepcopy(proof);bad['zones'][sw]['staticDockFloor']['minimumHeadroom']=1
try:build(bad)
except ValueError:pass
else:raise AssertionError('uncertified dock floor accepted')
bad=copy.deepcopy(proof);bad['zones'][0]['nativeDockFloors'][0]['triangles'][0]['v'][0][0]+=1000
try:build(bad)
except ValueError:pass
else:raise AssertionError('dock floor beyond vessel distance bound accepted')
expected='-- Native WMO street preference supplement; see RoadsSupplement-SOURCES.md.\nlocal _,A=...\nA.RoadSupplementData='+lua({'version':1,'build':70959,'proofSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'zones':zones})+'\n'
assert (ROOT/'Data/RoadsSupplement.lua').read_text()==expected,'generated artifact is stale'
print('PASS: seven native street/dock preference unions, exact provenance, bounded dock permissions, stale-data rejection and reproducible Lua')
