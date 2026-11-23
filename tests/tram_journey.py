"""Actual native portal-to-city journey plans and follows without setup."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
files=['Store.lua','Data/Terrain.lua','Data/Water.lua','Water.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Trams.lua','Data/WalkingPaths.lua','Roads.lua','Terrain.lua','PathReuse.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelBounds.lua','TravelNetwork.lua','Transports.lua','Trams.lua','Journey.lua']
for name in files:l.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text(encoding='utf8'))
l.execute("""
A.InitStore({preferRoads=false});UnitFactionGroup=function()return 'Alliance'end
UnitOnTaxi=function()return false end;UnitInVehicle=function()return false end;IsSwimming=function()return false end
for _,row in ipairs(A.TramData.edges) do
 assert(A.Terrain.Segment(row.a,row.a) and A.Terrain.Segment(row.b,row.b),'native city portal handoffs must be permitted')
 local goal=assert(A.Terrain.Approach({mapID=row.b.mapID,x=row.b.x+.01,y=row.b.y},30))
 local found,why,slices
 A.PlanningJob.Start(function()return A.Journey.Plan(row.a,goal,{maxWalkingCells=350000})end,function(p)found=p end,function(e)why=e end)
 slices=0;while A.PlanningJob.IsRunning()and slices<5000 do A.PlanningJob.Step();slices=slices+1 end
 assert(found,why or 'tram plan did not finish');assert(found.hasTransports)
 local tram;for _,leg in ipairs(found.legs)do if leg.transport and leg.transport.kind=='tram'then tram=leg.transport end end
 assert(tram and tram.id==row.id,'native fresh-character plan must select correct tram direction')
 A.Journey.Install(found)
 local x,y,i=A.TravelNetwork.World(row.a);UnitPosition=function()return y,x,row.boardingGroundHeight,i end
 A.Journey.Update(row.a,true);assert(A.Journey.Leg().kind=='walk','walk stage remains until the portal is entered')
 UnitPosition=function()return 0,0,0,369 end;A.Journey.Update(nil,true);assert(A.Journey.transportState.interiorSeen)
 x,y,i=A.TravelNetwork.World(row.b);UnitPosition=function()return y,x,row.arrivalGroundHeight,i end
 A.Journey.Update(row.b,true);assert(A.Journey.Leg().kind=='walk','city portal exit must automatically advance to onward walking')
 print('Native tram',row.fromName,'to',row.toName,'planned in',slices,'slices')
end
""")
print('PASS: both native tram directions plan/follow from permitted station approaches and automatically hand off to walking')
