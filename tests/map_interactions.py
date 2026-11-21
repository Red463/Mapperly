"""Modifier click ordering, exact marker coordinates and third-party fallback."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text(encoding='utf-8'))
lua.execute('''
fakeUI();A={};ctrl=false;alt=false
IsControlKeyDown=function() return ctrl end;IsAltKeyDown=function() return alt end;IsShiftKeyDown=function() return false end
C_Map={GetMapInfo=function() return {name='Duskwood'} end}
MapCanvasMixin={MouseAction={Click=3}}
A.map=WorldMapFrame;A.map.GetMapID=function() return 1431 end
A.map.GetNormalizedCursorPosition=function() return .9,.8 end
local mx,my=100,200;GetCursorPosition=function() return mx,my end
SetCursor=function(x,y) mx,my=x,y end
local timers={};C_Timer={After=function(_,fn) timers[#timers+1]=fn end}
RunTimers=function() local queued=timers;timers={};for _,fn in ipairs(queued) do fn() end end
starts=0;A.Navigation={ToPin=function(p) starts=starts+1;last=p;return true end}
A.ShowNote=function(map,x,y,note) edited={map=map,x=x,y=y,note=note} end
A.RefreshPins=function() end
local focus
GetMouseFoci=function() return focus and {focus} or {} end
SetFocusFrame=function(f) focus=f end
A.map.AddCanvasClickHandler=function(self,fn,priority) self.clickHandler=fn;self.clickPriority=priority end
A.map.AddGlobalPinMouseActionHandler=function(self,fn) self.pinHandler=fn end
''')
for name in ['Store.lua','Pins.lua','MapInteractions.lua']:
    path=root/name
    if path.exists(): lua.execute('assert(loadstring(...))("Mapperly",A)',path.read_text(encoding='utf-8-sig'))
lua.execute('''
A.InitStore({});A.RefreshPins=function() end
assert(A.AttachMapInteractions,'native map click integration must exist')
A.AttachMapInteractions(A.map)
assert(A.map.clickPriority>0 and not A.map.clickHandler(A.map,'LeftButton',.2,.3))
ctrl=true
local beforePing=starts
assert(not A.map.clickHandler(A.map,'LeftButton',.2,.3),'Ctrl-click must reach the ping system')
assert(starts==beforePing,'Ctrl-click must not start navigation')
alt=true
assert(not A.map.clickHandler(A.map,'LeftButton',.2,.3) and not A.map.clickHandler(A.map,'RightButton',.2,.3),'Ctrl+Alt chords must remain available to pings')
ctrl=false;alt=true
assert(A.map.clickHandler(A.map,'RightButton',.2,.3)==true and last.x==.2 and last.map==1431)
local count=starts
assert(A.map.clickHandler(A.map,'RightButton',1.2,.3)==true and starts==count,'invalid modifier click must be consumed without starting')
ctrl=false;alt=true
assert(A.map.clickHandler(A.map,'LeftButton',.4,.5) and edited.x==.4)
alt=false
assert(not A.map.clickHandler(A.map,'RightButton',.2,.3),'bare right-click must still zoom out')
local p=A.AddNote(1431,.25,.5,'Camp',{icon='inn',group='Friends'})
local pin={data=p};for k,v in pairs(MapperlyMapPinMixin) do pin[k]=v end
local forwarded=0;A.map.ProcessCanvasClickHandlers=function(_,button) assert(button=='LeftButton');forwarded=forwarded+1 end
ctrl=true;pin:OnClick('LeftButton');assert(forwarded==1 and starts==count,'Ctrl-click on a note must forward to native ping handlers')
ctrl=false;alt=true;pin:OnClick('RightButton');assert(last==p,'Alt-right-click must use the precise marker coordinates')
alt=false
ctrl=false;pin:OnClick('LeftButton');assert(edited.note==p,'ordinary note click must open editor')
local native=CreateFrame('Button',nil,A.map:GetCanvas())
native.GetMap=function() return A.map end;native.GetPosition=function() return .12345,.45678 end
SetFocusFrame(native);ctrl=false;alt=true
local event=A.waypointMouseEvents:GetScript('OnEvent')
ctrl=true
assert(not A.map.pinHandler(A.map,3,'LeftButton') and not A.map.pinHandler(A.map,3,'RightButton'),'native pin ping clicks must not be consumed')
local pingStarts=starts
event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','LeftButton');event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','LeftButton');RunTimers()
event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton');event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton');RunTimers()
assert(starts==pingStarts,'raw fallback must leave Ctrl ping clicks alone')
ctrl=false
local nativeCount=starts
event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton');event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton')
assert(starts==nativeCount,'native pins must not be rebuilt before their own OnClick runs')
assert(A.map.pinHandler(A.map,3,'RightButton') and last.x==.12345)
RunTimers();assert(starts==nativeCount+1,'native handler and fallback must create only one destination')
assert(not A.map.pinHandler(A.map,2,'RightButton'),'mouse-down must not start navigation')
native.OnClick=function() end
event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton');event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton')
RunTimers();assert(starts==nativeCount+2,'overriding native OnClick must still get a deferred waypoint fallback')
local raw=CreateFrame('Button',nil,native);raw.node={name='Copper vein'}
SetFocusFrame(raw)
event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton')
event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton')
RunTimers()
assert(last.name=='Copper vein' and last.x==.12345,'raw addon buttons must use their native wrapper position')
count=starts;event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton');SetCursor(130,200)
event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton');assert(starts==count,'dragging must never place waypoints')
RunTimers();assert(starts==count)
SetFocusFrame(UIParent);event(A.waypointMouseEvents,'GLOBAL_MOUSE_DOWN','RightButton');event(A.waypointMouseEvents,'GLOBAL_MOUSE_UP','RightButton')
assert(starts==count,'clicking outside map must never place waypoints')
''')
print('PASS: ping passthrough, Alt-right waypoints/Alt-left notes, native consumption, exact marker coordinates, raw addon pins and drag exclusion')
