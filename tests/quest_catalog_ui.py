"""Catalogue scope preserves active quests and validates pickup actions."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute('''
A.Navigation.Stop();A.db.navigationMode='direct'
local completed=false;local accepted=false
UnitLevel=function() return 30 end;UnitRace=function() return 'Human','Human',1 end;UnitClass=function() return 'Warrior','WARRIOR',1 end;UnitFactionGroup=function() return 'Alliance' end
C_QuestLog={GetNumQuestLogEntries=function() return accepted and 1 or 0 end,GetInfo=function() return {questID=901,title='Find the lantern'} end,
 IsOnQuest=function() return accepted end,IsQuestFlaggedCompleted=function() return completed end,IsComplete=function() return false end}
A.QuestCatalogData={version=1,quests={
 [901]={title='Find the lantern',level=20,minLevel=10,starters={{label='Lantern keeper',worldX=0,worldY=-10000,instance=0,faction='A'}}},
 [902]={title='Find the crown',minLevel=60,starters={{label='Crown keeper',worldX=0,worldY=-10000,instance=0,faction='A'}}}}}
A.ShowNavigationInput(1431);local f=A.navigationWindow;f.SelectPage('quests');local u=f.questUI
assert(u.scope=='active')
u.catalogScope:GetScript('OnClick')(u.catalogScope)
assert(u.scope=='catalog' and u.empty:GetText():find('two letters',1,true))
u.search:SetText('lantern');u.search:GetScript('OnTextChanged')(u.search)
A.QuestNavigationUI.driver:GetScript('OnUpdate')(A.QuestNavigationUI.driver,.3)
assert(u.questList.rows[1].record.id==901 and u.questList.rows[1].detail:GetText():find('Possible',1,true))
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
local row=u.locationList.rows[1];assert(row.record.catalog and row.go:IsEnabled())
local oldGo=A.Navigation.ToPin;local went=0
A.Navigation.ToPin=function(p) went=went+1;assert(p.catalog and p.questID==901);return true end
row.go:GetScript('OnClick')(row.go);assert(went==1)
A.ShowNavigationInput(1431);f.SelectPage('quests')
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
accepted=true
u.locationList.rows[1].go:GetScript('OnClick')(u.locationList.rows[1].go)
assert(went==1 and f.status:GetText():find('active',1,true),'accepting a quest must invalidate its old pickup action')
accepted=false;completed=true
u.locationList.rows[1].go:GetScript('OnClick')(u.locationList.rows[1].go)
assert(went==1 and f.status:GetText():find('completed',1,true))
completed=false;u.back:GetScript('OnClick')(u.back)
u.search:SetText('crown');u.search:GetScript('OnTextChanged')(u.search)
A.QuestNavigationUI.driver:GetScript('OnUpdate')(A.QuestNavigationUI.driver,.3)
u.questList.rows[1].locations:GetScript('OnClick')(u.questList.rows[1].locations)
assert(not u.locationList.rows[1].go:IsEnabled() and not u.locationList.rows[1].preview:IsEnabled())
u.back:GetScript('OnClick')(u.back);u.activeScope:GetScript('OnClick')(u.activeScope)
assert(u.scope=='active')
A.Navigation.ToPin=oldGo
''')
print('PASS: catalogue scope, throttled search, availability labels, starter routing and accepted/completed stale guards')
