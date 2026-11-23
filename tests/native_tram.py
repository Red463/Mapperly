"""Native tram pins and floor certificates must match original sources."""
from pathlib import Path
import json,hashlib,sys,math,struct
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools/roads'))
from local_casc import LocalCasc
sys.path.insert(0,str(root/'tools'))
from build_roads import chunks
from build_services import CACHE,WORLD
proof=json.loads((root/'tools/data/native-tram-service-70959.json').read_text())
assert hashlib.sha256((CACHE/WORLD).read_bytes()).hexdigest()==proof['sourceSha256']
assert len(proof['templates'])==len(proof['spawns'])==6
assert all(t['type']==11 and t['name']=='Subway'for t in proof['templates'])
assert all(s['instance']==369 for s in proof['spawns'])
assert {r['a']['mapID']for r in proof['edges']}=={1453,1455}
assert proof['nativeCycleMS']==143333
exits=json.loads((root/'tools/data/native-tram-exits-70959.json').read_text())
assert hashlib.sha256((root/'tools/data/native-tram-exits-70959.json').read_bytes()).hexdigest()==proof['floorSourceSha256']
casc=LocalCasc(root.parent/'output/forever-datamine-70959')
for row in exits['exits']:
 raw=casc.read_fdid(row['nativeRootFileDataID']);assert hashlib.sha256(raw).hexdigest()==row['rootSha256']
 raw=casc.read_fdid(row['nativeGroupFileDataID']);assert hashlib.sha256(raw).hexdigest()==row['groupSha256']
 a,b=next((a,b)for t,a,b in chunks(raw)if t=='MOGP')
 gc={t:raw[s:e]for t,s,e in chunks(raw,a+68,b)}
 vertices=list(struct.iter_unpack('<3f',gc['MOVT']));indices=list(struct.iter_unpack('<3H',gc['MOVI']))
 assert [list(vertices[i])for i in indices[row['triangle']]]==row['localVertices']
 assert abs(row['groundHeight']-row['z'])<.001
 assert row['heightError']<.001
print('PASS: native Subway spawn/template identity, both paired directions and original hashed WMO exit triangles')
