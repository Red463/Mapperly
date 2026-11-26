"""Confirmed boat arrivals must rebase walking from the actual disembark position."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/WalkingPaths.lua','Roads.lua','PathReuse.lua','Structures.lua','WalkingRegions.lua','TravelBounds.lua','TravelNetwork.lua','Transports.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute("""
local N,J,P,R=A.Navigation,A.Journey,A.TravelNetwork,A.RouteRecovery
N.Stop();A.InitStore({});A.db.navigationMode='terrain';UnitFactionGroup=function()return 'Alliance'end;UnitClass=function()return 'Warrior','WARRIOR',1 end
local row
for _,r in ipairs(A.TransportData.edges) do if r.id=='transport:11167:34:7' then row=r end end
assert(row)
local p=row.a;local now=0;GetTime=function()return now end
C_Map.GetBestMapForUnit=function()return p.mapID end
C_Map.GetPlayerMapPosition=function()return {GetXY=function()return p.x,p.y end}end
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map)return P.World({mapID=map,x=x,y=y})end
UnitPosition=function()local x,y,i=P.World(p);return y,x,row.arrivalGroundHeight,i end
local goal=assert(A.Terrain.Approach({mapID=1437,x=.106,y=.608},30))
assert(N.Start(goal.mapID,goal.x*100,goal.y*100,'Menethil onward'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
local oldPlan,oldTarget=J.active,N.target;assert(oldPlan,N.planningError or 'initial boat plan was not installed');local transitIndex
for i,leg in ipairs(oldPlan.legs) do if leg.transport and leg.transport.id==row.id then transitIndex=i;break end end
assert(transitIndex,'native Auberdine to Menethil boat must be selected')
local walk=oldPlan.legs[transitIndex+1]
local first,nextPoint=walk.points[1],walk.points[2]
local d=P.Distance(first,nextPoint);assert(d>14)
local landed={mapID=first.mapID,x=first.x+(nextPoint.x-first.x)*12/d,y=first.y+(nextPoint.y-first.y)*12/d}
assert(A.Terrain.Segment(landed,landed) and A.Transports.CanDisembark(row,landed,{departed=true}),'replay begins at a permitted, natively confirmed dock arrival')
local function arriving()
 N.Stop();J.Install(oldPlan);N.target=oldTarget;J.legIndex=transitIndex;J.index=oldPlan.legs[transitIndex].first;J.transportState={departed=true};p=landed
end
arriving();N.Tick()
assert(J.Leg().kind=='walk')
assert(N.pending and N.handoffPending and A.PlanningJob.IsRunning(),'boat-to-walk continuation must start at the actual disembark point instead of guiding back to the precomputed shore anchor')
assert(not N.frame.icon:IsShown(),'stale walking arrow is hidden until the actual-position route is ready')
now=4;N.Tick();assert(not R.IsOffRoute() and not N.frame.icon:IsShown(),'handoff work must not be classified as an ordinary off-route detour')
assert(J.active==oldPlan and N.target==oldTarget)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active~=oldPlan and not N.pending and not N.handoffPending)
assert(P.Distance(J.active.points[1],landed)<.001,'new walking geometry must start at the actual landing location')
assert(not R.IsOffRoute() and #A.db.destinationHistory==1)
arriving();local planner=J.Plan;J.Plan=function()return nil,'No onward connection' end
N.Tick();assert(N.handoffPending)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
J.Plan=planner;assert(J.active==oldPlan and N.target==oldTarget and not N.pending)
N.Tick();assert(not A.PlanningJob.IsRunning(),'failed handoff cannot loop indefinitely')
arriving();N.Tick();N.CancelPlanning();assert(not N.pending and not N.handoffPending and J.active==oldPlan)
arriving();N.pending={map=1437,x=.1,y=.6,name='Manual replacement'};N.Tick();assert(N.pending.name=='Manual replacement')
arriving();N.deferredRoutingTarget={map=1437,x=goal.x,y=goal.y,name='Deferred replacement'};N.Tick();assert(N.pending.name=='Deferred replacement')
-- A certified Stormwind pier already joins its native floor and must not
-- be replaced by an unconstrained terrain chord through harbour water.
N.Stop();A.InitStore({});A.db.navigationMode='terrain'
for _,r in ipairs(A.TransportData.edges) do if r.id=='transport:11616:6:18' then row=r end end
p=row.a
local city=assert(A.Terrain.Approach(P.Transform({worldX=1083.47,worldY=-8797.43,instance=0},1453),30))
assert(N.Start(city.mapID,city.x*100,city.y*100,'Stormwind city'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
local protectedPlan=assert(J.active,N.planningError)
for i,leg in ipairs(protectedPlan.legs) do if leg.transport and leg.transport.id==row.id then J.legIndex=i;J.index=leg.first;J.transportState={departed=true};break end end
assert(J.Leg().kind=='transport')
local pier=A.HarbourAccessData.corridors[row.arrivalCorridor];p=pier.a
UnitPosition=function()local x,y,i=P.World(p);return y,x,0,i end
N.Tick()
assert(J.Leg().kind=='walk' and J.active==protectedPlan and not N.pending and not N.handoffPending,'native pier arrival must keep the already joined protected walking floor')
assert(P.Distance(J.Current(),pier.b)>150,'certified floor continuation cannot send the player back to the boat')

-- Approach the Ratchet ferry by a different boardwalk, missing the inland waypoint.
N.Stop()
for _,r in ipairs(A.TransportData.edges) do if r.id=='transport:241:29:11' then row=r end end
p=row.a
local start=assert(A.Terrain.Approach({mapID=1434,x=.272,y=.769},100))
p=start
assert(N.Start(row.b.mapID,row.b.x*100,row.b.y*100,'Ratchet ferry'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active,N.planningError)
assert(J.Leg().kind=='walk' and J.active.legs[J.legIndex+1].transport.id==row.id)
p={mapID=1434,x=.258,y=.734}
print('Booty Bay replay: yards to shore waypoint and vessel',P.Distance(p,row.a),P.Distance(p,row.board))
assert(P.Distance(p,row.a)>100 and P.Distance(p,row.board)<25)
IsSwimming=function()return true end
N.Tick();assert(J.Leg().kind=='walk','swimming past the ship must not skip walking')
IsSwimming=function()return false end
J.Pause();N.Tick();assert(J.Leg().kind=='walk')
J.paused=false
local flights=A.Flights
A.Flights={OnTaxi=function()return true end}
N.Tick();assert(J.Leg().kind=='walk','a flyover must not trigger boat boarding')
A.Flights=flights
N.autoReplan=true;N.pending=N.target
A.PlanningJob.Start(function()error('obsolete walking detour ran')end)
N.Tick()
assert(J.Leg().transport==row and J.transportMessage=='Board the boat to Ratchet','the boarding plank must take priority over a missed inland waypoint')
assert(not J.transportState.departed and not N.pending and not R.IsOffRoute() and not A.PlanningJob.IsRunning())
N.Tick();assert(J.Leg().transport==row and not J.transportState.departed)

-- Booty Bay dock screenshot, rounded to the tenth shown by the client.
local plank={mapID=1434,x=.260,y=.732}
local nearPier={mapID=1434,x=.263,y=.732}
local plan=J.active
J.Install(plan);p=nearPier
assert(P.Distance(p,row.board)>25 and P.Distance(p,plank)<25)
N.Tick()
assert(J.Leg().transport==row,'approaching the observed plank should bypass the inland waypoint')
local aim,message=A.Transports.Guide(J.Leg(),p,J.transportState)
assert(aim and P.Distance(aim,plank)<.01,'the approach arrow must target the dock end of the plank')
p=plank;N.Tick()
assert(J.transportMessage=='Board the boat to Ratchet' and not J.transportState.departed)
local aboard=A.Transports.Aim(row.board,1434)
aim=A.Transports.Guide(J.Leg(),p,J.transportState)
assert(aim and P.Distance(aim,aboard)<.01,'from the plank, guide forward onto the ferry')
print('PASS: Booty Bay boarding plank at 26.0, 73.2;',P.Distance(p,row.board),'yards from the native vessel stop')
""")
print('PASS: native Auberdine-Menethil disembark rebase, protected recovery, old-route retention, history and job ownership')
