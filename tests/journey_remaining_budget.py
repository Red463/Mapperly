"""Direct walking work shares its remaining allowance with alternative journeys."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime

source = (ROOT / 'Journey.lua').read_text(encoding='utf8')
for with_progress in (False, True):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('''
      A={}; local progress={cells=37}
      A.ValidPin=function()return true end
      A.db={}
      local points
      A.Terrain={Zone=function()return {status='complete'}end,Segment=function()return true end}
      A.Terrain.Path=function(a,b,options)
        assert(options.maxExpansions==expectedDirectBudget)
        if options.yield and used>0 then options.yield(used)end
        progress.cells=progress.cells+used
        if failDirect then return nil,'budget'end
        points={a,b};return points,100
      end
      A.TravelNetwork={Canonical=function(map)return map end,
        CanImproveWithStructure=function()return comparison=='structure'end,
        CanImproveWithTransport=function()return true end,
        Plan=function(a,b,options)
          assert(options.maxWalkingCells==expectedRemaining,
            'remaining allowance: '..tostring(options.maxWalkingCells)..' expected '..tostring(expectedRemaining))
          if not failDirect then
            assert(options.candidatePoints==points and options.candidateDistance==100,
              'valid direct geometry must remain available even with zero allowance')
          end
          return {points=options.candidatePoints,network=true,remaining=options.maxWalkingCells}
        end}
      A.Transports={Edges=function()return comparison=='transport'and{{seconds=1}}or{}end,
        MinimumSeconds=function()return 1 end}
      A.StructureData={}
      A.mockProgress={Progress=function()return progress end}
    ''')
    if with_progress:
        lua.execute('A.PlanningJob=A.mockProgress')
    lua.execute('assert(loadstring(...))("Mapperly",A)', source)
    lua.execute('''
      local start={mapID=1,x=.1,y=.2}
      local goal={mapID=1,x=.8,y=.2}
      for _,test in ipairs({
        {kind='structure',budget=1000,spent=600,remaining=400},
        {kind='transport',budget=1000,spent=600,remaining=400},
        {kind='structure',budget=1000,spent=1000,remaining=0},
        {kind='transport',budget=1000,spent=1000,remaining=0},
        {kind='structure',budget=1000,spent=0,remaining=1000},
        {kind='structure',spent=600},
        {kind='transport',spent=600},
        {kind='failure',budget=1000,spent=600,remaining=400},
        {kind='failure',budget=1000,spent=1000,remaining=0}
      })do
        comparison=test.kind;failDirect=comparison=='failure';used=test.spent
        expectedRemaining=test.remaining;expectedDirectBudget=test.budget or 262144
        local caller={maxWalkingCells=test.budget,walkingOnly=false,custom='retain'}
        local result,why=A.Journey.Plan(start,goal,caller)
        assert(result and result.network,why)
        assert(caller.maxWalkingCells==test.budget and caller.custom=='retain'and caller.candidatePoints==nil,
          'caller options must remain unchanged')
        if not failDirect then assert(result.points and #result.points==2)end
      end
      comparison='none';failDirect=false;used=20
      expectedRemaining=nil;expectedDirectBudget=262144
      local ordinary=assert(A.Journey.Plan(start,goal,nil))
      assert(not ordinary.network and ordinary.kind=='walking'and ordinary.distance==100)
      A.Water={WithPlanningPolicy=function(allowed,work)return work()end}
      A.db.avoidSwimming=true
      comparison='structure';used=131072;expectedDirectBudget=131072;expectedRemaining=0
      local caller={maxWalkingCells=200000,custom='dry-caller'}
      local dry=assert(A.Journey.Plan(start,goal,caller))
      assert(dry.points and dry.remaining==0 and not dry.swimmingFallback)
      assert(caller.maxWalkingCells==200000 and caller.custom=='dry-caller',
        'the reserved dry attempt must not mutate the original caller allowance')
    ''')
print('PASS: journey direct-success/failure allowance, structure/transport comparisons, exhausted candidate, cached/unbudgeted behavior and caller immutability')
