"""Real Darkshire services use bundled data and ordinary permitted walking routes."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
files=['Store.lua','Data/Places.lua','Data/Services.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Flights.lua','Data/WalkingPaths.lua','Roads.lua','Terrain.lua','PathReuse.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelBounds.lua','TravelNetwork.lua','Journey.lua','QuestNavigation.lua','NearestServices.lua']
for f in files:l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute("""
A.InitStore({preferRoads=true,roadPreferenceStrength=3});UnitFactionGroup=function()return 'Alliance'end;UnitClass=function()return 'Warrior','WARRIOR',1 end
local start=assert(A.Terrain.Approach({mapID=1431,x=.826,y=.575},30))
A.Journey.PlayerPosition=function()return start end
for _,kind in ipairs({'inn','mail','flight'}) do
 local found,why,report;local slices=0
 A.PlanningJob.Start(function()local r,e=A.NearestServices.Find(kind,start);report=A.PlanningJob.Progress();return r,e end,function(r)found=r end,function(e)why=e end)
 while A.PlanningJob.IsRunning() and slices<4000 do A.PlanningJob.Step();slices=slices+1 end
 assert(found,why or 'native service search failed')
 assert(found.pin.map==1431,'nearby Darkshire service should win over other zones')
 if kind=='inn' then assert(found.pin.serviceKey:find(':6790:',1,true),'native Darkshire innkeeper Trelayne should be found') end
 for _,leg in ipairs(found.plan.legs) do assert(leg.kind=='walk' and not leg.transport);assert(A.Terrain.Validate(leg)) end
 assert(found.pin.walkingOnly and report.cells<=350000,'nearest walking must retain its global work bound')
 assert(A.NearestServices.Resolve(found.pin),'current bundled service must revalidate')
 print('Darkshire',kind,found.pin.name,found.plan.distance,'yd',found.checked,'routes',report.cells,'cells',slices,'slices',found.complete and 'nearest verified' or 'partial')
end
local peak
for _,p in ipairs(A.NearestServices.Candidates('flight',start)) do if p.serviceKey:find(':43:',1,true) then peak=p end end
assert(peak,'Aerie Peak source position must be retained')
assert(A.TravelNetwork.Distance({mapID=peak.map,x=peak.x,y=peak.y},A.FlightData.nodes[43].world)<.0001,'flight exact location must be the master, not its ground handoff')
assert(not A.NearestServices.Resolve(peak),'native handoff farther than30yd cannot masquerade as an exact service')
UnitFactionGroup=function()return 'Horde'end
for _,p in ipairs(A.NearestServices.Candidates('flight',start)) do assert(not p.serviceKey:find(':30:',1,true),'source-only Freewind Post is not a verified destination') end
""")
print('PASS: native inns/mailboxes/flight masters, source identity, validated walking legs, bounded work and action resolution')
