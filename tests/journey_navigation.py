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

lua.execute('''
local N=A.Navigation
N.Stop();A.db.navigationMode='terrain'
A.TerrainData={version=1,zones={[1431]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}}}}
local p={mapID=1431,x=.8,y=.2}
local bend={mapID=1431,x=.8,y=.8}
local goal={mapID=1431,x=.2,y=.2}
local wx,wy=hbd:GetWorldCoordinatesFromZone(goal.x,goal.y,1431)
N.target={map=1431,x=goal.x,y=goal.y,name='West destination',zone='Test zone',worldX=wx,worldY=wy,instance=0}
A.Journey.Install({kind='walking',mapID=1431,points={p,bend,goal}})
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return p.x,p.y end} end
-- A walking HUD must use the route's player-position feed rather than mixing
-- it with a separately sampled/offset world-position feed.
playerX,playerY,playerInstance=900,100,0;facing=0
N.Tick()
assert(math.abs(math.abs(N.frame.bearing)-math.pi)<.00001,'the HUD must guide south along the next leg even though the destination is west')
assert(N.frame.label:GetText()=='600 yd','primary distance must be to the next turn, not the final destination')
assert(N.frame.remaining and N.frame.remaining:GetText():find('remaining'),'total remaining distance must be labelled separately')
p.x=.8;p.y=.8
N.Tick()
assert(A.Journey.index==3 and N.frame.bearing>0 and N.frame.bearing<math.pi/2,'at a bend guidance must advance along the next route leg')
local original=hbd.GetPlayerWorldPosition
hbd.GetPlayerWorldPosition=function() return nil end
N.Tick();assert(N.frame.icon:IsShown(),'walking direction should not depend on a second world-position feed')
hbd.GetPlayerWorldPosition=original
N.Stop()
''')
print('PASS: winding-route HUD uses local route geometry, next-turn distance and automatic bend advancement')
