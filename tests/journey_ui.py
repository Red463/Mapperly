"""Navigation settings, safe map projection and themed journey preview."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
for file in ['Terrain.lua','PlanningJob.lua','Journey.lua','JourneyView.lua']:
 p=root/file
 if p.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',p.read_text(encoding='utf-8'))
lua.globals().PLANNING_JOB_SOURCE=(root/'PlanningJob.lua').read_text(encoding='utf-8')
lua.execute('''
InCombatLockdown=function() return false end
assert(A.settingsTabs.navigation,'settings must have a dedicated Navigation tab')
A.settingsTabs.navigation:GetScript('OnClick')()
assert(A.settingsWindow.navigationPage:IsShown() and not A.settingsWindow.displayPage:IsShown() and not A.settingsWindow.layersPage:IsShown())
A.smartRoutingCheck:SetChecked(false);A.smartRoutingCheck:GetScript('OnClick')(A.smartRoutingCheck);assert(A.db.navigationMode=='direct')
A.smartRoutingCheck:SetChecked(true);A.smartRoutingCheck:GetScript('OnClick')(A.smartRoutingCheck);assert(A.db.navigationMode=='terrain')
assert(A.preferRoadsCheck,'Navigation settings must expose road preference')
local oldStart=A.Navigation.Start;local replans=0
local oldTarget=A.Navigation.target;local oldPending=A.Navigation.pending
A.Navigation.Start=function(map,x,y,name,options) replans=replans+1;assert(map==1431 and x==40 and y==60);return true end
A.Navigation.pending={map=1431,x=.4,y=.6,name='Pending destination'}
A.preferRoadsCheck:SetChecked(true);A.preferRoadsCheck:GetScript('OnClick')(A.preferRoadsCheck)
assert(A.db.preferRoads and replans==1,'changing road preference must replan the latest smart destination')
A.db.navigationMode='direct'
A.preferRoadsCheck:SetChecked(false);A.preferRoadsCheck:GetScript('OnClick')(A.preferRoadsCheck)
assert(not A.db.preferRoads and replans==1,'direct guidance must ignore road preference')
A.Navigation.Start=oldStart;A.Navigation.target=oldTarget;A.Navigation.pending=oldPending;A.db.navigationMode='terrain'
local published=false
A.Navigation.target=nil;A.Navigation.pending=nil
A.PlanningJob.Start(function() coroutine.yield();return {} end,function() published=true end)
A.PlanningJob.Step();assert(A.PlanningJob.IsRunning())
A.Navigation.SetPreferRoads(true)
assert(not A.PlanningJob.IsRunning(),'changing road preference must cancel a pending preview even without a navigation target')
A.PlanningJob.Step();assert(not published,'a stale preview must not reopen after changing road preference')
A.db.preferRoads=false;A.Navigation.target=oldTarget;A.Navigation.pending=oldPending
local plan={kind='walking',mapID=1431,name='Walking test',coverage='complete',distance=800,estimatedSeconds=800/7,
 points={{mapID=1431,x=.1,y=.2},{mapID=1431,x=.3,y=.8},{mapID=1431,x=.7,y=.8}},
 legs={{kind='walk',name='Walk to Walking test',distance=800,estimatedSeconds=800/7}}}
A.map.GetMapID=function() return 1431 end
A.map:GetCanvas():SetSize(1000,600)
A.Journey.Install(plan);A.db.showJourneyRoute=true
local artLevel=150
A.map.GetPinFrameLevelsManager=function() return {
 GetFrameLevelStart=function(_,kind) return kind=='PIN_FRAME_LEVEL_MAP_HIGHLIGHT' and artLevel or 100 end,
 GetFrameLevelRange=function() return 5 end,
} end
A.JourneyView.Refresh()
assert(A.JourneyView.overlay:GetFrameLevel()>=artLevel+5,'walking lines must render above native exploration/highlight map artwork')
assert(#A.JourneyView.lines==2 and A.JourneyView.lines[1]:IsShown(),'each validated segment must render without shortcuts')
local line=A.JourneyView.lines[1]
local reached=math.abs(line.lineEnd[3]-300)<.0001 and math.abs(line.lineEnd[4]+480)<.0001
assert(line.lineStart[3]==100 and line.lineStart[4]==-120 and reached,'the continuous stroke must reach the corner of the projected route')
A.JourneyView.Show(plan,{map=1431,x=.7,y=.8,name='Walking test'})
assert(A.JourneyView.window:IsShown() and A.JourneyView.summary:GetText():find('800',1,true))
assert(A.JourneyView.pause:IsEnabled() and A.JourneyView.resume:IsEnabled(),'active journey controls must be exposed')
local replacement={kind='walking',mapID=1431,name='Replanned test',coverage='complete',distance=500,estimatedSeconds=70,
 points={{mapID=1431,x=.2,y=.2},{mapID=1431,x=.5,y=.5}},legs={{kind='walk',name='New walking leg'}}}
A.Journey.Install(replacement);A.Navigation.target={map=1431,x=.5,y=.5,name='Replanned test'}
A.JourneyView.Refresh()
assert(A.JourneyView.plan==replacement and A.JourneyView.summary:GetText():find('500',1,true),'an open active preview must track the newly installed geometry and summary')
A.JourneyView.Show(plan,{map=1431,x=.7,y=.8,name='A separate preview'})
A.JourneyView.Refresh();assert(A.JourneyView.plan==plan,'replanning must not replace a separate candidate preview')

local startNavigation=A.Navigation.Start
local requested
A.Navigation.Start=function(map,x,y,name,options) requested=options;return true end
A.db.navigationMode='direct';A.JourneyView.start:GetScript('OnClick')()
assert(requested and requested.mode=='terrain','Start on a walking preview must retain walking mode even when the global preference is direct')
A.Navigation.Start=startNavigation

A.db.showJourneyRoute=false;A.JourneyView.Refresh();assert(not line:IsShown(),'route display preference must hide all geometry')
A.Journey.Clear();A.JourneyView.window:Hide();A.JourneyView.Refresh();assert(not line:IsShown())
-- Complete the preview through the worker frame's OnUpdate, as the client does.
local createFrame=CreateFrame;local driver
CreateFrame=function(...) local frame=createFrame(...);driver=driver or frame;return frame end
assert(loadstring(PLANNING_JOB_SOURCE))('Mapperly',A)
local request=A.Journey.Request
A.Journey.Request=function(candidate,done,failed)
 return A.PlanningJob.Start(function() return plan end,done,failed)
end
local field=A.navigationWindow
A.db.navigationMode='terrain'
field.xInput:SetText('42.265799844097');field.yInput:SetText('66.5577526985558')
field.preview:GetScript('OnClick')()
assert(field.status:GetText():find('Planning',1,true))
CreateFrame=createFrame
assert(driver and driver:GetScript('OnUpdate'),'preview must have a live frame callback')
driver:GetScript('OnUpdate')(driver,.016)
assert(A.JourneyView.window:IsShown() and not A.PlanningJob.IsRunning())
assert(not field.status:GetText():find('Planning',1,true),'successful preview must clear its pending status')
A.Journey.Request=request

local oldLib=LibStub
local playerWX=-500
LibStub=function() return {
 GetPlayerWorldPosition=function() return playerWX,-500,0 end,
 GetWorldCoordinatesFromZone=function(_,x,y) return -x*1000,-y*1000,0 end,
 GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,map) return -x/1000,-y/1000 end,
} end
A.JourneyView.window:Hide();A.Journey.Clear();A.db.navigationMode='direct';A.db.showJourneyRoute=true
A.Navigation.target={map=1431,x=.8,y=.5,worldX=-800,worldY=-500,instance=0,name='Direct destination'}
A.JourneyView.Refresh()
local directLine=A.JourneyView.lines[1]
assert(directLine:IsShown() and directLine.lineStart[3]==500 and math.abs(directLine.lineEnd[3]-800)<.0001,
 'direct guidance must draw one continuous stroke to the destination')
playerWX=-600;A.JourneyView.Refresh();assert(directLine.lineStart[3]==600,'direct map line must follow player movement')
A.JourneyView.OpenCurrent();playerWX=-650;A.JourneyView.Refresh()
assert(A.JourneyView.plan.points[1].worldX==-650 and directLine.lineStart[3]==650,'the active direct journey window must track the player instead of freezing a preview')
A.Navigation.Stop()
assert(not A.JourneyView.window:IsShown() and not directLine:IsShown(),'stopping an active direct journey must close its live view and remove the line')
A.Navigation.target={map=1431,x=.8,y=.5,worldX=-800,worldY=-500,instance=0,name='Direct destination'}

assert(A.JourneyView.Preview({map=1431,x=.8,y=.5,name='Direct preview'}))
assert(A.JourneyView.plan.kind=='direct' and not A.PlanningJob.IsRunning(),'smart routing off must preview a straight line without a terrain search')
A.Navigation.SetSmartRouting(true)
assert(not A.JourneyView.window:IsShown(),'changing mode must close the stale preview')
LibStub=oldLib

''')
print('PASS: dedicated Navigation settings, mode persistence, normalized route geometry and themed preview controls')
lua.execute('''
local legs={};for i=1,12 do legs[i]={kind='walk',name='Walk through zone '..i} end
A.JourneyView.Show({kind='walking',mapID=1431,name='Long journey',distance=1000,estimatedSeconds=150,coverage='complete',
 points={{mapID=1431,x=.1,y=.1},{mapID=1431,x=.9,y=.9}},legs=legs},{map=1431,x=.9,y=.9,name='Long journey'})
assert(A.JourneyView.stepScroll and A.JourneyView.stepScroll:GetScrollChild():GetHeight()>=216,'all zone legs must be accessible in a scrolling preview')
assert(A.JourneyView.steps:GetText():find('zone 12',1,true))
''')
lua.execute('''
local V,J=A.JourneyView,A.Journey
local oldPlan,oldCandidate=V.plan,V.candidate
local oldLib=LibStub
local playerX=400
LibStub=function() return {GetPlayerWorldPosition=function() return playerX,0,0 end} end
local function p(x,worldX)
 return {mapID=1431,x=x,y=.5,worldX=worldX,worldY=0,instance=0}
end
local plan={kind='walking',name='Clipped walk',distance=2000,estimatedSeconds=300,
 points={p(-.5,-500),p(1.5,1500)},legs={{kind='walk',name='Walk'}}}
V.window:Hide();A.map:Show();A.db.showJourneyRoute=true;J.Install(plan)
V.Refresh()
local past,ahead=V.lines[0],V.lines[1]
assert(past:IsShown() and ahead:IsShown() and past.lineStart[3]==0 and math.abs(ahead.lineStart[3]-400)<.001,
 'the world map must fade the visible walked portion up to the projected player')
assert(past.color[4]<ahead.color[4] and ahead.color[2]>ahead.color[1])
assert(ahead.thickness==3 and ahead.routeCasing.thickness>ahead.thickness and ahead.routeCasing.thickness<=ahead.thickness+2)
assert(past.routeCasing.drawSublevel<past.drawSublevel and ahead.routeCasing.drawSublevel<ahead.drawSublevel)
local refresh=V.Refresh;local redraws=0
V.Refresh=function(...) redraws=redraws+1;return refresh(...) end
for i=1,3 do V.progressDriver:GetScript('OnUpdate')(V.progressDriver,.21) end
playerX=401;V.progressDriver:GetScript('OnUpdate')(V.progressDriver,.21)
assert(redraws==0,'standing still or moving a single yard cannot rebuild the visible route')
playerX=440;V.progressDriver:GetScript('OnUpdate')(V.progressDriver,.21)
assert(redraws==1 and math.abs(ahead.lineStart[3]-440)<.001 and J.index==2,'significant movement must update the map without advancing the follower')
V.Refresh=refresh
A.db.showJourneyRoute=false;V.Refresh()
assert(not past:IsShown() and not past.routeCasing:IsShown() and not ahead.routeCasing:IsShown())
for _,line in ipairs(V.fragments) do assert(not line:IsShown() and not line.routeCasing:IsShown()) end

-- Inspect the production render inputs to cover projections many map widths away.
local render=A.RouteStyle.Render
local seen
A.RouteStyle.Render=function(segments,...) seen=segments;return render(segments,...) end
local ship={kind='walking',name='Long sailing piece',distance=1000,estimatedSeconds=100,
 points={p(-10000,-10000),p(10000,10000),p(11000,11000),p(12000,12000)},legs={}}
for _,point in ipairs(ship.points) do point.transport=true end
J.Install(ship);A.db.showJourneyRoute=true;V.Refresh()
assert(#seen==1 and seen[1].kind=='transport' and math.abs(seen[1][1])<.01 and math.abs(seen[1][3]-1000)<.01,
 'clip long projected sailing pieces before allocating dots and skip fully offscreen pieces')
A.RouteStyle.Render=render;J.Clear();LibStub=oldLib;V.Show(oldPlan,oldCandidate)
''')
print('PASS: clipped world route, walking progress, casing cleanup and movement-based redraw')
