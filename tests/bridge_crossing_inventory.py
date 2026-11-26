"""Inventory must preserve instances, unknown assets and mid-zone candidates."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from audit_bridges_and_crossings import placement_key, candidate_reasons, map_points, disposition, asset_info
assert placement_key(0,'wmo',7)!=placement_key(1,'wmo',7)
assert placement_key(0,'wmo',7)!=placement_key(0,'m2',7)
assert 'name' in candidate_reasons({'name':'OldBridge','bounds':[0,0,0,10,60,6]})
assert 'elongated-geometry' in candidate_reasons({'name':'unnamed','bounds':[0,0,0,8,60,5]})
assert 'road-water-overlap' in candidate_reasons({'roadWaterOverlap':True})
assert not candidate_reasons({'name':'rock','bounds':[0,0,0,8,8,20]})
assert disposition({'error':'missing'})=='unresolved'
zones=[dict(id=1,terrainMap=0,west=100,east=0,north=100,south=0)]
assert map_points(0,50,50,zones)==[dict(mapID=1,x=.5,y=.5)]
assert not map_points(1,50,50,zones)
class Missing:
    def read_fdid(self,fid):raise KeyError('unavailable')
assert 'error' in asset_info(Missing(),'wmo',123)
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
from build_bridge_batch import dry_point
l=LuaRuntime();l.execute('A={Terrain={Segment=function(a,b,options) assert(options.allowSwimming==false);return false end}}')
assert not dry_point(l,dict(mapID=1,x=.5,y=.5)), 'a failed dry check cannot become a truthy Python multi-return tuple'
import csv,json
manifest=json.loads((root/'tools/data/bridges-and-crossings-manifest.json').read_text())
assert len(manifest['maps'])==len({m['id'] for m in manifest['maps']})
assert len(manifest['candidates'])==len({p['key'] for p in manifest['candidates']})
assert manifest['sourceBuildMismatch'] and manifest['limits']
assert any(m['errors'] for m in manifest['maps']), 'unavailable native maps must remain visible'
assert any(p['sourceStatus']=='certified-corridor' and len(p['maps'])>0 for p in manifest['candidates'])
assert all(p['liveStatus']=='not-tested' for p in manifest['candidates']), 'offline proofs cannot claim live acceptance'
for p in manifest['candidates']:
    if p['sourceStatus']=='certified-corridor':assert p['proof'] and (root/'tools/data'/p['proof']).exists()
assert any(p['reasons']==['road-water-overlap'] for p in manifest['candidates']), 'discovery must reach beyond names and elongated bounds'
assert len(manifest['nonWalkingCrossings'])>=33,'transport and tram portal records must be individually accounted for'
assert len({r['id']for r in manifest['nonWalkingCrossings']})==len(manifest['nonWalkingCrossings'])
assert all(r['liveStatus']=='not-tested'and r['sourceSha256']and r.get('to')for r in manifest['nonWalkingCrossings'])
print('PASS: stable inventory identities, unnamed geometry candidates, missing assets and same-zone placement')
