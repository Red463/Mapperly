"""Positive takeoff suppresses walking recovery; zero-height landing resumes travel."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_navigation.py'))['lua']
lua.execute('''
local N,J,F,R=A.Navigation,A.Journey,A.Flights,A.RouteRecovery
N.Stop();A.InitStore({});A.db.navigationMode='terrain'
local taxi=false;local now=0;local p={mapID=1431,x=.45,y=.5}
UnitOnTaxi=function() return taxi end;GetTime=function() return now end
C_Map.GetBestMapForUnit=function() return p.mapID end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return p.x,p.y end} end
UnitPosition=function() local x,y,i=A.TravelNetwork.World(p);return y,x,0,i end
local c=F.Character();c.nodes={[2]=true,[4]=true};c.offers={[2]={[4]={from=2,to=4,fare=100,hops={2,4}}}}
assert(N.Start(1429,60,50,'Flight destination'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.Leg().kind=='walk')
-- A previously recorded deviation must not fire on the takeoff tick.
p={mapID=1431,x=.48,y=.6};R.Clear();R.Update(p,0,false)
local start=N.Start;local calls=0
N.Start=function(...) calls=calls+1;return start(...) end
now=3.1;taxi=true;N.Tick()
N.Start=start
assert(calls==0 and not N.deferredRoutingTarget and not N.pending,'takeoff must be recognised before walking recovery starts a replacement')
assert(J.Leg().transport and J.transportState.flightSeen and N.frame.label:GetText():find('Flying',1,true))
N.OnFlightsChanged()
assert(not N.pending and not N.deferredRoutingTarget,'flight metadata updates in air cannot queue a redundant destination replan')
-- Client71037 returns zero height on both ground and taxi; observed landing
-- at the actual flight master plus positive on-foot evidence must suffice.
p={mapID=1429,x=.5,y=.5};taxi=false;now=40;N.Tick()
assert(J.Leg().kind=='walk','zero native altitude cannot leave a completed observed flight stuck in transport')
local function approach()
 N.Stop();taxi=false;now=0;p={mapID=1431,x=.45,y=.5};F.Closed()
 assert(N.Start(1429,60,50,'Flight destination'))
 while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
 return J.active,N.target
end
local oldPlan,oldTarget=approach()
N.OnFlightsChanged()
assert(N.pending and N.autoReplan,'discovery/fare refresh must be a quiet automatic update')
taxi=true
-- The planning driver can finish before Navigation.Tick observes takeoff.
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active==oldPlan and N.target==oldTarget and not N.pending,'an automatic result cannot replace the active journey after takeoff')
assert(J.transportState.flightSeen)
oldPlan,oldTarget=approach()
assert(N.Start(1429,60,50,'Manual replacement'));taxi=true
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active==oldPlan and N.target==oldTarget and N.deferredRoutingTarget.name=='Manual replacement','a manual result finishing in air must wait for landing')
taxi=false
N.OnFlightsChanged()
assert(N.deferredRoutingTarget.name=='Manual replacement' and not N.pending,'discovery cannot demote a deferred manual destination to automatic work')
N.Stop();taxi=false;p={mapID=1431,x=.45,y=.5}
assert(N.Start(1429,60,50,'First request'));taxi=true
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(not N.target and not J.active and N.deferredRoutingTarget.name=='First request','first-ever pending request cannot activate while airborne')
taxi=false;N.Tick()
assert(N.pending and N.pending.name=='First request','first destination must resume planning on positive landing')
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target.name=='First request' and J.active)
N.Stop();taxi=true
assert(N.Start(1429,60,50,'Airborne request'))
assert(N.deferredRoutingTarget and not N.pending and not N.target)
taxi=nil;N.Tick();assert(N.deferredRoutingTarget,'unknown taxi state cannot resume a saved request')
taxi=false;N.Tick();assert(N.pending and N.pending.name=='Airborne request')
N.Stop();A.db.navigationMode='direct';taxi=false
assert(N.Start(1429,60,50,'Old direct'));taxi=true
assert(N.Start(1429,65,50,'New direct'))
assert(N.target.name=='Old direct' and N.deferredRoutingTarget)
taxi=false;N.Tick()
assert(N.target.name=='New direct' and not N.deferredRoutingTarget,'direct guidance must also resume a manual destination after landing')
''')
print('PASS: takeoff recovery ordering and zero-altitude observed-flight landing')
