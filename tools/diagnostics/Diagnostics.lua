-- Loaded only by tools/package_diagnostic.py; never part of the normal TOC.
local _,A=...
local D={limit=400,watched=setmetatable({},{__mode='k'})};A.Diagnostics=D
local function value(v)
    if issecretvalue and issecretvalue(v) then return '<secret>' end
    if type(v)=='number' then return string.format('%.3f',v) end
    if type(v)=='string' or type(v)=='boolean' then return tostring(v) end
    return type(v)=='nil' and '-' or '<'..type(v)..'>'
end
local function call(object,method,...)
    if not object or type(object[method])~='function' then return '-' end
    local ok,a,b,c,d=pcall(object[method],object,...)
    if not ok then return '<unavailable>' end
    return value(a),value(b),value(c),value(d)
end
local function name(f)
    if not f then return '-' end
    if f==A.map then return 'WorldMapFrame' end
    if f==A.bar then return 'Mapperly.titlebar' end
    if f==UIParent then return 'UIParent' end
    if f==A.mapThemeTrim then return 'Mapperly.trim' end
    if A.mapThemeTrim and f==A.mapThemeTrim.themeChrome then return 'Mapperly.chrome' end
    if type(f)=='table' or type(f)=='userdata' then
        local n=call(f,'GetName')
        return n~='-' and n or '<anonymous '..tostring(f)..'>'
    end
    return value(f)
end
local function rect(f)
    return 'L='..call(f,'GetLeft')..' T='..call(f,'GetTop')..' W='..call(f,'GetWidth')..' H='..call(f,'GetHeight')..' scale='..call(f,'GetEffectiveScale')
end
local function point(f)
    if not f or type(f.GetPoint)~='function' then return '-' end
    local ok,p,r,rp,x,y=pcall(f.GetPoint,f,1)
    return ok and table.concat({value(p),name(r),value(rp),value(x),value(y)},',') or '<unavailable>'
end
local function saved(p) return type(p)=='table' and value(p.x)..','..value(p.y) or '-' end
local function snapshot()
    local db=A.db or {};local f=A.map
    return rect(f)..' anchor='..point(f)..' points='..call(f,'GetNumPoints')..' shown='..call(f,'IsShown')..' movable='..call(f,'IsMovable')..
        ' ui='..call(UIParent,'GetWidth')..'x'..call(UIParent,'GetHeight')..'@'..call(UIParent,'GetEffectiveScale')..
        ' dragging='..value(A.dragging)..' applying='..value(A.applying)..' queued='..value(A.viewportFitQueued)..
        ' pending='..value(A.dragLayoutPending)..'/'..value(A.dragViewportPending)..' combat='..value(InCombatLockdown and InCombatLockdown())..
        ' compact='..value(db.compact)..' locked='..value(db.locked)..' theme='..value(db.theme)..
        ' saved='..saved(db.position)..' largeSaved='..saved(db.largePosition)
end
local function trace()
    if not debugstack then return '' end
    local ok,s=pcall(debugstack,4,8,0)
    return ok and type(s)=='string' and s:sub(1,1200) or '<stack unavailable>'
end
local function now() return GetTime and GetTime() or 0 end
function D.Log(event,detail,stack)
    if not D.enabled or D.busy then return end
    D.busy=true
    local ok=pcall(function()
        local db=MapperlyDiagnosticsDB
        local state=snapshot();D.last=state
        db.total=db.total+1
        local line=string.format('%06d +%.3f %s %s\n  %s',db.total,now()-D.started,event,detail or '',state)
        if stack then line=line..'\n'..trace() end
        db.lines[#db.lines+1]=line
        if #db.lines>D.limit then table.remove(db.lines,1) end
    end)
    D.busy=nil
    if not ok then D.observerErrors=(D.observerErrors or 0)+1 end
end
local function environment()
    local lines={'Mapperly map position diagnostics','Build: '..value(A.version),'UIParent: '..rect(UIParent)}
    if GetBuildInfo then
        local ok,v,b,_,interface=pcall(GetBuildInfo)
        if ok then lines[#lines+1]='Client: '..value(v)..' build '..value(b)..' interface '..value(interface) end
    end
    if GetPhysicalScreenSize then
        local ok,w,h=pcall(GetPhysicalScreenSize)
        if ok then lines[#lines+1]='Physical display: '..value(w)..' x '..value(h) end
    end
    if GetCVar then
        for _,key in ipairs({'useUiScale','uiScale','gxWindowedResolution','gxMaximize','gxMonitor','gxWindow','gxResolution'}) do
            local ok,v=pcall(GetCVar,key)
            if ok then lines[#lines+1]='CVar '..key..'='..value(v) end
        end
    end
    local addons=C_AddOns
    if addons and addons.GetNumAddOns and addons.GetAddOnInfo and addons.IsAddOnLoaded then
        local ok,count=pcall(addons.GetNumAddOns)
        if ok and type(count)=='number' then
            local loaded={}
            for i=1,count do
                local good,isLoaded=pcall(addons.IsAddOnLoaded,i)
                if good and isLoaded then
                    local found,id=pcall(addons.GetAddOnInfo,i)
                    if found then
                        local version=addons.GetAddOnMetadata and select(2,pcall(addons.GetAddOnMetadata,id,'Version'))
                        loaded[#loaded+1]=value(id)..'@'..value(version)
                    end
                end
            end
            table.sort(loaded);lines[#lines+1]='Loaded addons: '..table.concat(loaded,', ')
        end
    end
    return table.concat(lines,'\n')
end
function D.Report(data)
    data=data or MapperlyDiagnosticsDB or {}
    return (data.header or 'Mapperly map position diagnostics')..'\nEvents captured: '..tostring(data.total or 0)..
        '; retained: '..tostring(#(data.lines or {}))..'; observer errors: '..tostring(D.observerErrors or 0)..
        '\n=== Event trace (oldest retained first) ===\n'..table.concat(data.lines or {},'\n\n')
end
local function watch(object,key,label)
    if not object or type(object[key])~='function' then return end
    D.watched[object]=D.watched[object] or {}
    if D.watched[object][key] then return end
    local ok=pcall(hooksecurefunc,object,key,function(...)
        if not D.enabled then return end
        local arguments={...};local count=select('#',...)
        local success,detail=pcall(function()
            local result={}
            for i=arguments[1]==object and 2 or 1,math.min(count,6) do
                local v=arguments[i]
                result[#result+1]=(type(v)=='table' or type(v)=='userdata') and name(v) or value(v)
            end
            return table.concat(result,',')
        end)
        D.Log(label..'.'..key,success and detail or '<arguments unavailable>',true)
    end)
    if ok then D.watched[object][key]=true end
end
local function scripts(f,label)
    if not f then return end
    D.watched[f]=D.watched[f] or {}
    -- Keep decorative chrome input-transparent; global events trace clicks.
    for _,script in ipairs({'OnDragStart','OnDragStop','OnShow','OnHide','OnSizeChanged'}) do
        local key='script:'..script
        if not D.watched[f][key] then
            local ok=pcall(f.HookScript,f,script,function(_,arg) D.Log(label..'.'..script,value(arg),true) end)
            if ok then D.watched[f][key]=true end
        end
    end
end
function D.Attach()
    local f=A.map;if not f then return end
    for _,entry in ipairs({{f,'map'},{A.bar,'bar'},{A.mapThemeTrim,'trim'},{A.mapThemeTrim and A.mapThemeTrim.themeChrome,'chrome'}}) do
        local target,label=entry[1],entry[2]
        if target then
            for _,key in ipairs({'SetPoint','ClearAllPoints','SetAllPoints','StartMoving','StopMovingOrSizing','SetScale','SetSize','SetMovable','SetUserPlaced','SetClampedToScreen','SetClampRectInsets','SetParent'}) do watch(target,key,label) end
            scripts(target,label)
        end
    end
    D.Log('attach','UIParent '..rect(UIParent),false)
end
function D.Start()
    if MapperlyDiagnosticsDB and type(MapperlyDiagnosticsDB.lines)=='table' and #MapperlyDiagnosticsDB.lines>0 then
        D.previous=D.Report();D.previous=D.previous:sub(1,800000)
    end
    MapperlyDiagnosticsDB={header=environment(),lines={},total=0,previous=D.previous}
    D.started=now();D.enabled=true;D.Attach();D.Log('capture-start','',true)
end
function D.Stop() D.Log('capture-stop','',false);D.enabled=false end
function D.Show(previous)
    D.Stop()
    local text=previous and (D.previous or MapperlyDiagnosticsDB and MapperlyDiagnosticsDB.previous) or D.Report()
    if not text then A.Print('No previous diagnostic capture is available.');return end
    if not D.window then
        local U=A.Dialogs
        local f=U.Window('MapperlyDiagnosticsWindow','Mapperly diagnostics','Select all, then Ctrl+C. Send the copied report back to Tom.',740,580)
        D.window=f
        local scroll=CreateFrame('ScrollFrame',nil,f,'UIPanelScrollFrameTemplate')
        scroll:SetPoint('TOPLEFT',f,'TOPLEFT',24,-100);scroll:SetPoint('BOTTOMRIGHT',f,'BOTTOMRIGHT',-46,64)
        local edit=CreateFrame('EditBox',nil,scroll);D.edit=edit
        edit:SetMultiLine(true);edit:SetAutoFocus(false);edit:SetFontObject('ChatFontNormal');edit:SetMaxLetters(0);edit:SetSize(660,400)
        edit:SetScript('OnEscapePressed',function() f:Hide() end);scroll:SetScrollChild(edit)
        U.Action(f,'Select all',24,526,120,function() edit:SetFocus();edit:HighlightText() end)
        A.Theme.ButtonRole(U.Action(f,'Close',596,526,120,function() f:Hide() end),'primary')
    end
    D.edit:SetText(text);A.Dialogs.Show(D.window);D.edit:SetFocus();D.edit:HighlightText()
end
local baseCommand=SlashCmdList.MAPPERLY
SlashCmdList.MAPPERLY=function(message,...)
    local arg=message:match('^%s*diagnose%s*(.-)%s*$')
    if arg==nil then return baseCommand(message,...) end
    if arg=='start' then D.Start();A.Print('Diagnostic capture started. Reproduce the snap-back, then use /mapperly diagnose report.')
    elseif arg=='stop' then D.Stop();A.Print('Diagnostic capture stopped.')
    elseif arg=='previous' then D.Show(true)
    elseif arg=='status' then A.Print('Capture '..(D.enabled and 'running' or 'stopped')..'; retained '..#((MapperlyDiagnosticsDB or {}).lines or {})..' events.')
    elseif arg=='' or arg=='report' then D.Show()
    else A.Print('/mapperly diagnose start | report | stop | status | previous') end
end
for _,key in ipairs({'ApplyLayout','SaveMapPosition','PositionMap','FitViewport','QueueViewportFit','LayoutShell','ResetMapPosition'}) do watch(A,key,'Mapperly') end
if type(A.AttachMap)=='function' then pcall(hooksecurefunc,A,'AttachMap',D.Attach) end
for _,key in ipairs({'UpdateUIPanelPositions','RestoreUIPanelArea','ShowUIPanel','HideUIPanel','UIParent_ManageFramePositions'}) do
    if type(_G[key])=='function' then
        pcall(hooksecurefunc,key,function(target)
            if D.enabled and A.map and A.map:IsShown() then D.Log('Blizzard.'..key,name(target),true) end
        end)
    end
end
local observer=CreateFrame('Frame')
D.observer=observer
for _,event in ipairs({'ADDON_LOADED','PLAYER_LOGIN','PLAYER_LOGOUT','DISPLAY_SIZE_CHANGED','UI_SCALE_CHANGED','GLOBAL_MOUSE_DOWN','GLOBAL_MOUSE_UP','ADDON_ACTION_BLOCKED','ADDON_ACTION_FORBIDDEN'}) do observer:RegisterEvent(event) end
observer:SetScript('OnEvent',function(_,event,a,b)
    if event=='ADDON_LOADED' and a=='Mapperly' then D.Start();A.Print('DIAGNOSTIC BUILD: use /mapperly diagnose start, reproduce the snap-back, then /mapperly diagnose report.');return end
    if event=='PLAYER_LOGIN' then D.Attach() end
    if event=='PLAYER_LOGOUT' then D.Stop();return end
    if not D.enabled then return end
    if event=='GLOBAL_MOUSE_DOWN' or event=='GLOBAL_MOUSE_UP' then
        if not A.map or not A.map:IsShown() then return end
        local focus=GetMouseFoci and GetMouseFoci() or {}
        local f=focus[1];local chain={}
        for i=1,6 do
            if not f then break end
            chain[#chain+1]=name(f)
            local ok,parent=pcall(function() return f:GetParent() end);f=ok and parent or nil
        end
        D.Log(event,value(a)..' focus='..table.concat(chain,' > '),false)
    else D.Log(event,value(a)..' '..value(b),true) end
end)
local elapsed=0
observer:SetScript('OnUpdate',function(_,dt)
    if not D.enabled then return end
    elapsed=elapsed+dt;if elapsed<.05 then return end;elapsed=0
    if not A.map or not A.map:IsShown() then return end
    local ok,state=pcall(snapshot)
    if ok and state~=D.last then D.Log('geometry-change','engine/poll observation',false) end
end)
