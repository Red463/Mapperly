"""Exercise the shared quest/services side slot through its real controls."""
from pathlib import Path
import runpy

lua = runpy.run_path(str(Path(__file__).with_name("run.py")))["lua"]
lua.execute("""
InCombatLockdown=function() return false end
local builds=0
A.CreateNearbyServicesPanel=function(map)
    builds=builds+1
    return CreateFrame('Frame',nil,map)
end
local function click(key)
    local button=A.controls[key]
    button:GetScript('OnClick')(button)
end
local function verify(services,quests)
    assert(A.servicesPanel:IsShown()==services)
    assert(A.map.QuestLog:IsShown()==quests)
    assert(A.controls.services.active==services)
    assert(A.controls.quests.active==quests)
    assert(A.settingsControls.questPane:GetChecked()==quests)
    assert(A.questPaneExtent==((services or quests) and 345 or 0))
end
for _,compact in ipairs({false,true}) do
    for _,theme in ipairs({'gatherly','original'}) do
        A.db.compact=compact;A.Theme.Set(theme)
        for _,preference in ipairs({false,true}) do
            A.db.questPane=preference;A.ApplyLayout();A.SyncSettings()
            local b=A.controls.services
            b:GetScript('OnEnter')(b)
            assert(GameTooltip:GetText()=='Show nearby services')
            click('services')
            verify(true,false)
            assert(GameTooltip:GetText()=='Hide nearby services')
            assert(A.db.questPane==preference and A.servicesPanel:GetParent()==A.map)
            assert(A.servicesPanel:GetWidth()==333 and A.servicesPanel.point[2]==A.map)
            local withPanel=A.map.ScrollContainer:GetWidth()
            -- A native hide notification while browsing services must preserve the saved quest choice.
            A.map:SetQuestLogPanelShown(false)
            verify(true,false)
            click('services');verify(false,preference)
            b:GetScript('OnLeave')(b)
            click('services');click('quests');verify(false,true)
            assert(A.map.ScrollContainer:GetWidth()==withPanel)
            click('services');A.map:SetQuestLogPanelShown(true);verify(false,true)
            click('services')
            local setting=A.settingsControls.questPane
            setting:SetChecked(true);setting:GetScript('OnClick')(setting);verify(false,true)
        end
    end
end
assert(builds==1,'reuse the drawer across openings and theme changes')
InCombatLockdown=function() return true end
click('services')
assert(A.layoutPending and not A.servicesPanel:IsShown() and A.map.QuestLog:IsShown(),
       'defer native layout changes during combat')
InCombatLockdown=function() return false end
A.ApplyLayout()
verify(true,false)
""")
print("PASS: services toolbar, shared drawer geometry, dynamic tooltips, quest bindings and preferences")
