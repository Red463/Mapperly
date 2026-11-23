"""Floor-aware lift arrival, missing height and tram interior/loading guidance."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/transports.py'))['lua']
lua.execute('''
local T=A.Transports
A.InitStore({});A.TransportData.build=42
local p={mapID=100,x=.5,y=.5}
local row={id='lift',kind='lift',name='Test lift',faction='Neutral',a=p,b=p,
 board={worldX=500,worldY=500,instance=0},arrival={worldX=500,worldY=500,instance=0},
 boardingGroundHeight=100,arrivalGroundHeight=0,toName='Lower landing',planningSeconds=90}
A.TransportData.edges={row}
assert(#T.Edges({})==1);A.db.useLifts=false;assert(#T.Edges({})==0);A.db.useLifts=true
local state={};local height=100
UnitPosition=function() return 500,500,height,0 end
local _,text,done=T.Guide({transport=row},p,state)
assert(not done and text:find('lift',1,true),'same XY at departure cannot complete a vertical trip')
height=70;_,text,done=T.Guide({transport=row},p,state)
assert(not done and state.departed and text:find('Stay aboard',1,true),'vertical motion must register departure')
_,text,done=T.Guide({transport=row},nil,state);assert(not done,'loading must retain the trip')
height=0;assert(select(3,T.Guide({transport=row},p,state)),'destination floor must finish the lift')
state={};height=0
assert(select(3,T.Guide({transport=row},p,state)),'verified destination floor must recover missed boarding without requiring a departure sample')
assert(T.CanDisembark(row,p,state,true),'explicit confirmation may acknowledge a destination floor')
state={};height=70
_,text,done=T.Guide({transport=row},p,state)
assert(not done and state.departed and text:find('Stay aboard',1,true),'first readable sample mid-ride must not remain on Board the lift')
state={};height=0
local nearExit={mapID=100,x=.53,y=.5}
UnitPosition=function() return 500,470,height,0 end
local aim;aim,text,done=T.Guide({transport=row},nearExit,state)
assert(not done and aim and text:find('landing marker',1,true),'near the destination floor, guide to the dry handoff instead of saying Stay aboard forever')
UnitPosition=function() return 500,500,height,0 end
state={};height=100;T.Guide({transport=row},p,state)
assert(not T.CanDisembark(row,p,state,true),'confirmation must reject a readable wrong floor')
height=60;T.Guide({transport=row},p,state);UnitPosition=nil
assert(not select(3,T.Guide({transport=row},p,state)) and state.needsConfirmation,'protected height needs confirmation')
assert(T.CanDisembark(row,p,state,true))
state={};row.kind='tram';row.interiorInstance=369;row.boardingGroundHeight=nil;row.arrivalGroundHeight=nil
UnitPosition=function() return 10,20,0,369 end
_,text,done=T.Guide({transport=row},nil,state)
assert(not done and state.departed and text:find('tram',1,true),'tram interior must keep manual ride instructions during missing map coverage')
UnitPosition=nil;_,text,done=T.Guide({transport=row},nil,state)
assert(not done and text,'loading cannot drop tram guidance')
''')
print('PASS: lift floor/departure guards, protected height, explicit confirmation and tram interiors')
