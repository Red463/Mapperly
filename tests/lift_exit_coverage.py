"""Lift exit coverage must work across clear ground, not isolated tiny disks."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parents[1]
lua=runpy.run_path(str(root/'tests/native_local_transports.py'))['lua']
lua.execute('''
A.LocalTransportData.build=70959;A.InitStore({})
local T,P=A.Transports,A.TravelNetwork
for _,row in ipairs(A.LocalTransportData.edges) do
 local grid=row.arrivalExitMask
 assert(grid and grid.version==1,'both lift exits need broad native coverage instead of tiny point triggers')
 local count=0
 for line,bits in ipairs(grid.rows) do
  for column=1,#bits do if bits:sub(column,column)=='1' then
   local x=grid.originEast-(column-.5)*grid.cellSize
   local y=grid.originNorth-(line-.5)*grid.cellSize
   local p=P.Transform({worldX=x,worldY=y,instance=1},grid.mapID)
   UnitPosition=function() return y,x,0,1 end
   assert(T.CanDisembark(row,p,{}),'every certified ground cell must allow handoff with zero height')
   count=count+1
  end end
 end
 assert(count>=900,'coverage must span the landing surroundings, rather than just the previous recorded endpoint')
 local bad=P.Transform({worldX=-1852.166,worldY=-4661.586,instance=1},grid.mapID)
 UnitPosition=function() return -4661.586,-1852.166,0,1 end
 assert(not T.CanDisembark(row,bad,{}),'broad coverage cannot include the lift shaft')
end
''')
print('PASS: every broad native exit cell permits walking handoff, both directions, while shaft stays blocked')
