local _,A=...
local M={};A.QuestContextMenu=M
local function validID(id)
    return not (issecretvalue and issecretvalue(id)) and type(id)=='number' and id>0 and id<math.huge and id%1==0
end
local function questID(owner)
    if type(owner)~='table' and type(owner)~='userdata' then return end
    if type(owner.IsForbidden)=='function' then local ok,v=pcall(owner.IsForbidden,owner);if not ok or v then return end end
    local id=owner.questID
    if not validID(id) and type(owner.GetQuestID)=='function' then local ok,v=pcall(owner.GetQuestID,owner);if ok then id=v end end
    if validID(id) then return id end
end
local function tip(entry,heading,detail)
    if type(entry.SetTooltip)=='function' then entry:SetTooltip(function(tooltip)
        tooltip:SetText(heading);tooltip:AddLine(detail,1,.82,0,true)
    end) end
end
function M.Navigate(selected)
    local pin,why=A.QuestNavigation.RouteTarget(selected)
    if not pin then if A.Print then A.Print(why) end;return end
    local ok,reason=A.Navigation.ToPin(pin)
    if ok and pin.approachDistance and A.Print then A.Print(string.format('Routing to a walkable approach, %.0f yd from %s. The final approach is manual.',pin.approachDistance,pin.label)) end
    return ok,reason
end
function M.Populate(owner,root)
    if not A.db or not A.QuestNavigation or not root or type(root.CreateButton)~='function' then return end
    local id=questID(owner)
    -- Native user-waypoint menus share this tag, but have no quest identity.
    if not id then return end
    local locations,why=A.QuestNavigation.Locations(id)
    if #locations==0 then
        local entry=root:CreateButton('Navigate to');entry:SetEnabled(false)
        tip(entry,'Mapperly navigation',why or 'No verified quest location is available.')
        return
    end
    local function annotate(entry,p)
        tip(entry,p.label,string.format('%s\n%s: %.1f, %.1f\n%s\nSmart routing may use a nearby walkable approach.',p.questTitle,p.zone,p.x*100,p.y*100,p.source=='native' and 'Current game quest data.' or 'Bundled Forever snapshot; location may be incomplete or outdated.'))
    end
    if #locations==1 then
        local selected=locations[1]
        annotate(root:CreateButton('Navigate to',function() M.Navigate(selected) end),selected)
    else
        local entry=root:CreateButton('Navigate to')
        if type(entry.SetScrollMode)=='function' then entry:SetScrollMode(300) end
        for _,p in ipairs(locations) do
            local selected=p
            local label=string.format('%s - %s (%.1f, %.1f)',p.label,p.zone,p.x*100,p.y*100)
            annotate(entry:CreateButton(label,function() M.Navigate(selected) end),p)
        end
    end
end
function M.Install()
    if M.installed then return true end
    if not Menu or type(Menu.ModifyMenu)~='function' then return false end
    M.handle=Menu.ModifyMenu('MENU_QUEST_MAP_LOG_TITLE',M.Populate);M.installed=true
    return true
end
M.driver=CreateFrame('Frame',nil,UIParent)
M.driver:RegisterEvent('ADDON_LOADED');M.driver:RegisterEvent('PLAYER_LOGIN')
M.driver:SetScript('OnEvent',function() M.Install() end)
M.Install()
