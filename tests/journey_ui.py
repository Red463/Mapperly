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
A.navigationChoices.direct:GetScript('OnClick')();assert(A.db.navigationMode=='direct')
A.navigationChoices.terrain:GetScript('OnClick')();assert(A.db.navigationMode=='terrain')
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
assert(line.lineStart[3]==100 and line.lineStart[4]==-120 and line.lineEnd[3]==300 and line.lineEnd[4]==-480,'route lines must use normalized canvas coordinates')
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
CreateFrame=function(...) local frame=createFrame(...);driver=frame;return frame end
assert(loadstring(PLANNING_JOB_SOURCE))('Mapperly',A)
local request=A.Journey.Request
A.Journey.Request=function(candidate,done,failed)
 return A.PlanningJob.Start(function() return plan end,done,failed)
end
local field=A.navigationWindow
field.xInput:SetText('42.265799844097');field.yInput:SetText('66.5577526985558')
field.preview:GetScript('OnClick')()
assert(field.status:GetText():find('Planning',1,true))
CreateFrame=createFrame
assert(driver and driver:GetScript('OnUpdate'),'preview must have a live frame callback')
driver:GetScript('OnUpdate')(driver,.016)
assert(A.JourneyView.window:IsShown() and not A.PlanningJob.IsRunning())
assert(not field.status:GetText():find('Planning',1,true),'successful preview must clear its pending status')
A.Journey.Request=request

''')
print('PASS: dedicated Navigation settings, mode persistence, normalized route geometry and themed preview controls')
