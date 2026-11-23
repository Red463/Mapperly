"""Road preference must survive direct shortcuts, smoothing and route caches."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute('fakeUI();A={}')
for name in ['Store.lua','Roads.lua','Terrain.lua','Journey.lua']:
    if (root/name).exists():lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text(encoding='utf-8-sig'))
lua.execute('''
A.InitStore({})
assert(A.db.preferRoads==false,'road preference must be saved and opt-in')
assert(A.Roads,'standalone road decoder must exist')
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function pack(lines)
 local out={}
 for _,line in ipairs(lines) do
  local row={};for x=1,#line,6 do
   local n=0;for i=0,5 do n=n*2+(line:sub(x+i,x+i)=='1' and 1 or 0) end
   row[#row+1]=alphabet:sub(n+1,n+1)
  end;out[#out+1]=table.concat(row)
 end;return out
end
local z={status='complete',w=20,h=5,widthYards=200,heightYards=50,
 rows=pack({'11111111111111111111','11111111111111111111','11111111111111111111','11111111111111111111','11111111111111111111'})}
A.TerrainData={version=1,zones={[1]=z}}
local rz={w=20,h=5,widthYards=200,heightYards=50,rows=pack({'11111111111111111111','11000000000000000011','11000000000000000011','00000000000000000000','00000000000000000000'})}
A.RoadData={version=1,zones={[1]=rz}}
local a,b={mapID=1,x=.025,y=.5},{mapID=1,x=.975,y=.5}
local plain,length=assert(A.Terrain.Path(a,b))
assert(#plain==2 and math.abs(length-190)<.01)
local road,distance=A.Terrain.Path(a,b,{preferRoads=true})
assert(road,distance)
assert(#road>2 and distance>190 and distance<240,'road preference should take a modest detour even on open ground')
local north=false;for _,p in ipairs(road) do if p.y<.2 then north=true end end
assert(north,'smoothing must retain the preferred road rather than cut back across open ground')
assert(A.Terrain.Validate({points=road}))
assert(#assert(A.Terrain.Path(a,b))==2,'road and normal routes must not share cached geometry')
assert(#assert(A.Terrain.Path(a,b,{preferRoads=true}))>2)
A.db.preferRoads=true
assert(#assert(A.Journey.Plan(a,b,{})).points>2,'saved preference must reach the actual journey planner')
assert(#assert(A.Journey.Plan(a,b,{preferRoads=false})).points==2,'explicit request override must be supported')
z.rows=pack({'11111111111111111111','00000000000000000000','11111111111111111111','11111111111111111111','11111111111111111111'})
assert(#assert(A.Terrain.Path(a,b,{preferRoads=true}))==2,'disconnected road must not permit crossing a blocked cell')
assert(A.Terrain.Validate({points=assert(A.Terrain.Path(a,b,{preferRoads=true}))}))
A.RoadData.zones={}
assert(#assert(A.Terrain.Path(a,b,{preferRoads=true}))==2,'missing road data must fall back to ordinary terrain routing')
rz.w=21;A.RoadData.zones[1]=rz
assert(not A.Roads.Zone(1,z),'mismatched road grids must be ignored')
''')
print('PASS: road preference, safe smoothing, cache separation, blocked terrain and missing-data fallback')

for name in ['Data/Terrain.lua','Data/Roads.lua']:
    lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text(encoding='utf8'))
lua.execute('''
local count=0
for id,z in pairs(A.RoadData.zones) do
 count=count+1;local t=assert(A.Terrain.Zone(id))
 assert(z.w==t.w and z.h==t.h and z.widthYards==t.widthYards and z.heightYards==t.heightYards,'road and terrain coordinates must agree exactly')
 assert(#z.rows==z.h)
 local cells=0
 for y,row in ipairs(z.rows) do
  assert(#row<=math.ceil(z.w/6) and not row:find('[^A-Za-z0-9+/]'))
  for x=0,math.min(z.w,#row*6)-1 do if A.Roads.Cell(z,x,y-1) then cells=cells+1 end end
 end
 assert(cells==z.roadCells,'bundled road count must match decoded masks')
 assert(not A.Roads.Cell(z,-1,0) and not A.Roads.Cell(z,z.w,0))
end
assert(count==55,'every supplied local zone must have a road mask')
local a={mapID=1429,x=.825,y=.686}
local b={mapID=1429,x=.42265799844097,y=.665577526985558,name='Elwynn road regression'}
local plain=assert(A.Journey.Plan(a,b,{preferRoads=false}))
local preferred=assert(A.Journey.Plan(a,b,{preferRoads=true}))
assert(A.Terrain.Validate(preferred),'native road route must remain walkable')
assert(preferred.distance>plain.distance and preferred.distance<plain.distance*1.35,'native Elwynn route must take a modest road detour')
''')
print('PASS: all 55 shipped road grids align, decode correctly and yield a validated native Elwynn detour')
