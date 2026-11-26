"""Budget exhaustion is reusable work, scoped to the search that exhausted it."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / '.test-deps'))
from lupa.lua51 import LuaRuntime


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((root / 'tests/wow.lua').read_text())
    lua.execute('fakeUI(); A={}; actualCalls=0')
    for name in ['Roads.lua', 'Water.lua', 'Terrain.lua', 'PlanningJob.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)', (root / name).read_text())
    lua.execute("""
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
function encode(cells)
 local row={}
 for first=1,#cells,6 do
  local bits=0
  for offset=0,5 do if cells[first+offset] then bits=bits+2^(5-offset) end end
  row[#row+1]=alphabet:sub(bits+1,bits+1)
 end
 return table.concat(row)
end
function makeZone()
 local z={status='complete',maskSha256='source',w=80,h=80,widthYards=800,heightYards=800,rows={}}
 for y=1,80 do
  local cells={};for x=1,80 do cells[x]=x~=40 or y==79 end
  z.rows[y]=encode(cells)
 end
 return z
end
A.TerrainData={version=1,zones={[1]=makeZone()}}
a={mapID=1,x=.1,y=.1}; b={mapID=1,x=.9,y=.1}
local original=A.Terrain.Path
A.Terrain.Path=function(...) actualCalls=actualCalls+1;return original(...) end
function search(first,last,options)
 local path,reason,progress
 A.PlanningJob.Start(function()
  path,reason=A.Terrain.Path(first,last,options)
  progress=A.PlanningJob.Progress();return path,reason
 end)
 local slices=0
 while A.PlanningJob.IsRunning() do A.PlanningJob.Step();slices=slices+1;assert(slices<100) end
 return path,reason,progress
end
function failure(first,last,options)
 local path,reason,progress=search(first,last,options)
 assert(not path and reason=='budget','fixture must exhaust only its search allowance: '..tostring(reason))
 assert(progress.paths==1,'cached attempts still count as one walking path')
 return progress
end
""")
    lua.execute('assert(loadstring(...))("Mapperly",A)', (root / 'PathReuse.lua').read_text())
    return lua


lua = runtime()
lua.execute("""
local first=failure(a,b,{maxExpansions=512})
assert(first.cells==512,'the fixture must spend the requested allowance')
local again=failure(a,b,{maxExpansions=512})
assert(actualCalls==1,'repeating a budget failure must not perform the same terrain search')
assert(again.cells==0,'reused failures must not report searched cells')
assert(failure(a,b,{budget=128}).cells==0 and actualCalls==1,'a smaller allowance can reuse the exhausted larger allowance')
assert(failure(a,b,{maxExpansions=511.9,budget=262144}).cells==0 and actualCalls==1,'effective floor and maxExpansions precedence apply')
local invalid,why=search(a,b,{maxExpansions=-1})
assert(not invalid and why=='invalid budget','failure reuse cannot hide invalid options')
assert(actualCalls==2)
local path=assert(search(a,b,{maxExpansions=262144}))
assert(actualCalls==3,'a larger allowance must retry and solve the detour')
assert(A.Terrain.Validate({mapID=1,points=path}),'the solved path must remain valid terrain geometry')
assert(search(a,b,{maxExpansions=1}),'known successful geometry takes priority over an older budget failure')
assert(actualCalls==3)
local short,reason=search(a,b,{maxExpansions=1,maxDistance=500})
assert(not short and reason=='too long','successful reuse must preserve the distance guard')
assert(A.PathReuse.Stats().failureHits==3,'failure reuse has a separate hit counter')
""")
print('PASS: repeated and lower-budget failures reuse work, progress stays honest, larger budgets solve, success wins')

lua = runtime()
lua.execute("""
failure(a,b,{maxExpansions=0,maxDistance=1000})
failure(a,b,{maxExpansions=0,maxDistance=1000});assert(actualCalls==1)
failure(a,b,{maxExpansions=0,maxDistance=1100});assert(actualCalls==2,'a broader search range must retry')
failure(a,b,{maxExpansions=0});assert(actualCalls==3,'unrestricted search must retry')
failure(b,a,{maxExpansions=0});assert(actualCalls==4,'budget-limited A* order cannot assume reverse symmetry')
failure({mapID=1,x=.10000000000001,y=.1},b,{maxExpansions=0})
assert(actualCalls==5,'distinct exact endpoints must retry')
local path,reason=search(a,b,{maxExpansions=0,maxDistance=100})
assert(not path and reason=='too long','range rejection still takes precedence over a budget failure')
A.PathReuse.Clear();failure(a,b,{maxExpansions=0})
assert(actualCalls==7,'clear must discard failed attempts')
for i=1,600 do failure({mapID=1,x=.05+i/100000,y=.1},b,{maxExpansions=0}) end
local stats=A.PathReuse.Stats()
assert(stats.failureEntries<=512,'failed attempts must have bounded memory')
local before=actualCalls;failure(a,b,{maxExpansions=0})
assert(actualCalls==before+1,'eviction must retry safely')
""")
print('PASS: exact range, direction and endpoints isolate failures; clear and bounded eviction retry safely')

lua = runtime()
lua.execute("""
failure(a,b,{maxExpansions=0})
A.TerrainData.zones[1].rows[2]=A.TerrainData.zones[1].rows[79]
failure(a,b,{maxExpansions=0});assert(actualCalls==2,'terrain edits must retry')
A.TerrainData.zones[1].groundRows={}
-- Ground corrections are resolved through Terrain.Zone, including in-place rows.
local z=A.TerrainData.zones[1]
A.GroundCorrectionData={version=1,zones={[1]={baseSha256='source',w=80,h=80,rows={}}}}
for i=1,80 do A.GroundCorrectionData.zones[1].rows[i]=string.rep('A',14) end
failure(a,b,{maxExpansions=0});assert(actualCalls==3)
A.GroundCorrectionData.zones[1].rows[3]='g'..string.rep('A',13)
failure(a,b,{maxExpansions=0});assert(actualCalls==4,'ground edits must retry')
A.RoadData={version=1,zones={[1]={w=80,h=80,widthYards=800,heightYards=800,roadCells=1,rows={}}}}
for i=1,80 do A.RoadData.zones[1].rows[i]=string.rep('A',14) end
failure(a,b,{maxExpansions=0,preferRoads=true,roadPreferenceStrength=3});assert(actualCalls==5)
A.RoadData.zones[1].rows[3]='g'..string.rep('A',13)
failure(a,b,{maxExpansions=0,preferRoads=true,roadPreferenceStrength=3});assert(actualCalls==6,'road edits must retry')
failure(a,b,{maxExpansions=0,preferRoads=true,roadPreferenceStrength=4});assert(actualCalls==7,'road cost policy must retry')
A.WaterData={version=1,zones={[1]={baseSha256='source',w=80,h=80,rows={}}}}
for i=1,80 do A.WaterData.zones[1].rows[i]=string.rep('/',14) end
failure(a,b,{maxExpansions=0,allowSwimming=false});assert(actualCalls==8,'swimming policy must retry')
A.WaterData.zones[1].rows[3]='f'..string.rep('/',13)
failure(a,b,{maxExpansions=0,allowSwimming=false});assert(actualCalls==9,'water edits must retry')
for map=2,20 do
 A.TerrainData.zones[map]=makeZone()
 failure({mapID=map,x=.1,y=.1},{mapID=map,x=.9,y=.1},{maxExpansions=0})
end
assert(A.PathReuse.Stats().contexts<=16)
local before=actualCalls;failure(a,b,{maxExpansions=0,allowSwimming=false})
assert(actualCalls==before+1,'evicted contexts cannot retain stale failure entries')
""")
print('PASS: terrain, ground, roads, road costs, swimming and water changes invalidate failures')

lua = runtime()
lua.execute("""
failure(a,b,{maxExpansions=0})
A.WalkingPortalData={version=1,stride=12,zones={}}
failure(a,b,{maxExpansions=0})
assert(actualCalls==2,'replacing compiled guide data must retry a prior failure')
failure(a,b,{maxExpansions=0});assert(actualCalls==2,'unchanged compiled guide data can reuse the failure')
A.WalkingPortalData={version=1,stride=12,zones={}}
failure(a,b,{maxExpansions=0})
assert(actualCalls==3,'guide identity changes must invalidate the failure even when the terrain mask is unchanged')
""")
print('PASS: compiled walking-guide identity scopes failure reuse')
