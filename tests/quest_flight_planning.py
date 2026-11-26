"""Production quest routing retains recorded flights within its walking budget."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
files=['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua',
       'Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua',
       'Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Trams.lua',
       'Data/Flights.lua','Data/QuestLocations.lua','Data/WalkingPaths.lua','Roads.lua',
       'Data/Water.lua','Water.lua','Data/WalkingPortals.lua','TerrainPortals.lua','Terrain.lua',
       'PathReuse.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelBounds.lua',
       'TravelNetwork.lua','Flights.lua','Transports.lua','Trams.lua','CityNavigation.lua',
       'Journey.lua','QuestNavigation.lua']
for strength in [4,3,5]:
 # Each strength starts cold, including terrain, portal and path-reuse caches.
 l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
 for f in files:l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
 l.globals().strength=strength
 l.execute('''
UnitGUID=function() return 'Player-1-QuestFlight' end;UnitFactionGroup=function() return 'Alliance' end;UnitClass=function() return 'Warrior','WARRIOR',1 end
GetMoney=function() return 1000000 end
C_QuestLog={GetNumQuestLogEntries=function() return 1 end,GetInfo=function() return {questID=1248,title='The Missing Diplomat',level=33} end,IsComplete=function() return true end}
 A.InitStore({preferRoads=true,roadPreferenceStrength=strength})
 local c=A.Flights.Character();c.nodes={[28]=true,[26]=true};c.offers={}
 assert(#A.Flights.Edges({faction='Alliance'})==0,'known nodes cannot invent an unobserved offer')
 c.offers={[28]={[26]={from=28,to=26,fare=100,hops={28,26}}}}
 assert(#A.Flights.Edges({faction='Alliance'})==1)
 local target=assert(A.QuestNavigation.RouteTarget(A.QuestNavigation.Locations(1248)[1]))
 local plan,why;local slices,paths,cells,flightsSeen=0,0,0,nil
 local finalProgress
 A.PlanningJob.Start(function()
  local result,reason=A.Journey.Plan({mapID=1440,x=.852,y=.446},target,{faction='Alliance'})
  finalProgress=A.PlanningJob.Progress();return result,reason
 end,function(p) plan=p end,function(r) why=r end)
 while A.PlanningJob.IsRunning() and slices<3000 do
  A.PlanningJob.Step();slices=slices+1;local p=A.PlanningJob.Progress();if p then paths=p.paths;cells=p.cells;flightsSeen=p.flightRoutes or flightsSeen end
 end
 assert(plan,why or 'known flight journey did not finish')
 paths=finalProgress.paths;cells=finalProgress.cells;flightsSeen=finalProgress.flightRoutes or flightsSeen
 local flight,boat=false,false
 for _,leg in ipairs(plan.legs) do
  if leg.kind=='walk' then assert(A.Terrain.Validate(leg),'the selected walking legs must retain valid terrain geometry') end
  if leg.transport then
   if leg.transport.kind=='flight' then assert(leg.transport.fromNodeID==28 and leg.transport.toNodeID==26);flight=true end
   if leg.transport.kind=='boat' then boat=true end
  end
 end
 assert(flight and boat,'the recorded flight and onward boat must be considered together')
 assert(flightsSeen==1,'progress must expose the actual eligible recorded flight count')
 assert(paths<16 and cells<1000000,'unrelated walking candidates must not starve the useful flight journey')
 print('Mikhail road strength',strength,'flight+boat',slices,'slices',paths,'paths',cells,'cells')
''')
print('PASS: recorded-flight quest journey finishes at Balanced/Firm/Strong without weakening discovery or search limits')
