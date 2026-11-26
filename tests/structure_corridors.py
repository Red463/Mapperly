from pathlib import Path
import sys,json,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'));sys.path.insert(0,str(root/'.test-deps'))
from build_structure_corridors import validate,validate_curved
rows=json.loads((root/'tools/data/native-gate-corridors-70959.json').read_text())
assert len(rows)==4
for row in rows:
 validate(row)
 bad=copy.deepcopy(row);bad['unsupportedInteriorSamples']=[40]
 try:validate(bad)
 except ValueError:pass
 else:raise AssertionError('missing floor support accepted')
 bad=copy.deepcopy(row);bad['worldCenterline'][10][0]+=4
 try:validate(bad)
 except ValueError:pass
 else:raise AssertionError('unverified lateral detour accepted')
for row in json.loads((root/'tools/data/native-curved-corridors-70959.json').read_text()):
 validate_curved(row)
 bad=copy.deepcopy(row);bad['worldCenterline'][10][0]+=20
 try:validate_curved(bad)
 except ValueError:pass
 else:raise AssertionError('emitted centerline can differ from supported samples')
 if any(f.get('nativeRiser') for f in row['faces']):
  bad=copy.deepcopy(row);bad['faces'].append(dict(nativeRiser=True,sourceFlags=96,v=[[0,0,0],[0,1,0],[.1,0,1]]))
  try:validate_curved(bad)
  except ValueError:pass
  else:raise AssertionError('tall native faces must not borrow the bounded stair-riser policy')
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute((root/'tests/wow.lua').read_text());lua.execute('fakeUI();A={}')
for file in ['Store.lua','Data/Terrain.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua','RouteRecovery.lua']:
 if (root/file).exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/file).read_text())
lua.execute('''
A.InitStore({})
assert(A.Structures,'native structure adapter must exist')
local count=0
for _,e in ipairs(A.CrossingData.edges) do if e.structure then
 count=count+1;assert(A.Structures.Get(e),'native floor corridor with permitted outdoor landings must validate')
 local bad={structure=e.structure,a={mapID=e.a.mapID,x=e.a.x+.01,y=e.a.y},b=e.b}
 assert(not A.Structures.Get(bad),'altered endpoints must not borrow a structure exemption')
end end
assert(count>=6)
for _,id in ipairs({300408,373730}) do
 local row=A.StructureData.corridors[id]
 local plan,reason=A.Journey.Plan(row.a,row.b,{})
 assert(plan,reason)
 assert(plan.legs[1].exitStructure==id and #plan.points>200,'curved native floors must retain their actual path rather than draw a straight tunnel shortcut')
 A.Journey.Install(plan)
 for i,w in ipairs(row.worldPath) do
  local world={worldX=w[1],worldY=w[2],instance=A.CrossingData.maps[row.a.mapID].instance}
  local p=A.TravelNetwork.Transform(world,i>#row.worldPath/2 and row.b.mapID or row.a.mapID)
  p=p or A.TravelNetwork.Transform(world,row.a.mapID) or A.TravelNetwork.Transform(world,row.b.mapID)
  assert(p)
  local aim,why=A.Journey.Update(p,true)
  assert(aim or why=='arrived',why)
 end
 local _,why=A.Journey.Update(row.b,true);assert(why=='arrived','native floor follower must finish after the actual exit')
end
for _,id in ipairs({300408,373730}) do
 local row=A.StructureData.corridors[id]
 for _,reverse in ipairs({false,true}) do
  local start,goal=reverse and row.b or row.a,reverse and row.a or row.b
  local plan,reason=A.Journey.Plan(start,goal,{});assert(plan,reason)
  A.Journey.Install(plan)
  local path=A.Structures.Path(id,start);local since=0
  for i,w in ipairs(path) do
   if i>1 then since=since+A.TravelNetwork.Distance(path[i-1],w) end
   if i==1 or since>=5 or i==#path then
    local p=A.TravelNetwork.Transform(w,i>#path/2 and goal.mapID or start.mapID)
    p=p or A.TravelNetwork.Transform(w,start.mapID) or A.TravelNetwork.Transform(w,goal.mapID)
    A.Journey.Update(p,true);since=0
   end
  end
  local _,why=A.Journey.Update(goal,true)
  assert(why=='arrived','floor follower must tolerate ordinary movement past dense samples in either direction')
 end
end
-- In Dun Algaz the zone assignment can change while the player is still
-- walking the tunnel. The arrow should keep guiding them to its far mouth.
for _,id in ipairs({73025,126354,68441769,68443158}) do
 local row=A.StructureData.corridors[id]
 for _,reverse in ipairs({false,true}) do
  local start,goal=reverse and row.b or row.a,reverse and row.a or row.b
  local plan,reason=A.Journey.Plan(start,goal,{walkingOnly=true});assert(plan,reason)
  assert(plan.legs[1].exitStructure==id)
  A.Journey.Install(plan)
  local ends=A.Structures.Path(id,start)
  local first,last=ends[1],ends[#ends]
  local count=math.ceil(A.TravelNetwork.Distance(first,last)/5)
  for step=0,count do
   local t=step/count
   local p=A.Structures.Aim({worldX=first.worldX+(last.worldX-first.worldX)*t,
      worldY=first.worldY+(last.worldY-first.worldY)*t,instance=first.instance},
      t<.5 and start.mapID or goal.mapID)
   local aim,status=A.Journey.Update(p,true)
   if step<count-2 then
    assert(aim and A.Journey.crossing and A.Journey.Leg().exitStructure==id,
     'Left tunnel guidance before reaching the far mouth: '..id..' step '..step)
   end
  end
  local _,status=A.Journey.Update(goal,true);assert(status=='arrived')
 end
end
local row=A.StructureData.corridors[300408]
local plan=assert(A.Journey.Plan(row.a,row.b,{}));A.Journey.Install(plan);A.Journey.Update(row.a,true)
local z=A.Terrain.Zone(row.a.mapID)
local off={mapID=row.a.mapID,x=row.a.x-10/z.widthYards,y=row.a.y-10/z.heightYards}
assert(A.Terrain.Segment(off,off) and not A.Structures.Contains(off,300408))
A.RouteRecovery.Clear();A.RouteRecovery.Update(off,10,true)
assert(A.RouteRecovery.Update(off,14,true).replan,'a safe outdoor deviation from the floor entry must replan without indexing world targets as zone coordinates')
local path={}
for _,xy in ipairs({{0,0},{10,0},{20,0},{20,2},{10,2},{0,2}}) do path[#path+1]={worldX=xy[1],worldY=xy[2],instance=0} end
local contains=A.Structures.Contains;A.Structures.Contains=function() return true end
-- A local synthetic map keeps the hairpin coordinates inside ordinary bounds.
A.CrossingData.maps[9000]={west=100,north=100,width=200,height=200,instance=0}
local p=A.TravelNetwork.Transform({worldX=1,worldY=1.1,instance=0},9000)
A.Journey.active={multiZone=true,points={},legs={{mapID=9000,exitPath=path,exitStructure=1}}};A.Journey.legIndex=1;A.Journey.crossing=true;A.Journey.inStructure=1;A.Journey.structureIndex=2;A.Journey.paused=false
A.Journey.Update(p,true)
assert(A.Journey.structureIndex==2,'nearby parallel return passage must not skip an unvisited hairpin')
A.Structures.Contains=contains
''')
print('PASS: native gate/curved floor proofs, landing checks and winding corridor following')
