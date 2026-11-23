"""A topology regression for the user's Duskwood -> Dun Morogh request."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={};assert(loadstring(...))("Mapperly",A)',(root/'Data/Crossings.lua').read_text())
lua.execute('''
local graph={}
for _,e in ipairs(A.CrossingData.edges) do
 graph[e.a.mapID]=graph[e.a.mapID] or {};graph[e.b.mapID]=graph[e.b.mapID] or {}
 graph[e.a.mapID][e.b.mapID]=true;graph[e.b.mapID][e.a.mapID]=true
end
local seen={[1431]=true};local queue={1431}
for _,map in ipairs(queue) do for nextMap in pairs(graph[map] or {}) do
 if not seen[nextMap] then seen[nextMap]=true;queue[#queue+1]=nextMap end
end end
assert(seen[1426],'Duskwood and Dun Morogh must be joined by data-backed walking connections')
''')
print('PASS: Duskwood and Dun Morogh walking topology is connected')
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI()')
for file in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/Structures.lua','Roads.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelNetwork.lua','Journey.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/file).read_text())
lua.execute('''
A.InitStore({preferRoads=true})
local a=assert(A.Terrain.Approach({mapID=1431,x=.77,y=.44},30))
local b=assert(A.Terrain.Approach({mapID=1426,x=.46,y=.51},30));b.name='Dun Morogh'
local result,reason;A.PlanningJob.Start(function() return A.Journey.Plan(a,b,{}) end,function(p) result=p end,function(r) reason=r end)
local steps=0
while A.PlanningJob.IsRunning() and steps<8000 do A.PlanningJob.Step();steps=steps+1 end
assert(result,reason or 'walking route did not finish')
assert(result.multiZone and result.destinationMapID==1426)
for _,leg in ipairs(result.legs) do assert(A.Terrain.Validate(leg)) end
print('Duskwood-Dun Morogh:',#result.legs,'legs,',math.floor(result.distance),'yd,',steps,'planning steps')
''')
