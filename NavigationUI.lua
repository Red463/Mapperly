local _,A=...
local function zoneName(map)
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(map);return info and info.name or 'Map '..tostring(map)
end
local function read(f)
    local x,y=A.Navigation.Parse(f.xInput:GetText(),f.yInput:GetText())
    if not x then f.error:SetText(y);return end
    local p={map=f.targetMap,x=x,y=y,name=f.nameInput:GetText()}
    if p.name:match('^%s*$') then p.name=zoneName(p.map) end
    return p
end
local function populate(f,p,savedRecord)
    f.savedRecord=savedRecord
    f.targetMap=p.map;f.zone:SetText(zoneName(p.map));f.nameInput:SetText(p.name or '')
    f.xInput:SetText(p.x and string.format('%.15g',p.x*100) or '')
    f.yInput:SetText(p.y and string.format('%.15g',p.y*100) or '')
    f.error:SetText('')
end
local function build()
    local U=A.Dialogs
    local f=U.Window('MapperlyNavigationWindow','Destinations','Set destinations, find quests and navigate to nearby services.',620,548);A.navigationWindow=f
    f.entryPage=CreateFrame('Frame',nil,f);f.entryPage:SetAllPoints(f)
    f.libraryPage=U.Card(f,24,132,572,344);f.libraryPage:Hide()
    if A.QuestNavigationUI then A.QuestNavigationUI.Build(f) end
    if A.NearestServicesUI then A.NearestServicesUI.Build(f) end
    local card=U.Card(f.entryPage,24,132,572,306)
    f.zone=U.Label(card,'',16,16,'GameFontNormal');f.zone:SetWidth(540);f.zone:SetWordWrap(false)
    U.Label(card,'Destination name (optional)',16,48,'GameFontNormal');f.nameInput=U.Input(card,20,70,532,28,120)
    U.Label(card,'X coordinate',16,112,'GameFontNormal');U.Label(card,'Y coordinate',294,112,'GameFontNormal')
    f.xInput=U.Input(card,20,134,248,28,16);f.yInput=U.Input(card,298,134,248,28,16)
    U.Label(card,'Use coordinates from 0 to 100. Decimals are supported.',16,178,'GameFontDisableSmall')
    U.Label(card,'Tip: Alt-right-click the map or a marker to navigate instantly.',16,204,'GameFontDisableSmall')
    f.error=U.Label(card,'',16,230,'GameFontRedSmall');f.error:SetSize(536,30);f.error:SetWordWrap(true)
    local function start()
        local p=read(f);if not p then return end
        local ok,reason=A.Navigation.ToPin(p)
        if ok then f:Hide() else f.error:SetText(reason or 'Unable to navigate here.') end
    end
    f.start=U.Action(f.entryPage,'Start',40,398,100,start)
    if A.Theme then A.Theme.ButtonRole(f.start,'primary') end
    f.save=U.Action(f.entryPage,'Save',150,398,100,function()
        local p=read(f);if not p then return end
        local record
        if f.savedRecord then record=A.Destinations.Update(f.savedRecord,p) else record=A.Destinations.Save(p) end
        if record then
            f.savedRecord=record;f.error:SetText('');f.status:SetText('Destination saved.')
        else f.error:SetText('This destination was removed. Reopen it from Saved.') end
    end)
    if A.JourneyView then
        f.preview=U.Action(f.entryPage,'Preview route',260,398,132,function()
            local p=read(f);if not p then return end
            f.status:SetText('Planning route...')
            local ok,reason=A.JourneyView.Preview(p)
            if not ok then f.status:SetText('');f.error:SetText(reason or 'Unable to preview route.') end
        end)
        f.journey=U.Action(f.entryPage,'Active journey',404,398,152,A.JourneyView.OpenCurrent)
    end
    f.stop=U.Action(f,'Stop',486,494,110,function() A.Navigation.Stop();f.status:SetText('Navigation stopped.') end)
    f.status=U.Label(f,'',24,494,'GameFontDisableSmall');f.status:SetSize(440,36);f.status:SetWordWrap(true)
    f.library=U.List(f.libraryPage,10,10,548,300)
    f.empty=U.Label(f.libraryPage,'',20,30,'GameFontDisableSmall')
    local function select(page)
        if f.page=='services' and page~='services' and A.NearestServicesUI then A.NearestServicesUI.Cancel(f) end
        f.page=page;U.Tabs(f.tabs,page);f.status:SetText('')
        if f.questPage then f.questPage:Hide() end
        if f.servicePage then f.servicePage:Hide() end
        if page=='services' then f.entryPage:Hide();f.libraryPage:Hide();f.clear:Hide();f.servicePage:Show();return end
        if page=='quests' then f.entryPage:Hide();f.libraryPage:Hide();f.clear:Hide();f.questPage:Show();f.SelectQuests();return end
        if page=='entry' then f.entryPage:Show();f.libraryPage:Hide();f.clear:Hide();return end
        f.entryPage:Hide();f.libraryPage:Show();f.clear:SetShown(page=='recent')
        local records=page=='saved' and A.db.savedDestinations or A.db.destinationHistory
        f.empty:SetText(#records==0 and (page=='saved' and 'No saved destinations. Save one from the Coordinates tab.' or 'Your last 20 destinations will appear here.') or '')
        f.library:Render(records,function(row,p)
            A.SetPinTexture(row.icon,'navigation',nil,24);row.title:SetText(p.name)
            row.detail:SetText(string.format('%s  -  %.1f, %.1f',zoneName(p.map),p.x*100,p.y*100))
            if not row.open then
                row.open=U.Action(row,'Edit',270,5,66,function() populate(f,row.record,f.page=='saved' and row.record or nil);select('entry') end)
                row.go=U.Action(row,'Go',342,5,66,function()
                    local ok,reason=A.Navigation.ToPin(row.record)
                    if ok then f:Hide() else f.status:SetText(reason) end
                end)
                row.remove=U.Action(row,'Remove',414,5,94,function()
                    if f.page=='saved' then A.Destinations.Remove(row.record) else A.Destinations.Save(row.record) end
                    select(f.page)
                end)
            end
            row.remove:SetText(page=='saved' and 'Remove' or 'Save')
        end)
    end
    f.tabs={}
    f.tabs.entry=U.Action(f,'Coordinates',24,88,108,function() select('entry') end,'tab')
    f.savedTab=U.Action(f,'Saved',140,88,108,function() select('saved') end,'tab');f.tabs.saved=f.savedTab
    f.recentTab=U.Action(f,'Recent',256,88,108,function() select('recent') end,'tab');f.tabs.recent=f.recentTab
    if A.QuestNavigationUI then f.tabs.quests=U.Action(f,'Quests',372,88,108,function() select('quests') end,'tab') end
    if A.NearestServicesUI then f.tabs.services=U.Action(f,'Services',488,88,108,function() select('services') end,'tab') end
    f.clear=U.Action(f,'Clear history',24,446,130,function() A.Destinations.ClearHistory();select('recent') end)
    for _,e in ipairs({f.nameInput,f.xInput,f.yInput}) do e:SetScript('OnEscapePressed',function() f:Hide() end);e:SetScript('OnEnterPressed',start) end
    f.nameInput:SetScript('OnTabPressed',function() f.xInput:SetFocus() end)
    f.xInput:SetScript('OnTabPressed',function() f.yInput:SetFocus() end)
    f.yInput:SetScript('OnTabPressed',function() f.nameInput:SetFocus() end)
    f.SelectPage=select;return f
end
function A.ShowNavigationInput(map)
    map=map or (A.map and A.map:GetMapID())
    if not map then A.Print('Open the destination map first.');return end
    local f=A.navigationWindow or build();local target=A.Navigation.target
    populate(f,target and target.map==map and target or {map=map})
    f.SelectPage('entry');A.Dialogs.Show(f);f.xInput:SetFocus()
end
