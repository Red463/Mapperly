"""Minimap route transforms, clipping, rotation, zoom and live preferences."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute("fakeUI();A={};radius=100;heading=0;shape='ROUND';rotate='0'")
for file in ['Store.lua','MinimapRoute.lua']:
 p=root/file
 if p.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',p.read_text(encoding='utf-8'))
lua.execute('''
A.InitStore({layoutVersion=2})
assert(A.db.navigationMode=='terrain' and A.db.showMinimapRoute,'smart routing and minimap route should default on')
local R=A.MinimapRoute;assert(R,'minimap route module must exist')
local hbd={GetPlayerWorldPosition=function() return -500,-500,0 end,
 GetWorldCoordinatesFromZone=function(_,x,y,map) return -x*1000,-y*1000,0 end}
LibStub=function() return hbd end
C_Minimap={GetViewRadius=function() return radius end,IsRotateMinimapIgnored=function() return false end}
GetCVar=function() return rotate end;GetPlayerFacing=function() return heading end
GetMinimapShape=function() return shape end
local x,y=R.Project(-600,-500,-500,-500,100,200,200,0)
assert(math.abs(x-100)<.0001 and y==0,'HBD world west/east axis must project correctly')
x,y=R.Project(-500,-400,-500,-500,100,200,200,math.pi/2)
assert(math.abs(x-100)<.0001 and math.abs(y)<.0001,'rotating minimaps must transform north correctly')
local a,b,c,d=R.Clip(-200,0,200,0,200,200,'ROUND')
assert(a<0 and c>0 and math.abs(a)<100 and math.abs(c)<100,'off-screen endpoints must still draw a crossing segment')
assert(not R.Clip(80,80,90,90,200,200,'ROUND'))
assert(R.Clip(80,80,90,90,200,200,'SQUARE'),'square minimaps must retain visible corner lines')
A.JourneyView={DisplayPlan=function() return {kind='walking',points={{mapID=1,x=.4,y=.5},{mapID=1,x=.6,y=.5}}} end}
R.Update()
assert(#R.lines==2 and R.lines[1]:IsShown(),'visible segments must leave a gap for the native player arrow')
local first=R.lines[1].lineStart[3]
radius=200;R.Update()
assert(math.abs(R.lines[1].lineStart[3])<math.abs(first),'zoom/range changes must update the projection')
rotate='1';heading=math.pi/2;R.Update()
assert(math.abs(R.lines[1].lineStart[3])<.0001 and math.abs(R.lines[1].lineStart[4])>0,'rotation changes must redraw the line')
A.db.showMinimapRoute=false;R.Update();assert(not R.lines[1]:IsShown())
A.db.showMinimapRoute=true;Minimap:Hide();R.Update();assert(not R.lines[1]:IsShown())
Minimap:Show();C_Minimap.GetViewRadius=function() return nil end;R.Update();assert(not R.lines[1]:IsShown(),'unavailable minimap geometry must hide stale lines')
''')
print('PASS: minimap world axes, zoom, rotation, circle/square clipping, player-arrow gap and display preferences')
