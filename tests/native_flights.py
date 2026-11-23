"""Pinned flight inventory, native approaches and real Stormwind outbound plan."""
from pathlib import Path
import runpy, json, hashlib
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_routes.py'))['lua']
for f in ['Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Flights.lua','WalkingRegions.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
audit=json.loads((root/'tools/data/native-flights-70959.json').read_text(encoding='utf-8-sig'))
assert lua.eval('A.FlightData.sourceSha256')==hashlib.sha256((root/'tools/data/native-flights-70959.json').read_bytes()).hexdigest()
assert sum(n['eligible'] for n in audit['nodes'])==65
assert sum(e['eligible'] for e in audit['edges'])==286
lua.execute('''
local F=A.Flights
A.InitStore({});F.WorldChanged(true)
UnitGUID=function() return 'Player-Native' end;UnitFactionGroup=function() return 'Alliance' end;UnitClass=function() return 'Mage','MAGE' end
GetMoney=function() return 1000000 end;UnitOnTaxi=function() return false end
local total,available,segments=0,0,0
for id,n in pairs(A.FlightData.nodes) do
 total=total+1
 if n.destinationAvailable then assert(A.Terrain.Segment(n.a,n.a));available=available+1 else assert(id==30) end
end
for _,edge in pairs(A.FlightData.segments) do assert(#edge.path>=2 and edge.seconds>0 and edge.cost>=0);segments=segments+1 end
assert(total==65 and available==64 and segments==286)
assert(#F.Edges({})==0,'native geometry alone must never unlock flights')
local source,target=A.FlightData.nodes[2],A.FlightData.nodes[4]
local c=F.Character();c.nodes={[2]=true,[4]=true};c.offers={[2]={[4]={from=2,to=4,fare=110,hops={2,4}}}}
local p=assert(A.Transports.Aim(source.world,source.a.mapID))
F.open=true;F.source=2;F.sessionGUID='Player-Native'
local context=assert(F.BoardingContext(p));F.Closed()
local plan,reason=A.TravelNetwork.Plan(p,target.a,{boardingContext=context,speed=7})
assert(plan,reason);assert(plan.hasTransports and plan.flightCost==110)
local flight
for _,leg in ipairs(plan.legs) do if leg.transport then flight=leg end end
assert(flight.transport.fromNodeID==2 and flight.transport.toNodeID==4)
assert(A.FlightData.nodes[6].landingZ<550,'Ironforge must retain native underground pad, never MCVT roof height')
assert(A.FlightData.nodes[11].landingZ<0,'Undercity must retain native underground pad')
''')
print('PASS: 65 pinned masters, 64 permitted handoffs, 286 native segments and live-source Stormwind flight plan')
