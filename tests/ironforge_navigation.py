"""Ironforge's indoor mask must not reject every destination from a city start."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/tram_journey.py'))['l']
l.execute('assert(loadstring(...))("Mapperly",A)',(root/'CityNavigation.lua').read_text(encoding='utf8'))
l.execute('assert(loadstring(...))("Mapperly",A)',(root/'RouteRecovery.lua').read_text(encoding='utf8'))
l.execute("""
A.InitStore({useTrams=false,useFlights=false,useBoats=false,useLifts=false,useZeppelins=false,useAirships=false})
local goal={mapID=1455,x=.555,y=.478}
local starts={{mapID=1455,x=.249,y=.753},{mapID=1455,x=.6,y=.4},{mapID=1455,x=.331534,y=.653159}}
for _,start in ipairs(starts)do
 assert(not A.Terrain.Segment(start,start),'native fixture must reproduce rejected indoor starts')
 local plan,why=A.Journey.Plan(start,goal,{maxWalkingCells=60000})
 assert(plan,why);assert(plan.hasCityGuidance and not plan.hasTransports,'indoor start must get city wayfinding without requiring a tram')
 assert(not A.Terrain.Segment(start,start),'city guidance must not whiten or change terrain permissions')
 A.Journey.Install(plan)
 local aim,message=A.Journey.Update(start,true)
 assert(aim and A.TravelNetwork.Distance(aim,goal)<.001 and not message,'guidance must aim at the destination rather than the rejected start')
 assert(A.Journey.Pause()and A.Journey.Resume(start))
end
local plan,why=A.Journey.Plan(goal,starts[1],{maxWalkingCells=60000})
assert(plan and plan.hasCityGuidance,why or 'indoor destination must also work')
A.Journey.Install(plan)
local aim,message=A.Journey.Update(goal,true)
assert(aim and not message,'a blocked city destination must not immediately report Return to route')
-- Crossing the native entrance retains its floor while inside, then releases
-- that inherited membership once normal city wayfinding leaves the gate.
local gate
for id,row in pairs(A.StructureData.corridors)do if row.a.mapID==1426 and row.b.mapID==1455 then gate={id=id,row=row};break end end
local entered=assert(A.Journey.Plan(gate.row.a,starts[2],{maxWalkingCells=60000}))
A.Journey.Install(entered)
local at
for i,leg in ipairs(entered.legs)do if leg.exitStructure==gate.id then at=i;break end end
assert(at)
local passage=entered.legs[at];local city=entered.legs[at+1]
A.Journey.legIndex=at;A.Journey.index=passage.last;A.Journey.crossing=true
A.Journey.inStructure=gate.id;A.Journey.structureIndex=#passage.exitPath
UnitPosition=nil
assert(A.Journey.Prepare(city.points[1]))
A.Journey.Update(city.points[1],true)
assert(A.Journey.inStructure==gate.id,'keep native gate state while still on its protected floor')
A.RouteRecovery.Clear()
assert(not A.RouteRecovery.Update(goal,10,true).replan)
assert(not A.RouteRecovery.Update(goal,14,true).replan,'city guidance must not trigger recovery due to a stale entrance structure')
assert(not A.Journey.inStructure,'leaving the protected entrance clears inherited gate membership')
-- Normal permitted Ironforge routes should continue using their terrain path.
plan=assert(A.Journey.Plan({mapID=1455,x=.187,y=.515},goal,{maxWalkingCells=60000}))
assert(not plan.hasCityGuidance)
-- The conservative service-search contract and outdoor permissions are separate.
assert(not A.Journey.Plan(starts[1],goal,{walkingOnly=true,maxWalkingCells=60000}))
local blockedOutdoor={mapID=1431,x=.5,y=.5}
assert(not A.Terrain.Segment(blockedOutdoor,blockedOutdoor),'outdoor fixture must be blocked')
assert(not A.Journey.Plan(blockedOutdoor,goal,{maxWalkingCells=60000}),'blocked outdoor starts remain rejected')
""")
print('PASS: native Ironforge blocked starts/destinations use city guidance; normal paths, terrain permissions and walking-only searches remain intact')

# Exercise the actual public Start/Request/background activation path too.
n=runpy.run_path(str(root/'tests/run.py'))['lua']
n.execute("""
local N,J,P=A.Navigation,A.Journey,A.TravelNetwork
N.Stop();A.InitStore({useTrams=false,useFlights=false,useBoats=false,useLifts=false,useZeppelins=false,useAirships=false})
UnitFactionGroup=function()return 'Alliance'end;UnitOnTaxi=function()return false end;UnitInVehicle=function()return false end
local player={mapID=1455,x=.249,y=.753}
C_Map.GetBestMapForUnit=function()return player.mapID end
C_Map.GetPlayerMapPosition=function()return {GetXY=function()return player.x,player.y end}end
local hbd={GetWorldCoordinatesFromZone=function(_,x,y,m)return P.World({mapID=m,x=x,y=y})end,
 GetPlayerWorldPosition=function()return P.World(player)end,
 GetZoneCoordinatesFromWorldInstance=function(_,x,y,i,m)local z=A.CrossingData.maps[m];if z and z.instance==i then return (z.west-x)/z.width,(z.north-y)/z.height end end}
LibStub=function(name)if name=='HereBeDragons-2.0'then return hbd end end
UnitPosition=function()local x,y,i=P.World(player);return y,x,0,i end
local function navigate(goal)
 local ok,why=N.Start(goal.mapID,goal.x*100,goal.y*100,'Ironforge test')
 assert(ok,why)
 for i=1,5000 do if not A.PlanningJob.IsRunning()then break end;A.PlanningJob.Step()end
 assert(N.target and not N.pending and J.active,N.planningError or 'navigation did not activate')
 assert(J.active.hasCityGuidance)
 N.Tick();assert(N.target and not N.recoveryError)
end
navigate({mapID=1455,x=.555,y=.478});N.Stop()
-- Exact rc.1 report: Ironforge33.1534,65.3159, Prefer roads/Firm.
player={mapID=1455,x=.331534,y=.653159}
A.db.preferRoads=true;A.db.roadPreferenceStrength=4
for _,xy in ipairs({{.636913,.252976},{.652174,.239557},{.32906,.727385},{.599129,.308279}})do
 navigate({mapID=1455,x=xy[1],y=xy[2]});N.Stop()
end
A.db.preferRoads=false
player={mapID=1455,x=.249,y=.753}
local gate
for _,row in pairs(A.StructureData.corridors)do if row.a.mapID==1426 and row.b.mapID==1455 then gate=row;break end end
assert(gate,'native Ironforge entrance fixture')
navigate(gate.a);N.Stop()
player=gate.a;navigate({mapID=1455,x=.6,y=.4});N.Stop()
""")
print('PASS: actual navigation within/out/into Ironforge, including all four exact reported destinations from33.1534,65.3159 at Firm road preference')
