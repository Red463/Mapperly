"""Certified mid-zone bridges must enter the network and retain deck guidance."""
from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
sys.path.insert(0,str(root/'tools'))
from build_structure_corridors import validate_curved
import copy
for row in json.loads((root/'tools/data/native-bridge-batch-70959.json').read_text()):
    validate_curved(row)
    bad=copy.deepcopy(row);bad['landings'][0]['terrainDelta']=1
    try:validate_curved(bad)
    except ValueError:pass
    else:raise AssertionError('unsupported deck-to-ground step accepted')
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
    l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute('''
A.InitStore({});local count=0
for id,row in pairs(A.StructureData.corridors) do if row.endpointAccess then
 count=count+1
 for _,reverse in ipairs({false,true}) do
  local a,b=reverse and row.b or row.a,reverse and row.a or row.b
  -- Ask the network directly to certify bank connections even if a valid
  -- ground route also exists. Permission remains separate from preference.
  local plan,why=A.TravelNetwork.Plan(a,b,{walkingOnly=true,maxWalkingCells=20000})
  assert(plan,why)
  local crossed=false;for _,leg in ipairs(plan.legs) do crossed=crossed or leg.exitStructure==id end
  assert(crossed,'same-zone bridge must be usable by the walking network')
  A.Journey.Install(plan)
  local path=A.Structures.Path(id,a)
  for i=1,#path,10 do
   local p=A.Structures.Aim(path[i],i>#path/2 and b.mapID or a.mapID)
   local aim,reason=A.Journey.Update(p,true);assert(aim or reason=='arrived',reason)
  end
  A.Journey.Update(b,true);local _,reason=A.Journey.Update(b,true);assert(reason=='arrived',tostring(id)..' '..tostring(reverse)..' '..tostring(reason)..' leg='..tostring(A.Journey.legIndex)..' crossing='..tostring(A.Journey.crossing)..' index='..tostring(A.Journey.structureIndex)..' exit='..tostring(#plan.legs[1].exitPath)..' contains='..tostring(A.Structures.Contains(b,id)))
 end
end end
assert(count>=3,'missing independently validated mid-zone bridges')
''')
print('PASS: certified bridge network routes, same-zone and cross-zone floor following in both directions')
