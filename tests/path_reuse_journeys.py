"""Native long journeys must use shipped geometry and retain bounded warm reuse."""
from pathlib import Path
import json,sys,time
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
FILES=['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Flights.lua','Data/QuestLocations.lua','Roads.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelBounds.lua','TravelNetwork.lua','Flights.lua','Transports.lua','Journey.lua','QuestNavigation.lua']
def setup(reuse):
 l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
 for f in FILES:
  l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
 if reuse:
  for f in ['Data/WalkingPaths.lua','PathReuse.lua']:
   l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
 l.execute("""
 UnitClass=function() return 'Warrior','WARRIOR',1 end
 UnitGUID=function() return 'Player-1-Reuse' end;UnitFactionGroup=function() return 'Alliance' end
 GetMoney=function() return 1000000 end
 A.InitStore({preferRoads=true,roadPreferenceStrength=4})
 local c=A.Flights.Character();c.nodes={[28]=true,[26]=true};c.offers={[28]={[26]={from=28,to=26,fare=100,hops={28,26}}}}
 function bench(which)
  local start,goal
  if which=='Mikhail' then start={mapID=1440,x=.852,y=.446};goal=assert(A.Terrain.Approach({mapID=1437,x=.10599045556884,y=.60770013605442},30))
  else start=assert(A.Terrain.Approach({mapID=1431,x=.77,y=.44},30));goal=assert(A.Terrain.Approach({mapID=1426,x=.46,y=.51},30)) end
  local plan,reason,report;local slices=0
  A.PlanningJob.Start(function()
   local p,r=A.Journey.Plan(start,goal,{faction='Alliance'})
   report=A.PlanningJob.Progress();return p,r
  end,function(p) plan=p end,function(r) reason=r end)
  while A.PlanningJob.IsRunning() and slices<6000 do A.PlanningJob.Step();slices=slices+1 end
  assert(plan,reason or 'journey did not finish')
  local transports={}
  for _,leg in ipairs(plan.legs) do
   if leg.kind=='walk' then assert(A.Terrain.Validate(leg),'reused walking geometry must remain valid') end
   if leg.transport then transports[#transports+1]=leg.transport.kind..':'..leg.transport.id end
  end
  local s=A.PathReuse and A.PathReuse.Stats() or {}
  return {slices=slices,cells=report.cells,paths=report.paths,distance=plan.distance,transports=table.concat(transports,'/'),baked=s.bakedHits or 0,hits=s.hits or 0}
 end
 """)
 return l
rows=[]
for name in ['Mikhail','Duskwood-DunMorogh']:
 base=setup(False);reuse=setup(True)
 results=[]
 for label,l in [('baseline',base),('shipped-cold',reuse),('shipped-warm',reuse)]:
  at=time.perf_counter();row=dict(l.globals().bench(name).items());row.update(case=name,kind=label,seconds=round(time.perf_counter()-at,4));results.append(row);print(json.dumps(row),flush=True)
 before,cold,warm=results
 assert cold['transports']==before['transports'],'fixed walking reuse cannot invent available transports'
 assert abs(cold['distance']-before['distance'])<max(1,before['distance']*.02),'prepared geometry must retain comparable walking distance'
 assert cold['baked']>0,'the real itinerary must use shipped connections'
 assert cold['cells']<before['cells'],'cold long-route terrain work must decrease'
 assert warm['cells']<cold['cells'],'repeat long-route work must benefit from cross-zone reuse'
 assert warm['hits']>cold['hits']
 rows.extend(results)
(root/'output/path-reuse-benchmark.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS: native cold and warm journeys reduce terrain work, retain transports and validate all walking geometry')
