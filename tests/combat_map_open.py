"""Open from closed in combat through native M and the Mapperly slash command."""
from pathlib import Path
import runpy
r=Path(__file__).resolve().parents[1]
l=runpy.run_path(str(r/'tests/map_toggle.py'))['l']
l.execute('''
local create=CreateFrame
CreateFrame=function(...)local f=create(...);A.testCombatCore=f;return f end
local ok,err=pcall(assert(loadstring(...)),"Mapperly",A)
CreateFrame=create;assert(ok,err)
''',(r/'Core.lua').read_text(encoding='utf-8'))
l.execute('''
local f=A.map;local combat=false;local disabled=false;local blocked=0
InCombatLockdown=function()return combat end
f.IsProtected=function()return false end
local nativeShow=f:GetScript('OnShow')
f:SetScript('OnShow',function(self,...)
 if self.needUpdateDisplayState and combat then error('native initial display state writes protected panel delegate')end
 return nativeShow(self,...)
end)
ShowUIPanel=function(frame)
 if combat then blocked=blocked+1;return end
 frame:Show()
end
HideUIPanel=function(frame)
 if combat then blocked=blocked+1;return end
 frame:Hide()
end
-- Native ToggleWorldMap checks WorldMapDisabled before dispatching the mixin.
ToggleWorldMap=function(...)if not disabled then return f:HandleUserActionToggleSelf(...)end end
local globalToggle=ToggleWorldMap
for _,theme in ipairs({'gatherly','original'})do
 for _,compact in ipairs({true,false})do
  for _,pane in ipairs({true,false})do
   for _,via in ipairs({'M','slash'})do
    combat=false;A.db.theme=theme;A.db.compact=compact;A.db.questPane=pane
    A.Theme.Apply();A.ApplyLayout(true);f:Hide()
    local width,height=f:GetWidth(),f:GetHeight()
    mapTogglePrefs.maximized=true;mapTogglePrefs.questLog=not pane
    f.needUpdateDisplayState=true;combat=true
    if via=='M'then ToggleWorldMap()else SlashCmdList.MAPPERLY('')end
    assert(f:IsShown(),'closed map must open during combat through '..via)
    assert(blocked==0,'combat opening must not call the blocked native panel helper')
    assert(A.db.compact==compact and A.db.questPane==pane,'combat opening must preserve size and quest-pane preferences')
    assert(f:GetWidth()==width and f:GetHeight()==height,'retain the prepared Mapperly layout during combat')
    ToggleWorldMap();assert(not f:IsShown(),'M must close a map opened during combat')
    ToggleWorldMap();assert(f:IsShown(),'M must reopen it during the same combat')
    combat=false
    local apply=A.ApplyLayout;local restored
    A.ApplyLayout=function(restore)restored=restore;return apply(restore)end
    A.testCombatCore:GetScript('OnEvent')(A.testCombatCore,'PLAYER_REGEN_ENABLED')
    A.ApplyLayout=apply
    assert(restored==true and not A.combatMapOpened,'actual combat-end event must restore saved layout and clear the pending-open flag')
    assert(f:IsShown(),'post-combat processing must leave an open map visible')
   end
  end
 end
end
combat=false;f:Hide();combat=true;disabled=true
ToggleWorldMap();assert(not f:IsShown(),'native disabled-map game rules must still apply')
SlashCmdList.MAPPERLY('');assert(not f:IsShown(),'slash opening must retain native disabled-map rules')
assert(ToggleWorldMap==globalToggle,'do not replace the global toggle or bindings')
disabled=false;f:Hide();f.IsProtected=function()return true end
ToggleWorldMap();assert(not f:IsShown()and blocked==0,'do not attempt blocked native calls for protected frames')
f.IsProtected=function()return false end
A.layoutReady=nil;A.nativeWindowed=nil
ToggleWorldMap();assert(f:IsShown(),'allow first opening before an out-of-combat layout has been prepared')
combat=false;A.testCombatCore:GetScript('OnEvent')(A.testCombatCore,'PLAYER_REGEN_ENABLED')
assert(f:IsShown()and A.layoutReady,'finish initial layout after combat without closing the map')
''')
print('PASS: combat opening from closed via M/slash, repeated toggles, size/pane/theme retention and native game rules')
