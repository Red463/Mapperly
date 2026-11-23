"""Build-backed Great Lift plans/following and independent unavailable tram policy."""
from pathlib import Path
import hashlib
import importlib.util
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
spec=importlib.util.spec_from_file_location('local_builder',root/'tools/build_local_transports.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
source=root/'tools/data/native-local-transports-70959.json'
data=builder.compile_data(source)
assert data['sourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua',
          'Data/Structures.lua','Data/LocalTransports.lua','Terrain.lua','Structures.lua','WalkingRegions.lua',
          'PlanningJob.lua','TravelNetwork.lua','Transports.lua','Journey.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
assert lua.globals().A.LocalTransportData.sourceSha256==data['sourceSha256']
assert lua.globals().A.LocalTransportData.exitSourceSha256==data['exitSourceSha256']
assert lua.globals().A.LocalTransportData.exitMaskSourceSha256==data['exitMaskSourceSha256']
lua.execute('''
A.InitStore({});local T,J=A.Transports,A.Journey
assert(T.HasMethod('lift') and not T.HasMethod('tram'))
assert(#T.Edges({})==2,'both verified directions must be available without faction assumptions')
for _,row in ipairs(A.LocalTransportData.edges) do
 local plan,reason=J.Plan(row.a,row.b,{})
 assert(plan,reason);assert(plan.hasTransports)
 local lift
 for _,leg in ipairs(plan.legs) do if leg.transport then lift=leg;break end end
 assert(lift and lift.transport.kind=='lift' and lift.name:find('Lift:',1,true))
 assert(lift.transport.id==row.id and lift.estimatedSeconds==120)
 for _,point in ipairs(lift.points) do assert(point.breakBefore,'unproven moving-platform geometry must not be drawn as a line') end
 J.Install(plan)
 local x,y=A.TravelNetwork.World(row.a)
 UnitPosition=function() return y,x,row.boardingGroundHeight,1 end
 J.Update(row.a,true);assert(J.Leg().kind=='transport')
 assert(J.transportState.boardingSeen)
 UnitPosition=function() return y,x,(row.boardingGroundHeight+row.arrivalGroundHeight)/2,1 end
 J.Update(row.a,true);assert(J.transportState.departed)
 J.Update(nil,true);assert(J.active==plan,'missing lift position must not stop navigation')
 x,y=A.TravelNetwork.World(row.b)
 UnitPosition=function() return y,x,row.arrivalGroundHeight,1 end
 local _,done=J.Update(row.b,true)
 if done~='arrived' then _,done=J.Update(row.b,true) end
 assert(done=='arrived','both vertical directions must hand off on the verified dry destination')
 -- The client may never expose a readable source/ride sample. Recover at land.
 J.Install(plan);UnitPosition=nil
 J.Update(row.a,true);J.Update(nil,true)
 UnitPosition=function() return y,x,row.arrivalGroundHeight,1 end
 _,done=J.Update(row.b,true)
 if done~='arrived' then _,done=J.Update(row.b,true) end
 assert(done=='arrived','missing boarding samples must not trap either real lift direction')
end
A.db.useLifts=false;assert(#T.Edges({})==0)
A.db.useLifts=true;A.LocalTransportData.build=0;assert(#T.Edges({})==0,'stale local data must be excluded independently')
''')
print('PASS: native local source validation, both Great Lift plans/followers, loading and saved method filtering')
