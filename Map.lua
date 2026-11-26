local _,A=...
local button=A.CreateIconButton
local function closeMap(frame)
    if InCombatLockdown() then
        if frame.IsProtected and frame:IsProtected() then A.Print('The game currently protects this map frame. Try closing it after combat.');return end
        -- HideUIPanel rejects all insecure addon calls during combat, even for
        -- the unprotected world map. Its normal OnHide lifecycle still runs.
        A.panelClosePending=true
        frame:Hide()
        return not frame:IsShown()
    end
    A.panelClosePending=nil
    if HideUIPanel then return HideUIPanel(frame) end
    return frame:Hide()
end
function A.FinishMapClose()
    if not A.panelClosePending or InCombatLockdown() then return end
    A.panelClosePending=nil
    local f=A.map
    -- skipShownCheck reconciles the panel manager after the immediate Hide.
    -- Never close a map the player has reopened since that request.
    if f and not f:IsShown() and HideUIPanel then HideUIPanel(f,true,true) end
end
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
    if A.drawerKey=='filters' then A.RefreshFilterPanel() end
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
local labels={mail='Mailboxes',inn='Inns',dungeon='Dungeon entrances',flight='Flight masters',transport='Boats, zeppelins and airships',portal='Portals',border='Zone exits',notes='Custom notes'}
function A.RefreshFilterPanel()
    if not A.filterWindow then return end
    local map=A.map:GetMapID();local counts={}
    for _,p in ipairs(A.PinsForMap(map)) do counts[p.category]=(counts[p.category] or 0)+1 end
    for k,row in pairs(A.filterWindow.rows) do
        row:SetChecked(A.db.filters[k])
        row.count:SetText(k~='border' and tostring(counts[k] or 0) or '')
    end
end
local function openFilters()
    local U=A.Dialogs
    if not A.filterWindow then
        local f=U.ToolWindow('MapperlyFilterWindow','Location filters','Markers on the current map',333,319)
        A.filterWindow=f;f.rows={}
        for index,k in ipairs(A.categories) do
            local row=CreateFrame('CheckButton',nil,f,'UICheckButtonTemplate')
            f.rows[k]=row
            row:SetSize(24,24);row:SetPoint('TOPLEFT',f,'TOPLEFT',16,-48-(index-1)*28)
            row:SetHitRectInsets(0,-265,0,0)
            local icon=row:CreateTexture(nil,'ARTWORK');icon:SetSize(18,18);icon:SetPoint('LEFT',row,'RIGHT',6,0)
            A.SetPinTexture(icon,k,nil,18)
            U.Label(row,labels[k],55,4,'GameFontHighlight')
            row.count=U.Label(row,'',250,5,'GameFontDisableSmall')
            row:SetScript('OnClick',function(s) A.db.filters[k]=not not s:GetChecked();A.Refresh();A.SyncSettings() end)
        end
        local function setAll(enabled)
            for _,k in ipairs(A.categories) do A.db.filters[k]=enabled end
            A.Refresh();A.SyncSettings()
        end
        U.Action(f,'Show all',14,279,148,function() setAll(true) end)
        U.Action(f,'Hide all',171,279,148,function() setAll(false) end)
    end
    A.RefreshFilterPanel()
    U.Show(A.filterWindow,'filters')
end
function A.AttachMap()
    if A.map or not WorldMapFrame or not WorldMapFrame.GetCanvas then return end
    A.map=WorldMapFrame
    local f=A.map
    -- Native M handling can request another open display state when character
    -- miniWorldMap/questLogOpen preferences disagree with our windowed shell.
    -- Keep native opening outside combat and global binding/rule checks.
    -- Combat opening uses the unprotected frame and defers mode changes.
    local nativeToggle=f.HandleUserActionToggleSelf
    if type(nativeToggle)=='function' then
        -- Direct opens have no native panel slot. Let CloseSpecialWindows
        -- dismiss them without registering code in the global Escape dispatcher.
        local dismiss=CreateFrame('Frame','MapperlyCombatMapDismiss',UIParent)
        dismiss:Hide()
        table.insert(UISpecialFrames,'MapperlyCombatMapDismiss')
        dismiss:SetScript('OnHide',function(self)
            if not self:IsShown() and f:IsVisible() then closeMap(f) end
        end)
        f:HookScript('OnHide',function(self)
            if not self:IsShown() then dismiss:Hide() end
        end)
        f.HandleUserActionToggleSelf=function(self,...)
            if self==f and self:IsShown() then return closeMap(self) end
            if self==f and InCombatLockdown() then
                if self.IsProtected and self:IsProtected() then A.Print('The game currently protects this map frame. Try opening it after combat.');return end
                -- The global map binding already checked the game's disabled-map
                -- rules. Show the unprotected frame without entering the blocked
                -- panel helper or changing native size/quest display states.
                A.panelClosePending=nil;A.combatMapOpened=true;A.layoutPending=true
                -- Native OnShow otherwise performs its first-open mode change
                -- through the protected panel delegate. Our deferred layout
                -- applies the remembered mode after combat instead.
                self.needUpdateDisplayState=nil
                self:Show()
                if self:IsShown() then dismiss:Show() end
                return
            end
            return nativeToggle(self,...)
        end
    end
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
    local function finishDragWork(reanchor)
        local layout,viewport=A.dragLayoutPending,A.dragViewportPending
        A.dragLayoutPending=nil;A.dragViewportPending=nil
        if layout then A.ApplyLayout(true)
        elseif reanchor then A.PositionMap();if viewport then A.QueueViewportFit() end
        elseif viewport then A.QueueViewportFit() end
    end
    bar:SetScript('OnDragStart',function()
        if A.db.locked or InCombatLockdown() and f.IsProtected and f:IsProtected() then return end
        A.dragging=true
        local ok,started=pcall(function()
            -- Native first-show/display changes can clear this independently
            -- of Mapperly's lock option, especially with deferred layout.
            f:SetMovable(true)
            if not f:IsMovable() then return false end
            f:StartMoving();return true
        end)
        if not ok or not started then
            -- A failed/partially started move must not strand the drag guard.
            pcall(f.StopMovingOrSizing,f);A.dragging=nil
            if A.MapReport then A.MapReport.Log('drag-start-failed',type(started)=='string' and started or 'Native map is not movable',true) end
            finishDragWork(false)
        end
    end)
    bar:SetScript('OnDragStop',function()
        if not A.dragging then return end
        -- StopMoving may itself fire layout/viewport callbacks. Keep the drag
        -- guard active until the final position has been captured.
        f:StopMovingOrSizing();A.SaveMapPosition();A.dragging=nil
        finishDragWork(true)
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
    local function drawerControl(key,asset,title,open,gap)
        return control(key,asset,function() return (A.drawerKey==key and 'Hide ' or 'Show ')..title end,function()
            if A.drawerKey==key then A.SelectMapDrawer(nil) else open() end
        end,gap)
    end
    local close=CreateFrame('Button',nil,f,'UIPanelCloseButton');A.closeButton=close
    close:SetSize(22,22);close:SetPoint('TOPRIGHT',f,'TOPRIGHT',-5,-3)
    close:SetFrameStrata('HIGH');close:SetFrameLevel(f:GetFrameLevel()+3000)
    close:SetScript('OnClick',function() closeMap(f) end)
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
    drawerControl('navigate','Navigate','destinations',function() A.ShowNavigationInput(nil,'navigate') end)
    drawerControl('notes','AddNote','map notes',function()
        local id=f:GetMapID();local pos=id and C_Map.GetPlayerMapPosition(id,'player')
        if not pos then
            id=C_Map.GetBestMapForUnit and C_Map.GetBestMapForUnit('player')
            pos=id and C_Map.GetPlayerMapPosition(id,'player')
            if pos then f:SetMapID(id) end
        end
        if pos then local x,y=pos:GetXY();A.ShowNote(id,x,y,nil,'notes')
        else A.ShowNoteBrowser();A.Print('Alt-click the map to place a note.') end
    end)
    drawerControl('filters','Filters','location filters',openFilters,10)
    local quest=control('quests','Quest',function() return A.QuestPaneSelected() and 'Hide quest log' or 'Show quest log' end,
        function() A.SelectQuestPane(not A.QuestPaneSelected()) end)
    quest.icon:SetSize(24,24)
    quest.arrow=quest:CreateFontString(nil,'OVERLAY','GameFontNormalSmall')
    quest.arrow:SetPoint('BOTTOMRIGHT',quest,'BOTTOMRIGHT',-2,2)
    drawerControl('services','Services','nearby services',function() A.SelectMapDrawer('services') end)
    control('reveal','Reveal',function() return A.db.reveal and 'Hide unexplored terrain' or 'Reveal unexplored terrain' end,function() A.db.reveal=not A.db.reveal;A.Refresh() end)
    control('lock','Lock',function() return A.db.locked and 'Unlock map position' or 'Lock map position' end,function() A.db.locked=not A.db.locked;A.ApplyLayout() end,10)
    drawerControl('settings','Settings','Mapperly settings',function() A.ShowSettings('settings') end)
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
    if f.SetQuestLogPanelShown then
        hooksecurefunc(f,'SetQuestLogPanelShown',function(_,shown)
            if A.applying then return end
            -- Native quest-log opens (including L and quest links) take this slot.
            if shown or not A.drawerKey then A.SelectQuestPane(shown) else A.ApplyLayout() end
        end)
    end
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
        if A.lastCanvasScale~=scale then
            A.lastCanvasScale=scale;A.RefreshPins()
            if A.JourneyView and A.db.showJourneyRoute then A.JourneyView.Refresh(true) end
        end
        A.UpdateOpacity()
        A.UpdateCoordinates()
    end)
    A.UpdateOpacity(true);A.ApplyLayout();A.Refresh()
end
