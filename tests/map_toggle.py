"""M must close Mapperly despite character-specific native display preferences.
Behavioral model from Forever QuestLogOwnerMixin.HandleUserActionToggleSelf;
source: Gethe/wow-ui-source, forever/Interface/AddOns/Blizzard_WorldMap.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tests/run.py').read_text(encoding='utf8')
setup=r"""
GameMenuEscPriority={AddOn=8}
function RegisterGameMenuEscHandler()
 error('Mapperly must leave the global game-menu Escape dispatcher untouched')
end
-- Native CreateFrame publishes named frames for CloseSpecialWindows to resolve.
local createFrame=CreateFrame
CreateFrame=function(kind,name,...)
 local frame=createFrame(kind,name,...)
 if name then _G[name]=frame end
 return frame
end
mapTogglePrefs={maximized=true,questLog=false}
mapNativeOpens=0;mapNativeCalls=0;mapPanelCloses=0
ShowUIPanel=function(f) f:Show() end
HideUIPanel=function(f) assert(f==WorldMapFrame);mapPanelCloses=mapPanelCloses+1;f:Hide() end
WorldMapFrame.IsMaximized=function(self)return self.nativeMaximized==true end
WorldMapFrame.HandleUserActionToggleSelf=function(self,...)
 mapNativeCalls=mapNativeCalls+1
 if self:IsShown() then
  if self:IsMaximized() or not mapTogglePrefs.maximized and mapTogglePrefs.questLog==self.QuestLog:IsShown() then
   HideUIPanel(self)
  else
   -- Native mode transition instead of closing, due to saved character state.
   ShowUIPanel(self)
   if mapTogglePrefs.maximized then self:Maximize() else self:SetQuestLogPanelShown(false) end
  end
 else
  mapNativeOpens=mapNativeOpens+1;ShowUIPanel(self)
  if mapTogglePrefs.maximized then self:Maximize() else self:Minimize() end
  self:SetQuestLogPanelShown(mapTogglePrefs.questLog)
 end
 return 'native result',select('#',...)
end
ToggleWorldMap=function(...)return WorldMapFrame:HandleUserActionToggleSelf(...)end
mapOriginalGlobalToggle=ToggleWorldMap
"""
source=source.replace('A.AttachMap()\nassert(A.map==WorldMapFrame',setup+'\nA.AttachMap()\nassert(A.map==WorldMapFrame',1)
context={'__file__':str(root/'tests/run.py')}
exec(compile(source,str(root/'tests/run.py'),'exec'),context)
l=context['lua']
l.execute("""
InCombatLockdown=function()return false end
local f=A.map
for _,nativeMax in ipairs({true,false}) do
 for _,nativeQuest in ipairs({true,false}) do
  for _,pane in ipairs({true,false}) do
   for _,compact in ipairs({true,false}) do
    mapTogglePrefs.maximized=nativeMax;mapTogglePrefs.questLog=nativeQuest
    A.db.questPane=pane;A.db.compact=compact
    f.nativeMaximized=false;f:Hide()
    local opened=mapNativeOpens
    local result,count=ToggleWorldMap('forward',42)
    assert(f:IsShown() and mapNativeOpens==opened+1,'M must retain the native opening path')
    assert(result=='native result' and count==2,'native opening arguments and return values must survive')
    -- Mapperly may legitimately use a different pane/size from native CVars.
    A.db.questPane=pane;A.db.compact=compact;A.ApplyLayout(true)
    local calls,closed=mapNativeCalls,mapPanelCloses
    ToggleWorldMap()
    assert(not f:IsShown(),'second M must close, even with mismatched native maximized/quest settings')
    assert(mapPanelCloses==closed+1,'close must retain native panel cleanup')
    assert(mapNativeCalls==calls,'visible toggle must not enter the native reopen/mode-transition branch')
    assert(A.db.questPane==pane and A.db.compact==compact,'closing must not change remembered Mapperly size or pane')
   end
  end
 end
end
assert(ToggleWorldMap==mapOriginalGlobalToggle,'do not replace the global map function or bindings')
local method=f.HandleUserActionToggleSelf;A.AttachMap();assert(f.HandleUserActionToggleSelf==method,'attachment must not nest toggle wrappers')
f:Show();local closed=mapPanelCloses;A.closeButton:GetScript('OnClick')();assert(not f:IsShown() and mapPanelCloses==closed+1)
f:Hide();ToggleWorldMap();assert(f:IsShown());ToggleWorldMap();assert(not f:IsShown())
f:Show();local hide=HideUIPanel;HideUIPanel=nil;ToggleWorldMap();assert(not f:IsShown(),'missing panel helper still closes the frame');HideUIPanel=hide
""")
print('PASS: M opens/closes across 16 character-display combinations, native open forwarding, close cleanup and attachment isolation')
