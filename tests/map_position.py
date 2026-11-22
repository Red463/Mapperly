"""Position persistence and decorated bounds through real map/settings callbacks."""
from pathlib import Path
import runpy
context = runpy.run_path(str(Path(__file__).with_name('run.py')))
lua = context['lua']
lua.execute('''
InCombatLockdown=function() return false end
local f=A.map
local uiScale=.7
UIParent.GetEffectiveScale=function() return uiScale end
f.GetEffectiveScale=function() return uiScale end
UIParent.GetLeft=function() return 0 end
UIParent.GetTop=function(self) return self:GetHeight() end
-- Resolve the map anchor into the coordinates reported by the real frame API.
f.GetLeft=function(self)
 local p=self.point
 if p[1]=='CENTER' then return (UIParent:GetWidth()-self:GetWidth())/2+p[4] end
 return p[4]
end
f.GetTop=function(self)
 local p=self.point
 if p[1]=='CENTER' then return (UIParent:GetHeight()+self:GetHeight())/2+p[5] end
 return UIParent:GetHeight()+p[5]
end
local nativeMinimize=f.Minimize
local nativeCalls=0
f.IsMaximized=function() return false end
f.Minimize=function(self)
 nativeCalls=nativeCalls+1;nativeMinimize(self)
 self:SetPoint('TOPLEFT',UIParent,'TOPLEFT',16,100)
end
for _,dims in ipairs({{3440,1440},{5120,1440},{2560,1080},{1920,1080},{800,600}}) do
 UIParent:SetSize(dims[1],dims[2])
 for _,compact in ipairs({true,false}) do
  A.db.compact=compact;A.db.questPane=true;A.ApplyLayout(true)
  A.bar:GetScript('OnDragStart')()
  assert(A.dragging,'both map sizes must support user positioning when unlocked')
  f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',24,-36)
  A.bar:GetScript('OnDragStop')()
  local function stays()
   assert(math.abs(f:GetLeft()-24)<.01 and math.abs(f:GetTop()-(dims[2]-36))<.01,'theme/lock/quest changes must retain the dragged map position')
  end
  local calls=nativeCalls
  A.Theme.Set('original');stays()
  A.Theme.Set('gatherly');stays()
  A.settingsControls.locked:SetChecked(true);A.settingsControls.locked:GetScript('OnClick')(A.settingsControls.locked);stays()
  A.settingsControls.locked:SetChecked(false);A.settingsControls.locked:GetScript('OnClick')(A.settingsControls.locked);stays()
  A.controls.quests:GetScript('OnClick')();stays()
  assert(nativeCalls==calls,'ordinary settings changes must not invoke native minimise/panel placement')
  A.map:GetScript('OnShow')(A.map);stays()
  -- A persisted point from another display must be fitted, including crest/trim.
  local key=compact and 'position' or 'largePosition'
  A.db[key]={x=dims[1]*2,y=100};A.ApplyLayout(true)
  assert(f:GetLeft()>=12 and f:GetLeft()+f:GetWidth()<=dims[1]-12+.01,'right/left trim must stay on screen')
  assert(f:GetTop()<=dims[2]-16+.01 and f:GetTop()-f:GetHeight()>=12-.01,'top crest and bottom trim must stay on screen')
 end
end
UIParent:SetSize(3440,1440);A.db.compact=true;A.db.position={x=200,y=-80};A.ApplyLayout(true)
A.db.compact=false;A.db.largePosition={x=300,y=-100};A.ApplyLayout(true)
A.db.compact=true;A.ApplyLayout()
assert(f:GetLeft()==200 and f:GetTop()==1360,'compact and enlarged positions must be remembered independently')
-- Capture unexpected native/addon drag paths before a settings relayout as well.
f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',250,-90)
A.Theme.Set('original')
assert(f:GetLeft()==250 and f:GetTop()==1350,'actual position must be captured before relayout')
-- Native panel layout can write an anchor after OnShow; the settled callback
-- must restore the owned position rather than remembering the temporary one.
local timers={}
C_Timer={After=function(_,fn) timers[#timers+1]=fn end}
A.map:GetScript('OnShow')(A.map)
f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',16,100)
assert(#timers==1)
timers[1]()
assert(f:GetLeft()==250 and f:GetTop()==1350,'deferred native panel positioning must not cut off or move the map')
C_Timer=nil
A.ResetMapPosition()
assert(A.db.position==nil and A.db.largePosition==nil,'explicit reset must clear both remembered positions')
assert(math.abs(f:GetLeft()-(UIParent:GetWidth()-f:GetWidth())/2)<.01,'reset must centre the map without recapturing its previous position')
-- A canvas resize can queue a viewport fit just before or during a drag.
-- Running that callback must not restore the pre-drag saved coordinates.
A.db.compact=true;A.db.locked=false;A.db.position={x=200,y=-80};A.ApplyLayout(true)
local dragTimers={}
C_Timer={After=function(_,fn) dragTimers[#dragTimers+1]=fn end}
A.QueueViewportFit()
A.bar:GetScript('OnDragStart')()
f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',350,-120)
dragTimers[1]()
assert(f:GetLeft()==350 and f:GetTop()==1320,'a queued viewport fit must not snap an active drag back to the saved position')
A.ApplyLayout(true)
assert(f:GetLeft()==350 and f:GetTop()==1320,'layout callbacks must defer while the user is dragging')
A.bar:GetScript('OnDragStop')()
for i=2,#dragTimers do dragTimers[i]() end
assert(A.db.position.x==350 and A.db.position.y==-120,'release must save the new point before deferred layout runs')
assert(f:GetLeft()==350 and f:GetTop()==1320,'deferred layout after release must keep the new point')
C_Timer=nil
-- Cover callbacks dispatched synchronously by StopMovingOrSizing, before
-- OnDragStop has a chance to save, as well as late queued callbacks.
local stopMoving=f.StopMovingOrSizing
for _,dims in ipairs({{3440,1440},{5120,1440},{2560,1080},{1920,1080}}) do
 UIParent:SetSize(dims[1],dims[2])
 for _,compact in ipairs({true,false}) do
  A.db.compact=compact;A.ApplyLayout(true)
  A.bar:GetScript('OnDragStart')()
  f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',240,-90)
  f.StopMovingOrSizing=function(self)
   A.PositionMap();A.FitViewport();A.ApplyLayout(true)
   assert(A.dragging and self:GetLeft()==240 and self:GetTop()==dims[2]-90,'stop callbacks must not restore the old point before the drag is saved')
  end
  A.bar:GetScript('OnDragStop')()
  assert(not A.dragging and not A.dragLayoutPending and not A.dragViewportPending,'deferred work must drain after release')
  local key=compact and 'position' or 'largePosition'
  assert(A.db[key].x==240 and A.db[key].y==-90,'stop callbacks must preserve the released point in both modes')
  A.QueueViewportFit()
  assert(f:GetLeft()==240 and f:GetTop()==dims[2]-90,'late fits must retain the released point')
 end
end
f.StopMovingOrSizing=stopMoving
UIParent:SetSize(3440,1440);A.db.compact=true;A.ApplyLayout(true)
-- UI scale conversion must apply to both axes, not just the vertical origin.
f.GetEffectiveScale=function() return uiScale*1.25 end
f.GetLeft=function() return 160 end;f.GetTop=function() return 1000 end
A.bar:GetScript('OnDragStart')();A.bar:GetScript('OnDragStop')()
assert(A.db.position.x==200 and A.db.position.y==-190,'drag saves must use UIParent coordinate units on both axes')
''')
print('PASS: map position survives settings and reopening; queued/in-drag/stop callbacks cannot snap movement back; ultrawide bounds and UI scale conversion')
