"""Mikhail's real quest spawn needs a bounded nearby walkable endpoint."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/QuestLocations.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelBounds.lua','TravelNetwork.lua','Transports.lua','Journey.lua','QuestNavigation.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute('''
A.InitStore({});UnitFactionGroup=function() return 'Alliance' end
C_QuestLog={GetNumQuestLogEntries=function() return 1 end,GetInfo=function() return {questID=1248,title='The Missing Diplomat',level=33} end,IsComplete=function() return true end}
local Q=A.QuestNavigation
local listed=Q.Locations(1248);assert(#listed==1 and listed[1].label=='Mikhail')
local raw=listed[1]
assert(not A.Terrain.Segment({mapID=raw.map,x=raw.x,y=raw.y},{mapID=raw.map,x=raw.x,y=raw.y}),'reported NPC point must reproduce blocked destination')
local target=assert(Q.RouteTarget(raw))
assert(target.approachDistance>3 and target.approachDistance<4,'Mikhail approach must be the verified nearby permitted cell')
assert(target.name:find('approach',1,true),'adjusted routing target must be explicit')
assert(target.questTarget.x==raw.x and target.questTarget.y==raw.y,'exact quest location must remain separate')
local p={mapID=target.map,x=target.x,y=target.y}
assert(A.Terrain.Segment(p,p) and A.WalkingRegions.Get(p)==1)
local rawAgain=Q.Locations(1248)[1];assert(rawAgain.x==raw.x and rawAgain.y==raw.y,'listing cannot silently move the NPC')
local result,why;local slices=0
A.PlanningJob.Start(function() return A.Journey.Plan({mapID=1440,x=.852,y=.446},target,{faction='Alliance'}) end,function(r) result=r end,function(r) why=r end)
while A.PlanningJob.IsRunning() and slices<3000 do A.PlanningJob.Step();slices=slices+1 end
assert(result,why or 'screenshot journey did not finish')
assert(result.hasTransports,'reported cross-continent journey must retain a real transport')
A.db.navigationMode='direct'
local exact=assert(Q.RouteTarget(raw));assert(exact.x==raw.x and exact.y==raw.y and not exact.approachDistance,'direct mode must retain exact quest coordinates')
A.db.navigationMode='terrain'
local approach=A.Terrain.Approach;A.Terrain.Approach=function() return nil,'no approach' end
local unavailable,reason=Q.RouteTarget(raw)
assert(not unavailable and reason:find('nearby',1,true),'no bounded approach must fail explicitly instead of weakening terrain rules')
A.Terrain.Approach=approach
print('Mikhail nearby approach:',target.approachDistance,'yd; screenshot route:',#result.legs,'legs;',slices,'slices')
''')
print('PASS: actual blocked quest point, bounded approach route, exact source retention and direct-mode behavior')
