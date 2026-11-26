"""Nearest services must compare verified walking journeys and preserve uncertainty."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
for f in ['Store.lua','PlanningJob.lua','QuestNavigation.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute("""
A.InitStore({});UnitFactionGroup=function() return 'Alliance' end
A.CrossingData={maps={[1]={west=100,north=100,width=100,height=100,instance=0},[2]={west=0,north=100,width=100,height=100,instance=0}}}
A.TravelNetwork={Canonical=function(m)return m end,World=function(p)local m=A.CrossingData.maps[p.mapID or p.map];return m.west-p.x*m.width,m.north-p.y*m.height,m.instance end}
A.TravelNetwork.Distance=function(a,b)local x,y,i=A.TravelNetwork.World(a);local u,v,j=A.TravelNetwork.World(b);return i==j and math.sqrt((x-u)^2+(y-v)^2) or nil end
A.Terrain={Zone=function()return {widthYards=100,heightYards=100}end,Segment=function(a,b)return a.mapID~=1 or a.x~=.02 end,Approach=function()return nil end}
A.BundledServices={
 {category='inn',id=1,name='Blocked',instance=0,x=50,y=98,access='A'},
 {category='inn',id=2,name='Long detour',instance=0,x=50,y=96,access='A'},
 {category='inn',id=3,name='Short route',instance=0,x=50,y=92,access='AH'},
 {category='inn',id=4,name='Enemy',instance=0,x=50,y=99,access='H'},
 {category='inn',id=5,name='Unknown access',instance=0,x=50,y=99.5},
 {category='inn',id=6,name='Other continent',instance=1,x=50,y=99,access='A'},
 {category='mail',id=7,name='Boundary mailbox',instance=0,x=50,y=-2,access='A'}}
local plans=0
A.Journey={PlayerPosition=function()return {mapID=1,x=0,y=.5}end,
 Plan=function(start,target,options)
  plans=plans+1;assert(options.walkingOnly,'nearest walking cannot add flights or boats')
  A.PlanningJob.Checkpoint()
  return {kind='walking',distance=target.name=='Long detour' and 50 or 9,points={start,{mapID=target.map,x=target.x,y=target.y}},legs={}}
 end}
""")
assert (root/'NearestServices.lua').exists(),'nearest service model must exist'
l.execute('assert(loadstring(...))("Mapperly",A)',(root/'NearestServices.lua').read_text())
l.execute("""
local S=A.NearestServices;local start=A.Journey.PlayerPosition()
local rows=S.Candidates('inn',start);assert(#rows==3,'enemy, unknown access and disconnected continents are excluded')
local result=assert(S.Find('inn',start));assert(result.pin.name=='Short route' and result.plan.distance==9,'physical nearest does not always have the shortest reachable route')
assert(result.complete,'unreachable blocked endpoints cannot claim to be useful services')
assert(result.pin.walkingOnly and result.pin.serviceKey)
local mail=assert(S.Find('mail',start));assert(mail.pin.map==2,'services across zone borders must remain searchable')
local capped=assert(S.Find('inn',start,{maxCandidates=1}));assert(not capped.complete,'a capped search cannot claim a proven nearest service')
local saved=A.Journey.Plan
A.Journey.Plan=function(s,p,o)if p.name=='Long detour' then return nil,'budget' end;return saved(s,p,o) end
local partial=assert(S.Find('inn',start));assert(partial.pin.name=='Short route' and not partial.complete,'a lower-bound budget failure remains uncertain')
A.Journey.Plan=saved
local pin=assert(S.Resolve(result.pin));assert(pin.name=='Short route')
A.db.navigationMode='direct';assert(not S.Resolve(result.pin),'old service results cannot silently become straight-line navigation');A.db.navigationMode='terrain'
UnitFactionGroup=function()return 'Horde'end
A.BundledServices[3].access='A'
assert(not S.Resolve(result.pin),'source/access changes must invalidate stale result actions')
UnitFactionGroup=function()return 'Alliance'end
local completed=false;assert(S.Request('mail',function(r)completed=true end,function(e)error(e)end))
assert(A.PlanningJob.IsRunning());A.PlanningJob.Cancel();A.PlanningJob.Step();assert(not completed,'cancellation cannot publish old results')
assert(S.Request('mail',function(r)completed=true end,function(e)error(e)end))
assert(not S.Request('inn',function()end,function()end),'service search cannot cancel an existing planning job')
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(completed)
A.Navigation={target={map=2,x=.7,y=.5}}
local searchFailure
assert(S.Request('dungeon',nil,function(reason)
    local history=A.PlanningJob.Recent()
    searchFailure=history[#history]
    assert(searchFailure.reason==reason)
end))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(searchFailure and searchFailure.state=='failed')
assert(not searchFailure.destination,'a search with no matching service has no destination')
assert(searchFailure.start.mapID==1 and searchFailure.start.x==0 and searchFailure.start.y==.5)
""")
print('PASS: nearest verified walking distance, faction/source guards, border coverage, partial results and transactional cancellation')
