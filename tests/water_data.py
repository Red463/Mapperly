"""All shipped liquid masks match native artifacts; certified floor stays separate."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from PIL import Image
from lupa.lua51 import LuaRuntime
manifest=json.loads((root/'tools/data/water-manifest.json').read_text())
assert hashlib.sha256((root/'Data/Water.lua').read_bytes()).hexdigest()==manifest['outputSha256']
assert hashlib.sha256((root/'Data/Terrain.lua').read_bytes()).hexdigest()==manifest['terrainSha256']
l=LuaRuntime(unpack_returned_tuples=True);l.execute('A={db={allowSwimming=false}}')
for f in ['Data/Terrain.lua','Data/Water.lua','Data/GroundCorrections.lua','Data/Crossings.lua','Data/Structures.lua','Water.lua','Terrain.lua','Structures.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
a=l.globals().A;alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
checked=0;unknown=0
for mid,z in a.WaterData.zones.items():
    p=root.parent/f'output/terrain-overlays-70959/{mid}.png';im=Image.open(p);raw=im.tobytes();w,h=im.size
    assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest['sources'][str(mid)]['pngSha256']
    assert hashlib.sha256(raw).hexdigest()==z.baseSha256
    for y in range(h):
        row=[]
        for x in range(0,w,6):
            bits=0
            for k in range(6):bits=bits*2+int(x+k<w and raw[y*w+x+k] in (0,255))
            row.append(alpha[bits])
        assert ''.join(row)==z.rows[y+1],f'Incorrect native liquid/missing classification {mid}:{y}'
    for value in (255,128,64):
        if value not in raw:continue
        at=raw.index(value);point=l.table_from(dict(mapID=mid,x=(at%w+.5)/w,y=(at//w+.5)/h))
        if value==255:assert a.Terrain.Allowed(point),'Native dry permitted ground rejected'
        else:assert not a.Terrain.Allowed(point),'Native liquid/unknown accepted as dry'
        if value==128:assert a.Terrain.Allowed(point,l.table_from(dict(allowSwimming=True)))
        if value==64:unknown+=1
    checked+=1
assert checked==55 and unknown==12
l.execute('''
local count=0
for _,e in ipairs(A.CrossingData.edges) do if e.structure then
 assert(A.Structures.Get(e),'certified native floor landing must remain accessible with swimming off: '..e.structure)
 count=count+1
end end
assert(count>=6)
-- A known wet ground projection cannot invalidate the separately certified
-- native floor geometry between dry landings. Ordinary road cells gain no exemption.
local e={structure=999,a={mapID=1,x=.08,y=.5},b={mapID=1,x=.92,y=.5}}
A.TerrainData.zones[1]={w=6,h=3,widthYards=60,heightYards=30,status='complete',maskSha256='fixture',rows={'/','/','/'}}
A.WaterData.zones[1]={w=6,h=3,baseSha256='fixture',rows={'/','z','/'}}
A.StructureData.corridors[999]={source='native-wmo-floor',samples=3,maximumStep=0,headroom=3,a=e.a,b=e.b,worldA={0,0,10},worldB={60,0,10}}
assert(not A.Terrain.Segment(e.a,e.b))
assert(A.Structures.Get(e),'certified floor uses supported dry endpoints and its own source geometry')
A.StructureData.corridors[999].source='road'
assert(not A.Structures.Get(e),'roads cannot borrow certified floor exemption')
''')
print(f'PASS: all {checked} native masks and {unknown} partial maps, liquid/missing rejection, certified floor preservation')
