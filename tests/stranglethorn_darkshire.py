"""A player south of the Stranglethorn chasm can walk across it and the zone border."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from benchmark_route_matrix import runtime

lua = runtime(profile='firm')
lua.execute("""
    A.db.useBoats = false
    A.db.useFlights = false
    local start = {mapID=1434, x=.422999, y=.0864479}
    local darkshire = {mapID=1431, x=.75236, y=.458606}

    local function check(first, last)
        local route, reason
        A.PlanningJob.Start(function()
            return A.Journey.Plan(first, last, {faction='Alliance', liveStart=true})
        end, function(value) route=value end, function(why) reason=why end)
        while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
        assert(route, reason)
        local crossedDeck, changedZone = false, false
        for _,leg in ipairs(route.legs) do
            assert(leg.kind=='walk', 'Expected a walk without any transport')
            assert(A.Terrain.Validate(leg), 'Invalid terrain on a walking approach')
            local floor = A.StructureData.corridors[leg.exitStructure]
            if floor and floor.placement==44103 then
                assert(leg.exitPath and #leg.exitPath>2, 'Guide the player along the chasm bridge deck')
                crossedDeck=true
            end
            if leg.mapID~=first.mapID then changedZone=true end
        end
        assert(crossedDeck and changedZone, 'Expected the Stranglethorn bridge and a zone handoff')
        A.Journey.Install(route)
        for _,leg in ipairs(route.legs) do
            for _,p in ipairs(leg.points) do A.Journey.Update(p,true) end
            for _,p in ipairs(leg.exitPath or {}) do
                A.Journey.Update(A.Structures.Aim(p,leg.mapID),true)
            end
        end
        local _,status=A.Journey.Update(last,true)
        assert(status=='arrived','Guidance failed to resume across the bridge and border')
    end
    check(start, darkshire)
    check(darkshire, start)

    -- A usable chasm bridge must be compared before accepting a boat detour.
    A.db.useBoats = true
    A.db.useFlights = true
    check(start, darkshire)

    A.Journey.Clear()
    local south={mapID=1434,x=.4079086334243864,y=.04100535762749127}
    local north={mapID=1434,x=.40600248291600355,y=.03246003151449403}
    local banks,work
    A.PlanningJob.Start(function()
        local plan,why=A.Journey.Plan(south,north,{walkingOnly=true,liveStart=true})
        work=A.PlanningJob.Progress().cells
        return plan,why
    end,function(value) banks=value end,error)
    while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
    assert(banks and banks.distance<60,'Both banks should route over the nearby deck')
    assert(work<10000,'Exhausted the ground-search budget for a short bridge crossing')
""")
print('PASS: reported northern Stranglethorn start to Darkshire and back on foot')
