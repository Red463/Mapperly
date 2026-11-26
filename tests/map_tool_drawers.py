"""Exercise toolbar switching, fitting, and restoring the standalone editors."""
from pathlib import Path
import runpy

lua = runpy.run_path(str(Path(__file__).with_name("run.py")))["lua"]
lua.execute("""
InCombatLockdown=function() return false end
local function click(key)
    local b=A.controls[key]
    b:GetScript('OnClick')(b)
end
local function attached(key,f)
    assert(A.drawerWindow==f and A.drawerKey==key and f:IsVisible())
    assert(f:GetParent():GetParent():GetParent():GetParent()==A.map)
    assert(f:GetFrameStrata()==f:GetParent():GetFrameStrata())
    assert(not f:IsMovable() and f:GetWidth()*f.scale<=A.questPaneExtent-12)
    assert(not A.map.QuestLog:IsShown() and A.controls[key].active)
end
A.SelectQuestPane(true)
A.map:SetFrameStrata('HIGH')
click('navigate')
local nav=A.navigationWindow
attached('navigate',nav)
nav.nameInput:SetText('Return point')
local V=A.JourneyView
local direct=A.Journey.DirectPlan
A.Journey.DirectPlan=function(p) return {kind='direct',name=p.name,distance=10,points={},legs={}} end
A.db.navigationMode='direct';nav.xInput:SetText('35');nav.yInput:SetText('50')
nav.preview:GetScript('OnClick')(nav.preview)
A.Journey.DirectPlan=direct
attached('navigate',V.window)
V.close:GetScript('OnClick')(V.close)
attached('navigate',nav)
assert(nav.nameInput:GetText()=='Return point')
click('filters')
attached('filters',A.filterWindow)
assert(not nav:IsShown() and nav:GetParent()==UIParent)
assert(nav:GetFrameStrata()=='DIALOG')
local row=A.filterWindow.rows.inn
row:SetChecked(false);row:GetScript('OnClick')(row)
assert(not A.db.filters.inn)
click('settings')
local settings=A.settingsWindow
attached('settings',settings)
assert(settings.themeChrome==nil or not settings.themeChrome:IsShown())
for _,theme in ipairs({'original','gatherly'}) do
    A.Theme.Set(theme);attached('settings',settings)
    UIParent:SetSize(1024,768)
    A.db.compact=true;A.db.scale=.5;A.ApplyLayout()
    assert(A.map:GetWidth()<=UIParent:GetWidth() and A.map.ScrollContainer:GetWidth()>0)
    local child=settings:GetParent()
    assert(child:GetHeight()>=settings:GetHeight()*settings.scale and child:GetParent():GetScrollChild()==child)
end
click('size');attached('settings',settings)
click('lock');attached('settings',settings)
click('settings')
assert(A.map.QuestLog:IsShown() and settings:GetParent()==UIParent and settings:IsMovable())
click('filters');A.map:SetQuestLogPanelShown(true)
assert(not A.filterWindow:IsShown() and A.map.QuestLog:IsShown() and A.drawerKey==nil)
C_Map.GetPlayerMapPosition=function() return nil end
click('notes');attached('notes',A.noteWindow)
assert(A.noteWindow.browser:IsShown() and not A.noteWindow.tabs.edit:IsEnabled())
click('notes')
InCombatLockdown=function() return true end
click('navigate')
assert(A.layoutPending and not nav:IsShown() and A.map.QuestLog:IsShown())
InCombatLockdown=function() return false end
A.ApplyLayout();attached('navigate',nav)
A.map:Hide()
A.ShowNavigationInput(1431)
assert(nav:IsVisible() and nav:GetParent()==UIParent and nav:IsMovable() and not A.drawerKey)

-- Services defines both the usable panel width and the remaining canvas.
-- Compare the live sidebar layout at both the native and a custom quest width.
A.map:Show()
for _,size in ipairs({{1920,1080},{1024,768},{800,600}}) do
 for _,compact in ipairs({true,false}) do
  for _,theme in ipairs({'original','gatherly'}) do
   for _,width in ipairs({333,360}) do
    UIParent:SetSize(unpack(size));A.map.questLogWidth=width
    A.db.compact=compact;A.db.scale=.5;A.Theme.Set(theme)
    click('services')
    local ref=A.servicesPanel:GetWidth()
    local canvas=A.map.ScrollContainer:GetWidth()
    local visibleHeight=A.map.ScrollContainer:GetHeight()
    for _,key in ipairs({'navigate','filters','settings','notes','quests'}) do
        click(key)
        assert(A.map.ScrollContainer:GetWidth()==canvas and A.questPaneExtent==ref+12,key)
        if key=='quests' then
            assert(A.map.QuestLog:GetWidth()==ref)
        else
            local form=A.drawerWindow
            assert(form:GetWidth()==ref and form.scale==1,key)
            if size[1]>=1024 and width==333 then
                assert(form.toolHeight<=visibleHeight,key..' requires whole-panel scrolling')
            end
        end
    end
   end
  end
 end
end
""")
print("PASS: shared tool drawers, route preview Back, theme changes, compact fit and standalone navigation")
