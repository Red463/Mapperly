"""Native Stormwind street hints participate in routing without changing ground."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('A={}')
for f in ['Data/Terrain.lua','Data/Roads.lua','Data/RoadsSupplement.lua','Roads.lua','Terrain.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text(encoding='utf8'))
lua.execute('''
local terrain=A.Terrain.Zone(1453);local original=terrain.rows
local base=A.RoadData.zones[1453];local patch=A.RoadSupplementData.zones[1453]
local chosen=A.Roads.Zone(1453,terrain)
assert(chosen and chosen.roadCells==5614,'Stormwind routing must use the native street and pier supplement')
local usable=0
for y=0,chosen.h-1 do for x=0,chosen.w-1 do
 if A.Roads.Cell(chosen,x,y) and not A.Roads.Cell(base,x,y) and A.Terrain.Allowed({mapID=1453,x=(x+.5)/chosen.w,y=(y+.5)/chosen.h}) then usable=usable+1 end
end end
assert(usable>100,'the added street hints must cover actual permitted walking cells')
local hash=patch.terrainMaskSha256;patch.terrainMaskSha256='stale'
assert(A.Roads.Zone(1453,terrain)==base,'stale terrain binding must retain the original hints');patch.terrainMaskSha256=hash
local row=patch.baseRows[1];patch.baseRows[1]='stale'
assert(A.Roads.Zone(1453,terrain)==base,'stale base rows cannot borrow the supplement');patch.baseRows[1]=row
assert(terrain.rows==original,'road hints must not rewrite walkability')
print('Additional usable Stormwind street cells:',usable)
''')
print('PASS: runtime street supplement, useful walking coverage, stale fallback and unchanged permissions')
