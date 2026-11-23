"""Actual planner/HUD: live boarding, asynchronous UI closure and interrupted flights."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
for f in ['TravelNetwork.lua','Flights.lua','Transports.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
local N,J,F=A.Navigation,A.Journey,A.Flights
N.Stop();A.db.navigationMode='terrain';A.db.useFlights=true
A.TerrainData={version=1,zones={}}
for _,id in ipairs({1431,1429}) do A.TerrainData.zones[id]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
A.CrossingData={version=1,build=99,maps={[1431]={name='Origin',west=1000,north=1000,width=1000,height=1000,instance=0},[1429]={name='Destination',west=0,north=1000,width=1000,height=1000,instance=0}},edges={}}
A.FlightData={version=1,build=99,nodes={},segments={}}
for _,r in ipairs({{2,1431,500},{4,1429,-500}}) do
 A.FlightData.nodes[r[1]]={id=r[1],name='Master '..r[1],factionMask=1,a={mapID=r[2],x=.5,y=.5},world={worldX=r[3],worldY=500,instance=0},z=10}
end
A.FlightData.segments['2:4']={seconds=30,cost=100,path={{worldX=500,worldY=500,instance=0},{worldX=0,worldY=500,instance=0},{worldX=-500,worldY=500,instance=0}}}
UnitGUID=function() return 'Player-Flight' end;UnitFactionGroup=function() return 'Alliance' end;UnitClass=function() return 'Mage','MAGE' end
local taxi=false;local now=0;UnitOnTaxi=function() return taxi end;GetMoney=function() return 1000 end;GetTime=function() return now end
local c=F.Character();c.nodes={[2]=true,[4]=true};c.offers={[2]={[4]={from=2,to=4,fare=100,hops={2,4}}}}
local map,x,y=1431,.5,.5
C_Map.GetBestMapForUnit=function() return map end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return x,y end} end
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map) return A.TravelNetwork.World({mapID=map,x=x,y=y}) end
-- At a live master, allow boarding directly from an otherwise blocked pad.
local segment=A.Terrain.Segment
A.Terrain.Segment=function(a,b) if a.mapID==1431 and a.x==.5 and b.x==.5 then return false end;return segment(a,b) end
F.open=true;F.source=2;F.sessionGUID='Player-Flight'
assert(N.Start(1429,60,50,'Flight destination'))
F.Closed() -- user closes native taxi UI before the cooperative job executes
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active and J.Leg().transport and J.Leg().transport.kind=='flight','blocked-pad boarding cannot fabricate a walking leg')
assert(J.active.flightCost==100)
local plan,target=J.active,N.target
taxi=true;N.Tick();assert(not N.frame.icon:IsShown() and N.frame.label:GetText():find('Flying',1,true))
assert(N.Start(1429,70,50,'Replacement after landing'))
assert(N.deferredRoutingTarget and not A.PlanningJob.IsRunning(),'new targets in flight wait for landing')
assert(N.SetTransportPreference('flight',false));assert(J.active==plan and N.deferredRoutingTarget.name=='Replacement after landing')
assert(N.SetSmartRouting(false));assert(J.active==plan and N.deferredRoutingTarget.name=='Replacement after landing','mode changes in air must retain the actual flight until landing')
assert(N.SetSmartRouting(true));assert(J.active==plan)
map=nil;F.WorldChanged(false);taxi=nil;N.Tick();assert(J.active==plan and N.target==target)
map=1429;x=.5;taxi=false;F.WorldChanged(true);UnitPosition=function() return 500,-500,10 end
N.Tick();assert(J.Leg().kind=='walk' and A.PlanningJob.IsRunning(),'valid landing resumes walking and replans the latest destination')
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target.name=='Replacement after landing')
-- A failed early-landing replacement preserves the journey and never loops.
N.Stop();A.db.useFlights=true;A.Terrain.Segment=segment
map=1431;x=.5;F.open=true;F.source=2;F.sessionGUID='Player-Flight'
assert(N.Start(1429,60,50,'Early landing'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
taxi=true;N.Tick();taxi=false;F.Closed();plan=J.active
N.deferredRoutingTarget={map=1429,x=.7,y=.5,name='Interrupted replacement'}
local calls=0;local request=J.Request
J.Request=function(...) calls=calls+1;return nil,'No safe connection from here.' end
N.Tick();now=3;N.Tick();now=6;N.Tick()
assert(calls==1 and J.active==plan,'interrupted flight recovery must make one transactional attempt')
J.Request=request
N.Stop();map=1431;x=.45;taxi=false
assert(N.Start(1429,60,50,'Board during approach'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.Leg().kind=='walk')
x=.48;taxi=true;N.Tick()
assert(J.Leg().transport and J.transportState.flightSeen and not N.frame.icon:IsShown(),'positive takeoff supersedes unfinished approach walking')
assert(N.Start(1429,70,50,'Takeoff replacement') and N.deferredRoutingTarget)
''')
print('PASS: live blocked-pad boarding, taxi lifecycle, queued target, loading and bounded interruption recovery')
