"""Actual navigation entry points commit only successful walking plans."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/navigation.py'))['lua']
for name in ['Terrain.lua','PlanningJob.lua','Journey.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text(encoding='utf-8'))
lua.execute('''
A.InitStore({layoutVersion=2});A.db.navigationMode='terrain'
A.TerrainData={version=1,zones={[1431]={status='complete',w=5,h=5,widthYards=1000,heightYards=1000,rows={'2','2','2','2','+'}}}}
playerX,playerY,playerInstance=900,900,0
C_Map.GetBestMapForUnit=function() return 1431 end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .1,.1 end} end
local N=A.Navigation
N.Stop()
assert(N.Start(1431,90,10,'Across the ridge'))
assert(N.pending and not N.target,'a pending walking request must not publish a partial destination')
for i=1,100 do A.PlanningJob.Step();if not A.PlanningJob.IsRunning() then break end end
assert(N.target and not N.pending and A.Journey.active and #A.Journey.active.points>2)
assert(#A.db.destinationHistory==1)
N.Tick()
local bend=A.Journey.Current()
local wx,wy=hbd:GetWorldCoordinatesFromZone(bend.x,bend.y,bend.mapID)
assert(math.abs(N.frame.bearing-N.Bearing(wx-playerX,wy-playerY))<.0001,'HUD bearing must follow a route bend rather than cut through the ridge')
N.Pause();N.Tick();assert(N.frame.label:GetText()=='Paused')
assert(N.Resume());N.Tick();assert(N.frame.icon:IsShown())
local currentTarget,currentPlan,currentBend=N.target,A.Journey.active,A.Journey.Current()
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .5,.1 end} end
playerX,playerY=500,900
N.Tick()
assert(N.frame:IsShown() and N.frame.icon:IsShown() and N.target==currentTarget and A.Journey.active==currentPlan,'entering a restricted cell must not hide guidance or stop navigation')
assert(A.Journey.Current()==currentBend,'restricted cells must preserve route progress')
N.Pause();assert(N.Resume());assert(N.frame.icon:IsShown())
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .1,.1 end} end
playerX,playerY=900,900
N.Tick();assert(N.frame.icon:IsShown(),'normal mask guidance must recover when the player returns')
assert(A.db.navigationMode=='terrain','smart routing must default on')
assert(N.SetSmartRouting(false))
assert(A.db.navigationMode=='direct' and N.target and not A.Journey.active and not N.pending and not A.PlanningJob.IsRunning(),'turning smart routing off must switch the active destination immediately')
assert(#A.db.destinationHistory==1,'mode changes must not duplicate history')
assert(N.SetSmartRouting(true));assert(N.pending)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(A.Journey.active and A.db.navigationMode=='terrain','turning smart routing back on must plan the current destination')
local before=N.target;local plan=A.Journey.active
assert(not N.Start(1431,50,10,'Blocked'))
assert(N.target==before and A.Journey.active==plan and #A.db.destinationHistory==1)
A.TerrainData.zones[1431].rows={'2','2','2','2','2'}
assert(N.Start(1431,90,30,'Unreachable'))
for i=1,100 do A.PlanningJob.Step();if not A.PlanningJob.IsRunning() then break end end
assert(N.target==before and A.Journey.active==plan and #A.db.destinationHistory==1,'a failed search must preserve the last successful journey and history')
assert(N.Start(1431,90,30));N.Stop();A.PlanningJob.Step();assert(not N.target and not A.Journey.active and not N.pending)
A.db.navigationMode='direct';assert(N.Start(1431,50,10,'Direct bearing'))
assert(N.target and not N.pending and not A.Journey.active,'direct bearing must remain an explicit option')
A.db.navigationMode='terrain';N.Stop()
A.TerrainData.zones[1431].rows={'2','2','2','2','+'}
assert(N.Start(1431,90,10,'Old target'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.Start(1431,90,30,'Replacement'))
A.Journey.index=#A.Journey.active.points
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .9,.1 end} end
playerX,playerY=100,900
N.Tick()
assert(N.pending and A.PlanningJob.IsRunning() and not N.target,'arrival at the previous target must not cancel the replacement request')
N.Stop()
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .1,.1 end} end
playerX,playerY=900,900
assert(N.Start(1431,90,30,'Pending mode switch'))
assert(N.pending and N.SetSmartRouting(false))
assert(N.target and N.target.name=='Pending mode switch' and not N.pending and not A.PlanningJob.IsRunning(),'turning smart routing off must immediately convert a pending destination')


''')
print('PASS: transactional walking navigation, bend-following HUD, pause/resume, cancellation and explicit direct mode')
