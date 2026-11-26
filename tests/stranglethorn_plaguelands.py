"""Replay the reported Firm-road journey through Dun Algaz in both directions."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "tools"))
from benchmark_route_matrix import runtime

for reverse in (False, True):
    lua = runtime(profile="firm")
    lua.globals().reverse = reverse
    lua.execute("""
        A.db.useBoats=false
        A.db.useFlights=false
        local start={mapID=1434,x=.467107,y=.159688}
        local goal={mapID=1423,x=.825708,y=.6939}
        if reverse then start,goal=goal,start end
        local route,reason
        A.PlanningJob.Start(function()
            return A.Journey.Plan(start,goal,{liveStart=true,faction='Alliance'})
        end,function(r) route=r end,function(e) reason=e end,goal,start)
        while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
        assert(route,reason)
        local progress=A.PlanningJob.Recent()[1].progress
        assert(progress.paths<=48,'Too many speculative walking joins: '..progress.paths)
        local first,last=route.points[1],route.points[#route.points]
        assert(first.mapID==start.mapID and last.mapID==goal.mapID)
        assert(math.abs(first.x-start.x)<1e-8 and math.abs(first.y-start.y)<1e-8)
        assert(math.abs(last.x-goal.x)<1e-8 and math.abs(last.y-goal.y)<1e-8)
        local placements={}
        for _,leg in ipairs(route.legs) do
            if leg.kind=='walk' then
                if not (leg.cityGuidance or leg.portalGuidance) then
                    assert(A.Terrain.Validate(leg),'Unwalkable approach on map '..leg.mapID)
                end
                local floor=A.StructureData.corridors[leg.exitStructure]
                if floor then placements[floor.placement]=true end
            else
                assert(leg.transport and leg.transport.kind~='boat' and leg.transport.kind~='flight')
            end
        end
        for _,id in ipairs({68443158,68441769,126354,73025}) do
            assert(placements[id],'Missing Dun Algaz tunnel '..id)
        end
    """)
print("PASS: Stranglethorn Vale to Eastern Plaguelands and back via all four Dun Algaz tunnels")
