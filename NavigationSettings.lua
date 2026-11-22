local _,A=...
local S={};A.NavigationSettings=S
function S.Sync()
    for mode,b in pairs(A.navigationChoices or {}) do b.active=A.db.navigationMode==mode;b:UpdateVisual() end
    if A.journeyRouteCheck then A.journeyRouteCheck:SetChecked(A.db.showJourneyRoute) end
end
function S.Build(parent)
    local U=A.Dialogs
    local mode=U.Card(parent,24,202,592,156)
    U.Label(mode,'Route planning',16,14,'GameFontNormal')
    A.navigationChoices={}
    for i,entry in ipairs({{'terrain','Walking route'},{'direct','Direct bearing'}}) do
        local key=entry[1]
        A.navigationChoices[key]=U.Action(mode,entry[2],16+(i-1)*284,42,268,function()
            A.db.navigationMode=key;S.Sync()
        end)
    end
    local description=U.Label(mode,'Walking routes avoid blocked terrain cells. Direct bearing points at the destination without calculating a path. Changes apply to the next journey.',16,90,'GameFontDisableSmall')
    description:SetSize(556,58);description:SetWordWrap(true)
    local display=U.Card(parent,24,374,592,100)
    U.Label(display,'Route display',16,14,'GameFontNormal')
    local check=CreateFrame('CheckButton',nil,display,'UICheckButtonTemplate');A.journeyRouteCheck=check
    check:SetSize(26,26);check:SetPoint('TOPLEFT',display,'TOPLEFT',14,-42)
    U.Label(display,'Show the walking route on the map',44,48)
    check:SetScript('OnClick',function(self)
        A.db.showJourneyRoute=not not self:GetChecked()
        if A.JourneyView then A.JourneyView.Refresh() end
    end)
    local coverage=U.Card(parent,24,490,592,174)
    U.Label(coverage,'Walking preview coverage',16,14,'GameFontNormal')
    local text=U.Label(coverage,'This preview plans within a single zone. Missing terrain stays blocked. Routes estimate terrain access; buildings, bridges, caves and fences may need manual navigation. The current masks allow swimming.',16,44,'GameFontDisableSmall')
    text:SetSize(556,96);text:SetWordWrap(true)
    S.Sync()
end
