"""Real navigation hooks restore/cancel/fail safely and persist paused intent."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
local N,J,S=A.Navigation,A.Journey,A.JourneySession
UnitGUID=function()return 'Player-session-integration'end
UnitFactionGroup=function()return 'Alliance'end
GetBuildInfo=function()return '1.60.1','70959','date',16001 end
UnitOnTaxi=function()return false end;UnitInVehicle=function()return false end;IsPlayerMoving=function()return false end
A.Flights.OnTaxi=function()return false end
N.Stop();A.InitStore({});A.db.navigationMode='terrain'
local P=A.TravelNetwork
local player=assert(A.Terrain.Approach({mapID=1431,x=.826,y=.575},30))
local goal=assert(A.Terrain.Approach({mapID=1431,x=.78,y=.56},30))
C_Map.GetBestMapForUnit=function()return player.mapID end
C_Map.GetPlayerMapPosition=function()return {GetXY=function()return player.x,player.y end}end
local hbd={GetWorldCoordinatesFromZone=function(_,x,y,m)return P.World({mapID=m,x=x,y=y})end,
 GetPlayerWorldPosition=function()return P.World(player)end,
 GetZoneCoordinatesFromWorldInstance=function(_,x,y,i,m)local z=A.CrossingData.maps[m];if z and z.instance==i then return (z.west-x)/z.width,(z.north-y)/z.height end end}
LibStub=function(n)if n=='HereBeDragons-2.0' then return hbd end end
assert(N.Start(goal.mapID,goal.x*100,goal.y*100,'Recover this journey'))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target,N.planningError)
N.Pause();assert(A.db.journeySessions['Player-session-integration'].paused,'Pause hook persists state')
local function reloadState()
 N.target=nil;N.pending=nil;N.deferredRoutingTarget=nil;J.Clear();S.Intent();assert(S.Open())
end
reloadState();local plan=J.Plan;J.Plan=function()return nil,'Fixture async resume failure'end
assert(S.Resume());while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
J.Plan=plan;assert(S.Open(),'async failure must retire resume ownership without erasing the saved intent')
assert(S.Resume());N.CancelPlanning();assert(S.Open(),'cancel must permit a new restore offer')
assert(S.Resume());while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(N.target and J.active and J.paused,'Installed hook restores pause before Tick can advance/arrive')
N.Resume();assert(not A.db.journeySessions['Player-session-integration'].paused,'Resume hook persists running state')
N.Pause();reloadState()
assert(not N.Start(1431,777,5,'Invalid'));assert(S.frame:IsShown(),'a rejected request must not consume the resume offer')
local report=A.RouteReport.Build();assert(report:find('Enter X and Y',1,true) and not report:find('Player-session-integration',1,true),'synchronous rejections are exported without GUIDs')
assert(N.Start(goal.mapID,goal.x*100,goal.y*100,'New intent',{mode='direct'}))
assert(not S.frame:IsShown() and N.target.name=='New intent','accepted newer intent consumes old offer')
A.db.journeySessions['Player-other']={schema=1,build='unrelated',target={map=1431,x=.1,y=.1,name='Other'}}
N.Stop();assert(not A.db.journeySessions['Player-session-integration'] and A.db.journeySessions['Player-other'],'Stop clears only this character')
""")
print('PASS: real activation/pause/resume/Stop persistence, async failed/cancelled restore ownership, manual intent and synchronous report hooks')
