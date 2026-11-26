"""Validate promising complete itineraries before unrelated walking prefixes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow.lua').read_text())
    lua.execute('fakeUI(); A={}; visits={}')
    for name in ['Store.lua', 'Terrain.lua', 'PlanningJob.lua', 'TravelNetwork.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
    lua.execute("""
A.InitStore({})
A.TerrainData={version=1,zones={}}
A.CrossingData={version=1,maps={},edges={}}
for map=1,4 do
 A.TerrainData.zones[map]={status='complete',w=6,h=6,widthYards=1000,heightYards=1000,rows={'/','/','/','/','/','/'}}
 A.CrossingData.maps[map]={name='Zone '..map,west=1000,north=1000,width=1000,height=1000,instance=0}
end
function p(map,x,y) return {mapID=map,x=x,y=y or .5} end
local path=A.Terrain.Path
A.Terrain.Path=function(from,to,options)
 visits[#visits+1]={mapID=from.mapID,from=from,to=to}
 return path(from,to,options)
end
local floors={}
A.Structures={Get=function(edge) return floors[edge.structure] end}
function crossing(id,from,to)
 local length=A.TravelNetwork.Distance(from,to)
 floors[id]={distance=length}
 A.CrossingData.edges[#A.CrossingData.edges+1]={a=from,b=to,distance=length,structure=id}
end
A.Structures.Path=function(id,from)
 for _,e in ipairs(A.CrossingData.edges) do if e.structure==id then return {from,from==e.a and e.b or e.a} end end
end
A.Structures.Access=function() end
function vehicle(id,from,to,seconds,fare)
 return {key=id,from=from,to=to,seconds=seconds,transport={kind='flight',id=id,a=from,b=to,board=from,arrival=to,
  name=id,planningSeconds=seconds,fare=fare,fromName='From',toName='To'}}
end
A.Flights={Money=function() return money end,Path=function(row) return {row.board,row.arrival} end,ContextValid=function() return false end}
A.Transports={Edges=function() return vehicles end,MinimumSeconds=function(rows)
 local seconds=math.huge;for _,row in ipairs(rows) do seconds=math.min(seconds,row.seconds) end;return seconds
end}
function plan(from,to,options)
 local result,reason
 A.PlanningJob.Start(function() return A.TravelNetwork.Plan(from,to,options or {speed=1}) end,
  function(p) result=p end,function(why) reason=why end)
 local slices=0;while A.PlanningJob.IsRunning() do A.PlanningJob.Step();slices=slices+1;assert(slices<100) end
 assert(result,reason);return result
end
""")
    return lua


lua = runtime()
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
crossing('useful',p(1,.7),p(2,.7))
for i=1,24 do crossing('dead-'..i,p(1,.1+i/10000,.51),p(4,.1+i/10000,.51)) end
vehicles={vehicle('lift',p(2,.75),p(3,.85),1)}
local route=plan(start,goal)
for _,call in ipairs(visits) do assert(call.mapID~=4,'a viable complete itinerary must precede validation of unrelated dead ends') end
assert(#visits<=3,'only the three joins of the winning itinerary need terrain validation')
assert(route.hasTransports and math.abs(route.estimatedSeconds-701)<.001)
for _,leg in ipairs(route.legs) do if leg.kind=='walk' then assert(A.Terrain.Validate(leg)) end end
""")
print('PASS: complete itinerary selection avoids unrelated dead-end terrain validation')

lua = runtime()
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
vehicles={vehicle('looks-short',p(1,.2),p(3,.6),1),vehicle('actually-short',p(1,.6),p(3,.9),2)}
-- The first departure and arrival are on opposite sides of a blocked band.
-- A real terrain detour makes its lower-bound winner slower overall.
A.TerrainData.zones[3].rows={'/','9','9','9','9','/'}
local route=plan(start,goal)
local selected;for _,leg in ipairs(route.legs) do if leg.transport then selected=leg.transport.id end end
assert(selected=='actually-short','complete itineraries must compare validated costs rather than accept their first feasible guess')
assert(math.abs(route.estimatedSeconds-502)<.001)
""")
print('PASS: validated walking detours can change the winning transport itinerary')

lua = runtime()
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
money=100
vehicles={vehicle('fast-expensive',p(1,.1),p(2,.4),1,90),vehicle('slow-free',p(1,.1),p(2,.4),20,0),vehicle('onward',p(2,.4),p(3,.9),1,20)}
local route=plan(start,goal)
assert(route.flightCost==20,'the complete itinerary must retain an affordable slower prefix')
assert(math.abs(route.estimatedSeconds-21)<.001)
""")
print('PASS: complete itinerary selection preserves nondominated total-fare choices')


def slow_join(lua):
    # Model the already measured expensive fine-grid join without making the
    # focused network test expand hundreds of thousands of terrain cells.
    # Successful geometry still comes from the real Terrain implementation.
    lua.execute("""
allowances={}
local original=A.Terrain.Path
A.Terrain.Path=function(from,to,options)
 if from.mapID==1 and math.abs(from.x-.1)<1e-9 and math.abs(to.x-.2)<1e-9 then
  local allowance=options.maxExpansions
  allowances[#allowances+1]=allowance
  local work=math.min(40000,allowance)
  if allowance<40000 then
   A.PlanningJob.BeginPath(from.mapID);A.PlanningJob.PathProgress(work)
   if options.yield then options.yield(work) end
   return nil,'budget'
  end
  local path,length=original(from,to,options)
  A.PlanningJob.PathProgress(work)
  if options.yield then options.yield(work) end
  return path,length
 end
 return original(from,to,options)
end
""")


lua = runtime()
slow_join(lua)
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
vehicles={vehicle('hard-approach',p(1,.2),p(3,.9),1),vehicle('quick-approach',p(1,.21),p(3,.9),2)}
local route=plan(start,goal)
local selected;for _,leg in ipairs(route.legs) do if leg.transport then selected=leg.transport.id end end
assert(selected=='quick-approach','a bounded first pass must try a good feasible alternative before deep walking search')
assert(#allowances==1 and allowances[1]<=16384,'the expensive join must receive only its initial probe allowance')
assert(math.abs(route.estimatedSeconds-112)<.001,'the verified alternate stays within twenty percent of the optimistic best journey')
""")
print('PASS: a bounded first pass finds a verified near-best alternative before expensive joins')

lua = runtime()
slow_join(lua)
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
vehicles={vehicle('only-route',p(1,.2),p(3,.9),1)}
local route=plan(start,goal,{speed=1,maxWalkingCells=100000})
assert(#allowances==2 and allowances[1]<=16384 and allowances[2]>=40000,'an essential budget-limited probe must retry with normal allowance')
assert(allowances[1]+40000<=100000,'the probe slice must reserve enough shared work for normal fallback')
assert(math.abs(route.estimatedSeconds-101)<.001)
""")
print('PASS: an essential narrow or expensive join retries after its temporary probe deferral')

lua = runtime()
slow_join(lua)
lua.execute("""
local start,goal=p(1,.1),p(3,.9)
vehicles={vehicle('hard-approach',p(1,.2),p(3,.9),1),vehicle('large-detour',p(1,.9),p(3,.9),2)}
local route=plan(start,goal)
local selected;for _,leg in ipairs(route.legs) do if leg.transport then selected=leg.transport.id end end
assert(selected=='hard-approach' and #allowances==2,'a much longer feasible alternative must not bypass deeper search for a substantially better journey')
assert(math.abs(route.estimatedSeconds-101)<.001)
""")
print('PASS: early feasibility cannot justify a large detour beyond the complete-journey quality bound')

lua = runtime()
lua.execute("""
local original=A.Terrain.Path
local budgetFailures=0
A.Terrain.Path=function(from,to,options)
 local path,length=original(from,to,options)
 if not path and length=='budget' then budgetFailures=budgetFailures+1 end
 if path and from.mapID==3 and math.abs(from.x-.8)<1e-9 and math.abs(to.x-.9)<1e-9 then
  -- Model a cheap verified road or smoothing detour whose actual distance
  -- is slightly longer than its straight-line itinerary estimate.
  path={from,p(3,.85,.525),to};length=111.80339887498949
  assert(A.Terrain.Validate({points=path}))
 end
 return path,length
end
local start,goal=p(1,.1),p(3,.9)
vehicles={vehicle('slight-detour',p(1,.2),p(3,.8),1),vehicle('cheaper-complete-journey',p(1,.3),p(3,.9),2)}
local route=plan(start,goal)
local selected;for _,leg in ipairs(route.legs) do if leg.transport then selected=leg.transport.id end end
assert(budgetFailures==0,'all fixture joins must finish cheaply without budget deferrals')
assert(selected=='cheaper-complete-journey','without deferred work, a slightly better complete itinerary must receive its cheap validation iteration')
assert(math.abs(route.estimatedSeconds-202)<.001)
""")
print('PASS: cheap successful joins preserve complete-journey quality without the deferral tolerance')

# Long trips may accept a verified route within the 5% phase bound. A
# materially quicker eligible service must still receive its terrain check.
for bend, expected in ((.02, 'first-service'), (.04, 'faster-service')):
    lua = runtime()
    lua.globals().bend = bend
    lua.globals().expected = expected
    lua.execute("""
        for map=5,6 do
            A.TerrainData.zones[map]=A.TerrainData.zones[4]
            A.CrossingData.maps[map]=A.CrossingData.maps[4]
        end
        for map=2,5 do crossing('zone-'..map,p(map,.9),p(map+1,.9)) end
        local original=A.Terrain.Path
        A.Terrain.Path=function(from,to,options)
            local path,length=original(from,to,options)
            if path and from.mapID==2 and math.abs(from.x-.8)<1e-9 and math.abs(to.x-.9)<1e-9 then
                local via=p(2,.85,.5+bend)
                path={from,via,to}
                length=A.TravelNetwork.Distance(from,via)+A.TravelNetwork.Distance(via,to)
                assert(A.Terrain.Validate({points=path}))
            end
            return path,length
        end
        vehicles={vehicle('first-service',p(1,.2),p(2,.8),1),vehicle('faster-service',p(1,.3),p(2,.9),2)}
        local route=plan(p(1,.1),p(6,.9))
        local selected
        for _,leg in ipairs(route.legs) do if leg.transport then selected=leg.transport.id end end
        assert(selected==expected,selected)
        assert(route.estimatedSeconds<=202*1.05)
    """)
print('PASS: five-boundary journeys retain transport alternatives beyond the 5% shortlist tolerance')
