"""Coordinate navigation geometry, state and input-window regression checks."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute('''
fakeUI();A={};UISpecialFrames={}
local original=CreateFrame
CreateFrame=function(kind,...)
 local f=original(kind,...)
 if kind=='FontString' then f.GetStringWidth=function(self) return #self:GetText()*7 end end
 return f
end
local mapID=1431
WorldMapFrame.GetMapID=function() return mapID end
A.map=WorldMapFrame
C_Map={GetMapInfo=function(id) return {mapID=id,name='Zone '..id,mapType=3} end}
playerX,playerY,playerInstance=0,0,0
facing=0
GetPlayerFacing=function() return facing end
hbd={GetWorldCoordinatesFromZone=function(_,x,y,map)
 if map==999 then return end
 return 1000-x*1000,1000-y*1000,map==900 and 1 or 0
end,GetPlayerWorldPosition=function() return playerX,playerY,playerInstance end,
GetZoneCoordinatesFromWorldInstance=function(_,x,y,instance,map)
 if instance~=0 then return end
 return (1000-x)/1000,(1000-y)/1000
end}
LibStub=function() return hbd end
refreshes=0;A.RefreshPins=function() refreshes=refreshes+1 end
messages={};A.Print=function(s) messages[#messages+1]=s end
''')
for name in ['Store.lua','Buttons.lua','Navigation.lua','NavigationUI.lua']:
    path=root/name
    if path.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text(encoding='utf-8-sig'))
lua.execute('''
A.InitStore({})
local N=A.Navigation
assert(N and N.Parse,'navigation must expose coordinate validation')
local x,y=N.Parse(' 42.5 ','0');assert(x==.425 and y==0)
assert(N.Parse('100','100')==1)
for _,bad in ipairs({'','abc','-1','100.1','1,2','.'}) do assert(not N.Parse(bad,'50')) end
assert(not N.Parse(0/0,50) and not N.Parse(math.huge,50))
assert(N.Start(1431,'50','50'))
local first=N.target
assert(first.map==1431 and first.x==.5 and first.worldX==500)
assert(not N.Start(1431,'bad','50') and N.target==first,'invalid replacement must preserve destination')
assert(not N.Start(999,'50','50') and N.target==first,'unmapped destination must preserve destination')
local function near(a,b) assert(math.abs(a-b)<.00001,tostring(a)..' vs '..tostring(b)) end
near(N.Bearing(0,100),0);near(N.Bearing(-100,0),-math.pi/2)
near(N.Bearing(100,0),math.pi/2);near(math.abs(N.Bearing(0,-100)),math.pi)
near(N.SmoothAngle(0,1,0),0)
local from,to=math.rad(179),math.rad(-179)
assert(N.SmoothAngle(from,to,1/60)>from or N.SmoothAngle(from,to,1/60)<-3,'smoothing must cross the shortest wrap')
local angles={}
for _,fps in ipairs({30,60,144}) do local a=0;for i=1,fps/2 do a=N.SmoothAngle(a,1.5,1/fps) end;angles[#angles+1]=a end
near(angles[1],angles[2]);near(angles[2],angles[3])
N.Tick();assert(N.frame:IsShown() and N.frame.icon:IsShown() and N.frame.label:GetText()=='707 yd')
assert(N.frame:GetFrameStrata()=='LOW','HUD must remain below map and dialogs')
local before=N.frame.icon.rotation;facing=.8;N.Animate(1/60)
assert(N.frame.icon.rotation~=before and N.frame.shadow.rotation==N.frame.icon.rotation)
playerInstance=1;N.Tick()
assert(N.target==first and not N.frame.icon:IsShown() and N.frame.label:GetText()=='Different continent / instance')
playerInstance=0;playerX=nil;N.Tick()
assert(N.target==first and not N.frame.icon:IsShown())
playerX=0;N.Tick();assert(N.frame.icon:IsShown())
facing=nil;N.Tick();assert(not N.frame.icon:IsShown(),'unavailable facing must not leave a stale arrow')
facing=0;N.Tick();assert(N.frame.icon:IsShown())
issecretvalue=function(v) return v==123456 end
playerX=123456;N.Tick();assert(not N.frame.icon:IsShown(),'protected position must not be used in geometry')
issecretvalue=nil;playerX=0
WorldMapFrame:Hide();N.Tick();assert(N.frame:IsShown(),'guide must remain visible after closing the map')
local pin=N.PinForMap(1431);assert(pin and pin.category=='navigation' and pin.x==.5)
N.frame.GetPoint=function() return 'CENTER',UIParent,'CENTER',140,180 end
N.frame:GetScript('OnDragStop')(N.frame)
assert(A.db.navigationAnchor.x==140 and A.db.navigationAnchor.y==180)
N.frame:GetScript('OnMouseUp')(N.frame,'RightButton')
assert(not N.target and not N.frame:IsShown(),'right click must stop guidance')
assert(N.Start(1431,50,50));playerX=505;playerY=500;N.Tick()
assert(not N.target and not N.frame:IsShown() and #messages>0,'arrival within ten yards must clear the destination')
playerX,playerY=0,0
assert(N.Start(1431,25,50));local active=N.target
A.ShowNavigationInput(1431)
local ui=A.navigationWindow
assert(ui and ui:IsShown() and ui.targetMap==1431)
ui.xInput:SetText('bad');ui.yInput:SetText('60');ui.start:GetScript('OnClick')()
assert(ui:IsShown() and ui.error:GetText()~='' and N.target==active)
A.map.GetMapID=function() return 1416 end
ui.xInput:SetText('35.5');ui.yInput:SetText('62.5');ui.start:GetScript('OnClick')()
assert(not ui:IsShown() and N.target.map==1431 and N.target.x==.355,'input must retain captured zone despite map navigation')
assert(N.Start(1431,'42.56','51.24'))
A.ShowNavigationInput(1431)
assert(ui.xInput:GetText()=='42.56' and ui.yInput:GetText()=='51.24','editing must preserve entered coordinate precision')
ui.start:GetScript('OnClick')();near(N.target.x,.4256);near(N.target.y,.5124)
A.ShowNavigationInput(1431);local retained=N.target
ui.xInput:GetScript('OnEscapePressed')()
assert(not ui:IsShown() and N.target==retained,'dismissing coordinate entry must not cancel an active destination')
A.ShowNavigationInput();assert(ui.targetMap==1416)
ui.stop:GetScript('OnClick')();assert(not N.target)
assert(A.InitStore({navigationAnchor={point='bogus',relativePoint='CENTER',x=0,y=0}}).navigationAnchor==nil)
assert(A.InitStore({navigationAnchor={point='CENTER',relativePoint='CENTER',x=0/0,y=0}}).navigationAnchor==nil)
assert(A.InitStore({navigationAnchor={point='CENTER',relativePoint='CENTER',x=20,y=100}}).navigationAnchor.y==100)
''')
print('PASS: navigation input, bearing/smoothing, position guards, arrival, cancellation, captured map and HUD state')
