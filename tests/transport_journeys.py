"""Mixed transport planning and the actual journey follower lifecycle."""
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/transports.py'))['lua']
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'Journey.lua').read_text())
lua.execute('''
A.InitStore({});A.TransportData.build=42
local row=A.TransportData.edges[1];row.board.worldX=500
row.a={mapID=100,x=.5,y=.5};row.b={mapID=200,x=.5,y=.5};row.path={row.board,row.arrival}
local a={mapID=100,x=.4,y=.5};local b={mapID=200,x=.6,y=.5,name='Across the sea'}
local J=A.Journey
local plan,reason=J.Plan(a,b,{});assert(plan,reason)
assert(plan.hasTransports and #plan.legs==3 and plan.legs[2].kind=='transport')
assert(math.abs(plan.distance-200)<.01,'walking distance must not count sea geometry or time-equivalent costs')
assert(math.abs(plan.estimatedSeconds-(300+200/7))<.01)
assert(plan.points[plan.legs[2].first].breakBefore,'boarding handoff cannot pretend to be certified walking geometry')
J.Install(plan)
local aim,why=J.Update(row.a,true)
assert(J.Leg().kind=='transport' and why:find('Board the boat',1,true),'arrival at shore must switch to boarding guidance')
assert(J.active==plan)
local _,lost=J.Update(nil,true);assert(lost and J.active==plan,'loading screens cannot discard transport journey')
assert(not J.Skip(row.a),'skip bend must not skip a transport journey')
J.Pause();assert(select(2,J.Update(row.a,true))=='Paused');assert(J.Resume(nil),'resume transport instructions must not require ground position')
local wrong={mapID=200,x=.1,y=.1};J.Update(wrong,true)
assert(J.Leg().kind=='transport','merely changing continent must not complete transport leg')
row.arrivalGroundHeight=10
UnitPosition=function() return 500,500,100 end
J.Update(row.b,true);assert(J.Leg().kind=='transport','tower arrival cannot finish while the player is still above the ground approach')
UnitPosition=function() return 500,500,10 end
J.Update(row.b,true);assert(J.Leg().kind=='walk' and J.MapID()==200,'destination shore must resume the actual walking leg')
UnitPosition=nil
J.Install(plan);J.Update(row.a,true)
assert(not J.ConfirmTransportArrival(row.a),'confirmation cannot skip a transport from its departure dock')
J.Update(row.b,true);assert(J.Leg().kind=='transport','protected height at a tower needs explicit land confirmation')
assert(J.ConfirmTransportArrival(row.b));J.Update(row.b,true);assert(J.Leg().kind=='walk')
row.arrivalGroundHeight=nil
local _,done=J.Update(b,true);assert(done=='arrived')
A.db.useBoats=false;local failed=J.Plan(a,b,{});assert(not failed,'disabled boats cannot join continents')
A.db.useBoats=true
-- Same-continent ferry: its shortcut competes with the walking route by time.
row.b={mapID=100,x=.9,y=.5};row.arrival={worldX=100,worldY=500,instance=0};row.planningSeconds=20;row.path={row.board,row.arrival}
row.a={mapID=100,x=.1,y=.5};row.board={worldX=900,worldY=500,instance=0}
plan,reason=J.Plan(row.a,row.b,{});assert(plan,reason);assert(plan.hasTransports,'a useful same-map ferry must be considered')
J.Install(plan);J.Update(row.a,true);assert(J.Leg().kind=='transport')
J.Update(row.a,true);assert(J.Leg().kind=='transport','same-map ferry cannot instantly complete at source shore')
J.Update(row.b,true);local _,finished=J.Update(row.b,true);assert(finished=='arrived')
-- Consecutive stops on one vessel must keep the player aboard.
row.a=a;row.b={mapID=200,x=.5,y=.5};row.board={worldX=600,worldY=500,instance=0};row.arrival={worldX=500,worldY=500,instance=1}
row.pathID=999;row.fromNodeID=11;row.toNodeID=12;row.fromName='Origin';row.toName='Intermediate';row.planningSeconds=300
A.CrossingData.maps[300]={name='Final stop',west=1000,north=1000,width=1000,height=1000,instance=2}
A.TerrainData.zones[300]=A.TerrainData.zones[200]
local second={id='circle-2',pathID=999,kind='boat',name='Intermediate to final',faction='Neutral',a=row.b,b={mapID=300,x=.5,y=.5},board=row.arrival,arrival={worldX=500,worldY=500,instance=2},planningSeconds=300,path={},fromNodeID=12,toNodeID=13,fromName='Intermediate',toName='Final stop'}
A.TransportData.edges={row,second}
plan,reason=J.Plan(a,second.b,{});assert(plan,reason)
assert(#plan.legs==3,'same-vessel continuation must not require disembarking and boarding again')
J.Install(plan);J.Update(a,true);J.Update(row.b,true)
assert(J.Leg().kind=='transport','intermediate shore must not finish a through sailing')
J.Update(second.b,true);assert(select(2,J.Update(second.b,true))=='arrived')
''')
print('PASS: mixed time-based planning, boarding/loading/arrival, same-map ferry and preferences')
