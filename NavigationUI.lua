local _, A = ...
local width, preferredHeight = 333, 340
local pageTop, footerHeight = 83, 44
local cardWidth = width - 16

local function zoneName(map)
    local info = C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    return info and info.name or 'Map '..tostring(map)
end

local function read(f)
    local x, y = A.Navigation.Parse(f.xInput:GetText(), f.yInput:GetText())
    if not x then f.error:SetText(y); return end
    local p = {map=f.targetMap, x=x, y=y, name=f.nameInput:GetText()}
    if p.name:match('^%s*$') then p.name = zoneName(p.map) end
    return p
end

local function populate(f, p, savedRecord)
    f.savedRecord = savedRecord
    f.targetMap = p.map
    f.zone:SetText(zoneName(p.map))
    f.nameInput:SetText(p.name or '')
    f.xInput:SetText(p.x and string.format('%.15g', p.x * 100) or '')
    f.yInput:SetText(p.y and string.format('%.15g', p.y * 100) or '')
    f.error:SetText('')
end

local function build()
    local U = A.Dialogs
    local f = U.ToolWindow('MapperlyNavigationWindow', 'Destinations', 'Alt-right-click a map point or marker to go.', width, preferredHeight)
    A.navigationWindow = f

    local initialBodyHeight = preferredHeight - pageTop - footerHeight
    local entry = U.Card(f, 8, pageTop, cardWidth, initialBodyHeight)
    f.entryPage = entry
    f.zone = U.Label(entry, '', 10, 7, 'GameFontNormal')
    f.zone:SetWidth(cardWidth - 20)
    f.zone:SetWordWrap(false)
    f.zone:SetJustifyH('LEFT')
    U.Label(entry, 'Name (optional)', 10, 28, 'GameFontNormal')
    f.nameInput = U.Input(entry, 14, 44, 291, 24, 120)
    U.Label(entry, 'X (0-100)', 10, 76, 'GameFontNormal')
    U.Label(entry, 'Y (0-100)', 163, 76, 'GameFontNormal')
    f.xInput = U.Input(entry, 14, 92, 138, 24, 16)
    f.yInput = U.Input(entry, 167, 92, 138, 24, 16)
    f.error = U.Label(entry, '', 10, 181, 'GameFontRedSmall')
    f.error:SetSize(cardWidth - 20, 29)
    f.error:SetWordWrap(true)
    f.error:SetJustifyH('LEFT')

    local function start()
        local p = read(f)
        if not p then return end
        local ok, reason = A.Navigation.ToPin(p)
        if ok then f:Hide() else f.error:SetText(reason or 'Unable to navigate here.') end
    end
    f.start = U.Action(entry, 'Start', 10, 120, 145, start)
    f.save = U.Action(entry, 'Save', 161, 120, 145, function()
        local p = read(f)
        if not p then return end
        local record
        if f.savedRecord then record = A.Destinations.Update(f.savedRecord, p) else record = A.Destinations.Save(p) end
        if record then
            f.savedRecord = record
            f.error:SetText('')
            f.status:SetText('Destination saved.')
        else
            f.error:SetText('This destination was removed. Reopen it from Saved.')
        end
    end)
    if A.JourneyView then
        f.preview = U.Action(entry, 'Preview route', 10, 151, 145, function()
            local p = read(f)
            if not p then return end
            f.status:SetText('Planning route...')
            local ok, reason = A.JourneyView.Preview(p)
            if not ok then f.status:SetText(''); f.error:SetText(reason or 'Unable to preview route.') end
        end)
        f.journey = U.Action(entry, 'Active journey', 161, 151, 145, A.JourneyView.OpenCurrent)
    end

    f.stop = U.Action(f, 'Stop', 0, 0, 66, function()
        A.Navigation.Stop()
        f.status:SetText('Navigation stopped.')
    end)
    f.stop:ClearAllPoints()
    f.stop:SetPoint('BOTTOMRIGHT', f, 'BOTTOMRIGHT', -8, 8)
    f.status = U.Label(f, '', 0, 0, 'GameFontDisableSmall')
    f.status:ClearAllPoints()
    f.status:SetPoint('BOTTOMLEFT', f, 'BOTTOMLEFT', 10, 4)
    f.status:SetSize(242, 36)
    f.status:SetWordWrap(true)
    f.status:SetJustifyH('LEFT')

    f.libraryPage = U.Card(f, 8, pageTop, cardWidth, initialBodyHeight)
    f.libraryPage:Hide()
    f.library = U.List(f.libraryPage, 5, 4, cardWidth - 10, initialBodyHeight - 8, {rowHeight=64, rowGap=3})
    f.empty = U.Label(f.libraryPage, '', 12, 12, 'GameFontDisableSmall')
    f.empty:SetWidth(cardWidth - 42)
    f.empty:SetWordWrap(true)
    f.empty:SetJustifyH('LEFT')
    if A.QuestNavigationUI then A.QuestNavigationUI.Build(f, pageTop, cardWidth, initialBodyHeight) end

    function f:FitToolHeight(height)
        local bodyHeight = height - pageTop - footerHeight
        self.libraryPage:SetHeight(bodyHeight)
        self.library.frame:SetHeight(bodyHeight - (self.page == 'recent' and 38 or 8))
        if self.questUI then self.questUI.fit(bodyHeight) end
    end

    local function select(page)
        f.page = page
        U.Tabs(f.tabs, page)
        f.status:SetText('')
        entry:SetShown(page == 'entry')
        f.libraryPage:SetShown(page == 'saved' or page == 'recent')
        f.clear:SetShown(page == 'recent')
        f:FitToolHeight(f:GetHeight())
        if f.questPage then f.questPage:SetShown(page == 'quests') end
        if page == 'quests' then f.SelectQuests(); return end
        if page == 'entry' then return end
        local records = page == 'saved' and A.db.savedDestinations or A.db.destinationHistory
        f.empty:SetText(page == 'saved' and 'Save a destination from the Coords tab.' or 'Your last 20 destinations will appear here.')
        f.empty:SetShown(#records == 0)
        f.library:Render(records, function(row, p)
            A.SetPinTexture(row.icon, 'navigation', nil, 24)
            row.title:SetText(p.name)
            row.title:SetWidth(f.library.width - 44)
            row.detail:SetText(string.format('%s  -  %.1f, %.1f', zoneName(p.map), p.x * 100, p.y * 100))
            row.detail:SetWidth(f.library.width - 44)
            if not row.open then
                row.open = U.Action(row, 'Edit', 5, 33, 86, function()
                    populate(f, row.record, f.page == 'saved' and row.record or nil)
                    select('entry')
                end)
                row.go = U.Action(row, 'Go', 96, 33, 76, function()
                    local ok, reason = A.Navigation.ToPin(row.record)
                    if ok then f:Hide() else f.status:SetText(reason) end
                end)
                row.remove = U.Action(row, 'Remove', 177, 33, 96, function()
                    if f.page == 'saved' then A.Destinations.Remove(row.record) else A.Destinations.Save(row.record) end
                    select(f.page)
                end)
                row:EnableMouse(true)
                row:SetScript('OnEnter', function(self)
                    GameTooltip:SetOwner(self, 'ANCHOR_LEFT')
                    GameTooltip:SetText(self.record.name)
                    GameTooltip:AddLine(self.detail:GetText(), 1, .82, 0, true)
                    GameTooltip:Show()
                end)
                row:SetScript('OnLeave', function() GameTooltip:Hide() end)
            end
            row.remove:SetText(page == 'saved' and 'Remove' or 'Save')
        end)
    end
    f.tabs = {}
    f.tabs.entry = U.Action(f, 'Coords', 8, 49, 76, function() select('entry') end, 'tab')
    f.savedTab = U.Action(f, 'Saved', 88, 49, 76, function() select('saved') end, 'tab')
    f.tabs.saved = f.savedTab
    f.recentTab = U.Action(f, 'Recent', 168, 49, 76, function() select('recent') end, 'tab')
    f.tabs.recent = f.recentTab
    if A.QuestNavigationUI then f.tabs.quests = U.Action(f, 'Quests', 248, 49, 77, function() select('quests') end, 'tab') end
    f.clear = U.Action(f.libraryPage, 'Clear history', 0, 0, 112, function()
        A.Destinations.ClearHistory()
        select('recent')
    end)
    f.clear:ClearAllPoints()
    f.clear:SetPoint('BOTTOMLEFT', f.libraryPage, 'BOTTOMLEFT', 5, 4)
    for _, e in ipairs({f.nameInput, f.xInput, f.yInput}) do
        e:SetScript('OnEscapePressed', function() f:Hide() end)
        e:SetScript('OnEnterPressed', start)
    end
    f.nameInput:SetScript('OnTabPressed', function() f.xInput:SetFocus() end)
    f.xInput:SetScript('OnTabPressed', function() f.yInput:SetFocus() end)
    f.yInput:SetScript('OnTabPressed', function() f.nameInput:SetFocus() end)
    f.SelectPage = select
    return f
end

function A.ShowNavigationInput(map, drawerKey)
    map = map or (A.map and A.map:GetMapID())
    if not map then A.Print('Open the destination map first.'); return end
    local f = A.navigationWindow or build()
    local target = A.Navigation.target
    populate(f, target and target.map == map and target or {map=map})
    f.SelectPage('entry')
    A.Dialogs.Show(f, drawerKey)
    if f:IsVisible() then f.xInput:SetFocus() end
end
