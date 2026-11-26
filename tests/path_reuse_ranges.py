"""A reusable detour is not proof that a shorter distance-bounded path fails."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute((ROOT / 'tests/wow.lua').read_text())
lua.execute('fakeUI(); A={}; calls=0; clears=0')
for name in ['Roads.lua', 'Terrain.lua', 'PlanningJob.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
lua.execute("""
A.TerrainData={version=1,zones={[1]={status='complete',w=6,h=6,widthYards=100,heightYards=100,rows={'/','/','/','/','/','/'}}}}
A.RoadData={version=1,zones={[1]={w=6,h=6,widthYards=100,heightYards=100,roadCells=1,rows={'A','A','A','A','A','A'}}}}
a={mapID=1,x=.1,y=.5};b={mapID=1,x=.9,y=.5}
local original=A.Terrain.Path;A.Terrain.Path=function(...) calls=calls+1;return original(...) end
local clear=A.Terrain.ClearPathCache;A.Terrain.ClearPathCache=function() clears=clears+1;return clear() end
function search(options)
 local path,length,progress
 A.PlanningJob.Start(function()
  path,length=A.Terrain.Path(a,b,options);progress=A.PlanningJob.Progress();return path,length
 end)
 while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
 assert(progress.paths==1,'a bounded retry must count as one path attempt')
 return path,length
end
""")
lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / 'PathReuse.lua').read_text())
lua.execute("""
local options={preferRoads=true,roadPreferenceStrength=5}
local signature,mode=A.PathReuse.Signature(1,options)
local pair=A.PathReuse.Key(a,b)
local detour={a,{mapID=1,x=.1,y=.9},{mapID=1,x=.9,y=.9},b}
assert(A.Terrain.Validate({points=detour}))
A.WalkingPathData={version=1,revision=1,zones={[1]={[mode]={signature=signature,paths={[pair]={points=detour,length=160}}}}}}
local path,length=search(options)
assert(path and length==160 and calls==0,'fixture must load the verified reusable detour')
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=100,maxExpansions=0})
assert(not path and length=='budget' and calls==1,'an over-limit reusable detour must trigger a bounded core search')
assert(clears==1,'the bounded search must clear the old unrestricted inner cache')
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=100,maxExpansions=0})
assert(not path and length=='budget' and calls==1,'the bounded failure can reuse its exact range and allowance')
path,length=search(options)
assert(path and length==160 and calls==1,'a bounded failure must preserve valid unrestricted geometry')
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=100,maxExpansions=1000})
assert(path and math.abs(length-80)<.000001 and calls==2,'a larger bounded allowance must find the in-range straight path')
assert(A.Terrain.Validate({points=path}))
path,length=search(options)
assert(path and length==160 and calls==2,'bounded success must preserve the unrestricted cached route')
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=50,maxExpansions=1000})
assert(not path and length=='too long' and calls==3,'a genuinely shorter-than-direct limit must still fail')
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=200,maxExpansions=0})
assert(path and length==160 and calls==3,'bounded failure cannot poison a broader range')
assert(clears==3)
A.PathReuse.Clear()
path,length=search({preferRoads=true,roadPreferenceStrength=5,maxDistance=100,maxExpansions=1000})
assert(path and math.abs(length-80)<.000001 and calls==4,'a cold baked detour must also trigger the bounded core search')
path,length=search(options)
assert(path and length==160 and calls==4,'a cold bounded retry must retain its verified baked route')
""")
print('PASS: cached and baked detours trigger isolated bounded retries, preserve unrestricted geometry and respect genuine distance limits')
