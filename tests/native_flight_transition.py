"""Auberdine to Astranaar follows the real native flight through zero-Z landing."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_recovery_transition.py'))['lua']
for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Flights.lua','Data/Structures.lua','Structures.lua','WalkingRegions.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
local N,J,F,P=A.Navigation,A.Journey,A.Flights,A.TravelNetwork
N.Stop();A.InitStore({});F.Closed();F.WorldChanged(true)
local source,destination=A.FlightData.nodes[26],A.FlightData.nodes[28]
local c=F.Character();c.nodes={[26]=true,[28]=true};c.offers={[26]={[28]={from=26,to=28,fare=1,hops={26,28}}}}
local p=source.a;local taxi=false
UnitOnTaxi=function() return taxi end
C_Map.GetBestMapForUnit=function() return p.mapID end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return p.x,p.y end} end
UnitPosition=function() local x,y,i=P.World(p);return y,x,0,i end
local goal=assert(A.Terrain.Approach({mapID=1440,x=.36,y=.50},30))
assert(N.Start(goal.mapID,goal.x*100,goal.y*100,'Astranaar onward'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.Leg().transport and J.Leg().transport.fromNodeID==26 and J.Leg().transport.toNodeID==28)
local plan=J.active;taxi=true;N.Tick()
assert(not A.PlanningJob.IsRunning() and J.active==plan and J.transportState.flightSeen)
p=destination.a;taxi=false;N.Tick()
assert(J.Leg().kind=='walk' and not J.transportMessage and N.frame.icon:IsShown(),'native Astranaar landing must restore the walking arrow on the first on-foot tick')
assert(not A.PlanningJob.IsRunning(),'an ordinary expected landing needs no recovery search')
''')
print('PASS: native Auberdine–Astranaar takeoff retains journey and landing immediately resumes walking')
