local _,A=...
local C={ready=false};A.Compatibility=C
local function tableValue(v)return type(v)=='table' and v or nil end
function C.Detect()
    -- EQoL's IsFrameEnabled query initializes saved defaults. Read the active
    -- runtime DB and registry instead; never change another addon's settings.
    local addon=tableValue(_G.EnhanceQoL)
    local mover=addon and tableValue(addon.Mover)
    local db=mover and tableValue(mover.db)
    if not db or db.enabled~=true then return false end
    local frames=tableValue(db.frames)
    local saved=frames and tableValue(frames.WorldMapFrame)
    if saved and type(saved.enabled)=='boolean' then return saved.enabled end
    local functions=tableValue(mover.functions)
    local get=functions and functions.GetEntryForFrameName
    if type(get)~='function' then return false end
    local ok,entry=pcall(get,'WorldMapFrame')
    return ok and type(entry)=='table' and entry.defaultEnabled~=false or false
end
function C.Check()
    local active=C.Detect()
    if not active then
        if C.frame then C.frame:Hide() end
        return false
    end
    if not C.ready or C.warned or not A.db or not A.map or not A.map:IsShown() then return false end
    if InCombatLockdown and InCombatLockdown() then return false end
    if A.Announcements and A.Announcements.IsBusy() then return false end
    local U=A.Dialogs;local f=C.frame
    if not f then
        f=U.Window('MapperlyCompatibilityWindow','Map position conflict','EnhanceQoL World Map mover',540,350);C.frame=f
        f.body=U.Label(f,"EnhanceQoL's World Map mover is enabled. Both addons manage the same window, which can make Mapperly snap back or reset after changing settings.\n\nIn /eqol: Interface > Mover > World, untick World Map, then /reload.",28,110,'GameFontHighlightSmall')
        f.body:SetSize(484,136);f.body:SetWordWrap(true);f.body:SetJustifyH('LEFT')
        local hint=U.Label(f,'Other EnhanceQoL mover features can stay enabled.',28,260,'GameFontDisableSmall');hint:SetWidth(484)
        f.done=U.Action(f,'Got it',400,300,112,function()f:Hide()end)
    end
    U.Show(f)
    if f:IsShown() then C.warned=true;return true end
    return false
end
local events=CreateFrame('Frame',nil,UIParent);C.events=events
events:SetSize(1,1);events:SetPoint('TOPLEFT',UIParent,'TOPLEFT',0,0);events:EnableMouse(false)
events:RegisterEvent('PLAYER_ENTERING_WORLD');events:RegisterEvent('PLAYER_LEAVING_WORLD')
events:SetScript('OnEvent',function(_,event)
    C.ready=event=='PLAYER_ENTERING_WORLD'
    if not C.ready and C.frame then C.frame:Hide() end
end)
local elapsed=0
events:SetScript('OnUpdate',function(_,dt)
    if not C.ready then return end
    elapsed=elapsed+dt;if elapsed<1 then return end;elapsed=0
    if C.frame and C.frame:IsShown() or A.map and A.map:IsShown() then C.Check() end
end)
