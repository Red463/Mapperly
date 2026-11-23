"""Real Southshore to Goldshire must compare complete flight-plus-walk journeys."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/native_flights.py'))['lua']
for f in ['Data/Roads.lua','Roads.lua','Data/Structures.lua','Structures.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
local F=A.Flights
A.InitStore({});local c=F.Character();c.nodes={[14]=true,[6]=true,[2]=true,[4]=true}
c.offers={[14]={[2]={from=14,to=2,fare=500,hops={14,6,2}},[4]={from=14,to=4,fare=600,hops={14,6,2,4}}}}
local source=A.FlightData.nodes[14]
local destination={mapID=1429,x=.425,y=.655,name='Goldshire'}
local stormwind=A.FlightData.nodes[2]
local exit
for _,e in ipairs(A.CrossingData.edges) do
 if e.a.mapID==1453 and e.b.mapID==1429 then exit=e.a end
 if e.b.mapID==1453 and e.a.mapID==1429 then exit=e.b end
end
assert(exit and A.WalkingRegions.Get(stormwind.a)==A.WalkingRegions.Get(exit),'Stormwind flight handoff must connect to its existing Elwynn exit')
assert(stormwind.landingZ==stormwind.z,'city landing must retain actual native pad height, not root terrain height')
local function plan(offers)
 c.offers[14]=offers
 local route,why=A.TravelNetwork.Plan(source.a,destination,{speed=7,preferRoads=true,faction='Alliance'})
 assert(route,why)
 local landing
 for _,leg in ipairs(route.legs) do if leg.transport and leg.transport.kind=='flight' then landing=leg.transport.toNodeID end end
 print('Southshore-Goldshire',landing,math.floor(route.distance),math.floor(route.estimatedSeconds))
 return route,landing
end
local offers=c.offers[14]
local both,landing=plan(offers)
local stormwind=plan({[2]=offers[2]})
local sentinel=plan({[4]=offers[4]})
assert(stormwind.estimatedSeconds<sentinel.estimatedSeconds,'fixture must establish the faster full journey')
assert(landing==2,'choose Stormwind instead of Sentinel Hill when its complete route is faster')
''')
print('PASS: native Southshore-Goldshire selects the faster Stormwind flight and walking connection')
