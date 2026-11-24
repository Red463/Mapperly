"""Replay Forever's AcquirePin mouse-routing callback with combat restrictions."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.test-deps'))
from lupa.lua51 import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute((root/'tests/wow.lua').read_text())
lua.execute('''
fakeUI();A={map=WorldMapFrame};combat=false;writes=0
InCombatLockdown=function() return combat end
-- Native contract: MapCanvas_DataProviderBase.lua, forever branch,
-- MapCanvasPinMixin:CheckMouseButtonPassthrough (clear, then apply).
MapCanvasPinMixin={}
function MapCanvasPinMixin:CheckMouseButtonPassthrough(...)
 self:SetPassThroughButtons()
 local buttons={}
 for i=1,select('#',...) do
  local button=select(i,...)
  if self:ShouldMouseButtonBePassthrough(button) then buttons[#buttons+1]=button end
 end
 self:SetPassThroughButtons(unpack(buttons))
end
native=MapCanvasPinMixin.CheckMouseButtonPassthrough
function pin(category)
 local p=CreateFrame('Button',nil,A.map)
 for k,v in pairs(MapCanvasPinMixin) do p[k]=v end
 for k,v in pairs(MapperlyMapPinMixin) do p[k]=v end
 p.data={category=category};p.GetMap=function()return A.map end
 p.SetPassThroughButtons=function(self,...)
  assert(not combat,'Button:SetPassThroughButtons() blocked in combat')
  writes=writes+1;self.passes={...}
 end
 return p
end
''')
lua.execute('assert(loadstring(...))("Mapperly",A)',(root/'Pins.lua').read_text())
lua.execute('''
local service=pin('inn');service:CheckMouseButtonPassthrough('RightButton')
assert(service.passes[1]=='RightButton')
local before=writes;combat=true
-- AcquirePin calls this after OnAcquired on every new or reused pin.
for i=1,49 do service:CheckMouseButtonPassthrough('RightButton') end
local note=pin('notes');note:CheckMouseButtonPassthrough('RightButton')
assert(writes==before,'Combat acquisition must not write restricted input state')
A.FlushPinMouseRouting();assert(writes==before,'Combat flush must also defer')
combat=false;A.FlushPinMouseRouting()
assert(service.passes[1]=='RightButton' and #note.passes==0)
assert(writes==before+4,'Repeated acquisitions must coalesce per pin')
before=writes;A.FlushPinMouseRouting();assert(writes==before,'Flush must drain pending work')
-- Reused pins must use their latest category, not stale passthrough decisions.
combat=true;service:CheckMouseButtonPassthrough('RightButton');service.data.category='notes'
combat=false;A.FlushPinMouseRouting();assert(#service.passes==0)
combat=true;note:CheckMouseButtonPassthrough('RightButton');note:OnReleased()
combat=false;before=writes;A.FlushPinMouseRouting();assert(writes==before,'Released pins must not be configured')
combat=true;service:CheckMouseButtonPassthrough('RightButton');service:Hide()
combat=false;before=writes;A.FlushPinMouseRouting();assert(writes==before,'Hidden pins must not be configured')
assert(MapCanvasPinMixin.CheckMouseButtonPassthrough==native,'Do not patch Blizzard or other addons globally')
''')
print('PASS: Mapperly pin input defers in combat, coalesces, restores latest routing and discards released/hidden pins')
