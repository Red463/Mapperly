local _,A=...
local UI={};A.QuestNavigationUI=UI
local function title(quest)
    return (quest.level and quest.level>0 and '['..quest.level..'] ' or '')..quest.title
end
local function tooltip(row,heading,detail)
    row:EnableMouse(true);row.questHeading=heading;row.questDetail=detail
    if row.questTooltip then return end
    row.questTooltip=true
    row:SetScript('OnEnter',function(self)
        GameTooltip:SetOwner(self,'ANCHOR_RIGHT');GameTooltip:SetText(self.questHeading)
        GameTooltip:AddLine(self.questDetail,1,.82,0,true);GameTooltip:Show()
    end)
    row:SetScript('OnLeave',function() GameTooltip:Hide() end)
end
function UI.Build(f)
    local U=A.Dialogs
    local page=CreateFrame('Frame',nil,f);page:SetAllPoints(f);page:Hide();f.questPage=page
    local card=U.Card(page,24,132,572,344)
    local u={scope='active'};f.questUI=u
    u.searchFrame=CreateFrame('Frame',nil,card);u.searchFrame:SetAllPoints(card)
    U.Label(u.searchFrame,'Search quests',16,18,'GameFontNormal')
    local function scope(value) u.scope=value;u.selectedID=nil;UI.searchWait=nil;f.status:SetText('');UI.Refresh(f) end
    u.activeScope=U.Action(u.searchFrame,'Active',292,8,112,function() scope('active') end,'choice')
    u.catalogScope=U.Action(u.searchFrame,'Find quests',412,8,132,function() scope('catalog') end,'choice')
    u.search=U.Input(u.searchFrame,20,44,532,28,120)
    u.questList=U.List(u.searchFrame,10,92,548,230)
    u.locationsFrame=CreateFrame('Frame',nil,card);u.locationsFrame:SetAllPoints(card);u.locationsFrame:Hide()
    u.back=U.Action(u.locationsFrame,'Back',16,12,80,function() u.selectedID=nil;UI.Refresh(f) end)
    u.heading=U.Label(u.locationsFrame,'',112,18,'GameFontNormal');u.heading:SetSize(426,20);u.heading:SetWordWrap(false)
    u.help=U.Label(u.locationsFrame,'',16,50,'GameFontDisableSmall');u.help:SetSize(536,30);u.help:SetWordWrap(true)
    u.locationList=U.List(u.locationsFrame,10,88,548,238)
    u.empty=U.Label(card,'',20,100,'GameFontDisableSmall');u.empty:SetSize(520,100);u.empty:SetWordWrap(true)
    u.search:SetScript('OnTextChanged',function()
        u.selectedID=nil;f.status:SetText('')
        if u.scope=='catalog' then UI.searchWait=0;UI.dirty=true else UI.Refresh(f) end
    end)
    u.search:SetScript('OnEnterPressed',function() UI.searchWait=nil;UI.Refresh(f) end)
    u.search:SetScript('OnEscapePressed',function() f:Hide() end)
    page:SetScript('OnShow',function() UI.Refresh(f) end)
    function f.SelectQuests() u.selectedID=nil;UI.Refresh(f);u.search:SetFocus() end
    return page
end
local function act(f,selected,preview)
    local pin,why=A.QuestNavigation.RouteTarget(selected)
    if not pin then f.status:SetText(why);return end
    local ok,reason
    if preview then
        ok,reason=A.JourneyView.Preview(pin)
        if ok then f.status:SetText(pin.approachDistance and string.format('Planning to a walkable approach, %.0f yd from the exact quest location.',pin.approachDistance) or pin.catalog and 'Planning route to the recorded quest starter.' or 'Planning quest route...') end
    else
        ok,reason=A.Navigation.ToPin(pin)
        if ok then
            if pin.approachDistance and A.Print then A.Print(string.format('Routing to a walkable approach, %.0f yd from %s. The final approach is manual.',pin.approachDistance,pin.label)) end
            if pin.catalog and pin.availabilityStatus=='unknown' and A.Print then A.Print('Quest availability is unconfirmed. Routing to the recorded starter; check pickup requirements in-game.') end
            f:Hide()
        end
    end
    if not ok then f.status:SetText(reason or 'Unable to plan this quest destination.') end
end
function UI.Refresh(f,keepScroll)
    f=f or A.navigationWindow
    if not f or not f.questUI then return end
    local U,Q,u=A.Dialogs,A.QuestNavigation,f.questUI
    u.activeScope.active=u.scope=='active';u.activeScope:UpdateVisual()
    u.catalogScope.active=u.scope=='catalog';u.catalogScope:UpdateVisual()
    local quest
    if u.selectedID then
        if u.scope=='catalog' then quest=A.QuestCatalog.Find(u.selectedID) else quest=Q.Find(u.selectedID) end
    end
    if u.selectedID and not quest then u.selectedID=nil;f.status:SetText('This quest is no longer in your active quest log.') end
    u.searchFrame:SetShown(not quest);u.locationsFrame:SetShown(not not quest)
    local list=quest and u.locationList or u.questList
    local scroll=keepScroll and list.frame:GetVerticalScroll() or 0
    if quest then
        u.heading:SetText(title(quest))
        local records,why
        if u.scope=='catalog' then records,why=A.QuestCatalog.Locations(quest.id) else records,why=Q.Locations(quest.id) end
        local uncertain=false
        for _,pin in ipairs(records) do if pin.progressUnknown then uncertain=true;break end end
        u.help:SetText(quest.catalog and quest.reason or uncertain and 'Game pins and snapshot locations. Some snapshot objectives may already be complete.' or 'Choose an objective, turn-in location or game travel waypoint.')
        u.empty:SetText(#records==0 and why or '');u.empty:SetShown(#records==0)
        list:Render(records,function(row,p)
            A.SetPinTexture(row.icon,'quest',nil,24);row.title:SetText(p.label);row.title:SetWidth(276)
            local source=p.source=='native' and 'Game' or 'Snapshot'
            row.detail:SetText(string.format('%s  |  %.1f, %.1f  |  %s',p.zone,p.x*100,p.y*100,source))
            tooltip(row,p.label,p.questTitle..'\n'..p.zone..'\n'..(p.source=='native' and 'Current game quest data.' or 'Bundled Forever database snapshot; may be incomplete or outdated.')..(p.progressUnknown and '\nIndividual objective progress is unavailable; check your quest log.' or '')..(p.catalog and '\n'..p.availabilityReason or '')..'\nIf the exact point is blocked, smart routing uses permitted ground within 30 yd and labels it as an approach.')
            if not row.preview then
                row.preview=U.Action(row,'Preview',328,5,88,function() act(f,row.record,true) end)
                row.go=U.Action(row,'Go',424,5,76,function() act(f,row.record,false) end)
            end
            row.preview:SetEnabled(A.JourneyView~=nil and p.available~=false);row.go:SetEnabled(p.available~=false)
        end)
    else
        local records,why
        if u.scope=='catalog' then records,why=A.QuestCatalog.Search(u.search:GetText()) else records,why=Q.Search(u.search:GetText()) end
        u.empty:SetText(why or (#records==0 and 'No active quests match your search.' or ''));u.empty:SetShown(#records==0)
        if #records>0 and why then f.status:SetText(why) end
        list:Render(records,function(row,p)
            A.SetPinTexture(row.icon,'quest',nil,24);row.title:SetText(title(p));row.title:SetWidth(350)
            local status=p.catalog and (p.status=='possible' and 'Possible pickup' or p.status=='unavailable' and 'Unavailable' or 'Availability unconfirmed')
            row.detail:SetText(status and status..'  |  Quest '..p.id or p.failed and 'Failed quest' or p.complete and 'Ready to turn in' or 'In progress')
            tooltip(row,p.title,'Quest '..p.id..'\n'..(p.catalog and p.reason..'\nSnapshot data may be incomplete or outdated.' or p.complete and 'Ready to turn in.' or 'Choose Locations to view known destinations.'))
            if not row.locations then row.locations=U.Action(row,'Locations',400,5,100,function()
                u.selectedID=row.record.id;f.status:SetText('');UI.Refresh(f)
            end) end
        end)
    end
    if keepScroll then list.frame:SetVerticalScroll(math.max(0,math.min(scroll,list.child:GetHeight()-list.frame:GetHeight()))) end
end
UI.driver=CreateFrame('Frame',nil,UIParent);UI.driver:SetSize(1,1);UI.driver:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);UI.driver:EnableMouse(false)
for _,event in ipairs({'QUEST_LOG_UPDATE','QUEST_ACCEPTED','QUEST_REMOVED','QUEST_WATCH_UPDATE','QUEST_POI_UPDATE','QUEST_DATA_LOAD_RESULT','QUEST_TURNED_IN','PLAYER_LEVEL_UP','UPDATE_FACTION','SKILL_LINES_CHANGED','PLAYER_ENTERING_WORLD'}) do pcall(UI.driver.RegisterEvent,UI.driver,event) end
UI.driver:SetScript('OnEvent',function() UI.dirty=true end)
local elapsed=0
UI.driver:SetScript('OnUpdate',function(_,dt)
    if UI.searchWait then UI.searchWait=UI.searchWait+dt;if UI.searchWait<.15 then return end;UI.searchWait=nil end
    elapsed=elapsed+dt;if elapsed<.2 then return end;elapsed=0
    local f=A.navigationWindow
    if UI.dirty and f and f:IsShown() and f.questPage:IsShown() then UI.dirty=nil;UI.Refresh(f,true) end
end)
