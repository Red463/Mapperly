"""Drive real Navigation.Start/Tick through a scheduled crossing and load gap."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
for f in ['TravelNetwork.lua','Transports.lua','RouteRecovery.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
local N,J=A.Navigation,A.Journey
N.Stop();A.db.navigationMode='terrain';A.db.useBoats=true
A.TerrainData={version=1,zones={}}
for _,id in ipairs({1431,1429}) do A.TerrainData.zones[id]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
A.CrossingData={version=1,build=42,maps={[1431]={name='Origin',west=1000,north=1000,width=1000,height=1000,instance=0},[1429]={name='Destination',west=1000,north=1000,width=1000,height=1000,instance=1}},edges={}}
local a,b={mapID=1431,x=.5,y=.5},{mapID=1429,x=.5,y=.5}
local row={id='ferry',kind='boat',name='Test ferry',faction='Neutral',a=a,b=b,board={worldX=500,worldY=500,instance=0},arrival={worldX=500,worldY=500,instance=1},planningSeconds=300,path={}}
A.TransportData={version=1,build=42,edges={row}}
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map) return A.TravelNetwork.World({mapID=map,x=x,y=y}) end
local map,x,y=1431,.4,.5
C_Map.GetBestMapForUnit=function() return map end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return x,y end} end
assert(N.Start(1429,60,50,'Ferry destination'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target and J.active.hasTransports and N.frame.label:GetText()=='100 yd')
x=.5;N.Tick();assert(J.Leg().kind=='transport')
assert(N.frame.remaining:GetText():find('Board the boat',1,true))
local plan,target=J.active,N.target
A.db.preferRoads=false;assert(N.SetPreferRoads(true))
assert(J.active==plan and not A.PlanningJob.IsRunning(),'preference changes aboard must wait for land instead of replanning from a moving ship')
assert(N.Start(1429,70,50,'Latest replacement'))
assert(N.SetPreferRoads(false));assert(N.deferredRoutingTarget.name=='Latest replacement')
assert(N.SetTransportPreference('zeppelin',false))
assert(N.deferredRoutingTarget.name=='Latest replacement','a second preference cannot replace the deferred latest destination with the old active target')
map=nil;N.Tick();assert(J.active==plan and N.target==target and not N.frame.icon:IsShown(),'missing boat position must retain instructions, not draw an invented bearing')
map=1429;x=.5;N.Tick()
assert(J.Leg().kind=='walk' and N.frame.label:GetText()=='100 yd','destination shore must resume the actual walking arrow')
assert(A.PlanningJob.IsRunning(),'deferred preferences must replan the remaining journey after disembarking')
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target.name=='Latest replacement')
x=.7;N.Tick();assert(not N.target and not J.active)
-- Switching to direct guidance also honours the latest deferred destination.
map=1431;x=.5;A.db.navigationMode='terrain';J.Install(plan);N.target=target;N.Tick()
assert(N.Start(1429,70,50,'Direct replacement'));assert(N.SetPreferRoads(true))
assert(N.SetSmartRouting(false));assert(N.target.name=='Direct replacement' and not J.active and not N.deferredRoutingTarget)
''')
print('PASS: real scheduled Navigation.Start/Tick, loading preservation and walking HUD resumption')
