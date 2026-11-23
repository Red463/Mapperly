"""Generated walking geometry must match runtime inputs and fail closed when stale."""
from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
assert (root/'Data/WalkingPaths.lua').exists(),'ship the precomputed walking dataset'
manifest=json.loads((root/'tools/data/walking-paths-manifest.json').read_text())
for name,digest in manifest['inputs'].items():
 assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,'stale walking input: '+name
assert hashlib.sha256((root/'Data/WalkingPaths.lua').read_bytes()).hexdigest()==manifest['outputSha256']
l=LuaRuntime(unpack_returned_tuples=True);l.execute('A={}')
for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/WalkingPaths.lua','Roads.lua','Terrain.lua','PathReuse.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute("""
local total,modes=0,{}
for map,zone in pairs(A.WalkingPathData.zones) do for mode,group in pairs(zone) do
 local options={preferRoads=mode>0,roadPreferenceStrength=mode}
 assert(A.PathReuse.Signature(map,options)==group.signature,'stale generated terrain/road data')
 for key,entry in pairs(group.paths) do
  local path=entry.points;assert(#path>=2)
  local a,b=path[1],path[#path]
  assert(A.PathReuse.Key(a,b)==key)
  local before=A.PathReuse.Stats().bakedHits
  local result,length=A.Terrain.Path(a,b,options)
  assert(result and math.abs(length-entry.length)<.00001)
  assert(A.PathReuse.Stats().bakedHits==before+1,'generated path must be used without live search')
  assert(A.Terrain.Validate({points=result}),'all generated segments must remain terrain-permitted')
  total=total+1;modes[mode]=true
 end
end end
assert(total>100,'ship a useful set of actual connections')
for mode=0,5 do assert(modes[mode],'all six road modes must be covered') end
print('Validated generated walking paths',total)
""")
# Synthetic generated data tests exercise stale/corrupt inputs without expensive searches.
l.execute("""
A.PathReuse.Clear()
local map,zone=next(A.WalkingPathData.zones);local mode,group=next(zone);local key,entry=next(group.paths)
local a,b=entry.points[1],entry.points[#entry.points];local options={preferRoads=mode>0,roadPreferenceStrength=mode}
local before=A.PathReuse.Stats().bakedHits
local saved=group.signature;group.signature='stale'
local p=A.Terrain.Path(a,b,options);assert(A.PathReuse.Stats().bakedHits==before,'stale signature must fall back')
group.signature=saved;A.PathReuse.Clear()
local savedLength=entry.length;entry.length=-1
A.Terrain.Path(a,b,options);assert(A.PathReuse.Stats().bakedHits==before,'corrupt geometry must fall back')
entry.length=savedLength;A.PathReuse.Clear()
local savedPoints=entry.points;entry.points={17}
local ok=pcall(A.Terrain.Path,a,b,options)
assert(ok and A.PathReuse.Stats().bakedHits==before,'malformed baked points must fall back without throwing')
entry.points=savedPoints;A.PathReuse.Clear()
local q,why=A.Terrain.Path(a,b,{preferRoads=mode>0,roadPreferenceStrength=mode,maxDistance=0})
assert(not q and why=='too long','baked path must preserve distance bounds')
""")
print('PASS: generated source signatures, every terrain segment, six modes, stale/corrupt fallback and range bounds')
