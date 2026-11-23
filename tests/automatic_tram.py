"""Bundled tram service must work without any player recording/setup."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/run.py'))['lua']
l.execute("""
A.InitStore({})
assert(A.TramData and #A.TramData.edges==2,'bundle both fixed tram directions')
assert(not A.RecordedTransports and not A.NavigationSettings.connectionsButton,'player recording workflow must not load or appear')
assert(A.Transports.HasMethod('tram'))
local edges=A.Transports.Edges({});local n=0
for _,edge in ipairs(edges) do if edge.transport.kind=='tram' then n=n+1 end end
assert(n==2,'tram must be available on a fresh character with no recorded trips')
A.db.useTrams=false;for _,edge in ipairs(A.Transports.Edges({})) do assert(edge.transport.kind~='tram') end
A.db.useTrams=true
UnitOnTaxi=function()return false end;UnitInVehicle=function()return false end;IsSwimming=function()return false end
for _,row in ipairs(A.TramData.edges) do
 local state={};local x,y,i=A.TravelNetwork.World(row.a)
 UnitPosition=function()return y,x,row.boardingGroundHeight,i end
 local aim,text,done=A.Transports.Guide({transport=row},row.a,state)
 assert(not done and text,'source station must not finish the trip')
 UnitPosition=function()return 0,0,0,369 end
 aim,text,done=A.Transports.Guide({transport=row},nil,state)
 assert(state.interiorSeen and not done and not aim and text,'tram interior must retain ride instruction without city projection')
 UnitPosition=nil;aim,text,done=A.Transports.Guide({transport=row},nil,state);assert(not done,'loading cannot finish the trip')
 x,y,i=A.TravelNetwork.World(row.b)
 UnitPosition=function()return y,x,row.arrivalGroundHeight-4.252,i end
 assert(A.Transports.CanDisembark(row,row.b,state),'destination-city portal transition does not require an exact floor height')
 UnitPosition=function()return y,x,row.arrivalGroundHeight,i end
 assert(A.Transports.CanDisembark(row,row.b,state),'paired city exit must finish automatically without player confirmation')
 local flightState=A.Flights;A.Flights={worldReady=false}
 assert(not A.Transports.CanDisembark(row,row.b,state),'loading must not accept stale destination coordinates')
 local loadingState={};UnitPosition=function()return 0,0,0,369 end
 A.Transports.Guide({transport=row},nil,loadingState);assert(not loadingState.interiorSeen,'loading must not establish station-entry evidence from a stale instance')
 UnitPosition=function()return y,x,row.arrivalGroundHeight,i end
 A.Flights=flightState
 assert(not A.Transports.CanDisembark(row,row.b,{}),'destination XY alone cannot infer a witnessed tram ride')
 UnitPosition=function()return y+100,x,0,i end
 assert(not A.Transports.CanDisembark(row,row.b,state),'native/map disagreement must reject')
 UnitPosition=function()return y,x,0,i end
 assert(A.Transports.CanDisembark(row,row.b,state),'witnessed portal exit may use the certified safe-location floor with zero native Z')
 local savedSecret=issecretvalue;local secret={};issecretvalue=function(v)return v==secret end
 UnitPosition=function()return secret,secret,secret,secret end
 LibStub=function()return {GetPlayerWorldPosition=function()return x,y,i end}end
 assert(A.Transports.CanDisembark(row,row.b,state),'public map/HBD position must support a witnessed exit when native coordinates are protected')
 local observed={}
 LibStub=function()return {GetPlayerWorldPosition=function()return 0,0,369 end}end
 A.Transports.Guide({transport=row},nil,observed);assert(observed.interiorSeen,'public station instance must work when native position is protected')
 UnitPosition=function()return secret,secret,secret,0 end
 assert(not A.Transports.CanDisembark(row,row.b,state),'public native instance cannot bypass a conflicting public HBD station instance')
 LibStub=function()return nil end
 UnitPosition=function()return secret,x+100,secret,0 end
 assert(not A.Transports.CanDisembark(row,row.b,state),'one readable conflicting native axis must reject arrival')
 UnitPosition=function()return secret,secret,secret,secret end
 LibStub=function()return {GetPlayerWorldPosition=function()return x+100,secret,0 end}end
 assert(not A.Transports.CanDisembark(row,row.b,state),'one readable conflicting HBD axis must reject arrival')
 issecretvalue=savedSecret;LibStub=function()return nil end
 UnitPosition=function()return y,x,0,369 end
 assert(not A.Transports.CanDisembark(row,row.b,state),'stale city position while still inside station cannot arrive')
end
""")
print('PASS: fresh-character bundled tram, independent switch, witnessed interior/loading and automatic paired floor arrival')
