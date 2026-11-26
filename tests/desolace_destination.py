"""One request must route automatically to connected ground near the original pin."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_route_matrix import runtime

runtime(profile='firm', flights=True).execute("""
local start={mapID=1443,x=.67392,y=.72364}
local goal={map=1443,x=.395107,y=.936345,name='Desolace'}
A.Journey.PlayerPosition=function() return start end
local raw={mapID=1443,x=goal.x,y=goal.y}
assert(A.WalkingRegions.Get(A.Terrain.Approach(raw,80))~=A.WalkingRegions.Get(start))
local plan
assert(A.Journey.Request(goal,function(result) plan=result end,error))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(plan and A.Terrain.Validate(plan))
local last=plan.points[#plan.points]
assert(math.abs(last.x-.408248)<.00001 and math.abs(last.y-.949306)<.00001)
assert(plan.approachDistance>70 and plan.approachDistance<72)
assert(goal.map==1443 and goal.x==.395107 and goal.y==.936345)
local exact
assert(A.Journey.Request(last,function(result) exact=result end,error))
while A.PlanningJob.IsRunning() do A.PlanningJob.Step() end
assert(exact and not exact.approachDistance)
print('PASS: automatic Desolace approach',last.x*100,last.y*100,plan.distance,'yd')
""")
