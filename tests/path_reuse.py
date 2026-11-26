"""Cross-zone reuse, option isolation, source invalidation and bounded storage."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True)
l.execute("A={}; calls=0")
l.execute("""
A.TerrainData={version=1,zones={}}
for i=1,3 do A.TerrainData.zones[i]={status='complete',w=4,h=4,widthYards=100,heightYards=100,rows={'8','8','8','8'}} end
A.Roads={Strength=function(s) return s or 3,'',1+(s or 3)/10 end,Zone=function(map) return A.road end}
A.Terrain={Zone=function(map) return A.TerrainData.zones[map] end,
 Segment=function(a,b) return not A.blocked end,
 Path=function(a,b,o)
  calls=calls+1
  if o and o.maxDistance and o.maxDistance<10 then return nil,'too long' end
  return {{mapID=a.mapID,x=a.x,y=a.y},{mapID=b.mapID,x=b.x,y=b.y}},10
 end}
""")
assert (root/'PathReuse.lua').exists(),'PathReuse runtime must exist'
l.execute('assert(loadstring(...))("Mapperly",A)',(root/'PathReuse.lua').read_text())
l.execute("""
local function p(map,x) return {mapID=map,x=x or .1,y=.5} end
local a,b=p(1),p(1,.9)
assert(A.Terrain.Path(a,b));assert(calls==1)
assert(A.Terrain.Path(p(2),p(2,.9)));assert(calls==2)
local points=assert(A.Terrain.Path(a,b));assert(calls==2,'changing zones must retain previous results')
points[1].x=.42;points[2].x=.43
local reverse=assert(A.Terrain.Path(b,a));assert(reverse[1].x==.9 and reverse[2].x==.1 and calls==2,'cached geometry must be copied and reversible')
A.road={rows={'8','8','8','8'},w=4,h=4,widthYards=100,heightYards=100}
assert(A.Terrain.Path(a,b,{preferRoads=true,roadPreferenceStrength=4}));assert(calls==3)
A.road={rows={'8','8','8','8'},w=4,h=4,widthYards=100,heightYards=100}
assert(A.Terrain.Path(a,b,{preferRoads=true,roadPreferenceStrength=4}));assert(calls==4)
assert(A.Terrain.Path(a,b,{preferRoads=true,roadPreferenceStrength=5}));assert(calls==5)
assert(A.Terrain.Path(a,b,{preferRoads=true,roadPreferenceStrength=4}));assert(calls==5,'road-strength contexts must survive switching')
A.road.rows[2]='4';assert(A.Terrain.Path(a,b,{preferRoads=true,roadPreferenceStrength=4}));assert(calls==6,'road edits invalidate reuse')
A.TerrainData.zones[1].rows[1]='4';assert(A.Terrain.Path(a,b));assert(calls==7,'terrain edits invalidate reuse')
A.TerrainData.zones[1].groundRows={'4'};assert(A.Terrain.Path(a,b));assert(calls==8,'ground edits invalidate reuse')
local q,why=A.Terrain.Path(a,b,{maxDistance=5});assert(not q and why=='too long','range bounds still apply to hits')
assert(A.Terrain.Path(a,b));assert(calls==9,'a separate bounded retry cannot poison unlimited result')
A.blocked=true;assert(A.Terrain.Path(a,b));assert(calls==10,'invalid cached segments must fall back')
A.blocked=false
for i=1,700 do assert(A.Terrain.Path(p(2,i/1000),p(2,.99))) end
local s=A.PathReuse.Stats();assert(s.entries<=512 and s.points<=16384 and s.contexts<=16,'retained live geometry must be bounded')
print('reuse stats',s.hits,s.entries,s.points,s.contexts)
""")
print('PASS: cross-zone/mode reuse, copied reverse paths, mutable source isolation, range semantics and bounded cache')

# Exercise the original inner terrain cache too, not just a call-count double.
r=LuaRuntime(unpack_returned_tuples=True);r.execute('A={}')
for name in ['Roads.lua','Terrain.lua','PathReuse.lua']:
 r.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
r.execute("""
A.TerrainData={version=1,zones={[1]={status='complete',w=6,h=6,widthYards=600,heightYards=600,rows={'/','/','/','/','/','/'}}}}
local road={w=6,h=6,widthYards=600,heightYards=600,roadCells=6,rows={'A','A','/','A','A','A'}}
A.RoadData={version=1,zones={[1]=road}}
local a,b={mapID=1,x=.08,y=.58},{mapID=1,x=.92,y=.58}
local options={preferRoads=true,roadPreferenceStrength=5,maxExpansions=262144}
assert(A.Terrain.Path(a,b,options))
road.rows[3]='A';road.rows[5]='/'
local path=assert(A.Terrain.Path(a,b,options));local lower=false
for _,p in ipairs(path) do if p.y>.7 then lower=true end end
assert(lower,'an inner cache hit cannot retain roads removed in place')
A.TerrainData.zones[1]={status='complete',w=6,h=6,widthYards=600,heightYards=600,maskSha256='base',rows={'A','A','A','h','A','A'}}
A.GroundCorrectionData={version=1,zones={[1]={baseSha256='base',w=6,h=6,rows={'/','/','/','/','/','/'}}}}
road.rows={'A','A','A','A','A','A'};road.roadCells=1
assert(A.Terrain.Path(a,b,options))
for i=1,6 do A.GroundCorrectionData.zones[1].rows[i]='A' end
local blocked=A.Terrain.Path(a,b,options)
assert(not blocked,'removed ground corrections cannot leak an inner cached path through blocked terrain')
local checkpoints=0;A.Terrain.Checkpoint=function() checkpoints=checkpoints+1 end
A.TerrainData.zones[2]={status='complete',w=600,h=600,widthYards=600,heightYards=600,rows={}}
for i=1,600 do A.TerrainData.zones[2].rows[i]=string.rep('/',100) end
A.PathReuse.Signature(2,{})
assert(checkpoints>=7,'cold content hashing must cooperate with the planner')
""")
print('PASS: actual inner-cache ground/road mutation regressions and cooperative cold hashing')
