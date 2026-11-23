"""Timbermaw branch floors must connect native zone-core services without new ground permission."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for file in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/file).read_text())
lua.execute('''
A.InitStore({})
local count=0
for _,edge in ipairs(A.CrossingData.edges) do
 local row=A.StructureData.corridors[edge.structure]
 if row and row.placement==372018 then
  count=count+1;assert(A.Structures.Get(edge))
  local a,b=A.WalkingRegions.Get(row.a),A.WalkingRegions.Get(row.b)
  assert(a and a>0 and b and b>0)
  for _,reverse in ipairs({false,true}) do
   local start,goal=reverse and row.b or row.a,reverse and row.a or row.b
   local plan,reason=A.Journey.Plan(start,goal,{});assert(plan,reason)
   assert(plan.legs[1].exitStructure==edge.structure)
   A.Journey.Install(plan);local path=A.Structures.Path(edge.structure,start);local travelled=0
   for i,w in ipairs(path) do
    if i>1 then travelled=travelled+A.TravelNetwork.Distance(path[i-1],w) end
    if i==1 or travelled>=5 or i==#path then
     local p=A.TravelNetwork.Transform(w,i>#path/2 and goal.mapID or start.mapID)
     p=p or A.TravelNetwork.Transform(w,start.mapID) or A.TravelNetwork.Transform(w,goal.mapID)
     assert(p);A.Journey.Update(p,true);travelled=0
    end
   end
   local _,why=A.Journey.Update(goal,true);assert(why=='arrived','Timbermaw follower must finish each branch in either direction')
  end
 end
end
assert(count==3,'all three source-supported Timbermaw branch pairs must be represented separately')
local blood=A.TravelNetwork.Transform({worldX=-337.2,worldY=5068.4,instance=1},1448)
local everlook=A.TravelNetwork.Transform({worldX=-4742.4,worldY=6799.2,instance=1},1452)
local result,reason;A.PlanningJob.Start(function() return A.Journey.Plan(blood,everlook,{preferRoads=true}) end,function(p) result=p end,function(r) reason=r end)
local steps=0
while A.PlanningJob.IsRunning() and steps<8000 do A.PlanningJob.Step();steps=steps+1 end
assert(result,reason or 'native zone-core route did not finish')
assert(result.multiZone and result.destinationMapID==1452)
local found=false
for _,leg in ipairs(result.legs) do
 assert(A.Terrain.Validate(leg));if leg.exitStructure and A.StructureData.corridors[leg.exitStructure].placement==372018 then found=true end
end
assert(found,'Bloodvenom Post to Everlook must traverse the native Timbermaw corridor')
print('Bloodvenom Post-Everlook:',#result.legs,'legs,',math.floor(result.distance),'yd,',steps,'planning steps')
local astranaar=A.TravelNetwork.Transform({worldX=-289.2,worldY=2827.3,instance=1},1440)
result=nil;reason=nil;steps=0
A.PlanningJob.Start(function() return A.Journey.Plan(astranaar,everlook,{preferRoads=true}) end,function(p) result=p end,function(r) reason=r end)
while A.PlanningJob.IsRunning() and steps<8000 do A.PlanningJob.Step();steps=steps+1 end
assert(result,reason or 'connected Ashenvale-Felwood-Winterspring journey did not finish')
assert(result.multiZone and #result.legs>=3)
for _,leg in ipairs(result.legs) do assert(A.Terrain.Validate(leg)) end
print('Astranaar-Everlook:',#result.legs,'legs,',math.floor(result.distance),'yd,',steps,'planning steps')
''')
print('PASS: all Timbermaw branch pairs, reverse following and real zone-core walking')
