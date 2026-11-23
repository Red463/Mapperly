"""Active quest search and validated standalone/native destination selection."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','QuestNavigation.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
A.InitStore({})
local log={{isHeader=true,title='Duskwood'},{questID=20,title='Raven [Hill]',level=20},{questID=21,title='The Hermit',level=25},{questID=22,title='Hidden',isHidden=true},{questID=23,title='No position',level=10}}
local complete={[20]=false,[21]=true,[23]=false}
C_QuestLog={GetNumQuestLogEntries=function() return #log end,GetInfo=function(i) return log[i] end,IsComplete=function(id) return complete[id] end,
 GetQuestObjectives=function(id) return id==20 and {{text='Find the journal',finished=true,objectiveID=100},{text='Speak to Sven',finished=false,objectiveID=101}} or {} end,
 GetQuestsOnMap=function(map) return {{questID=20,x=.4,y=.6,mapID=0,inProgress=true},{questID=21,x=.6,y=.3,mapID=map,inProgress=false},{questID=23,x=.5,y=.5,mapID=map,isQuestStart=true}} end,
 GetNextWaypoint=function(id) if id==20 then return 1431,.3,.4 end end}
GetQuestUiMapID=function() return 1431 end
C_Map={GetMapInfo=function(id) return {name=id==1431 and 'Duskwood' or 'Eastern Kingdoms',mapType=3} end}
A.CrossingData={maps={[1431]={west=1000,north=1000,width=1000,height=1000,instance=0},[1417]={west=2000,north=2000,width=2000,height=2000,instance=0}}}
A.QuestLocationData={version=1,quests={[20]={
 {kind='objective',objectiveID=100,label='Completed journal',worldX=500,worldY=500,instance=0},
 {kind='objective',objectiveID=101,label='Sven',worldX=300,worldY=200,instance=0},
 {kind='objective',label='Invalid',worldX=0/0,worldY=0,instance=0}},
 [21]={{kind='turnin',label='Hermit',worldX=400,worldY=700,instance=0}}}}
local Q=A.QuestNavigation
assert(#Q.Search('')==3)
assert(#Q.Search('RAVEN [')==1,'quest search must be plain text and case insensitive')
assert(#Q.Search('.*')==0,'search input cannot be interpreted as a pattern')
local targets=Q.Locations(20)
assert(#targets==3,'native objective, travel waypoint and unfinished snapshot objective should be offered')
assert(targets[1].map==1431,'native pin coordinates belong to the queried UI map')
local saved
for _,p in ipairs(targets) do
 assert(A.ValidPin(p));assert(p.name:find('Raven [Hill]',1,true))
 assert(p.label~='Completed journal')
 if p.label=='Sven' then assert(p.map==1431 and p.x==.7 and p.y==.8 and p.source=='snapshot');saved=p end
end
assert(saved and Q.Resolve(saved),'existing target must revalidate')
log[1].isCollapsed=true
ExpandQuestHeader=function() error('search cannot expand native headers') end
CollapseQuestHeader=function() error('search cannot collapse native headers') end
assert(#Q.Search('Raven')==1 and Q.Resolve(saved),'modern log enumeration remains independent of header display state')
C_QuestLog.IsFailed=function(id) return id==20 end
local failed,failedReason=Q.Locations(20)
assert(#failed==0 and failedReason:find('failed',1,true),'native failed quests cannot offer navigation')
assert(not Q.Resolve(saved),'quest failure invalidates an already selected objective')
C_QuestLog.IsFailed=function() return false end
local turnins=Q.Locations(21)
assert(#turnins>=1)
for _,p in ipairs(turnins) do assert(p.kind=='turnin') end
local none,reason=Q.Locations(23);assert(#none==0 and reason,'no verified position must be explained')
complete[20]=true
assert(not Q.Resolve(saved),'objective cannot be activated after the quest becomes ready to turn in')
complete[20]=false;log[2]={isHeader=true,title='Removed quest'}
assert(not Q.Resolve(saved),'abandoned quest cannot start a stale destination')
-- Protected/missing/throwing APIs and legacy log readers remain safe.
C_QuestLog.GetNumQuestLogEntries=function() error('not available') end
GetNumQuestLogEntries=function() return 2 end
GetQuestLogTitle=function(i) if i==1 then return 'Old header',0,0,true else return 'Legacy quest',12,0,false,false,1,nil,77 end end
local legacy=Q.Search('Legacy');assert(#legacy==1 and legacy[1].complete==true)
C_QuestLog=nil;GetNumQuestLogEntries=nil;GetQuestLogTitle=nil
local empty,why=Q.Search('');assert(#empty==0 and why)
''')
print('PASS: active-only plain-text quest search, native/snapshot destinations, source labels, progress filtering and stale guards')
