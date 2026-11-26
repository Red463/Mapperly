local _, A = ...
local bag = 'Interface\\AddOns\\Mapperly\\Media\\Toolbar\\Medium\\Services'
local headerHeight, categoryHeight, providerHeight = 24, 43, 36
local refresh, draw

local function label(parent, font, align)
    local text = parent:CreateFontString(nil, 'OVERLAY', font)
    text:SetJustifyH(align or 'LEFT')
    text:SetWordWrap(false)
    return A.Theme.Label(text, font)
end

local function fill(parent, layer, r, g, b, a)
    local texture = parent:CreateTexture(nil, layer)
    texture:SetAllPoints(parent)
    texture:SetColorTexture(r, g, b, a)
    return texture
end

local function leave(button)
    if GameTooltip:IsOwned(button) then GameTooltip:Hide() end
end

local function collapsedSections(panel)
    if panel.query ~= '' then return panel.searchCollapsed end
    return A.db.collapsedServiceSections
end

local function headerButton(panel)
    local b = CreateFrame('Button', nil, panel.content)
    b:SetHeight(headerHeight - 2)
    fill(b, 'BACKGROUND', .11, .11, .12, 1)
    b.leather = b:CreateTexture(nil, 'BORDER')
    b.leather:SetAllPoints(b)
    b.leather:SetAtlas('common-button-list-collapseExpand')
    fill(b, 'HIGHLIGHT', 1, .78, .36, .12)
    b.title = label(b, 'GameFontNormal')
    b.title:SetPoint('LEFT', 9, 0)
    b.title:SetPoint('RIGHT', -56, 0)
    b.count = label(b, 'GameFontNormalSmall', 'RIGHT')
    b.count:SetPoint('RIGHT', -25, 0)
    b.mark = b:CreateTexture(nil, 'ARTWORK')
    b.mark:SetPoint('RIGHT', -7, 0)
    b.mark:SetSize(13, 13)
    b:SetScript('OnMouseDown', function(self) self.pressedKey = self.line.key end)
    b:SetScript('OnClick', function(self)
        if not self.line then return end
        local key, pressed = self.line.key, self.pressedKey
        self.pressedKey = nil
        if pressed and key ~= pressed then return end
        local collapsed = collapsedSections(panel)
        collapsed[key] = not collapsed[key] or nil
        refresh(panel, false, true)
    end)
    return b
end

local function tooltip(row)
    local line = row.line
    if not line then return end
    local p = line.provider
    GameTooltip:SetOwner(row, 'ANCHOR_LEFT')
    GameTooltip:SetText(line.category.label)
    GameTooltip:AddLine(p.subtitle, .95, .90, .78, true)
    GameTooltip:AddLine(('Navigate to %s (%d yd).'):format(p.service.name, math.floor(p.service.distance + .5)), 1, .82, .38, true)
    GameTooltip:Show()
end

local function clickTarget(line)
    return line and (line.key..'/'..line.provider.service.key)
end

local function itemButton(panel)
    local row = CreateFrame('Button', nil, panel.content)
    row.face = fill(row, 'BACKGROUND', .066, .046, .033, .92)
    fill(row, 'HIGHLIGHT', .93, .72, .39, .15)
    local rule = row:CreateTexture(nil, 'BORDER')
    rule:SetPoint('BOTTOMLEFT', 2, 0)
    rule:SetPoint('BOTTOMRIGHT', -2, 0)
    rule:SetHeight(1)
    rule:SetColorTexture(.55, .45, .31, .20)
    row.rim = row:CreateTexture(nil, 'BORDER')
    row.rim:SetPoint('LEFT', 4, 0)
    row.rim:SetColorTexture(.41, .33, .21, .85)
    local well = row:CreateTexture(nil, 'ARTWORK', nil, -1)
    well:SetPoint('TOPLEFT', row.rim, 'TOPLEFT', 1, -1)
    well:SetPoint('BOTTOMRIGHT', row.rim, 'BOTTOMRIGHT', -1, 1)
    well:SetColorTexture(.06, .05, .04, 1)
    row.icon = row:CreateTexture(nil, 'ARTWORK')
    row.icon:SetAllPoints(well)
    row.title = label(row, 'GameFontNormal')
    row.detail = label(row, 'GameFontHighlightSmall')
    row.distance = label(row, 'GameFontHighlightSmall', 'RIGHT')
    row.distance:SetWidth(52)
    row.more = CreateFrame('Button', nil, row)
    row.more:SetPoint('RIGHT', 0, 0)
    row.more:SetSize(22, 36)
    row.more.mark = row.more:CreateTexture(nil, 'ARTWORK')
    row.more.mark:SetPoint('CENTER')
    row.more.mark:SetSize(11, 11)
    fill(row.more, 'HIGHLIGHT', .93, .72, .39, .14)
    row.more:SetScript('OnEnter', function(self)
        if not row.line then return end
        GameTooltip:SetOwner(self, 'ANCHOR_LEFT')
        GameTooltip:SetText((panel.expanded[row.line.key] and 'Hide' or 'Show')..' other locations')
        GameTooltip:Show()
    end)
    row.more:SetScript('OnLeave', leave)
    row.more:SetScript('OnHide', leave)
    row.more:SetScript('OnMouseDown', function(self) self.pressedKey = row.line.key end)
    row.more:SetScript('OnClick', function(self)
        if not row.line then return end
        local key, pressed = row.line.key, self.pressedKey
        self.pressedKey = nil
        if pressed and key ~= pressed then return end
        panel.expanded[key] = not panel.expanded[key] or nil
        refresh(panel, false, true)
    end)
    row:SetScript('OnEnter', tooltip)
    row:SetScript('OnLeave', leave)
    row:SetScript('OnHide', leave)
    row:SetScript('OnMouseDown', function(self) self.pressedKey = clickTarget(self.line) end)
    row:SetScript('OnClick', function(self)
        local line, pressed = self.line, self.pressedKey
        self.pressedKey = nil
        if not line or pressed and pressed ~= clickTarget(line) then return end
        local service = line.provider.service
        local ok, reason = A.NearbyServices.Navigate(service)
        panel.status:SetText(ok and ('Route requested for '..service.name) or reason or 'Unable to navigate to this service.')
    end)
    return row
end

local function paintItem(panel, row, line)
    local category, p = line.category, line.provider
    local alternative = line.kind == 'provider'
    local more = not alternative and #category.providers > 1
    local margin = more and 22 or 6
    local iconSize = alternative and 23 or 31
    row:SetHeight(line.height - 1)
    row.rim:SetSize(iconSize + 2, iconSize + 2)
    row.icon:SetTexture(p.icon or category.icon)
    row.title:ClearAllPoints()
    row.title:SetPoint('TOPLEFT', iconSize + 12, -6)
    row.title:SetPoint('TOPRIGHT', -margin - 56, -6)
    row.title:SetText(alternative and p.service.name or category.label)
    row.detail:ClearAllPoints()
    row.detail:SetPoint('BOTTOMLEFT', iconSize + 12, 5)
    row.detail:SetPoint('BOTTOMRIGHT', -margin, 5)
    row.detail:SetText(alternative and (p.example or p.service.detail) or p.subtitle)
    row.distance:ClearAllPoints()
    row.distance:SetPoint('TOPRIGHT', -margin, -7)
    row.distance:SetText(('%d yd'):format(math.floor(p.service.distance + .5)))
    row.more:SetShown(more)
    if more then row.more.mark:SetAtlas(panel.expanded[line.key] and 'common-button-list-minus' or 'common-button-list-plus') end
    if A.db.theme == 'original' then row.face:SetColorTexture(.062, .065, .072, .98)
    else row.face:SetColorTexture(.066, .046, .033, .92) end
end

-- Every line has an absolute offset. Mixed-height headers and nested locations
-- can scroll normally while the frame pool stays bounded by the visible area.
local function firstAt(lines, offset)
    local lo, hi = 1, #lines + 1
    while lo < hi do
        local mid = math.floor((lo + hi) / 2)
        if lines[mid].offset + lines[mid].height <= offset then lo = mid + 1 else hi = mid end
    end
    return lo
end

draw = function(panel)
    local top, heights = panel.scroll:GetVerticalScroll(), panel.scroll:GetHeight()
    local nh, nr = 0, 0
    for i = firstAt(panel.lines, top), #panel.lines do
        local line = panel.lines[i]
        if line.offset >= top + heights then break end
        local button
        if line.kind == 'header' then
            nh = nh + 1
            button = panel.headers[nh] or headerButton(panel)
            panel.headers[nh] = button
            button.title:SetText(line.group.label)
            button.count:SetText(tostring(#line.group.categories))
            button.mark:SetAtlas(collapsedSections(panel)[line.key] and 'common-button-list-plus' or 'common-button-list-minus')
            button.leather:SetShown(A.db.theme ~= 'original')
        else
            nr = nr + 1
            button = panel.rows[nr] or itemButton(panel)
            panel.rows[nr] = button
            paintItem(panel, button, line)
        end
        button.line = line
        local inset = line.kind == 'provider' and 15 or 0
        if button.offset ~= line.offset or button.inset ~= inset then
            button:ClearAllPoints()
            button:SetPoint('TOPLEFT', panel.content, 'TOPLEFT', inset, -line.offset)
            button:SetPoint('TOPRIGHT', panel.content, 'TOPRIGHT', 0, -line.offset)
            button.offset, button.inset = line.offset, inset
        end
        button:Show()
        if line.provider and GameTooltip:IsOwned(button) then tooltip(button) end
    end
    for i = nh + 1, #panel.headers do panel.headers[i]:Hide(); panel.headers[i].line = nil end
    for i = nr + 1, #panel.rows do panel.rows[i]:Hide(); panel.rows[i].line = nil end
end

local function compose(panel, groups, reset)
    local scroll, lines = panel.scroll, {}
    local top = reset and 0 or scroll:GetVerticalScroll()
    local anchor = not reset and panel.lines[firstAt(panel.lines, top)]
    local offset = 0
    local function add(line, height)
        line.offset, line.height = offset, height
        if anchor and line.key == anchor.key then top = offset + scroll:GetVerticalScroll() - anchor.offset end
        lines[#lines + 1] = line
        offset = offset + height
    end
    for _, group in ipairs(groups) do
        add({kind='header', key=group.key, group=group}, headerHeight)
        if not collapsedSections(panel)[group.key] then
            for _, category in ipairs(group.categories) do
                add({kind='category', key=category.key, category=category, provider=category.providers[1]}, categoryHeight)
                if panel.expanded[category.key] then
                    for i = 2, #category.providers do
                        local p = category.providers[i]
                        add({kind='provider', key=category.key..'/'..p.service.key, category=category, provider=p}, providerHeight)
                    end
                end
            end
        end
    end
    panel.lines = lines
    panel.content:SetHeight(math.max(1, offset))
    local clamped = math.max(0, math.min(top, offset - scroll:GetHeight()))
    if clamped ~= scroll:GetVerticalScroll() then scroll:SetVerticalScroll(clamped) end
    draw(panel)
end

local function location(zone)
    if not zone then return '' end
    local town = GetSubZoneText and GetSubZoneText()
    if not (issecretvalue and issecretvalue(town)) and type(town)=='string' and town ~= '' and town ~= zone then
        return town..', '..zone
    end
    return zone
end

refresh = function(panel, reset, force)
    local groups, zone, reason = A.NearbyServiceGroups.List(panel.query)
    panel.place:SetText(location(zone))
    if not reset and not force and groups == panel.groups and zone == panel.lastZone and reason == panel.lastReason
        and panel.theme == A.db.theme then return end
    reset = reset or zone ~= panel.lastZone
    panel.groups, panel.lastZone, panel.lastReason, panel.theme = groups, zone, reason, A.db.theme
    if reset then panel.status:SetText(('Within %d yd   •   Click a service to navigate'):format(A.NearbyServices.radius)) end
    panel.empty:SetText(reason or (panel.query ~= '' and 'No nearby services match your search.' or 'No known services nearby.'))
    panel.empty:SetShown(#groups == 0)
    compose(panel, groups, reset)
end

function A.CreateNearbyServicesPanel(parent)
    local panel = CreateFrame('Frame', nil, parent, 'BackdropTemplate')
    panel:Hide()
    panel:EnableMouse(true)
    A.Theme.Register(panel, 'card')
    panel.lines, panel.headers, panel.rows = {}, {}, {}
    panel.expanded, panel.searchCollapsed, panel.query = {}, {}, ''
    local search = CreateFrame('EditBox', nil, panel, 'SearchBoxTemplate')
    panel.search = search
    search:SetPoint('TOPLEFT', 12, -9)
    search:SetPoint('TOPRIGHT', -12, -9)
    search:SetHeight(23)
    search:SetMaxLetters(80)
    search:SetAutoFocus(false)
    search.instructionText = 'Search services and goods'
    local instructions = search.Instructions
    if type(instructions)=='table' or type(instructions)=='userdata' then instructions:SetText(search.instructionText) end
    local icon = panel:CreateTexture(nil, 'ARTWORK')
    icon:SetTexture(bag)
    icon:SetPoint('TOPLEFT', 18, -41)
    icon:SetSize(32, 32)
    local title = label(panel, 'GameFontNormalLarge')
    title:SetText('Nearby services')
    title:SetPoint('TOPLEFT', 61, -40)
    panel.place = label(panel, 'GameFontHighlightSmall')
    panel.place:SetPoint('TOPLEFT', 61, -61)
    panel.place:SetPoint('TOPRIGHT', -12, -61)
    panel.status = label(panel, 'GameFontHighlightSmall')
    panel.status:SetPoint('BOTTOMLEFT', 12, 6)
    panel.status:SetPoint('BOTTOMRIGHT', -12, 6)
    panel.status:SetHeight(28)
    panel.status:SetWordWrap(true)
    local scroll = CreateFrame('ScrollFrame', nil, panel, 'UIPanelScrollFrameTemplate')
    panel.scroll = scroll
    scroll:SetPoint('TOPLEFT', panel, 'TOPLEFT', 12, -83)
    scroll:SetPoint('BOTTOMRIGHT', panel, 'BOTTOMRIGHT', -30, 36)
    panel.content = CreateFrame('Frame', nil, scroll)
    panel.content:SetSize(1, 1)
    scroll:SetScrollChild(panel.content)
    panel.empty = label(panel, 'GameFontHighlightSmall', 'CENTER')
    panel.empty:SetPoint('TOPLEFT', scroll, 'TOPLEFT', 6, -12)
    panel.empty:SetPoint('TOPRIGHT', scroll, 'TOPRIGHT', -6, -12)
    panel.empty:SetWordWrap(true)
    scroll:HookScript('OnSizeChanged', function(_, width)
        panel.content:SetWidth(math.max(1, width))
        draw(panel)
    end)
    scroll:HookScript('OnVerticalScroll', function() draw(panel) end)
    search:HookScript('OnTextChanged', function(self)
        panel.query = self:GetText():match('^%s*(.-)%s*$')
        panel.searchCollapsed = {}
        if panel:IsVisible() then refresh(panel, true) end
    end)
    panel:SetScript('OnShow', function(self)
        self.elapsed = 0
        self.content:SetWidth(math.max(1, scroll:GetWidth()))
        refresh(self, true)
    end)
    panel:SetScript('OnHide', function() search:ClearFocus() end)
    panel:SetScript('OnUpdate', function(self, elapsed)
        self.elapsed = self.elapsed + elapsed
        if self.elapsed >= 1 then
            self.elapsed = 0
            refresh(self, false)
        end
    end)
    return panel
end
