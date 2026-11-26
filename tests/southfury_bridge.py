"""Real Southfury bridge geometry must connect both banks without opening the ravine."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for name in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
A.InitStore({})
local row=A.StructureData.corridors[294532]
assert(row,'Southfury bridge is missing from the verified native floor network')
for _,reverse in ipairs({false,true}) do
 local a,b=reverse and row.b or row.a,reverse and row.a or row.b
 local plan,why=A.Journey.Plan(a,b,{walkingOnly=true,maxWalkingCells=20000})
 assert(plan,why)
 assert(plan.legs[1].exitStructure==294532,'use the bridge rather than a distant terrain crossing')
 assert(plan.distance<61,'bank-to-bank bridge route must remain local')
 A.Journey.Install(plan)
 local path=A.Structures.Path(294532,a)
 for i=1,#path,20 do
  local p=A.Structures.Aim(path[i],i>#path/2 and b.mapID or a.mapID)
  local aim,reason=A.Journey.Update(p,true)
  assert(aim or reason=='arrived',reason)
 end
 A.Journey.Update(b,true)
 local _,reason=A.Journey.Update(b,true);assert(reason=='arrived')
end
local middle=row.worldPath[181]
local p=A.Structures.Aim({worldX=middle[1],worldY=middle[2],instance=1},1447)
assert(not A.Terrain.Segment(p,p),'ravine terrain must stay blocked')
assert(A.Structures.Contains(p,294532),'native bridge deck must be recognized')
local nearby=row.worldPath[185]
local q=A.Structures.Aim({worldX=nearby[1],worldY=nearby[2],instance=1},1447)
for _,reverse in ipairs({false,true}) do
 local plan,why=A.Journey.Plan(reverse and q or p,reverse and p or q,{walkingOnly=true,maxWalkingCells=20000})
 assert(plan,why);assert(plan.distance<1.01,'nearby deck endpoints must not detour to a bank and back')
end
for _,goal in ipairs({row.a,row.b}) do
 local plan,why=A.Journey.Plan(p,goal,{walkingOnly=true,maxWalkingCells=20000})
 assert(plan,why)
 assert(plan.distance<52,'starting on the bridge must use the nearest partial deck path')
 A.Journey.Install(plan)
 local floor=plan.legs[1].exitPath
 assert(floor,'partial start must follow the bridge deck')
 local aim=A.Journey.Update(p,true)
 assert(A.Journey.crossing and A.Journey.inStructure==294532 and aim and aim.mapID,'partial-deck start must enter the floor follower immediately')
 for i=1,#floor,15 do
  local q=A.Structures.Aim(floor[i],goal.mapID)
  local aim,reason=A.Journey.Update(q,true);assert(aim or reason=='arrived',reason)
 end
 A.Journey.Update(goal,true)
 local _,reason=A.Journey.Update(goal,true);assert(reason=='arrived','partial-deck start must finish on the bank')
 local back,reason=A.Journey.Plan(goal,p,{walkingOnly=true,maxWalkingCells=20000})
 assert(back,reason);assert(back.distance<52)
 A.Journey.Install(back)
 local floor=back.legs[1].exitPath
 for i=1,#floor,15 do A.Journey.Update(A.Structures.Aim(floor[i],goal.mapID),true) end
 A.Journey.Update(p,true)
 local _,reason=A.Journey.Update(p,true);assert(reason=='arrived','partial-deck destination must finish on the deck')
end
local approach={mapID=1440,x=.95,y=.486}
local departure={mapID=1447,x=.12,y=.75}
for _,reverse in ipairs({false,true}) do
 local plan,reason=A.Journey.Plan(reverse and departure or approach,reverse and approach or departure,{walkingOnly=true,maxWalkingCells=50000})
 assert(plan,reason)
 local bridge=false;for _,leg in ipairs(plan.legs) do bridge=bridge or leg.exitStructure==294532 end
 assert(bridge,'nearby outdoor approaches must connect through the Southfury bridge')
end
UnitPosition=function() return middle[2],middle[1],middle[3]-20,1 end
assert(not A.Structures.Contains(p,294532),'position beneath the bridge must not borrow deck permission')
assert(not A.Journey.Plan(p,row.b,{walkingOnly=true,maxWalkingCells=100}), 'under-bridge start must remain rejected')
UnitPosition=nil
assert(not A.Structures.Contains({worldX=middle[1],worldY=middle[2],instance=0},294532),'another continent cannot borrow bridge floor')
assert(not A.Structures.Access({worldX=middle[1],worldY=middle[2],instance=0}),'wrong-instance access must reject without crashing')
''')
print('PASS: Southfury native bridge, both directions, partial deck endpoints and ravine exclusion')
