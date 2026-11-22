local _,A=...
A.headerHeight=42
A.footerHeight=22
A.railWidth=32
local function frame(value) return (type(value)=='table' or type(value)=='userdata') and value.Hide end
function A.HideChrome(value)
    if not frame(value) then return end
    value:Hide()
    if not A.hiddenChrome[value] then
        A.hiddenChrome[value]=true
        value:HookScript('OnShow',function(s) s:Hide() end)
    end
end
A.hiddenChrome={}
local function positionKey() return A.db.compact and 'position' or 'largePosition' end
function A.SaveMapPosition()
    local f=A.map
    if not f then return end
    local left,top=f:GetLeft(),f:GetTop()
    if type(left)~='number' or type(top)~='number' then return end
    local ratio=f:GetEffectiveScale()/UIParent:GetEffectiveScale()
    -- Frame coordinates use its effective scale; saved offsets use UIParent units.
    local x=left*ratio-(UIParent:GetLeft() or 0)
    local y=top*ratio-(UIParent:GetTop() or UIParent:GetHeight())
    if A.Number(x,-10000,10000,nil)==x and A.Number(y,-10000,10000,nil)==y then
        A.db[positionKey()]={x=x,y=y}
    end
end
function A.PositionMap()
    if A.dragging then return end
    local f=A.map
    local sw,sh=UIParent:GetWidth(),UIParent:GetHeight()
    -- Native portrait/trim extends beyond the logical frame rectangle.
    local side,bottom,top=12,12,16
    f:SetClampedToScreen(true);f:SetClampRectInsets(-side,side,top,-bottom)
    local p=A.db[positionKey()]
    local x=p and p.x or (sw-f:GetWidth())/2
    local y=p and p.y or -(sh-f:GetHeight())/2
    x=math.max(side,math.min(sw-f:GetWidth()-side,x))
    y=math.min(-top,math.max(f:GetHeight()+bottom-sh,y))
    f:ClearAllPoints();f:SetPoint('TOPLEFT',UIParent,'TOPLEFT',x,y)
end
function A.ResetMapPosition()
    A.db.position=nil;A.db.largePosition=nil
    A.ApplyLayout(true)
end
function A.PositionMapPinButton()
    local f=A.map
    local pin=f and f.WorldMapTrackingPinButton
    if not frame(pin) or not frame(f.ScrollContainer) then return end
    -- Forever normally anchors this at the canvas top-left, under our crest.
    -- Use the free corner beside the toolbar, leaving addon controls untouched.
    pin:ClearAllPoints()
    pin:SetPoint('TOPRIGHT',f.ScrollContainer,'TOPRIGHT',-6,-6)
end
function A.FitQuestBackground()
    local log=A.map and A.map.QuestLog
    local scroll=log and log.QuestsFrame and log.QuestsFrame.ScrollFrame
    local background=scroll and scroll.Background
    if not background then return end
    if not scroll.mapperlyBackgroundHooked and scroll.ResizeBackground then
        scroll.mapperlyBackgroundHooked=true
        -- Quest refreshes reset the atlas and reapply the native fixed-height crop.
        hooksecurefunc(scroll,'ResizeBackground',A.FitQuestBackground)
    end
    local atlas=background:GetAtlas()
    if not atlas then return end
    -- Restore the atlas UVs after the native crop, retaining normal/empty artwork.
    -- The same native texture covers the entire list instead of ending halfway.
    background:SetAtlas(atlas,false)
    background:ClearAllPoints()
    background:SetAllPoints(scroll)
    if A.Theme then A.Theme.QuestBackground(scroll,background) end
end
function A.FitViewport()
    local f=A.map
    if not f or not f:IsShown() then return end
    if A.dragging then A.dragViewportPending=true;return end
    if InCombatLockdown() then A.layoutPending=true;return end
    -- ShowUIPanel can finish anchoring after OnShow. Reassert the saved,
    -- decorated screen bounds once that native layout has settled.
    A.PositionMap()
    -- Native Minimize recalculates these before our final dimensions are applied.
    -- Rebuild zoom levels from the settled viewport, then discard the old pan ratio.
    if f.OnFrameSizeChanged then f:OnFrameSizeChanged() end
    if f.ResetZoom then f:ResetZoom(true) end
    A.Refresh()
end
function A.QueueViewportFit()
    if A.viewportFitQueued then return end
    if C_Timer and C_Timer.After then
        A.viewportFitQueued=true
        C_Timer.After(0,function()
            A.viewportFitQueued=nil
            A.FitViewport()
        end)
    else A.FitViewport() end
end
function A.LayoutShell()
    local f=A.map
    A.headerHeight=A.db.theme=='gatherly' and 26 or 42
    for _,key in ipairs({'BorderFrame','BlackoutFrame','NavBar','SidePanelToggle','WorldMapTrackingOptionsButton'}) do A.HideChrome(f[key]) end
    if f.SetQuestLogPanelShown then f:SetQuestLogPanelShown(A.db.questPane) end
    local sw,sh=UIParent:GetWidth(),UIParent:GetHeight()
    local width=sw*(A.db.compact and math.min(.86,.76*A.db.scale) or .92)
    local height=sh*(A.db.compact and math.min(.84,.78*A.db.scale) or .90)
    -- Native quest rows, details and search/count controls have fixed-width art.
    -- Reserve their native width instead of compressing them with map size.
    local questWidth=type(f.questLogWidth)=='number' and math.max(333,f.questLogWidth) or 333
    local pane=A.db.questPane and questWidth+12 or 0
    A.questPaneExtent=pane
    local inset=A.db.theme=='gatherly' and 6 or 0;A.mapInset=inset
    -- Keep native edge gutters outside the 3:2 artwork, not underneath opaque
    -- footer/toolbar surfaces that would cover the matching bronze frame.
    local strips=A.headerHeight+A.footerHeight+inset
    local mapWidth=math.min(width-pane-A.railWidth-2*inset,(height-strips)*1.5)
    if A.db.compact then
        -- The slider changes the window, not text/icon scale. Retain enough
        -- canvas height for the full toolbar and enough width beside the log.
        local maximum=math.max(1,math.min(sw*.92-pane-A.railWidth-2*inset,(sh*.90-strips)*1.5))
        local minimum=math.min(maximum,math.max(360,((A.minimumRailHeight or 374)-strips)*1.5))
        mapWidth=math.min(maximum,math.max(minimum,mapWidth))
    end
    f:SetScale(1);f:SetSize(mapWidth+pane+A.railWidth+2*inset,mapWidth/1.5+strips)
    if A.actionRail then
        -- On unusually small screens the native-width quest pane may prevent
        -- the full-height minimum; shrink only the rail to keep every action.
        local top=A.db.theme=='gatherly' and A.headerHeight or 0;A.railTopOffset=top
        A.actionRail:ClearAllPoints();A.actionRail:SetPoint('TOPRIGHT',f,'TOPRIGHT',-inset,-top)
        A.actionRail:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-inset,inset)
        A.actionRail:SetScale(math.min(1,(f:GetHeight()-inset-top-8)/((A.minimumRailHeight or 374)-8)))
    end
    local scroll=f.ScrollContainer
    if frame(scroll) then
        scroll:ClearAllPoints();scroll:SetPoint('TOPLEFT',f,'TOPLEFT',inset,-A.headerHeight)
        scroll:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-pane-A.railWidth-inset,A.footerHeight+inset)
    end
    if frame(f.QuestLog) and A.db.questPane then
        f.QuestLog:ClearAllPoints();f.QuestLog:SetPoint('TOPRIGHT',f,'TOPRIGHT',-6-A.railWidth-inset,-A.headerHeight)
        f.QuestLog:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-6-A.railWidth-inset,A.footerHeight+inset);f.QuestLog:SetWidth(questWidth)
    end
    A.PositionMapPinButton()
    A.FitQuestBackground()
    local surfaceWidth=f:GetWidth()-A.railWidth-2*inset
    if A.bar then A.bar:ClearAllPoints();A.bar:SetPoint('TOPLEFT',f,'TOPLEFT',inset,0);A.bar:SetSize(surfaceWidth,A.headerHeight) end
    if A.footer then A.footer:ClearAllPoints();A.footer:SetPoint('BOTTOMLEFT',f,'BOTTOMLEFT',inset,inset);A.footer:SetWidth(surfaceWidth) end
    local brandWidth=A.brandText and math.ceil(A.brandText:GetStringWidth()) or 0
    if A.brandText then A.brandText:SetWidth(brandWidth) end
    if A.Theme then A.Theme.PositionZoneHeading();A.Theme.RefreshMapMaterials() end
    if A.coordinateText then A.coordinateText:SetWidth(math.max(1,surfaceWidth-20)) end
end
function A.UpdateNavigation()
    if not A.zoneHeading then return end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(A.map:GetMapID())
    A.zoneHeading:SetText(info and A.ZoneTitle(info.mapID or A.map:GetMapID(),info.name) or 'World map')
end
