"""Reported Ashenvale route must avoid irrelevant transport/zone searches."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Data/LocalTransports.lua','Data/Flights.lua','Roads.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','PlanningJob.lua','TravelNetwork.lua','Flights.lua','Transports.lua','Journey.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
A.InitStore({preferRoads=true,roadPreferenceStrength=4})
local lookups=0;local cell=A.Roads.Cell
A.Roads.Cell=function(...) lookups=lookups+1;return cell(...) end
local result,why;local frames,paths,cells=0,0,0
A.PlanningJob.Start(function()
 return A.Journey.Plan({mapID=1440,x=.729,y=.683},{mapID=1440,x=.286813448654843,y=.203167073055504},{faction='Alliance'})
end,function(p) result=p end,function(r) why=r end)
while A.PlanningJob.IsRunning() and frames<2000 do
 A.PlanningJob.Step();frames=frames+1;local p=A.PlanningJob.Progress()
 if p then paths=math.max(paths,p.paths);cells=math.max(cells,p.cells) end
end
assert(result,why or 'reported route did not finish')
print('Ashenvale Firm:',frames,'slices',paths,'paths',cells,'cells',lookups,'road lookups',result.distance,'yd')
assert(paths==1,'nearby transport methods that cannot win must not cause extra zone searches')
assert(cells<250000,'reported route must avoid the redundant neighbour-zone searches')
assert(lookups<700000,'road costs must not be decoded repeatedly for each neighbour')
assert(A.Terrain.Validate(result),'performance cannot bypass terrain restrictions')
assert(math.abs(result.distance-4326.393889929523)<.001,'optimisation must retain the existing Firm route')
local P=A.TravelNetwork
local function p(x,i) return {worldX=x,worldY=0,instance=i} end
local function edge(a,b,seconds) return {from=a,to=b,seconds=seconds} end
assert(not P.CanImproveWithTransport(p(0,0),p(100,0),{edge(p(1000,0),p(90,0),1)},1,100))
assert(P.CanImproveWithTransport(p(0,0),p(100,0),{edge(p(0,0),p(90,0),1)},1,100))
-- No single leg reaches the destination continent: relaxed pruning must
-- still admit a useful journey containing multiple transports.
assert(P.CanImproveWithTransport(p(0,0),p(100,0),{
 edge(p(0,0),p(0,1),1),edge(p(0,1),p(99,0),1)},1,100))
assert(not P.CanImproveWithTransport(p(0,0),p(100,0),{
 edge(p(0,0),p(0,1),100),edge(p(0,1),p(99,0),1)},1,100))
-- Differential check against a fully connected relaxed-world graph with
-- separate walking/used-transport states. This catches pruning a useful
-- combination, including trips that change instance more than once.
math.randomseed(70959)
for trial=1,80 do
 local nodes={p(math.random(0,100),0),p(math.random(0,100),0)}
 local edges={}
 for i=1,6 do
  local a,b=p(math.random(0,100),math.random(0,2)),p(math.random(0,100),math.random(0,2))
  nodes[#nodes+1]=a;nodes[#nodes+1]=b;edges[#edges+1]=edge(a,b,math.random(1,30))
 end
 local n=#nodes;local d={}
 for i=1,n do d[i]={};for j=1,n do
  d[i][j]=i==j and 0 or nodes[i].instance==nodes[j].instance and math.abs(nodes[i].worldX-nodes[j].worldX) or math.huge
 end end
 for i,e in ipairs(edges) do local a,b=2*i+1,2*i+2;d[a][b]=math.min(d[a][b],e.seconds) end
 for k=1,n do for i=1,n do for j=1,n do d[i][j]=math.min(d[i][j],d[i][k]+d[k][j]) end end end
 local best=math.huge
 for i,e in ipairs(edges) do
  local a,b=2*i+1,2*i+2
  best=math.min(best,d[1][a]+e.seconds+d[b][2])
 end
 local limit=math.random(1,100)
 assert(P.CanImproveWithTransport(nodes[1],nodes[2],edges,1,limit)==(best<limit),'relaxed transport oracle mismatch')
end
''')
print('PASS: unchanged native route, bounded road lookups and safe multi-transport pruning')
