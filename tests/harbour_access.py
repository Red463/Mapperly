"""Certified city-to-harbour descent works with Forever's zero altitude."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Data/HarbourAccess.lua','Data/Transports.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Transports.lua','Journey.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
A.InitStore({})
local id=7095901453;local row=A.StructureData.corridors[id];assert(row)
assert(A.WalkingRegions.Get(row.a)==36 and A.WalkingRegions.Get(row.b)==1)
for _,reverse in ipairs({false,true}) do
 local start,goal=reverse and row.b or row.a,reverse and row.a or row.b
 local plan,why=A.Journey.Plan(start,goal,{})
 assert(plan,why);assert(plan.legs[1].exitStructure==id,'harbour route must use the native corridor')
 A.Journey.Install(plan)
 for _,world in ipairs(A.Structures.Path(id,start)) do
  local p=A.TravelNetwork.Transform(world,1453)
  UnitPosition=function() return world.worldY,world.worldX,0,0 end
  A.Journey.Update(p,true)
 end
 local _,done=A.Journey.Update(goal,true)
 assert(done=='arrived','zero-height client must follow the verified harbour floors in both directions')
end
local pier=A.StructureData.corridors[7095901454]
assert(pier and A.WalkingRegions.Get(pier.a)==1 and A.WalkingRegions.Get(pier.b)==1)
local incoming
for _,r in ipairs(A.TransportData.edges) do if r.arrivalCorridor==7095901454 then incoming=r end end
assert(incoming and A.TravelNetwork.Distance(incoming.b,incoming.arrival)<14)
local function at(p,z)
 local x,y=A.TravelNetwork.World(p);UnitPosition=function() return y,x,z,0 end
end
at(incoming.b,0)
assert(not A.Transports.CanDisembark(incoming,incoming.b,{}),'zero altitude near vessel cannot prove disembarkation')
at(pier.a,0)
assert(A.Transports.CanDisembark(incoming,pier.a,{}),'walking clear along the certified pier must finish the boat leg')
at(pier.a,80)
assert(not A.Transports.CanDisembark(incoming,pier.a,{}),'readable wrong-floor position cannot finish boat journey')
local old=A.StructureData.corridors[7095901454];A.StructureData.corridors[7095901454]=nil
for _,edge in ipairs(A.Transports.Edges({faction='Alliance'})) do
 assert(not edge.transport.arrivalCorridor and not edge.transport.boardingCorridor,'incomplete dock data cannot expose a service that requires its floor proof')
end
A.StructureData.corridors[7095901454]=old
''')
print('PASS: private native harbour floor descent/ascent, connected regions and zero-height following')
