"""Replay the reported Farholde Keep detour on the shipped navigation data."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_route_matrix import runtime

for roads, dry in [('firm', False), ('off', True)]:
    lua = runtime(profile=roads, avoid=dry)
    lua.execute("""
    local a={mapID=2548,x=.590,y=.771}
    local b={mapID=2548,x=.606,y=.816}
    for _,reverse in ipairs({false,true}) do
        local plan,reason=A.Journey.Plan(reverse and b or a,reverse and a or b,
            {walkingOnly=true,allowSwimming=not benchAvoid,liveStart=true})
        assert(plan,reason)
        local crossed=false
        for _,leg in ipairs(plan.legs) do
            local bridge=A.StructureData.corridors[leg.exitStructure]
            if bridge and bridge.placement==67711058 then
                assert(#leg.exitPath>2)
                crossed=true
            end
        end
        assert(crossed,'Farholde route bypassed the bridge: '..plan.distance..' yd')
        assert(plan.distance<250,'unnecessary detour near bridge')
        print(benchStrength,benchAvoid,reverse,plan.distance)
    end
    """)
