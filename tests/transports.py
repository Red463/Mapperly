"""Availability and endpoint binding for directed scheduled transports."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Terrain.lua','TravelNetwork.lua','Transports.lua']:
 if (root/f).exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
assert(A.Transports,'scheduled transport adapter must exist')
A.InitStore({})
A.CrossingData={version=1,build=42,maps={[100]={name='Origin',west=1000,north=1000,width=1000,height=1000,instance=0},[200]={name='Destination',west=1000,north=1000,width=1000,height=1000,instance=1}},edges={}}
A.TerrainData={version=1,zones={}}
for _,id in ipairs({100,200}) do A.TerrainData.zones[id]={status='complete',w=2,h=2,widthYards=1000,heightYards=1000,rows={'w','w'}} end
local a,b={mapID=100,x=.5,y=.5},{mapID=200,x=.5,y=.5}
local boat={id='circle-1',kind='boat',name='Circular ferry',faction='Neutral',a=a,b=b,board={worldX=500,worldY=500,instance=0},arrival={worldX=500,worldY=500,instance=1},planningSeconds=300,path={}}
local zep={id='zep',kind='zeppelin',name='Horde zeppelin',faction='Horde',a=a,b=b,board=boat.board,arrival=boat.arrival,planningSeconds=300,path={}}
A.TransportData={version=1,build=42,edges={boat,zep}}
local T=A.Transports
assert(#T.Edges({faction='Alliance'})==1,'opposing faction policy must be excluded')
assert(#T.Edges({faction='Horde'})==2)
assert(#T.Edges({})==1,'unknown player faction may use verified neutral services only')
A.db.useBoats=false;assert(#T.Edges({faction='Alliance'})==0)
A.db.useBoats=true;A.db.useZeppelins=false;assert(#T.Edges({faction='Horde'})==1)
A.db.useZeppelins=true
boat.faction='Unknown';assert(#T.Edges({faction='Alliance'})==0,'unknown route policy cannot be assumed neutral');boat.faction='Neutral'
assert(T.Edges({faction='Alliance'})[1].from.mapID==100,'directed services must retain source stop')
assert(T.Edges({faction='Alliance'})[1].to.mapID==200,'reverse edge must not be invented')
A.TransportData.build=41;assert(#T.Edges({faction='Alliance'})==0,'stale transport data must not mix with another world build')
A.TransportData.build=42;boat.board.worldX=50
assert(#T.Edges({faction='Alliance'})==0,'an unsupported distant boarding approach must be rejected')
''')
print('PASS: directed transports, faction/preferences, source guards and bounded boarding approaches')
