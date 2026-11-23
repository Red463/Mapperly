"""Ground-region pruning must match terrain and invalidate with source masks."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'));sys.path.insert(0,str(root/'.test-deps'))
from build_walking_regions import components,decode_rows
assert decode_rows({1:'g',2:''},8,2)==bytes([1]+[0]*15),'trimmed empty packed cells must remain blocked'
labels,regions=components(bytes([1,0,0,1]),2,2)
assert len(regions)==2 and labels[0]!=labels[3], 'diagonally touching islands cannot share a safe region'
labels,regions=components(bytes([1,1,0,1]),2,2)
assert len(regions)==1
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('A={}')
for f in ['Terrain.lua','WalkingRegions.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/f).read_text())
lua.execute('''
A.TerrainData={version=1,zones={[1]={status='complete',w=4,h=1,widthYards=40,heightYards=10,maskSha256='base',rows={'g'}}}}
local patch={w=4,h=1,baseSha256='base',maskSha256='extra',cells=1,rows={'Q'}}
A.GroundCorrectionData={version=1,zones={[1]=patch}}
A.WalkingRegionData={version=1,zones={[1]={w=4,h=1,baseSha256='base',groundSha256='extra',groundCells=1,exceptions={{x=1,y=0,w=1,h=1,rows={'g'}}}}}}
local p={mapID=1,x=.375,y=.5}
assert(A.Terrain.Allowed(p) and A.WalkingRegions.Get(p)==2)
patch.maskSha256='changed-same-cell-count'
assert(A.WalkingRegions.Get(p)==nil,'stale region cache must not prune changed supplemental ground')
patch.baseSha256='wrong'
assert(not A.Terrain.Allowed(p),'supplement cannot apply to a different base terrain mask')
''')
print('PASS: exact four-neighbor regions and terrain/supplement source guards')
