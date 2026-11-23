"""Budget-aware search retains slower cheap prefixes after a common flight edge."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/flight_routes.py'))['lua']
lua.execute('''
local F=A.Flights
A.InitStore({});A.FlightData={version=1,build=99,nodes={},segments={}}
A.CrossingData={version=1,build=99,maps={},edges={}}
A.TerrainData={version=1,zones={}}
UnitGUID=function() return 'Player-Budget' end;UnitFactionGroup=function() return 'Alliance' end;UnitClass=function() return 'Mage','MAGE' end
GetMoney=function() return 100 end
local c=F.Character()
for i=1,5 do
 local map=100+i
 A.CrossingData.maps[map]={name='Node '..i,west=10000-i*1000,north=1000,width=1000,height=1000,instance=0}
 A.TerrainData.zones[map]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}}
 A.FlightData.nodes[i]={id=i,name='Node '..i,factionMask=1,a={mapID=map,x=.5,y=.5},world={worldX=9500-i*1000,worldY=500,instance=0},z=10}
 c.nodes[i]=true
end
local function edge(a,b,fare,seconds)
 c.offers[a]=c.offers[a] or {};c.offers[a][b]={from=a,to=b,fare=fare,hops={a,b}}
 A.FlightData.segments[a..':'..b]={seconds=seconds,cost=fare,path={A.FlightData.nodes[a].world,A.FlightData.nodes[b].world}}
end
edge(1,2,90,1);edge(1,3,0,10);edge(3,2,0,10);edge(2,4,0,1);edge(4,5,20,1)
local p,why=A.TravelNetwork.Plan({mapID=101,x=.5,y=.5},{mapID=105,x=.5,y=.5},{speed=7})
assert(p and p.flightCost==20,'slower affordable prefix must survive faster expensive prefix: '..tostring(why))
''')
print('PASS: nondominated time/fare prefixes preserve affordable multi-flight journeys')
