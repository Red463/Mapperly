"""Real map controls stay usable during combat without blocked panel calls."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(r/'tests/map_toggle.py'))['l']
l.execute('''
local combat=false
InCombatLockdown=function()return combat end
local f=A.map
f.IsProtected=function()return false end
local blocked,cleanups,moves=0,0,0
HideUIPanel=function(frame,skipPoint,skipShown)
 if combat then blocked=blocked+1;return end
 cleanups=cleanups+1;frame:Hide()
end
f.StartMoving=function()moves=moves+1 end
UIParent.GetLeft=function()return 0 end
UIParent.GetTop=function(self)return self:GetHeight()end
f.GetLeft=function(self)return self.point[4]end
f.GetTop=function(self)return UIParent:GetHeight()+self.point[5]end
for _,theme in ipairs({'gatherly','original'})do
 for _,compact in ipairs({true,false})do
  combat=false;A.db.theme=theme;A.db.compact=compact;A.db.locked=false
  A.Theme.Apply();f:Show();A.ApplyLayout(true)
  combat=true
  local n=moves
  A.bar:GetScript('OnDragStart')(A.bar,'LeftButton')
  assert(moves==n+1 and A.dragging,'combat must not prevent unlocked unprotected map movement')
  f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',50,-60)
  A.bar:GetScript('OnDragStop')(A.bar)
  local key=compact and 'position'or 'largePosition'
  assert(not A.dragging and A.db[key].x==50 and A.db[key].y==-60,'combat drag must save final position')
  A.closeButton:GetScript('OnClick')(A.closeButton)
  assert(not f:IsShown(),'X must immediately close the unprotected map in combat')
  assert(blocked==0,'combat close must not call the blocked panel-manager helper')
  local closed=cleanups;combat=false;A.FinishMapClose()
  assert(cleanups==closed+1,'native panel cleanup must finish after combat')
  A.FinishMapClose();assert(cleanups==closed+1,'cleanup is performed once')
 end
end
-- A map reopened before deferred cleanup must not be closed later.
combat=false;f:Show();combat=true;ToggleWorldMap()
assert(not f:IsShown()and blocked==0,'M must also close a visible map in combat')
combat=false;A.FinishMapClose()
combat=false;f:Show();combat=true;A.closeButton:GetScript('OnClick')()
f:Show();combat=false;local n=cleanups;A.FinishMapClose()
assert(f:IsShown()and cleanups==n,'deferred close must not close a reopened map')
-- Keep explicit locking and actual protected-frame restrictions.
A.db.locked=true;combat=true;n=moves;A.bar:GetScript('OnDragStart')()
assert(moves==n,'locked map must remain locked')
A.db.locked=false;f.IsProtected=function()return true end
A.bar:GetScript('OnDragStart')();assert(moves==n,'protected frames cannot be moved insecurely in combat')
f.IsProtected=function()return false end
combat=false;f:Show();n=cleanups;A.closeButton:GetScript('OnClick')()
assert(not f:IsShown()and cleanups==n+1,'out-of-combat closing retains native panel cleanup')
''')
print('PASS: combat drag/save and immediate X close, deferred native cleanup, both sizes/themes and locked/protected guards')
