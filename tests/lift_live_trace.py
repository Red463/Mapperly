"""Replay Forever71037's zero-altitude Great Lift capture against real data."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/native_local_transports.py'))['lua']
lua.execute('''
local T,P=A.Transports,A.TravelNetwork
A.InitStore({});A.LocalTransportData.build=70959
local row=A.LocalTransportData.edges[1];local state={}
local plan,why=A.Journey.Plan(row.a,{mapID=1441,x=.2922,y=.3425},{})
assert(plan,why);A.Journey.Install(plan)
-- Capture: waiting/approach, shaft, vertical-ride projection, walk off, clear ground.
local trace={
 {-4622.077,-1856.072}, {-4643.702,-1854.578},
 {-4661.586,-1852.166}, {-4670.851,-1849.807},
 {-4689.645,-1855.970}, {-4703.071,-1881.235}}
for i,v in ipairs(trace) do
 local p=P.Transform({worldX=v[2],worldY=v[1],instance=1},1441)
 UnitPosition=function() return v[1],v[2],0,1 end
 local _,message,arrived=T.Guide({transport=row},p,state)
 A.Journey.Update(p,true)
 if i==1 then
  assert(not state.departed,'zero is an unavailable altitude here, not proof the waiting player is riding')
  assert(not message:find('Stay aboard',1,true))
 end
 if i<=4 then assert(not arrived,'the tower/shaft projection must never complete a zero-height lift') end
 if i==#trace then
  assert(arrived,'verified clear destination ground must resume walking despite zero height and an alternate exit')
  assert(A.Journey.Leg().kind=='walk','the real follower must leave the lift step and resume its planned walking leg')
 end
end
for _,service in ipairs(A.LocalTransportData.edges) do
 local exit=service.arrivalExits[1]
 local x,y,instance=P.World(exit)
 local p={mapID=exit.mapID,x=exit.x,y=exit.y}
 UnitPosition=function() return y,x,0,instance end
 assert(select(3,T.Guide({transport=service},p,{})),'both directions must accept checked exit ground with unavailable altitude')
 UnitPosition=function() return y,x,service.boardingGroundHeight,instance end
 assert(not select(3,T.Guide({transport=service},p,{})),'readable opposite-floor height cannot borrow a clear exit exemption')
 UnitPosition=function() return y+20,x,service.boardingGroundHeight,instance end
 assert(not T.CanDisembark(service,p,{}),'contradictory live XY must not be treated as unavailable height')
 UnitPosition=function() return y,x,service.boardingGroundHeight,369 end
 assert(not T.CanDisembark(service,p,{}),'contradictory live instance must not borrow an exit exemption')
 UnitPosition=nil
 assert(select(3,T.Guide({transport=service},p,{})),'checked ground can recover a protected height without requiring the old marker')
end
''')
print('PASS: live zero-height lift trace rejects waiting/shaft and recognises clear destination ground')
