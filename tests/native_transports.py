"""Native scheduled journeys and bounded legacy walking regressions."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Roads.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelNetwork.lua','Transports.lua','Journey.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
A.InitStore({})
io.stdout:setvbuf('no')
assert(#A.TransportData.edges==25)
assert(#A.Transports.Edges({faction='Alliance'})==17)
assert(#A.Transports.Edges({faction='Horde'})==12)
assert(#A.Transports.Edges({})==4)
for _,row in ipairs(A.TransportData.edges) do
 local state={}
 assert(not select(3,A.Transports.Guide({transport=row},row.a,state)),'native service cannot finish at its departure approach')
 assert(not select(3,A.Transports.Guide({transport=row},nil,state)),'loading cannot invent an arrival')
 local east,north=A.TravelNetwork.World(row.b)
 UnitPosition=function() return north,east,row.arrivalGroundHeight end
 assert(select(3,A.Transports.Guide({transport=row},row.b,state)),'all native destinations need a valid on-ground handoff')
end
UnitPosition=nil
local function plan(a,b,side)
 local result,reason;A.PlanningJob.Start(function() return A.Journey.Plan(a,b,{faction=side,preferRoads=true}) end,function(p) result=p end,function(r) reason=r end)
 local steps=0;while A.PlanningJob.IsRunning() and steps<5000 do A.PlanningJob.Step();steps=steps+1 end
 assert(result,reason or 'native scheduled route did not finish')
 assert(steps<2000,'transport integration must retain bounded useful planning latency')
 print(a.name or a.mapID,b.name or b.mapID,#result.legs,math.floor(result.distance),steps)
 return result
end
for _,side in ipairs({'Alliance','Horde'}) do
 local row
 for _,r in ipairs(A.TransportData.edges) do if r.kind=='airship' and r.faction==side then row=r;break end end
 assert(row,'both native Zephras airship services need mapped approaches')
 assert(plan(row.a,row.b,side).hasTransports)
end
local row=A.TransportData.edges[1]
assert(plan(row.a,row.b,'Alliance').hasTransports)
local function service(north,east,map)
 return assert(A.Terrain.Approach(A.TravelNetwork.Transform({worldX=east,worldY=north,instance=A.CrossingData.maps[map].instance},map),30))
end
local ratchet,booty=service(-894.6,-3773,1413),service(-14473,464.1,1434)
assert(A.WalkingRegions.Get(ratchet)==A.WalkingRegions.Get(row.a) and A.WalkingRegions.Get(booty)==A.WalkingRegions.Get(row.b),'boat handoffs must connect the actual Ratchet and Booty Bay town regions')
assert(plan(ratchet,booty,'Alliance').hasTransports)
local stormwind,auberdine=service(-8797.43,1083.47,1453),service(6341.4,557.7,1439)
local stormwindEdge
for _,e in ipairs(A.TransportData.edges) do if e.pathID==11616 and e.a.mapID==1453 then stormwindEdge=e;break end end
assert(stormwindEdge and A.WalkingRegions.Get(stormwind)==36 and A.WalkingRegions.Get(stormwindEdge.a)==1,'Stormwind boat handoff must use the actual harbour, connected by certified city access')
assert(stormwindEdge.boardingCorridor==7095901454 and A.TravelNetwork.Distance(stormwindEdge.a,stormwindEdge.board)<14)
assert(stormwindEdge.boardingAccess and stormwindEdge.arrivalGroundHeight)
local fromCity=plan(stormwind,auberdine,'Alliance');assert(fromCity.hasTransports)
local pier=A.HarbourAccessData.corridors[7095901454]
local function hasPierPoints(route)
 local found=0
 for _,p in ipairs(route.points) do
  if p.mapID==1453 or p.structure==7095901454 then
   for _,raw in ipairs(pier.worldPath) do
    local x,y=A.TravelNetwork.World(p)
    if (x-raw[1])^2+(y-raw[2])^2<.0001 then found=found+1;break end
   end
  end
 end
 assert(found>=#pier.worldPath,'boat approach must include the full certified pier instead of a swimming shortcut')
end
hasPierPoints(fromCity)
local returning=plan(auberdine,stormwind,'Alliance');assert(returning.hasTransports);hasPierPoints(returning)
local transitIndex
for i,leg in ipairs(returning.legs) do if leg.transport and leg.transport.arrivalCorridor then transitIndex=i;break end end
A.Journey.Install(returning);A.Journey.legIndex=transitIndex
A.Journey.index=returning.legs[transitIndex].first
local wx,wy=A.TravelNetwork.World(pier.a);UnitPosition=function() return wy,wx,0,0 end
local nextAim=A.Journey.Update(pier.a,true)
assert(nextAim and A.TravelNetwork.Distance(nextAim,pier.b)>150,'stepping clear of the boat must not point back to the start of the pier')
UnitPosition=nil
local origin,destination
for _,r in ipairs(A.TransportData.edges) do
 if r.pathID==11167 and r.fromName=='Menethil Harbor' then origin=r.a end
 if r.pathID==11167 and r.toName=='Auberdine' then destination=r.b end
end
assert(origin and destination)
local through=plan(origin,destination,'Alliance')
assert(#through.legs==3 and through.legs[2].name:find('Stay aboard',1,true),'native three-stop service must preserve through sailing')
local a=assert(A.Terrain.Approach({mapID=1431,x=.77,y=.44},30));a.name='Duskwood'
local b=assert(A.Terrain.Approach({mapID=1426,x=.46,y=.51},30));b.name='Dun Morogh'
plan(a,b,'Alliance')
''')
print('PASS: native scheduled transport plans and long walking route compatibility')
