"""Prove long walking-network separation only when all region inputs are known."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
NETWORK = ROOT / 'TravelNetwork.lua'
if '--staged' in sys.argv:
    NETWORK = ROOT / 'output/route-improvements-2026-11-25/hardening/r27/TravelNetwork.lua'
sys.path.insert(0, str(ROOT / '.test-deps'))
from lupa.lua51 import LuaRuntime


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / 'tests/wow.lua').read_text())
    lua.execute('fakeUI(); A={}; calls=0')
    for name in ['Store.lua', 'Terrain.lua', 'WalkingRegions.lua', 'PlanningJob.lua']:
        lua.execute('assert(loadstring(...))("Mapperly",A)', (ROOT / name).read_text())
    lua.execute('assert(loadstring(...))("Mapperly",A)', NETWORK.read_text())
    lua.execute("""
A.InitStore({})
A.TerrainData={version=1,zones={}};A.CrossingData={version=1,maps={},edges={}}
A.WalkingRegionData={version=1,zones={}}
for map=1,4 do
 A.TerrainData.zones[map]={status='complete',w=6,h=1,widthYards=100,heightYards=10,maskSha256='base',rows={'/'}}
 A.CrossingData.maps[map]={name='Zone '..map,west=100,north=10,width=100,height=10,instance=0}
 A.WalkingRegionData.zones[map]={w=6,h=1,baseSha256='base',groundCells=0,groundSha256='',exceptions={}}
end
function p(map,x) return {mapID=map,x=x,y=.5} end
a=p(1,.1);b=p(4,.9)
local floors={};A.Structures={Get=function(edge) return floors[edge.structure] end,Access=function() end}
function crossing(from,to)
 local id=#A.CrossingData.edges+1
 local row={a=from,b=to,structure=id,distance=A.TravelNetwork.Distance(from,to)}
 floors[id]=row;A.CrossingData.edges[id]=row
end
A.Structures.Path=function(id,from)
 local row=floors[id];return {from,from==row.a and row.b or row.a}
end
crossing(p(1,.9),p(2,.1));crossing(p(2,.9),p(3,.1));crossing(p(3,.9),p(4,.1))
function separate()
 -- The third cell is blocked: the right three cells form region2.
 A.TerrainData.zones[2].rows={'3'}
 A.WalkingRegionData.zones[2].exceptions={{x=3,y=0,w=3,h=1,rows={'4'}}}
end
local original=A.Terrain.Path
A.Terrain.Path=function(...) calls=calls+1;return original(...) end
transportEdges={}
A.Transports={Edges=function() return transportEdges end,MinimumSeconds=function() return 10 end}
function vehicle(from,to,kind)
 local row={a=from,b=to,board=from,arrival=to,name='Test vehicle',kind=kind or 'boat',planningSeconds=10}
 local edge={from=from,to=to,key='one-way',transport=row,seconds=10}
 transportEdges[1]=edge
 return row
end
function run(options)
 local result,reason;local steps=0
 A.PlanningJob.Start(function() return A.TravelNetwork.Plan(a,b,options or {walkingOnly=true,speed=1}) end,
  function(path) result=path end,function(why) reason=why end)
 while A.PlanningJob.IsRunning() do A.PlanningJob.Step();steps=steps+1;assert(steps<100) end
 return result,reason
end
""")
    return lua


lua = runtime()
lua.execute("""
separate()
local path,reason=run()
assert(not path and reason=='No verified walking network connects the start and destination ground regions.','known separated ground must report network disconnection')
assert(calls==0,'a verified region cut must precede unrelated detailed walking searches')
""")
print('PASS: verified separated long walking network fails before any detailed searches')

lua = runtime()
lua.execute("""
local path,reason=run();assert(path,reason)
for _,leg in ipairs(path.legs) do if leg.kind=='walk' then assert(A.Terrain.Validate(leg)) end end
assert(calls>0,'connected regions must retain actual path validation')
""")
print('PASS: connected region network retains verified terrain planning')

lua = runtime()
lua.execute("""
A.WalkingRegionData.zones[2]=nil
local path,reason=run();assert(path,reason)
assert(calls>0,'missing region data must fall through to detailed searches')
""")
print('PASS: unverified region rows skip the separation proof')

lua = runtime()
lua.execute("""
separate();crossing(p(2,.2),p(2,.6))
local path,reason=run();assert(path,reason)
local bridge=false
for _,leg in ipairs(path.legs) do
 if leg.exitStructure==4 then bridge=true end
 if leg.kind=='walk' then assert(A.Terrain.Validate(leg)) end
end
assert(bridge,'a certified structure must retain its explicit connection between ground regions')
""")
print('PASS: certified floor edges can connect otherwise separated terrain regions')

lua = runtime()
lua.execute("""
separate();b=p(2,.9)
local path,reason=run()
assert(not path and calls>0,'nearby walking requests must retain their existing lightweight path search')
assert(reason~='No verified walking network connects the start and destination ground regions.')
""")
print('PASS: nearby requests avoid long-network preflight overhead')

lua = runtime()
lua.execute("""
separate()
-- This vehicle only runs from the goal side towards the starting side.
vehicle(p(3,.1),p(2,.1))
local path,why=run({speed=1})
assert(not path and calls==0 and why:find('travel settings',1,true),
 'an enabled one-way vehicle in the wrong direction cannot repair a disconnected journey')
""")
print('PASS: disconnected mixed journey detected before local searches')

lua = runtime()
lua.execute("""
separate();vehicle(p(2,.1),p(3,.1))
local route,why=run({speed=1})
assert(route and route.hasTransports,why)
assert(calls>0,'the positive trip must still validate its walking approaches')
""")
print('PASS: an enabled vehicle can bridge disconnected ground regions')

lua = runtime()
lua.execute("""
separate()
A.CityNavigation={Supports=function(p) return p.mapID==2 end,
 Path=function(from,to) if from.mapID==2 and to.mapID==2 then
  return {from,to,cityGuidance=true},A.TravelNetwork.Distance(from,to)
 end end}
local route,why=run({speed=1})
assert(route and route.hasCityGuidance,why)
""")
print('PASS: interior city guidance remains reachable across outdoor ground regions')

lua = runtime()
lua.execute("""
separate()
local from=p(2,.9)
local row=vehicle(from,p(3,.2),'tram')
row.automaticTram=true;row.fromName='Station';row.toName='Terminus'
A.Trams={Access=function(first,last) if first.mapID==2 and last==from then
 return {first,last,portalGuidance=true},A.TravelNetwork.Distance(first,last)
end end}
local route,why=run({speed=1})
assert(route and route.hasTransports and route.hasPortalGuidance,why)
""")
print('PASS: tram portal guidance can connect a boarding point on another region')

lua = runtime()
lua.execute("""
separate()
local pier,shore=p(2,.9),p(2,.2)
local boat=vehicle(pier,p(3,.1))
boat.boardingCorridor='pier'
A.HarbourAccessData={proofSha256='test',corridors={pier={a=shore,b=pier}}}
A.TransportData={harbourProofSha256='test'}
A.Transports.DockCorridor=function(id) return A.HarbourAccessData.corridors[id] end
local structurePath=A.Structures.Path
A.Structures.Path=function(id,start)
 if id~='pier' then return structurePath(id,start) end
 local path={}
 for i,p in ipairs({shore,pier}) do
  local x,y,instance=A.TravelNetwork.World(p)
  path[i]={worldX=x,worldY=y,instance=instance}
 end
 return path
end
local route,why=run({speed=1})
assert(route and route.hasTransports,why)
""")
print('PASS: a certified dock floor can bridge disconnected shore and boarding regions')

lua = runtime()
lua.execute("""
separate();A.WalkingRegionData.zones[2]=nil
local route,why=run({speed=1})
assert(not route and calls>0 and not why:find('travel settings',1,true),
 'unknown mixed connectivity requires trying the real planner')
""")
print('PASS: mixed plans with incomplete region data retain detailed search')
