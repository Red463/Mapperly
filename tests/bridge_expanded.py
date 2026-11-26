"""The covered Westfall/Duskwood model bridge must get a native floor route."""
from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
sys.path.insert(0,str(root/'tools'))
from build_structure_corridors import validate_curved
proofs=json.loads((root/'tools/data/native-bridge-expanded-70959.json').read_text())
chasm=next((row for row in proofs if row['placementKey']=='0:m2:44103'),None)
assert chasm is not None,'Missing collision-floor proof for the northern Stranglethorn road bridge'
assert chasm['model']==189411 and chasm['verificationRevision']==3 and chasm['isBridgeAsset']
assert validate_curved(chasm)>38 and not chasm['existingGroundLine']
for landing in chasm['landings']:
    strip=landing['stripContacts']
    assert [sample['offsetYards'] for sample in strip]==[-.5,-.25,0,.25,.5]
    assert all(sample['permitted'] and abs(sample['terrainDelta'])<=.3 for sample in strip)
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute((root/'tests/wow.lua').read_text());l.execute('fakeUI();A={}')
for f in ['Store.lua','Data/Terrain.lua','Data/Water.lua','Data/GroundCorrections.lua','Data/WalkingRegions.lua','Data/Crossings.lua','Data/Structures.lua','Water.lua','Terrain.lua','Structures.lua','WalkingRegions.lua','TravelNetwork.lua','Journey.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
l.execute('''
A.InitStore({});local id=472884672753248
local row=A.StructureData.corridors[id];assert(row,'Westfall/Duskwood covered model bridge is missing')
assert(row.source=='native-model-floor')
for _,reverse in ipairs({false,true}) do
 local a,b=reverse and row.b or row.a,reverse and row.a or row.b
 local plan,why=A.Journey.Plan(a,b,{walkingOnly=true,allowSwimming=false,maxWalkingCells=20000});assert(plan,why)
 local found=false;for _,leg in ipairs(plan.legs) do found=found or leg.exitStructure==id end
 assert(found,'use the model deck, not a chord through the river')
 A.Journey.Install(plan);local path=A.Structures.Path(id,a)
 for i=1,#path,10 do
  local p=A.Structures.Aim(path[i],i>#path/2 and b.mapID or a.mapID)
  local aim,reason=A.Journey.Update(p,true);assert(aim or reason=='arrived',reason)
 end
 A.Journey.Update(b,true);local _,reason=A.Journey.Update(b,true);assert(reason=='arrived')
end
-- Narrow bridge access must respect its proven width, never a blanket 2.5yd.
local narrow
for _,r in pairs(A.StructureData.corridors) do if r.radius and r.radius<1 then narrow=r;break end end
assert(narrow,'include independently width-verified narrow bridges')
local path=narrow.worldPath;local a,b=path[math.floor(#path/2)],path[math.floor(#path/2)+1]
local dx,dy=b[1]-a[1],b[2]-a[2];local length=math.sqrt(dx*dx+dy*dy)
local outside={worldX=a[1]-dy/length*(narrow.radius+.2),worldY=a[2]+dx/length*(narrow.radius+.2),instance=A.CrossingData.maps[narrow.a.mapID].instance}
for id,r in pairs(A.StructureData.corridors) do if r==narrow then assert(not A.Structures.Contains(outside,id),'outside a narrow strip cannot borrow floor permission') end end
for id,r in pairs(A.StructureData.corridors) do if r.placement==19975 then
 assert(not A.Structures.Contains({worldX=-1066.128068576474,worldY=-9616.567270688278,instance=0},id),'uncertified semicircular endpoint cap must not grant deck access')
end end
local w=row.worldPath[math.floor(#row.worldPath/2)]
local p=A.Structures.Aim({worldX=w[1],worldY=w[2],instance=0},row.a.mapID)
UnitPosition=function()return w[2],w[1],0,0 end
assert(not A.Structures.Access(p,true),'unknown/placeholder live elevation must not admit a player from below the bridge')
assert(A.Structures.Access(p,false),'remote destination pins can still target the certified deck')
local denied,explanation=A.Journey.Plan(p,row.b,{walkingOnly=true,allowSwimming=false,liveStart=true,maxWalkingCells=20000})
assert(not denied and explanation:find('elevation',1,true),'live route admission must preserve the elevation requirement')
UnitPosition=function()return w[2],w[1],w[3],0 end
assert(A.Journey.Plan(p,row.b,{walkingOnly=true,allowSwimming=false,liveStart=true,maxWalkingCells=20000}),'a confirmed player deck height must allow a partial crossing')
UnitPosition=nil
local a={mapID=1439,x=.37988400,y=.43553532}
local b={mapID=1439,x=.38502036,y=.43354279}
local near,why=A.Journey.Plan(a,b,{walkingOnly=true,allowSwimming=false,maxWalkingCells=150000})
assert(near,why);assert(near.distance<80,'ordinary bank approaches must use the nearby bridge instead of the long dry-ground detour')
''')
print('PASS: smaller-model bridge routing in both directions and bounded narrow floor permission')
