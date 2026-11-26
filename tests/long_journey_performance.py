"""A cold Ratchet to Shimmering Flats request should finish with work to spare."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import benchmark_route_matrix as bench

lua = bench.runtime(profile='firm')
lua.execute('''
    local route, reason, progress
    local start = {mapID=1413, x=.624, y=.378}
    local goal = {mapID=1441, x=.78, y=.75}
    A.PlanningJob.Start(function()
        local result, why = A.Journey.Plan(start, goal, {faction='Alliance', liveStart=true})
        progress = A.PlanningJob.Progress()
        return result, why
    end, function(result) route=result end, function(why) reason=why end)
    while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
    assert(route, reason)
    local lift=false
    for _, leg in ipairs(route.legs) do
        if leg.kind == 'walk' then assert(A.Terrain.Validate(leg)) end
        if leg.transport and leg.transport.kind == 'lift' then lift=true end
    end
    assert(lift, 'Expected the Great Lift on this character without recorded flights')
    assert(progress.cells < 250000, 'Firm road routing spent too much work on the lift journey')
    print('PASS Ratchet to Shimmering Flats', progress.paths, 'paths', progress.cells, 'cells')
''')
