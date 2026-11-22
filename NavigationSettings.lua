local _,A=...
local S={};A.NavigationSettings=S
function S.Sync()
    if A.smartRoutingCheck then A.smartRoutingCheck:SetChecked(A.db.navigationMode~='direct') end
    if A.journeyRouteCheck then A.journeyRouteCheck:SetChecked(A.db.showJourneyRoute) end
    if A.minimapRouteCheck then A.minimapRouteCheck:SetChecked(A.db.showMinimapRoute) end
end
function S.Build(parent)
    local U=A.Dialogs
    local mode=U.Card(parent,24,202,592,156)
    U.Label(mode,'Route planning',16,14,'GameFontNormal')
    local smart=CreateFrame('CheckButton',nil,mode,'UICheckButtonTemplate');A.smartRoutingCheck=smart
    smart:SetSize(26,26);smart:SetPoint('TOPLEFT',mode,'TOPLEFT',14,-42)
    U.Label(mode,'Smart routing',44,48)
    smart:SetScript('OnClick',function(self) A.Navigation.SetSmartRouting(not not self:GetChecked());S.Sync() end)
    local description=U.Label(mode,'Enabled by default. Finds a walking route around restricted terrain. Turn it off for straight-line guidance. Changes update the current destination immediately.',16,90,'GameFontDisableSmall')
    description:SetSize(556,58);description:SetWordWrap(true)
    local display=U.Card(parent,24,374,592,116)
    U.Label(display,'Route display',16,14,'GameFontNormal')
    local check=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.journeyRouteCheck=check
    check:SetSize(26,26);check:SetPoint('TOPLEFT',display,'TOPLEFT',14,-42)
    U.Label(display,'Show route on the world map',44,48)
    check:SetScript('OnClick',function(self)
        A.db.showJourneyRoute=not not self:GetChecked()
        if A.JourneyView then A.JourneyView.Refresh() end
    end)
    local mini=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.minimapRouteCheck=mini
    mini:SetSize(26,26);mini:SetPoint('TOPLEFT',display,'TOPLEFT',14,-76)
    U.Label(display,'Show route on the minimap',44,82)
    mini:SetScript('OnClick',function(self)
        A.db.showMinimapRoute=not not self:GetChecked()
        if A.MinimapRoute then A.MinimapRoute.Update() end
    end)
    local coverage=U.Card(parent,24,506,592,158)
    U.Label(coverage,'Walking preview coverage',16,14,'GameFontNormal')
    local text=U.Label(coverage,'This preview plans within a single zone. Missing terrain stays blocked. Routes estimate terrain access; buildings, bridges, caves and fences may need manual navigation. The current masks allow swimming.',16,44,'GameFontDisableSmall')
    text:SetSize(556,96);text:SetWordWrap(true)
    S.Sync()
end
