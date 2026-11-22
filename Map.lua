local _,A=...
local button=A.CreateIconButton
function A.UpdateCoordinates()
    if not A.coordinateText then return end
    if not A.db.coordinates then A.coordinateText:SetText('');return end
    local id=A.map:GetMapID()
    local pos=id and C_Map.GetPlayerMapPosition(id,'player')
    local text='Player: --, --'
    if pos then local x,y=pos:GetXY();text=string.format('Player: %.1f, %.1f',x*100,y*100) end
    local x,y=A.map:GetNormalizedCursorPosition()
    local cursor=x and y and x>=0 and x<=1 and y>=0 and y<=1 and string.format('Cursor: %.1f, %.1f',x*100,y*100) or 'Cursor: --, --'
    -- FontStrings escape a literal pipe as ||.
    A.coordinateText:SetText(text..'  ||  '..cursor)
end
function A.ApplyLayout(restorePosition)
    if A.applying then return end
    if A.dragging then A.dragLayoutPending=true;return end
    if InCombatLockdown() then A.layoutPending=true;return end
    A.layoutPending=nil
    local f=A.map
    -- Preserve the actual position before native sizing or theme changes touch it.
    -- Opening/resolution changes restore the saved point instead of sampling a
    -- temporary anchor supplied by Blizzard's panel manager.
    if not restorePosition and A.layoutReady and A.layoutCompact==A.db.compact and f:IsShown() then A.SaveMapPosition() end
    A.applying=true
    -- Repeated Minimize calls invoke UpdateUIPanelPositions/RestoreUIPanelArea,
    -- letting Blizzard's panel layout move a window that Mapperly already owns.
    if f.Minimize and (not A.nativeWindowed or f.IsMaximized and f:IsMaximized()) then f:Minimize() end
    A.nativeWindowed=true
    A.LayoutShell()
    f:SetMovable(not A.db.locked)
    A.PositionMap()
    A.layoutReady=true;A.layoutCompact=A.db.compact
    A.UpdateButtonStates()
    A.applying=nil
    A.UpdateOpacity()
    A.QueueViewportFit()
end
function A.Refresh()
    if not A.map or not A.db or not A.map:IsShown() then return end
    if A.LoadServices then A.LoadServices() end
    A.RefreshPins();A.RefreshReveal()
    if A.JourneyView then A.JourneyView.Refresh() end
    A.AttachZoneLevels()
    A.UpdateNavigation()
    A.UpdateButtonStates()
end
local function current()
    local id=C_Map and C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit('player')
    if not id then return end
    A.map:SetMapID(id)
    if A.map.ResetZoom then A.map:ResetZoom(true) end
    if A.map.EnumeratePinsByTemplate then
        for pin in A.map:EnumeratePinsByTemplate('GroupMembersPinTemplate') do
            if pin.StopPlayerPing then pin:StopPlayerPing() end
            if pin.UpdatePlayerPins then pin:UpdatePlayerPins() end
            if pin.StartPlayerPing then pin:StartPlayerPing(2,.25) end
        end
    end
end
local labels={mail='Mailboxes',inn='Inns',dungeon='Dungeon entrances',flight='Flight masters',transport='Boats and zeppelins',portal='Portals',border='Zone exits',notes='Custom notes'}
local function menuEntry(text,fn,checked,tip)
    local info=UIDropDownMenu_CreateInfo();info.text=text;info.func=fn;info.checked=checked
    info.isNotRadio=true;info.keepShownOnClick=true;info.notCheckable=checked==nil
    if tip then info.tooltipTitle=text;info.tooltipText=tip;info.tooltipOnButton=true end
    UIDropDownMenu_AddButton(info,1)
end
function A.BuildMenu(_,level)
    if level~=1 then return end
    local map=A.map:GetMapID();local counts={}
    for _,p in ipairs(A.PinsForMap(map)) do counts[p.category]=(counts[p.category] or 0)+1 end
    for _,category in ipairs(A.categories) do
        local k=category
        local tip=(k=='inn' or k=='mail') and 'Bundled Forever locations plus services you discover. No other addon is needed; coverage may have gaps.' or nil
        local suffix=k=='border' and '' or ' ('..(counts[k] or 0)..')'
        menuEntry(labels[k]..suffix,function() A.db.filters[k]=not A.db.filters[k];A.Refresh() end,A.db.filters[k],tip)
    end
    menuEntry('Show all',function() for _,k in ipairs(A.categories) do A.db.filters[k]=true end;A.Refresh() end)
    menuEntry('Hide all',function() for _,k in ipairs(A.categories) do A.db.filters[k]=false end;A.Refresh() end)
end
function A.AttachMap()
    if A.map or not WorldMapFrame or not WorldMapFrame.GetCanvas then return end
    A.map=WorldMapFrame
    local f=A.map
    local bar=CreateFrame('Frame',nil,f,'BackdropTemplate');A.bar=bar
    bar:SetSize(540,A.headerHeight);bar:SetPoint('TOPLEFT',f,'TOPLEFT',0,0);bar:SetFrameLevel(f:GetFrameLevel()+100)
    bar:SetBackdrop({bgFile='Interface\\Tooltips\\UI-Tooltip-Background'});bar:SetBackdropColor(.025,.022,.018,1)
    local footer=CreateFrame('Frame',nil,f,'BackdropTemplate');A.footer=footer
    footer:SetSize(540,A.footerHeight);footer:SetPoint('BOTTOMLEFT',f,'BOTTOMLEFT',0,0)
    footer:SetFrameLevel(f:GetFrameLevel()+100)
    -- Keep a single opaque coordinate strip above legacy map-coordinate widgets.
    footer:SetFrameStrata('HIGH');footer:SetFrameLevel(f:GetFrameLevel()+2500)
    footer:SetBackdrop({bgFile='Interface\\Tooltips\\UI-Tooltip-Background'});footer:SetBackdropColor(.025,.022,.018,1)
    bar:EnableMouse(true);bar:RegisterForDrag('LeftButton')
    bar:SetScript('OnDragStart',function() if not A.db.locked and not InCombatLockdown() then A.dragging=true;f:StartMoving() end end)
    bar:SetScript('OnDragStop',function()
        if not A.dragging then return end
        -- StopMoving may itself fire layout/viewport callbacks. Keep the drag
        -- guard active until the final position has been captured.
        f:StopMovingOrSizing();A.SaveMapPosition();A.dragging=nil
        local layout,viewport=A.dragLayoutPending,A.dragViewportPending
        A.dragLayoutPending=nil;A.dragViewportPending=nil
        if layout then A.ApplyLayout(true)
        else A.PositionMap();if viewport then A.QueueViewportFit() end end
    end)
    local function toggleSize()
        if InCombatLockdown() then A.Print('Map size can be changed after combat.');return end
        A.db.compact=not A.db.compact;A.ApplyLayout()
    end
    -- Replace the native size controls, retaining the shared canvas/pin providers.
    local border=f.BorderFrame
    local nativeSize=border and border.MaximizeMinimizeFrame
    if nativeSize then
        nativeSize:Hide()
        nativeSize:HookScript('OnShow',function(s) s:Hide() end)
    end
    local rail=CreateFrame('Frame',nil,f,'BackdropTemplate');A.actionRail=rail
    rail:SetWidth(A.railWidth);rail:SetPoint('TOPRIGHT',f,'TOPRIGHT',0,0)
    rail:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',0,0)
    rail:SetFrameStrata('HIGH');rail:SetFrameLevel(f:GetFrameLevel()+150)
    rail:SetBackdrop({bgFile='Interface\\Tooltips\\UI-Tooltip-Background'})
    rail:SetBackdropColor(.025,.027,.03,1)
    if A.Theme then
        A.Theme.Register(bar,'mapbar');A.Theme.Register(footer,'footer');A.Theme.Register(rail,'rail')
        A.mapThemeTrim=A.Theme.MapChrome(f)
    end
    local headingHost=CreateFrame('Frame',nil,f);A.zoneHeadingHost=headingHost
    headingHost:SetAllPoints(f);headingHost:EnableMouse(false);headingHost:SetFrameStrata('HIGH');headingHost:SetFrameLevel(f:GetFrameLevel()+200)
    A.zoneHeading=headingHost:CreateFontString(nil,'OVERLAY','GameFontNormal')
    A.zoneHeading:SetPoint('LEFT',bar,'LEFT',12,0);A.zoneHeading:SetJustifyH('LEFT');A.zoneHeading:SetWordWrap(false)
    A.menu=CreateFrame('Frame','MapperlyDropdown',UIParent,'UIDropDownMenuTemplate')
    UIDropDownMenu_Initialize(A.menu,A.BuildMenu,'MENU')
    local previous,railHeight=nil,4
    local function control(key,asset,tip,fn,gap)
        local b=button(rail,asset,fn);b:ClearAllPoints()
        if previous then
            b:SetPoint('TOP',previous,'BOTTOM',0,-(gap or 4));railHeight=railHeight+(gap or 4)
        else b:SetPoint('TOP',rail,'TOP',0,-4) end
        railHeight=railHeight+b:GetHeight();A.minimumRailHeight=railHeight+4
        previous=b
        A.AttachButtonTooltip(b,tip)
        A.controls=A.controls or {};A.controls[key]=b;return b
    end
    local close=CreateFrame('Button',nil,f,'UIPanelCloseButton');A.closeButton=close
    close:SetSize(22,22);close:SetPoint('TOPRIGHT',f,'TOPRIGHT',-5,-3)
    close:SetFrameStrata('HIGH');close:SetFrameLevel(f:GetFrameLevel()+3000)
    close:SetScript('OnClick',function() if HideUIPanel then HideUIPanel(f) else f:Hide() end end)
    A.AttachButtonTooltip(close,'Close map');A.controls=A.controls or {};A.controls.close=close
    A.sizeButton=control('size','Resize',function() return A.db.compact and 'Enlarge map' or 'Use compact map' end,toggleSize)
    A.navigation=control('parent','ParentMap',function()
        local info=C_Map.GetMapInfo and C_Map.GetMapInfo(f:GetMapID())
        local parent=info and info.parentMapID and C_Map.GetMapInfo(info.parentMapID)
        return parent and 'Zoom out to '..parent.name or 'Parent map'
    end,function()
        local info=C_Map.GetMapInfo and C_Map.GetMapInfo(f:GetMapID())
        if info and info.parentMapID and info.parentMapID>0 then f:SetMapID(info.parentMapID) end
    end,10)
    control('locate','Locate','My location: return to your zone and ping your arrow',current)
    control('navigate','Navigate','Destinations: coordinates, saved places and recent history. Alt-right-click map or marker for a quick waypoint.',function() A.ShowNavigationInput() end)
    control('notes','AddNote','Add note at player; Alt-click to place anywhere',function()
        local id=f:GetMapID();local pos=id and C_Map.GetPlayerMapPosition(id,'player')
        if not pos then
            id=C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit('player')
            pos=id and C_Map.GetPlayerMapPosition(id,'player')
            if pos then f:SetMapID(id) end
        end
        if pos then local x,y=pos:GetXY();A.ShowNote(id,x,y) else A.Print('Alt-click the map to place a note.') end
    end)
    control('filters','Filters','Location filters',function(self) ToggleDropDownMenu(1,nil,A.menu,self,0,0) end,10)
    local quest=control('quests','Quest',function() return A.db.questPane and 'Hide quest log' or 'Show quest log' end,function()
        A.db.questPane=not A.db.questPane;A.ApplyLayout()
        if A.SyncSettings then A.SyncSettings() end
    end)
    quest.icon:SetSize(24,24)
    quest.arrow=quest:CreateFontString(nil,'OVERLAY','GameFontNormalSmall')
    quest.arrow:SetPoint('BOTTOMRIGHT',quest,'BOTTOMRIGHT',-2,2)
    control('reveal','Reveal',function() return A.db.reveal and 'Hide unexplored terrain' or 'Reveal unexplored terrain' end,function() A.db.reveal=not A.db.reveal;A.Refresh() end)
    control('lock','Lock',function() return A.db.locked and 'Unlock map position' or 'Lock map position' end,function() A.db.locked=not A.db.locked;A.ApplyLayout() end,10)
    control('settings','Settings','Open Mapperly settings',A.ShowSettings)
    A.coordinateText=footer:CreateFontString(nil,'OVERLAY','GameFontNormalSmall')
    A.coordinateText:SetPoint('LEFT',footer,'LEFT',10,0);A.coordinateText:SetJustifyH('LEFT');A.coordinateText:SetWordWrap(false)
    A.brandText=bar:CreateFontString(nil,'OVERLAY','GameFontNormalSmall')
    A.brandText:SetPoint('RIGHT',bar,'RIGHT',-10,0);A.brandText:SetJustifyH('RIGHT');A.brandText:SetWordWrap(false)
    A.brandText:SetText('Mapperly '..A.version)
    if A.Theme then
        A.Theme.Register(A.zoneHeading,'zone')
        A.Theme.Register(A.coordinateText,'text',{kind='coordinate'});A.Theme.Register(A.brandText,'text',{kind='coordinate'})
        A.Theme.Apply()
    end
    A.AttachZoneLevels()
    if type(f.AdjustOverlayFrames)=='function' then hooksecurefunc(f,'AdjustOverlayFrames',A.PositionMapPinButton) end
    f:HookScript('OnShow',function() A.UpdateOpacity(true);A.ApplyLayout(true);A.Refresh() end)
    if f.SetMapID then hooksecurefunc(f,'SetMapID',A.Refresh) end
    if f.Maximize then hooksecurefunc(f,'Maximize',function() if not A.applying then A.db.compact=false;A.ApplyLayout() end end) end
    if f.Minimize then hooksecurefunc(f,'Minimize',function() if not A.applying then A.db.compact=true;A.ApplyLayout() end end) end
    if f.SetQuestLogPanelShown then hooksecurefunc(f,'SetQuestLogPanelShown',function(_,shown) if not A.applying then A.db.questPane=not not shown;A.ApplyLayout() end end) end
    f:HookScript('OnSizeChanged',function() if not A.applying then A.ApplyLayout() end end)
    f:GetCanvas():HookScript('OnSizeChanged',A.Refresh)
    if f.ScrollContainer then
        f.ScrollContainer:HookScript('OnSizeChanged',function() if not A.applying then A.QueueViewportFit() end end)
    end
    A.AttachMapInteractions(f)
    local elapsed=0
    local serviceRetry=0
    bar:SetScript('OnUpdate',function(_,dt)
        elapsed=elapsed+dt;if elapsed<.15 then return end;elapsed=0
        serviceRetry=serviceRetry+.15
        if serviceRetry>=5 then serviceRetry=0;if A.LoadServices then A.LoadServices() end end
        A.UpdateButtonStates()
        local scale=f:GetCanvas():GetEffectiveScale()
        if A.lastCanvasScale~=scale then A.lastCanvasScale=scale;A.RefreshPins() end
        A.UpdateOpacity()
        A.UpdateCoordinates()
    end)
    A.UpdateOpacity(true);A.ApplyLayout();A.Refresh()
end
