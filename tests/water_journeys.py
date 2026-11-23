"""Real dry-mode service planning and Great Lift native-floor exit checks."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
# Reuse the source-backed native service scenario with water policy loaded and
# disabled before planning; every walking leg validates against the dry grid.
path=root/'tests/nearest_services_native.py';source=path.read_text()
source=source.replace("'Data/Terrain.lua',","'Data/Terrain.lua','Data/Water.lua','Water.lua',")
source=source.replace('A.InitStore({preferRoads=true,','A.InitStore({allowSwimming=false,preferRoads=true,')
exec(compile(source,str(path),'exec'),dict(__file__=str(path)))
# Every certified exit cell is dry in the actual liquid source as well as the
# original native ground proof. Retain the existing zero-height handoff tests.
context=runpy.run_path(str(root/'tests/native_local_transports.py'));lua=context['lua']
for name in ['Data/Water.lua','Water.lua']:
 lua.execute('assert(loadstring(...))("Mapperly",A)',(root/name).read_text())
lua.execute('''
A.db.allowSwimming=false
local count=0
for _,row in ipairs(A.LocalTransportData.edges) do
 local grid=row.arrivalExitMask
 for line,bits in ipairs(grid.rows) do for column=1,#bits do if bits:sub(column,column)=='1' then
  local east=grid.originEast-(column-.5)*grid.cellSize
  local north=grid.originNorth-(line-.5)*grid.cellSize
  local p=A.TravelNetwork.Transform({worldX=east,worldY=north,instance=1},grid.mapID)
  assert(A.Terrain.Segment(p,p),'certified native lift exit must also have known nonliquid source')
  UnitPosition=function() return north,east,0,1 end
  assert(A.Transports.CanDisembark(row,p,{}),'swimming off must preserve every certified lift exit')
  count=count+1
 end end end
end
assert(count==2223)
''')
print('PASS: native dry-mode nearest services and all 2223 certified lift exit cells')
