"""Simple portal instructions must work across Stormwind's indoor mask gap."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(root/'tests/tram_journey.py'))['l']
for name in ['RouteRecovery.lua','RouteSteps.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text(encoding='utf8'))
l.execute("""
A.InitStore({useBoats=false,useZeppelins=false,useAirships=false,useFlights=false,useLifts=false,preferRoads=false})
local sw=assert(A.TravelNetwork.Transform({worldX=455.91745489266,worldY=-8782.60466527114,instance=0},1453))
assert(A.Terrain.Segment(sw,sw))
local outbound,back
for _,r in ipairs(A.TramData.edges)do if r.a.mapID==1453 then outbound=r else back=r end end
local function calculate(a,b)
 local result,why
 A.PlanningJob.Start(function()return A.Journey.Plan(a,b,{maxWalkingCells=60000})end,function(p)result=p end,function(e)why=e end)
 for i=1,5000 do if not A.PlanningJob.IsRunning()then break end;A.PlanningJob.Step()end
 assert(result,why or 'plan unfinished');return result
end
local plan=calculate(sw,outbound.b)
local enter,ride
for _,leg in ipairs(plan.legs)do if leg.portalGuidance then enter=leg end;if leg.transport then ride=leg.transport end end
assert(enter and ride and ride.automaticTram,'main-city start must get portal guidance instead of failing on the station mask gap')
assert(enter.name=='Walk through the Stormwind tram portal')
A.Journey.Install(plan)
UnitPosition=function()return 0,0,0,369 end
A.Journey.Update(nil,true)
assert(A.Journey.Leg().kind=='transport'and A.Journey.transportState.interiorSeen,'entering the station must advance the walk stage even if the last outside position was missed')
UnitPosition=nil
A.Journey.Install(plan)
local aim,message=A.Journey.Update(sw,true)
assert(aim and A.TravelNetwork.Distance(aim,outbound.a)<.001 and not message,'portal leg must guide directly to portal without obstructed/return-to-route warnings')
assert(A.Journey.Pause()and A.Journey.Resume(sw),'coarse portal instruction must pause/resume without requiring a terrain segment')
for i=1,20 do assert(not A.RouteRecovery.Update(sw,i,true).replan,'city streets need not follow a straight portal bearing')end
local text=A.RouteSteps.Describe({kind='transport',transport=outbound})
assert(text=='Ride the tram and exit the Ironforge portal')
-- Reverse: leave the SW portal then receive the normal onward city instruction.
plan=calculate(back.a,sw)
local after
for i,leg in ipairs(plan.legs)do if leg.transport then after=plan.legs[i+1]end end
assert(after and after.portalGuidance,'onward city guidance must not fail at the reverse exit')
A.Journey.Install(plan)
local x,y,instance=A.TravelNetwork.World(back.a);UnitPosition=function()return y,x,0,instance end
A.Journey.Update(back.a,true)
UnitPosition=function()return 0,0,0,369 end;A.Journey.Update(nil,true)
-- Arrival can be sampled away from the exact floor/12yd exit radius.
local emerged={mapID=1453,x=back.b.x+.025,y=back.b.y}
x,y,instance=A.TravelNetwork.World(emerged);UnitPosition=function()return y,x,0,instance end
A.Journey.Update(emerged,true)
assert(A.Journey.Leg().kind=='walk'and A.Journey.Leg().portalGuidance,'destination-city exit must resume walking automatically')
assert(A.TravelNetwork.Distance(A.Journey.Current(),sw)<.001,'onward guidance must aim ahead, not back at the exit')
local resumed=calculate(emerged,sw)
assert(not resumed.hasTransports and resumed.hasPortalGuidance,'replanning after the exit must not send the player on a second round-trip tram ride')
-- The exception is scoped to enabled tram graph endpoints, never general walking.
local edges=A.Transports.Edges({})
assert(not A.Trams.Access(sw,outbound.a,{}))
assert(not A.Trams.Access(sw,outbound.a,edges,false),'certified dock-access composition must be able to prohibit the portal-bearing fallback')
assert(not A.Trams.Access(sw,{mapID=1453,x=.6,y=.6},edges))
local walkingOnly=A.Journey.Plan(emerged,sw,{walkingOnly=true,maxWalkingCells=60000})
assert(not walkingOnly,'walking-only service routing must not use portal-bearing city exceptions')
A.db.useTrams=false;assert(not A.Trams.Access(sw,outbound.a,A.Transports.Edges({})))
""")
print('PASS: source portal -> tram/destination portal -> walking, both directions across city mask gaps')
