"""Swimming policy applies to searches, guards, approaches and reused geometry."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
l=LuaRuntime(unpack_returned_tuples=True);l.execute('A={db={allowSwimming=true}}')
for f in ['Terrain.lua','PathReuse.lua']:
 l.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
if (root/'Water.lua').exists():l.execute('assert(loadstring(...))("Mapperly",A)',(root/'Water.lua').read_text())
l.execute('''
A.TerrainData={version=1,zones={[1]={status='complete',w=6,h=3,widthYards=60,heightYards=30,maskSha256='base',rows={'/','/','/'}}}}
A.WaterData={version=1,build=70959,zones={[1]={w=6,h=3,baseSha256='base',rows={'/','z','/'}}}}
local a,b={mapID=1,x=.08,y=.5},{mapID=1,x=.92,y=.5}
assert(A.Terrain.Path(a,b))
A.db.allowSwimming=false
assert(not A.Terrain.Segment(a,b),'dry mode must reject known liquid')
assert(not A.Terrain.Allowed({mapID=1,x=.5,y=.5}))
local p=assert(A.Terrain.Path(a,b));assert(#p>2,'dry mode must detour around water instead of using allowed-mode cache')
assert(A.Terrain.Validate({points=p}))
assert(not A.Terrain.Validate({points={a,b}}))
assert(A.Terrain.Segment(a,b,{allowSwimming=true}),'explicit allowed policy overrides saved preference')
local direct=assert(A.Terrain.Path(a,b,{allowSwimming=true}));assert(#direct==2)
local approach=assert(A.Terrain.Approach({mapID=1,x=.5,y=.5},20));assert(A.Terrain.Allowed(approach))
A.WaterData.zones[1].rows[2]='/'
assert(A.Terrain.Segment(a,b));assert(#assert(A.Terrain.Path(a,b))==2,'mutable water inputs invalidate dry reuse')
A.WaterData.zones[1].baseSha256='stale'
assert(not A.Terrain.Segment(a,b),'stale source cannot assert dryness')
assert(not A.Terrain.Path(a,b),'unknown water coverage fails closed')
A.db.allowSwimming=true
assert(A.Terrain.Segment(a,b),'unknown water coverage preserves existing allowed mode')
assert(A.Water and A.Water.AllowSwimming({allowSwimming=false})==false)
assert(not A.Water.Zone(999,nil),'unsupported overview must return no coverage')
''')
print('PASS: swimming guards, dry detour, explicit options, mutable cache, stale/unknown rejection')
