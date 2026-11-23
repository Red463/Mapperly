"""Native city thresholds must be actual floor corridors, not terrain shortcuts."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for file in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/file).read_text())
lua.execute('''
A.InitStore({})
for _,pair in ipairs({{1426,1455},{1420,1458}}) do
 local edge
 for _,e in ipairs(A.CrossingData.edges) do
  if e.a.mapID==pair[1] and e.b.mapID==pair[2] or e.a.mapID==pair[2] and e.b.mapID==pair[1] then edge=e;break end
 end
 assert(edge,'Missing native city walking connection '..pair[1]..' -> '..pair[2])
 local row=assert(A.Structures.Get(edge),'city entrances require a bound native floor proof')
 assert(row.worldPath and #row.worldPath>3)
 assert(A.WalkingRegions.Get(row.b)==1,'city anchor must join the existing main permitted ground region')
 assert(A.WalkingRegions.Get(row.a)==1,'city outdoor approach must join the existing main permitted ground region')
 for _,reverse in ipairs({false,true}) do
  local start,goal=reverse and row.b or row.a,reverse and row.a or row.b
  local plan,reason=A.Journey.Plan(start,goal,{})
  assert(plan,reason);assert(plan.multiZone)
  assert(plan.legs[1].exitStructure==edge.structure,'city passage must use its actual floor geometry')
  A.Journey.Install(plan);local path=A.Structures.Path(edge.structure,start);local travelled=0
  for i,w in ipairs(path) do
   if i>1 then travelled=travelled+A.TravelNetwork.Distance(path[i-1],w) end
   if i==1 or travelled>=5 or i==#path then
    local p=A.TravelNetwork.Transform(w,i>#path/2 and goal.mapID or start.mapID)
    p=p or A.TravelNetwork.Transform(w,start.mapID) or A.TravelNetwork.Transform(w,goal.mapID)
    assert(p,'floor must remain in the city or approach map bounds')
    local aim,why=A.Journey.Update(p,true);assert(aim or why=='arrived',why);travelled=0
   end
  end
  local _,why=A.Journey.Update(goal,true);assert(why=='arrived','city passage must finish in either direction')
 end
end
''')
print('PASS: native Ironforge and static Undercity sewer crossings, both directions, main-ground anchors')
