"""A cross-continent itinerary should not exhaust its budget on nearby detours."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_route_matrix import runtime

# Use a reproducible set of synthetic flight offers, independent of player data.
lua = runtime(profile='firm', flights=True)
lua.execute("""
local origin={mapID=1453,x=.633205,y=.810596}
local destination={mapID=1443,x=.646717,y=.104367}
local plan,reason,work
A.PlanningJob.Start(function()
    local result,why=A.Journey.Plan(origin,destination,{liveStart=true,faction='Alliance'})
    work=A.PlanningJob.Progress()
    return result,why
end,function(p) plan=p end,function(why) reason=why end)
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(plan,reason)
local boat=false
for _,leg in ipairs(plan.legs) do
    if leg.kind=='walk' and not leg.cityGuidance and not leg.portalGuidance then
        assert(A.Terrain.Validate(leg))
    end
    if leg.transport and leg.transport.kind=='boat' then boat=true end
end
local last=plan.points[#plan.points]
assert(last.mapID==destination.mapID and last.x==destination.x and last.y==destination.y)
assert(boat and work.flightRoutes==36 and work.paths<60)
print('PASS: Stormwind to Desolace with synthetic flights',work.paths,'paths',work.cells,'cells')
""")
