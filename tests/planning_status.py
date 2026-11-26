"""Visible planning feedback, identity-safe results and cancellation from the map."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
lua.execute('''
assert(A.PlanningStatus,'visible planning status must exist')
local J,S,N=A.PlanningJob,A.PlanningStatus,A.Navigation
local p={map=1431,x=.4,y=.6,name='Far destination'}
local published=false
J.Start(function()
 J.Report('Checking zone connections',{checked=16,total=49,flightRoutes=2,flightSources=1});coroutine.yield()
 J.BeginPath(1431);J.PathProgress(1024);coroutine.yield()
 return {points={{mapID=1431,x=.4,y=.6}},distance=1200,legs={{},{}}}
end,function(plan) published=true;S.Ready(id,p,plan) end)
id=S.Begin(p)
assert(id and S.frame:IsShown() and S.frame:GetFrameStrata()=='FULLSCREEN_DIALOG','status must be above the world map')
assert(S.frame.destination:GetText():find('Far destination',1,true))
J.Step();S.Update(.5)
assert(S.frame.phase:GetText():find('zone connections',1,true))
assert(S.frame.detail:GetText():find('Flight routes considered: 2',1,true),'flight eligibility must be visible while planning')
J.Step();S.Update(2)
assert(S.frame.detail:GetText():find('1024',1,true),'real search activity must be visible')
assert(S.frame.elapsed:GetText()~='0s','elapsed time must visibly advance')
J.Step();assert(published and S.frame.state=='ready')
S.Update(6);assert(not S.frame:IsShown(),'success feedback should clear after being readable')
J.Start(function() coroutine.yield();return {} end)
local old=S.Begin(p)
J.Start(function() coroutine.yield();return {} end)
local current=S.Begin({map=1431,x=.5,y=.5,name='New destination'})
S.Failed(old,p,'stale failure');assert(S.frame.jobID==current and S.frame.state=='running','stale callbacks must not replace the current status')
N.Build();N.target={map=1431,x=.1,y=.1,name='Old destination'}
local target=N.target
N.pending={map=1431,x=.5,y=.5,name='Replacement'}
S.frame.action:GetScript('OnClick')()
assert(not J.IsRunning() and not N.pending and N.target==target,'Cancel must stop the calculation while preserving the active destination')
S.Failed(nil,p,'No verified outdoor walking crossings connect these zones yet.')
assert(S.frame:IsShown() and S.frame.state=='failed' and S.frame.detail:GetText():find('No verified',1,true))
S.Update(100);assert(S.frame:IsShown(),'failure must remain visible until dismissed')
S.frame.action:GetScript('OnClick')();assert(not S.frame:IsShown())
N.target=nil
S.Clear();J.Start(function() coroutine.yield();return {} end)
S.Failed(nil,p,'Destination terrain is unavailable.')
assert(S.frame:IsShown() and S.frame.state=='failed' and J.IsRunning(),'an invalid manual click during silent automatic work must show its error without cancelling the background job')
S.frame.action:GetScript('OnClick')();assert(J.IsRunning())
J.Cancel()
''')
print('PASS: visible planning stages, elapsed/activity, results, stale callback protection and cancel preserving active guidance')
lua.execute('''
local N,J,S=A.Navigation,A.PlanningJob,A.PlanningStatus
N.Stop();A.db.navigationMode='terrain'
LibStub=function() return {
 GetWorldCoordinatesFromZone=function(_,x,y) return 1000-x*1000,1000-y*1000,0 end,
 GetZoneCoordinatesFromWorldInstance=function(_,x,y) return (1000-x)/1000,(1000-y)/1000 end,
 GetPlayerWorldPosition=function() return 900,900,0 end} end
GetPlayerFacing=function() return 0 end
C_Map.GetBestMapForUnit=function() return 1431 end
C_Map.GetPlayerMapPosition=function() return {GetXY=function() return .1,.1 end} end
GetMouseFoci=nil;GetMouseFocus=nil
IsAltKeyDown=function() return true end;IsControlKeyDown=function() return false end;IsShiftKeyDown=function() return false end
A.TerrainData={version=1,zones={}}
for _,map in ipairs({1431,1429}) do A.TerrainData.zones[map]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
A.map.GetMapID=function() return 1431 end
assert(A.HandleMapClick(A.map,'RightButton',.9,.9))
assert(S.frame:IsShown() and S.frame.state=='running' and N.pending,'Alt-right-click must immediately show visible status')
while J.IsRunning() do J.Step() end
assert(S.frame.state=='ready' and N.target.x==.9)
local target,plan=N.target,A.Journey.active
A.CrossingData={version=1,maps={
 [1431]={west=1000,north=1000,width=1000,height=1000,instance=0,name='Duskwood'},
 [1429]={west=500,north=1000,width=1000,height=1000,instance=0,name='Elwynn'}},edges={}}
A.map.GetMapID=function() return 1429 end
A.HandleMapClick(A.map,'RightButton',.9,.9)
assert(S.frame.state=='running')
S.frame.action:GetScript('OnClick')()
assert(N.target==target and A.Journey.active==plan and not N.pending,'cancelling an Alt-right-click replacement must keep the real active route')
A.HandleMapClick(A.map,'RightButton',.9,.9)
while J.IsRunning() do J.Step() end
assert(S.frame.state=='failed' and S.frame.detail:GetText():find('No verified',1,true),'unsupported far routes must explain the failure above the map')
assert(N.target==target and A.Journey.active==plan)
N.Stop()
''')
print('PASS: actual Alt-right-click immediately reports progress, completion and unsupported far-route failure')
lua.execute('''
local S,R,J=A.PlanningStatus,A.RouteReport,A.PlanningJob
local attempted={map=1434,x=.42,y=.086,name='Private note title'}
local player={mapID=1434,x=.1,y=.2}
A.Journey.PlayerPosition=function() return player end
S.Failed(nil,attempted,'No crossing from this bank.')
local status=S.frame
assert(status.copyReport:IsShown() and status.reportHint:GetText():find('CurseForge',1,true))
R.Open()
local window=R.frame
local focused,selected=false,false
window.edit.SetFocus=function() focused=true end
window.edit.HighlightText=function(_,first,last) selected=focused and first==nil and last==nil end
window:Hide()
player.x=.9
status.copyReport:GetScript('OnClick')()
local snapshot=window.edit:GetText()
assert(window:IsShown() and window:GetFrameStrata()=='FULLSCREEN_DIALOG' and selected)
assert(snapshot:find('Reported error: No crossing from this bank.',1,true))
assert(snapshot:find('Requested destination: map=1434 x=0.42 y=0.086',1,true))
assert(snapshot:find('Actual position: map=1434 x=0.1 y=0.2',1,true))
assert(not snapshot:find('Private note title',1,true) and not window.refresh:IsShown())
assert(window.copyHint:GetText():find('Ctrl+C',1,true))
IsMacClient=function() return true end
status.copyReport:GetScript('OnClick')()
assert(window.copyHint:GetText():find('Cmd+C',1,true))
J.Start(function() coroutine.yield() end)
local id=S.Begin(attempted)
assert(not status.copyReport:IsShown() and not status.reportHint:IsShown())
S.Failed(nil,attempted,'Second click rejected')
assert(status.state=='running' and status.jobID==id and status.copyReport:IsShown())
assert(status.action:GetText()=='Cancel' and window.edit:GetText()==snapshot)
status.copyReport:GetScript('OnClick')()
assert(window.edit:GetText():find('Reported error: Second click rejected',1,true))
assert(J.IsRunning())
status.action:GetScript('OnClick')()
assert(not J.IsRunning() and not status.copyReport:IsShown())
R.Open()
assert(window.refresh:IsShown() and not window.edit:GetText():find('Reported error:',1,true))
''')
print('PASS: failure action selects the frozen route report on Windows and Mac and preserves concurrent planning')
