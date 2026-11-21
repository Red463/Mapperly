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
end
function A.FitViewport()
    local f=A.map
    if not f or not f:IsShown() then return end
    if InCombatLockdown() then A.layoutPending=true;return end
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
    -- The art gets a 3:2 viewport; bars are outside it, with no portrait or mat.
    local strips=A.headerHeight+A.footerHeight
    local mapWidth=math.min(width-pane-A.railWidth,(height-strips)*1.5)
    f:SetScale(1);f:SetSize(mapWidth+pane+A.railWidth,mapWidth/1.5+strips)
    local scroll=f.ScrollContainer
    if frame(scroll) then
        scroll:ClearAllPoints();scroll:SetPoint('TOPLEFT',f,'TOPLEFT',0,-A.headerHeight)
        scroll:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-pane-A.railWidth,A.footerHeight)
    end
    if frame(f.QuestLog) and A.db.questPane then
        f.QuestLog:ClearAllPoints();f.QuestLog:SetPoint('TOPRIGHT',f,'TOPRIGHT',-6-A.railWidth,-A.headerHeight)
        f.QuestLog:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-6-A.railWidth,A.footerHeight);f.QuestLog:SetWidth(questWidth)
    end
    A.FitQuestBackground()
    if A.bar then A.bar:SetWidth(f:GetWidth()-A.railWidth) end
    if A.zoneHeading then A.zoneHeading:SetWidth(math.max(80,f:GetWidth()-A.railWidth-24)) end
    if A.footer then A.footer:SetWidth(f:GetWidth()-A.railWidth) end
    if A.playerCoordinates then
        local column=math.max(1,(f:GetWidth()-A.railWidth-32)/2)
        A.playerCoordinates:SetWidth(column);A.cursorCoordinates:SetWidth(column)
    end
end
function A.UpdateNavigation()
    if not A.zoneHeading then return end
    local info=C_Map.GetMapInfo and C_Map.GetMapInfo(A.map:GetMapID())
    A.zoneHeading:SetText(info and A.ZoneTitle(info.mapID or A.map:GetMapID(),info.name) or 'World map')
end
