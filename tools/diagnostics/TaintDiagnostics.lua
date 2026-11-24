-- Diagnostic build only. Observe events/read existing errors; never hook native
-- handlers, inspect aura data, change CVars or replace shared Blizzard mixins.
local _,A=...
local D={entries={},total=0,limit=16,maxBytes=58000};A.TaintDiagnostics=D
local function readable(v)return not (issecretvalue and issecretvalue(v))end
local function text(v)
    if not readable(v) then return '<secret>' end
    if type(v)=='string' then return v end
    if type(v)=='number' or type(v)=='boolean' then return tostring(v) end
    return '-'
end
local function call(fn,...)
    if type(fn)~='function' then return end
    local ok,a,b,c,d=pcall(fn,...);if ok then return a,b,c,d end
end
local function clean(s)
    for _,private in ipairs({call(UnitName,'player') or false,call(UnitGUID,'player') or false,call(GetRealmName) or false}) do
        if readable(private) and type(private)=='string' and #private>0 then s=s:gsub(private:gsub('([^%w])','%%%1'),'[private]') end
    end
    return s:gsub('|','/')
end
local function ownership(lines,label,object,keys)
    if not readable(object) or (type(object)~='table' and type(object)~='userdata') then return end
    for _,key in ipairs(keys) do
        local secure,by=call(issecurevariable,object,key)
        local state=readable(secure) and (secure==true and 'secure' or secure==false and 'tainted by '..text(by) or 'unavailable') or 'unavailable'
        lines[#lines+1]=label..'.'..key..': '..state
    end
end
local function nativeErrors(lines)
    local frame=ScriptErrorsFrame
    if type(frame)~='table' or type(frame.GetErrorData)~='function' then lines[#lines+1]='Native error list unavailable.';return end
    local found=0
    for i=1,1000 do
        local err=call(frame.GetErrorData,frame,i)
        if not readable(err) or type(err)~='table' then break end
        local message=readable(err.message) and type(err.message)=='string' and err.message
        local stack=readable(err.stack) and type(err.stack)=='string' and err.stack or ''
        if message and (message:find('Mapperly',1,true) or stack:find('AddOns/Mapperly/',1,true)) then
            found=found+1
            lines[#lines+1]=message:sub(1,1800)..'\n'..stack:sub(1,4000)
            if found==4 then break end
        end
    end
    if found==0 then lines[#lines+1]='No readable Mapperly errors in the native list.' end
end
function D.Build()
    local v,b=call(GetBuildInfo)
    local lines={'Mapperly taint investigation: '..text(A.version),'Client: '..text(v)..' build='..text(b),
        'Combat: '..text(call(InCombatLockdown))..' map shown: '..text(A.map and call(A.map.IsShown,A.map)),
        'Blocked actions: '..D.total..'; retained: '..#D.entries,
        'Capture is passive. Event stacks are delivery-time evidence, not guaranteed taint origins.',
        '\nNative ownership (current state):'}
    ownership(lines,'Global',_G,{'WorldMapFrame','ShowUIPanel','HideUIPanel','EditModeManagerFrame'})
    ownership(lines,'WorldMapFrame',A.map,{'HandleUserActionToggleSelf','SetMapID','mapID','expandedMapInsetsByMapID','dataProviders'})
    ownership(lines,'MapCanvasPinMixin',MapCanvasPinMixin,{'CheckMouseButtonPassthrough'})
    ownership(lines,'EditModeManagerFrame',EditModeManagerFrame,{'registeredSystemFrames','ShowSystemSelections','HideSystemSelections','UpdateLayoutInfo'})
    for _,name in ipairs({'BuffFrame','DebuffFrame','PlayerFrame','TargetFrame'}) do
        ownership(lines,name,_G[name],{'OnEditModeEnter','OnEditModeExit','Update','UpdateAuras'})
    end
    lines[#lines+1]='\nExisting native Mapperly errors (messages/stacks only; no locals):'
    nativeErrors(lines)
    lines[#lines+1]='\nBlocked-action capture:'
    for _,entry in ipairs(D.entries) do lines[#lines+1]=entry end
    return clean(table.concat(lines,'\n')):sub(1,D.maxBytes)
end
function D.Open(previous)
    if InCombatLockdown and InCombatLockdown() then A.Print('Open the taint report after combat. Capture is still running.');return end
    local report=previous and MapperlyTaintDiagnosticsDB and MapperlyTaintDiagnosticsDB.report or not previous and D.Build()
    if type(report)~='string' then A.Print('No saved report is available.');return end
    local U=A.Dialogs;local f=D.frame
    if not f then
        f=U.Window('MapperlyTaintReportWindow','Mapperly taint report','Press Ctrl+C to copy. Nothing is sent automatically.',740,580);D.frame=f
        local scroll=CreateFrame('ScrollFrame',nil,f,'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT',f,'TOPLEFT',24,-100);scroll:SetSize(666,400)
        f.edit=U.Input(scroll,0,0,660,400,D.maxBytes,true);scroll:SetScrollChild(f.edit)
        f.edit:SetScript('OnEscapePressed',function()f:Hide()end)
        U.Action(f,'Select all',24,526,120,function()f.edit:SetFocus();f.edit:HighlightText()end)
        U.Action(f,'Close',596,526,120,function()f:Hide()end)
    end
    f.edit:SetText(report);f.edit:SetHeight(math.max(400,select(2,report:gsub('\n',''))*15+24))
    U.Show(f);f.edit:SetFocus();f.edit:HighlightText()
end
local baseCommand=SlashCmdList.MAPPERLY
SlashCmdList.MAPPERLY=function(msg)
    local arg=type(msg)=='string' and msg:match('^%s*taintreport%s*(.-)%s*$')
    if arg~=nil then
        if arg=='' then return D.Open() end
        if arg=='previous' then return D.Open(true) end
        A.Print('/mapperly taintreport [previous]');return
    end
    return baseCommand(msg)
end
D.events=CreateFrame('Frame')
for _,event in ipairs({'ADDON_LOADED','ADDON_ACTION_BLOCKED','ADDON_ACTION_FORBIDDEN','PLAYER_LOGOUT'}) do D.events:RegisterEvent(event) end
D.events:SetScript('OnEvent',function(_,event,addon,fn)
    if event=='ADDON_LOADED' and addon=='Mapperly' then
        if type(MapperlyTaintDiagnosticsDB)~='table' then MapperlyTaintDiagnosticsDB={} end
        A.Print('Taint diagnostic build: quest normally, then use /mapperly taintreport after combat.');return
    end
    if event=='PLAYER_LOGOUT' then
        MapperlyTaintDiagnosticsDB=type(MapperlyTaintDiagnosticsDB)=='table' and MapperlyTaintDiagnosticsDB or {}
        MapperlyTaintDiagnosticsDB.report=D.Build();return
    end
    if event~='ADDON_ACTION_BLOCKED' and event~='ADDON_ACTION_FORBIDDEN' then return end
    if not readable(addon) or addon~='Mapperly' then return end
    D.total=D.total+1
    local entry=text(call(GetTime))..' '..event..' '..text(fn):sub(1,180)..' combat='..text(call(InCombatLockdown))
    entry=entry..'\n'..text(call(debugstack,3,14,0)):sub(1,1800)
    D.entries[#D.entries+1]=clean(entry)
    if #D.entries>D.limit then table.remove(D.entries,1) end
end)
