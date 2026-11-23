local _,A=...
local R={limit=60,maxBytes=60000,lines={},total=0,watched=setmetatable({},{__mode='k'})};A.MapReport=R
local function readable(v) return not (issecretvalue and issecretvalue(v)) end
local function scalar(v)
    if not readable(v) then return '<secret>' end
    if type(v)=='number' and v==v and math.abs(v)<math.huge then return string.format('%.3f',v) end
    if type(v)=='string' then return v:sub(1,180) end
    if type(v)=='boolean' then return tostring(v) end
    return '-'
end
local function call(fn,...)
    if type(fn)~='function' then return end
    local ok,v=pcall(fn,...);if ok and readable(v) then return v end
end
local function method(f,key,...)
    if not readable(f) or (type(f)~='table' and type(f)~='userdata') then return end
    local ok,fn=pcall(function()return f[key]end)
    if ok then return call(fn,f,...) end
end
local function name(f)
    if not readable(f) then return '<secret>' end
    if f==A.map then return 'WorldMapFrame' end
    if f==A.bar then return 'Mapperly.titlebar' end
    if f==UIParent then return 'UIParent' end
    if type(f)=='table' or type(f)=='userdata' then return scalar(method(f,'GetName')) end
    return scalar(f)
end
local function rect(f)
    local result={}
    for _,key in ipairs({'Left','Top','Width','Height','Scale','EffectiveScale','NumPoints','FrameLevel'}) do
        result[#result+1]=key..'='..scalar(method(f,'Get'..key))
    end
    result[#result+1]='shown='..scalar(method(f,'IsShown'))
    result[#result+1]='movable='..scalar(method(f,'IsMovable'))
    result[#result+1]='clamped='..scalar(method(f,'IsClampedToScreen'))
    result[#result+1]='userPlaced='..scalar(method(f,'IsUserPlaced'))
    result[#result+1]='parent='..name(method(f,'GetParent'))
    if f and type(f.GetPoint)=='function' then
        local count=method(f,'GetNumPoints');count=type(count)=='number' and math.min(4,math.max(0,count)) or 1
        for i=1,count do
            local ok,p,relative,rp,x,y=pcall(f.GetPoint,f,i)
            if ok then result[#result+1]='anchor'..i..'='..table.concat({scalar(p),name(relative),scalar(rp),scalar(x),scalar(y)},',') end
        end
    end
    return table.concat(result,' ')
end
local function saved(p) return type(p)=='table' and scalar(p.x)..','..scalar(p.y) or '-' end
local function snapshot()
    local db=A.db or {};local values={}
    for _,key in ipairs({'compact','scale','questPane','locked','theme'}) do values[#values+1]=key..'='..scalar(db[key]) end
    for _,key in ipairs({'dragging','applying','layoutReady','layoutCompact','layoutPending','dragLayoutPending','dragViewportPending','viewportFitQueued','nativeWindowed'}) do values[#values+1]=key..'='..scalar(A[key]) end
    values[#values+1]='combat='..scalar(call(InCombatLockdown))
    return rect(A.map)..'\n  '..table.concat(values,' ')..' saved='..saved(db.position)..' largeSaved='..saved(db.largePosition)
end
local function redact(s)
    for _,private in ipairs({call(UnitName,'player') or false,call(UnitGUID,'player') or false,call(GetRealmName) or false}) do
        if type(private)=='string' and #private>0 then s=s:gsub(private:gsub('([^%w])','%%%1'),'[private]') end
    end
    return s:gsub('|','/')
end
function R.Log(event,detail,stack)
    if not R.enabled or R.busy then return end
    R.busy=true
    local ok=pcall(function()
        R.total=R.total+1
        local state=snapshot();R.last=state
        local line=string.format('%d +%.2fs %s %s\n  %s',R.total,(call(GetTime) or 0)-(R.started or 0),event,detail or '',state)
        if stack then line=line..'\n  '..tostring(call(debugstack,4,5,0) or '<stack unavailable>'):sub(1,600) end
        R.lines[#R.lines+1]=redact(line):sub(1,1600)
        if #R.lines>R.limit then table.remove(R.lines,1) end
    end)
    R.busy=nil
    if not ok then R.errors=(R.errors or 0)+1 end
end
local function watch(object,key,label)
    if not object or type(object[key])~='function' then return end
    R.watched[object]=R.watched[object] or {}
    if R.watched[object][key] then return end
    local ok=pcall(hooksecurefunc,object,key,function(...)
        if not R.enabled then return end
        local args={...};local count=select('#',...)
        local success,detail=pcall(function()
            local text={}
            for i=readable(args[1]) and args[1]==object and 2 or 1,math.min(count,6) do text[#text+1]=name(args[i]) end
            return table.concat(text,',')
        end)
        R.Log(label..'.'..key,success and detail or '<arguments unavailable>',true)
    end)
    if ok then R.watched[object][key]=true end
end
local function attach()
    for _,key in ipairs({'ApplyLayout','SaveMapPosition','PositionMap','FitViewport','QueueViewportFit','LayoutShell','ResetMapPosition'}) do watch(A,key,'Mapperly') end
    for _,key in ipairs({'UpdateUIPanelPositions','RestoreUIPanelArea','ShowUIPanel','HideUIPanel','UIParent_ManageFramePositions'}) do watch(_G,key,'Blizzard') end
    for _,entry in ipairs({{A.map,'map'},{A.bar,'bar'},{A.mapThemeTrim,'trim'}}) do
        local f,label=entry[1],entry[2]
        if f then
            for _,key in ipairs({'SetPoint','ClearAllPoints','SetAllPoints','StartMoving','StopMovingOrSizing','SetScale','SetSize','SetMovable','SetUserPlaced','SetClampedToScreen','SetClampRectInsets','SetParent'}) do watch(f,key,label) end
            R.watched[f]=R.watched[f] or {}
            for _,script in ipairs({'OnDragStart','OnDragStop','OnMouseDown','OnMouseUp','OnShow','OnHide','OnSizeChanged'}) do
                local key='script:'..script
                if not R.watched[f][key] then
                    local ok=pcall(f.HookScript,f,script,function() R.Log(label..'.'..script,'',true) end)
                    if ok then R.watched[f][key]=true end
                end
            end
        end
    end
end
function R.Start()
    R.lines={};R.total=0;R.errors=0;R.started=call(GetTime) or 0;R.enabled=true
    attach();R.Log('capture-start','',true)
end
function R.Stop() R.Log('capture-stop','',false);R.enabled=false end
function R.Build()
    local lines={'Mapperly map position report: '..scalar(A.version)}
    local function add(k,v) lines[#lines+1]=k..': '..v end
    if type(GetBuildInfo)=='function' then
        local ok,v,b,_,interface=pcall(GetBuildInfo)
        if ok then add('Client',scalar(v)..' build='..scalar(b)..' interface='..scalar(interface)) end
    end
    if type(GetPhysicalScreenSize)=='function' then
        local ok,w,h=pcall(GetPhysicalScreenSize);if ok then add('Physical display',scalar(w)..' x '..scalar(h)) end
    end
    for _,k in ipairs({'useUiScale','uiScale','gxWindowedResolution','gxResolution','gxMonitor','gxMaximize','gxWindow'}) do add('CVar',k..'='..scalar(call(GetCVar,k))) end
    add('UIParent',rect(UIParent));add('Map',snapshot())
    if A.map then add('Canvas',rect(call(A.map.GetCanvas,A.map)));add('Viewport',rect(A.map.ScrollContainer)) end
    local addons=C_AddOns or {};local loaded={}
    local count=call(addons.GetNumAddOns or GetNumAddOns)
    if type(count)=='number' then
        for i=1,math.min(count,1000) do
            if call(addons.IsAddOnLoaded or IsAddOnLoaded,i) then
                local id=call(addons.GetAddOnInfo or GetAddOnInfo,i)
                if type(id)=='string' then loaded[#loaded+1]=scalar(id)..'@'..scalar(call(addons.GetAddOnMetadata or GetAddOnMetadata,id,'Version')) end
            end
        end
    end
    table.sort(loaded);add('Loaded addons',table.concat(loaded,', '):sub(1,10000))
    local trace={};local size=0
    for i=#R.lines,1,-1 do
        local row=R.lines[i];if size+#row+2>42000 then break end
        table.insert(trace,1,row);size=size+#row+2
    end
    add('Capture','events='..R.total..' retained='..#trace..' observerErrors='..(R.errors or 0)..' (oldest retained first)')
    lines[#lines+1]=#trace>0 and table.concat(trace,'\n\n') or 'No detailed capture. Use /mapperly mapreport start, reproduce the issue, then /mapperly mapreport.'
    return redact(table.concat(lines,'\n')):sub(1,R.maxBytes)
end
function R.Open()
    R.Stop()
    local U=A.Dialogs;local f=R.frame
    if not f then
        f=U.Window('MapperlyMapReportWindow','Map position report','Press Ctrl+C to copy. Nothing is sent automatically.',740,580);R.frame=f
        local scroll=CreateFrame('ScrollFrame',nil,f,'UIPanelScrollFrameTemplate');scroll:SetPoint('TOPLEFT',f,'TOPLEFT',24,-100);scroll:SetSize(666,400)
        local edit=U.Input(scroll,0,0,660,400,R.maxBytes,true);f.edit=edit;scroll:SetScrollChild(edit)
        edit:SetScript('OnEscapePressed',function() f:Hide() end)
        edit:SetScript('OnTextChanged',function(self,user)if user then self:SetText(f.report or '')end end)
        U.Action(f,'Select all',24,526,120,function()edit:SetFocus();edit:HighlightText()end)
        U.Action(f,'Close',596,526,120,function()f:Hide()end)
    end
    f.report=R.Build();f.edit:SetText(f.report);f.edit:SetHeight(math.max(400,select(2,f.report:gsub('\n',''))*15+24));U.Show(f)
    f.edit:SetFocus();f.edit:HighlightText()
end
function R.Command(arg)
    if arg=='start' then
        if not A.map then A.Print('Open the world map with M first, then use /mapperly mapreport start.');return end
        R.Start();A.Print('Map capture started. Move the map and change the setting that resets it, then use /mapperly mapreport.')
    elseif arg=='stop' then R.Stop();A.Print('Map capture stopped.')
    elseif arg=='' or arg=='report' then R.Open()
    else A.Print('/mapperly mapreport start | report | stop') end
end
local observer=CreateFrame('Frame');R.observer=observer
for _,event in ipairs({'DISPLAY_SIZE_CHANGED','UI_SCALE_CHANGED','ADDON_ACTION_BLOCKED','ADDON_ACTION_FORBIDDEN','GLOBAL_MOUSE_DOWN','GLOBAL_MOUSE_UP','PLAYER_LOGOUT'}) do observer:RegisterEvent(event) end
observer:SetScript('OnEvent',function(_,event,a,b)
    if not R.enabled then return end
    if event=='GLOBAL_MOUSE_DOWN' or event=='GLOBAL_MOUSE_UP' then
        if not method(A.map,'IsShown') then return end
        local focus=call(GetMouseFoci);local f=type(focus)=='table' and focus[1];local chain={}
        for i=1,6 do
            if not readable(f) then chain[#chain+1]='<secret>';break end
            if not f then break end
            chain[#chain+1]=name(f);f=method(f,'GetParent')
        end
        R.Log(event,scalar(a)..' focus='..table.concat(chain,' > '),false);return
    end
    R.Log(event,scalar(a)..' '..scalar(b),true)
    if event=='PLAYER_LOGOUT' then R.enabled=false end
end)
local elapsed=0
observer:SetScript('OnUpdate',function(_,dt)
    if not R.enabled then return end
    elapsed=elapsed+dt;if elapsed<.15 then return end;elapsed=0
    local ok,state=pcall(snapshot)
    if ok and state~=R.last then R.Log('geometry-change','engine/poll observation',false) end
end)
