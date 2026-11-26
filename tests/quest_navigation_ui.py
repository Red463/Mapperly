"""Quests tab integrates with existing themed destination actions safely."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/run.py'))['lua']
lua.execute('''
A.Navigation.Stop()
local active=true
C_QuestLog={GetNumQuestLogEntries=function() return active and 1 or 0 end,GetInfo=function() return {questID=71,title='Raven Hill',level=20} end,
 IsComplete=function() return false end,GetQuestObjectives=function() return {} end,
 GetQuestsOnMap=function(map) return {{questID=71,mapID=map,x=.4,y=.6,inProgress=true}} end}
GetQuestUiMapID=function() return 1431 end
A.ShowNavigationInput(1431)
local f=A.navigationWindow;assert(f.tabs.quests,'Destinations needs a fourth Quests tab')
f.tabs.quests:GetScript('OnClick')(f.tabs.quests)
local u=f.questUI
assert(f.questPage:IsShown() and not f.entryPage:IsShown() and not f.libraryPage:IsShown())
assert(#u.questList.rows>=1 and u.questList.rows[1].record.id==71)
local result=u.questList.rows[1]
assert(result.title.point[4]+result.title:GetWidth()<result.locations.point[4],'quest names must end before Locations')
assert(result.locations.point[4]+result.locations:GetWidth()<=result:GetWidth())
local questHeight,locationHeight=u.questList.frame:GetHeight(),u.locationList.frame:GetHeight()
f:FitToolHeight(f:GetHeight()+100)
assert(u.questList.frame:GetHeight()==questHeight+100 and u.locationList.frame:GetHeight()==locationHeight+100)
f:FitToolHeight(f:GetHeight())
u.search:SetText('does not exist');u.search:GetScript('OnTextChanged')(u.search)
assert(not u.questList.rows[1]:IsShown() and u.empty:GetText():find('No active quests',1,true))
u.search:SetText('RAVEN');u.search:GetScript('OnTextChanged')(u.search)
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
assert(u.selectedID==71 and u.locationList.rows[1].record.questID==71)
local row=u.locationList.rows[1];local went,previewed=0,0
assert(row.go.point[4]+row.go:GetWidth()<=row:GetWidth() and -row.go.point[5]+row.go:GetHeight()<=row:GetHeight())
local oldGo,oldPreview=A.Navigation.ToPin,A.JourneyView.Preview
A.Navigation.ToPin=function(p) went=went+1;assert(p.questID==71 and p.map==1431 and p.x==.4);return true end
A.JourneyView.Preview=function(p) previewed=previewed+1;assert(p.questID==71);return true end
A.QuestNavigationUI.driver:GetScript('OnEvent')(A.QuestNavigationUI.driver,'QUEST_LOG_UPDATE')
A.QuestNavigationUI.driver:GetScript('OnUpdate')(A.QuestNavigationUI.driver,.3)
assert(went==0 and previewed==0 and u.selectedID==71,'passive quest refresh cannot start navigation or lose current selection')
row.preview:GetScript('OnClick')(row.preview);assert(previewed==1)
row.go:GetScript('OnClick')(row.go);assert(went==1 and not f:IsShown())
A.ShowNavigationInput(1431);f.SelectPage('quests')
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
active=false
u.locationList.rows[1].go:GetScript('OnClick')(u.locationList.rows[1].go)
assert(went==1 and f.status:GetText():find('no longer',1,true),'stale quest click cannot replace navigation')
A.QuestNavigationUI.Refresh(f)
assert(not u.selectedID and u.empty:GetText():find('No active quests',1,true))
f.SelectPage('entry');assert(f.entryPage:IsShown() and not f.questPage:IsShown())
f.SelectPage('saved');assert(f.libraryPage:IsShown() and not f.questPage:IsShown())
for _,tab in pairs(f.tabs) do local x=tab.point[4];assert(x>=8 and x+tab:GetWidth()<=f:GetWidth()-8,'tabs must fit the drawer insets') end
A.Navigation.ToPin=oldGo;A.JourneyView.Preview=oldPreview
-- Reproduce the actual reported quest through both UI actions, not only
-- through the model: the list stays exact while the routed endpoint moves.
UnitFactionGroup=function() return 'Alliance' end
C_QuestLog.GetNumQuestLogEntries=function() return 1 end
C_QuestLog.GetInfo=function() return {questID=1248,title='The Missing Diplomat',level=33} end
C_QuestLog.IsComplete=function() return true end
C_QuestLog.GetQuestsOnMap=function() return {} end
A.db.navigationMode='terrain'
A.ShowNavigationInput(1431);f.SelectPage('quests')
u.search:SetText('');u.search:GetScript('OnTextChanged')(u.search)
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
local location=u.locationList.rows[1];local rawX=location.record.x;local starts=0
local function routed(p)
 assert(p.questID==1248 and p.map==1437 and p.x~=rawX and p.approachDistance<4 and p.questTarget.x==rawX)
 starts=starts+1;return true
end
A.Navigation.ToPin=routed;A.JourneyView.Preview=routed
location.preview:GetScript('OnClick')(location.preview)
assert(f.status:GetText():find('approach',1,true))
location.go:GetScript('OnClick')(location.go)
assert(starts==2 and location.record.x==rawX)
A.Navigation.ToPin=oldGo;A.JourneyView.Preview=oldPreview
local p=assert(A.QuestNavigation.RouteTarget(location.record));local invoked=0;local oldStart=A.Navigation.Start
A.JourneyView.Show({kind='direct',distance=10,legs={},points={},name=p.name},p)
A.Navigation.Start=function() invoked=invoked+1;return true end
C_QuestLog.GetNumQuestLogEntries=function() return 0 end
A.JourneyView.start:GetScript('OnClick')(A.JourneyView.start)
assert(invoked==0 and A.JourneyView.steps:GetText():find('no longer',1,true),'preview Start must revalidate the selected quest')
C_QuestLog.GetNumQuestLogEntries=function() return 1 end
A.JourneyView.plan.kind='walking'
A.Navigation.Start=function(map,x,y,name,options)
 invoked=invoked+1;assert(map==1437 and x/100~=rawX and name:find('approach',1,true) and options.mode=='terrain');return true
end
A.JourneyView.start:GetScript('OnClick')(A.JourneyView.start)
assert(invoked==1)
A.Navigation.Start=oldStart
''')
print('PASS: themed quest tab, search, location selection, preview/go, stale guards and existing destination pages')
