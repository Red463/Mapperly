"""Multi-hop walking, verified connector geometry and boundary handoff."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for name in ['Store.lua','Terrain.lua','PlanningJob.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
 if (root/name).exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
A.InitStore({});assert(A.TravelNetwork,'cross-zone planner must exist')
A.TerrainData={version=1,zones={}}
for i=1,3 do A.TerrainData.zones[i]={status='complete',w=4,h=4,widthYards=100,heightYards=100,rows={'8','8','8','8'}} end
A.CrossingData={version=1,maps={
 [1]={name='West',west=100,north=100,width=100,height=100,instance=0},
 [2]={name='Middle',west=50,north=100,width=100,height=100,instance=0},
 [3]={name='East',west=0,north=100,width=100,height=100,instance=0}},edges={
 {id=1,a={mapID=1,x=.75,y=.5},b={mapID=2,x=.3,y=.5},distance=5},
 {id=2,a={mapID=2,x=.75,y=.5},b={mapID=3,x=.3,y=.5},distance=5}}}
local function p(map,x,y) return {mapID=map,x=x,y=y or .5} end
local plan,why=A.Journey.Plan(p(1,.1),p(3,.9),{})
assert(plan,why);assert(plan.multiZone and #plan.legs==3 and #plan.points>=6)
assert(math.abs(plan.distance-180)<.001,'distance must include local legs and crossing connectors')
local sum=0;for _,leg in ipairs(plan.legs) do sum=sum+leg.distance end;assert(math.abs(sum-plan.distance)<.001)
for _,leg in ipairs(plan.legs) do assert(A.Terrain.Validate(leg),'local legs must remain terrain-validated') end
A.Journey.Install(plan)
local early=assert(A.Journey.Update(p(2,.05),true))
assert(early.mapID==1 and A.Journey.legIndex==1,'overlapping map rectangles must not cause an early leg skip before the verified crossing')
local aim=assert(A.Journey.Update(p(1,.75),true))
assert(aim.mapID==1 and aim.x>.75 and A.Journey.legIndex==1,'near the exit the arrow must aim across, not declare arrival or stop at the boundary')
assert(not A.Journey.Update(p(3,.3),true),'an unexpected zone must not skip an intermediate leg')
aim=assert(A.Journey.Update(p(2,.3),true))
assert(A.Journey.legIndex==2 and aim.mapID==2,'the client zone change must hand guidance to the next local leg')
assert(A.Journey.Remaining(p(2,.3))>0)
A.Journey.Pause();assert(not A.Journey.Update(p(2,.4),true));assert(A.Journey.Resume(p(2,.4)))
aim=assert(A.Journey.Update(p(2,.75),true));assert(aim.mapID==2 and aim.x>.75)
assert(A.Journey.Update(p(3,.3),true));local _,arrived=A.Journey.Update(p(3,.9),true);assert(arrived=='arrived')
local reverse=assert(A.Journey.Plan(p(3,.9),p(1,.1),{}));assert(#reverse.legs==3)
A.RouteRecovery.Clear();A.Journey.Install(plan)
A.RouteRecovery.Update(p(1,.5,.05),0);assert(A.RouteRecovery.Update(p(1,.5,.05),3).replan)
A.Journey.Update(p(1,.75),true);A.Journey.Update(p(2,.3),true)
A.RouteRecovery.Update(p(2,.5,.05),4)
assert(not A.RouteRecovery.Update(p(2,.5,.05),7).replan,'crossing zones must retain the automatic replanning cooldown')
A.CrossingData.maps[3].instance=1
assert(not A.Journey.Plan(p(1,.1),p(3,.9),{}),'walking must not cross unrelated terrain instances')
A.CrossingData.maps[3].instance=0
local old=A.CrossingData.edges;A.CrossingData.edges={}
assert(not A.Journey.Plan(p(1,.1),p(3,.9),{}),'overlapping rectangles alone must never create a crossing')
A.CrossingData.edges=old
''')
print('PASS: cross-zone multi-hop plans, safe connectors, map handoff, reverse routing and explicit gaps')

for name in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/Crossings.lua','Data/Structures.lua','Roads.lua','Structures.lua','WalkingRegions.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
assert(#A.CrossingData.edges>=110)
for _,e in ipairs(A.CrossingData.edges) do
 if e.structure then assert(A.Structures.Get(e)) else
  local ab=assert(A.TravelNetwork.Transform(e.a,e.b.mapID))
  local ba=assert(A.TravelNetwork.Transform(e.b,e.a.mapID))
  assert(A.Terrain.Segment(e.a,ba) and A.Terrain.Segment(ab,e.b))
  assert(math.abs(A.TravelNetwork.Distance(e.a,e.b)-e.distance)<.001 and e.distance<=120.001)
 end
end
local a=assert(A.Terrain.Approach({mapID=1431,x=.77,y=.44},30))
local b=assert(A.Terrain.Approach({mapID=1429,x=.42,y=.65},30));b.name='Goldshire'
local result,why;local steps=0
A.db.preferRoads=true
A.PlanningJob.Start(function() return A.Journey.Plan(a,b,{}) end,function(p) result=p end,function(r) why=r end)
while A.PlanningJob.IsRunning() and steps<5000 do A.PlanningJob.Step();steps=steps+1 end
assert(result,why or 'native cross-zone job did not complete')
assert(result.multiZone and #result.legs==2 and steps>1)
assert(result.distance>2500 and result.distance<4000)
for _,leg in ipairs(result.legs) do assert(A.Terrain.Validate(leg)) end
A.Journey.Install(result)
for i,leg in ipairs(result.legs) do
 for _,p in ipairs(leg.points) do
  local aim,reason=A.Journey.Update(p,true)
  assert(aim or reason=='arrived',reason)
 end
 if i<#result.legs then assert(A.Journey.crossing,'guidance must wait for the real zone change') end
end
local _,reason=A.Journey.Update(b,true);assert(reason=='arrived')
print('Native Darkshire-Goldshire:',math.floor(result.distance),'yd,',steps,'cooperative steps')
''')
print('PASS: expanded native connectors and cooperative Darkshire-to-Goldshire route/follower')
