"""Unaccepted quest search must distinguish known restrictions from uncertainty."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
for f in ['Store.lua','QuestNavigation.lua','QuestCatalog.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute('''
A.InitStore({})
local done={[2]=true,[4]=true};local on={[6]=true};local level=20;local cls=1
UnitLevel=function() return level end;UnitRace=function() return 'Human','Human',1 end;UnitClass=function() return 'Warrior','WARRIOR',cls end;UnitFactionGroup=function() return 'Alliance' end
C_QuestLog={GetNumQuestLogEntries=function() return 1 end,GetInfo=function() return {questID=6,title='Active quest',level=10} end,
 IsComplete=function() return false end,IsFailed=function() return false end,
 IsOnQuest=function(id) return on[id] or false end,IsQuestFlaggedCompleted=function(id) return done[id] or false end}
local starter={label='Quest giver',worldX=500,worldY=500,instance=0,faction='A',source='snapshot'}
A.CrossingData={maps={[1431]={west=1000,north=1000,width=1000,height=1000,instance=0}}}
C_Map={GetMapInfo=function() return {name='Duskwood'} end}
A.QuestCatalogData={version=1,quests={
 [1]={title='Start [Here]',level=10,minLevel=5,raceIDs={1},classIDs={1},prevQuestID=2,starters={starter}},
 [2]={title='Previous quest',starters={starter}},
 [3]={title='Too high',minLevel=50,starters={starter}},
 [4]={title='Already completed',starters={starter}},
 [5]={title='Unknown conditions',availabilityUnverified=true,starters={starter}},
 [6]={title='Active quest',starters={starter}},
 [7]={title='Missing prerequisite',prevQuestID=99,starters={starter}},
 [8]={title='Repeatable',repeatable=true,starters={starter}},
 [9]={title='No starter',starters={}},
 [10]={title='Must stay in progress',prevQuestID=-6,starters={starter}},
 [11]={title='Breadcrumb target',dependentBreadcrumbIDs={6},starters={starter}}}}
local C=A.QuestCatalog
assert(#C.Search('START [')==1 and #C.Search('.*')==0)
assert(#C.Search('Active quest')==0,'already accepted quests belong to Active scope')
assert(C.Find(1).status=='possible')
assert(C.Find(3).available==false and C.Find(3).reason:find('50',1,true))
assert(C.Find(4).available==false and C.Find(4).reason:lower():find('completed',1,true))
assert(C.Find(5).status=='unknown','unevaluated conditions cannot be labeled available')
assert(C.Find(7).available==false)
assert(C.Find(8).status=='unknown','repeatable reset availability cannot be inferred from history')
assert(C.Find(10).status=='possible')
assert(C.Find(11).available==false and C.Find(11).reason:find('abandon',1,true),'active breadcrumb quests must block their target')
cls=2;assert(C.Find(1).available==false);cls=1
local locations=C.Locations(1);assert(#locations==1 and locations[1].catalog and locations[1].map==1431)
local target=assert(A.QuestNavigation.RouteTarget(locations[1]));assert(target.questID==1 and target.catalog)
on[1]=true;assert(not A.QuestNavigation.RouteTarget(locations[1]),'accepting a quest invalidates its pickup action');on[1]=nil
done[1]=true;assert(not C.Resolve(locations[1]),'completion invalidates a nonrepeatable pickup');done[1]=nil
done[2]=nil;assert(not C.Resolve(locations[1]),'changed prerequisite status must be checked again');done[2]=true
local none,why=C.Locations(9);assert(#none==0 and why)
local legacyComplete=C_QuestLog.IsQuestFlaggedCompleted;C_QuestLog.IsQuestFlaggedCompleted=nil
assert(C.Find(1).status=='unknown','missing completion history must not invent availability')
C_QuestLog.IsQuestFlaggedCompleted=legacyComplete
local short,reason=C.Search('');assert(#short==0 and reason,'catalogue needs a query instead of rendering thousands of rows')
''')
print('PASS: catalogue search, native eligibility, unknown requirements, exact starters and stale pickup guards')
