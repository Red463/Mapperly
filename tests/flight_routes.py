"""Observed offered itineraries, whole fares and affirmative boarding access."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_discovery.py'))['lua']
for f in ['Terrain.lua','TravelNetwork.lua','Transports.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
A.InitStore({});A.FlightData={version=1,build=99,nodes={},segments={}}
A.CrossingData={version=1,build=99,maps={[100]={name='Source',west=1000,north=1000,width=1000,height=1000,instance=0},[200]={name='Destination',west=0,north=1000,width=1000,height=1000,instance=0}},edges={}}
A.TerrainData={version=1,zones={}}
for _,map in ipairs({100,200}) do A.TerrainData.zones[map]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
local function node(id,map,x,world)
 return {id=id,name='Master '..id,factionMask=1,a={mapID=map,x=x,y=.5},world={worldX=world,worldY=500,instance=0},z=10}
end
A.FlightData.nodes[2]=node(2,100,.5,500);A.FlightData.nodes[4]=node(4,200,.5,-500);A.FlightData.nodes[5]=node(5,100,1,0)
A.FlightData.segments['2:5']={seconds=10,cost=30,path={{worldX=500,worldY=500,instance=0},{worldX=0,worldY=500,instance=0}}}
A.FlightData.segments['5:4']={seconds=10,cost=40,path={{worldX=0,worldY=500,instance=0},{worldX=-500,worldY=500,instance=0}}}
local guid='Player-A';local side='Alliance';local taxi=false;local money=100
UnitGUID=function() return guid end;UnitFactionGroup=function() return side end;UnitClass=function() return 'Mage','MAGE' end
UnitOnTaxi=function() return taxi end;GetMoney=function() return money end
local F=A.Flights;local c=F.Character();c.nodes={[2]=true,[4]=true};c.offers={[2]={[4]={from=2,to=4,fare=90,hops={2,5,4}}}}
assert(type(F.Edges)=='function','flight availability adapter must exist')
local e=F.Edges({});assert(#e==1 and e[1].transport.kind=='flight')
local r=e[1].transport
assert(r.fare==90 and not r.fareEstimated,'whole itinerary quote must not be duplicated or split')
assert(not c.nodes[5],'offered transit through an intermediate node does not discover it')
assert(#F.Path(r)>=4,'complete matched native itinerary should supply real flight geometry')
assert(r.fromNodeID==2 and r.toNodeID==4)
money=10;assert(#F.Edges({})==0,'known unaffordable quote must be excluded')
c.offers[2][4].fare=0;money=0;assert(#F.Edges({})==1,'free offered flights remain valid')
c.offers[2][4].fare=nil;c.offers[2][4].hops=nil;money=100
e=F.Edges({});assert(#e==1 and e[1].transport.fare==nil,'missing fare cannot become free')
local p=F.Path(e[1].transport);assert(p[2].breakBefore,'unverified geometry cannot draw a straight flight shortcut')
A.db.useFlights=false;assert(#F.Edges({})==0);A.db.useFlights=true
guid='Player-B';assert(#F.Edges({})==0,'alts cannot use another character offerings');guid='Player-A'
A.FlightData.nodes[4].factionMask=2;assert(#F.Edges({})==0);A.FlightData.nodes[4].factionMask=1
A.FlightData.nodes[4].classToken='DRUID';assert(#F.Edges({})==0);A.FlightData.nodes[4].classToken=nil
guid=nil;assert(#F.Edges({})==0);guid='Player-A'
F.open=true;F.source=2;F.sessionGUID=guid
local here={mapID=100,x=.51,y=.5};local context=assert(F.BoardingContext(here))
F.Closed()
e=F.Edges({start=here,boardingContext=context});assert(e[1].from==here,'an already-proven boarding position survives taxi-window closure during planning')
taxi=true;assert(not F.BoardingContext(here),'in-air position cannot become a walking boarding exception')
taxi=false
c.offers[2][4].fare=90;c.offers[2][4].hops={2,5,4}
assert(#A.Transports.Edges({})==1,'observed flights must join the mixed travel network')
local plan=assert(A.TravelNetwork.Plan({mapID=100,x=.5,y=.5},{mapID=200,x=.5,y=.5},{speed=7}))
assert(plan.hasTransports and plan.flightCost==90,'mixed preview must account for the whole offered fare once')
local flight
for _,leg in ipairs(plan.legs) do if leg.transport then flight=leg end end
assert(flight and flight.name:match('Flight:'))
local state={};local aim,message,arrived=A.Transports.Guide(flight,{mapID=100,x=.5,y=.5},state)
assert(not arrived and message:match('flight master'))
taxi=true;aim,message,arrived=A.Transports.Guide(flight,nil,state)
assert(not aim and not arrived and message:match('Flying'),'airborne arrow cannot direct towards a walking bend')
taxi=nil;aim,message,arrived=A.Transports.Guide(flight,{mapID=200,x=.5,y=.5},state)
assert(not arrived,'unreadable taxi status cannot be interpreted as landing')
taxi=false;UnitPosition=function() return 500,-500,10 end
aim,message,arrived=A.Transports.Guide(flight,{mapID=200,x=.5,y=.5},state)
assert(arrived,'seen flight followed by valid landing should advance')
state={};aim,message,arrived=A.Transports.Guide(flight,{mapID=200,x=.5,y=.5},state)
assert(not arrived and state.needsConfirmation,'UI close or simply reaching an endpoint must not invent a completed flight')
assert(A.Transports.CanDisembark(flight.transport,{mapID=200,x=.5,y=.5},state,true))
local now=0;GetTime=function() return now end
state={};taxi=true;F.Guide(flight,nil,state);taxi=false
F.Guide(flight,{mapID=100,x=.5,y=.5},state);now=3
F.Guide(flight,{mapID=100,x=.5,y=.5},state)
assert(state.interrupted,'a stable early landing should trigger recovery, never a fake destination arrival')
F.WorldChanged(false);assert(not select(3,F.Guide(flight,{mapID=200,x=.5,y=.5},state)))
F.WorldChanged(true)
state={};taxi=true;F.Guide(flight,nil,state);taxi=false;now=10
F.Guide(flight,{mapID=100,x=.5,y=.5},state)
F.WorldChanged(false);now=100;F.WorldChanged(true)
F.Guide(flight,{mapID=100,x=.5,y=.5},state)
assert(not state.interrupted,'loading elapsed time cannot count as stable on-foot landing evidence')
-- Separate offered flights still share the character's single money balance.
A.TerrainData.zones[300]=A.TerrainData.zones[200]
A.CrossingData.maps[300]={name='Third zone',west=-1000,north=1000,width=1000,height=1000,instance=0}
A.FlightData.nodes[8]=node(8,300,.5,-1500);c.nodes[8]=true
A.FlightData.segments['4:8']={seconds=10,cost=80,path={{worldX=-500,worldY=500,instance=0},{worldX=-1500,worldY=500,instance=0}}}
c.offers[4]={[8]={from=4,to=8,fare=80,hops={4,8}}};money=100
assert(not A.TravelNetwork.Plan({mapID=100,x=.5,y=.5},{mapID=300,x=.5,y=.5},{}),'two individually affordable flights cannot exceed the total quoted budget')
''')
print('PASS: observed directed flight availability, whole fares, unknown geometry and boarding snapshots')
