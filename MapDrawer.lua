local _, A = ...

-- QuestLog keeps its native width. Mapperly forms share one scroll viewport
-- and keep the same controls, callbacks and drafts when the map changes size.
local host, scroll, content, overflowBar
local mounted
local icons = {navigate='Navigate', notes='AddNote', settings='Settings', filters='Filters'}

local function release()
    if not mounted then return end
    local window = mounted
    mounted = nil
    window:Hide()
    window:ClearAllPoints()
    window:SetParent(UIParent)
    window:SetFrameStrata('DIALOG')
    A.Theme.SetDrawerIcon(window,nil)
    window:SetScale(1)
    window:SetSize(window.toolWidth,window.toolHeight)
    if window.FitToolHeight then window:FitToolHeight(window.toolHeight) end
    window:SetPoint('CENTER', UIParent, 'CENTER')
    window:SetClampedToScreen(true)
    window:SetMovable(true)
    window:RegisterForDrag('LeftButton')
end

function A.SelectMapDrawer(key, window)
    A.drawerKey, A.drawerWindow = key, window
    if mounted ~= window then release() end
    if window and mounted ~= window then window:Hide() end
    A.ApplyLayout()
    if InCombatLockdown() then A.Print('The map drawer will update after combat.') end
    if A.SyncSettings then A.SyncSettings() end
end

function A.LayoutToolDrawer(width,height)
    local window = A.drawerWindow
    if not window then
        if host then host:Hide() end
        return
    end
    if not host then
        host = A.Dialogs.Card(A.map, 0, 0, 1, 1)
        host:EnableMouse(true)
        scroll = CreateFrame('ScrollFrame', nil, host)
        scroll:SetAllPoints(host)
        content = CreateFrame('Frame', nil, scroll)
        scroll:SetScrollChild(content)
        -- Only unusually short viewports need whole-panel scrolling. Keep
        -- the normal content width and leave wheel input to the list under it.
        overflowBar=CreateFrame('Slider',nil,host)
        overflowBar:SetOrientation('VERTICAL');overflowBar:SetWidth(8)
        overflowBar:SetPoint('TOPRIGHT',host,'TOPRIGHT',-1,-6)
        overflowBar:SetPoint('BOTTOMRIGHT',host,'BOTTOMRIGHT',-1,6)
        local thumb=overflowBar:CreateTexture(nil,'ARTWORK')
        thumb:SetSize(6,24);thumb:SetColorTexture(.65,.52,.31,.95)
        overflowBar:SetThumbTexture(thumb)
        overflowBar:SetScript('OnValueChanged',function(_,value) scroll:SetVerticalScroll(value) end)
        scroll:SetScript('OnMouseWheel',function(_,delta)
            overflowBar:SetValue(scroll:GetVerticalScroll()-delta*32)
        end)
    end
    local formHeight=math.max(window.toolHeight,height)
    local overflow=math.max(0,formHeight-height)
    content:SetSize(width,formHeight)
    window:SetSize(width,formHeight)
    if window.FitToolHeight then window:FitToolHeight(formHeight) end
    overflowBar:SetMinMaxValues(0,overflow)
    overflowBar:SetShown(overflow>0)
    scroll:EnableMouseWheel(overflow>0)
    local offset=mounted==window and math.min(scroll:GetVerticalScroll(),overflow) or 0
    overflowBar:SetValue(offset)
    scroll:SetVerticalScroll(offset)
    if mounted ~= window then
        mounted = window
        window:ClearAllPoints()
        window:SetParent(content)
        window:SetFrameStrata(content:GetFrameStrata())
        A.Theme.SetDrawerIcon(window,icons[A.drawerKey])
        window:SetClampedToScreen(false)
        window:RegisterForDrag()
        window:SetMovable(false)
        window:SetPoint('TOP', content, 'TOP')
        if not window.mapperlyDrawerHook then
            window.mapperlyDrawerHook = true
            window:HookScript('OnHide', function(self)
                -- A hidden parent also fires OnHide. Only an explicit close
                -- (Done, Save, Cancel or X) should dismiss the selected tool.
                if mounted == self and not self:IsShown() then A.SelectMapDrawer(nil) end
            end)
        end
    end
    window:SetScale(1)
    host:Show()
    window:Show()
    return host
end
