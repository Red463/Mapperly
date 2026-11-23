"""Service searches must preserve walking-only intent and bounded terrain work."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute('A={}')
for f in ['Store.lua','Journey.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute("""
A.InitStore({});local work=0
A.Terrain={Zone=function()return {status='complete'}end,Segment=function()return true end,Path=function(a,b,o) assert(o.maxExpansions<=77,'nearest search must bound its local work');work=work+30;return {a,b},100 end}
A.TravelNetwork={Canonical=function(m)return m end,Plan=function(a,b,o)assert(o.walkingOnly,'cross-zone service search must exclude vehicles');assert(o.maxWalkingCells<=77);return {walkingOnly=o.walkingOnly}end}
A.Transports={Edges=function()return {{seconds=1}}end,MinimumSeconds=function()return 1 end}
local a,b={mapID=1,x=.1,y=.1},{map=1,x=.9,y=.9}
local p=A.Journey.Plan(a,b,{walkingOnly=true,maxWalkingCells=77});assert(p.kind=='walking','same-zone walking-only service cannot switch to a ferry')
b.map=2;assert(A.Journey.Plan(a,b,{walkingOnly=true,maxWalkingCells=77}).walkingOnly)
-- An initial failed local attempt consumes part of the same caller budget.
A.PlanningJob={Progress=function()return {cells=work}end}
A.StructureData={};A.Terrain.Path=function(a,b,o) work=work+30;return nil,'unreachable' end
A.TravelNetwork.Plan=function(a,b,o)assert(o.maxWalkingCells==47,'native passage fallback must not reset the work budget');return {}end
b.map=1;assert(A.Journey.Plan(a,b,{walkingOnly=true,maxWalkingCells=77}))
""")
print('PASS: walking-only service routes exclude vehicles and share bounded work with native-passage fallback')
