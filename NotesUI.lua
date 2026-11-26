local _, A = ...
local width, height = 333, 344
local U = A.Dialogs

local function mapName(map)
    local info = C_Map.GetMapInfo and C_Map.GetMapInfo(map)
    return info and info.name or 'Map '..tostring(map)
end

local function build()
    local f = U.ToolWindow('MapperlyNoteWindow', 'Map notes', 'Alt-click the map to place a note.', width, height)
    A.noteWindow = f
    f.editor = U.Card(f, 8, 78, 317, 207)
    f.browser = U.Card(f, 8, 78, 317, 226)
    f.place = U.Label(f.editor, '', 10, 7, 'GameFontNormal')
    f.place:SetWidth(267)
    f.place:SetWordWrap(false)
    f.place:SetJustifyH('LEFT')

    U.Label(f.editor, 'Name', 10, 28, 'GameFontNormal')
    U.Label(f.editor, 'Group (optional)', 175, 28, 'GameFontNormal')
    f.nameInput = U.Input(f.editor, 13, 42, 148, 24, 120)
    f.groupInput = U.Input(f.editor, 178, 42, 126, 24, 40)
    U.Label(f.editor, 'Description (optional)', 10, 70, 'GameFontNormal')
    local descriptionCard = U.Card(f.editor, 10, 86, 297, 43)
    local scroll = CreateFrame('ScrollFrame', nil, descriptionCard, 'UIPanelScrollFrameTemplate')
    scroll:SetPoint('TOPLEFT', descriptionCard, 'TOPLEFT', 6, -2)
    scroll:SetSize(264, 39)
    f.descriptionInput = U.Input(scroll, 0, 0, 264, 39, 1000, true)
    scroll:SetScrollChild(f.descriptionInput)
    scroll:EnableMouse(true)
    scroll:SetScript('OnMouseDown', function() f.descriptionInput:SetFocus() end)
    f.descriptionInput:SetScript('OnCursorChanged', function(_, _, y, _, lineHeight)
        local top, cursor = scroll:GetVerticalScroll(), -y
        if cursor < top then
            scroll:SetVerticalScroll(cursor)
        elseif cursor + lineHeight > top + scroll:GetHeight() then
            scroll:SetVerticalScroll(cursor + lineHeight - scroll:GetHeight())
        end
    end)

    local picker = CreateFrame('Frame', nil, f.editor)
    picker:SetSize(317, 75)
    picker:SetPoint('BOTTOMLEFT', f.editor, 'BOTTOMLEFT', 0, 0)
    U.Label(picker, 'Map icon', 10, 0, 'GameFontNormal')
    f.selectedPreview = f.editor:CreateTexture(nil, 'ARTWORK')
    f.selectedPreview:SetSize(20, 20)
    f.selectedPreview:SetPoint('TOPRIGHT', f.editor, 'TOPRIGHT', -10, -4)
    f.iconButtons = {}
    local function selectIcon(key)
        f.selectedIcon = key
        A.SetPinTexture(f.selectedPreview, key, nil, 20)
        for k, button in pairs(f.iconButtons) do
            button.active = k == key
            button:UpdateVisual()
        end
    end
    for i, key in ipairs(A.noteIcons) do
        local x = 15 + ((i-1) % 6)*48
        local y = 16 + math.floor((i-1)/6)*28
        local button = U.Action(picker, '', x, y, 45, function() selectIcon(key) end)
        button:SetHeight(26)
        button.preview = button:CreateTexture(nil, 'ARTWORK')
        button.preview:SetSize(22, 22)
        button.preview:SetPoint('CENTER')
        A.SetPinTexture(button.preview, key, nil, 22)
        A.AttachButtonTooltip(button, 'Select this symbol for your note')
        f.iconButtons[key] = button
    end

    f.error = U.Label(f, '', 0, 0, 'GameFontRedSmall')
    f.error:ClearAllPoints()
    f.error:SetPoint('BOTTOMLEFT', f, 'BOTTOMLEFT', 10, 34)
    f.error:SetSize(313, 25)
    f.error:SetJustifyH('LEFT')
    f.error:SetWordWrap(true)
    local function refresh()
        A.db.filters.notes = true
        if A.Refresh then A.Refresh() end
    end
    local function save()
        local fields = {
            name=f.nameInput:GetText(), group=f.groupInput:GetText(),
            description=f.descriptionInput:GetText(), icon=f.selectedIcon,
        }
        local note
        if f.editing then
            local exists = false
            for _, p in ipairs(A.db.notes) do
                if p == f.editing then exists = true; break end
            end
            if not exists then
                f.error:SetText('This note was removed. Reopen the editor.')
                return
            end
            note = A.UpdateNote(f.editing, fields)
        else
            note = A.AddNote(f.targetMap, f.x, f.y, fields.name, fields)
        end
        if not note then
            f.error:SetText('Enter a name and a valid map location.')
            return
        end
        refresh()
        f:Hide()
    end
    local footer = CreateFrame('Frame', nil, f)
    footer:SetPoint('BOTTOMLEFT', f, 'BOTTOMLEFT', 8, 6)
    footer:SetSize(317, 28)
    f.save = U.Action(footer, 'Save note', 0, 0, 82, save)
    f.navigate = U.Action(footer, 'Navigate', 86, 0, 81, function()
        local name = f.nameInput:GetText()
        if name:match('^%s*$') then name = 'Map note' end
        local ok, reason = A.Navigation.ToPin({map=f.targetMap, x=f.x, y=f.y, name=name})
        if ok then f:Hide() else f.error:SetText(reason) end
    end)
    f.delete = U.Action(footer, 'Delete', 171, 0, 69, function()
        if f.editing then
            A.RemoveNote(f.editing)
            refresh()
            f:Hide()
        end
    end)
    U.Action(footer, 'Cancel', 244, 0, 73, function() f:Hide() end)

    U.Label(f.browser, 'Search names, groups, descriptions or zones', 10, 7, 'GameFontDisableSmall')
    f.search = U.Input(f.browser, 13, 23, 291, 24, 120)
    f.library = U.List(f.browser, 7, 54, 303, 166, {rowHeight=42, rowGap=2})
    f.empty = U.Label(f.browser, '', 13, 65, 'GameFontDisableSmall')
    local function renderNotes()
        local records, query = {}, f.search:GetText():lower()
        for _, p in ipairs(A.db.notes) do
            if A.ValidPin(p) then
                local text = table.concat({p.name, p.group or '', p.description or '', mapName(p.map)}, ' ')
                if text:lower():find(query, 1, true) then records[#records+1] = p end
            end
        end
        table.sort(records, function(a, b)
            local ga, gb = (a.group or ''):lower(), (b.group or ''):lower()
            if ga ~= gb then return ga < gb end
            return a.name:lower() < b.name:lower()
        end)
        f.empty:SetText(#records == 0 and 'No matching notes.' or '')
        f.library:Render(records, function(row, p)
            A.SetPinTexture(row.icon, p.icon or 'notes', nil, 24)
            row.title:SetText(p.name)
            local group = p.group and p.group ~= '' and p.group..'  -  ' or ''
            row.detail:SetText(group..mapName(p.map)..string.format('  %.1f, %.1f', p.x*100, p.y*100))
            if not row.open then
                local buttonX = f.library.width - 58
                row.title:SetWidth(buttonX - 42)
                row.open = U.Action(row, 'Edit', buttonX, 1, 54, function()
                    local n = row.record
                    A.ShowNote(n.map, n.x, n.y, n, A.drawerWindow == f and 'notes' or nil)
                end)
                row.open:SetHeight(19)
            end
        end)
    end

    local function select(page)
        local edit = page == 'edit'
        U.Tabs(f.tabs, page)
        f.editor:SetShown(edit)
        f.browser:SetShown(not edit)
        f.error:SetShown(edit)
        f.save:SetShown(edit)
        f.navigate:SetShown(edit)
        f.delete:SetShown(edit and f.editing ~= nil)
        if not edit then renderNotes() end
    end
    f.tabs = {}
    f.tabs.edit = U.Action(f, 'Edit note', 8, 46, 156, function() select('edit') end, 'tab')
    f.browserTab = U.Action(f, 'My notes', 169, 46, 156, function() select('browser') end, 'tab')
    f.tabs.browser = f.browserTab
    f.search:SetScript('OnTextChanged', renderNotes)
    for _, input in ipairs({f.nameInput, f.groupInput, f.descriptionInput, f.search}) do
        input:SetScript('OnEscapePressed', function() f:Hide() end)
    end
    f.nameInput:SetScript('OnEnterPressed', save)
    f.groupInput:SetScript('OnEnterPressed', save)
    f.nameInput:SetScript('OnTabPressed', function() f.groupInput:SetFocus() end)
    f.groupInput:SetScript('OnTabPressed', function() f.descriptionInput:SetFocus() end)
    f.SelectPage, f.SelectIcon = select, selectIcon

    -- Taller map views put the extra space into the note text and library.
    function f:FitToolHeight(available)
        local extra = math.max(0, available - height)
        self.editor:SetHeight(207 + extra)
        descriptionCard:SetHeight(43 + extra)
        scroll:SetHeight(39 + extra)
        self.browser:SetHeight(226 + extra)
        self.library.frame:SetHeight(166 + extra)
    end
    return f
end

function A.ShowNote(map, x, y, note, drawerKey)
    local f = A.noteWindow or build()
    f.targetMap, f.x, f.y, f.editing = map, x, y, note
    f.tabs.edit:SetEnabled(true)
    f.place:SetText(string.format('%s  -  %.1f, %.1f', mapName(map), x*100, y*100))
    f.nameInput:SetText(note and note.name or '')
    f.groupInput:SetText(note and note.group or '')
    f.descriptionInput:SetText(note and note.description or '')
    f.SelectIcon(note and note.icon or 'note_poi')
    f.error:SetText('')
    f.SelectPage('edit')
    U.Show(f, drawerKey)
    if f:IsVisible() then f.nameInput:SetFocus() end
end

function A.ShowNoteBrowser()
    local f = A.noteWindow or build()
    f.tabs.edit:SetEnabled(false)
    f.SelectPage('browser')
    U.Show(f, 'notes')
end
