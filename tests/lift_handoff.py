"""A lift exit immediately replans onward walking instead of pointing backwards."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/journey_navigation.py'))['lua']
for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/Crossings.lua',
          'Data/Structures.lua','Data/Transports.lua','Data/LocalTransports.lua','Roads.lua','Structures.lua',
          'WalkingRegions.lua','TravelNetwork.lua','Transports.lua','RouteRecovery.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
local N,J,P=A.Navigation,A.Journey,A.TravelNetwork
N.Stop();A.InitStore({});A.db.navigationMode='terrain'
local row=A.LocalTransportData.edges[1];local p=row.a
C_Map.GetBestMapForUnit=function() return p.mapID end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return p.x,p.y end} end
hbd.GetWorldCoordinatesFromZone=function(_,x,y,map) return P.World({mapID=map,x=x,y=y}) end
UnitPosition=function() local x,y,i=P.World(p);return y,x,0,i end
assert(N.Start(1441,29.6,34.2,'Thousand Needles'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.Leg().kind=='transport')
local oldPlan,oldTarget=J.active,N.target
p=P.Transform({worldX=-1852.978,worldY=-4709.713,instance=1},1441)
N.Tick()
assert(J.Leg().kind=='walk','the recorded left exit must complete the lift')
assert(N.pending and N.autoReplan and A.PlanningJob.IsRunning(),'onward walking should replan immediately at the actual exit')
assert(not N.frame.icon:IsShown(),'do not point back to the old arrival marker while updating')
N.Tick()
assert(N.pending and not N.frame.icon:IsShown(),'the outdated arrow must remain hidden on every tick until the handoff replacement finishes')
assert(J.active==oldPlan and N.target==oldTarget,'retain the working journey while the replacement calculates')
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active~=oldPlan and not N.pending and N.target.name=='Thousand Needles')
assert(not N.handoffPending)
assert(not J.transportMessage and not N.frame.remaining:GetText():find('Take the lift',1,true),'walking HUD must clear the lift instruction')
assert(#A.db.destinationHistory==1,'a handoff update must not duplicate destination history')
local function atLift()
 N.Stop();p=row.a;J.Install(oldPlan);N.target=oldTarget;N.Tick()
 assert(J.Leg().kind=='transport')
 p=P.Transform({worldX=-1852.978,worldY=-4709.713,instance=1},1441)
end
atLift();N.pending={map=1441,x=.3,y=.34,name='Manual replacement'}
N.Tick();assert(N.pending.name=='Manual replacement','lift completion must preserve a pending manual destination')
atLift();N.deferredRoutingTarget={map=1441,x=.296,y=.342,name='Deferred replacement'}
N.Tick();assert(N.pending and N.pending.name=='Deferred replacement','deferred changes take priority over automatic handoff work')
atLift();local planFunction=J.Plan
J.Plan=function() return nil,'No replacement route' end
N.Tick();assert(N.pending)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
J.Plan=planFunction
assert(J.active==oldPlan and N.target==oldTarget and not N.pending,'a failed handoff update preserves the established route')
N.Tick();assert(not A.PlanningJob.IsRunning(),'failure must not start a repeated handoff planning loop')
atLift();N.Tick();assert(N.handoffPending)
N.CancelPlanning();assert(not N.handoffPending and not N.pending and J.active==oldPlan,'cancel clears handoff UI state while retaining the route')
atLift();N.Tick();assert(N.handoffPending)
assert(N.SetSmartRouting(false));assert(not J.active and not N.handoffPending and not N.pending,'switching to direct guidance clears the handoff wait state')
N.Stop();A.InitStore({});A.db.navigationMode='terrain'
row=A.LocalTransportData.edges[2];p=row.a
assert(N.Start(1413,44.22,90.17,'Return to the Barrens'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
oldPlan=J.active
-- The client still reports Thousand Needles at this upper Barrens exit.
p=P.Transform({worldX=-1854.166686,worldY=-4600.167625,instance=1},1441)
N.Tick();assert(N.pending)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(J.active~=oldPlan and not N.recoveryError,'upward handoff must replan on the proven current walking map despite delayed native map assignment')
''')
print('PASS: recorded left-lift exit immediately updates onward walking and clears the transport HUD')
