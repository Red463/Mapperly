"""Exact final work accounting and cooperative validation of reusable geometry."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow.lua').read_text())
    lua.execute('fakeUI(); A={}')
    for name in ['Roads.lua', 'TerrainPortals.lua', 'Terrain.lua', 'PlanningJob.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
    lua.execute("""
function zone(width)
 local rows={string.rep('/',math.ceil(width/6))}
 A.TerrainData={version=1,zones={[1]={status='complete',w=width,h=1,widthYards=width*10,heightYards=10,maskSha256='base',rows=rows}}}
 A.RoadData={version=1,zones={[1]={w=width,h=1,widthYards=width*10,heightYards=10,roadCells=width,rows=rows}}}
 a={mapID=1,x=.5/width,y=.5};b={mapID=1,x=(width-.5)/width,y=.5}
end
function run(options)
 local path,reason,progress;local steps=0
 A.PlanningJob.Start(function()
  path,reason=A.Terrain.Path(a,b,options);progress=A.PlanningJob.Progress();return path,reason
 end)
 while A.PlanningJob.IsRunning() do A.PlanningJob.Step();steps=steps+1;assert(steps<100) end
 assert(progress.paths==1,'one attempt must retain one path progress entry')
 return path,reason,progress,steps
end
""")
    return lua


lua = runtime()
lua.execute("""
zone(6)
local counts={}
local path,length,progress=run({preferRoads=true,maxExpansions=100,yield=function(count) counts[#counts+1]=count end})
assert(path and math.abs(length-50)<.000001)
assert(progress.cells==5,'five expanded fine cells below256 must be reported exactly')
assert(#counts==1 and counts[1]==5,'the caller must receive the final five-cell work count once')
A.Terrain.ClearPathCache();counts={}
path,length,progress=run({preferRoads=true,maxExpansions=3,yield=function(count) counts[#counts+1]=count end})
assert(not path and length=='budget')
assert(progress.cells==3 and #counts==1 and counts[1]==3,'a three-cell exhausted allowance must be reported exactly')
counts={};A.Terrain.ClearPathCache()
path,length,progress=run({yield=function(count) counts[#counts+1]=count end})
assert(path and progress.cells==0 and #counts==0,'a clear straight fast path must retain zero expansion work')
""")
print('PASS: exact fine-grid success and budget counts below256, with zero-work fast paths preserved')

lua = runtime()
lua.execute("""
zone(120)
-- Ten one-component tiles, each joined to the next by its sole horizontal
-- portal at offset0. The last tile has no outgoing portal record.
A.WalkingPortalData={version=1,stride=12,zones={[1]={w=120,h=1,maskSha256='base',rows={string.rep('BAACB',9)..'A'}}}}
local original=A.TerrainPortals.Trace;local guided=0
A.TerrainPortals.Trace=function(z,map,sx,sy,ex,ey,factor,cell,push,pop,charge)
 return original(z,map,sx,sy,ex,ey,factor,cell,push,pop,function() guided=guided+1;return charge() end)
end
local counts={}
local path,length,progress=run({preferRoads=true,maxExpansions=16384,yield=function(count) counts[#counts+1]=count end})
assert(path and A.Terrain.Validate({points=path}))
assert(guided==9,'the actual portal graph must expand its nine non-goal tile states')
assert(progress.cells==119,'nine coarse states and ten eleven-cell refinements must count119 actual expansions')
assert(#counts==1 and counts[1]==119,'guided final work below256 must reach the caller exactly once')
""")
print('PASS: actual compiled portal search and fine refinement report their complete shared work')

lua = runtime()
lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / 'PathReuse.lua').read_text())
lua.execute("""
zone(6)
local path={}
for i=0,256 do path[#path+1]={mapID=1,x=a.x+(b.x-a.x)*i/256,y=.5} end
local signature,mode=A.PathReuse.Signature(1,{})
local pair=A.PathReuse.Key(a,b)
A.WalkingPathData={version=1,revision=1,zones={[1]={[mode]={signature=signature,paths={[pair]={points=path,length=50}}}}}}
local baked,length,progress,coldSteps=run({})
assert(baked and progress.cells==0)
assert(coldSteps>=2,'many short baked segments must yield during geometry validation')
local warm,warmLength,warmProgress,warmSteps=run({})
assert(warm and warmLength==length and warmProgress.cells==0)
assert(warmSteps>=2,'many short warm-cache segments must yield during their live validation')
local hits=A.PathReuse.Stats().hits
A.PlanningJob.Start(function() return A.Terrain.Path(a,b,{}) end)
A.PlanningJob.Step();assert(A.PlanningJob.IsRunning(),'the cache validation must remain cancellable while yielded')
A.PlanningJob.Cancel();A.PlanningJob.Step()
assert(not A.PlanningJob.IsRunning() and A.PathReuse.Stats().hits==hits,'cancelling yielded validation must stop before consuming the cached result')
""")
print('PASS: baked and warm geometry validation yield, retain zero searched cells and remain cancellable')
