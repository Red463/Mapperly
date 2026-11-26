"""Minimap route transforms, clipping, rotation, zoom and live preferences."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute("fakeUI();A={};radius=100;heading=0;shape='ROUND';rotate='0'")
for file in ['Store.lua','RouteProgress.lua','RouteStyle.lua','MinimapRoute.lua']:
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
local created={}
local create=CreateFrame
CreateFrame=function(kind,name,parent,...)
 local region=create(kind,name,parent,...)
 if parent==R.overlay and (kind=='Line' or kind=='Texture') then created[#created+1]=region end
 return region
end
R.Update()
assert(#R.lines==2 and R.lines[1]:IsShown(),'visible segments must leave a gap for the native player arrow')
assert(R.lines[1].thickness==2.5,'minimap route should use a 2.5px core')
local first=R.lines[1].lineStart[3]
radius=200;R.Update()
assert(math.abs(R.lines[1].lineStart[3])<math.abs(first),'zoom/range changes must update the projection')
rotate='1';heading=math.pi/2;R.Update()
assert(math.abs(R.lines[1].lineStart[3])<.0001 and math.abs(R.lines[1].lineStart[4])>0,'rotation changes must redraw the line')
-- Follow a long walking leg past the player, just outside the native arrow gap.
-- Both raw endpoints lie beyond the minimap, so the projected split must be computed before clipping.
local plan={kind='walking',points={{worldX=-320,worldY=-490,instance=0},{worldX=-640,worldY=-490,instance=0}}}
local separatePreview={kind='walking',points=plan.points}
local displayed=plan
local initialDisplay=A.JourneyView.DisplayPlan
A.JourneyView.DisplayPlan=function() return displayed end
A.Journey={active=plan,index=2,Leg=function() end}
local render=A.RouteStyle.Render
local visible={}
A.RouteStyle.Render=function(segments,...)
 visible=segments
 return render(segments,...)
end
rotate='0';radius=100;R.Update()
assert(#visible==2 and visible[1].kind=='completed' and visible[2].kind=='ahead','the player divides the current visible leg')
assert(visible[1][1]<-80 and math.abs(visible[1][3])<.001 and math.abs(visible[2][1])<.001 and visible[2][3]>80,
 'the two styles must meet at the player projection, even with both endpoints offscreen')
assert(#R.directions==1 and R.directions[1][1]:IsShown() and R.directions[1][1].lineStart[3]>0,
 'only one chevron should be visible and it must point along the upcoming portion')
local allocated=#created
R.Update();assert(#created==allocated,'redrawing unchanged geometry must reuse allocated regions')
displayed=separatePreview;R.Update()
assert(#visible==1 and visible[1].kind=='ahead','a separate preview must not inherit the active journey split')
displayed={kind='walking',points={
 {worldX=-440,worldY=-430,instance=0},{worldX=-560,worldY=-430,instance=0},
 {worldX=-440,worldY=-520,instance=0,breakBefore=true},{worldX=-560,worldY=-520,instance=0}}}
R.Update()
assert(#visible==2 and visible[2].split,'the minimap must preserve breaks between visible legs')
local tip=R.directions[1][1].lineStart
assert(R.directions[1][1]:IsShown() and math.abs(tip[4]+20)<.001,
 'the sole direction marker should prefer the visible forward route nearest the player')
local hairpin={kind='walking',points={
 {worldX=-395,worldY=-500,instance=0},{worldX=-570,worldY=-500,instance=0},
 {worldX=-570,worldY=-518,instance=0},{worldX=-430,worldY=-518,instance=0}}}
A.Journey.active=hairpin;displayed=hairpin;R.Update()
assert(visible[2].fromPlayer and not visible[3].fromPlayer and not visible[4].fromPlayer,
 'only the upcoming piece of the current walking segment starts the preferred arrow run')
tip=R.directions[1][1].lineStart
assert(tip[3]>8 and math.abs(tip[4])<.001,'a close return leg cannot steal the chevron from the current direction')
hairpin.points[1].worldX=-500;R.Update()
assert(visible[1].fromPlayer and R.directions[1][1].lineStart[3]>8,
 'the current direction must also take priority just as the player starts the route')
displayed={points={{worldX=-380,worldY=-500,instance=0,transport=true},{worldX=-620,worldY=-500,instance=0,transport=true}}}
R.Update()
assert(#R.fragments.dots>0 and not R.directions[1][1]:IsShown(),'transport draws dots and releases the walking chevron')
for _,dot in ipairs(R.fragments.dots) do if dot:IsShown() then
 local x,y=dot.point[4],dot.point[5]
 assert(math.sqrt(x*x+y*y)-dot:GetWidth()/2>=8,'the full transport dot must clear the native player arrow')
end end
A.RouteStyle.Render=render
A.db.showMinimapRoute=false;R.Update()
for _,region in ipairs(created) do assert(not region:IsShown(),'a hidden minimap route must release every stroke and marker') end
A.db.showMinimapRoute=true;Minimap:Hide();R.Update();assert(not R.lines[1]:IsShown())
Minimap:Show();C_Minimap.GetViewRadius=function() return nil end;R.Update();assert(not R.lines[1]:IsShown(),'unavailable minimap geometry must hide stale lines')
A.Journey=nil;A.JourneyView.DisplayPlan=initialDisplay
CreateFrame=create
''')
print('PASS: minimap projection, clipped progress, direction, pooled cleanup and display preferences')
